import os
import json
from flask import Blueprint, request, jsonify
from app.services.ai_service import extract_symptoms

main = Blueprint('main', __name__)

# --- MEMORI SEMENTARA ---
USER_MEMORY = {}

# --- LOAD DATASET ---
def load_knowledge_base():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) 
    file_path = os.path.join(base_dir, '..', 'Dataset', 'knowledge_base.json')
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return []

PENYAKIT_DB = load_knowledge_base()

GEJALA_MAP = {
    "G01": "Demam", "G02": "Batuk", "G03": "Pilek",
    "G04": "Pusing/Sakit Kepala", "G05": "Sakit Tenggorokan", "G06": "Lemas",
    "G07": "Sesak Napas", "G08": "Napas Cepat", "G09": "Mengi",
    "G10": "Mual/Muntah", "G11": "Penciuman Hilang", "G12": "Suara Serak",
    "G13": "Sakit Telinga", "G14": "Nyeri Dada", "G15": "Bengkak"
}

# --- KAMUS MANUAL (Agar Bot 100% Peka) ---
# Jika AI gagal deteksi, kode ini yang akan menangkapnya
MANUAL_KEYWORDS = {
    "demam": "G01", "panas": "G01", "menggigil": "G01", "meriang": "G01",
    "batuk": "G02", "uhuk": "G02",
    "pilek": "G03", "flu": "G03", "meler": "G03", "tersumbat": "G03", "ingus": "G03",
    "pusing": "G04", "sakit kepala": "G04", "nyut": "G04", "pening": "G04",
    "tenggorokan": "G05", "telan": "G05", "nelan": "G05",
    "lemas": "G06", "lelah": "G06", "letih": "G06", "lesu": "G06", "capek": "G06",
    "sesak": "G07", "aprak": "G07",
    "mual": "G10", "muntah": "G10",
    "serak": "G12", "suara habis": "G12",
    "nyeri dada": "G14", "sakit dada": "G14"
}

@main.route('/chat', methods=['POST'])
def chat():
    user_ip = request.remote_addr
    data = request.json
    user_message = data.get('message', '').lower()

    # 1. AUTO-RESET (Jika user menyapa)
    reset_keywords = ['halo', 'hi', 'hai', 'pagi', 'siang', 'sore', 'malam', 'reset', 'ulang', 'clear', 'sakit apa']
    if any(word in user_message for word in reset_keywords):
        USER_MEMORY[user_ip] = set()
        if len(user_message.split()) <= 2:
            return jsonify({"response": "Halo! Silakan sebutkan gejala yang Anda rasakan.", "diagnosis": {"result": "Reset"}})

    # 2. METODE 1: AI NER (Cerdas tapi kadang luput)
    try:
        extracted_data = extract_symptoms(user_message)
    except:
        extracted_data = []

    new_symptoms = set()
    
    # Ambil hasil dari AI
    for item in extracted_data:
        code = item.get('code') or item.get('entity')
        if code:
            if '-' in code: code = code.split('-')[-1]
            if code in GEJALA_MAP:
                new_symptoms.add(code)

    # 3. METODE 2: KEYWORD MATCHING (Backup Manual)
    # Cek setiap kata kunci di kamus, kalau ada di pesan user -> Masukkan!
    for kata, kode in MANUAL_KEYWORDS.items():
        if kata in user_message:
            new_symptoms.add(kode)

    # 4. UPDATE MEMORI
    if user_ip not in USER_MEMORY:
        USER_MEMORY[user_ip] = set()
    
    USER_MEMORY[user_ip].update(new_symptoms)
    current_symptoms = USER_MEMORY[user_ip]
    gejala_display = [GEJALA_MAP.get(g, g) for g in current_symptoms]

    # 5. DIAGNOSA
    diagnosa_list = []
    if current_symptoms:
        for penyakit in PENYAKIT_DB:
            kunci = set(penyakit.get('gejala_kunci', []))
            cocok = len(current_symptoms.intersection(kunci))
            total_kunci = len(kunci)
            confidence = (cocok / total_kunci) * 100 if total_kunci > 0 else 0
            
            if confidence > 0:
                diagnosa_list.append({
                    "nama": penyakit['nama'],
                    "confidence": round(confidence, 1),
                    "saran": penyakit['saran'],
                    "missing": list(kunci - current_symptoms),
                    "gejala_cocok": cocok
                })
        diagnosa_list = sorted(diagnosa_list, key=lambda x: (x['confidence'], x['gejala_cocok']), reverse=True)

    # 6. RESPONSE BUILDER
    if not current_symptoms:
        bot_text = "Maaf, saya belum menangkap gejala medis spesifik. Bisa ceritakan apa yang Anda rasakan?"
    
    elif len(current_symptoms) == 1:
        satu_gejala = gejala_display[0]
        potential = [d['nama'] for d in diagnosa_list[:3]]
        
        # Cari saran gejala lain
        saran_set = set()
        for d in diagnosa_list[:3]:
            for m in d['missing']:
                nama = GEJALA_MAP.get(m)
                if nama: saran_set.add(nama)
        
        saran_text = " atau ".join(list(saran_set)[:2])
        bot_text = (f"Saya mencatat gejala: {satu_gejala}.\n\n"
                    f"Ini bisa mengarah ke {', '.join(potential)}. "
                    f"Apakah Anda juga merasakan {saran_text}?")

    elif diagnosa_list:
        top = diagnosa_list[0]
        gejala_str = ", ".join(gejala_display)
        
        if top['confidence'] >= 50:
            bot_text = (f"Berdasarkan keluhan ({gejala_str}), kondisi ini mengarah pada {top['nama']}.\n\n"
                        f"Saran: {top['saran']}")
        else:
            missing_names = [GEJALA_MAP.get(m) for m in top['missing'][:2]]
            tanya = " atau ".join(filter(None, missing_names))
            bot_text = (f"Saya mendeteksi gejala: {gejala_str}. Pola ini mirip {top['nama']}, "
                        f"tapi belum pasti. Apakah Anda merasakan {tanya}?")
    else:
        bot_text = "Gejala tercatat, namun pola penyakit belum dikenali."

    return jsonify({"response": bot_text})