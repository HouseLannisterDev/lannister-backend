"""
Script para entrenar el modelo BERT del chatbot con las FAQs.
Crea un clasificador de 18 categorías (incluyendo búsqueda de noticias).

Uso:
    python chatbot/train_chatbot.py

Requisitos:
    - transformers
    - torch
    - scikit-learn
"""

import json
import os
import torch
from pathlib import Path
from sklearn.model_selection import train_test_split
from transformers import (
    AutoTokenizer,
    AutoModelForSequenceClassification,
    TrainingArguments,
    Trainer,
)
from torch.utils.data import Dataset
import numpy as np


# ================================
# 1. CONFIGURACIÓN
# ================================
BASE_DIR = Path(__file__).resolve().parent.parent
FAQ_NORMALIZED_PATH = BASE_DIR / "chatbot/faqs/faqs_normalized.json"
MODEL_OUTPUT_PATH = BASE_DIR / "chatbot/faq_model_2"

# Modelo base multilingüe
MODEL_NAME = "bert-base-multilingual-uncased"

# Hiperparámetros
NUM_EPOCHS = 8
BATCH_SIZE = 16
LEARNING_RATE = 2e-5
MAX_LENGTH = 128  # Tokens máximos por pregunta


# ================================
# 2. CARGAR Y PREPARAR DATASET
# ================================
def load_faqs(path):
    """Carga el archivo JSON de FAQs normalizadas."""
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data["faqs"]


def prepare_dataset(faqs):
    """
    Convierte las FAQs en un dataset de entrenamiento.
    
    Returns:
        texts: Lista de preguntas normalizadas
        labels: Lista de labels (0-17)
        label_map: Mapeo de FAQ id a label
    """
    texts = []
    labels = []
    label_map = {}
    
    for idx, faq in enumerate(faqs):
        faq_id = faq["id"]
        label_map[faq_id] = idx
        
        # Preguntas en español
        for question in faq["questions"]["es"]:
            texts.append(question)
            labels.append(idx)
        
        # Preguntas en inglés
        for question in faq["questions"]["en"]:
            texts.append(question)
            labels.append(idx)
    
    return texts, labels, label_map


# ================================
# 3. DATASET DE PYTORCH
# ================================
class FAQDataset(Dataset):
    """Dataset de PyTorch para las FAQs."""
    
    def __init__(self, texts, labels, tokenizer, max_length=128):
        self.texts = texts
        self.labels = labels
        self.tokenizer = tokenizer
        self.max_length = max_length
    
    def __len__(self):
        return len(self.texts)
    
    def __getitem__(self, idx):
        text = self.texts[idx]
        label = self.labels[idx]
        
        encoding = self.tokenizer(
            text,
            add_special_tokens=True,
            max_length=self.max_length,
            padding="max_length",
            truncation=True,
            return_tensors="pt"
        )
        
        return {
            "input_ids": encoding["input_ids"].flatten(),
            "attention_mask": encoding["attention_mask"].flatten(),
            "labels": torch.tensor(label, dtype=torch.long)
        }


# ================================
# 4. MÉTRICAS DE EVALUACIÓN
# ================================
def compute_metrics(eval_pred):
    """Calcula accuracy durante el entrenamiento."""
    logits, labels = eval_pred
    predictions = np.argmax(logits, axis=-1)
    accuracy = np.mean(predictions == labels)
    return {"accuracy": accuracy}


# ================================
# 5. ENTRENAMIENTO
# ================================
def train_model():
    """Entrena el modelo BERT con las FAQs."""
    
    print("=" * 60)
    print("🚀 ENTRENAMIENTO DEL CHATBOT LANNISTER NEWS")
    print("=" * 60)
    
    # 1. Cargar FAQs
    print("\n📚 Cargando FAQs...")
    faqs = load_faqs(FAQ_NORMALIZED_PATH)
    num_labels = len(faqs)
    print(f"   ✅ {num_labels} FAQs cargadas (incluyendo búsqueda de noticias)")
    
    # 2. Preparar dataset
    print("\n🔧 Preparando dataset...")
    texts, labels, label_map = prepare_dataset(faqs)
    print(f"   ✅ {len(texts)} preguntas totales")
    print(f"   ✅ Distribución: {len(texts) // num_labels} preguntas promedio por FAQ")
    
    # 3. Split train/test
    print("\n✂️  Dividiendo en train/test...")
    train_texts, test_texts, train_labels, test_labels = train_test_split(
        texts, labels, test_size=0.15, random_state=42, stratify=labels
    )
    print(f"   ✅ Train: {len(train_texts)} ejemplos")
    print(f"   ✅ Test: {len(test_texts)} ejemplos")
    
    # 4. Cargar tokenizer y modelo
    print(f"\n🤖 Cargando modelo base: {MODEL_NAME}")
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    model = AutoModelForSequenceClassification.from_pretrained(
        MODEL_NAME,
        num_labels=num_labels
    )
    print("   ✅ Modelo cargado")
    
    # 5. Crear datasets de PyTorch
    print("\n📦 Creando datasets de PyTorch...")
    train_dataset = FAQDataset(train_texts, train_labels, tokenizer, MAX_LENGTH)
    test_dataset = FAQDataset(test_texts, test_labels, tokenizer, MAX_LENGTH)
    print("   ✅ Datasets creados")
    
    # 6. Configurar entrenamiento
    print("\n⚙️  Configurando entrenamiento...")
    training_args = TrainingArguments(
        output_dir=str(MODEL_OUTPUT_PATH),
        num_train_epochs=NUM_EPOCHS,
        per_device_train_batch_size=BATCH_SIZE,
        per_device_eval_batch_size=BATCH_SIZE,
        learning_rate=LEARNING_RATE,
        weight_decay=0.01,
        logging_steps=50,
        eval_strategy="epoch",
        save_strategy="epoch",
        save_total_limit=2,
        load_best_model_at_end=True,
        metric_for_best_model="accuracy",
        fp16=torch.cuda.is_available(),  # Usar mixed precision si hay GPU
        report_to="none",  # No usar wandb/tensorboard
    )
    
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=test_dataset,
        compute_metrics=compute_metrics,
    )
    
    print(f"   ✅ Épocas: {NUM_EPOCHS}")
    print(f"   ✅ Batch size: {BATCH_SIZE}")
    print(f"   ✅ Learning rate: {LEARNING_RATE}")
    print(f"   ✅ Max length: {MAX_LENGTH} tokens")
    print(f"   ✅ Device: {'GPU' if torch.cuda.is_available() else 'CPU'}")
    
    # 7. Entrenar
    print("\n🏋️  Iniciando entrenamiento...")
    print("-" * 60)
    trainer.train()
    
    # 8. Evaluar
    print("\n📊 Evaluando modelo final...")
    eval_results = trainer.evaluate()
    print(f"   ✅ Accuracy: {eval_results['eval_accuracy']:.2%}")
    print(f"   ✅ Loss: {eval_results['eval_loss']:.4f}")
    
    # 9. Guardar modelo y tokenizer
    print(f"\n💾 Guardando modelo en: {MODEL_OUTPUT_PATH}")
    trainer.save_model(str(MODEL_OUTPUT_PATH))
    tokenizer.save_pretrained(str(MODEL_OUTPUT_PATH))
    
    # Guardar mapeo de labels
    label_map_path = MODEL_OUTPUT_PATH / "label_map.json"
    with open(label_map_path, "w", encoding="utf-8") as f:
        json.dump(label_map, f, ensure_ascii=False, indent=2)
    
    print("   ✅ Modelo guardado exitosamente")
    
    print("\n" + "=" * 60)
    print("✨ ENTRENAMIENTO COMPLETADO")
    print("=" * 60)
    print(f"\n📈 Resultados finales:")
    print(f"   • Accuracy: {eval_results['eval_accuracy']:.2%}")
    print(f"   • Loss: {eval_results['eval_loss']:.4f}")
    print(f"   • Total ejemplos: {len(texts)}")
    print(f"   • Categorías: {num_labels}")
    print(f"\n🎯 El modelo está listo para usar en el chatbot!")


# ================================
# 6. EJECUCIÓN
# ================================
if __name__ == "__main__":
    train_model()
