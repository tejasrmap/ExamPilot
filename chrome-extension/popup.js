/**
 * ExamPilot Popup Script — GT InnoX LLP
 */

document.addEventListener("DOMContentLoaded", () => {
  const statusBadge = document.getElementById("connectionStatus");
  const statusText = document.getElementById("statusText");
  const tabCapture = document.getElementById("tabCapture");
  const tabManual = document.getElementById("tabManual");
  const captureSection = document.getElementById("captureSection");
  const manualSection = document.getElementById("manualSection");
  const btnExtract = document.getElementById("btnExtract");
  const btnAnalyzeManual = document.getElementById("btnAnalyzeManual");
  const loadingIndicator = document.getElementById("loadingIndicator");
  const errorBanner = document.getElementById("errorBanner");
  const errorMessage = document.getElementById("errorMessage");
  const resultSection = document.getElementById("resultSection");
  const resSuggested = document.getElementById("resSuggested");
  const resConfidence = document.getElementById("resConfidence");
  const resExplanation = document.getElementById("resExplanation");
  const resOptionsList = document.getElementById("resOptionsList");
  const btnOpenDesktop = document.getElementById("btnOpenDesktop");

  // Tab switching
  tabCapture.addEventListener("click", () => {
    tabCapture.classList.add("active");
    tabManual.classList.remove("active");
    captureSection.classList.add("active");
    manualSection.classList.remove("active");
  });

  tabManual.addEventListener("click", () => {
    tabManual.classList.add("active");
    tabCapture.classList.remove("active");
    manualSection.classList.add("active");
    captureSection.classList.remove("active");
  });

  // Check connection status
  function checkStatus() {
    chrome.runtime.sendMessage(
      { target: "native_host", payload: { action: "ping" } },
      (res) => {
        if (chrome.runtime.lastError || !res || !res.success) {
          statusBadge.className = "status-badge disconnected";
          statusText.textContent = "Disconnected";
        } else {
          statusBadge.className = "status-badge connected";
          statusText.textContent = "Connected";
        }
      }
    );
  }
  checkStatus();

  function showError(msg) {
    errorMessage.textContent = msg;
    errorBanner.classList.remove("hidden");
    loadingIndicator.classList.add("hidden");
  }

  function hideError() {
    errorBanner.classList.add("hidden");
  }

  function showLoading(show) {
    if (show) {
      hideError();
      loadingIndicator.classList.remove("hidden");
      resultSection.classList.add("hidden");
    } else {
      loadingIndicator.classList.add("hidden");
    }
  }

  function renderResult(data) {
    resSuggested.textContent = data.suggested_answer || "-";
    const confVal = Math.round((data.confidence || 0.85) * 100);
    resConfidence.textContent = confVal + "%";
    resExplanation.textContent = data.explanation || "No explanation provided.";

    resOptionsList.innerHTML = "";
    const analysis = data.option_analysis || {};
    for (const [opt, exp] of Object.entries(analysis)) {
      const li = document.createElement("li");
      li.className = (opt === data.suggested_answer) ? "correct" : "incorrect";
      li.innerHTML = `<strong>Option ${opt}:</strong> ${exp}`;
      resOptionsList.appendChild(li);
    }

    resultSection.classList.remove("hidden");
  }

  // Extract from active webpage
  btnExtract.addEventListener("click", async () => {
    hideError();
    showLoading(true);

    try {
      const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
      if (!tab || !tab.id) {
        showError("Unable to access current active tab.");
        showLoading(false);
        return;
      }

      // Ensure content script is injected in active tab
      try {
        await chrome.scripting.executeScript({
          target: { tabId: tab.id },
          files: ["content.js"]
        });
      } catch (injErr) {
        // May already be injected or restricted page
      }

      chrome.tabs.sendMessage(tab.id, { action: "extract_selected_content" }, (response) => {
        showLoading(false);
        if (chrome.runtime.lastError || !response || !response.success) {
          const err = response ? response.error : (chrome.runtime.lastError?.message || "Please highlight a practice question on the page first.");
          showError(err);
          return;
        }

        tabManual.click();
        const extracted = response.text || "";
        
        // Simple regex parser for options A, B, C, D
        const optMatchA = extracted.match(/(?:^|\n)\s*(?:\(?A[\)\.\:\-\]]|\(A\))\s*([^\n]+)/i);
        const optMatchB = extracted.match(/(?:^|\n)\s*(?:\(?B[\)\.\:\-\]]|\(B\))\s*([^\n]+)/i);
        const optMatchC = extracted.match(/(?:^|\n)\s*(?:\(?C[\)\.\:\-\]]|\(C\))\s*([^\n]+)/i);
        const optMatchD = extracted.match(/(?:^|\n)\s*(?:\(?D[\)\.\:\-\]]|\(D\))\s*([^\n]+)/i);

        if (optMatchA && optMatchB) {
          // Extract question statement (everything before option A)
          const qText = extracted.split(/(?:^|\n)\s*(?:\(?A[\)\.\:\-\]]|\(A\))/i)[0].trim();
          document.getElementById("inputQuestion").value = qText || extracted;
          if (optMatchA) document.getElementById("optA").value = optMatchA[1].trim();
          if (optMatchB) document.getElementById("optB").value = optMatchB[1].trim();
          if (optMatchC) document.getElementById("optC").value = optMatchC[1].trim();
          if (optMatchD) document.getElementById("optD").value = optMatchD[1].trim();
        } else {
          document.getElementById("inputQuestion").value = extracted;
        }
      });
    } catch (e) {
      showError("Extraction failed: " + e.message);
      showLoading(false);
    }
  });

  // Analyze question
  btnAnalyzeManual.addEventListener("click", () => {
    hideError();
    const qText = document.getElementById("inputQuestion").value.trim();
    const optA = document.getElementById("optA").value.trim();
    const optB = document.getElementById("optB").value.trim();
    const optC = document.getElementById("optC").value.trim();
    const optD = document.getElementById("optD").value.trim();

    if (!qText) {
      showError("Please enter the question text.");
      return;
    }

    const options = {};
    if (optA) options["A"] = optA;
    if (optB) options["B"] = optB;
    if (optC) options["C"] = optC;
    if (optD) options["D"] = optD;

    if (Object.keys(options).length < 2) {
      showError("Please enter at least 2 options.");
      return;
    }

    showLoading(true);

    const payload = {
      action: "analyze_question",
      payload: {
        question: qText,
        options: options,
        subject_name: "General"
      }
    };

    chrome.runtime.sendMessage({ target: "native_host", payload: payload }, (res) => {
      showLoading(false);
      if (chrome.runtime.lastError || !res || !res.success) {
        const err = res ? res.error : (chrome.runtime.lastError?.message || "Failed to connect to local AI.");
        showError(err);
        return;
      }

      renderResult(res.data);
    });
  });

  // Open Desktop
  btnOpenDesktop.addEventListener("click", () => {
    chrome.runtime.sendMessage({ target: "native_host", payload: { action: "open_desktop" } });
  });
});

