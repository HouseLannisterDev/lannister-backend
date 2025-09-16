#!/usr/bin/env python
"""
Script para probar el chatbot rápidamente sin entrenar
Usa intents de ejemplo para verificar que todo funcione
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lannister_news_api.settings')
django.setup()

import json
import shutil
from chatBot.neural_network import NewsletterChatbot

def setup_test_environment():
    """Configura el entorno de prueba con intents de ejemplo"""
    print("🔧 Configurando entorno de prueba...")
    
    # Copiar intents de ejemplo
    source = 'intents_spanish_example.json'
    target = 'intents_spanish.json'
    
    if os.path.exists(source):
        shutil.copy(source, target)
        print(f"✅ Copiado {source} -> {target}")
    else:
        print(f"❌ No se encontró {source}")
        return False
    
    return True

def test_chatbot():
    """Prueba el chatbot con mensajes de ejemplo"""
    print("\n🤖 Probando chatbot...")
    
    # Inicializar chatbot
    chatbot = NewsletterChatbot()
    
    # Cargar intents
    if not chatbot.load_intents():
        print("❌ Error cargando intents")
        return
    
    # Entrenar con datos mínimos
    print("🧠 Entrenando modelo básico...")
    try:
        history = chatbot.train_model(epochs=50, batch_size=4)
        print("✅ Modelo entrenado")
    except Exception as e:
        print(f"❌ Error entrenando: {e}")
        return
    
    # Probar mensajes
    test_messages = [
        "hola",
        "noticias de política",
        "qué hay de deportes",
        "últimas noticias",
        "ayuda",
        "adiós"
    ]
    
    print("\n💬 Probando conversación:")
    print("-" * 50)
    
    for message in test_messages:
        try:
            response, intent, confidence = chatbot.get_response(message)
            print(f"👤 Usuario: {message}")
            print(f"🤖 Bot: {response}")
            print(f"📊 Intent: {intent} (Confianza: {confidence:.2f})")
            print("-" * 50)
        except Exception as e:
            print(f"❌ Error con mensaje '{message}': {e}")
    
    print("\n🎉 ¡Prueba completada!")

def interactive_chat():
    """Chat interactivo con el usuario"""
    print("\n💬 Modo chat interactivo (escribe 'quit' para salir)")
    
    chatbot = NewsletterChatbot()
    
    # Intentar cargar modelo existente
    if not chatbot.load_model():
        print("⚠️  No se encontró modelo pre-entrenado")
        print("🧠 Entrenando modelo básico...")
        
        if not chatbot.load_intents():
            print("❌ Error cargando intents")
            return
        
        try:
            chatbot.train_model(epochs=50, batch_size=4)
            print("✅ Modelo entrenado")
        except Exception as e:
            print(f"❌ Error entrenando: {e}")
            return
    else:
        if not chatbot.load_intents():
            print("❌ Error cargando intents")
            return
        print("✅ Modelo cargado exitosamente")
    
    print("\n🤖 Chatbot listo. ¡Escribe tu mensaje!")
    
    while True:
        try:
            message = input("\n👤 Tú: ").strip()
            
            if message.lower() in ['quit', 'salir', 'exit']:
                print("👋 ¡Hasta luego!")
                break
            
            if not message:
                continue
            
            response, intent, confidence = chatbot.get_response(message)
            print(f"🤖 Bot: {response}")
            print(f"📊 [{intent}] Confianza: {confidence:.2f}")
            
        except KeyboardInterrupt:
            print("\n👋 ¡Hasta luego!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")

def main():
    """Función principal"""
    print("🚀 Probador de ChatBot con IA")
    print("=" * 40)
    
    if len(sys.argv) > 1 and sys.argv[1] == '--interactive':
        # Modo interactivo
        if setup_test_environment():
            interactive_chat()
    else:
        # Modo de prueba automática
        if setup_test_environment():
            test_chatbot()
            
            # Preguntar si quiere modo interactivo
            answer = input("\n¿Quieres probar el chat interactivo? (y/n): ").lower()
            if answer in ['y', 'yes', 's', 'si', 'sí']:
                interactive_chat()

if __name__ == "__main__":
    main()
