// content.js
// Scans all links on the webpage and flags suspicious ones

function checkAndMarkLinks() {
  const links = document.querySelectorAll('a[href]');
  
  links.forEach(link => {
    const url = link.href;
    
    if (!url || url.startsWith('javascript') || url.startsWith('#')) return;
    if (link.dataset.phishingChecked) return;
    
    link.dataset.phishingChecked = 'true';

    chrome.runtime.sendMessage(
      { type: 'CHECK_URL', url: url },
      response => {
        if (!response || !response.success) return;
        
        const data = response.data;
        
        // Create warning badge
        const badge = document.createElement('span');
        badge.style.cssText = `
          display: inline-block;
          margin-left: 4px;
          padding: 1px 6px;
          border-radius: 4px;
          font-size: 11px;
          font-weight: bold;
          vertical-align: middle;
          cursor: help;
        `;

        if (data.verdict === 'PHISHING') {
          badge.style.background = '#ef4444';
          badge.style.color = 'white';
          badge.textContent = '🚨 PHISHING';
          badge.title = `Risk: ${data.risk_score}% — ${data.reasons.join(', ')}`;
          link.style.textDecoration = 'line-through';
          link.style.color = '#ef4444';
        } else if (data.verdict === 'SUSPICIOUS') {
          badge.style.background = '#f59e0b';
          badge.style.color = 'white';
          badge.textContent = '⚠️ SUSPICIOUS';
          badge.title = `Risk: ${data.risk_score}% — ${data.reasons.join(', ')}`;
        } else {
          badge.style.background = '#10b981';
          badge.style.color = 'white';
          badge.textContent = '✅ SAFE';
          badge.title = `Risk: ${data.risk_score}%`;
        }

        link.parentNode.insertBefore(badge, link.nextSibling);
      }
    );
  });
}

// Run on page load
checkAndMarkLinks();

// Run again if new links are added dynamically
const observer = new MutationObserver(checkAndMarkLinks);
observer.observe(document.body, { childList: true, subtree: true });