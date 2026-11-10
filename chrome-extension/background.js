/**
 * ExamPilot 2.0 Background Service Worker — GT InnoX LLP
 * Manifest V3 Cloud Companion connected to ExamPilot SaaS REST API.
 */

const DEFAULT_BACKEND_URL = "http://127.0.0.1:8000/api";

chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.action === "CAPTURE_VISIBLE_TAB") {
    chrome.tabs.captureVisibleTab(null, { format: "png" }, (dataUrl) => {
      if (chrome.runtime.lastError || !dataUrl) {
        sendResponse({ success: false, error: chrome.runtime.lastError?.message || "Capture failed" });
      } else {
        sendResponse({ success: true, dataUrl });
      }
    });
    return true; // Keep channel open for async response
  }

  if (message.action === "GET_CONFIG") {
    chrome.storage.local.get(["backendUrl", "authToken"], (res) => {
      sendResponse({
        backendUrl: res.backendUrl || DEFAULT_BACKEND_URL,
        authToken: res.authToken || null
      });
    });
    return true;
  }
});
