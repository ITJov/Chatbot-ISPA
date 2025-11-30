from transformers import AutoTokenizer, AutoModelForTokenClassification, pipeline

model_path = "./model_output"
print(f"Memuat model dari: {model_path}")

tokenizer = AutoTokenizer.from_pretrained(model_path)
model = AutoModelForTokenClassification.from_pretrained(model_path)

nlp = pipeline("ner", model=model, tokenizer=tokenizer, aggregation_strategy="simple")

test_sentences = [
    "Dok, anak saya batuk kering dan demam tinggi sejak kemarin.",
    "Kepala saya pusing banget dan hidung mampet susah napas.",
    "Tenggorokan sakit buat nelan, kayaknya radang."
]

print("\n=== HASIL PENGUJIAN AKHIR ===")

for text in test_sentences:
    print(f"\nKalimat: '{text}'")
    results = nlp(text)
    
    if not results:
        print("  (Tidak ada gejala terdeteksi)")
    
    for entity in results:
        label = entity['entity_group']  
        word = entity['word']           
        conf = entity['score']          
        
        clean_word = word.replace("##", "")
        
        print(f"  -> Deteksi: {clean_word} ({label}) | Yakin: {conf:.1%}")

print("\n=============================")