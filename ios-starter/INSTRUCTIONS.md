# 📱 iOS Setup Instructions (Exact Steps)

Follow these steps to run the Jiri iOS app in Xcode.

## 1. Create a New Xcode Project

1.  Open **Xcode**.
2.  Select **Create New Project...**
3.  Choose **iOS** tab -> **App**. Click **Next**.
4.  Fill in the details:
    -   **Product Name**: `Jiri`
    -   **Organization Identifier**: `com.example` (or your own)
    -   **Interface**: **SwiftUI**
    -   **Language**: **Swift**
    -   **Storage**: None
    -   Click **Next** and save it in `repo/jiri` (or wherever you prefer).

## 2. Add Jiri Source Files

1.  In **Finder**, open the `ios-starter` folder inside your repo:
    ```bash
    open ios-starter
    ```
2.  **Select these 3 files**:
    -   `JiriApp.swift`
    -   `JiriConversationIntent.swift`
    -   `ContentView.swift`
3.  **Drag and Drop** them into the Project Navigator (left sidebar in Xcode) under the `Jiri` folder.
4.  **Important**: When prompted:
    -   ✅ Check **"Copy items if needed"**
    -   ✅ Check **"Create groups"**
    -   ✅ Check the target **"Jiri"**
    -   Click **Finish**.

## 3. Configure the App Entry Point

1.  In Xcode, locate the file named `JiriApp.swift` (the one created by Xcode, usually inside the `Jiri` folder).
2.  **Delete it** (Move to Trash).
3.  Now you should only have *my* `JiriApp.swift` (the one you dragged in). It has `@main` which serves as the entry point.

## 4. Configure URL Scheme (Critical for Handoff)

1.  Click on the blue **Jiri** project icon at the top of the left navigator.
2.  Select the **Jiri** target in the main center panel.
3.  Click the **Info** tab at the top.
4.  Scroll down to **URL Types**.
5.  Click the **+** button.
6.  Set **Identifier**: `com.example.jiri` (matches your Bundle Identifier).
7.  Set **URL Schemes**: `jiri` (all lowercase).
    -   *This allows `jiri://` links to open your app.*

## 5. Build and Run

1.  Select a Simulator (e.g., **iPhone 16 Pro**) from the top bar.
2.  Press **Cmd + R** (or the Play button).
3.  The app should launch with a "Talk to Jiri" screen.

## 6. How to Test Siri Handoff

Since you are on Simulator, you can't speak to Siri directly, but you can use **Shortcuts**:

1.  On the Simulator home screen, open the **Shortcuts** app.
2.  You should see an "App Shortcut" automatically created (e.g., "Talk to Jiri").
3.  Tap it to run.
4.  When prompted for text, type: **"Book an Uber"**
5.  Expected result:
    -   Siri (Shortcuts) says: *"Opening the app for you..."*
    -   The Jiri app opens automatically.
    -   You see the conversation history ("Book an Uber") on the screen.

🎉 **Success!** You have verified the full loop.
