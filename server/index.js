// Minimal Poke-like backend: static file server + chat endpoints
// No external deps; Node 18+ recommended (built-in fetch)

const http = require('http');
const fs = require('fs');
const path = require('path');
const { URL } = require('url');

const PORT = process.env.PORT ? Number(process.env.PORT) : 8787;
const API_KEY = process.env.OPENAI_API_KEY || '';
const DEFAULT_MODEL = process.env.OPENAI_MODEL || 'gpt-4o-mini';
const DEFAULT_TEMPERATURE = Number.isFinite(Number(process.env.OPENAI_TEMPERATURE))
  ? Number(process.env.OPENAI_TEMPERATURE)
  : 0.7;

// Python backend URL
const PYTHON_BACKEND_URL = process.env.PYTHON_BACKEND_URL || 'http://localhost:8788';

// In-memory conversation logs by session
// Map<string, Array<{ role: 'user'|'assistant'|'system', content: string, timestamp?: string }>>
const sessions = new Map();

const systemPrompt = `# Financial Advisor System Prompt

You are Sydney, a financial advisor AI with attitude. You're knowledgeable but never boring, direct but never cruel. Your goal is to help users make better financial decisions while keeping them engaged.

## Core Personality Traits
- Confident but not arrogant
- Straight-talking but not rude
- Witty but never at the user's expense
- Slightly irreverent about financial institutions
- Protective of the user's financial wellbeing

## Voice and Style
- Use concise sentences with occasional longer explanations
- Prefer active voice and direct statements
- Use financial jargon sparingly, and always explain it
- Occasionally use mild slang, but never when discussing serious financial matters
- Use emojis only for emphasis, not decoration (max 1 per message)
- Never use corporate buzzwords or financial platitudes

## Interaction Patterns
- Start responses with direct answers, then add context
- When users are making poor financial choices, be blunt but constructive
- When users are on the right track, be encouraging but not overly enthusiastic
- Always acknowledge user emotions about money (stress, excitement, confusion)
- Use analogies to explain complex financial concepts
- Never lecture or talk down to users

## Financial Advice Guidelines
- Always clarify you're not a licensed financial advisor
- Provide balanced perspectives on financial decisions
- Highlight both risks and potential rewards
- Never make specific stock picks or timing recommendations
- Always consider the user's stated financial goals and risk tolerance
- Emphasize long-term thinking over get-rich-quick schemes

## Response Structure
1. Direct answer to the question (1-2 sentences)
2. Brief explanation or context (2-3 sentences)
3. Actionable advice or next steps when appropriate
4. Question to engage further only when relevant

## Example Responses

### When asked about investing with little money:
"$50 a month is plenty to start investing. The key isn't how much you start with, but how consistent you are.

I'd recommend a low-cost index fund through someone like Vanguard or Fidelity - they won't charge you ridiculous fees for the privilege of holding your money. Set up automatic transfers and forget about it for a few years.

What's your biggest concern about getting started?"

### When asked about paying off debt vs. investing:
"Pay off that credit card debt first. At 22% interest, it's basically a financial emergency.

That high-interest debt is costing you way more than you'd make in the market. Think of it this way: paying it off is a guaranteed 22% return on your money. Even Warren Buffett can't promise that kind of performance.

How much can you realistically put toward that debt each month?"`;

function nowISO() { return new Date().toISOString(); }

function sendJSON(res, status, data) {
  const body = JSON.stringify(data);
  res.writeHead(status, {
    'Content-Type': 'application/json; charset=utf-8',
    'Content-Length': Buffer.byteLength(body),
    'Cache-Control': 'no-store',
  });
  res.end(body);
}

function notFound(res) {
  res.writeHead(404, { 'Content-Type': 'text/plain; charset=utf-8' });
  res.end('Not found');
}

function serveStatic(req, res, filePath) {
  const ext = path.extname(filePath).toLowerCase();
  const type =
    ext === '.html' ? 'text/html' :
    ext === '.css' ? 'text/css' :
    ext === '.js' ? 'application/javascript' :
    ext === '.svg' ? 'image/svg+xml' :
    ext === '.json' ? 'application/json' : 'text/plain';

  fs.readFile(filePath, (err, data) => {
    if (err) return notFound(res);
    res.writeHead(200, { 'Content-Type': `${type}; charset=utf-8`, 'Cache-Control': 'no-store' });
    res.end(data);
  });
}

function getMessages(sessionId) {
  if (!sessions.has(sessionId)) sessions.set(sessionId, []);
  return sessions.get(sessionId);
}

function clampTemp(t) {
  const x = Number(t);
  if (!Number.isFinite(x)) return DEFAULT_TEMPERATURE;
  if (x < 0) return 0;
  if (x > 2) return 2;
  return x;
}

async function handleChatSend(req, res, urlObj) {
  try {
    const chunks = [];
    for await (const chunk of req) chunks.push(chunk);
    const raw = Buffer.concat(chunks).toString('utf8') || '{}';
    let payload = {};
    try { payload = JSON.parse(raw); } catch { payload = {}; }

    const list = Array.isArray(payload.messages) ? payload.messages : [];
    const latest = [...list].reverse().find(m => m && typeof m.content === 'string' && (m.role || '').toLowerCase() === 'user');
    if (!latest || !latest.content.trim()) {
      return sendJSON(res, 400, { ok: false, error: 'Missing user message' });
    }

    const sessionId =
      (typeof payload.session === 'string' && payload.session.trim()) ||
      urlObj.searchParams.get('session') ||
      'default';

    const model = (typeof payload.model === 'string' && payload.model.trim()) || DEFAULT_MODEL;
    const temperature = clampTemp(payload.temperature ?? DEFAULT_TEMPERATURE);

    // Append user message to server log
    const thread = getMessages(sessionId);
    thread.push({ role: 'user', content: latest.content.trim(), timestamp: nowISO() });

    // Fire-and-forget assistant generation
    generateAssistant({ sessionId, userText: latest.content.trim(), model, temperature })
      .catch(err => console.error('[chat] generation failed:', err?.message || err));

    res.writeHead(202, { 'Content-Type': 'text/plain; charset=utf-8', 'Cache-Control': 'no-store' });
    res.end('');
  } catch (e) {
    console.error('[chat] send error', e);
    return sendJSON(res, 500, { ok: false, error: 'Internal error' });
  }
}

async function generateAssistant({ sessionId, userText, model, temperature }) {
  const thread = getMessages(sessionId);
  const history = [{ role: 'system', content: systemPrompt }, ...thread.map(m => ({ role: m.role, content: m.content }))];

  const body = {
    model,
    messages: history,
    temperature,
  };

  if (!API_KEY) {
    // No key — simulate a fast response for local testing
    const stub = 'I’m offline right now, but here’s the flow: tell me your risk vibe (cautious, balanced, or bold) and what you want to accomplish first.';
    thread.push({ role: 'assistant', content: stub, timestamp: nowISO() });
    return;
  }

  const resp = await fetch('https://api.openai.com/v1/chat/completions', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${API_KEY}`,
    },
    body: JSON.stringify(body),
  });

  if (!resp.ok) {
    const detail = await resp.text().catch(() => '');
    const msg = `OpenAI error ${resp.status}: ${detail || resp.statusText}`;
    console.error(msg);
    thread.push({ role: 'assistant', content: 'I hit a snag reaching my brain — try again in a moment.', timestamp: nowISO() });
    return;
  }

  const data = await resp.json();
  const content = data?.choices?.[0]?.message?.content || 'Okay.';
  thread.push({ role: 'assistant', content, timestamp: nowISO() });
}

function handleHistoryGet(_req, res, urlObj) {
  const sessionId = urlObj.searchParams.get('session') || 'default';
  const thread = getMessages(sessionId);
  sendJSON(res, 200, { messages: thread });
}

function handleHistoryDelete(_req, res, urlObj) {
  const sessionId = urlObj.searchParams.get('session') || 'default';
  sessions.set(sessionId, []);
  sendJSON(res, 200, { ok: true });
}

async function proxyToPython(req, res) {
  // Proxy request to Python backend
  try {
    const u = new URL(req.url, `http://${req.headers.host}`);
    const pythonUrl = `${PYTHON_BACKEND_URL}${u.pathname}${u.search}`;
    
    // Collect request body if POST/PUT
    let body = '';
    if (req.method === 'POST' || req.method === 'PUT') {
      const chunks = [];
      for await (const chunk of req) chunks.push(chunk);
      body = Buffer.concat(chunks).toString('utf8');
    }
    
    // Forward request
    const response = await fetch(pythonUrl, {
      method: req.method,
      headers: {
        'Content-Type': 'application/json',
      },
      body: body || undefined
    });
    
    // Forward response
    const data = await response.text();
    res.writeHead(response.status, {
      'Content-Type': response.headers.get('content-type') || 'application/json',
      'Cache-Control': 'no-store'
    });
    res.end(data);
  } catch (err) {
    console.error('[proxy] Error:', err.message);
    sendJSON(res, 503, { 
      ok: false, 
      error: 'Python backend unavailable',
      message: 'Make sure the Python backend is running on port 8788'
    });
  }
}

const server = http.createServer(async (req, res) => {
  try {
    const u = new URL(req.url, `http://${req.headers.host}`);
    const pathname = u.pathname;

    // Proxy /api/v2 requests to Python backend
    if (pathname.startsWith('/api/v2/')) {
      return proxyToPython(req, res);
    }

    // Legacy API routes (v1)
    if (pathname === '/api/v1/chat/send' && req.method === 'POST') return handleChatSend(req, res, u);
    if (pathname === '/api/v1/chat/history' && req.method === 'GET') return handleHistoryGet(req, res, u);
    if (pathname === '/api/v1/chat/history' && req.method === 'DELETE') return handleHistoryDelete(req, res, u);

    // Handle SnapTrade callback
    if (pathname.startsWith('/callback')) {
      console.log('[server] SnapTrade callback received:', req.url);
      
      try {
        // Parse query parameters
        const queryParams = Object.fromEntries(u.searchParams);
        console.log('[server] Callback query params:', queryParams);
        
        // Forward to Python backend
        const response = await fetch(`${PYTHON_BACKEND_URL}/api/snaptrade/callback?${u.search.substring(1)}`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' }
        });
        
        const result = await response.json();
        console.log('[server] Python backend response:', result);
        
        // Return callback.html with the result
        const callbackHtml = `
          <!DOCTYPE html>
          <html>
          <head>
            <title>SnapTrade Connection</title>
            <style>
              body { font-family: Arial, sans-serif; padding: 20px; background: #1a1a1a; color: #fff; }
              .container { max-width: 500px; margin: 0 auto; text-align: center; }
              .success { color: #00d4aa; }
              .error { color: #e74c3c; }
            </style>
          </head>
          <body>
            <div class="container">
              <h1>SnapTrade Connection</h1>
              ${result.success ? 
                '<div class="success"><h2>✅ Connection Successful!</h2><p>Your Robinhood account has been connected via SnapTrade.</p></div>' :
                '<div class="error"><h2>❌ Connection Failed</h2><p>Error: ' + (result.error || 'Unknown error') + '</p></div>'
              }
              <p><a href="/chat.html" style="color: #00d4aa;">Return to App</a></p>
              <p><em>You will be redirected automatically in 3 seconds...</em></p>
              <script>
                // Store connection details if successful
                if (${result.success}) {
                  // Get user credentials from URL parameters or backend response
                  const urlParams = new URLSearchParams(window.location.search);
                  const userId = urlParams.get('userId') || ${JSON.stringify(result.user_id)} || 'connected_user';
                  const userSecret = urlParams.get('userSecret') || ${JSON.stringify(result.user_secret)} || 'connected_secret';
                  
                  // Store in localStorage for persistent connection
                  localStorage.setItem('snaptrade_user_id', userId);
                  localStorage.setItem('snaptrade_user_secret', userSecret);
                  localStorage.setItem('snaptrade_connected', 'true');
                  localStorage.setItem('snaptrade_connected_at', new Date().toISOString());
                  
                  console.log('SnapTrade connection stored:', { userId, userSecret });
                  console.log('URL params:', Object.fromEntries(urlParams));
                  
                  // Auto-redirect to chat page after storing credentials
                  setTimeout(() => {
                    window.location.href = '/chat.html';
                  }, 3000);
                } else {
                  // Even if connection failed, redirect back to chat
                  setTimeout(() => {
                    window.location.href = '/chat.html';
                  }, 3000);
                }
                
                // Notify parent window if in popup
                if (window.opener) {
                  window.opener.postMessage({
                    type: 'snaptrade_callback',
                    success: ${result.success},
                    data: ${JSON.stringify(result)}
                  }, '*');
                  window.close();
                }
              </script>
            </div>
          </body>
          </html>
        `;
        
        res.writeHead(200, { 'Content-Type': 'text/html' });
        res.end(callbackHtml);
        return;
      } catch (error) {
        console.error('[server] Callback error:', error);
        res.writeHead(500, { 'Content-Type': 'text/html' });
        res.end(`
          <html>
          <body style="font-family: Arial, sans-serif; padding: 20px; background: #1a1a1a; color: #fff; text-align: center;">
            <h1>Connection Error</h1>
            <p>There was an error processing the SnapTrade callback.</p>
            <p><a href="/chat.html" style="color: #00d4aa;">Return to App</a></p>
          </body>
          </html>
        `);
        return;
      }
    }

    // Static assets (serve from project root)
    const root = path.resolve(__dirname, '..');
    let filePath = path.join(root, pathname === '/' ? 'index.html' : pathname.replace(/^\/+/, ''));

    // Prevent directory traversal
    if (!filePath.startsWith(root)) return notFound(res);

    // If directory, append index.html
    if (fs.existsSync(filePath) && fs.statSync(filePath).isDirectory()) {
      filePath = path.join(filePath, 'index.html');
    }
    // If not found, try adding .html for route-like paths
    if (!fs.existsSync(filePath) && !path.extname(filePath)) {
      const tryHtml = `${filePath}.html`;
      if (fs.existsSync(tryHtml)) filePath = tryHtml;
    }

    if (!fs.existsSync(filePath)) return notFound(res);
    return serveStatic(req, res, filePath);
  } catch (e) {
    console.error('[server] error', e);
    res.writeHead(500, { 'Content-Type': 'text/plain; charset=utf-8' });
    res.end('Server error');
  }
});


server.listen(PORT, () => {
  console.log(`[pokefin] listening on http://localhost:${PORT}`);
});
