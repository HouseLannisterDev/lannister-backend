#!/usr/bin/env python
"""
Simple local testing script for the Lannister News Chatbot.
Tests FAQ responses using the trained BERT model without Django dependencies.

Usage:
    python chatbot/test_chatbot_simple.py
"""

import json
from pathlib import Path
try:
    from colorama import init, Fore, Style
    from transformers import pipeline
    import spacy
except ImportError as e:
    print(f"Error: Missing required packages - {e}")
    print("Install with: pip install transformers torch colorama spacy")
    print("And then: python -m spacy download es_core_news_sm")
    exit(1)

# Initialize colorama
init(autoreset=True)

# Paths
PROJECT_ROOT = Path(__file__).parent.parent
FAQ_PATH = PROJECT_ROOT / "chatbot" / "faqs" / "faqs.json"
MODEL_PATH = PROJECT_ROOT / "chatbot" / "faq_model_2"
LABEL_MAP_PATH = MODEL_PATH / "label_map.json"

# Global variables
nlp = None
classifier = None
label_map = None
faqs = None

def load_resources():
    """Load spaCy, model, FAQs, and label map."""
    global nlp, classifier, label_map, faqs
    
    print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'LANNISTER NEWS CHATBOT - LOCAL TESTING':^60}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}\n")
    print(f"{Fore.YELLOW}Loading resources...{Style.RESET_ALL}\n")
    
    # Load spaCy
    try:
        nlp = spacy.load("es_core_news_sm")
        print(f"{Fore.GREEN}✓ spaCy loaded{Style.RESET_ALL}")
    except OSError:
        print(f"{Fore.RED}✗ spaCy model not found{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}Run: python -m spacy download es_core_news_sm{Style.RESET_ALL}")
        exit(1)
    
    # Load FAQs
    try:
        with open(FAQ_PATH, 'r', encoding='utf-8') as f:
            data = json.load(f)
            faqs = data.get("faqs", data)  # Handle both formats
        print(f"{Fore.GREEN}✓ Loaded {len(faqs)} FAQs from {FAQ_PATH.name}{Style.RESET_ALL}")
    except FileNotFoundError:
        print(f"{Fore.RED}✗ Error: {FAQ_PATH} not found{Style.RESET_ALL}")
        exit(1)
    
    # Load label map
    try:
        with open(LABEL_MAP_PATH, 'r', encoding='utf-8') as f:
            label_map = json.load(f)
        print(f"{Fore.GREEN}✓ Loaded label map with {len(label_map)} labels{Style.RESET_ALL}")
    except FileNotFoundError:
        print(f"{Fore.RED}✗ Error: {LABEL_MAP_PATH} not found{Style.RESET_ALL}")
        exit(1)
    
    # Load BERT model
    try:
        classifier = pipeline(
            "text-classification",
            model=str(MODEL_PATH),
            device=-1,  # Use CPU
            truncation=True,
            max_length=128
        )
        print(f"{Fore.GREEN}✓ BERT model loaded from {MODEL_PATH.name}{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.RED}✗ Error loading model: {e}{Style.RESET_ALL}")
        exit(1)
    
    print(f"\n{Fore.GREEN}{'✓ All resources loaded successfully':^60}{Style.RESET_ALL}\n")

def normalize_text(text):
    """Normalize text using spaCy lemmatization."""
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
    label = result['label']  # e.g., "LABEL_0", "LABEL_1", etc.
    confidence = result['score']
    
    # Extract label number (e.g., "LABEL_0" -> 0)
    label_num = int(label.split('_')[1])
    
    # Convert label number to FAQ ID using inverted map
    # label_map has {faq_id: label_num}, we need {label_num: faq_id}
    inverted_map = {v: int(k) for k, v in label_map.items()}
    faq_id = inverted_map.get(label_num, -1)
    
    # Check threshold
    if confidence < threshold:
        return {
            "answer": "Lo siento, no entendí. Por favor intenta con otra pregunta.",
            "confidence": confidence,
            "type": "fallback",
            "faq_id": None,
            "domain": None
        }
    
    # Get FAQ
    faq = get_faq_by_id(faq_id)
    if not faq:
        return {
            "answer": "Error: FAQ no encontrado",
            "confidence": confidence,
            "type": "error",
            "faq_id": faq_id,
            "domain": None
        }
    
    # Check if it's news search
    if faq_id == 18:
        return {
            "answer": "🔍 BÚSQUEDA DE NOTICIAS (requiere MongoDB con datos de noticias)",
            "confidence": confidence,
            "type": "news_search",
            "faq_id": faq_id,
            "domain": faq.get("domain", "unknown")
        }
    
    # Return FAQ answer
    answer_text = faq.get("answer", {})
    if isinstance(answer_text, dict):
        answer_text = answer_text.get("es", str(answer_text))  # Use Spanish by default
    
    return {
        "answer": answer_text,
        "confidence": confidence,
        "type": "faq",
        "faq_id": faq_id,
        "domain": faq.get("domain", "unknown")
    }

def test_question(question):
    """Test a single question."""
    print(f"{Fore.YELLOW}Q: {question}{Style.RESET_ALL}")
    
    result = predict_answer(question)
    
    answer = result.get("answer", "No response")
    confidence = result.get("confidence", 0.0)
    response_type = result.get("type", "unknown")
    
    # Color based on type
    if response_type == "faq":
        color = Fore.GREEN
    elif response_type == "news_search":
        color = Fore.BLUE
    elif response_type == "fallback":
        color = Fore.YELLOW
    else:
        color = Fore.RED
    
    print(f"{color}A: {answer}{Style.RESET_ALL}")
    print(f"{Fore.WHITE}   Confidence: {confidence:.2%} | Type: {response_type} | FAQ ID: {result.get('faq_id', 'N/A')} | Domain: {result.get('domain', 'N/A')}{Style.RESET_ALL}")
    print()

def test_faq_samples():
    """Test sample questions from different FAQs."""
    print(f"\n{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'TEST 1: FAQ SAMPLES':^60}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}\n")
    
    test_questions = [
        "¿Qué es Lannister News?",
        "¿Cómo me registro?",
        "¿Puedo publicar una noticia?",
        "¿Cómo se verifica una noticia?",
        "¿Cuáles son los términos de servicio?",
    ]
    
    for q in test_questions:
        test_question(q)

def test_news_search():
    """Test news search questions."""
    print(f"\n{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'TEST 2: NEWS SEARCH (FAQ #18)':^60}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}\n")
    
    test_questions = [
        "Dame noticias de deportes",
        "Muéstrame las últimas noticias de tecnología",
        "Quiero ver noticias de moda",
        "Show me technology news",
        "What's the latest in sports?",
    ]
    
    for q in test_questions:
        test_question(q)

def test_edge_cases():
    """Test edge cases and low confidence scenarios."""
    print(f"\n{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'TEST 3: EDGE CASES':^60}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}\n")
    
    test_questions = [
        "asdfghjkl",  # Random text
        "¿Cuál es el sentido de la vida?",  # Out of domain
        "pizza",  # Single word
    ]
    
    for q in test_questions:
        test_question(q)

def interactive_mode():
    """Interactive testing mode."""
    print(f"\n{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'INTERACTIVE MODE':^60}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}\n")
    print(f"{Fore.WHITE}Type your questions below. Type 'exit' or 'quit' to stop.{Style.RESET_ALL}\n")
    
    while True:
        try:
            question = input(f"{Fore.CYAN}Your question: {Style.RESET_ALL}")
            if question.lower() in ['exit', 'quit', 'salir']:
                print(f"\n{Fore.GREEN}Goodbye!{Style.RESET_ALL}\n")
                break
            if question.strip():
                print()
                test_question(question)
        except KeyboardInterrupt:
            print(f"\n\n{Fore.GREEN}Goodbye!{Style.RESET_ALL}\n")
            break

def main():
    """Main test runner."""
    load_resources()
    
    print(f"{Fore.WHITE}Choose a test mode:{Style.RESET_ALL}")
    print(f"{Fore.WHITE}  1. Test FAQ samples{Style.RESET_ALL}")
    print(f"{Fore.WHITE}  2. Test news search{Style.RESET_ALL}")
    print(f"{Fore.WHITE}  3. Test edge cases{Style.RESET_ALL}")
    print(f"{Fore.WHITE}  4. Run all tests{Style.RESET_ALL}")
    print(f"{Fore.WHITE}  5. Interactive mode{Style.RESET_ALL}")
    print()
    
    try:
        choice = input(f"{Fore.CYAN}Select mode (1-5): {Style.RESET_ALL}").strip()
    except KeyboardInterrupt:
        print(f"\n\n{Fore.GREEN}Goodbye!{Style.RESET_ALL}\n")
        return
    
    if choice == '1':
        test_faq_samples()
    elif choice == '2':
        test_news_search()
    elif choice == '3':
        test_edge_cases()
    elif choice == '4':
        test_faq_samples()
        test_news_search()
        test_edge_cases()
    elif choice == '5':
        interactive_mode()
    else:
        print(f"{Fore.RED}Invalid choice. Exiting.{Style.RESET_ALL}")
    
    print(f"\n{Fore.GREEN}Testing completed!{Style.RESET_ALL}\n")

if __name__ == "__main__":
    main()
