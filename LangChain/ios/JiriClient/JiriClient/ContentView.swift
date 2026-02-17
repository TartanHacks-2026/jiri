import SwiftUI
import AVFoundation

struct ContentView: View {
    @State private var inputText = ""
    @State private var conversationLog: [(role: String, text: String)] = []
    @State private var sessionId = ""
    @State private var isLoading = false
    @State private var errorMessage: String?
    
    @StateObject private var voiceManager = VoiceManager()
    
    var body: some View {
        NavigationView {
            VStack(spacing: 0) {
                // Conversation Log
                ScrollViewReader { proxy in
                    ScrollView {
                        LazyVStack(alignment: .leading, spacing: 12) {
                            ForEach(Array(conversationLog.enumerated()), id: \.offset) { index, message in
                                MessageBubble(role: message.role, text: message.text)
                                    .id(index)
                            }
                        }
                        .padding()
                    }
                    .onChange(of: conversationLog.count) { _ in
                        if let lastIndex = conversationLog.indices.last {
                            withAnimation {
                                proxy.scrollTo(lastIndex, anchor: .bottom)
                            }
                        }
                    }
                }
                
                Divider()
                
                // Input Area
                VStack(spacing: 8) {
                    // Status Indicator
                    if voiceManager.state != .idle {
                        HStack(spacing: 4) {
                            if voiceManager.isProcessing {
                                ProgressView()
                                    .scaleEffect(0.7)
                            } else if voiceManager.isListening {
                                Circle()
                                    .fill(Color.red)
                                    .frame(width: 8, height: 8)
                            }
                            Text(statusText)
                                .font(.caption)
                                .foregroundColor(.gray)
                            
                            // Live transcript preview
                            if voiceManager.isListening && !voiceManager.transcript.isEmpty {
                                Text(voiceManager.transcript)
                                    .font(.caption)
                                    .foregroundColor(.secondary)
                                    .lineLimit(1)
                            }
                        }
                        .frame(maxWidth: .infinity, alignment: .leading)
                        .padding(.horizontal)
                    }

                    HStack(spacing: 12) {
                        TextField("Ask Jiri...", text: $inputText)
                            .textFieldStyle(.roundedBorder)
                            .disabled(isLoading || voiceManager.isBusy)
                        
                        // Mic Button
                        Button(action: { voiceManager.toggleListening() }) {
                            ZStack {
                                if voiceManager.isProcessing {
                                    ProgressView()
                                } else {
                                    Image(systemName: micIcon)
                                        .font(.title)
                                        .foregroundColor(micColor)
                                }
                            }
                        }
                        .disabled(isLoading || voiceManager.isProcessing)
                        
                        // Send Button
                        Button(action: sendMessage) {
                            if isLoading {
                                ProgressView()
                                    .progressViewStyle(CircularProgressViewStyle())
                            } else {
                                Image(systemName: "arrow.up.circle.fill")
                                .font(.title)
                            }
                        }
                        .disabled(inputText.isEmpty || isLoading || voiceManager.isBusy)
                    }
                    .padding()
                }
                .background(Color(.systemBackground))
            }
            .navigationTitle("Jiri")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .navigationBarTrailing) {
                    Button("Clear") {
                        conversationLog.removeAll()
                        sessionId = ""
                    }
                }
            }
            .alert("Error", isPresented: .constant(errorMessage != nil)) {
                Button("OK") { errorMessage = nil }
            } message: {
                Text(errorMessage ?? "")
            }
        }
        .onChange(of: voiceManager.assistantText) { text in
            if !text.isEmpty && !voiceManager.transcript.isEmpty {
                // Add completed voice turn to conversation log
                conversationLog.append((role: "user", text: voiceManager.transcript))
                conversationLog.append((role: "assistant", text: text))
            }
        }
        .onChange(of: voiceManager.state) { newState in
            // When listening stops, copy transcript to input field for editing
            if newState == .idle && !voiceManager.transcript.isEmpty && voiceManager.assistantText.isEmpty {
                inputText = voiceManager.transcript
            }
        }
        .onChange(of: voiceManager.errorMessage) { err in
            if let err = err {
                errorMessage = err
            }
        }
    }
    
    private func sendMessage() {
        let query = inputText.trimmingCharacters(in: .whitespacesAndNewlines)
        guard !query.isEmpty else { return }
        
        inputText = ""
        conversationLog.append((role: "user", text: query))
        isLoading = true
        
        Task {
            do {
                let (reply, newSessionId, _) = try await JiriAPI.send(query, sessionId: sessionId)
                sessionId = newSessionId
                conversationLog.append((role: "assistant", text: reply))
            } catch {
                errorMessage = error.localizedDescription
            }
            isLoading = false
        }
    }
    
    private var statusText: String {
        switch voiceManager.state {
        case .idle: return ""
        case .listening: return "Listening..."
        case .processing: return "Thinking..."
        case .playing: return "Speaking..."
        }
    }
    
    private var micIcon: String {
        switch voiceManager.state {
        case .idle: return "mic.circle.fill"
        case .listening: return "stop.circle.fill"
        case .processing: return "hourglass"
        case .playing: return "speaker.wave.2.circle.fill"
        }
    }
    
    private var micColor: Color {
        switch voiceManager.state {
        case .idle: return .blue
        case .listening: return .red
        case .processing: return .orange
        case .playing: return .green
        }
    }
}

struct MessageBubble: View {
    let role: String
    let text: String
    
    var isUser: Bool { role == "user" }
    
    var body: some View {
        HStack {
            if isUser { Spacer() }
            
            Text(text)
                .padding(.horizontal, 16)
                .padding(.vertical, 10)
                .background(isUser ? Color.blue : Color(.systemGray5))
                .foregroundColor(isUser ? .white : .primary)
                .clipShape(RoundedRectangle(cornerRadius: 16))
            
            if !isUser { Spacer() }
        }
    }
}

#Preview {
    ContentView()
}
