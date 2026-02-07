import AppIntents

/// App Intent that allows Siri to invoke Jiri.
/// Usage: "Hey Siri, Ask Jiri [query]"
@available(iOS 16.0, *)
struct AskJiriIntent: AppIntent {
    static var title: LocalizedStringResource = "Ask Jiri"
    static var description = IntentDescription("Ask Jiri a question or give a command")
    
    /// The user's spoken query.
    @Parameter(title: "Query", requestValueDialog: "What would you like to ask Jiri?")
    var query: String
    
    /// Optional session ID for conversation continuity.
    @Parameter(title: "Session ID", default: "")
    var sessionId: String
    
    static var parameterSummary: some ParameterSummary {
        Summary("Ask Jiri \(\.$query)")
    }
    
    /// Performs the intent by calling the Jiri backend.
    func perform() async throws -> some IntentResult & ReturnsValue<String> & ProvidesDialog {
        do {
            let (reply, newSessionId, _) = try await JiriAPI.send(query, sessionId: sessionId)
            
            // Store session ID for next turn (in a real app, use UserDefaults or AppStorage)
            // For now, just return the reply
            
            return .result(
                value: reply,
                dialog: IntentDialog(stringLiteral: reply)
            )
        } catch {
            let errorMessage = "Sorry, I couldn't connect to Jiri. Please try again."
            return .result(
                value: errorMessage,
                dialog: IntentDialog(stringLiteral: errorMessage)
            )
        }
    }
}

/// Shortcut provider that exposes the AskJiri intent to Shortcuts app and Siri.
@available(iOS 16.0, *)
struct JiriShortcuts: AppShortcutsProvider {
    static var appShortcuts: [AppShortcut] {
        AppShortcut(
            intent: AskJiriIntent(),
            phrases: [
                "Ask \(.applicationName)",
                "Talk to \(.applicationName)"
            ],
            shortTitle: "Ask Jiri",
            systemImageName: "waveform"
        )
    }
}
