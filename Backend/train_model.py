import json
import numpy as np
from datasets import Dataset
from transformers import AutoTokenizer, AutoModelForTokenClassification, TrainingArguments, Trainer, DataCollatorForTokenClassification

#
DATASET_PATH = "../Dataset/dataset_training.json" 
OUTPUT_DIR = "./model_output" 
BASE_MODEL = "distilbert-base-uncased"
# =============================================

print("1. Memuat Dataset...")
with open(DATASET_PATH, 'r') as f:
    raw_data = json.load(f)

# Ambil semua unique tags dari dataset untuk bikin kamus label
unique_tags = set()
for item in raw_data:
    unique_tags.update(item['ner_tags'])
label_list = sorted(list(unique_tags)) # Urutkan agar konsisten

# Buat mapping (Komputer cuma ngerti angka, bukan teks)
label2id = {label: i for i, label in enumerate(label_list)}
id2label = {i: label for i, label in enumerate(label_list)}

print(f"   Ditemukan {len(label_list)} label unik: {label_list}")

# Convert ke format HuggingFace Dataset
hf_dataset = Dataset.from_list(raw_data)

print("2. Tokenisasi Data...")
tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL)

# Fungsi untuk memecah kalimat jadi token angka & merapikan label
def tokenize_and_align_labels(examples):
    tokenized_inputs = tokenizer(examples["tokens"], truncation=True, is_split_into_words=True)
    labels = []
    for i, label in enumerate(examples["ner_tags"]):
        word_ids = tokenized_inputs.word_ids(batch_index=i)
        previous_word_idx = None
        label_ids = []
        for word_idx in word_ids:
            if word_idx is None:
                label_ids.append(-100) 
            elif word_idx != previous_word_idx:
                label_ids.append(label2id[label[word_idx]])
            else:
                label_ids.append(label2id[label[word_idx]])
            previous_word_idx = word_idx
        labels.append(label_ids)
    tokenized_inputs["labels"] = labels
    return tokenized_inputs

tokenized_datasets = hf_dataset.map(tokenize_and_align_labels, batched=True)

print("3. Menyiapkan Model...")
model = AutoModelForTokenClassification.from_pretrained(
    BASE_MODEL, 
    num_labels=len(label_list),
    id2label=id2label,
    label2id=label2id
)

args = TrainingArguments(
    output_dir=OUTPUT_DIR,
    eval_strategy="no", 
    learning_rate=5e-5,
    per_device_train_batch_size=8,
    num_train_epochs=50, 
    weight_decay=0.01,
    save_strategy="epoch"
)

data_collator = DataCollatorForTokenClassification(tokenizer)

trainer = Trainer(
    model=model,
    args=args,
    train_dataset=tokenized_datasets,
    tokenizer=tokenizer,
    data_collator=data_collator,
)

print("4. MULAI TRAINING... (Tunggu sebentar)")
trainer.train()

print("5. Menyimpan Model...")
model.save_pretrained(OUTPUT_DIR)
tokenizer.save_pretrained(OUTPUT_DIR)

print(f"SELESAI! Model tersimpan di folder '{OUTPUT_DIR}'")