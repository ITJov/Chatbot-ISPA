import os
import json
from flask import Blueprint, request, jsonify
from app.services.ai_service import extract_symptoms
from collections import Counter

main = Blueprint('main', __name__)

# --- KONFIGURASI FILE MEMORI ---
# Ingatan akan disimpan di file ini, bukan di RAM
MEMORY_FILE = 'session_memory.json'

def load_memory():
    """Membaca ingatan dari file JSON"""
    if not os.path.exists(MEMORY_FILE):
        return {}
    try:
        with open(MEMORY_FILE, 'r') as f:
            return json.load(f)
    except:
        return {}

def save_memory(memory_data):
    """Menulis ingatan ke file JSON"""
    try:
        with open(MEMORY_FILE, 'w') as f:
            json.dump(memory_data, f, indent=2)
    except Exception as e:
        print(f"Gagal menyimpan memori: {e}")

# --- LOAD DATASET PENYAKIT ---
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
    "G07": "Sesak Napas", "G08": "Napas Cepat", "G09": "Mengi/Napas Berbunyi",
    "G10": "Mual/Muntah", "G11": "Penciuman Hilang", "G12": "Suara Serak",
    "G13": "Sakit Telinga", "G14": "Nyeri Dada", "G15": "Bengkak"
}

# --- KAMUS MANUAL LENGKAP ---
MANUAL_KEYWORDS = {
    "demam": "G01", "panas": "G01", "menggigil": "G01", "meriang": "G01", "suhu tinggi": "G01",
    "batuk": "G02", "uhuk": "G02", "berdahak": "G02", "kering": "G02",
    "pilek": "G03", "flu": "G03", "meler": "G03", "tersumbat": "G03", "ingus": "G03", "hidung mampet": "G03",
    "pusing": "G04", "sakit kepala": "G04", "nyut": "G04", "pening": "G04", "migrain": "G04", "kepala sakit": "G04",
    "tenggorokan": "G05", "telan": "G05", "nelan": "G05", "radang": "G05",
    "lemas": "G06", "lelah": "G06", "letih": "G06", "lesu": "G06", "capek": "G06",
    "sesak": "G07", "engap": "G07", "sulit napas": "G07", "susah napas": "G07",
    "napas cepat": "G08", "ngos-ngosan": "G08",
    "mengi": "G09", "bengek": "G09", "bunyi ngik": "G09",
    "mual": "G10", "muntah": "G10", "enek": "G10", "perut mual": "G10",
    "penciuman": "G11", "bau": "G11", "anosmia": "G11", "cium": "G11", "hambar": "G11", "tidak bisa mencium": "G11",
    "serak": "G12", "suara habis": "G12", "parau": "G12",
    "telinga": "G13", "kuping": "G13", "pendengaran": "G13",
    "nyeri dada": "G14", "sakit dada": "G14", "dada sakit": "G14", "dada nyeri": "G14",
    "bengkak": "G15", "kelenjar": "G15", "benjolan": "G15"
}

@main.route('/chat', methods=['POST'])
def chat():
    data = request.json
    user_message = data.get('message', '').lower()
    
    # Gunakan Session ID dari frontend, atau IP sebagai fallback
    session_id = data.get('session_id') or request.remote_addr
    
    # 1. LOAD MEMORI DARI FILE (Anti-Reset)
    all_memory = load_memory()
    
    # Ambil gejala user ini (convert dari list ke set supaya unik)
    current_symptoms = set(all_memory.get(session_id, []))

    # 2. AUTO-RESET
    reset_keywords = ['halo', 'hi', 'hai', 'pagi', 'reset', 'ulang', 'clear', 'mulai', 'tes']
    if any(word in user_message for word in reset_keywords):
        current_symptoms = set() # Kosongkan di variabel
        all_memory[session_id] = [] # Kosongkan di file
        save_memory(all_memory)
        
        if len(user_message.split()) <= 2:
            return jsonify({"response": "Halo! Memori telah direset. Silakan sebutkan keluhan Anda."})

    # 3. DETEKSI GEJALA (Hybrid)
    try:
        extracted_data = extract_symptoms(user_message)
    except:
        extracted_data = []

    new_symptoms = set()
    # AI Detection
    for item in extracted_data:
        code = item.get('code') or item.get('entity')
        if code:
            if '-' in code: code = code.split('-')[-1]
            if code in GEJALA_MAP: new_symptoms.add(code)
    
    # Manual Keyword Detection
    for kata, kode in MANUAL_KEYWORDS.items():
        if kata in user_message:
            new_symptoms.add(kode)

    # 4. UPDATE & SIMPAN KE FILE
    if new_symptoms:
        current_symptoms.update(new_symptoms)
        # Simpan ke file (JSON butuh List, bukan Set)
        all_memory[session_id] = list(current_symptoms)
        save_memory(all_memory)
    
    # --- LOGIKA DIAGNOSA ---
    gejala_display = [GEJALA_MAP.get(g, g) for g in current_symptoms]
    gejala_str = ", ".join(gejala_display)

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

    # 5. RESPONSE BUILDER
    if not current_symptoms:
        bot_text = "Maaf, saya belum menangkap gejala medis spesifik. Bisa ceritakan apa yang Anda rasakan?"

    # Jika gejala ada, tapi confidence masih rendah (< 60%)
    elif diagnosa_list and diagnosa_list[0]['confidence'] < 60:
        top_candidates = diagnosa_list[:3]
        all_missing = []
        for d in top_candidates:
            all_missing.extend(d['missing'])
        
        if all_missing:
            # Cari gejala pembeda yang paling sering muncul
            most_common = Counter(all_missing).most_common(2)
            saran_gejala = [GEJALA_MAP.get(code) for code, count in most_common]
            pertanyaan = " atau ".join(filter(None, saran_gejala))
            potential_names = ", ".join([d['nama'] for d in top_candidates])
            
            bot_text = (f"Saya mencatat gejala: {gejala_str}.\n"
                        f"Pola ini mirip dengan {potential_names}.\n\n"
                        f"Untuk memastikan, apakah Anda juga merasakan {pertanyaan}?")
        else:
             bot_text = f"Gejala {gejala_str} tercatat, namun belum cukup spesifik untuk diagnosa pasti."

    # Jika confidence tinggi (>= 60%)
    elif diagnosa_list:
        top = diagnosa_list[0]
        bot_text = (f"Berdasarkan kombinasi {gejala_str}, analisis saya mengarah pada {top['nama']} "
                    f"({top['confidence']}% kecocokan).\n\n"
                    f"Saran Medis: {top['saran']}")
    else:
        bot_text = "Gejala tercatat, namun belum cocok dengan database penyakit ISPA."

    return jsonify({"response": bot_text})