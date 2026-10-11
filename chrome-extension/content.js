/**
 * ExamPilot Content Script — GT InnoX LLP
 * Permitted Practice Question Extraction
 * Operates strictly upon user-initiated request.
 */

chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === "extract_selected_content") {
    try {
      const selection = window.getSelection().toString().trim();
      if (selection) {
        sendResponse({ success: true, text: selection });
      } else {
        sendResponse({
          success: false,
          error: "No text currently selected. Highlight an MCQ on the page and try again."
        });
      }
    } catch (err) {
      sendResponse({ success: false, error: err.message });
    }
  }
  return true;
});

