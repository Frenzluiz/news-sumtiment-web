# Backend - News Sumtiment Web
Folder ini berisi backend Flask untuk aplikasi News Summarizer & Sentiment.

## Struktur
- `app.py` : Flask app yang memuat model, melakukan scraping, summarization, dan sentiment analysis.
- `requirements.txt` : daftar dependency.
- `models/` : tempat upload model (tidak termasuk model di repo).

## Cara Menjalankan (Colab / Lokal)
1. Upload folder ini ke Google Drive (jika pakai Colab).
2. Pastikan model disimpan di `backend/models/summarization_model_final` dan `backend/models/sentiment_model_batch1_final`.
3. Set token ngrok di `app.py` (ganti `ISI_TOKEN_NGROK_KAMU`).
4. Jalankan:
   ```bash
   pip install -r requirements.txt
   python app.py
   ```
5. Tunggu sampai muncul `🚀 Public URL: ...` di console.
