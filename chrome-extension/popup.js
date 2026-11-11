/**
 * ExamPilot 2.0 Popup Controller
 * Connects directly to ExamPilot SaaS backend REST API.
 */

let backendUrl = "http://127.0.0.1:8000/api";
let authToken = "";

document.addEventListener("DOMContentLoaded", async () => {
  // Load saved settings
  chrome.storage.local.get(["backendUrl", "authToken"], (res) => {
    if (res.backendUrl) {
      backendUrl = res.backendUrl;
      const inp = document.getElementById("backendUrlInput");
      if (inp) inp.value = backendUrl;
    }
    if (res.authToken) {
      authToken = res.authToken;
      const inp = document.getElementById("authTokenInput");
      if (inp) inp.value = authToken;
    }
  });

  // Tab switching
  const tabs = [
    { btn: "tabCapture", sec: "captureSection" },
    { btn: "tabManual", sec: "manualSection" },
    { btn: "tabConfig", sec: "configSection" }
  ];

  tabs.forEach(t => {
    const btn = document.getElementById(t.btn);
    btn?.addEventListener("click", () => {
      tabs.forEach(o => {
        document.getElementById(o.btn)?.classList.remove("active");
        document.getElementById(o.sec)?.classList.remove("active");
      });
      btn.classList.add("active");
      document.getElementById(t.sec)?.classList.add("active");
    });
  });

  // Save config
  document.getElementById("btnSaveConfig")?.addEventListener("click", () => {
    const url = document.getElementById("backendUrlInput").value.trim();
    const token = document.getElementById("authTokenInput").value.trim();
    backendUrl = url || backendUrl;
    authToken = token;
    chrome.storage.local.set({ backendUrl, authToken }, () => {
      alert("Settings saved successfully!");
    });
  });

  // Screen Capture and OCR
  document.getElementById("btnCaptureScreen")?.addEventListener("click", async () => {
    showLoading("Capturing screen and running RapidOCR...");
    hideError();
    hideResult();

    chrome.runtime.sendMessage({ action: "CAPTURE_VISIBLE_TAB" }, async (resp) => {
      if (!resp || !resp.success || !resp.dataUrl) {
        showError(resp?.error || "Failed to capture browser tab.");
        hideLoading();
        return;
      }

      try {
        // Send base64 to /api/ocr/image
        const formData = new FormData();
        formData.append("image_base64", resp.dataUrl);

        const ocrRes = await fetch(`${backendUrl}/ocr/image`, {
          method: "POST",
          body: formData
        });

        if (!ocrRes.ok) {
          throw new Error(`OCR processing failed: HTTP ${ocrRes.status}`);
        }

        const ocrData = await ocrRes.json();
        const qText = ocrData.parsed_question || ocrData.raw_text;
        const opts = ocrData.options || {};

        if (!qText || Object.keys(opts).length < 2) {
          throw new Error("Could not detect a clear MCQ structure on this screen. Try highlighting the question text instead.");
        }

        // Now run AI Analysis
        showLoading("Analyzing question with cloud AI provider...");
        await executeAnalysis(qText, opts);
      } catch (err) {
        showError(err.message);
      } finally {
        hideLoading();
      }
    });
  });

  // Extract Selected Text from tab
  document.getElementById("btnExtractSelectedText")?.addEventListener("click", async () => {
    showLoading("Extracting highlighted text...");
    hideError();
    hideResult();

    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
    if (!tab?.id) {
      showError("No active browser tab found.");
      hideLoading();
      return;
    }

    try {
      const results = await chrome.scripting.executeScript({
        target: { tabId: tab.id },
        func: () => window.getSelection().toString()
      });

      const selected = results?.[0]?.result?.trim();
      if (!selected) {
        throw new Error("No text was selected. Highlight the MCQ on the web page first.");
      }

      // Switch to manual view and populate
      document.getElementById("tabManual")?.click();
      document.getElementById("inputQuestion").value = selected;
      hideLoading();
    } catch (err) {
      showError(err.message);
      hideLoading();
    }
  });

  // Manual Solve Button
  document.getElementById("btnAnalyzeManual")?.addEventListener("click", async () => {
    const qText = document.getElementById("inputQuestion").value.trim();
    const opts = {
      A: document.getElementById("optA").value.trim(),
      B: document.getElementById("optB").value.trim(),
      C: document.getElementById("optC").value.trim(),
      D: document.getElementById("optD").value.trim()
    };

    const cleanOpts = {};
    for (const [k, v] of Object.entries(opts)) {
      if (v) cleanOpts[k] = v;
    }

    if (!qText) {
      showError("Please enter a question statement.");
      return;
    }
    if (Object.keys(cleanOpts).length < 2) {
      showError("Please enter at least 2 multiple choice options.");
      return;
    }

    showLoading("Analyzing question with cloud AI provider...");
    hideError();
    hideResult();

    try {
      await executeAnalysis(qText, cleanOpts);
    } catch (err) {
      showError(err.message);
    } finally {
      hideLoading();
    }
  });
});

async function executeAnalysis(questionText, options) {
  const headers = { "Content-Type": "application/json" };
  if (authToken) {
    headers["Authorization"] = `Bearer ${authToken}`;
  }

  const payload = {
    question_text: questionText,
    options: options,
    source_type: "extension"
  };

  const res = await fetch(`${backendUrl}/questions/analyse`, {
    method: "POST",
    headers: headers,
    body: JSON.stringify(payload)
  });

  if (!res.ok) {
    let detail = "AI analysis failed.";
    try {
      const j = await res.json();
      detail = j.detail || detail;
    } catch {}
    throw new Error(detail);
  }

  const data = await res.json();
  renderResult(data);
}

function renderResult(data) {
  document.getElementById("resSuggested").innerText = data.suggested_answer || "A";
  document.getElementById("resConfidence").innerText = (data.confidence?.level || "Medium").toUpperCase();
  document.getElementById("resExplanation").innerText = data.explanation || "";

  const listEl = document.getElementById("resOptionsList");
  listEl.innerHTML = "";
  if (data.option_analysis) {
    Object.entries(data.option_analysis).forEach(([opt, reason]) => {
      const li = document.createElement("li");
      const isCorrect = opt.toUpperCase() === (data.suggested_answer || "").toUpperCase();
      li.innerHTML = `<strong>Option ${opt}:</strong> ${reason}`;
      if (isCorrect) {
        li.style.color = "#22c55e";
        li.style.fontWeight = "bold";
      }
      listEl.appendChild(li);
    });
  }

  document.getElementById("resultSection")?.classList.remove("hidden");
}

function showLoading(msg) {
  const ind = document.getElementById("loadingIndicator");
  const txt = document.getElementById("loadingMsg");
  if (txt && msg) txt.innerText = msg;
  ind?.classList.remove("hidden");
}

function hideLoading() {
  document.getElementById("loadingIndicator")?.classList.add("hidden");
}

function showError(msg) {
  const b = document.getElementById("errorBanner");
  const t = document.getElementById("errorMessage");
  if (t) t.innerText = msg;
  b?.classList.remove("hidden");
}

function hideError() {
  document.getElementById("errorBanner")?.classList.add("hidden");
}

function hideResult() {
  document.getElementById("resultSection")?.classList.add("hidden");
}
