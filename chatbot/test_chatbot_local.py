"""
Script para probar el chatbot localmente (sin servidor Django).
Ejecutar: python chatbot/test_chatbot_local.py
"""

from chatbot.services.chatbot_factory import ChatbotFactory
from colorama import init, Fore, Style
import sys
import os

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Inicializar colorama para colores en terminal
try:
    init(autoreset=True)
except:
    pass

def print_header(text):
    """Imprime un encabezado bonito."""
    print("\n" + "=" * 70)
    print(f"{Fore.CYAN}{Style.BRIGHT}{text}")
    print("=" * 70)

def print_result(result):
    """Imprime el resultado de manera formateada."""
    print(f"\n{Fore.GREEN}📝 Respuesta:")
    print(f"{Style.BRIGHT}{result['answer']}")
    print(f"\n{Fore.YELLOW}📊 Metadata:")
    print(f"   • Confianza: {result['confidence']:.2%}")
    print(f"   • Tipo: {result['type']}")
    if result.get('category'):
        print(f"   • Categoría: {result['category']}")
    if result.get('count'):
        print(f"   • Noticias encontradas: {result['count']}")

def test_faqs():
    """Prueba las FAQs estáticas."""
    print_header("🧪 PROBANDO FAQs ESTÁTICAS")
    
    service = ChatbotFactory.create()
    
    test_questions = [
        "¿Qué es Lannister News?",
        "Who developed this?",
        "Hola",
        "Gracias",
        "Cómo clasifican las noticias",
    ]
    
    for idx, question in enumerate(test_questions, 1):
        print(f"\n{Fore.BLUE}Pregunta {idx}: {question}")
        try:
            result = service.get_answer(question)
            print_result(result)
        except Exception as e:
            print(f"{Fore.RED}❌ Error: {str(e)}")

def test_news_search():
    """Prueba la búsqueda de noticias."""
    print_header("🔍 PROBANDO BÚSQUEDA DE NOTICIAS")
    
    service = ChatbotFactory.create()
    
    test_questions = [
        "dame noticias de deportes",
        "muéstrame moda",
        "give me tech news",
        "quiero ver animales",
        "búscame judiciales",
        "show me sports",
    ]
    
    for idx, question in enumerate(test_questions, 1):
        print(f"\n{Fore.BLUE}Pregunta {idx}: {question}")
        try:
            result = service.get_answer(question)
            print_result(result)
        except Exception as e:
            print(f"{Fore.RED}❌ Error: {str(e)}")

def interactive_mode():
    """Modo interactivo para probar preguntas personalizadas."""
    print_header("💬 MODO INTERACTIVO")
    print(f"{Fore.YELLOW}Escribe 'salir' o 'exit' para terminar\n")
    
    service = ChatbotFactory.create()
    
    while True:
        try:
            question = input(f"{Fore.GREEN}Tu pregunta: {Style.RESET_ALL}")
            
            if question.lower() in ['salir', 'exit', 'quit']:
                print(f"\n{Fore.CYAN}¡Hasta luego! 👋")
                break
            
            if not question.strip():
                continue
            
            result = service.get_answer(question)
            print_result(result)
            
        except KeyboardInterrupt:
            print(f"\n\n{Fore.CYAN}¡Hasta luego! 👋")
            break
        except Exception as e:
            print(f"{Fore.RED}❌ Error: {str(e)}")

def main():
    """Función principal."""
    print_header("🤖 TEST DEL CHATBOT LANNISTER NEWS")
    
    print(f"\n{Fore.YELLOW}Selecciona una opción:")
    print(f"  1. Probar FAQs estáticas")
    print(f"  2. Probar búsqueda de noticias")
    print(f"  3. Probar todo")
    print(f"  4. Modo interactivo")
    
    try:
        choice = input(f"\n{Fore.GREEN}Opción (1-4): {Style.RESET_ALL}").strip()
        
        if choice == '1':
            test_faqs()
        elif choice == '2':
            test_news_search()
        elif choice == '3':
            test_faqs()
            test_news_search()
        elif choice == '4':
            interactive_mode()
        else:
            print(f"{Fore.RED}Opción inválida")
            
    except KeyboardInterrupt:
        print(f"\n\n{Fore.CYAN}¡Hasta luego! 👋")
    except Exception as e:
        print(f"{Fore.RED}❌ Error: {str(e)}")

if __name__ == "__main__":
    # Configurar Django antes de usar el chatbot
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lannister_news_api.settings')
    import django
    django.setup()
    
    main()
