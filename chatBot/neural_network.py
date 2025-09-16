# chatBot/neural_network.py
import json
import pickle
import numpy as np
import random
import logging
import os
from typing import List, Tuple, Dict, Any
import tensorflow as tf
from keras.models import Sequential, load_model
from keras.layers import Dense, Dropout
from keras.optimizers import SGD
from keras.optimizers.schedules import ExponentialDecay
from sklearn.preprocessing import LabelEncoder

try:
    import nltk
    from nltk.stem import WordNetLemmatizer
    nltk.download('punkt', quiet=True)
    nltk.download('wordnet', quiet=True)
    NLTK_AVAILABLE = True
except ImportError:
    NLTK_AVAILABLE = False

logger = logging.getLogger(__name__)

class NewsletterChatbot:
    """
    Chatbot especializado en noticias usando redes neuronales
    """
    
    def __init__(self, model_path: str = None):
        # Configuración de rutas relativas a la nueva estructura organizada
        chatbot_dir = os.path.dirname(os.path.abspath(__file__))
        self.model_path = model_path or os.path.join(chatbot_dir, 'models', 'chatbot_model.h5')
        self.words_path = os.path.join(chatbot_dir, 'models', 'words.pkl')
        self.classes_path = os.path.join(chatbot_dir, 'models', 'classes.pkl')
        self.intents_path = os.path.join(chatbot_dir, 'data', 'intents_spanish.json')
        
        # Inicializar lemmatizer si NLTK está disponible
        if NLTK_AVAILABLE:
            self.lemmatizer = WordNetLemmatizer()
        else:
            self.lemmatizer = None
            logger.warning("NLTK no disponible, usando limpieza básica de texto")
        
        # Variables del modelo
        self.model = None
        self.words = []
        self.classes = []
        self.intents = None
        
        # Configuración de entrenamiento
        self.ignore_words = ['?', '!', '.', ',']
        
        # Cargar intents automáticamente
        self.load_intents()
        
    def simple_tokenize(self, text: str) -> List[str]:
        """Tokenización simple si NLTK no está disponible"""
        import re
        # Dividir por espacios y limpiar caracteres especiales
        words = re.findall(r'\b\w+\b', text.lower())
        return words
    
    def simple_lemmatize(self, word: str) -> str:
        """Lemmatización simple si NLTK no está disponible"""
        # Reglas básicas de español
        if word.endswith('ando') or word.endswith('iendo'):
            return word[:-4] + 'ar'  # Simplificado
        elif word.endswith('ión'):
            return word[:-3] + 'ar'
        return word
    
    def preprocess_text(self, text: str) -> List[str]:
        """Preprocesa texto usando NLTK o métodos alternativos"""
        if NLTK_AVAILABLE and self.lemmatizer:
            # Usar NLTK
            words = nltk.word_tokenize(text)
            words = [self.lemmatizer.lemmatize(w.lower()) for w in words if w not in self.ignore_words]
        else:
            # Usar método simple
            words = self.simple_tokenize(text)
            words = [self.simple_lemmatize(w) for w in words if w not in self.ignore_words]
        
        return words
    
    def load_intents(self, intents_path: str = None):
        """Carga el archivo de intents"""
        path = intents_path or self.intents_path
        try:
            with open(path, 'r', encoding='utf-8') as file:
                self.intents = json.load(file)
            logger.info(f"Intents cargados desde {path}")
            return True
        except FileNotFoundError:
            logger.error(f"Archivo de intents no encontrado: {path}")
            return False
        except json.JSONDecodeError as e:
            logger.error(f"Error decodificando JSON: {e}")
            return False
    
    def prepare_training_data(self):
        """Prepara los datos para entrenar el modelo"""
        if not self.intents:
            raise ValueError("Primero debes cargar los intents")
        
        words = []
        classes = []
        documents = []
        
        # Procesar cada intent
        for intent in self.intents['intents']:
            for pattern in intent['patterns']:
                # Tokenizar las palabras del patrón
                w = self.preprocess_text(pattern)
                words.extend(w)
                # Agregar documento
                documents.append((w, intent['tag']))
                # Agregar clase si no existe
                if intent['tag'] not in classes:
                    classes.append(intent['tag'])
        
        # Limpiar y ordenar listas
        words = sorted(list(set(words)))
        classes = sorted(list(set(classes)))
        
        logger.info(f"Documentos: {len(documents)}")
        logger.info(f"Clases: {len(classes)} - {classes}")
        logger.info(f"Palabras únicas: {len(words)}")
        
        # Guardar palabras y clases
        pickle.dump(words, open(self.words_path, 'wb'))
        pickle.dump(classes, open(self.classes_path, 'wb'))
        
        # Crear datos de entrenamiento
        training = []
        output_empty = [0] * len(classes)
        
        for doc in documents:
            # Crear bolsa de palabras
            bag = []
            pattern_words = doc[0]
            
            for w in words:
                bag.append(1) if w in pattern_words else bag.append(0)
            
            # Crear vector de salida
            output_row = list(output_empty)
            output_row[classes.index(doc[1])] = 1
            
            training.append([bag, output_row])
        
        # Mezclar datos
        random.shuffle(training)
        training = np.array(training, dtype=object)
        
        # Dividir en X e Y
        train_x = list(training[:, 0])
        train_y = list(training[:, 1])
        
        self.words = words
        self.classes = classes
        
        return np.array(train_x), np.array(train_y)
    
    def build_model(self, input_shape: int, num_classes: int):
        """Construye la arquitectura del modelo"""
        model = Sequential()
        
        # Capa de entrada con más neuronas para mejor capacidad
        model.add(Dense(256, input_shape=(input_shape,), activation='relu'))
        model.add(Dropout(0.5))
        
        # Capas ocultas
        model.add(Dense(128, activation='relu'))
        model.add(Dropout(0.5))
        
        model.add(Dense(64, activation='relu'))
        model.add(Dropout(0.3))
        
        # Capa de salida
        model.add(Dense(num_classes, activation='softmax'))
        
        return model
    
    def train_model(self, epochs: int = 300, batch_size: int = 8, learning_rate: float = 0.01):
        """Entrena el modelo de red neuronal"""
        logger.info("Iniciando entrenamiento del modelo...")
        
        # Preparar datos
        train_x, train_y = self.prepare_training_data()
        
        # Construir modelo
        self.model = self.build_model(len(train_x[0]), len(train_y[0]))
        
        # Configurar optimizador con decay exponencial
        lr_schedule = ExponentialDecay(
            initial_learning_rate=learning_rate,
            decay_steps=100,
            decay_rate=0.96
        )
        
        sgd = SGD(learning_rate=lr_schedule, momentum=0.9, nesterov=True)
        
        # Compilar modelo
        self.model.compile(
            loss='categorical_crossentropy',
            optimizer=sgd,
            metrics=['accuracy']
        )
        
        # Entrenar
        history = self.model.fit(
            train_x, 
            train_y,
            epochs=epochs,
            batch_size=batch_size,
            verbose=1,
            validation_split=0.1  # 10% para validación
        )
        
        # Guardar modelo
        self.model.save(self.model_path)
        logger.info(f"Modelo guardado en {self.model_path}")
        
        return history
    
    def load_model(self):
        """Carga un modelo pre-entrenado"""
        try:
            self.model = load_model(self.model_path)
            self.words = pickle.load(open(self.words_path, 'rb'))
            self.classes = pickle.load(open(self.classes_path, 'rb'))
            logger.info("Modelo cargado exitosamente")
            return True
        except Exception as e:
            logger.error(f"Error cargando modelo: {e}")
            return False
    
    def clean_up_sentence(self, sentence: str) -> List[str]:
        """Limpia y tokeniza una oración"""
        return self.preprocess_text(sentence)
    
    def bow(self, sentence: str, show_details: bool = True) -> np.ndarray:
        """Convierte una oración en bolsa de palabras"""
        sentence_words = self.clean_up_sentence(sentence)
        bag = [0] * len(self.words)
        
        for s in sentence_words:
            for i, w in enumerate(self.words):
                if w == s:
                    bag[i] = 1
                    if show_details:
                        logger.debug(f"Encontrada palabra: {w}")
        
        return np.array(bag)
    
    def predict_class(self, sentence: str, threshold: float = 0.25) -> List[Dict[str, Any]]:
        """Predice la clase/intent de una oración"""
        if not self.model:
            raise ValueError("Modelo no cargado")
        
        # Generar predicción
        p = self.bow(sentence, show_details=False)
        res = self.model.predict(np.array([p]))[0]
        
        # Filtrar predicciones por umbral
        results = [[i, r] for i, r in enumerate(res) if r > threshold]
        
        # Ordenar por probabilidad
        results.sort(key=lambda x: x[1], reverse=True)
        
        return_list = []
        for r in results:
            return_list.append({
                "intent": self.classes[r[0]], 
                "probability": str(r[1])
            })
        
        return return_list
    
    def get_response(self, message: str) -> Tuple[str, str, float]:
        """Obtiene respuesta del chatbot"""
        if not self.intents:
            return "Error: Intents no cargados", "error", 0.0
        
        # Detectar palabras clave directamente para mayor precisión
        message_lower = message.lower()
        
        # Mapeo directo de palabras clave a categorías
        keyword_mapping = {
            "Deportes": ["deporte", "deportes", "futbol", "fútbol", "seleccion", "selección", "colombia", "partido", "liga", "campeonato", "atletismo", "natacion", "basquet", "tenis", "messi", "ronaldo", "barcelona", "madrid", "gol", "goles", "mundial", "copa", "champions", "pelota", "balon", "balón", "arquero", "portero", "delantero", "james", "falcao", "cuadrado"],
            "Tecnología": ["tecnologia", "tecnología", "tech", "software", "hardware", "app", "apps", "inteligencia", "artificial", "programacion", "desarrollo"],
            "Moda": ["moda", "fashion", "tendencia", "tendencias", "ropa", "diseño", "estilo", "pasarela"],
            "Animales": ["animal", "animales", "mascota", "mascotas", "perro", "gato", "fauna", "vida silvestre", "conservacion"],
            "Judiciales": ["judicial", "judiciales", "ley", "legal", "tribunal", "justicia", "crimen", "investigacion", "policia"]
        }
        
        # Mapeo de emociones a sentimientos
        sentiment_mapping = {
            "positivas": "POSITIVE",
            "buenas": "POSITIVE", 
            "felices": "POSITIVE",
            "alegres": "POSITIVE",
            "optimistas": "POSITIVE",
            "negativas": "NEGATIVE",
            "tristes": "NEGATIVE",
            "malas": "NEGATIVE",
            "pesimistas": "NEGATIVE",
            "deprimentes": "NEGATIVE",
            "neutrales": "NEUTRAL"
        }
        
        # Buscar palabras clave en el mensaje
        detected_category = None
        detected_sentiment = None
        is_football_specific = False  # Nuevo: detectar si es específicamente fútbol
        keyword_confidence = 0.8  # Alta confianza para detección directa
        
        # Palabras específicas de fútbol para respuestas enfáticas
        football_keywords = ["futbol", "fútbol", "messi", "ronaldo", "barcelona", "madrid", "gol", "goles", "mundial", "copa", "champions", "pelota", "balon", "balón", "arquero", "portero", "delantero", "james", "falcao", "cuadrado", "seleccion", "selección"]
        
        # Detectar categoría (búsqueda de palabras completas)
        import re
        for category, keywords in keyword_mapping.items():
            for keyword in keywords:
                # Usar regex para buscar palabras completas
                pattern = r'\b' + re.escape(keyword) + r'\b'
                if re.search(pattern, message_lower):
                    detected_category = category
                    logger.info(f"Detectada categoría: {keyword} -> {category}")
                    
                    # Verificar si es específicamente fútbol
                    if category == "Deportes" and keyword in football_keywords:
                        is_football_specific = True
                        logger.info(f"¡Detectado como consulta específica de fútbol!")
                    break
            if detected_category:
                break
        
        # Detectar sentimiento (búsqueda de palabras completas)
        for emotion, sentiment in sentiment_mapping.items():
            # Usar regex para buscar palabras completas
            pattern = r'\b' + re.escape(emotion) + r'\b'
            if re.search(pattern, message_lower):
                detected_sentiment = sentiment
                logger.info(f"Detectado sentimiento: {emotion} -> {sentiment}")
                break
        
        # Si detectamos una categoría por palabra clave, úsala
        if detected_category or detected_sentiment:
            if detected_category:
                tag = detected_category
                logger.info(f"Usando categoría detectada: {tag}")
            elif detected_sentiment:
                tag = f"sentiment_{detected_sentiment.lower()}"
                logger.info(f"Usando sentimiento detectado: {tag}")
            confidence = keyword_confidence
        else:
            # Fallback al modelo entrenado
            ints = self.predict_class(message)
            if not ints:
                tag = "no_entiendo"
                confidence = 0.0
            else:
                tag = ints[0]['intent']
                confidence = float(ints[0]['probability'])
        
        # Categorías que requieren búsqueda de noticias
        news_categories = ["Deportes", "Tecnología", "Moda", "Animales", "Judiciales"]
        sentiment_categories = ["sentiment_positive", "sentiment_negative", "sentiment_neutral"]
        sentiment_tags = ["sentimiento_positivo", "sentimiento_negativo"]
        
        logger.info(f"Tag detectado: {tag}, Categorías de noticias: {news_categories}, Categorías de sentimiento: {sentiment_categories}")
        
        if tag in news_categories or tag in sentiment_categories or tag in sentiment_tags:
            # Buscar noticias reales en la base de datos
            try:
                from mongo_client import get_mongo_client
                client = get_mongo_client()
                news_collection = client["news"]
                
                # Construir query de búsqueda
                query = {}
                if tag in news_categories:
                    query["category"] = tag
                    
                    # Mejorar consulta para fútbol específico
                    if tag == "Deportes" and is_football_specific:
                        # Buscar noticias que contengan términos futbolísticos específicos
                        football_terms = r"\b(fútbol|soccer|gol|barcelona|madrid|messi|ronaldo|champions|liga|mundial|eurocopa|premier|laliga|serie a|bundesliga|ligue 1|copa|balón|equipo|partido|estadio|entrenador|jugador|delantero|defensa|portero|árbitro|penalti|offside|corner|tarjeta|expulsión|lesión|fichaje|transferencia|mercado|contrato|salario|directiva|afición|hinchada|ultras|clásico|derbi|final|semifinal|cuartos|octavos|grupo|clasificación|tabla|puntos|goles|asistencias|mvp|mejor jugador|estrella|crack|genio|fenómeno)\b"
                        query = {
                            "category": tag,
                            "$or": [
                                {"title": {"$regex": football_terms, "$options": "i"}},
                                {"content": {"$regex": football_terms, "$options": "i"}},
                                {"summary": {"$regex": football_terms, "$options": "i"}}
                            ]
                        }
                    
                    logger.info(f"Buscando por categoría: {tag}")
                elif tag in sentiment_categories:
                    sentiment_label = tag.split("_")[1].upper()
                    query["sentiment.label"] = sentiment_label
                    logger.info(f"Buscando por sentimiento: {sentiment_label}")
                elif tag in sentiment_tags:
                    # Convertir tags de sentimiento del archivo intents a labels de MongoDB
                    if tag == "sentimiento_positivo":
                        sentiment_label = "POSITIVE"
                    elif tag == "sentimiento_negativo":
                        sentiment_label = "NEGATIVE"
                    else:
                        sentiment_label = "NEUTRAL"
                    query["sentiment.label"] = sentiment_label
                    logger.info(f"Buscando por sentimiento desde intents: {sentiment_label}")
                
                logger.info(f"Query MongoDB: {query}")
                
                # Buscar noticias
                news_docs = list(news_collection.find(
                    query, 
                    {"title": 1, "description": 1, "url": 1, "source_domain": 1, "sentiment": 1, "publishedAt": 1}
                ).limit(3))
                
                logger.info(f"Documentos encontrados: {len(news_docs)}")
                for doc in news_docs:
                    logger.info(f"Noticia: {doc.get('title', 'Sin título')} - Sentimiento: {doc.get('sentiment', 'N/A')}")
                
                if news_docs:
                    # Definir nombres de sentimientos
                    sentiment_names = {"positive": "positivas", "negative": "tristes/negativas", "neutral": "neutrales"}
                    
                    # Formatear respuesta con noticias reales
                    if tag in news_categories:
                        # Respuestas enfáticas específicas para fútbol
                        if tag == "Deportes" and is_football_specific:
                            intro = random.choice([
                                f"⚽ ¡Aquí tienes las últimas noticias de fútbol!",
                                f"🥅 ¡Te traigo lo más hot del mundo del fútbol!",
                                f"🏆 ¡Prepárate para las mejores noticias futboleras!",
                                f"⚽ ¡Lo más reciente del fútbol para ti!",
                                f"🔥 ¡Las noticias más calientes del fútbol!",
                                f"⚽ ¡Aquí está toda la actualidad futbolística!"
                            ])
                        else:
                            intro = random.choice([
                                f"📰 Aquí tienes las últimas noticias de {tag}:",
                                f"📰 Te muestro las novedades más recientes de {tag}:",
                                f"📰 Estas son las noticias más actuales sobre {tag}:"
                            ])
                    elif tag in sentiment_categories:
                        sentiment_label = tag.split("_")[1]
                        sentiment_name = sentiment_names.get(sentiment_label.lower(), sentiment_label.lower())
                        intro = random.choice([
                            f"😊 Aquí tienes noticias {sentiment_name}:",
                            f"💭 Te muestro noticias con tono {sentiment_name}:",
                            f"📰 Estas son noticias {sentiment_name} que encontré:"
                        ])
                    elif tag in sentiment_tags:
                        if tag == "sentimiento_positivo":
                            intro = random.choice([
                                "😊 Aquí tienes noticias positivas:",
                                "🌟 Te muestro noticias que te alegrarán:",
                                "✨ Estas son noticias optimistas para ti:"
                            ])
                        elif tag == "sentimiento_negativo":
                            intro = random.choice([
                                "😔 Aquí tienes noticias con tono más serio:",
                                "📰 Te muestro noticias de actualidad que requieren atención:",
                                "⚠️ Estas son noticias importantes aunque no sean positivas:"
                            ])
                        else:
                            intro = "📰 Aquí tienes noticias neutrales:"
                    
                    news_items = []
                    for i, news in enumerate(news_docs, 1):
                        title = news.get('title', 'Sin título')
                        description = news.get('description', '')
                        url = news.get('url', '')
                        source = news.get('source_domain', 'Fuente desconocida')
                        sentiment_info = news.get('sentiment', {})
                        
                        # Truncar descripción si es muy larga
                        if description and len(description) > 150:
                            description = description[:147] + "..."
                        
                        # Formatear item de noticia con personalización para fútbol
                        if tag == "Deportes" and is_football_specific:
                            news_item = f"⚽ **{i}. {title}**"
                        else:
                            news_item = f"**{i}. {title}**"
                            
                        if description:
                            news_item += f"\n📝 {description}"
                        
                        # Añadir información de sentimiento si se busca por sentimiento
                        if (tag in sentiment_categories or tag in sentiment_tags) and sentiment_info:
                            sentiment_emoji = {"POSITIVE": "😊", "NEGATIVE": "😔", "NEUTRAL": "😐"}.get(sentiment_info.get('label', ''), '')
                            news_item += f"\n{sentiment_emoji} Sentimiento: {sentiment_info.get('label', 'N/A')} ({sentiment_info.get('score', 0):.2f})"
                        
                        # URLs personalizadas para fútbol
                        if tag == "Deportes" and is_football_specific:
                            news_item += f"\n🏆 **¡Leer más!:** {url}"
                        else:
                            news_item += f"\n🔗 **Leer más:** {url}"
                            
                        news_item += f"\n📍 **Fuente:** {source}"
                        
                        news_items.append(news_item)
                    
                    result = intro + "\n\n" + "\n\n".join(news_items)
                    
                    # Añadir sugerencia personalizada al final
                    if tag == "Deportes" and is_football_specific:
                        result += f"\n\n⚽ *¿Quieres saber sobre algún equipo o jugador específico? ¡Pregúntame!*"
                    elif tag in sentiment_categories or tag in sentiment_tags:
                        result += f"\n\n💡 *¿Te gustaría ver noticias de algún tema específico?*"
                    else:
                        result += f"\n\n💡 *¿Te interesa alguna noticia en particular?*"
                    
                    return result, tag, confidence
                else:
                    # No hay noticias de esa categoría/sentimiento con respuesta especial para fútbol
                    sentiment_names = {"positive": "positivas", "negative": "tristes/negativas", "neutral": "neutrales"}
                    
                    if tag in news_categories:
                        if tag == "Deportes" and is_football_specific:
                            result = f"⚽ ¡Ups! No encontré noticias específicas de fútbol en este momento. Pero puedo ayudarte con noticias deportivas en general o sobre otros temas. ¿Qué prefieres?"
                        else:
                            result = f"No encontré noticias recientes sobre {tag}. ¿Te interesa algún otro tema?"
                    elif tag in sentiment_categories:
                        sentiment_label = tag.split("_")[1]
                        sentiment_name = sentiment_names.get(sentiment_label.lower(), sentiment_label.lower())
                        result = f"No encontré noticias {sentiment_name} en este momento. ¿Te interesa algún tema específico?"
                    elif tag in sentiment_tags:
                        if tag == "sentimiento_positivo":
                            result = "No encontré noticias positivas en este momento. ¿Te interesa algún tema específico?"
                        elif tag == "sentimiento_negativo":
                            result = "No encontré noticias negativas en este momento. ¿Te interesa algún tema específico?"
                        else:
                            result = "No encontré noticias neutrales en este momento. ¿Te interesa algún tema específico?"
                    return result, tag, confidence
                    
            except Exception as e:
                logger.error(f"Error buscando noticias: {e}")
                # Fallback a respuesta predefinida
                pass
        
        # Buscar respuestas predefinidas para otros intents
        list_of_intents = self.intents['intents']
        result = "Lo siento, no entendí tu pregunta."
        
        for i in list_of_intents:
            if i['tag'] == tag:
                result = random.choice(i['responses'])
                break
        
        return result, tag, confidence
    
    def chat(self):
        """Inicia una sesión de chat interactiva"""
        print("¡Chatbot de Noticias iniciado! (escribe 'quit' para salir)")
        
        while True:
            message = input("Tú: ")
            if message.lower() == 'quit':
                break
            
            response, intent, confidence = self.get_response(message)
            print(f"Bot: {response}")
            print(f"[Intent: {intent}, Confianza: {confidence:.2f}]")
    
    def evaluate_model(self, test_sentences: List[Tuple[str, str]]) -> Dict[str, float]:
        """Evalúa el rendimiento del modelo con oraciones de prueba"""
        correct = 0
        total = len(test_sentences)
        
        for sentence, expected_intent in test_sentences:
            _, predicted_intent, confidence = self.get_response(sentence)
            if predicted_intent == expected_intent:
                correct += 1
        
        accuracy = correct / total if total > 0 else 0
        
        return {
            "accuracy": accuracy,
            "correct": correct,
            "total": total
        }
