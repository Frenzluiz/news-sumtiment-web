// frontend/script.js
async function analyze() {
    const url = document.getElementById("url").value.trim();
    const resultDiv = document.getElementById("result");
    if (!url) {
        resultDiv.innerHTML = '<div style="color:red;">Masukkan URL!</div>';
        return;
    }
    resultDiv.innerHTML = '<div style="color:blue;">⏳ Sedang menganalisis...</div>';
    try {
        const res = await fetch("/analyze", {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ url })
        });
        const data = await res.json();
        if (res.ok) {
            resultDiv.innerHTML = `
                <h4>🧾 Ringkasan:</h4><p>${data.summary}</p>
                <h5>😊 Sentimen :</h5><p>${data.sentiment}</p>
                <h5>📰 Cuplikan Konten Asli:</h5><p>${data.original_content}</p>
            `;
        } else {
            resultDiv.innerHTML = `<div style="color:red;">⚠️ ${data.error}</div>`;
        }
    } catch (e) {
        resultDiv.innerHTML = `<div style="color:red;">❌ ${e.message}</div>`;
    }
}
