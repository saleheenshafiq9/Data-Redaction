// Helper to check if URL is a PDF
function isPdfUrl(url) {
    return url && (
      url.endsWith('.pdf') || 
      url.includes('.pdf?') || 
      url.toLowerCase().includes('application/pdf') ||
      url.startsWith('data:application/pdf')
    );
  }
  
  // Helper to actually send the PDF off
  async function sendPdfFromTab(tab) {
    try {
      console.log("Processing tab:", tab.url);
      
      // 1) Verify we have a PDF URL
      if (!isPdfUrl(tab.url)) {
        throw new Error("Current tab doesn't appear to be a PDF. URL must end with .pdf");
      }
  
      // 2) Grab PDF bytes
      console.log("Fetching PDF content...");
      const res = await fetch(tab.url);
      if (!res.ok) throw new Error(`Cannot fetch PDF: ${res.status} ${res.statusText}`);
      
      const pdfBlob = await res.blob();
      console.log(`PDF fetched, size: ${pdfBlob.size} bytes`);
      
      // 3) Build FormData
      const form = new FormData();
      form.append("file", pdfBlob, "document.pdf");
      
      // 4) POST to FastAPI
      console.log("Sending to FastAPI server...");
      const apiRes = await fetch("http://localhost:8000/upload", {
        method: "POST",
        body: form
      });
      
      if (!apiRes.ok) {
        const errorText = await apiRes.text();
        throw new Error(`Upload failed: ${apiRes.status} - ${errorText}`);
      }
      
      const json = await apiRes.json();
      console.log("Backend response:", json);
      
      // 5) Notify on success
      chrome.notifications.create({
        type: "basic",
        iconUrl: "icon48.png",
        title: "PDF Redactor",
        message: "Upload succeeded! Check the console for details."
      });
    } catch (err) {
      console.error("PDF processing error:", err);
      
      chrome.notifications.create({
        type: "basic",
        iconUrl: "icon48.png",
        title: "PDF Redactor Error",
        message: err.message
      });
    }
  }
  
  // 1) Handle toolbar icon clicks
  chrome.action.onClicked.addListener(tab => {
    console.log("Action clicked for tab:", tab.url);
    sendPdfFromTab(tab);
  });
  
  // 2) Handle messages from popup.html
  chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
    console.log("Received message:", message);
    
    if (message.action === "send-pdf") {
      // Find the active tab in the current window
      chrome.tabs.query({ active: true, currentWindow: true }, tabs => {
        if (!tabs[0] || !tabs[0].url) {
          return chrome.notifications.create({
            type: "basic",
            iconUrl: "icon48.png",
            title: "PDF Redactor Error",
            message: "No active tab found."
          });
        }
        
        console.log("Processing active tab:", tabs[0].url);
        sendPdfFromTab(tabs[0]);
      });
      
      // Indicate we'll respond asynchronously
      return true;
    }
  });