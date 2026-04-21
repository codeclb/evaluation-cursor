const form = document.getElementById("analyze-form");
const resultNode = document.getElementById("result");
const historyNode = document.getElementById("history");

async function loadHistory() {
  const response = await fetch("/api/history");
  const entries = await response.json();

  historyNode.innerHTML = "";
  if (!entries.length) {
    const emptyItem = document.createElement("li");
    emptyItem.textContent = "No saved analyses yet.";
    historyNode.appendChild(emptyItem);
    return;
  }

  for (const item of entries) {
    const li = document.createElement("li");
    li.textContent = `${item.original_filename} | "${item.target_word}" = ${item.frequency} (${item.analyzed_at})`;
    historyNode.appendChild(li);
  }
}

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  resultNode.textContent = "Analyzing...";

  const formData = new FormData(form);

  try {
    const response = await fetch("/api/analyze", {
      method: "POST",
      body: formData,
    });

    const payload = await response.json();
    if (!response.ok) {
      throw new Error(payload.error || "Analysis failed.");
    }

    resultNode.textContent = JSON.stringify(payload, null, 2);
    await loadHistory();
  } catch (error) {
    resultNode.textContent = `Error: ${error.message}`;
  }
});

loadHistory();
