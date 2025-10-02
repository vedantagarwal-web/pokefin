// Placeholder agents to simulate async behavior. Swap with real services later.

export async function profileAgent({ text }) {
  await delay(500 + Math.random() * 600);
  // naive extraction for demo only
  const risk = /(cautious|conservative|balanced|moderate|bold|aggressive)/i.exec(text)?.[1] || 'balanced';
  const income = /\$([\d,.]+)/.exec(text)?.[1];
  const horizon = /(\d+)\s*(years?|months?|mos?)/i.exec(text)?.[0];
  const parts = [];
  parts.push(`Risk comfort reads ${risk.toLowerCase()}.`);
  if (income) parts.push(`Income noted around $${income}.`);
  if (horizon) parts.push(`Time horizon ~${horizon}.`);
  return { summary: parts.join(' ') || 'Profile noted.' };
}

export async function strategyAgent({ text }) {
  await delay(650 + Math.random() * 650);
  const reply = [
    'Here’s a simple, steady approach (not advice):',
    '• Keep 3–6 months of expenses in a high-yield savings for buffer.',
    '• Automate monthly investing into low-cost, broad-market index ETFs.',
    '• Adjust stock/bond mix to your risk comfort (more bonds if cautious).',
    '• Rebalance 1–2x per year; ignore daily noise.',
  ].join('\n');
  return { reply };
}

export async function researchAgent({ text }) {
  await delay(600 + Math.random() * 700);
  const reply = [
    'Quick research stub:',
    '• Macro: Inflation cooling vs. employment steady — mixed signals.',
    '• Equities: Mega-cap earnings drive near-term swings.',
    '• Bonds: Yields eased from highs; duration risk still matters.',
    '• Action: Stay diversified; avoid reacting to single headlines.',
  ].join('\n');
  return { reply };
}

function delay(ms) { return new Promise(r => setTimeout(r, ms)); }

