/**
 * ExamPilot Background Service Worker — GT InnoX LLP
 * Manages Native Messaging communication with Desktop application.
 */

const NATIVE_HOST_NAME = "com.gtinnox.exampilot";
let nativePort = null;
let pendingRequests = new Map();

function connectNativeHost() {
  if (nativePort) return nativePort;
  try {
    nativePort = chrome.runtime.connectNative(NATIVE_HOST_NAME);
    
    nativePort.onMessage.addListener((response) => {
      const reqId = response.request_id;
      if (reqId && pendingRequests.has(reqId)) {
        const callback = pendingRequests.get(reqId);
        pendingRequests.delete(reqId);
        callback(response);
      }
    });

    nativePort.onDisconnect.addListener(() => {
      console.warn("ExamPilot Native host disconnected:", chrome.runtime.lastError?.message);
      nativePort = null;
      // Reject any pending requests
      pendingRequests.forEach((cb) => {
        cb({ success: false, error: "Desktop application is disconnected." });
      });
      pendingRequests.clear();
    });

    return nativePort;
  } catch (e) {
    console.error("Failed to connect to ExamPilot Native host:", e);
    nativePort = null;
    return null;
  }
}

chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.target === "native_host") {
    const port = connectNativeHost();
    if (!port) {
      sendResponse({
        success: false,
        error: "Unable to connect to ExamPilot Desktop host. Ensure the application is installed."
      });
      return true;
    }

    const reqId = "req_" + Date.now() + "_" + Math.random().toString(36).substring(2, 7);
    message.payload.request_id = reqId;

    pendingRequests.set(reqId, sendResponse);

    try {
      port.postMessage(message.payload);
    } catch (err) {
      pendingRequests.delete(reqId);
      sendResponse({ success: false, error: "Failed to send message: " + err.message });
    }
    return true; // Keep channel open for async response
  }
});

