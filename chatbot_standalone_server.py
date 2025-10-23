#!/usr/bin/env python
"""
Simple standalone chatbot API server for testing without Django/MySQL.
Runs on port 8001 to avoid conflicts.

Usage:
    python chatbot_standalone_server.py
    
Then test with Postman:
    POST http://localhost:8001/chatbot
    Content-Type: application/json
    Body: {"question": "Dame noticias de deportes"}
"""

from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

# Import chatbot components
try:
    from transformers import pipeline
    import spacy
    from chatbot.services.text_normalizer import TextNormalizer
except ImportError as e:
    print(f"Error: Missing required packages - {e}")
    print("Install with: pip install transformers torch spacy")
    sys.exit(1)

# Paths
FAQ_PATH = PROJECT_ROOT / "chatbot" / "faqs" / "faqs.json"
MODEL_PATH = PROJECT_ROOT / "chatbot" / "faq_model_2"
LABEL_MAP_PATH = MODEL_PATH / "label_map.json"

# Global resources
nlp = None
classifier = None
label_map = None
faqs = None

def load_resources():
    """Load all required resources."""
    global nlp, classifier, label_map, faqs
    
    print("🚀 Loading chatbot resources...")
    
    # Load spaCy
    try:
        nlp = spacy.load("es_core_news_sm")
        print("✓ spaCy loaded")
    except OSError:
        print("✗ spaCy model not found. Run: python -m spacy download es_core_news_sm")
        sys.exit(1)
    
    # Load FAQs
    try:
        with open(FAQ_PATH, 'r', encoding='utf-8') as f:
            data = json.load(f)
            faqs = data.get("faqs", data)
        print(f"✓ Loaded {len(faqs)} FAQs")
    except FileNotFoundError:
        print(f"✗ Error: {FAQ_PATH} not found")
        sys.exit(1)
    
    # Load label map
    try:
        with open(LABEL_MAP_PATH, 'r', encoding='utf-8') as f:
            label_map = json.load(f)
        print(f"✓ Loaded label map")
    except FileNotFoundError:
        print(f"✗ Error: {LABEL_MAP_PATH} not found")
        sys.exit(1)
    
    # Load BERT model
    try:
        classifier = pipeline(
            "text-classification",
            model=str(MODEL_PATH),
            device=-1,
            truncation=True,
            max_length=128
        )
        print(f"✓ BERT model loaded")
    except Exception as e:
        print(f"✗ Error loading model: {e}")
        sys.exit(1)
    
    print("✅ All resources loaded successfully!\n")

def normalize_text(text):
    """Normalize text using spaCy."""
    doc = nlp(text.lower())
    return " ".join([token.lemma_ for token in doc if not token.is_stop and not token.is_punct])

def get_faq_by_id(faq_id):
    """Get FAQ by ID."""
    for faq in faqs:
        if faq.get("id") == faq_id:
            return faq
    return None

def predict_answer(question, threshold=0.08):
    """Predict answer for a question."""
    # Normalize question
    normalized = normalize_text(question)
    
    # Get prediction
    result = classifier(normalized)[0]
    label = result['label']
    confidence = result['score']
    
    # Extract label number
    label_num = int(label.split('_')[1])
    
    # Convert to FAQ ID
    inverted_map = {v: int(k) for k, v in label_map.items()}
    faq_id = inverted_map.get(label_num, -1)
    
    # Check threshold
    if confidence < threshold:
        return {
            "answer": "Lo siento, no entendí. Por favor intenta con otra pregunta.",
            "confidence": confidence,
            "type": "fallback"
        }
    
    # Get FAQ
    faq = get_faq_by_id(faq_id)
    if not faq:
        return {
            "answer": "Error: FAQ no encontrado",
            "confidence": confidence,
            "type": "error"
        }
    
    # Check if it's news search
    if faq_id == 18:
        return {
            "answer": "🔍 Búsqueda de noticias detectada. En producción, esto consultaría MongoDB y devolvería noticias de la categoría solicitada.",
            "confidence": confidence,
            "type": "news_search",
            "category": "detected",
            "note": "MongoDB connection not available in standalone mode. Deploy to test full functionality."
        }
    
    # Return FAQ answer
    answer_text = faq.get("answer", {})
    if isinstance(answer_text, dict):
        answer_text = answer_text.get("es", str(answer_text))
    
    return {
        "answer": answer_text,
        "confidence": confidence,
        "type": "faq",
        "faq_id": faq_id,
        "domain": faq.get("domain", "unknown")
    }

class ChatbotHandler(BaseHTTPRequestHandler):
    """HTTP request handler for chatbot API."""
    
    def do_POST(self):
        """Handle POST requests to /chatbot."""
        if self.path == '/chatbot' or self.path == '/chatbot/':
            try:
                # Read request body
                content_length = int(self.headers['Content-Length'])
                body = self.rfile.read(content_length)
                data = json.loads(body.decode('utf-8'))
                
                # Extract question
                question = data.get('question', '')
                if not question:
                    self.send_error_response(400, "Missing 'question' field")
                    return
                
                # Get answer
                result = predict_answer(question)
                
                # Send response
                self.send_json_response(200, result)
                
                # Log to console
                print(f"Q: {question}")
                print(f"A: {result.get('type')} (conf: {result.get('confidence', 0):.2%})")
                print()
                
            except json.JSONDecodeError:
                self.send_error_response(400, "Invalid JSON")
            except Exception as e:
                self.send_error_response(500, str(e))
        else:
            self.send_error_response(404, "Not found. Use POST /chatbot")
    
    def do_GET(self):
        """Handle GET requests."""
        if self.path == '/' or self.path == '/health':
            self.send_json_response(200, {
                "status": "ok",
                "message": "Lannister News Chatbot API",
                "endpoints": {
                    "POST /chatbot": "Send question and get answer"
                }
            })
        else:
            self.send_error_response(404, "Not found")
    
    def send_json_response(self, status_code, data):
        """Send JSON response."""
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode('utf-8'))
    
    def send_error_response(self, status_code, message):
        """Send error response."""
        self.send_json_response(status_code, {"error": message})
    
    def log_message(self, format, *args):
        """Suppress default logging."""
        pass

def main():
    """Start the server."""
    load_resources()
    
    PORT = 8001
    server = HTTPServer(('localhost', PORT), ChatbotHandler)
    
    print(f"🎯 Chatbot API Server running on http://localhost:{PORT}")
    print(f"📡 Test endpoint: POST http://localhost:{PORT}/chatbot")
    print(f'💡 Example body: {{"question": "Hola"}}')
    print(f"\n🛑 Press Ctrl+C to stop\n")
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n\n👋 Server stopped")
        server.shutdown()

if __name__ == "__main__":
    main()
