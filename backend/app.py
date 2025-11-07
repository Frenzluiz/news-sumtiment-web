# backend/app.py

# === INSTALL DEPENDENCY ===
# pip install flask transformers sentencepiece torch bs4 requests -q

from flask import Flask, request, jsonify, send_from_directory
from transformers import T5Tokenizer, T5ForConditionalGeneration, AutoTokenizer, AutoModelForSequenceClassification
import torch
from bs4 import BeautifulSoup
import requests
import re
import os
import random

app = Flask(__name__, static_folder="../frontend", static_url_path="/")

# === PATH MODEL ===
backend_path = os.path.dirname(os.path.abspath(__file__))
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

# === SCRAPE TITLE & CONTENT ===
def scrape_title(url):
    try:
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")
        title_tag = soup.find("h1", class_=lambda x: x and "detail__title" in x)
        if title_tag: return title_tag.get_text(strip=True)
        if soup.title: return soup.title.get_text(strip=True)
        return "Judul tidak ditemukan"
    except Exception as e:
        return f"Error scraping: {e}"

def scrape_content(url):
    try:
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")
        paragraphs = []
        content_divs = soup.find_all("div", class_=lambda x: x and "detail__body-text" in x)
        for div in content_divs:
            ps = div.find_all("p")
            paragraphs.extend([p.get_text(" ", strip=True) for p in ps if p.get_text(" ", strip=True)])
        if not paragraphs:
            article = soup.find("article")
            if article:
                ps = article.find_all("p")
                paragraphs = [p.get_text(" ", strip=True) for p in ps if p.get_text(" ", strip=True)]
        return paragraphs if paragraphs else []
    except Exception as e:
        return f"Error scraping: {e}"

# === CLEAN TEXT ===
def clean_text(text):
    text = re.sub(r"<[^>]+>", "", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()

# === SENTIMENT ANALYSIS ===
def analyze_sentiment(text):
    try:
        inputs = tokenizer_sent(text, return_tensors="pt", truncation=True, max_length=512)
        outputs = model_sent(**inputs)
        probs = torch.softmax(outputs.logits, dim=1)
        conf, pred_idx = torch.max(probs, dim=1)
        conf = conf.item()
        pred_idx = pred_idx.item()
        labels_map = {0: "Negatif", 1: "Netral", 2: "Positif"}
        if conf >= 0.6:
            return labels_map.get(pred_idx, "Netral")
    except:
        pass

    # fallback keyword
    negatif_keywords = ['bunuh diri','pembunuhan','teror','bom','penyanderaan','kekerasan ekstrem']
    positif_keywords = ['keuntungan','pertumbuhan','sukses','prestasi','donasi','inovasi']
    text_lower = re.sub(r'[^\w\s]', '', text.lower())
    if any(k in text_lower for k in negatif_keywords): return "Negatif"
    if any(k in text_lower for k in positif_keywords): return "Positif"
    return "Netral"

# === ROUTE FRONTEND ===
@app.route("/")
def index():
    return app.send_static_file("index.html")

# === ROUTE ANALYZE ===
@app.route("/analyze", methods=["POST"])
def analyze():
    data = request.json
    url = data.get("url", "").strip()
    if not url: return jsonify({"error": "URL tidak diberikan."}), 400

    title = scrape_title(url)
    content = scrape_content(url)
    if not content or (isinstance(content, str) and "Error" in content):
        return jsonify({"error": "Konten tidak ditemukan atau situs tidak didukung."}), 400

    clean_paragraphs = [clean_text(p) for p in content if clean_text(p)]
    clean_content = " ".join(clean_paragraphs)

    # Summarization
    summary = ""
    sentences = re.split(r'(?<=[.!?]) +', clean_content)
    sentences = [s.strip() for s in sentences if s.strip()]
    if len(clean_content.split()) < 50:
        summary = sentences[0] if sentences else "Ringkasan tidak tersedia."
    else:
        input_text = "summarize: " + clean_content[:2000]
        inputs_summ = tokenizer_summ(input_text, return_tensors="pt", truncation=True, max_length=512)
        summary_ids = model_summ.generate(inputs_summ["input_ids"], max_length=100, min_length=30, num_beams=2, length_penalty=1.5, early_stopping=True, no_repeat_ngram_size=3)
        summary = tokenizer_summ.decode(summary_ids[0], skip_special_tokens=True).strip()
        if len(summary.split()) < 10: summary = sentences[0] if sentences else "Ringkasan tidak tersedia."

    sentiment = analyze_sentiment(title)
    original_content = clean_paragraphs[0][:500]+"..." if clean_paragraphs else clean_content[:500]+"..."

    return jsonify({"summary": summary, "sentiment": sentiment, "original_content": original_content})

# === RUN APP ===
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5069, debug=True)
