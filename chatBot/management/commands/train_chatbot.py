# chatBot/management/commands/train_chatbot.py
from django.core.management.base import BaseCommand
from django.conf import settings
import os
import logging
from chatBot.data_preprocessor import NewsDataPreprocessor
from chatBot.neural_network import NewsletterChatbot

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Entrena el chatbot con datos de noticias de MongoDB'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--news_limit',
            type=int,
            default=10000,
            help='Límite de noticias a procesar (default: 10000)'
        )
        parser.add_argument(
            '--epochs',
            type=int,
            default=200,
            help='Número de épocas para entrenamiento (default: 200)'
        )
        parser.add_argument(
            '--batch_size',
            type=int,
            default=8,
            help='Tamaño del batch (default: 8)'
        )
        parser.add_argument(
            '--learning_rate',
            type=float,
            default=0.01,
            help='Tasa de aprendizaje (default: 0.01)'
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Forzar entrenamiento aunque ya exista un modelo'
        )
    
    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('🤖 Iniciando entrenamiento del chatbot...')
        )
        
        try:
            # 1. Generar intents desde datos de noticias
            self.stdout.write('📊 Procesando datos de noticias...')
            preprocessor = NewsDataPreprocessor()
            
            # Obtener estadísticas
            stats = preprocessor.get_news_statistics()
            self.stdout.write(
                f"📈 Total de noticias en BD: {stats['total_news']}"
            )
            self.stdout.write(
                f"📈 Categorías encontradas: {stats['total_categories']}"
            )
            
            # Generar intents
            intents_data = preprocessor.generate_intents_from_news(
                limit=options['news_limit']
            )
            
            if not intents_data['intents']:
                self.stdout.write(
                    self.style.ERROR('❌ No se pudieron generar intents. Verifica la conexión a MongoDB.')
                )
                return
            
            # Guardar intents
            intents_file = 'intents_spanish.json'
            if preprocessor.save_intents_to_file(intents_data, intents_file):
                self.stdout.write(
                    self.style.SUCCESS(f'✅ Intents guardados en {intents_file}')
                )
            else:
                self.stdout.write(
                    self.style.ERROR('❌ Error guardando intents')
                )
                return
            
            # 2. Entrenar red neuronal
            self.stdout.write('🧠 Entrenando red neuronal...')
            chatbot = NewsletterChatbot()
            
            # Cargar intents
            if not chatbot.load_intents(intents_file):
                self.stdout.write(
                    self.style.ERROR('❌ Error cargando intents para entrenamiento')
                )
                return
            
            # Entrenar modelo
            history = chatbot.train_model(
                epochs=options['epochs'],
                batch_size=options['batch_size'],
                learning_rate=options['learning_rate']
            )
            
            # Mostrar métricas finales
            final_accuracy = history.history['accuracy'][-1]
            final_loss = history.history['loss'][-1]
            
            if 'val_accuracy' in history.history:
                final_val_accuracy = history.history['val_accuracy'][-1]
                self.stdout.write(
                    f"📊 Precisión final (validación): {final_val_accuracy:.4f}"
                )
            
            self.stdout.write(
                f"📊 Precisión final: {final_accuracy:.4f}"
            )
            self.stdout.write(
                f"📊 Pérdida final: {final_loss:.4f}"
            )
            
            # 3. Probar el modelo
            self.stdout.write('🧪 Probando el modelo...')
            test_messages = [
                "hola",
                "noticias de política",
                "qué hay de deportes",
                "últimas noticias",
                "adiós"
            ]
            
            for message in test_messages:
                response, intent, confidence = chatbot.get_response(message)
                self.stdout.write(
                    f"👤 '{message}' -> 🤖 '{response[:100]}...' (Intent: {intent}, Confianza: {confidence:.2f})"
                )
            
            self.stdout.write(
                self.style.SUCCESS('🎉 ¡Entrenamiento completado exitosamente!')
            )
            
            # Mostrar archivos generados
            self.stdout.write('\n📁 Archivos generados:')
            for filename in ['chatbot_model.h5', 'words.pkl', 'classes.pkl', 'intents_spanish.json']:
                if os.path.exists(filename):
                    size = os.path.getsize(filename) / 1024  # KB
                    self.stdout.write(f"  ✅ {filename} ({size:.1f} KB)")
                else:
                    self.stdout.write(f"  ❌ {filename} (no encontrado)")
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Error durante el entrenamiento: {str(e)}')
            )
            logger.exception("Error en entrenamiento del chatbot")
            raise
