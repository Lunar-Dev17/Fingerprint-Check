"""HTML template for /test interactive client-side detection page."""

TEST_PAGE_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>fingerprint-check | Bot & Headless Fingerprint Audit</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
  <style>
    :root {
      --bg: #090d16;
      --card-bg: rgba(18, 26, 44, 0.7);
      --card-border: rgba(255, 255, 255, 0.08);
      --text: #e2e8f0;
      --text-muted: #94a3b8;
      --accent: #6366f1;
      --accent-glow: rgba(99, 102, 241, 0.25);
      --pass: #10b981;
      --pass-bg: rgba(16, 185, 129, 0.12);
      --pass-border: rgba(16, 185, 129, 0.3);
      --warn: #f59e0b;
      --warn-bg: rgba(245, 158, 11, 0.12);
      --warn-border: rgba(245, 158, 11, 0.3);
      --fail: #f43f5e;
      --fail-bg: rgba(244, 63, 94, 0.12);
      --fail-border: rgba(244, 63, 94, 0.3);
    }
    * {
      box-sizing: border-box;
      margin: 0;
      padding: 0;
    }
    body {
      background: var(--bg);
      background-image:
        radial-gradient(at 0% 0%, rgba(99, 102, 241, 0.15) 0px, transparent 50%),
        radial-gradient(at 100% 100%, rgba(244, 63, 94, 0.1) 0px, transparent 50%);
      color: var(--text);
      font-family: 'Outfit', sans-serif;
      min-height: 100vh;
      padding: 2.5rem 1.5rem;
    }
    .container {
      max-width: 960px;
      margin: 0 auto;
    }
    header {
      margin-bottom: 2rem;
      display: flex;
      justify-content: space-between;
      align-items: center;
      flex-wrap: wrap;
      gap: 1rem;
    }
    .logo-group {
      display: flex;
      align-items: center;
      gap: 0.75rem;
    }
    .logo-icon {
      width: 44px;
      height: 44px;
      border-radius: 12px;
      background: linear-gradient(135deg, #6366f1, #a855f7);
      display: flex;
      align-items: center;
      justify-content: center;
      font-weight: 700;
      font-size: 1.25rem;
      color: white;
      box-shadow: 0 4px 14px var(--accent-glow);
    }
    h1 {
      font-size: 1.75rem;
      font-weight: 700;
      letter-spacing: -0.02em;
    }
    .subtitle {
      color: var(--text-muted);
      font-size: 0.95rem;
      margin-top: 0.2rem;
    }
    .btn {
      background: #1e293b;
      color: var(--text);
      border: 1px solid var(--card-border);
      padding: 0.6rem 1.2rem;
      border-radius: 10px;
      font-family: inherit;
      font-size: 0.9rem;
      font-weight: 500;
      cursor: pointer;
      transition: all 0.2s ease;
      display: inline-flex;
      align-items: center;
      gap: 0.5rem;
    }
    .btn:hover {
      background: #334155;
      border-color: rgba(255, 255, 255, 0.2);
    }
    .btn-primary {
      background: linear-gradient(135deg, #6366f1, #4f46e5);
      border: none;
      color: white;
      box-shadow: 0 4px 14px var(--accent-glow);
    }
    .btn-primary:hover {
      background: linear-gradient(135deg, #4f46e5, #4338ca);
      transform: translateY(-1px);
    }
    #report-summary {
      background: var(--card-bg);
      backdrop-filter: blur(16px);
      border: 1px solid var(--card-border);
      border-radius: 16px;
      padding: 1.5rem;
      margin-bottom: 2rem;
      display: flex;
      flex-wrap: wrap;
      gap: 1.5rem;
      align-items: center;
      justify-content: space-between;
    }
    .stat-cards {
      display: flex;
      gap: 1rem;
      flex-wrap: wrap;
    }
    .stat-card {
      padding: 0.75rem 1.25rem;
      border-radius: 12px;
      min-width: 100px;
      text-align: center;
    }
    .stat-card .count {
      font-size: 1.75rem;
      font-weight: 700;
      line-height: 1.2;
    }
    .stat-card .label {
      font-size: 0.75rem;
      text-transform: uppercase;
      letter-spacing: 0.05em;
      margin-top: 0.2rem;
    }
    .stat-total { background: rgba(255, 255, 255, 0.04); }
    .stat-pass { background: var(--pass-bg); border: 1px solid var(--pass-border); color: var(--pass); }
    .stat-warn { background: var(--warn-bg); border: 1px solid var(--warn-border); color: var(--warn); }
    .stat-fail { background: var(--fail-bg); border: 1px solid var(--fail-border); color: var(--fail); }

    .loading-state {
      padding: 3rem;
      text-align: center;
      color: var(--text-muted);
    }
    .spinner {
      width: 40px;
      height: 40px;
      border: 3px solid rgba(255, 255, 255, 0.1);
      border-top-color: var(--accent);
      border-radius: 50%;
      animation: spin 0.8s linear infinite;
      margin: 0 auto 1rem;
    }
    @keyframes spin {
      to { transform: rotate(360deg); }
    }
    .checks-list {
      display: flex;
      flex-direction: column;
      gap: 1rem;
    }
    .check-card {
      background: var(--card-bg);
      backdrop-filter: blur(12px);
      border: 1px solid var(--card-border);
      border-radius: 14px;
      padding: 1.25rem 1.5rem;
      transition: border-color 0.2s ease, transform 0.2s ease;
    }
    .check-card:hover {
      border-color: rgba(255, 255, 255, 0.15);
      transform: translateY(-1px);
    }
    .check-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 0.6rem;
    }
    .check-title {
      font-size: 1.05rem;
      font-weight: 600;
      display: flex;
      align-items: center;
      gap: 0.5rem;
    }
    .status-badge {
      padding: 0.3rem 0.75rem;
      border-radius: 9999px;
      font-size: 0.75rem;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 0.06em;
    }
    .badge-pass { background: var(--pass-bg); color: var(--pass); border: 1px solid var(--pass-border); }
    .badge-warn { background: var(--warn-bg); color: var(--warn); border: 1px solid var(--warn-border); }
    .badge-fail { background: var(--fail-bg); color: var(--fail); border: 1px solid var(--fail-border); }
    .check-explanation {
      color: var(--text-muted);
      font-size: 0.9rem;
      line-height: 1.5;
      margin-bottom: 0.75rem;
    }
    .check-fix {
      background: rgba(0, 0, 0, 0.3);
      border-left: 3px solid var(--accent);
      padding: 0.6rem 0.9rem;
      border-radius: 0 8px 8px 0;
      font-size: 0.85rem;
      font-family: 'JetBrains Mono', monospace;
      color: #cbd5e1;
    }
    .check-fix span {
      color: var(--text-muted);
      display: block;
      font-family: 'Outfit', sans-serif;
      font-size: 0.75rem;
      text-transform: uppercase;
      margin-bottom: 0.2rem;
      letter-spacing: 0.05em;
    }
    footer {
      margin-top: 3rem;
      text-align: center;
      color: var(--text-muted);
      font-size: 0.85rem;
    }
  </style>
</head>
<body>
  <div class="container">
    <header>
      <div class="logo-group">
        <div class="logo-icon">FC</div>
        <div>
          <h1>fingerprint-check</h1>
          <p class="subtitle">Client-Side & Server-Side Headless Bot Fingerprint Audit</p>
        </div>
      </div>
      <div>
        <button id="btn-rerun" class="btn btn-primary" onclick="runAudit()">Rerun Audit</button>
      </div>
    </header>

    <div id="report-summary" style="display: none;">
      <div>
        <h2 style="font-size: 1.15rem; font-weight: 600;">Overall Analysis</h2>
        <p id="summary-headline" style="color: var(--text-muted); font-size: 0.9rem; margin-top: 0.25rem;"></p>
      </div>
      <div class="stat-cards">
        <div class="stat-card stat-total">
          <div id="total-count" class="count">0</div>
          <div class="label">Total</div>
        </div>
        <div class="stat-card stat-pass">
          <div id="passed-count" class="count">0</div>
          <div class="label">Pass</div>
        </div>
        <div class="stat-card stat-warn">
          <div id="warned-count" class="count">0</div>
          <div class="label">Warn</div>
        </div>
        <div class="stat-card stat-fail">
          <div id="failed-count" class="count">0</div>
          <div class="label">Fail</div>
        </div>
      </div>
    </div>

    <div id="loading-spinner" class="loading-state">
      <div class="spinner"></div>
      <p>Collecting browser runtime metrics and analyzing request fingerprint...</p>
    </div>

    <div id="checks-container" class="checks-list"></div>

    <pre id="report-json" style="display: none;" aria-hidden="true"></pre>

    <footer>
      fingerprint-check • Self-hosted scraper bot detection analysis tool
    </footer>
  </div>

  <script>
    async function collectClientMetrics() {
      const plugins = navigator.plugins ? Array.from(navigator.plugins).map(p => p.name) : [];
      const languages = navigator.languages ? Array.from(navigator.languages) : [];
      const tz = (typeof Intl !== 'undefined' && Intl.DateTimeFormat)
        ? (Intl.DateTimeFormat().resolvedOptions().timeZone || '')
        : '';
      const tzOffset = new Date().getTimezoneOffset();
      const hasChrome = typeof window.chrome !== 'undefined' && window.chrome !== null;
      const hasRuntime = hasChrome && typeof window.chrome.runtime !== 'undefined';

      return {
        webdriver: navigator.webdriver === true,
        webdriver_raw: navigator.webdriver,
        plugins_count: plugins.length,
        plugins_names: plugins,
        languages: languages,
        language: navigator.language || '',
        timezone: tz,
        timezone_offset: tzOffset,
        has_window_chrome: hasChrome,
        has_chrome_runtime: hasRuntime,
        screen_width: window.screen ? window.screen.width : 0,
        screen_height: window.screen ? window.screen.height : 0,
        screen_avail_width: window.screen ? window.screen.availWidth : 0,
        screen_avail_height: window.screen ? window.screen.availHeight : 0,
        screen_color_depth: window.screen ? window.screen.colorDepth : 0,
        outer_width: window.outerWidth,
        outer_height: window.outerHeight,
        inner_width: window.innerWidth,
        inner_height: window.innerHeight,
        js_user_agent: navigator.userAgent || ''
      };
    }

    async function runAudit() {
      const spinner = document.getElementById('loading-spinner');
      const summary = document.getElementById('report-summary');
      const container = document.getElementById('checks-container');

      spinner.style.display = 'block';
      summary.style.display = 'none';
      container.innerHTML = '';

      try {
        const payload = await collectClientMetrics();
        const response = await fetch('/report', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload)
        });

        if (!response.ok) {
          throw new Error('Failed to generate report: ' + response.statusText);
        }

        const data = await response.json();
        window.__report__ = data;

        // Populate raw JSON pre for automated test access
        const jsonEl = document.getElementById('report-json');
        if (jsonEl) {
          jsonEl.textContent = JSON.stringify(data, null, 2);
        }

        renderReport(data);
      } catch (err) {
        spinner.style.display = 'none';
        container.innerHTML = '<div class="check-card" style="border-color: var(--fail-border);"><h3 style="color: var(--fail);">Audit Error</h3><p>' + err.message + '</p></div>';
      }
    }

    function renderReport(data) {
      const spinner = document.getElementById('loading-spinner');
      const summary = document.getElementById('report-summary');
      const container = document.getElementById('checks-container');

      spinner.style.display = 'none';
      summary.style.display = 'flex';

      document.getElementById('total-count').textContent = data.summary.total;
      document.getElementById('passed-count').textContent = data.summary.passed;
      document.getElementById('warned-count').textContent = data.summary.warned;
      document.getElementById('failed-count').textContent = data.summary.failed;

      const headline = document.getElementById('summary-headline');
      if (data.summary.failed > 0) {
        headline.textContent = 'High Bot Confidence: ' + data.summary.failed + ' critical bot signature(s) detected.';
        headline.style.color = 'var(--fail)';
      } else if (data.summary.warned > 0) {
        headline.textContent = 'Moderate Suspicion: ' + data.summary.warned + ' potential anomaly warning(s).';
        headline.style.color = 'var(--warn)';
      } else {
        headline.textContent = 'Authentic Session: All checks passed browser-grade standards.';
        headline.style.color = 'var(--pass)';
      }

      container.innerHTML = '';
      data.checks.forEach((chk, idx) => {
        const card = document.createElement('div');
        card.className = 'check-card';
        card.id = 'check-card-' + idx;
        card.setAttribute('data-status', chk.status);
        card.setAttribute('data-name', chk.name);

        const badgeClass = chk.status === 'pass' ? 'badge-pass' : (chk.status === 'warn' ? 'badge-warn' : 'badge-fail');

        card.innerHTML = `
          <div class="check-header">
            <div class="check-title">${escapeHtml(chk.name)}</div>
            <span class="status-badge ${badgeClass}" id="badge-${idx}">${chk.status.toUpperCase()}</span>
          </div>
          <p class="check-explanation">${escapeHtml(chk.explanation)}</p>
          <div class="check-fix">
            <span>Remediation Suggestion:</span>
            ${escapeHtml(chk.fix || chk.fix_suggestion)}
          </div>
        `;
        container.appendChild(card);
      });
    }

    function escapeHtml(str) {
      if (!str) return '';
      return String(str)
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;');
    }

    // Auto-run on load
    window.addEventListener('DOMContentLoaded', runAudit);
  </script>
</body>
</html>
"""
