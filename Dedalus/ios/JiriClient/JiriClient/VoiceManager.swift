import Foundation
import AVFoundation
import Speech

/// Simple voice state for turn-based architecture
enum VoiceState: String {
    case idle
    case listening      // Recording + live transcribing
    case processing     // Sending to backend
    case playing        // Playing TTS response
}

/// Handles on-device speech recognition, API communication, and playback.
/// Turn-based: Listen (on-device STT) -> Send text -> LLM -> TTS -> Play
@MainActor
class VoiceManager: NSObject, ObservableObject {
    
    // MARK: - Published State
    @Published var state: VoiceState = .idle
    @Published var transcript: String = ""
    @Published var assistantText: String = ""
    @Published var errorMessage: String?
    
    // Convenience computed properties
    var isListening: Bool { state == .listening }
    var isProcessing: Bool { state == .processing }
    var isPlaying: Bool { state == .playing }
    var isBusy: Bool { state != .idle }
    
    // MARK: - Components
    private var speechRecognizer: SFSpeechRecognizer?
    private var recognitionRequest: SFSpeechAudioBufferRecognitionRequest?
    private var recognitionTask: SFSpeechRecognitionTask?
    private var audioEngine: AVAudioEngine?
    private var audioPlayer: AVAudioPlayer?
    private var sessionId: String = ""
    
    // MARK: - Initialization
    override init() {
        super.init()
        speechRecognizer = SFSpeechRecognizer(locale: Locale(identifier: "en-US"))
        audioEngine = AVAudioEngine()
    }
    
    // MARK: - Authorization
    
    func requestPermissions() async -> Bool {
        // Request microphone permission
        let micGranted = await withCheckedContinuation { continuation in
            AVAudioSession.sharedInstance().requestRecordPermission { granted in
                continuation.resume(returning: granted)
            }
        }
        
        // Request speech recognition permission
        let speechGranted = await withCheckedContinuation { continuation in
            SFSpeechRecognizer.requestAuthorization { status in
                continuation.resume(returning: status == .authorized)
            }
        }
        
        return micGranted && speechGranted
    }
    
    // MARK: - Listening (On-Device Speech Recognition)
    
    func startListening() {
        guard state == .idle else { return }
        guard let speechRecognizer = speechRecognizer, speechRecognizer.isAvailable else {
            errorMessage = "Speech recognition not available"
            return
        }
        guard let audioEngine = audioEngine else {
            errorMessage = "Audio engine not initialized"
            return
        }
        
        // Reset state
        transcript = ""
        assistantText = ""
        errorMessage = nil
        
        // Configure audio session for recording
        do {
            let audioSession = AVAudioSession.sharedInstance()
            try audioSession.setCategory(.playAndRecord, mode: .measurement, options: [.defaultToSpeaker, .allowBluetoothHFP])
            try audioSession.setActive(true, options: .notifyOthersOnDeactivation)
        } catch {
            errorMessage = "Audio session error: \(error.localizedDescription)"
            return
        }
        
        // Create recognition request
        recognitionRequest = SFSpeechAudioBufferRecognitionRequest()
        guard let recognitionRequest = recognitionRequest else {
            errorMessage = "Unable to create recognition request"
            return
        }
        
        recognitionRequest.shouldReportPartialResults = true
        
        // Start recognition task
        recognitionTask = speechRecognizer.recognitionTask(with: recognitionRequest) { [weak self] result, error in
            Task { @MainActor in
                guard let self = self else { return }
                
                if let result = result {
                    self.transcript = result.bestTranscription.formattedString
                }
                
                if let error = error as NSError?, error.domain == "kAFAssistantErrorDomain" {
                    // Ignore "no speech detected" errors
                    if error.code != 1110 {
                        self.errorMessage = error.localizedDescription
                    }
                }
            }
        }
        
        // Configure audio input
        let inputNode = audioEngine.inputNode
        let recordingFormat = inputNode.outputFormat(forBus: 0)
        
        inputNode.installTap(onBus: 0, bufferSize: 1024, format: recordingFormat) { buffer, _ in
            self.recognitionRequest?.append(buffer)
        }
        
        // Start audio engine
        do {
            audioEngine.prepare()
            try audioEngine.start()
            state = .listening
            print("🎤 Listening started (on-device STT)")
        } catch {
            errorMessage = "Audio engine error: \(error.localizedDescription)"
            stopListening()
        }
    }
    
    func stopListening() {
        guard state == .listening else { return }
        
        // Stop audio engine
        audioEngine?.stop()
        audioEngine?.inputNode.removeTap(onBus: 0)
        
        // End recognition
        recognitionRequest?.endAudio()
        recognitionRequest = nil
        recognitionTask?.cancel()
        recognitionTask = nil
        
        print("🛑 Listening stopped. Transcript: \(transcript)")
        
        // Just return to idle - let user review/edit transcript before sending
        state = .idle
    }
    
    // MARK: - API Communication
    
    private func sendTextToBackend(text: String) async {
        do {
            let response = try await JiriAPI.sendTextChat(text: text, sessionId: sessionId)
            
            self.sessionId = response.sessionId
            self.assistantText = response.replyText
            
            // Play audio if available
            if let audioBase64 = response.audioBase64,
               let audioData = Data(base64Encoded: audioBase64) {
                playAudio(data: audioData)
            } else {
                state = .idle
            }
            
        } catch {
            errorMessage = "Failed: \(error.localizedDescription)"
            state = .idle
            print("❌ API error: \(error)")
        }
    }
    
    // MARK: - Playback
    
    private func playAudio(data: Data) {
        // Configure audio session for playback
        do {
            let audioSession = AVAudioSession.sharedInstance()
            try audioSession.setCategory(.playback, mode: .default, options: [.defaultToSpeaker])
            try audioSession.setActive(true)
        } catch {
            print("❌ Audio session error for playback: \(error)")
        }
        
        do {
            audioPlayer = try AVAudioPlayer(data: data)
            audioPlayer?.delegate = self
            audioPlayer?.play()
            state = .playing
            print("🔊 Playing response audio")
        } catch {
            print("❌ Playback error: \(error)")
            state = .idle
        }
    }
    
    func stopPlayback() {
        audioPlayer?.stop()
        audioPlayer = nil
        state = .idle
    }
    
    // MARK: - Controls
    
    func toggleListening() {
        switch state {
        case .idle:
            startListening()
        case .listening:
            stopListening()
        case .playing:
            stopPlayback()
        case .processing:
            break // Cannot interrupt processing
        }
    }
}

// MARK: - AVAudioPlayerDelegate
extension VoiceManager: AVAudioPlayerDelegate {
    nonisolated func audioPlayerDidFinishPlaying(_ player: AVAudioPlayer, successfully flag: Bool) {
        Task { @MainActor in
            self.state = .idle
            print("✓ Playback finished")
        }
    }
}
