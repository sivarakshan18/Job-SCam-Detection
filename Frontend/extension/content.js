console.log("📬 Job Scam Detector - Content Script Loaded");

// ✅ Create "Scan for Job Scam" button
function createScanButton() {
  const button = document.createElement('div');
  button.className = 'T-I J-J5-Ji aoO v7 T-I-atl L3';
  button.style.marginRight = '8px';
  button.style.backgroundColor = '#4285F4';
  button.style.color = 'white';
  button.innerText = 'Scan for Job Scam';
  button.setAttribute('role', 'button');
  button.setAttribute('data-tooltip', 'Detect Fake Job Emails');
  return button;
}

// ✅ Extract the visible email content
function getEmailContent() {
  const selectors = ['.a3s.aiL', '.ii.gt', '.adn.ads', '[role="presentation"]'];
  for (const selector of selectors) {
    const content = document.querySelector(selector);
    if (content) {
      return content.innerText.trim();
    }
  }
  return '';
}

// ✅ Find Gmail’s toolbar (Compose / Read window)
function findToolbar() {
  const selectors = ['.btC', '.aDh', '[role="toolbar"]', '.gU.Up'];
  for (const selector of selectors) {
    const toolbar = document.querySelector(selector);
    if (toolbar) return toolbar;
  }
  return null;
}

// ✅ Inject our button
function injectButton() {
  const existing = document.querySelector('.job-scan-button');
  if (existing) return; // Avoid duplicates

  const toolbar = findToolbar();
  if (!toolbar) {
    console.log("Toolbar not found yet");
    return;
  }

  console.log("🧩 Toolbar found, injecting Job Scam Detector button");
  const button = createScanButton();
  button.classList.add('job-scan-button');

  // On click → analyze email
  button.addEventListener('click', async () => {
    const emailText = getEmailContent();
    if (!emailText) {
      alert("⚠️ No email content found!");
      return;
    }

    button.innerText = "Analyzing...";
    button.style.backgroundColor = "#999";

    try {
      const response = await fetch("http://127.0.0.1:5000/predict", {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text: emailText })
      });

      const data = await response.json();
      if (data.error) throw new Error(data.error);

      const resultText = `🧠 Prediction: ${data.prediction_label}\nConfidence: ${data.confidence}`;
      console.log(resultText);
      alert(resultText); // simple popup result

      // Color feedback
      if (data.fraudulent === 1) {
        button.style.backgroundColor = 'red';
        button.innerText = "🚨 Scam Detected";
      } else {
        button.style.backgroundColor = 'green';
        button.innerText = "✅ Safe Email";
      }
    } catch (err) {
      console.error(err);
      alert("❌ Error: Could not connect to Flask API.");
      button.style.backgroundColor = '#d93025';
      button.innerText = "API Error";
    } finally {
      setTimeout(() => {
        button.style.backgroundColor = '#4285F4';
        button.innerText = 'Scan for Job Scam';
      }, 3000);
    }
  });

  toolbar.insertBefore(button, toolbar.firstChild);
}

// ✅ Watch Gmail for new compose or read windows
const observer = new MutationObserver(() => {
  const composeOrRead = document.querySelector('.aDh, .btC, [role="dialog"], .a3s.aiL');
  if (composeOrRead) {
    setTimeout(injectButton, 700);
  }
});

observer.observe(document.body, { childList: true, subtree: true });
