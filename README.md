# AI-customer-support-chatbot

An intelligent customer support chatbot system with a modern web interface and Flask backend. The bot provides automated responses to common customer inquiries using keyword-based FAQ matching and includes escalation capabilities for complex issues.

## Features

### Core Functionality
- **Intelligent FAQ Matching**: Keyword-based matching system with confidence scoring
- **Real-time Chat Interface**: Modern, responsive chat UI with typing indicators
- **Session Management**: Persistent conversation sessions with unique identifiers
- **Escalation System**: Automatic detection and manual escalation to human agents
- **Conversation History**: Complete chat history storage and retrieval
- **Multi-category Support**: Handles orders, returns, shipping, payments, account issues, and more

### Technical Features
- **RESTful API**: Well-structured API endpoints for all operations
- **SQLite Database**: Persistent storage for sessions and messages
- **CORS Support**: Cross-origin resource sharing enabled
- **Health Monitoring**: Built-in health check endpoint
- **Logging**: Comprehensive logging for debugging and monitoring

### User Interface
- **Responsive Design**: Works seamlessly across desktop and mobile devices
- **Dark/Light Theme**: Toggle between themes for better user experience
- **Typing Animation**: Visual feedback during bot response generation
- **Message Timestamps**: All messages include timestamp information
- **Escalation Controls**: Easy-to-use escalation button for human assistance

## Prerequisites

- Python 3.7 or higher
- Modern web browser (Chrome, Firefox, Safari, Edge)

## Installation

1. **Clone or download the project files**
   ```bash
   # Ensure you have both backend.py and index.html in the same directory
   ```

2. **Install Python dependencies**
   ```bash
   pip install flask flask-cors
   ```

3. **Run the backend server**
   ```bash
   python backend.py
   ```

4. **Access the application**
   - Open `index.html` in your web browser
   - Or navigate to `http://localhost:5000` to see the API status

## Project Structure

```
customer-support-bot/
├── backend.py          # Flask backend server
├── index.html          # Frontend chat interface
├── support.db          # SQLite database (auto-created)
└── README.md           # This file
```

## Configuration

### Backend Configuration

The bot comes pre-configured with comprehensive FAQs covering:

- **Orders**: Tracking, cancellation, modification
- **Returns**: Policy, process, refunds
- **Shipping**: Delivery times, address changes
- **Payments**: Accepted methods, billing issues
- **Account**: Login problems, password reset
- **Products**: Size guides, specifications
- **Technical**: Website issues, troubleshooting
- **Quality**: Damaged items, replacements

### Customization Options

1. **Modify FAQs**: Edit the `load_faqs()` method in `backend.py`
2. **Adjust Confidence Thresholds**: Modify the threshold values in `find_best_faq_match()`
3. **Update Escalation Keywords**: Add/remove keywords in the `escalation_keywords` list
4. **Change Styling**: Modify the CSS in `index.html`

## API Endpoints

### Chat Endpoint
```http
POST /api/chat
Content-Type: application/json

{
  "message": "How do I track my order?",
  "session_id": "optional-session-id"
}
```

### Conversation History
```http
GET /api/history/{session_id}
```

### Session Management
```http
GET /api/sessions
```

### Escalation
```http
POST /api/escalate
Content-Type: application/json

{
  "session_id": "session-id",
  "reason": "Customer request"
}
```

### Health Check
```http
GET /api/health
```

## Usage

1. **Start the Backend**
   ```bash
   python backend.py
   ```
   The server will start on `http://localhost:5000`

2. **Open the Chat Interface**
   - Open `index.html` in your web browser
   - The interface will automatically connect to the backend

3. **Start Chatting**
   - Type your message in the input field
   - Press Enter or click Send
   - The bot will respond based on FAQ matching
   - Use the escalate button if you need human assistance

## How It Works

### FAQ Matching System
1. **Keyword Analysis**: User queries are analyzed for matching keywords
2. **Confidence Scoring**: Each FAQ match receives a confidence score (0-1)
3. **Response Selection**:
   - High confidence (>0.7): Direct FAQ answer
   - Medium confidence (>0.5): FAQ answer + escalation offer
   - Low confidence (<0.5): Escalation to human agent

### Escalation Logic
The system automatically escalates conversations when:
- Confidence score is below 0.7
- Escalation keywords are detected (urgent, emergency, complaint, etc.)
- User manually requests escalation

### Session Management
- Each conversation gets a unique session ID
- All messages are stored with timestamps
- Sessions persist across browser refreshes
- Message count and activity tracking included

## Database Schema

### Sessions Table
- `session_id`: Unique session identifier
- `created_at`: Session creation timestamp
- `last_activity`: Last message timestamp
- `message_count`: Total messages in session

### Messages Table
- `id`: Auto-incrementing message ID
- `session_id`: Associated session
- `message_type`: user, bot, or system
- `content`: Message content (JSON for bot responses)
- `timestamp`: Message timestamp
- `confidence_score`: Bot response confidence
- `source`: Response source (FAQ category, fallback, etc.)

## 🚀 Deployment

### Local Development
```bash
python backend.py
# Server runs on http://localhost:5000
```

### Production Deployment
1. Use a production WSGI server like Gunicorn
2. Configure proper database (consider PostgreSQL for production)
3. Set up reverse proxy (nginx)
4. Enable SSL/TLS
5. Configure proper logging

Example with Gunicorn:
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 backend:app
```

## Customization

### Adding New FAQs
```python
{
    "question": "Your question here?",
    "answer": "Your detailed answer here.",
    "keywords": ["keyword1", "keyword2", "keyword3"],
    "category": "your_category"
}
```

### Modifying UI Theme
Edit the CSS variables in `index.html`:
```css
:root {
    --primary-color: #4a90e2;
    --background-color: #f5f5f5;
    --text-color: #333;
    /* ... other variables ... */
}
```

### Adjusting Response Behavior
Modify confidence thresholds in `generate_response()`:
```python
if faq_match and confidence > 0.8:  # Higher threshold
    # Direct response
elif faq_match and confidence > 0.6:  # Lower threshold
    # Response with escalation offer
```

## Troubleshooting

### Common Issues

1. **Database locked error**
   - Restart the backend server
   - Check file permissions on support.db

2. **CORS errors**
   - Ensure Flask-CORS is installed
   - Check that CORS is properly configured

3. **Connection refused**
   - Verify backend server is running
   - Check that port 5000 is available

4. **FAQ not matching**
   - Review keywords in FAQ entries
   - Adjust confidence thresholds
   - Check for typos in keywords

### Debug Mode
The server runs in debug mode by default. For production:
```python
app.run(debug=False, host='0.0.0.0', port=5000)
```

## Monitoring

The application includes several monitoring capabilities:

- **Health Check**: `/api/health` endpoint for system status
- **Session Tracking**: Monitor active sessions and message counts
- **Response Metrics**: Track confidence scores and response times
- **Escalation Monitoring**: Log all escalation events

## Contributing

To extend this bot:

1. **Add new FAQ categories**: Update the `load_faqs()` method
2. **Improve matching algorithm**: Enhance `find_best_faq_match()`
3. **Add new API endpoints**: Follow the existing pattern in `backend.py`
4. **Enhance UI**: Modify `index.html` with additional features

## License

This project is open source and available under the MIT License.

## Support

For technical support or questions about this customer support bot system:
- Review the troubleshooting section above
- Check the API health endpoint at `/api/health`
- Examine server logs for detailed error information

## Version History

- **v1.0**: Initial release with basic FAQ matching and chat interface
- Features: SQLite database, REST API, responsive UI, escalation system

Built using Flask, HTML5, CSS3, and JavaScript
