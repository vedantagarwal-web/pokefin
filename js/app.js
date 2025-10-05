// Minimal chat MVP (frontend) wired to Poke-like backend endpoints

const chatEl = document.getElementById('chat');
const inputEl = document.getElementById('msg');
const sendBtn = document.getElementById('send');
const resetBtn = document.getElementById('resetBtn');
let connectBrokerageBtn = null;

const STORAGE_KEY_BASE = 'pokefin.chat.v1';
const SESSION_KEY = 'pokefin.session.v1';
const API_BASE = '/api/v2';

const sessionId = getSessionId();
const state = {
  messages: load(),
  typingId: null,
};

function storageKey() { return `${STORAGE_KEY_BASE}.${sessionId}`; }

function load() {
  try {
    const raw = localStorage.getItem(storageKey());
    if (!raw) return [];
    return JSON.parse(raw);
  } catch { return []; }
}

function save() {
  localStorage.setItem(storageKey(), JSON.stringify(state.messages));
}

function now() { return new Date().toISOString(); }

function addMessage(role, text) {
  const msg = { id: crypto.randomUUID(), role, text, t: now() };
  state.messages.push(msg);
  save();
  renderMessage(msg);
  scrollToBottom();
  return msg;
}

function renderAll() {
  chatEl.innerHTML = '';
  state.messages.forEach(renderMessage);
  scrollToBottom();
}

function linkifyText(text) {
  // Escape HTML to prevent XSS
  const escaped = text
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;');
  
  // Convert markdown formatting (simplified for browser compatibility)
  let formatted = escaped
    // Bold: **text** (must be converted BEFORE single *)
    .replace(/\*\*([^*]+?)\*\*/g, '<strong>$1</strong>')
    // Inline code: `text`
    .replace(/`([^`]+?)`/g, '<code style="background: var(--color-surface-elevated); padding: 2px 6px; border-radius: 4px; font-family: var(--font-mono); font-size: 13px;">$1</code>');
  
  // Convert URLs to clickable links (styling handled by CSS)
  const urlPattern = /(https?:\/\/[^\s]+)/g;
  const linked = formatted.replace(urlPattern, '<a href="$1" target="_blank" rel="noopener noreferrer">$1</a>');
  
  // Convert newlines to <br>
  return linked.replace(/\n/g, '<br>');
}

function renderMessage(msg) {
  const row = document.createElement('div');
  row.className = `row ${msg.role}`;  // Use 'user' or 'assistant' directly

  const bubble = document.createElement('div');
  bubble.className = 'bubble';
  bubble.innerHTML = linkifyText(msg.text);
  row.appendChild(bubble);

  // Check if this is a research recommendation (contains "Recommendation:" or "Conviction:")
  if (msg.role === 'assistant' && msg.text && (msg.text.includes('🎯 Recommendation:') || msg.text.includes('Conviction:'))) {
    // Try to extract ticker from message - look for pattern like "TSLA" or "on TSLA"
    const tickerMatch = msg.text.match(/(?:on |research on |deep research on |for )([A-Z]{2,5})\b/i) || msg.text.match(/\b([A-Z]{2,5})\b/);
    if (tickerMatch) {
      const ticker = tickerMatch[1].toUpperCase();
      
      // Parse the research data from the message text
      const researchData = parseResearchData(msg.text, ticker);
      
      // Save research data to localStorage
      localStorage.setItem(`research_${ticker}`, JSON.stringify(researchData));
      localStorage.setItem(`has_research_${ticker}`, 'true');
      
      console.log(`📋 Saved research data for ${ticker}`);
      
      // Add whiteboard button
      const whiteboardBtn = document.createElement('button');
      whiteboardBtn.textContent = '📋 Open Whiteboard';
      whiteboardBtn.className = 'whiteboard-btn';
      whiteboardBtn.onclick = () => window.open(`whiteboard.html?ticker=${ticker}`, '_blank');
      row.appendChild(whiteboardBtn);
    }
  }
  
  function parseResearchData(text, ticker) {
    // Extract key data from the formatted text
    const data = { ticker };
    
    // Extract recommendation
    const recMatch = text.match(/🎯 Recommendation:\s*(\w+)/);
    if (recMatch) data.action = recMatch[1];
    
    // Extract conviction
    const convMatch = text.match(/Conviction:\s*(\d+)\/10/);
    if (convMatch) data.conviction = parseInt(convMatch[1]);
    
    // Extract prices
    const priceMatch = text.match(/Price:\s*\$?([\d.]+)\s*→\s*\$?([\d.]+)\s*\(([+-]?[\d.]+)%\)/);
    if (priceMatch) {
      data.current_price = parseFloat(priceMatch[1]);
      data.target_price = parseFloat(priceMatch[2]);
      data.upside_pct = parseFloat(priceMatch[3]);
    }
    
    // Extract key thesis
    const thesisMatch = text.match(/💡 Key Thesis:\s*([^\n]+)/);
    if (thesisMatch) data.key_thesis = thesisMatch[1];
    
    // Extract data sections with improved regex
    const sections = {
      price_data: {},
      fundamentals: {},
      sentiment_data: {},
      news_headlines: []
    };
    
    // Parse market data
    const marketDataMatch = text.match(/📊 Market Data:[\s\S]*?(?=📊|✅|⚠️|🎯|$)/);
    if (marketDataMatch) {
      const marketText = marketDataMatch[0];
      const priceMatch2 = marketText.match(/Current Price:\s*\$?([\d.,]+)/);
      if (priceMatch2) sections.price_data.current_price = parseFloat(priceMatch2[1].replace(/,/g, ''));
      
      const marketCapMatch = marketText.match(/Market Cap:\s*\$?([\d.]+)([BMT])/);
      if (marketCapMatch) {
        let cap = parseFloat(marketCapMatch[1]);
        const unit = marketCapMatch[2];
        if (unit === 'T') cap *= 1e12;
        else if (unit === 'B') cap *= 1e9;
        else if (unit === 'M') cap *= 1e6;
        sections.price_data.market_cap = cap;
      }
    }
    
    // Parse fundamentals
    const fundMatch = text.match(/P\/E Ratio:\s*([\d.]+)/);
    if (fundMatch) sections.fundamentals.pe_ratio = parseFloat(fundMatch[1]);
    
    const marginMatch = text.match(/Profit Margin:\s*([\d.]+)%/);
    if (marginMatch) sections.fundamentals.profit_margin = parseFloat(marginMatch[1]);
    
    const growthMatch = text.match(/Revenue Growth:\s*([\d.]+)%/);
    if (growthMatch) sections.fundamentals.revenue_growth = parseFloat(growthMatch[1]);
    
    // Parse social sentiment
    const redditMatch = text.match(/Reddit:\s*([A-Z\s]+)\s*\((\d+)% bullish,\s*(\d+) mentions\)/);
    if (redditMatch) {
      sections.sentiment_data.reddit = {
        sentiment_label: redditMatch[1].trim(),
        sentiment_score: parseInt(redditMatch[2]) / 100,
        mention_volume: parseInt(redditMatch[3])
      };
    }
    
    const twitterMatch = text.match(/Twitter:\s*([A-Z\s]+)\s*\((\d+)% bullish/);
    if (twitterMatch) {
      sections.sentiment_data.twitter = {
        sentiment_label: twitterMatch[1].trim(),
        sentiment_score: parseInt(twitterMatch[2]) / 100
      };
    }
    
    return { ...data, ...sections };
  }

  // Render charts if present
  if (msg.charts && msg.charts.length > 0) {
    console.log('📊 Rendering', msg.charts.length, 'chart(s)');
    msg.charts.forEach((chartData, idx) => {
      console.log(`Chart ${idx}:`, chartData.type, chartData.ticker);
      const chartContainer = window.chartManager.createChartContainer();
      row.appendChild(chartContainer);
      
      // Render chart after DOM insertion
      setTimeout(() => {
        try {
          if (chartData.type === 'comparison') {
            window.chartManager.renderComparisonChart(chartContainer.id, chartData);
          } else if (chartData.type === 'heatmap') {
            window.chartManager.renderSectorHeatmap(chartContainer.id, chartData);
          } else {
            window.chartManager.renderPriceChart(chartContainer.id, chartData);
          }
          console.log('✅ Chart rendered:', chartContainer.id);
        } catch (e) {
          console.error('❌ Chart render error:', e);
        }
      }, 100);
    });
  }

  chatEl.appendChild(row);
}

function renderTyping() {
  const row = document.createElement('div');
  row.className = 'row assistant';  // Match CSS expectations
  row.dataset.typing = '1';

  const bubble = document.createElement('div');
  bubble.className = 'bubble typing-bubble';
  
  // Create animated dots
  const wrap = document.createElement('div');
  wrap.className = 'typing';
  for (let i = 0; i < 3; i++) {
    const dot = document.createElement('span');
    dot.className = 'dot';
    wrap.appendChild(dot);
  }
  
  bubble.appendChild(wrap);
  row.appendChild(bubble);
  chatEl.appendChild(row);
  scrollToBottom();
  return row;
}

function clearTyping() {
  const node = chatEl.querySelector('[data-typing="1"]');
  if (node) node.remove();
}

function scrollToBottom() {
  requestAnimationFrame(() => {
    chatEl.scrollTop = chatEl.scrollHeight + 9999;
  });
}

function bootstrapIfEmpty() {
  if (state.messages.length === 0) {
    addMessage('assistant',
      "Welcome to Orthogonal. Ask me about any stock for institutional-grade analysis.\n\nTry: 'Should I buy Tesla?' or 'Compare NVDA vs AMD'");
  } else {
    renderAll();
  }
}

function setSending(disabled) {
  inputEl.disabled = disabled;
  sendBtn.disabled = disabled;
}

async function onSend() {
  const text = inputEl.value.trim();
  if (!text) return;
  inputEl.value = '';
  resizeTextarea();

  addMessage('user', text);
  setSending(true);

  const typingNode = renderTyping();
  try {
    await sendToBackend(text);
    // Poll for assistant response
    await pollForAssistant(text, { attempts: 30, intervalMs: 1000 });
    clearTyping();
    // Sync UI with server history
    await syncHistory();
  } catch (err) {
    console.error(err);
    clearTyping();
    addMessage('assistant', "Error processing your request. Please try again or rephrase your question.");
  } finally {
    setSending(false);
  }
}

function resizeTextarea() {
  inputEl.style.height = 'auto';
  inputEl.style.height = Math.min(160, inputEl.scrollHeight) + 'px';
}

async function sendToBackend(text) {
  // Build conversation history from current messages
  const history = state.messages.map(m => ({
    role: m.role,
    content: m.text
  }));
  
  // Add the new user message
  history.push({ role: 'user', content: text });
  
  const res = await fetch(`${API_BASE}/chat/send`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      session: sessionId,
      messages: history,
    }),
  });
  if (!(res.ok || res.status === 202)) {
    const detail = await res.text();
    throw new Error(detail || `Request failed (${res.status})`);
  }
}

async function pollForAssistant(userText, { attempts = 20, intervalMs = 1000 } = {}) {
  for (let i = 0; i < attempts; i++) {
    await new Promise(r => setTimeout(r, intervalMs));
    const data = await fetch(`${API_BASE}/chat/history?session=${encodeURIComponent(sessionId)}`, { cache: 'no-store' }).then(r => r.json()).catch(() => null);
    if (!data || !Array.isArray(data.messages)) continue;
    const current = data.messages;
    const hasUser = current.some(m => m.role === 'user' && (m.content || m.text) === userText);
    const last = current[current.length - 1];
    const assistantReplied = hasUser && last && last.role === 'assistant';
    if (assistantReplied) return;
  }
}

async function syncHistory() {
  try {
    const data = await fetch(`${API_BASE}/chat/history?session=${encodeURIComponent(sessionId)}`, { cache: 'no-store' }).then(r => r.json());
    if (Array.isArray(data?.messages)) {
      // Map server shape to UI shape, preserving charts
      state.messages = data.messages.map((m, i) => ({ 
        id: m.id || `srv-${i}`, 
        role: m.role, 
        text: m.content || m.text, 
        t: m.timestamp || now(),
        charts: m.charts || []
      }));
      save();
      renderAll();
    }
  } catch (e) {
    console.error('syncHistory failed', e);
  }
}

function onReset() {
  fetch(`${API_BASE}/chat/history?session=${encodeURIComponent(sessionId)}`, { method: 'DELETE' })
    .catch(() => {})
    .finally(async () => {
      state.messages = [];
      save();
      renderAll();
      bootstrapIfEmpty();
    });
}

// Events
sendBtn.addEventListener('click', onSend);
resetBtn.addEventListener('click', onReset);
inputEl.addEventListener('keydown', (e) => {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault();
    onSend();
  }
});
inputEl.addEventListener('input', resizeTextarea);

// Init
syncHistory().finally(() => {
  renderAll();
  bootstrapIfEmpty();
  resizeTextarea();
});

function getSessionId() {
  try {
    const existing = localStorage.getItem(SESSION_KEY);
    if (existing && existing.length > 0) return existing;
    const id = crypto.randomUUID();
    localStorage.setItem(SESSION_KEY, id);
    return id;
  } catch {
    // Fallback for very old browsers or blocked storage
    return 'default';
  }
}

// Robinhood Connection Modal Functions
function openBrokerageModal() {
  console.log('Opening brokerage modal');
  const modal = document.getElementById('brokerageModal');
  if (modal) {
    modal.style.display = 'flex';
    resetConnectionFlow();
    console.log('Brokerage modal opened successfully');
  } else {
    console.error('Brokerage modal element not found');
  }
}

function closeBrokerageModal() {
  document.getElementById('brokerageModal').style.display = 'none';
}

function resetConnectionFlow() {
  console.log('Resetting connection flow');
  
  // Clear any existing SnapTrade credentials
  localStorage.removeItem('snaptrade_user_id');
  localStorage.removeItem('snaptrade_user_secret');
  localStorage.removeItem('snaptrade_connected');
  localStorage.removeItem('snaptrade_connected_at');
  console.log('Cleared existing SnapTrade credentials');
  
  const step1 = document.getElementById('connectionStep1');
  const step2 = document.getElementById('connectionStep2');
  const step3 = document.getElementById('connectionStep3');
  const error = document.getElementById('connectionError');
  
  console.log('Found elements:', { step1: !!step1, step2: !!step2, step3: !!step3, error: !!error });
  
  if (step1) {
    step1.classList.add('active');
    step1.style.display = 'block'; // Force visibility
    console.log('Step1 classes:', step1.className);
  }
  if (step2) {
    step2.classList.remove('active');
    step2.style.display = 'none';
  }
  if (step3) {
    step3.classList.remove('active');
    step3.style.display = 'none';
  }
  if (error) {
    error.classList.remove('active');
    error.style.display = 'none';
  }
  
  console.log('Connection flow reset complete');
}

function showConnectionStep(stepNumber) {
  console.log(`Showing connection step ${stepNumber}`);
  // Hide all steps
  document.querySelectorAll('.connection-step').forEach(step => {
    step.classList.remove('active');
    step.style.display = 'none';
  });
  
  // Show the requested step
  const targetStep = document.getElementById(`connectionStep${stepNumber}`);
  if (targetStep) {
    targetStep.classList.add('active');
    targetStep.style.display = 'block'; // Force visibility
    console.log(`Step ${stepNumber} classes:`, targetStep.className);
  } else {
    console.error(`Connection step ${stepNumber} not found`);
  }
}

function showConnectionError(errorMessage) {
  console.log('Showing connection error:', errorMessage);
  document.querySelectorAll('.connection-step').forEach(step => {
    step.classList.remove('active');
    step.style.display = 'none';
  });
  const errorElement = document.getElementById('connectionError');
  if (errorElement) {
    errorElement.classList.add('active');
    errorElement.style.display = 'block'; // Force visibility
    document.getElementById('errorText').textContent = errorMessage;
  }
}

async function showRobinhoodOAuth() {
  try {
    console.log('Starting Robinhood OAuth2 flow');
    
    // Get SnapTrade connection portal URL from backend
    console.log('Fetching SnapTrade connection URL from backend...');
    const response = await fetch('http://localhost:8788/api/snaptrade/connect');
    console.log('Response status:', response.status);
    
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }
    
    const connectionData = await response.json();
    console.log('Connection data received:', connectionData);
    
    if (connectionData.success) {
            const connectionUrlElement = document.getElementById('connectionUrl');
            const instructionsElement = document.querySelector('.instructions ol');
            
            if (connectionUrlElement) {
                const connectionUrl = connectionData.portal_url;
                console.log('SnapTrade Portal URL:', connectionData);
                
                // Store user credentials for the callback
                if (connectionData.user_id && connectionData.user_secret) {
                    sessionStorage.setItem('snaptrade_user_id', connectionData.user_id);
                    sessionStorage.setItem('snaptrade_user_secret', connectionData.user_secret);
                    console.log('SnapTrade user credentials stored in session');
                    
                    // Add user credentials to the portal URL for callback
                    const urlWithCredentials = new URL(connectionUrl);
                    urlWithCredentials.searchParams.set('userId', connectionData.user_id);
                    urlWithCredentials.searchParams.set('userSecret', connectionData.user_secret);
                    
                    // Update the connection URL
                    connectionUrlElement.href = urlWithCredentials.toString();
                    console.log('Updated portal URL with credentials:', urlWithCredentials.toString());
                } else {
                    connectionUrlElement.href = connectionUrl;
                }
                
                // Update button text based on mode
                if (connectionData.credentials_issue) {
                    connectionUrlElement.textContent = '⚠️ SnapTrade Demo (Invalid Credentials)';
                } else if (connectionData.mock) {
                    connectionUrlElement.textContent = '🔗 Connect via SnapTrade (Demo)';
                } else {
                    connectionUrlElement.textContent = '🔗 Connect via SnapTrade';
                }
                
                console.log('Connection URL element updated');
            } else {
                console.error('Connection URL element not found');
            }
            
            showConnectionStep(2);
            console.log('Showing connection step 2');
            
            // Update instructions based on connection mode
            if (instructionsElement) {
        if (connectionData.credentials_issue) {
          instructionsElement.innerHTML = `
            <li><strong>⚠️ SnapTrade Credentials Issue:</strong></li>
            <li>Your SNAPTRADE_CLIENT_ID and SNAPTRADE_CONSUMER_KEY appear to be invalid</li>
            <li>Click the demo link above to see the error message</li>
            <li><strong>To fix:</strong></li>
            <li>1. Register for SnapTrade API access at <a href="https://snaptrade.com/register" target="_blank" style="color: #00d4aa;">snaptrade.com/register</a></li>
            <li>2. Get your Client ID and Consumer Key from the dashboard</li>
            <li>3. Update your .env file with valid credentials</li>
            <li>4. For testing, you can use Alpaca Paper Trading</li>
            <li>Alternatively, use "Check Connection" to simulate success</li>
          `;
        } else if (connectionData.mock) {
          instructionsElement.innerHTML = `
            <li>Click "Connect via SnapTrade (Demo)" above</li>
            <li>You'll see SnapTrade's demo/error page</li>
            <li>This demonstrates the connection flow</li>
            <li>For real connections, valid SnapTrade credentials are required</li>
            <li>Return here and click "Check Connection" to simulate success</li>
          `;
        } else {
          instructionsElement.innerHTML = `
            <li>Click "Connect via SnapTrade" above</li>
            <li>You'll be redirected to SnapTrade's secure portal</li>
            <li>Select your brokerage (Robinhood, TD Ameritrade, etc.)</li>
            <li>Log in to your brokerage account</li>
            <li>Authorize access to your account data</li>
            <li>You'll be redirected back to complete the connection</li>
            <li>Click "Check Connection" to verify the connection</li>
            <li><strong>Note:</strong> Connection links expire in 5 minutes</li>
          `;
        }
        console.log('Instructions updated');
      } else {
        console.error('Instructions element not found');
      }
    } else {
      throw new Error(connectionData.error || 'Failed to get SnapTrade connection URL');
    }
  } catch (error) {
    console.error('SnapTrade setup error:', error);
    
    // Show helpful error message with retry option
    showConnectionError(`
      <div style="text-align: left;">
        <h4>SnapTrade Connection Issue</h4>
        <p>Failed to setup SnapTrade connection: ${error.message}</p>
        <p><strong>Common causes:</strong></p>
        <ul style="margin: 10px 0; padding-left: 20px;">
          <li>Connection link expired (links expire in 5 minutes)</li>
          <li>Network connectivity issues</li>
          <li>SnapTrade service temporarily unavailable</li>
        </ul>
        <button onclick="resetConnectionFlow(); showRobinhoodOAuth();" style="margin-top: 10px; padding: 8px 16px; background: #00d4aa; color: white; border: none; border-radius: 4px; cursor: pointer;">
          🔄 Try Again
        </button>
      </div>
    `);
  }
}

function showMockConnection() {
  // Show mock connection URL for demo purposes
  const mockUrl = 'https://app.snaptrade.com/connect?demo=true&brokerage=robinhood';
  document.getElementById('connectionUrl').href = mockUrl;
  document.getElementById('connectionUrl').textContent = '🔗 Connect Robinhood Account (Demo)';
  showConnectionStep(2);
  
  // Update instructions for demo
  const instructions = document.querySelector('.instructions ol');
  if (instructions) {
    instructions.innerHTML = `
      <li>Click the connection link above (Demo Mode)</li>
      <li>You'll see a demo connection flow</li>
      <li>For real connection, SnapTrade integration is required</li>
      <li>Click "Check Connection" to simulate success</li>
      <li>Then click "Analyze Portfolio" to see demo data</li>
    `;
  }
}

// Brokerage Connection Event Listeners - moved to DOMContentLoaded

document.addEventListener('DOMContentLoaded', function() {
  // Initialize brokerage connection button
  connectBrokerageBtn = document.getElementById('connectBrokerage');
  if (connectBrokerageBtn) {
    console.log('Connect brokerage button found, adding event listener');
    connectBrokerageBtn.addEventListener('click', function() {
      console.log('Connect brokerage button clicked');
      openBrokerageModal();
    });
  } else {
    console.log('Connect brokerage button NOT found');
  }
  
  // Modal close button
  const modalCloseBtn = document.getElementById('modalClose');
  if (modalCloseBtn) {
    modalCloseBtn.addEventListener('click', closeBrokerageModal);
  }
  
  // Reset connection button
  const resetConnectionBtn = document.getElementById('resetConnection');
  if (resetConnectionBtn) {
    resetConnectionBtn.addEventListener('click', resetConnectionFlow);
  }
  
  // Generate Connection Button
  const generateConnectionBtn = document.getElementById('generateConnection');
  console.log('Generate connection button found:', !!generateConnectionBtn);
  if (generateConnectionBtn) {
    console.log('Adding event listener to generate connection button');
    generateConnectionBtn.addEventListener('click', async function() {
      try {
        console.log('Generate connection button clicked');
        
        // Try OAuth2 flow directly first
        await showRobinhoodOAuth();
        
      } catch (error) {
        console.error('Error generating connection:', error);
        showConnectionError('Error generating connection link: ' + error.message);
      }
    });
    console.log('Event listener added successfully');
  } else {
    console.error('Generate connection button NOT found');
  }

  // Debug Connection Button
  const debugConnectionBtn = document.getElementById('debugConnection');
  if (debugConnectionBtn) {
    debugConnectionBtn.addEventListener('click', async function() {
      console.log('=== DEBUG CONNECTION ===');
      
      const snaptradeUserId = localStorage.getItem('snaptrade_user_id');
      const snaptradeUserSecret = localStorage.getItem('snaptrade_user_secret');
      const snaptradeConnected = localStorage.getItem('snaptrade_connected');
      const snaptradeConnectedAt = localStorage.getItem('snaptrade_connected_at');
      
      console.log('LocalStorage data:', {
        userId: snaptradeUserId,
        userSecret: snaptradeUserSecret ? snaptradeUserSecret.substring(0, 10) + '...' : null,
        connected: snaptradeConnected,
        connectedAt: snaptradeConnectedAt
      });
      
      if (snaptradeUserId && snaptradeUserSecret) {
        try {
          const response = await fetch('http://localhost:8788/api/snaptrade/accounts', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              userId: snaptradeUserId,
              userSecret: snaptradeUserSecret
            })
          });
          const result = await response.json();
          console.log('SnapTrade API response:', result);
          
          if (result.success) {
            if (result.accounts && result.accounts.length > 0) {
              alert(`✅ Connection working! Found ${result.accounts.length} accounts:\n${JSON.stringify(result.accounts, null, 2)}`);
            } else {
              alert(`⚠️ SnapTrade user exists but no brokerage accounts connected.\n\nThis means you need to:\n1. Go back to SnapTrade portal\n2. Actually connect your Robinhood account\n3. Complete the brokerage linking process`);
            }
          } else {
            alert(`❌ SnapTrade API error: ${result.error || 'Unknown error'}`);
          }
        } catch (error) {
          console.error('Debug connection error:', error);
          alert(`❌ Network error: ${error.message}`);
        }
      } else {
        alert('❌ No SnapTrade credentials found in localStorage. Please start the connection process.');
      }
    });
  }

  // Check Connection Button
  const checkConnectionBtn = document.getElementById('checkConnection');
  if (checkConnectionBtn) {
    checkConnectionBtn.addEventListener('click', async function() {
      try {
        // Check if we have a stored access token
        const checkStoredToken = localStorage.getItem('robinhood_access_token');
        const checkIsConnected = localStorage.getItem('robinhood_connected') === 'true';
        
        if (checkStoredToken && checkIsConnected) {
          // Real connection - verify with API
          try {
            const response = await fetch(`http://localhost:8788/api/robinhood/accounts?access_token=${checkStoredToken}`);
            const result = await response.json();
            
            if (result.success) {
              document.getElementById('accountInfo').innerHTML = `
                <div>Account Status: Connected (Live)</div>
                <div>Brokerage: Robinhood</div>
                <div>Accounts: ${result.accounts.length}</div>
                <div>Connection Time: ${localStorage.getItem('robinhood_connected_at')}</div>
                <div>Access Token: ${checkStoredToken.substring(0, 20)}...</div>
              `;
              showConnectionStep(3);
              return;
            } else {
              // Token invalid, clear storage
              localStorage.removeItem('robinhood_access_token');
              localStorage.removeItem('robinhood_connected');
              localStorage.removeItem('robinhood_connected_at');
            }
          } catch (error) {
            console.error('Token verification failed:', error);
          }
        }
        
        // Check if we're in demo mode
        const connectionUrl = document.getElementById('connectionUrl').href;
        if (connectionUrl.includes('demo=true')) {
          // Demo mode - simulate successful connection
          document.getElementById('accountInfo').innerHTML = `
            <div>Account Status: Connected (Demo)</div>
            <div>Brokerage: Robinhood</div>
            <div>Account Type: Individual</div>
            <div>Connection Time: ${new Date().toLocaleString()}</div>
            <div>Demo Data: Mock portfolio with sample holdings</div>
          `;
          showConnectionStep(3);
          return;
        }
        
        // Check if we have a stored SnapTrade connection
        const snaptradeUserId = localStorage.getItem('snaptrade_user_id');
        const snaptradeUserSecret = localStorage.getItem('snaptrade_user_secret');
        const snaptradeConnected = localStorage.getItem('snaptrade_connected') === 'true';
        
        if (snaptradeUserId && snaptradeUserSecret && snaptradeConnected) {
          // Verify SnapTrade connection with API
          try {
            const response = await fetch(`http://localhost:8788/api/snaptrade/accounts`, {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({
                userId: snaptradeUserId,
                userSecret: snaptradeUserSecret
              })
            });
            const result = await response.json();
            
            // Check if we have real accounts (not mock accounts)
            const hasRealAccounts = result.success && result.accounts && result.accounts.length > 0 && 
              !(result.accounts.length === 1 && result.accounts[0].id === 'mock_account_1');
            
            if (hasRealAccounts) {
              document.getElementById('accountInfo').innerHTML = `
                <div>Account Status: Connected (Live)</div>
                <div>Brokerage: SnapTrade</div>
                <div>Accounts: ${result.accounts.length}</div>
                <div>Connection Time: ${localStorage.getItem('snaptrade_connected_at')}</div>
                <div>User ID: ${snaptradeUserId.substring(0, 20)}...</div>
              `;
              showConnectionStep(3);
              
              // Close the modal if it's open (user returned from SnapTrade)
              const modal = document.getElementById('brokerageModal');
              if (modal && modal.style.display === 'flex') {
                console.log('Connection successful, closing modal...');
                setTimeout(() => {
                  closeBrokerageModal();
                }, 2000); // Give user time to see the success message
              }
              return;
            } else if (result.success && result.accounts && result.accounts.length === 0) {
              // User is connected but has no brokerage accounts yet - this means they need to actually connect a brokerage
              console.log('SnapTrade user exists but no brokerage accounts connected');
              
              // Clear the stored credentials since no brokerage is connected
              localStorage.removeItem('snaptrade_user_id');
              localStorage.removeItem('snaptrade_user_secret');
              localStorage.removeItem('snaptrade_connected');
              localStorage.removeItem('snaptrade_connected_at');
              
              // Show error message explaining what happened
              showConnectionError('No brokerage account was connected. Please try the connection process again and make sure to complete the brokerage linking in the SnapTrade portal.');
              return;
            } else {
              // Connection invalid, clear storage
              localStorage.removeItem('snaptrade_user_id');
              localStorage.removeItem('snaptrade_user_secret');
              localStorage.removeItem('snaptrade_connected');
              localStorage.removeItem('snaptrade_connected_at');
              showConnectionError('SnapTrade connection verification failed. Please reconnect.');
              return;
            }
          } catch (error) {
            console.error('SnapTrade verification failed:', error);
            showConnectionError('Failed to verify SnapTrade connection. Please try again.');
            return;
          }
        }
        
        // Check if we have a stored token from OAuth2 callback (legacy)
        const verifyStoredToken = localStorage.getItem('robinhood_access_token');
        const verifyIsConnected = localStorage.getItem('robinhood_connected') === 'true';
        
        if (verifyStoredToken && verifyIsConnected) {
          // Verify connection with API
          try {
            const response = await fetch(`http://localhost:8788/api/robinhood/accounts?access_token=${verifyStoredToken}`);
            const result = await response.json();
            
            if (result.success) {
              document.getElementById('accountInfo').innerHTML = `
                <div>Account Status: Connected (Live)</div>
                <div>Brokerage: Robinhood</div>
                <div>Accounts: ${result.accounts.length}</div>
                <div>Connection Time: ${localStorage.getItem('robinhood_connected_at')}</div>
                <div>Access Token: ${verifyStoredToken.substring(0, 20)}...</div>
              `;
              showConnectionStep(3);
              return;
            } else {
              // Token invalid, clear storage
              localStorage.removeItem('robinhood_access_token');
              localStorage.removeItem('robinhood_connected');
              localStorage.removeItem('robinhood_connected_at');
              showConnectionError('Token verification failed. Please reconnect.');
              return;
            }
          } catch (error) {
            console.error('Token verification failed:', error);
            showConnectionError('Failed to verify connection. Please try again.');
            return;
          }
        }
        
        // Fallback to chat-based check
        const response = await sendMessage('Check my brokerage connection status');
        if (response && response.ok) {
          const responseText = response.response;
          if (responseText.includes('connected') || responseText.includes('success')) {
            document.getElementById('accountInfo').innerHTML = `
              <div>Account Status: Connected</div>
              <div>Connection Time: ${new Date().toLocaleString()}</div>
            `;
            showConnectionStep(3);
          } else {
            showConnectionError('Account not yet connected. Please complete the connection process.');
          }
        } else {
          showConnectionError('Failed to check connection status');
        }
      } catch (error) {
        console.error('Error checking connection:', error);
        showConnectionError('Error checking connection status');
      }
    });
  }

  // Analyze Portfolio Button
  const analyzePortfolioBtn = document.getElementById('analyzePortfolio');
  if (analyzePortfolioBtn) {
    analyzePortfolioBtn.addEventListener('click', async function() {
      closeBrokerageModal();
      
      // Check if we have real Robinhood connection
      const analysisStoredToken = localStorage.getItem('robinhood_access_token');
      const analysisIsConnected = localStorage.getItem('robinhood_connected') === 'true';
      
      if (analysisStoredToken && analysisIsConnected) {
        // Store analysis request flag
        localStorage.setItem('robinhood_analyze_request', 'true');
        localStorage.setItem('robinhood_access_token_for_analysis', analysisStoredToken);
      }
      
      // Send message to analyze portfolio
      const input = document.getElementById('msg');
      input.value = 'Analyze my connected portfolio';
      input.dispatchEvent(new Event('keydown', { key: 'Enter' }));
    });
  }
});

// Close modal when clicking outside
document.addEventListener('click', function(event) {
  const modal = document.getElementById('brokerageModal');
  if (event.target === modal) {
    closeBrokerageModal();
  }
});

// Function to refresh connection status
async function refreshConnectionStatus() {
  console.log('Refreshing connection status...');
  const checkBtn = document.getElementById('checkConnection');
  if (checkBtn) {
    checkBtn.click();
  }
}

// Listen for SnapTrade callback messages
window.addEventListener('message', function(event) {
  if (event.data && event.data.type === 'snaptrade_callback') {
    console.log('SnapTrade callback received:', event.data);
    
    if (event.data.success) {
      // Connection successful - refresh the connection check
      console.log('SnapTrade connection successful, refreshing status...');
      setTimeout(refreshConnectionStatus, 1000);
    } else {
      console.error('SnapTrade connection failed:', event.data.data);
    }
  }
});

// Check if we're returning from a SnapTrade callback or have stored credentials
document.addEventListener('DOMContentLoaded', function() {
  // Check if we have SnapTrade credentials stored (user returning from callback)
  const snaptradeUserId = localStorage.getItem('snaptrade_user_id');
  const snaptradeUserSecret = localStorage.getItem('snaptrade_user_secret');
  const snaptradeConnected = localStorage.getItem('snaptrade_connected') === 'true';
  
  if (snaptradeUserId && snaptradeUserSecret && snaptradeConnected) {
    console.log('Detected stored SnapTrade credentials, checking connection status...');
    setTimeout(refreshConnectionStatus, 1000);
  }
  
  // Also check URL parameters for callback indicators
  if (window.location.search.includes('snaptrade_callback') || 
      window.location.hash.includes('snaptrade_callback') ||
      window.location.search.includes('userId') ||
      window.location.search.includes('userSecret')) {
    console.log('Detected SnapTrade callback return, refreshing status...');
    setTimeout(refreshConnectionStatus, 2000);
  }
});
