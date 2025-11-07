# news-sumtiment-web

Aplikasi web untuk **meringkas berita otomatis** dan **menganalisis sentimen** menggunakan model AI (T5 & BERT).

Lihat folder `backend/` dan `frontend/`.

---

## 🔗 Link Model

File model **tidak disertakan di repo** karena ukurannya besar. Silakan download model dari Google Drive:

- **Model Summarization:** [Download di sini](https://drive.google.com/drive/folders/1UT-v1IFwxD9SSPOH6I0LLKwiHAnS7RZ1?usp=sharing)  
- **Model Sentiment:** [Download di sini](https://drive.google.com/drive/folders/1RNj5UbiIvehHQYVD0ON7vkWnreGRcasN?usp=sharing)  

Setelah diunduh, letakkan folder model di:
backend/summarization_model_final 
dan 
backend/sentiment_model_batch1_final

## 🖥️ Struktur Proyek
news-sumtiment-web/
├─ backend/ # Kode backend Flask
│ ├─ app.py
│ ├─ requirements.txt
│ └─ Folder model (tidak termasuk di repo)
├─ frontend/ # Kode frontend (HTML, CSS, JS)
│ ├─ index.html
│ ├─ script.js
│ └─ style.css
├─ .gitignore
└─ README.md

## ⚙️ Instalasi & Persiapan

1. Clone repo:
git clone https://github.com/Frenzluiz/news-sumtiment-web.git
cd news-sumtiment-web/backend

2. Buat virtual environment (opsional tapi disarankan):
python -m venv venv
.\venv\Scripts\activate # Windows
source venv/bin/activate # Linux/Mac

3. Install dependencies:
pip install -r requirements.txt

4. Pastikan model sudah diletakkan di folder yang tepat seperti dijelaskan di atas.
## 🚀 Menjalankan Aplikasi
1. Jalankan Flask backend:
   python app.py
2. Backend akan bisa diakses di http://127.0.0.1:5017/

3. Buka browser, akses frontend `index.html` untuk memasukkan link berita dan melakukan **summarization + sentiment analysis**.

## 📌 Catatan

- File model **tidak ada di repo** karena besar (>100 MB), gunakan link Google Drive di atas.  
- `.gitignore` sudah menonaktifkan tracking folder model agar repo tetap ringan.  
- Untuk menambahkan model baru, cukup letakkan di folder `backend/` sesuai struktur.
