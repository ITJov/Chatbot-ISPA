import os
import json
import re
from flask import Blueprint, request, jsonify
from app.services.ai_service import extract_symptoms
from collections import Counter

main = Blueprint('main', __name__)

# --- KONFIGURASI MEMORI FILE (Agar Tahan Restart) ---
MEMORY_FILE = 'session_memory.json'

def load_memory():
    """Membaca ingatan dari file JSON"""
    if not os.path.exists(MEMORY_FILE):
        return {}
    try:
        with open(MEMORY_FILE, 'r') as f:
            data = json.load(f)
            return data if isinstance(data, dict) else {}
    except Exception as e:
        print(f"⚠️ ERROR BACA MEMORI: {e}")
        return {}

def save_memory(memory_data):
    """Menulis ingatan ke file JSON"""
    try:
        with open(MEMORY_FILE, 'w') as f:
            json.dump(memory_data, f, indent=2)
    except Exception as e:
        print(f"⚠️ ERROR TULIS MEMORI: {e}")

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
    "G07": "Sesak Napas", "G08": "Napas Cepat", "G09": "Mengi/Napas Berbunyi",
    "G10": "Mual/Muntah", "G11": "Penciuman Hilang", "G12": "Suara Serak",
    "G13": "Sakit Telinga", "G14": "Nyeri Dada", "G15": "Bengkak"
}

# --- KAMUS MANUAL LENGKAP (IMPLICIT INTENT) ---
MANUAL_KEYWORDS = {
    # G01 - Demam
    "demam": "G01", "panas": "G01", "menggigil": "G01", "meriang": "G01", "suhu": "G01",
    # G02 - Batuk
    "batuk": "G02", "uhuk": "G02", "berdahak": "G02", "kering": "G02",
    # G03 - Pilek (Hidung)
    "pilek": "G03", "flu": "G03", "meler": "G03", "tersumbat": "G03", "ingus": "G03", "hidung": "G03",
    # G04 - Pusing (Kepala)
    "pusing": "G04", "sakit kepala": "G04", "nyut": "G04", "pening": "G04", "migrain": "G04", "kepala": "G04",
    # G05 - Tenggorokan
    "tenggorokan": "G05", "telan": "G05", "nelan": "G05", "radang": "G05",
    # G06 - Lemas
    "lemas": "G06", "lelah": "G06", "letih": "G06", "lesu": "G06", "capek": "G06",
    # G07 - Sesak
    "sesak": "G07", "engap": "G07", "sulit napas": "G07", "susah napas": "G07",
    # G08 - Napas Cepat
    "napas cepat": "G08", "ngos": "G08",
    # G09 - Mengi
    "mengi": "G09", "bengek": "G09", "bunyi ngik": "G09",
    # G10 - Mual/Muntah (Perut)
    "mual": "G10", "muntah": "G10", "enek": "G10", "perut": "G10",
    # G11 - Penciuman
    "penciuman": "G11", "bau": "G11", "anosmia": "G11", "cium": "G11", "hambar": "G11",
    # G12 - Serak
    "serak": "G12", "suara": "G12", "parau": "G12",
    # G13 - Telinga
    "telinga": "G13", "kuping": "G13", "pendengaran": "G13",
    # G14 - Nyeri Dada (Dada)
    "nyeri dada": "G14", "sakit dada": "G14", "dada": "G14", "jantung": "G14", 
    # G15 - Bengkak
    "bengkak": "G15", "kelenjar": "G15", "benjolan": "G15"
}

@main.route('/chat', methods=['POST'])
def chat():
    data = request.json
    user_message = data.get('message', '').lower()
    session_id = data.get('session_id')
    
    # 1. VALIDASI SESSION
    if not session_id:
        print("⚠️ Warning: No Session ID")
        session_id = "TEMP_SESSION"

    # 2. LOAD MEMORI
    all_memory = load_memory()
    current_symptoms = set(all_memory.get(session_id, []))

    # 3. AUTO-RESET CERDAS (Regex Whole Word)
    # Hanya reset jika kata "hi", "halo" berdiri sendiri, bukan di dalam kata "kehilangan"
    reset_keywords = {'halo', 'hi', 'hai', 'pagi', 'reset', 'ulang', 'clear', 'mulai'}
    user_words = set(re.findall(r'\w+', user_message)) # Pecah kalimat jadi kata
    
    if not user_words.isdisjoint(reset_keywords): # Jika ada irisan kata
        current_symptoms = set()
        all_memory[session_id] = []
        save_memory(all_memory)
        if len(user_message.split()) <= 2:
            return jsonify({"response": "Halo! Memori baru siap. Silakan sebutkan keluhan Anda."})

    # 4. HYBRID DETECTION
    # A. AI Detection
    try:
        extracted_data = extract_symptoms(user_message)
    except:
        extracted_data = []

    new_symptoms = set()
    for item in extracted_data:
        code = item.get('code') or item.get('entity')
        if code:
            if '-' in code: code = code.split('-')[-1]
            if code in GEJALA_MAP: new_symptoms.add(code)
    
    # B. Manual Keyword Detection
    for kata, kode in MANUAL_KEYWORDS.items():
        if kata in user_message:
            new_symptoms.add(kode)
            
    # C. Typo Handling (Simple)
    if not new_symptoms:
        typo_map = {
            "btuk": "G02", "dmm": "G01", "kpala": "G04", "plk": "G03", "ssak": "G07"
        }
        for word in user_message.split():
            if word in typo_map: new_symptoms.add(typo_map[word])

    # 5. UPDATE & SIMPAN MEMORI
    if new_symptoms:
        current_symptoms.update(new_symptoms)
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

    # 6. RESPONSE BUILDER
    diagnosis_payload = {"details": []} # Data untuk grafik frontend
    
    if not current_symptoms:
        bot_text = "Maaf, saya belum menangkap gejala medis spesifik. Bisa ceritakan apa yang Anda rasakan?"

    # Kasus: Confidence masih rendah (<60%) -> Tanya Gejala Pembeda
    elif diagnosa_list and diagnosa_list[0]['confidence'] < 60:
        top_candidates = diagnosa_list[:3]
        
        # Kirim data kandidat ke frontend untuk grafik (tetap tampilkan potensi)
        diagnosis_payload["details"] = [{"nama": d['nama'], "confidence": d['confidence']} for d in top_candidates]

        all_missing = []
        for d in top_candidates: all_missing.extend(d['missing'])
        
        if all_missing:
            most_common = Counter(all_missing).most_common(2)
            saran_gejala = [GEJALA_MAP.get(code) for code, count in most_common]
            pertanyaan = " atau ".join(filter(None, saran_gejala))
            potential_names = ", ".join([d['nama'] for d in top_candidates])
            
            bot_text = (f"Saya mencatat gejala: **{gejala_str}**.\n"
                        f"Pola ini mirip dengan **{potential_names}**.\n\n"
                        f"Untuk memastikan, apakah Anda juga merasakan **{pertanyaan}**?")
        else:
             bot_text = f"Gejala **{gejala_str}** tercatat, namun belum cukup spesifik untuk diagnosa pasti."

    # Kasus: Confidence Tinggi (>=60%) -> Vonis
    elif diagnosa_list:
        top = diagnosa_list[0]
        # Kirim data top 3 ke frontend
        diagnosis_payload["details"] = [{"nama": d['nama'], "confidence": d['confidence']} for d in diagnosa_list[:3]]
        
        bot_text = (f"Berdasarkan kombinasi **{gejala_str}**, analisis saya mengarah pada **{top['nama']}** "
                    f"({top['confidence']}% kecocokan).\n\n"
                    f"**Saran Medis:** {top['saran']}")
    else:
        bot_text = "Gejala tercatat, namun belum cocok dengan database penyakit ISPA."

    return jsonify({
        "response": bot_text,
        "diagnosis": diagnosis_payload # Ini data untuk grafik
    })