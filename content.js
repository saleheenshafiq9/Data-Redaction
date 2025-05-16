// This content script helps with PDFs loaded in the browser
console.log("PDF Redactor content script loaded");

// Listen for messages from the background script
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.action === "check-pdf") {
    // Check if this page is a PDF
    const isPdf = document.contentType === "application/pdf";
    sendResponse({isPdf});
    return true;
  }
});