//
//  JiriConversationIntent.swift
//  Jiri
//
//  App Intent for Siri voice interaction with backend handoff support
//

import Foundation
import AppIntents

/// App Intent that handles voice conversations with Jiri backend
@available(iOS 17.0, *)
struct JiriConversationIntent: AppIntent {
    static var title: LocalizedStringResource = "Talk to Jiri"
    static var description =  IntentDescription("Have a conversation with your Jiri assistant")
    
    /// User's spoken input from Siri
    @Parameter(title: "What do you want to say?")
    var userText: String
    
    /// Session ID for conversation continuity (optional)
    @Parameter(title: "Session ID", default: "")
    var sessionID: String
    
    /// Main perform function - called when intent is triggered
    @MainActor
    func perform() async throws -> some IntentResult & ProvidesDialog {
        // Backend API endpoint
        let backendURL = URL(string: "https://your-backend.com/turn")!
        
        // Construct request payload
        let payload: [String: Any] = [
            "session_id": sessionID,
            "user_text": userText,
            "client": "app_intent",
            "meta": [
                "voice": true,
                "device": "iphone",
                "timezone": TimeZone.current.identifier
            ]
        ]
        
        // Make POST request to backend
        var request = URLRequest(url: backendURL)
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        request.httpBody = try? JSONSerialization.data(withJSONObject: payload)
        
        let (data, _) = try await URLSession.shared.data(for: request)
        
        // Parse response
        guard let json = try? JSONSerialization.jsonObject(with: data) as? [String: Any],
              let sessionID = json["session_id"] as? String,
              let replyText = json["reply_text"] as? String else {
            return .result(dialog: "Sorry, I couldn't connect to the server.")
        }
        
        // Check if backend wants to hand off to app
        let shouldHandoff = (json["handoff_to_app"] as? Bool) ?? false
        let deepLinkURL = json["deep_link_url"] as? String
        
        if shouldHandoff, let urlString = deepLinkURL, let url = URL(string: urlString) {
            // Open the main app with session context
            try await openURL(url)
            return .result(dialog: replyText)
        }
        
        // Continue in Siri (no handoff needed)
        return .result(dialog: replyText)
    }
}

/// App Shortcuts configuration - registers Siri phrases
@available(iOS 17.0, *)
struct JiriAppShortcuts: AppShortcutsProvider {
    static var appShortcuts: [AppShortcut] {
        AppShortcut(
            intent: JiriConversationIntent(),
            phrases: [
                "Hey Jiri, let's talk",
                "Talk to Jiri",
                "Ask Jiri",
                "Open Jiri"
            ],
            shortTitle: "Talk to Jiri",
            systemImageName: "waveform.circle"
        )
    }
}
