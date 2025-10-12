# AII VSCode Extension

**Version 0.1.0** - AI-powered development assistant bringing 39 AI functions directly into your editor with real-time streaming.

> Part of the [AII project](../README.md) - AI-Powered Terminal Assistant with HTTP API

## Features

### 💬 Interactive Chat
Chat with AII directly in VSCode - similar to Cursor, Claude Code, and Continue.
- **Keyboard Shortcut:** `Cmd+Shift+A` (Mac) / `Ctrl+Shift+A` (Windows/Linux)
- **Command:** `AII: Chat`
- **Features:**
  - Token-by-token streaming for real-time responses
  - Beautiful Markdown rendering with syntax highlighting (artifact mode)
  - Conversation history maintains context across messages
  - Ask questions, get explanations, generate code, and more

### 🔧 Code Generation
Generate code from natural language descriptions with real-time streaming.
- **Keyboard Shortcut:** `Cmd+Shift+G` (Mac) / `Ctrl+Shift+G` (Windows/Linux)
- **Command:** `AII: Generate Code`

### 📝 Git Commit Messages
AI-powered commit message generation from staged changes.
- **Keyboard Shortcut:** `Cmd+Shift+C` (Mac) / `Ctrl+Shift+C` (Windows/Linux)
- **Command:** `AII: Generate Commit Message`

### 💡 Code Explanation
Understand complex code in plain English.
- **Command:** `AII: Explain Code`
- Select code and run the command

### 🌍 Translation
Translate text/comments between languages.
- **Command:** `AII: Translate Text`
- Select text and specify target language

## Requirements

- **AII API server** running (v0.4.12+)
- **API key** configured (auto-detected from `~/.aii/.aii_api_key`)

## Quick Start

1. Install extension from VSCode Marketplace
2. Start AII API server: `aii serve` (runs on port 16169)
3. Extension will auto-detect API key from `~/.aii/.aii_api_key`
4. Use commands via Command Palette or keyboard shortcuts

## Configuration

### Settings

- **`aii.apiUrl`** - API server URL (default: `http://localhost:16169`)
- **`aii.apiKey`** - API key (leave empty to auto-detect from `~/.aii/.aii_api_key`)
- **`aii.streaming`** - Enable real-time streaming for faster responses (default: `true`)

### API Key Setup

The extension auto-detects your API key in this order:

1. VSCode settings (`aii.apiKey`)
2. File: `~/.aii/.aii_api_key`
3. Environment variable: `AII_API_KEY`

**Recommended:** Place your API key in `~/.aii/.aii_api_key` for automatic detection.

## Usage Examples

### Generate Code
1. Open a file in your preferred language
2. Press `Cmd+Shift+G`
3. Describe the code you want (e.g., "function to calculate fibonacci numbers")
4. Watch as code streams in real-time and inserts at cursor

### Generate Commit Message
1. Stage your changes: `git add .`
2. Press `Cmd+Shift+C`
3. Review AI-generated commit message
4. Confirm to commit

### Explain Code
1. Select code you want explained
2. Run `AII: Explain Code` from Command Palette
3. View explanation in output panel

### Translate Text
1. Select text to translate
2. Run `AII: Translate Text` from Command Palette
3. Enter target language
4. Choose to replace or keep both versions

## Features

✅ **Real-time streaming** - See responses token-by-token (<100ms latency)
✅ **Zero-config** - Auto-detects API key and server
✅ **Keyboard shortcuts** - 1-keystroke access to common operations
✅ **39 AI functions** - Full AII function library accessible
✅ **Status bar indicator** - Connection status at a glance
✅ **Error recovery** - Graceful handling of network issues

## Troubleshooting

### Extension won't activate
- Ensure AII API server is running: `aii serve`
- Check API key is configured (see Configuration above)
- Check VSCode Output panel (View → Output → AII)

### Commands not working
- Verify server is accessible: `curl http://localhost:16169/api/status`
- Check status bar shows "$(check) AII" (connected)
- Review error messages in output panel

### Streaming not working
- Enable streaming in settings: `aii.streaming: true`
- Check network connection to API server
- Fallback to REST API if streaming fails

## Development

This extension is part of the AII project monorepo.

### Build
```bash
cd aii-vscode
npm install
npm run compile
```

### Debug
Press F5 in VSCode to launch Extension Development Host

### Package
```bash
npm install -g vsce
vsce package
```

## License

MIT

## Support

- **Issues:** https://github.com/aii-labs/aii-vscode/issues
- **Documentation:** https://github.com/aii-labs/aii-vscode
- **API Docs:** See main AII repository

---

**Made with ❤️ by the AII team**
