import pandas as pd
import json
import re
import os

# 1. Load CSV
df = pd.read_csv('Dataset/raw_dataset.csv') 

formatted_data = []

def find_label_in_sentence(sentence, entity_text):
    # Membersihkan tanda baca agar pencarian akurat
    sentence_clean = re.sub(r'[^\w\s]', '', sentence).lower()
    entity_clean = re.sub(r'[^\w\s]', '', entity_text).lower()
    
    try:
        start_index = sentence_clean.index(entity_clean)
        return start_index
    except ValueError:
        return -1

# 2. Loop setiap baris data
for index, row in df.iterrows():
    sentence = str(row['Kalimat Teks (Input)'])
    raw_labels = str(row['Entitas & Label (Output)']) # Format: "batuk (G02), 3 hari (DURASI)"
    
    # Tokenisasi sederhana (memisahkan spasi)
    # Catatan: Nanti DistilBERT punya tokenizer sendiri, ini untuk mapping awal saja
    tokens = sentence.split()
    
    # Siapkan list label default "O" (Outside) sepanjang kalimat
    ner_tags = ["O"] * len(tokens)
    
    # Parsing kolom C (memisahkan koma)
    # Contoh raw_labels: "batuk kering (G02), parah (INTENSITAS)"
    entities = [e.strip() for e in raw_labels.split(',')]
    
    for entity in entities:
        # Pisahkan Teks dan Label. Contoh: "batuk kering" dan "G02"
        # Regex mencari pola: "teks (LABEL)"
        match = re.match(r"(.+)\s\((.+)\)", entity)
        if match:
            word_phrase = match.group(1).strip() # "batuk kering"
            label_code = match.group(2).strip()  # "G02"
            
            # Cari kata tersebut ada di token nomor berapa
            word_parts = word_phrase.split()
            
            # Algoritma pencocokan sederhana
            for i in range(len(tokens)):
                # Cek apakah token ini cocok dengan kata pertama entitas
                # (Logic ini sederhana, bisa dikembangkan lagi)
                token_clean = re.sub(r'[^\w\s]', '', tokens[i]).lower()
                first_word_clean = re.sub(r'[^\w\s]', '', word_parts[0]).lower()

                if token_clean == first_word_clean:
                    # Jika cocok, tandai BIO scheme
                    ner_tags[i] = f"B-{label_code}" # Beginning
                    
                    # Jika entitas lebih dari 1 kata (misal: "batuk kering")
                    for j in range(1, len(word_parts)):
                        if i + j < len(tokens):
                             ner_tags[i + j] = f"I-{label_code}" # Inside
                    break

    # Simpan hasil format
    formatted_data.append({
        "id": index,
        "tokens": tokens,
        "ner_tags": ner_tags
    })

# 3. Simpan ke JSON
output_file = 'dataset/dataset_training.json'
with open(output_file, 'w') as f:
    json.dump(formatted_data, f, indent=2)

print(f"Berhasil konversi! Data tersimpan di {output_file}")
print("Contoh data pertama:", formatted_data[0])