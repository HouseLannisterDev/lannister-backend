from pymongo import MongoClient
from pymongo.server_api import ServerApi
from django.conf import settings

def get_mongo_client():
    if settings.MONGO_DB.get("URI"):  
        # Conexión a MongoDB Atlas usando URI
        client = MongoClient(settings.MONGO_DB["URI"], server_api=ServerApi('1'))
    else:  
        # Conexión local tradicional
        client = MongoClient(settings.MONGO_DB["HOST"], settings.MONGO_DB["PORT"])
    
    return client[settings.MONGO_DB["NAME"]]

def test_mongo_connection():
    """Función para probar la conexión a MongoDB Atlas"""
    try:
        if settings.MONGO_DB.get("URI"):
            client = MongoClient(settings.MONGO_DB["URI"], server_api=ServerApi('1'))
            client.admin.command('ping')
            print("✅ Conexión exitosa a MongoDB Atlas!")
            return True
        else:
            print("⚠️ Usando conexión local de MongoDB")
            return True
    except Exception as e:
        print(f"❌ Error conectando a MongoDB: {e}")
        return False
