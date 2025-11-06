document.getElementById("analyze-btn").addEventListener("click", async () => {
  const url = document.getElementById("url").value.trim();
  const resultDiv = document.getElementById("result");
  if (!url) {
    resultDiv.innerHTML = '<div class="text-danger">Masukkan URL!</div>';
    return;
  }
  resultDiv.innerHTML = '<div class="text-primary">⏳ Sedang menganalisis...</div>';

  try {
    const res = await fetch("/analyze", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ url })
    });
    const data = await res.json();
    if (res.ok) {
      resultDiv.innerHTML = `
        <h4>🧾 Ringkasan:</h4><p>${data.summary}</p>
        <h5>😊 Sentimen:</h5><p>${data.sentiment}</p>
        <h5>📰 Cuplikan Konten:</h5><p>${data.original_content}</p>
      `;
    } else {
      resultDiv.innerHTML = `<div class="text-danger">⚠️ ${data.error}</div>`;
    }
  } catch (e) {
    resultDiv.innerHTML = `<div class="text-danger">❌ ${e.message}</div>`;
  }
});
