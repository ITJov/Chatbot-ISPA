from flask import Blueprint, request, jsonify
# Import fungsi dari service yang baru kita buat
from app.services.ai_service import extract_symptoms

main = Blueprint('main', __name__)

@main.route('/chat', methods=['POST'])
def chat():
    data = request.json
    user_message = data.get('message', '')

    if not user_message:
        return jsonify({"error": "Pesan tidak boleh kosong"}), 400

    # 1. Panggil Otak AI untuk Ekstraksi Gejala
    extracted_data = extract_symptoms(user_message)

    # 2. Pisahkan mana Gejala Utama (G01-G15), mana Info Tambahan
    gejala_utama = []
    info_tambahan = []

    for item in extracted_data:
        if item['code'].startswith('G'): # G01, G02, dst
            gejala_utama.append(item)
        else: # DURASI, INTENSITAS
            info_tambahan.append(item)

    # --- TODO NANTI: DI SINI MASUKKAN LOGIKA NAIVE BAYES/RULE BASED ---
    # Logika: "Jika ada G01 dan G02, maka penyakitnya Flu"
    # Untuk sekarang, kita kembalikan hasil ekstraksi mentah dulu
    
    diagnosis_dummy = "Belum ada diagnosa (Menunggu modul Rule-Based)"
    if len(gejala_utama) > 0:
        diagnosis_dummy = "Gejala terdeteksi, analisis penyakit akan segera hadir."

    # 3. Kirim Respon JSON ke Frontend
    response_data = {
        "user_message": user_message,
        "ai_analysis": {
            "all_entities": extracted_data,
            "symptoms_identified": [g['code'] for g in gejala_utama], # List kode: ['G01', 'G02']
        },
        "diagnosis": {
            "result": diagnosis_dummy,
            "confidence": "N/A" # Nanti diisi hasil hitungan Naive Bayes
        },
        # Bot reply sederhana berdasarkan temuan
        "bot_reply": f"Saya mendeteksi Anda mengalami: {', '.join([g['word'] for g in gejala_utama])}. {diagnosis_dummy}"
    }

    return jsonify(response_data)