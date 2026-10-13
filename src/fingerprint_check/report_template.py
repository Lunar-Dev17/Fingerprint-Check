"""Single, dependency-free minimal HTML template for /report endpoint."""

import html

from fingerprint_check.models import ReportResponse


def render_report_html(report: ReportResponse) -> str:
    """Render a standalone, dependency-free dark-theme HTML report page."""
    total = report.summary.total
    passed = report.summary.passed
    warned = report.summary.warned
    failed = report.summary.failed

    score = round(((passed * 100 + warned * 50) / total)) if total > 0 else 100

    if failed > 0:
        score_status = "High Bot Risk"
        score_color = "#f43f5e"
        score_bg = "rgba(244, 63, 94, 0.12)"
    elif warned > 0:
        score_status = "Moderate Suspicion"
        score_color = "#f59e0b"
        score_bg = "rgba(245, 158, 11, 0.12)"
    else:
        score_status = "Authentic Browser"
        score_color = "#10b981"
        score_bg = "rgba(16, 185, 129, 0.12)"

    rows_html = []
    for idx, chk in enumerate(report.checks):
        status = chk.status.lower()
        if status == "pass":
            badge_class = "badge-pass"
            badge_text = "PASS"
        elif status == "warn":
            badge_class = "badge-warn"
            badge_text = "WARN"
        else:
            badge_class = "badge-fail"
            badge_text = "FAIL"

        name_esc = html.escape(chk.name)
        exp_esc = html.escape(chk.explanation)
        fix_esc = html.escape(chk.fix or chk.fix_suggestion)

        # Expand failed or warned checks by default for immediate developer visibility
        open_attr = " open" if status in ("fail", "warn") else ""

        row = f"""
      <details class="check-item {badge_class}"{open_attr} id="check-{idx}">
        <summary class="check-summary">
          <div class="summary-left">
            <span class="chevron" aria-hidden="true">▸</span>
            <span class="check-name">{name_esc}</span>
          </div>
          <span class="status-badge {badge_class}">{badge_text}</span>
        </summary>
        <div class="check-details">
          <div class="detail-section">
            <div class="detail-label">Why it matters</div>
            <p class="detail-text">{exp_esc}</p>
          </div>
          <div class="detail-section">
            <div class="detail-label">Remediation Suggestion</div>
            <code class="fix-code">{fix_esc}</code>
          </div>
        </div>
      </details>"""
        rows_html.append(row)

    rows_rendered = "\n".join(rows_html)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>fingerprint-check | Audit Report</title>
  <style>
    :root {{
      --bg: #0d1117;
      --card-bg: #161b22;
      --border: #30363d;
      --text: #e6edf3;
      --text-muted: #8b949e;
      --pass: #10b981;
      --pass-bg: rgba(16, 185, 129, 0.12);
      --warn: #f59e0b;
      --warn-bg: rgba(245, 158, 11, 0.12);
      --fail: #f43f5e;
      --fail-bg: rgba(244, 63, 94, 0.12);
    }}
    * {{
      box-sizing: border-box;
      margin: 0;
      padding: 0;
    }}
    body {{
      background: var(--bg);
      color: var(--text);
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
      line-height: 1.5;
      padding: 2.5rem 1rem;
    }}
    .container {{
      max-width: 860px;
      margin: 0 auto;
    }}
    header {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 2rem;
      border-bottom: 1px solid var(--border);
      padding-bottom: 1.25rem;
    }}
    .brand {{
      font-size: 1.25rem;
      font-weight: 700;
      letter-spacing: -0.01em;
      display: flex;
      align-items: center;
      gap: 0.5rem;
    }}
    .brand-tag {{
      font-size: 0.75rem;
      font-weight: 500;
      color: var(--text-muted);
      background: rgba(255, 255, 255, 0.05);
      padding: 0.2rem 0.5rem;
      border-radius: 6px;
    }}
    .raw-link {{
      color: var(--text-muted);
      text-decoration: none;
      font-size: 0.85rem;
      border: 1px solid var(--border);
      padding: 0.35rem 0.75rem;
      border-radius: 6px;
      transition: all 0.15s ease;
    }}
    .raw-link:hover {{
      color: var(--text);
      background: var(--card-bg);
    }}
    .score-card {{
      background: var(--card-bg);
      border: 1px solid var(--border);
      border-radius: 12px;
      padding: 1.5rem;
      margin-bottom: 1.75rem;
      display: flex;
      flex-wrap: wrap;
      justify-content: space-between;
      align-items: center;
      gap: 1.25rem;
    }}
    .score-left {{
      display: flex;
      align-items: center;
      gap: 1.25rem;
    }}
    .score-circle {{
      width: 72px;
      height: 72px;
      border-radius: 50%;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      background: {score_bg};
      border: 2px solid {score_color};
      color: {score_color};
    }}
    .score-val {{
      font-size: 1.5rem;
      font-weight: 700;
      line-height: 1;
    }}
    .score-denom {{
      font-size: 0.65rem;
      opacity: 0.8;
      text-transform: uppercase;
    }}
    .score-meta h2 {{
      font-size: 1.15rem;
      font-weight: 600;
      color: {score_color};
    }}
    .score-meta p {{
      color: var(--text-muted);
      font-size: 0.85rem;
    }}
    .stats-pills {{
      display: flex;
      gap: 0.5rem;
      flex-wrap: wrap;
    }}
    .pill {{
      padding: 0.35rem 0.75rem;
      border-radius: 8px;
      font-size: 0.85rem;
      font-weight: 600;
      background: rgba(255, 255, 255, 0.04);
      border: 1px solid var(--border);
    }}
    .pill-pass {{ color: var(--pass); border-color: rgba(16, 185, 129, 0.3); background: var(--pass-bg); }}
    .pill-warn {{ color: var(--warn); border-color: rgba(245, 158, 11, 0.3); background: var(--warn-bg); }}
    .pill-fail {{ color: var(--fail); border-color: rgba(244, 63, 94, 0.3); background: var(--fail-bg); }}

    .checks-list {{
      display: flex;
      flex-direction: column;
      gap: 0.6rem;
    }}
    .check-item {{
      background: var(--card-bg);
      border: 1px solid var(--border);
      border-radius: 10px;
      overflow: hidden;
      transition: border-color 0.15s ease;
    }}
    .check-item[open] {{
      border-color: rgba(255, 255, 255, 0.2);
    }}
    .check-summary {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 0.9rem 1.1rem;
      cursor: pointer;
      list-style: none;
      user-select: none;
    }}
    .check-summary::-webkit-details-marker {{
      display: none;
    }}
    .summary-left {{
      display: flex;
      align-items: center;
      gap: 0.65rem;
    }}
    .chevron {{
      font-size: 0.75rem;
      color: var(--text-muted);
      transition: transform 0.2s ease;
      display: inline-block;
    }}
    .check-item[open] .chevron {{
      transform: rotate(90deg);
    }}
    .check-name {{
      font-weight: 500;
      font-size: 0.95rem;
    }}
    .status-badge {{
      font-size: 0.7rem;
      font-weight: 700;
      letter-spacing: 0.04em;
      padding: 0.25rem 0.55rem;
      border-radius: 6px;
      text-transform: uppercase;
    }}
    .badge-pass {{ color: var(--pass); background: var(--pass-bg); }}
    .badge-warn {{ color: var(--warn); background: var(--warn-bg); }}
    .badge-fail {{ color: var(--fail); background: var(--fail-bg); }}

    .check-details {{
      padding: 0.9rem 1.1rem 1.1rem 2.5rem;
      border-top: 1px solid rgba(255, 255, 255, 0.05);
      background: rgba(0, 0, 0, 0.15);
      display: flex;
      flex-direction: column;
      gap: 0.75rem;
    }}
    .detail-label {{
      font-size: 0.72rem;
      font-weight: 600;
      text-transform: uppercase;
      letter-spacing: 0.05em;
      color: var(--text-muted);
      margin-bottom: 0.2rem;
    }}
    .detail-text {{
      font-size: 0.88rem;
      color: var(--text);
      line-height: 1.45;
    }}
    .fix-code {{
      display: block;
      background: #090d16;
      border: 1px solid var(--border);
      border-radius: 6px;
      padding: 0.55rem 0.8rem;
      font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
      font-size: 0.82rem;
      color: #93c5fd;
      white-space: pre-wrap;
      word-break: break-word;
    }}
    footer {{
      margin-top: 2.5rem;
      text-align: center;
      color: var(--text-muted);
      font-size: 0.8rem;
    }}
  </style>
</head>
<body>
  <div class="container">
    <header>
      <div class="brand">
        fingerprint-check
        <span class="brand-tag">report</span>
      </div>
      <div>
        <a href="/report?format=json" class="raw-link" id="link-raw-json">View JSON</a>
      </div>
    </header>

    <div class="score-card" id="score-card">
      <div class="score-left">
        <div class="score-circle">
          <span class="score-val" id="score-val">{score}</span>
          <span class="score-denom">/ 100</span>
        </div>
        <div class="score-meta">
          <h2 id="score-status">{score_status}</h2>
          <p>{total} total detection heuristics evaluated</p>
        </div>
      </div>
      <div class="stats-pills">
        <span class="pill pill-pass" id="pill-pass">{passed} PASS</span>
        <span class="pill pill-warn" id="pill-warn">{warned} WARN</span>
        <span class="pill pill-fail" id="pill-fail">{failed} FAIL</span>
      </div>
    </div>

    <div class="checks-list" id="checks-list">
{rows_rendered}
    </div>

    <footer>
      fingerprint-check • Self-hosted bot detection auditor
    </footer>
  </div>
</body>
</html>
"""
