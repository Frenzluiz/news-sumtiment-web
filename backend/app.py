# === INSTALL DEPENDENCY ===
import nest_asyncio
import threading
from flask import Flask, request, jsonify, send_from_directory
from transformers import T5Tokenizer, T5ForConditionalGeneration, AutoTokenizer, AutoModelForSequenceClassification
from pyngrok import ngrok
import torch, requests, re, os, random
from bs4 import BeautifulSoup

# === INIT ===
nest_asyncio.apply()
app = Flask(__name__, static_folder="../frontend", static_url_path="/")

# === PATH MODEL ===
backend_path = "./models"
summ_path = os.path.join(backend_path, "summarization_model_final")
sent_path = os.path.join(backend_path, "sentiment_model_batch1_final")

# === LOAD MODEL ===
print("🔹 Memuat model summarization...")
tokenizer_summ = T5Tokenizer.from_pretrained(summ_path)
model_summ = T5ForConditionalGeneration.from_pretrained(summ_path)
model_summ.to("cpu")

print("🔹 Memuat model sentiment...")
tokenizer_sent = AutoTokenizer.from_pretrained(sent_path)
model_sent = AutoModelForSequenceClassification.from_pretrained(sent_path)
model_sent.to("cpu")
print("✅ Model siap digunakan!")

# === SCRAPE CONTENT ===
def scrape_content(url):
    try:
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")
        paragraphs = []

        # Detik
        for div in soup.find_all("div", class_=lambda x: x and "detail__body-text" in x):
            ps = div.find_all("p")
            paragraphs.extend([p.get_text(" ", strip=True) for p in ps])

        # Kompas
        if not paragraphs:
            for div in soup.find_all("div", class_=lambda x: x and "read__content" in x):
                ps = div.find_all("p")
                paragraphs.extend([p.get_text(" ", strip=True) for p in ps])

        # Tempo
        if not paragraphs:
            for div in soup.find_all("div", class_=lambda x: x and "article-content" in x):
                ps = div.find_all("p")
                paragraphs.extend([p.get_text(" ", strip=True) for p in ps])

        # Fallback
        if not paragraphs:
            article = soup.find("article")
            if article:
                paragraphs = [p.get_text(" ", strip=True) for p in article.find_all("p")]

        return paragraphs if paragraphs else []
    except Exception as e:
        return f"Error scraping: {e}"

def clean_text(text):
    text = re.sub(r"<[^>]+>", "", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()

# === ROUTES ===
@app.route("/")
def serve_frontend():
    return send_from_directory("../frontend", "index.html")

@app.route("/analyze", methods=["POST"])
def analyze():
    data = request.json
    url = data.get("url", "").strip()
    if not url:
        return jsonify({"error": "URL tidak diberikan."}), 400

    content = scrape_content(url)
    if not content or isinstance(content, str):
        return jsonify({"error": "Konten tidak ditemukan atau situs tidak didukung."}), 400

    clean_content = " ".join([clean_text(p) for p in content])
    summary = ""
    sentences = re.split(r'(?<=[.!?]) +', clean_content)

    if len(clean_content.split()) < 50:
        summary = sentences[0] if sentences else "Ringkasan tidak tersedia."
    else:
        input_text = "summarize: " + clean_content[:2000]
        inputs_summ = tokenizer_summ(input_text, return_tensors="pt", truncation=True, max_length=512)
        summary_ids = model_summ.generate(
            inputs_summ["input_ids"], max_length=100, min_length=30,
            num_beams=2, length_penalty=1.5, early_stopping=True, no_repeat_ngram_size=3
        )
        summary = tokenizer_summ.decode(summary_ids[0], skip_special_tokens=True).strip()

        if (len(summary.split()) < 10 or
            any(k in summary.lower() for k in ["summarize", "marize", "ization", "tidak dapat dihasilkan"]) or
            "ringkasan tidak" in summary.lower()):
            if content:
                first_para = content[0]
                summary = first_para.split('. ')[0] + ("..." if len(first_para) > 120 else "")
            else:
                summary = "Ringkasan tidak tersedia."

    inputs_sent = tokenizer_sent(clean_content, return_tensors="pt", truncation=True, max_length=512)
    outputs_sent = model_sent(**inputs_sent)
    sentiment = torch.argmax(outputs_sent.logits, dim=1).item()
    sentiment_label = ['Negatif', 'Netral', 'Positif'][sentiment]

    original_content = " ".join(content[:3])
    if len(original_content) > 1000:
        original_content = original_content[:1000] + "..."

    return jsonify({
        "summary": summary,
        "sentiment": sentiment_label,
        "original_content": original_content
    })

# === NGROK ===
@app.route("/stop_ngrok", methods=["POST"])
def stop_ngrok():
    try:
        ngrok.disconnect(public_url)
        return jsonify({"message": "Ngrok dihentikan."})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


ngrok.set_auth_token("350wSbScyB2ilgky1ciut75NkzM_zdwNbhm39TcSSCSwssB5")
public_url = ngrok.connect(5060, bind_tls=True).public_url
print("🚀 Public URL:", public_url)
print("Gunakan aplikasi dari:", public_url)

# Simpan URL untuk frontend
with open("backend_url.txt", "w") as f:
    f.write(public_url)
    
# === RUN FLASK ===
def run_app():
    app.run(host="0.0.0.0", port=5060)

threading.Thread(target=run_app).start()
