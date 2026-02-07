import Foundation

/// API client for communicating with the Jiri backend.
class JiriAPI {
    /// The base URL of the Jiri backend (update with your ngrok URL or deployed server).
    static var baseURL = "https://bfaa-128-2-149-230.ngrok-free.app"
    
    /// Sends a message to the Jiri backend and returns the reply.
    /// - Parameters:
    ///   - query: The user's spoken text.
    ///   - sessionId: Optional session ID for conversation continuity.
    /// - Returns: A tuple of (replyText, sessionId, endConversation).
    static func send(_ query: String, sessionId: String = "", retryCount: Int = 0) async throws -> (reply: String, sessionId: String, end: Bool) {
        let maxRetries = 3
        
        do {
            guard let url = URL(string: "\(baseURL)/turn") else {
                throw JiriError.invalidURL
            }
            
            var request = URLRequest(url: url)
            request.httpMethod = "POST"
            request.setValue("application/json", forHTTPHeaderField: "Content-Type")
            
            let payload: [String: Any] = [
                "session_id": sessionId,
                "user_text": query,
                "client": "ios_app",
                "meta": [
                    "voice": true,
                    "device": "iphone",
                    "timezone": TimeZone.current.identifier
                ]
            ]
            
            request.httpBody = try JSONSerialization.data(withJSONObject: payload)
            
            // Use ephemeral configuration to avoid socket reuse issues in Simulator
            let config = URLSessionConfiguration.ephemeral
            config.timeoutIntervalForRequest = 120 // Increased to 2 minutes for long GPT-4o responses
            let session = URLSession(configuration: config)
            
            let (data, response) = try await session.data(for: request)
            
            guard let httpResponse = response as? HTTPURLResponse, httpResponse.statusCode == 200 else {
                throw JiriError.serverError
            }
            
            guard let json = try JSONSerialization.jsonObject(with: data) as? [String: Any],
                  let replyText = json["reply_text"] as? String,
                  let newSessionId = json["session_id"] as? String,
                  let endConversation = json["end_conversation"] as? Bool else {
                throw JiriError.invalidResponse
            }
            
            return (replyText, newSessionId, endConversation)
            
        } catch {
            if retryCount < maxRetries {
                let delay = UInt64(pow(2.0, Double(retryCount)) * 1_000_000_000) // Quadratic backoff: 1s, 2s, 4s
                try await Task.sleep(nanoseconds: delay)
                return try await send(query, sessionId: sessionId, retryCount: retryCount + 1)
            }
            throw error
        }
    }
    
    // MARK: - Voice Chat (Audio Upload)
    
    struct VoiceChatResponse {
        let sessionId: String
        let transcript: String
        let replyText: String
        let audioBase64: String?
    }
    
    /// Sends audio to the voice chat endpoint and returns transcript + reply + audio.
    static func sendVoiceChat(audioData: Data, sessionId: String = "") async throws -> VoiceChatResponse {
        guard let url = URL(string: "\(baseURL)/voice/chat") else {
            throw JiriError.invalidURL
        }
        
        let boundary = UUID().uuidString
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("multipart/form-data; boundary=\(boundary)", forHTTPHeaderField: "Content-Type")
        request.timeoutInterval = 120
        
        // Build multipart body
        var body = Data()
        
        // Add session_id field
        body.append("--\(boundary)\r\n".data(using: .utf8)!)
        body.append("Content-Disposition: form-data; name=\"session_id\"\r\n\r\n".data(using: .utf8)!)
        body.append("\(sessionId)\r\n".data(using: .utf8)!)
        
        // Add audio file
        body.append("--\(boundary)\r\n".data(using: .utf8)!)
        body.append("Content-Disposition: form-data; name=\"audio\"; filename=\"recording.m4a\"\r\n".data(using: .utf8)!)
        body.append("Content-Type: audio/m4a\r\n\r\n".data(using: .utf8)!)
        body.append(audioData)
        body.append("\r\n".data(using: .utf8)!)
        
        // End boundary
        body.append("--\(boundary)--\r\n".data(using: .utf8)!)
        
        request.httpBody = body
        
        let config = URLSessionConfiguration.ephemeral
        config.timeoutIntervalForRequest = 120
        let session = URLSession(configuration: config)
        
        let (data, response) = try await session.data(for: request)
        
        guard let httpResponse = response as? HTTPURLResponse, httpResponse.statusCode == 200 else {
            throw JiriError.serverError
        }
        
        guard let json = try JSONSerialization.jsonObject(with: data) as? [String: Any],
              let newSessionId = json["session_id"] as? String,
              let transcript = json["transcript"] as? String,
              let replyText = json["reply_text"] as? String else {
            throw JiriError.invalidResponse
        }
        
        let audioBase64 = json["audio_base64"] as? String
        
        return VoiceChatResponse(
            sessionId: newSessionId,
            transcript: transcript,
            replyText: replyText,
            audioBase64: audioBase64
        )
    }
    
    // MARK: - Text Chat (On-device STT)
    
    /// Sends transcribed text to the backend and returns reply + audio.
    /// Used with on-device speech recognition.
    static func sendTextChat(text: String, sessionId: String = "") async throws -> VoiceChatResponse {
        guard let url = URL(string: "\(baseURL)/voice/text") else {
            throw JiriError.invalidURL
        }
        
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        request.timeoutInterval = 60
        
        let payload: [String: Any] = [
            "text": text,
            "session_id": sessionId
        ]
        request.httpBody = try JSONSerialization.data(withJSONObject: payload)
        
        let config = URLSessionConfiguration.ephemeral
        config.timeoutIntervalForRequest = 60
        let session = URLSession(configuration: config)
        
        let (data, response) = try await session.data(for: request)
        
        guard let httpResponse = response as? HTTPURLResponse, httpResponse.statusCode == 200 else {
            throw JiriError.serverError
        }
        
        guard let json = try JSONSerialization.jsonObject(with: data) as? [String: Any],
              let newSessionId = json["session_id"] as? String,
              let replyText = json["reply_text"] as? String else {
            throw JiriError.invalidResponse
        }
        
        let audioBase64 = json["audio_base64"] as? String
        
        return VoiceChatResponse(
            sessionId: newSessionId,
            transcript: text,  // Use the input text as transcript
            replyText: replyText,
            audioBase64: audioBase64
        )
    }
}

enum JiriError: Error, LocalizedError {
    case invalidURL
    case serverError
    case invalidResponse
    
    var errorDescription: String? {
        switch self {
        case .invalidURL: return "Invalid server URL"
        case .serverError: return "Server returned an error"
        case .invalidResponse: return "Could not parse server response"
        }
    }
}
