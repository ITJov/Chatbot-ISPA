import os
from transformers import AutoTokenizer, AutoModelForTokenClassification, pipeline

# 1. Konfigurasi Path Model
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
MODEL_PATH = os.path.join(BASE_DIR, "model_output")

print(f"--- LOAD AI MODEL DARI: {MODEL_PATH} ---")

# 2. Load Model Sekali Saja (di awal) agar cepat
try:
    tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH)
    model = AutoModelForTokenClassification.from_pretrained(MODEL_PATH)
    
    nlp_pipeline = pipeline("ner", model=model, tokenizer=tokenizer, aggregation_strategy="simple")
    print("--- MODEL BERHASIL DILOAD! ---")
except Exception as e:
    print(f"ERROR LOAD MODEL: {e}")
    nlp_pipeline = None

# 3. Fungsi yang akan dipanggil oleh routes.py
def extract_symptoms(text):
    if not nlp_pipeline:
        return []

    results = nlp_pipeline(text)
    
    merged_data = []
    
    for entity in results:
        word = entity['word']
        label = entity['entity_group']
        conf = float(f"{entity['score']:.4f}")

       
        if word.startswith("##"):
            if merged_data:
                # Gabungkan dengan kata terakhir di list
                prev_word = merged_data[-1]["word"]
                merged_data[-1]["word"] = prev_word + word.replace("##", "")
                
        else:
            if merged_data and merged_data[-1]["code"] == label:
                 prev_word = merged_data[-1]["word"]
                 merged_data[-1]["word"] = prev_word + " " + word
            else:
                new_symptom = {
                    "word": word,
                    "code": label,
                    "confidence": conf
                }
                merged_data.append(new_symptom)
        
    return merged_data