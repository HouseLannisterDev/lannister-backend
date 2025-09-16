#!/usr/bin/env python
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lannister_news_api.settings')
django.setup()

from chatBot.neural_network import ChatbotNeuralNetwork
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def retrain_model():
    print("🚀 Reentrenando el modelo con los nuevos intents...")
    
    try:
        # Crear instancia del chatbot
        chatbot = ChatbotNeuralNetwork()
        
        # Entrenar el modelo
        chatbot.train_model(epochs=200, batch_size=8, learning_rate=0.01)
        
        print("✅ Modelo entrenado exitosamente!")
        
        # Probar con algunas consultas
        test_messages = [
            "dame malas noticias",
            "dame buenas noticias", 
            "noticias de deportes",
            "hola",
            "gracias"
        ]
        
        print("\n🧪 Probando el modelo:")
        for message in test_messages:
            response, intent, confidence = chatbot.get_response(message)
            print(f"'{message}' -> Intent: {intent}, Confidence: {confidence:.2f}")
            print(f"Respuesta: {response[:100]}...")
            print("-" * 50)
            
    except Exception as e:
        logger.error(f"Error durante el entrenamiento: {e}")
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    retrain_model()
