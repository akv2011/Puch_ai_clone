# WhatsApp-Gemini MCP Server

A Model Context Protocol server that integrates WhatsApp messaging with Google's Gemini LLM, allowing you to send AI-powered responses through WhatsApp.

## 🚀 Features

- **Send AI-powered WhatsApp messages**: Process messages through Gemini LLM and send responses via WhatsApp
- **Direct chat with Gemini**: Use Gemini LLM for AI conversations without WhatsApp
- **Direct WhatsApp messaging**: Send messages directly without AI processing
- **Service status checking**: Monitor the health of all connected services

## 🛠️ Tools Available

1. **send_whatsapp_with_gemini**: Send messages to WhatsApp after processing through Gemini
2. **chat_with_gemini**: Chat directly with Gemini LLM
3. **send_whatsapp_direct**: Send direct WhatsApp messages without AI
4. **get_server_status**: Check service status

## 📋 Prerequisites

1. **Google Gemini API Key**
   - Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
   - Create a new API key
   - Keep it secure

2. **Twilio Account** (for WhatsApp)
   - Sign up at [Twilio](https://www.twilio.com/)
   - Get your Account SID and Auth Token
   - Enable WhatsApp sandbox for testing

## ⚙️ Setup Instructions

### 1. Install Dependencies

```powershell
cd whatsapp-gemini-server
uv sync
```

### 2. Configure Environment

1. Copy the environment template:
   ```powershell
   copy .env.example .env
   ```

2. Edit `.env` file with your credentials:
   ```env
   GEMINI_API_KEY=your_actual_gemini_api_key
   TWILIO_ACCOUNT_SID=your_twilio_account_sid
   TWILIO_AUTH_TOKEN=your_twilio_auth_token
   TWILIO_WHATSAPP_NUMBER=whatsapp:+14155238886
   ```

### 3. Set Up Twilio WhatsApp Sandbox

1. Go to [Twilio Console WhatsApp Sandbox](https://console.twilio.com/us1/develop/sms/try-it-out/whatsapp-learn)
2. Follow the instructions to join the sandbox
3. Send the activation message to the sandbox number

### 4. Test the Server

```powershell
uv run whatsapp_gemini.py
```

## 🔧 Configuration with Claude Desktop

Add this to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "whatsapp-gemini": {
      "command": "C:\\Users\\arunk\\.local\\bin\\uv.exe",
      "args": [
        "--directory",
        "c:\\Users\\arunk\\Puch_ai_clone\\whatsapp-gemini-server",
        "run",
        "whatsapp_gemini.py"
      ],
      "type": "stdio"
    }
  }
}
```

## 📱 Usage Examples

### With Claude Desktop:

1. **Send AI-powered WhatsApp message**:
   - "Send a WhatsApp message to +1234567890 asking about the weather"
   - The message will be processed by Gemini and sent via WhatsApp

2. **Chat with Gemini**:
   - "Ask Gemini about the best programming practices"

3. **Send direct WhatsApp**:
   - "Send 'Hello!' directly to +1234567890 via WhatsApp"

4. **Check service status**:
   - "Check if all services are working"

## 🔐 Security Notes

- **Never commit your `.env` file** - it contains sensitive credentials
- **Use environment variables** for production deployments
- **Twilio Sandbox** is for testing only - upgrade for production use

## 🐛 Troubleshooting

### Common Issues:

1. **"Gemini API key not configured"**
   - Ensure `GEMINI_API_KEY` is set in your `.env` file
   - Verify the API key is valid

2. **"Twilio not configured"**
   - Check `TWILIO_ACCOUNT_SID` and `TWILIO_AUTH_TOKEN` in `.env`
   - Verify credentials are correct

3. **WhatsApp messages not sending**
   - Ensure you've activated the Twilio WhatsApp sandbox
   - Check that the recipient has also joined the sandbox
   - Verify phone number format (+1234567890)

4. **Import errors**
   - Run `uv sync` to install all dependencies

### Logs and Debugging:

The server logs all activities to stderr. Check the logs for detailed error information.

## 🔄 Workflow

1. **User sends request** → Claude Desktop
2. **Claude processes** → Calls MCP server tool
3. **Message sent to Gemini** → Gets AI response
4. **AI response sent** → WhatsApp via Twilio
5. **Confirmation returned** → Back to Claude

## 🌟 Advanced Features

- **Context support**: Provide context to Gemini for better responses
- **Message history**: Track sent messages with SIDs
- **Error handling**: Comprehensive error reporting
- **Service monitoring**: Real-time status checking

## 📚 API References

- [Google Gemini API](https://ai.google.dev/docs)
- [Twilio WhatsApp API](https://www.twilio.com/docs/whatsapp)
- [MCP Protocol](https://modelcontextprotocol.io/)
