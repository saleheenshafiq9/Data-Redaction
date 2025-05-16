document.addEventListener('DOMContentLoaded', function() {
    const sendButton = document.getElementById('send');
    const statusDiv = document.getElementById('status');
    
    // Check if we're on a PDF page
    chrome.tabs.query({active: true, currentWindow: true}, function(tabs) {
      const currentTab = tabs[0];
      const isPdf = currentTab.url && (
        currentTab.url.endsWith('.pdf') || 
        currentTab.url.includes('.pdf?') ||
        currentTab.url.toLowerCase().includes('application/pdf') ||
        currentTab.url.startsWith('data:application/pdf')
      );
      
      if (!isPdf) {
        statusDiv.textContent = 'Warning: Current page does not appear to be a PDF';
        statusDiv.className = 'error';
        // We'll still allow the button to be clicked
      }
    });
    
    // Set up button click handler
    sendButton.addEventListener('click', function() {
      statusDiv.textContent = 'Sending PDF to redaction server...';
      statusDiv.className = '';
      
      // Send message to background script
      chrome.runtime.sendMessage({ action: 'send-pdf' }, function(response) {
        // This might not be called if background script uses sendResponse asynchronously
        if (response) {
          statusDiv.textContent = response.message || 'Operation completed';
          statusDiv.className = response.success ? 'success' : 'error';
        }
      });
      
      // Listen for any errors from background
      chrome.runtime.onMessage.addListener(function(message) {
        if (message.type === 'pdf-status') {
          statusDiv.textContent = message.message;
          statusDiv.className = message.success ? 'success' : 'error';
        }
      });
    });
  });