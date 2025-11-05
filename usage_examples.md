# VibeCoder Usage Examples

## Basic App Generation

### Default Mode (with progress indicator)
```bash
uv run generate_app.py
```
Shows:
- 🚀 App name and location
- 🔄 Animated progress spinner while waiting for OpenAI API
- ✅ Completion message with instructions

### Verbose Mode (with detailed output)
```bash
uv run generate_app.py --verbose
# or
uv run generate_app.py -v
```
Shows:
- 📋 Detailed app specification
- 📡 Real-time streaming output from OpenAI API
- 🔄 Step-by-step agent execution
- ✅ Completion message

## What You'll See

### Normal Mode:
```
🚀 Generating React app: Task Manager
📍 Output location: result/task-manager-app
🤖 Using OpenAI GPT-5 model...

🔄 Communicating with OpenAI API ⠋

✅ App generation completed!
🎯 Your app is ready in: result/task-manager-app
🏃 To run: cd result/task-manager-app && npm install && npm run dev
```

### Verbose Mode:
```
🚀 Generating React app: Task Manager
📍 Output location: result/task-manager-app
🤖 Using OpenAI GPT-5 model...
📋 App Specification:
   • Name: task-manager-app
   • Display Name: Task Manager
   • Description: A modern React task management application with localStorage persistence
   • Template: react-simple-spa
   • Author: VibeCoder

🔄 Starting agent execution...
📡 Sending request to OpenAI API...
[Live streaming output from the agent will appear here]

✅ App generation completed!
```

## Error Handling

The system provides helpful error messages for common issues:

### Missing API Key:
```
❌ Error during app generation: The api_key client option must be set
💡 Tip: Make sure your OpenAI API key is set in the .env file
   Create a .env file with: OPENAI_API_KEY=your_key_here
```

### Rate Limits:
```
❌ Error during app generation: Rate limit exceeded
💡 Tip: OpenAI rate limit reached. Please wait a moment and try again.
```

### Network Issues:
```
❌ Error during app generation: Connection failed
💡 Tip: Check your internet connection and try again.
```

## Features

- **🔄 Progress Feedback**: Visual indication that the system is working
- **⏱️ Real-time Updates**: See agent progress in verbose mode
- **❌ Graceful Cancellation**: Ctrl+C cleanly stops execution
- **💡 Helpful Errors**: Clear guidance when things go wrong
- **🎯 Success Guidance**: Next steps after successful generation