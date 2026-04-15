from __future__ import annotations

import html
import json
from urllib.parse import parse_qs


FIELDS = [
    ("company", "Company Name"),
    ("ticker", "Ticker"),
    ("market_cap", "Market Cap"),
    ("enterprise_value", "Enterprise Value"),
    ("share_price", "Share Price"),
    ("eps", "EPS"),
    ("revenue", "Revenue"),
    ("net_income", "Net Income"),
    ("free_cash_flow", "Free Cash Flow"),
    ("total_debt", "Total Debt"),
    ("cash_and_equivalents", "Cash And Equivalents"),
    ("shareholders_equity", "Shareholders Equity"),
    ("ebit", "EBIT"),
    ("interest_expense", "Interest Expense"),
    ("revenue_growth_3y", "Revenue Growth 3Y"),
    ("fcf_growth_3y", "FCF Growth 3Y"),
    ("gross_margin", "Gross Margin"),
    ("operating_margin", "Operating Margin"),
    ("industry_pe", "Industry P/E"),
    ("industry_ev_ebit", "Industry EV/EBIT"),
]

DEFAULTS = {
    "company": "Apple-Like Example",
    "ticker": "ALEX",
    "market_cap": "2800000000000",
    "enterprise_value": "2850000000000",
    "share_price": "185.0",
    "eps": "6.4",
    "revenue": "395000000000",
    "net_income": "100000000000",
    "free_cash_flow": "99500000000",
    "total_debt": "110000000000",
    "cash_and_equivalents": "62000000000",
    "shareholders_equity": "72000000000",
    "ebit": "123000000000",
    "interest_expense": "3900000000",
    "revenue_growth_3y": "0.09",
    "fcf_growth_3y": "0.11",
    "gross_margin": "0.45",
    "operating_margin": "0.30",
    "industry_pe": "31.0",
    "industry_ev_ebit": "24.0",
}


def safe_divide(numerator, denominator):
    if denominator == 0:
        return None
    return numerator / denominator


def format_ratio(value, suffix=""):
    if value is None:
        return "N/A"
    return f"{value:.2f}{suffix}"


def format_percent(value):
    if value is None:
        return "N/A"
    return f"{value * 100:.2f}%"


def parse_input(values):
    data = {}

    for field_name, _ in FIELDS:
        raw_value = values.get(field_name, "").strip()

        if field_name in {"company", "ticker"}:
            if not raw_value:
                raise ValueError(f"{field_name} is required.")
            data[field_name] = raw_value
            continue

        if not raw_value:
            raise ValueError(f"{field_name} is required.")

        try:
            data[field_name] = float(raw_value)
        except ValueError as exc:
            raise ValueError(f"{field_name} must be a number.") from exc

    return data


def analyze(data):
    pe_ratio = safe_divide(data["share_price"], data["eps"])
    ev_to_ebit = safe_divide(data["enterprise_value"], data["ebit"])
    fcf_yield = safe_divide(data["free_cash_flow"], data["market_cap"])
    debt_to_equity = safe_divide(data["total_debt"], data["shareholders_equity"])
    interest_coverage = safe_divide(data["ebit"], data["interest_expense"])
    roe = safe_divide(data["net_income"], data["shareholders_equity"])

    undervaluation_gap = 0.0
    if pe_ratio is not None and data["industry_pe"]:
        undervaluation_gap += (data["industry_pe"] - pe_ratio) / data["industry_pe"]
    if ev_to_ebit is not None and data["industry_ev_ebit"]:
        undervaluation_gap += (
            (data["industry_ev_ebit"] - ev_to_ebit) / data["industry_ev_ebit"]
        )

    quality_score = 0
    health_score = 0
    reasons = []

    if data["revenue_growth_3y"] >= 0.08:
        quality_score += 1
        reasons.append("Revenue growth is healthy over the last 3 years.")
    if data["fcf_growth_3y"] >= 0.08:
        quality_score += 1
        reasons.append("Free cash flow growth suggests improving earnings power.")
    if data["gross_margin"] >= 0.40:
        quality_score += 1
        reasons.append("Gross margin points to pricing power or operational strength.")
    if data["operating_margin"] >= 0.15:
        quality_score += 1
        reasons.append("Operating margin indicates disciplined profitability.")
    if roe is not None and roe >= 0.15:
        quality_score += 1
        reasons.append("Return on equity supports strong shareholder returns.")

    if debt_to_equity is not None and debt_to_equity <= 1.0:
        health_score += 1
        reasons.append("Debt-to-equity is within a manageable range.")
    if interest_coverage is not None and interest_coverage >= 5.0:
        health_score += 1
        reasons.append("Interest coverage suggests debt servicing is comfortable.")
    if fcf_yield is not None and fcf_yield >= 0.05:
        health_score += 1
        reasons.append("Free cash flow yield is attractive relative to market value.")

    if undervaluation_gap >= 0.20:
        valuation_score = 3
        valuation_status = "undervalued"
        reasons.append("Relative valuation screens as meaningfully discounted versus peers.")
    elif undervaluation_gap >= 0.05:
        valuation_score = 2
        valuation_status = "slightly undervalued"
        reasons.append("Relative valuation suggests modest undervaluation.")
    elif undervaluation_gap <= -0.20:
        valuation_score = 0
        valuation_status = "overvalued"
        reasons.append("Relative valuation appears stretched versus peers.")
    elif undervaluation_gap <= -0.05:
        valuation_score = 1
        valuation_status = "slightly overvalued"
        reasons.append("Relative valuation suggests a premium price.")
    else:
        valuation_score = 2
        valuation_status = "fairly valued"
        reasons.append("Relative valuation looks close to peer benchmarks.")

    total_score = quality_score + health_score + valuation_score

    if total_score >= 9 and valuation_status in {"undervalued", "slightly undervalued"}:
        strategy = "Accumulate"
        conviction = "high"
    elif total_score >= 6 and valuation_status != "overvalued":
        strategy = "Watchlist / Selective Buy"
        conviction = "medium"
    elif valuation_status == "overvalued":
        strategy = "Avoid or Wait for Better Entry"
        conviction = "medium"
    else:
        strategy = "Hold / Neutral"
        conviction = "low"

    report = "\n".join(
        [
            "Stock Analysis Report",
            "=====================",
            f"Company: {data['company']} ({data['ticker']})",
            f"Valuation Status: {valuation_status.title()}",
            f"Suggested Strategy: {strategy}",
            f"Conviction: {conviction.title()}",
            "",
            "Scores",
            f"- Business Quality: {quality_score} / 5",
            f"- Financial Health: {health_score} / 3",
            f"- Valuation: {valuation_score} / 3",
            "",
            "Key Metrics",
            f"- P/E Ratio: {format_ratio(pe_ratio)}",
            f"- EV / EBIT: {format_ratio(ev_to_ebit)}",
            f"- Free Cash Flow Yield: {format_percent(fcf_yield)}",
            f"- Debt / Equity: {format_ratio(debt_to_equity)}",
            f"- Interest Coverage: {format_ratio(interest_coverage, 'x')}",
            f"- Return on Equity: {format_percent(roe)}",
            f"- Relative Valuation Gap: {format_percent(undervaluation_gap)}",
            "",
            "Why the Tool Said This",
        ]
        + [f"- {reason}" for reason in reasons]
    )

    return {
        "company": data["company"],
        "ticker": data["ticker"],
        "valuation_status": valuation_status,
        "investment_strategy": strategy,
        "quality_score": quality_score,
        "health_score": health_score,
        "valuation_score": valuation_score,
        "conviction": conviction,
        "metrics": {
            "pe_ratio": pe_ratio,
            "ev_to_ebit": ev_to_ebit,
            "fcf_yield": fcf_yield,
            "debt_to_equity": debt_to_equity,
            "interest_coverage": interest_coverage,
            "roe": roe,
            "undervaluation_gap": undervaluation_gap,
        },
        "reasons": reasons,
        "report": report,
    }


def render_page(report_text="Run an analysis to see the result here.", values=None, error=None):
    values = {**DEFAULTS, **(values or {})}

    fields_html = []
    for field_name, label in FIELDS:
        value = html.escape(values.get(field_name, ""), quote=True)
        full = ' style="grid-column: 1 / -1;"' if field_name == "company" else ""
        fields_html.append(
            f'<div{full}><label for="{field_name}">{label}</label>'
            f'<input id="{field_name}" name="{field_name}" value="{value}" /></div>'
        )

    error_html = ""
    if error:
        error_html = (
            f'<div style="background:#fff0ea;border:1px solid #d58b73;'
            f'color:#7e2f1b;padding:12px 14px;border-radius:12px;margin-bottom:16px;">'
            f'{html.escape(error)}</div>'
            f'</div>'
        )

    safe_report = html.escape(report_text)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Stock Analysis Tool</title>
  <style>
    body {{
      margin: 0;
      font-family: Georgia, "Times New Roman", serif;
      background: linear-gradient(180deg, #f7f1e8 0%, #efe5d5 100%);
      color: #1e1c18;
    }}
    .page {{
      max-width: 1100px;
      margin: 0 auto;
      padding: 32px 20px 48px;
    }}
    .layout {{
      display: grid;
      grid-template-columns: 1.1fr 0.9fr;
      gap: 20px;
    }}
    .card {{
      background: rgba(255,250,242,0.94);
      border: 1px solid #d5c7af;
      border-radius: 18px;
      padding: 20px;
      box-shadow: 0 12px 30px rgba(83,58,31,0.08);
    }}
    .grid {{
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 14px;
    }}
    label {{
      display: block;
      font-size: 0.95rem;
      margin-bottom: 4px;
      font-weight: 700;
    }}
    input {{
      width: 100%;
      box-sizing: border-box;
      padding: 10px 12px;
      border-radius: 10px;
      border: 1px solid #d5c7af;
      background: #fffdf9;
      font-size: 0.95rem;
    }}
    button {{
      margin-top: 18px;
      background: #7c4f2c;
      color: white;
      border: 0;
      border-radius: 999px;
      padding: 12px 20px;
      font-size: 1rem;
      cursor: pointer;
    }}
    pre {{
      white-space: pre-wrap;
      word-break: break-word;
      line-height: 1.5;
      margin: 0;
    }}
    @media (max-width: 860px) {{
      .layout {{
        grid-template-columns: 1fr;
      }}
      .grid {{
        grid-template-columns: 1fr;
      }}
    }}
  </style>
</head>
<body>
  <div class="page">
    <h1>Stock Analysis Tool</h1>
    <p>Enter a company's financial data and get a valuation and strategy report.</p>
    <div class="layout">
      <div class="card">
        {error_html}
        <form method="post" action="/">
          <div class="grid">
            {''.join(fields_html)}
          </div>
          <button type="submit">Analyze Company</button>
        </form>
      </div>
      <div class="card">
        <h2>Analysis Report</h2>
        <pre>{safe_report}</pre>
      </div>
    </div>
  </div>
</body>
</html>"""


def html_response(start_response, body, status="200 OK"):
    payload = body.encode("utf-8")
    start_response(
        status,
        [
            ("Content-Type", "text/html; charset=utf-8"),
            ("Content-Length", str(len(payload))),
        ],
    )
    return [payload]


def json_response(start_response, payload, status="200 OK"):
    body = json.dumps(payload, indent=2).encode("utf-8")
    start_response(
        status,
        [
            ("Content-Type", "application/json; charset=utf-8"),
            ("Content-Length", str(len(body))),
        ],
    )
    return [body]


def app(environ, start_response):
    method = environ.get("REQUEST_METHOD", "GET").upper()
    path = environ.get("PATH_INFO", "/")

    if path == "/health":
        return json_response(start_response, {"status": "ok"})

    if method == "POST":
        length = int(environ.get("CONTENT_LENGTH") or "0")
        body = environ["wsgi.input"].read(length)
        form = parse_qs(body.decode("utf-8"), keep_blank_values=True)
        values = {key: item[0] if item else "" for key, item in form.items()}

        try:
            parsed = parse_input(values)
            result = analyze(parsed)
            return html_response(start_response, render_page(result["report"], values=values))
        except ValueError as exc:
            return html_response(
                start_response,
                render_page(values=values, error=str(exc)),
                status="400 Bad Request",
            )

    return html_response(start_response, render_page())
