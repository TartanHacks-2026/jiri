//
//  JiriApp.swift
//  Jiri
//
//  Main app entry point with deep link handler
//

import SwiftUI

@main
struct JiriApp: App {
    @StateObject private var sessionManager = SessionManager()
    
    var body: some Scene {
        WindowGroup {
            ContentView()
                .environmentObject(sessionManager)
                .onOpenURL { url in
                    handleDeepLink(url)
                }
        }
    }
    
    /// Handle deep links from Siri App Intent
    private func handleDeepLink(_ url: URL) {
        guard url.scheme == "jiri",
              url.host == "continue" else {
            return
        }
        
        // Parse query parameters
        let components = URLComponents(url: url, resolvingAgainstBaseURL: true)
        guard let sessionID = components?.queryItems?.first(where: { $0.name == "session_id" })?.value else {
            return
        }
        
        // Restore session and navigate to voice view
        Task {
            await sessionManager.restoreSession(sessionID)
        }
    }
}

/// Session manager for handling conversation state
@MainActor
class SessionManager: ObservableObject {
    @Published var currentSessionID: String?
    @Published var messages: [Message] = []
    @Published var isInVoiceMode: Bool = false
    
    func restoreSession(_ sessionID: String) async {
        self.currentSessionID = sessionID
        
        // Fetch conversation history from backend
        let url = URL(string: "https://your-backend.com/session/\(sessionID)/history")!
        
        do {
            let (data, _) = try await URLSession.shared.data(from: url)
            let response = try JSONDecoder().decode(SessionHistoryResponse.struct, from: data)
            
            self.messages = response.messages.map { msg in
                Message(role: msg.role, content: msg.content)
            }
            
            // Auto-start voice mode
            self.isInVoiceMode = true
            
        } catch {
            print("Failed to restore session: \(error)")
        }
    }
}

struct Message: Identifiable {
    let id = UUID()
    let role: String  // "user" or "assistant"
    let content: String
}

struct SessionHistoryResponse: Codable {
    let session_id: String
    let messages: [MessageDTO]
}

struct MessageDTO: Codable {
    let role: String
    let content: String
}
