from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime
import uuid
import sqlite3
import json
import logging
import time
import random

app = Flask(__name__)
app.secret_key = 'customer-support-bot'
CORS(app)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CustomerSupportBot:
    def __init__(self):
        self.init_database()
        self.load_faqs()
        
    def init_database(self):
        self.conn = sqlite3.connect('support.db', check_same_thread=False)
        cursor = self.conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sessions (
                session_id TEXT PRIMARY KEY,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                message_count INTEGER DEFAULT 0
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT,
                message_type TEXT,
                content TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                confidence_score REAL,
                source TEXT
            )
        ''')
        
        self.conn.commit()
        logger.info("Database initialized")
        
    def load_faqs(self):
        '''Load FAQ database'''
        self.faqs = [
            {
                "question": "How do I track my order?",
                "answer": "You can track your order by logging into your account and visiting the 'My Orders' section. You'll find real-time tracking information and delivery updates there. You can also use your order number to track without logging in.",
                "keywords": ["track", "order", "shipping", "delivery", "status", "where is"],
                "category": "orders"
            },
            {
                "question": "What is your return policy?",
                "answer": "We offer a 30-day return policy for unused items in original condition. Returns are free and easy - just print a return label from your account. Refunds are processed within 5-7 business days after we receive your return.",
                "keywords": ["return", "refund", "policy", "exchange", "money back", "warranty"],
                "category": "returns"
            },
            {
                "question": "How can I cancel my order?",
                "answer": "Orders can be cancelled within 1 hour of placement through your account dashboard. After that, the order enters processing and cannot be cancelled. Contact our support team immediately if you need urgent cancellation assistance.",
                "keywords": ["cancel", "stop", "order", "remove", "delete", "change"],
                "category": "orders"
            },
            {
                "question": "What payment methods do you accept?",
                "answer": "We accept all major credit cards (Visa, MasterCard, American Express), PayPal, Apple Pay, Google Pay, Shop Pay, and bank transfers. All payments are processed securely with 256-bit SSL encryption.",
                "keywords": ["payment", "credit card", "paypal", "billing", "pay", "checkout"],
                "category": "payments"
            },
            {
                "question": "How long does shipping take?",
                "answer": "Standard shipping takes 3-5 business days, express shipping takes 1-2 business days, and overnight shipping arrives the next business day. International shipping varies by location (5-14 business days). Free shipping on orders over $50.",
                "keywords": ["shipping", "delivery", "time", "how long", "when", "fast"],
                "category": "shipping"
            },
            {
                "question": "I can't access my account",
                "answer": "Please try resetting your password using the 'Forgot Password' link on the login page. If you're still having trouble, clear your browser cache or try a different browser. Our support team can help you regain access if needed.",
                "keywords": ["account", "login", "password", "access", "forgot", "locked"],
                "category": "account"
            },
            {
                "question": "Do you have size guides?",
                "answer": "Yes! Detailed size guides are available on each product page. Look for the 'Size Guide' link near the size selection. We also offer free exchanges if the size doesn't fit perfectly.",
                "keywords": ["size", "guide", "fit", "measurements", "sizing", "chart"],
                "category": "products"
            },
            {
                "question": "The website isn't working properly",
                "answer": "Please try clearing your browser cache and cookies, or try using a different browser. Disable ad blockers temporarily as they can interfere with functionality. If issues persist, our technical team can assist you.",
                "keywords": ["website", "not working", "broken", "error", "technical", "bug"],
                "category": "technical"
            },
            {
                "question": "How do I change my shipping address?",
                "answer": "You can change your shipping address within 1 hour of placing your order through your account dashboard. After processing begins, contact support immediately - we may still be able to update it depending on fulfillment status.",
                "keywords": ["shipping address", "change", "modify", "address", "delivery location"],
                "category": "shipping"
            },
            {
                "question": "What if my item arrives damaged?",
                "answer": "We sincerely apologize if your item arrived damaged! Please contact us immediately with photos of the damage and your order number. We'll arrange a free replacement or full refund right away, plus expedited shipping at no cost.",
                "keywords": ["damaged", "broken", "defective", "quality", "problem", "replacement"],
                "category": "quality"
            }
        ]
        
        logger.info(f"Loaded {len(self.faqs)} FAQs")
        
    def find_best_faq_match(self, query, threshold=0.6):
        '''Simple keyword-based FAQ matching'''
        query_lower = query.lower()
        best_match = None
        best_score = 0
        
        for faq in self.faqs:
            score = 0
            for keyword in faq["keywords"]:
                if keyword.lower() in query_lower:
                    score += 1
            
            normalized_score = score / len(faq["keywords"])
            
            if normalized_score > best_score and normalized_score >= threshold:
                best_score = normalized_score
                best_match = faq
        
        if best_match:
            confidence = min(0.95, 0.6 + (best_score * 0.35))
            return best_match, confidence
            
        return None, 0
    
    def generate_response(self, query, session_id):
        '''Generate response using FAQ matching'''
        start_time = time.time()
        
        escalation_keywords = [
            'urgent', 'emergency', 'complaint', 'angry', 'disappointed', 'frustrated', 
            'terrible', 'awful', 'worst', 'hate', 'never again', 'lawsuit', 'attorney',
            'manager', 'supervisor', 'escalate', 'speak to human', 'real person'
        ]
        
        query_lower = query.lower()
        escalation_triggered = any(keyword in query_lower for keyword in escalation_keywords)
        
        faq_match, confidence = self.find_best_faq_match(query)
        
        if faq_match and confidence > 0.7:
            response = faq_match["answer"]
            source = f"FAQ-{faq_match['category'].title()}"
            
        elif faq_match and confidence > 0.5:
            response = faq_match["answer"] + "\n\nIf this doesn't fully answer your question, I can connect you with a human agent for more specific help."
            source = f"FAQ-{faq_match['category'].title()}"
            escalation_triggered = True
            
        else:
            fallback_responses = [
                "I understand your question, but I'd like to connect you with a human agent who can provide more specific assistance.",
                "That's a great question! Let me escalate this to our support team who can give you a detailed answer.",
                "I want to make sure you get the best help possible. Would you like me to connect you with a human agent?",
                "For this specific inquiry, our human support team would be better equipped to assist you."
            ]
            
            response = random.choice(fallback_responses)
            confidence = 0.4
            source = "AI-Fallback"
            escalation_triggered = True
        
        response_time = (time.time() - start_time) * 1000
        
        return {
            "response": response,
            "confidence": confidence,
            "source": source,
            "escalation_needed": escalation_triggered,
            "response_time": response_time,
            "category": faq_match["category"] if faq_match else "general"
        }
    
    def save_conversation(self, session_id, user_message, bot_response_data):
        '''Save conversation to database'''
        cursor = self.conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO messages (session_id, message_type, content, confidence_score, source) 
                VALUES (?, ?, ?, ?, ?)
            ''', (session_id, "user", user_message, None, "user"))
            
            cursor.execute('''
                INSERT INTO messages (session_id, message_type, content, confidence_score, source) 
                VALUES (?, ?, ?, ?, ?)
            ''', (
                session_id, 
                "bot", 
                json.dumps(bot_response_data),
                bot_response_data.get('confidence'),
                bot_response_data.get('source')
            ))
            
            # Update or create session record
            cursor.execute('''
                INSERT OR REPLACE INTO sessions (session_id, last_activity, message_count) 
                VALUES (?, CURRENT_TIMESTAMP, 
                    COALESCE((SELECT message_count FROM sessions WHERE session_id = ?), 0) + 2)
            ''', (session_id, session_id))
            
            self.conn.commit()
            
        except Exception as e:
            logger.error(f"Error saving conversation: {e}")
            self.conn.rollback()
    
    def get_conversation_history(self, session_id):
        '''Retrieve conversation history'''
        cursor = self.conn.cursor()
        
        try:
            cursor.execute('''
                SELECT message_type, content, timestamp, confidence_score, source
                FROM messages WHERE session_id = ? ORDER BY timestamp
            ''', (session_id,))
            
            messages = cursor.fetchall()
            history = []
            
            for msg_type, content, timestamp, confidence, source in messages:
                if msg_type == "bot":
                    try:
                        content = json.loads(content)
                    except:
                        content = {"response": content}
                
                history.append({
                    "type": msg_type,
                    "content": content,
                    "timestamp": timestamp,
                    "confidence": confidence,
                    "source": source
                })
                
            return history
            
        except Exception as e:
            logger.error(f"Error getting conversation history: {e}")
            return []

bot = CustomerSupportBot()

# API Routes
@app.route('/api/chat', methods=['POST'])
def chat():
    '''Main chat endpoint'''
    try:
        data = request.get_json()
        message = data.get('message', '').strip()
        session_id = data.get('session_id')
        
        if not message:
            return jsonify({"error": "Message is required"}), 400
            
        if not session_id:
            session_id = str(uuid.uuid4())
            cursor = bot.conn.cursor()
            cursor.execute(
                "INSERT INTO sessions (session_id) VALUES (?)",
                (session_id,)
            )
            bot.conn.commit()
        
        response_data = bot.generate_response(message, session_id)
        
        bot.save_conversation(session_id, message, response_data)
        
        return jsonify({
            "session_id": session_id,
            "response": response_data["response"],
            "confidence": response_data["confidence"],
            "source": response_data["source"],
            "escalation_needed": response_data["escalation_needed"],
            "response_time": response_data["response_time"],
            "category": response_data.get("category", "general"),
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}")
        return jsonify({"error": "Internal server error"}), 500

@app.route('/api/history/<session_id>', methods=['GET'])
def get_history(session_id):
    '''Get conversation history'''
    try:
        history = bot.get_conversation_history(session_id)
        return jsonify({"history": history})
    except Exception as e:
        logger.error(f"Error getting history: {e}")
        return jsonify({"error": "Internal server error"}), 500

@app.route('/api/sessions', methods=['GET'])
def get_sessions():
    '''Get session list'''
    try:
        cursor = bot.conn.cursor()
        cursor.execute('''
            SELECT session_id, created_at, last_activity, message_count
            FROM sessions
            ORDER BY last_activity DESC
            LIMIT 50
        ''')
        
        sessions = cursor.fetchall()
        
        session_list = [
            {
                "session_id": sid,
                "created_at": created,
                "last_activity": activity,
                "message_count": msg_count or 0
            }
            for sid, created, activity, msg_count in sessions
        ]
        
        return jsonify({"sessions": session_list})
    except Exception as e:
        logger.error(f"Error getting sessions: {e}")
        return jsonify({"error": "Internal server error"}), 500

@app.route('/api/escalate', methods=['POST'])
def escalate():
    '''Escalation endpoint'''
    try:
        data = request.get_json()
        session_id = data.get('session_id')
        reason = data.get('reason', 'Customer request')
        
        logger.info(f"Escalation requested for session {session_id}: {reason}")
        
        cursor = bot.conn.cursor()
        escalation_data = {
            "type": "escalation",
            "reason": reason,
            "timestamp": datetime.now().isoformat()
        }
        
        cursor.execute('''
            INSERT INTO messages (session_id, message_type, content, source) 
            VALUES (?, ?, ?, ?)
        ''', (session_id, "system", json.dumps(escalation_data), "system"))
        
        bot.conn.commit()
        
        return jsonify({
            "message": "I've escalated your conversation to our human support team. Please call +91 00000 00000 for immediate assistance.",
            "escalated": True,
            "phone_number": "+91 00000 00000"
        })
        
    except Exception as e:
        logger.error(f"Error in escalate endpoint: {e}")
        return jsonify({"error": "Internal server error"}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    '''Health check endpoint'''
    try:
        cursor = bot.conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM sessions")
        session_count = cursor.fetchone()[0]
        
        return jsonify({
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "database_connected": True,
            "total_sessions": session_count,
            "faq_count": len(bot.faqs)
        })
        
    except Exception as e:
        logger.error(f"Health check error: {e}")
        return jsonify({
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }), 500

@app.route('/', methods=['GET'])
def home():
    '''Home endpoint'''
    return jsonify({
        "message": "Customer Support Bot API is running",
        "endpoints": [
            "POST /api/chat",
            "GET /api/history/<session_id>",
            "GET /api/sessions",
            "POST /api/escalate",
            "GET /api/health"
        ]
    })

if __name__ == '__main__':
    logger.info("Starting Customer Support Bot server...")
    logger.info(f"Loaded {len(bot.faqs)} FAQs")
    logger.info("Server ready on http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)
