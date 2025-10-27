workspace "Lannister News Backend" "Arquitectura del sistema de noticias" {

    model {
        # Actores
        user = person "Usuario" "Usuario de la aplicación web/mobile"
        
        # Sistemas Externos
        gnews = softwareSystem "GNEWS API" "API externa de noticias" "External"
        huggingface = softwareSystem "HuggingFace" "Modelo ML DistilBERT" "External"
        
        # Sistema Principal
        lannisterBackend = softwareSystem "Lannister Backend" "API REST para gestión de noticias, usuarios y chatbot" {
            
            # Contenedores
            nginx = container "NGINX" "Reverse Proxy" "NGINX" "Gateway" {
                tags "Infrastructure"
            }
            
            djangoApp = container "Django Application" "API REST" "Django 5.2.5, Python 3.12" {
                
                # Componentes
                router = component "URL Router" "Enrutamiento de peticiones" "Django URLs"
                middleware = component "Middleware Stack" "CORS, CSRF, Sessions, Auth" "Django Middleware"
                
                # News Module
                newsViews = component "News Views" "Endpoints de noticias" "Django Views"
                newsService = component "News Service" "Lógica de negocio noticias" "Python"
                newsRepo = component "News Repository" "Acceso a datos noticias" "PyMongo"
                
                # Chatbot Module
                chatbotViews = component "Chatbot Views" "Endpoints chatbot" "Django Views"
                chatbotFactory = component "Chatbot Factory" "Creación de servicio chatbot" "Factory Pattern"
                chatbotService = component "Chatbot Service" "Lógica ML + Búsqueda" "Python"
                faqManager = component "FAQ Manager" "Gestión de FAQs" "Python"
                modelProvider = component "Model Provider" "Proveedor ML Model" "Singleton Pattern"
                newsSearchService = component "News Search Service" "Búsqueda de noticias" "Python"
                
                # Users Module
                userViews = component "User Views" "Endpoints usuarios" "Django ViewSet"
                authViews = component "Auth Views" "Autenticación" "Django REST"
                serializers = component "Serializers" "Serialización datos" "DRF Serializers"
                
                # Relaciones internas
                router -> newsViews "Enruta"
                router -> chatbotViews "Enruta"
                router -> userViews "Enruta"
                router -> authViews "Enruta"
                
                newsViews -> newsService "Usa"
                newsService -> newsRepo "Usa"
                
                chatbotViews -> chatbotFactory "Crea"
                chatbotFactory -> chatbotService "Instancia"
                chatbotService -> faqManager "Consulta"
                chatbotService -> modelProvider "Clasifica"
                chatbotService -> newsSearchService "Busca"
                newsSearchService -> newsRepo "Consulta"
                
                userViews -> serializers "Serializa"
                authViews -> serializers "Serializa"
            }
            
            mysqlDB = container "MySQL Database" "Datos relacionales" "MySQL 8.0 (AWS RDS)" "Database"
            mongoDB = container "MongoDB" "Noticias y metadata" "MongoDB Atlas" "Database"
            redis = container "Redis Cache" "Sesiones y cache" "Redis 7.x (ElastiCache)" "Cache"
            
            scraper = container "News Scraper" "Scraping automatizado" "Python Script"
            
            # Relaciones entre contenedores
            nginx -> djangoApp "Forward HTTPS" "HTTPS"
            
            djangoApp -> mysqlDB "Lee/Escribe" "MySQL Protocol"
            djangoApp -> mongoDB "Lee/Escribe" "MongoDB Protocol"
            djangoApp -> redis "Cache/Sessions" "Redis Protocol"
            
            newsRepo -> mongoDB "Query"
            serializers -> mysqlDB "ORM"
            middleware -> redis "Sessions"
            
            modelProvider -> huggingface "Carga modelo"
            scraper -> gnews "Fetch articles" "HTTPS/REST"
            scraper -> mongoDB "Inserta noticias"
        }
        
        # Relaciones de usuario
        user -> nginx "Usa" "HTTPS"
        
        # Tags
        tags "Backend"
    }

    views {
        systemContext lannisterBackend "SystemContext" {
            include *
            autoLayout
        }
        
        container lannisterBackend "Containers" {
            include *
            autoLayout
        }
        
        component djangoApp "Components" {
            include *
            autoLayout
        }
        
        styles {
            element "Software System" {
                background #1168bd
                color #ffffff
            }
            element "External" {
                background #999999
                color #ffffff
            }
            element "Container" {
                background #438dd5
                color #ffffff
            }
            element "Component" {
                background #85bbf0
                color #000000
            }
            element "Database" {
                shape Cylinder
                background #ff6b6b
                color #ffffff
            }
            element "Cache" {
                shape Cylinder
                background #51cf66
                color #ffffff
            }
            element "Infrastructure" {
                background #f59f00
                color #ffffff
            }
        }
    }
}
