from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
import numpy as np
from scipy import stats

app = Flask(__name__)
CORS(app)

HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>T-Test Calculator</title>
<link href="https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=Syne:wght@400;600;800&display=swap" rel="stylesheet">
<style>
  :root {
    --bg: #0a0a0f;
    --surface: #111118;
    --card: #16161f;
    --border: #2a2a3a;
    --accent: #7c3aed;
    --accent2: #06b6d4;
    --text: #e8e8f0;
    --muted: #6b6b80;
    --success: #10b981;
    --warn: #f59e0b;
    --danger: #ef4444;
  }

  * { box-sizing: border-box; margin: 0; padding: 0; }

  body {
    background: var(--bg);
    color: var(--text);
    font-family: 'Syne', sans-serif;
    min-height: 100vh;
    overflow-x: hidden;
  }

  body::before {
    content: '';
    position: fixed;
    top: -50%;
    left: -50%;
    width: 200%;
    height: 200%;
    background: radial-gradient(ellipse at 30% 20%, rgba(124,58,237,0.08) 0%, transparent 50%),
                radial-gradient(ellipse at 70% 80%, rgba(6,182,212,0.06) 0%, transparent 50%);
    pointer-events: none;
    z-index: 0;
  }

  .container {
    max-width: 900px;
    margin: 0 auto;
    padding: 2rem 1.5rem;
    position: relative;
    z-index: 1;
  }

  header {
    text-align: center;
    margin-bottom: 3rem;
    animation: fadeDown 0.6s ease both;
  }

  .label-tag {
    display: inline-block;
    font-family: 'Space Mono', monospace;
    font-size: 0.7rem;
    letter-spacing: 0.2em;
    color: var(--accent2);
    border: 1px solid var(--accent2);
    padding: 0.25rem 0.75rem;
    border-radius: 2px;
    margin-bottom: 1rem;
    text-transform: uppercase;
  }

  h1 {
    font-size: clamp(2rem, 5vw, 3.5rem);
    font-weight: 800;
    line-height: 1;
    background: linear-gradient(135deg, #fff 0%, var(--accent2) 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
  }

  .subtitle {
    color: var(--muted);
    font-size: 0.95rem;
    margin-top: 0.75rem;
    font-weight: 400;
  }

  .tabs {
    display: flex;
    gap: 0.5rem;
    margin-bottom: 2rem;
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 0.4rem;
    animation: fadeUp 0.5s 0.1s ease both;
  }

  .tab {
    flex: 1;
    padding: 0.65rem 1rem;
    border: none;
    background: transparent;
    color: var(--muted);
    font-family: 'Syne', sans-serif;
    font-size: 0.85rem;
    font-weight: 600;
    border-radius: 5px;
    cursor: pointer;
    transition: all 0.2s;
    text-transform: uppercase;
    letter-spacing: 0.05em;
  }

  .tab.active {
    background: var(--accent);
    color: #fff;
  }

  .tab:hover:not(.active) {
    background: var(--card);
    color: var(--text);
  }

  .panel { display: none; }
  .panel.active { display: block; animation: fadeUp 0.3s ease both; }

  .card {
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 1.75rem;
    margin-bottom: 1.5rem;
  }

  .card-title {
    font-size: 0.7rem;
    font-family: 'Space Mono', monospace;
    letter-spacing: 0.15em;
    color: var(--muted);
    text-transform: uppercase;
    margin-bottom: 1.25rem;
    display: flex;
    align-items: center;
    gap: 0.5rem;
  }

  .card-title::before {
    content: '';
    display: inline-block;
    width: 8px; height: 8px;
    background: var(--accent);
    border-radius: 50%;
  }

  .form-group { margin-bottom: 1.25rem; }

  label {
    display: block;
    font-size: 0.82rem;
    font-weight: 600;
    color: var(--muted);
    margin-bottom: 0.4rem;
    letter-spacing: 0.04em;
  }

  input, select, textarea {
    width: 100%;
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 6px;
    color: var(--text);
    font-family: 'Space Mono', monospace;
    font-size: 0.88rem;
    padding: 0.65rem 0.9rem;
    transition: border-color 0.2s;
    outline: none;
  }

  input:focus, select:focus, textarea:focus {
    border-color: var(--accent);
    box-shadow: 0 0 0 3px rgba(124,58,237,0.12);
  }

  textarea { resize: vertical; min-height: 80px; }

  select option { background: var(--card); }

  .grid-2 {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 1rem;
  }

  @media (max-width: 600px) { .grid-2 { grid-template-columns: 1fr; } }

  .hint {
    font-size: 0.75rem;
    color: var(--muted);
    margin-top: 0.3rem;
    font-family: 'Space Mono', monospace;
  }

  .btn {
    width: 100%;
    padding: 0.85rem 2rem;
    background: linear-gradient(135deg, var(--accent), #5b21b6);
    border: none;
    border-radius: 7px;
    color: #fff;
    font-family: 'Syne', sans-serif;
    font-size: 0.95rem;
    font-weight: 700;
    letter-spacing: 0.06em;
    text-transform: uppercase;
    cursor: pointer;
    transition: all 0.2s;
    position: relative;
    overflow: hidden;
    margin-top: 0.5rem;
  }

  .btn::after {
    content: '';
    position: absolute;
    top: 50%; left: 50%;
    width: 0; height: 0;
    background: rgba(255,255,255,0.15);
    border-radius: 50%;
    transform: translate(-50%, -50%);
    transition: width 0.4s, height 0.4s;
  }

  .btn:active::after { width: 300px; height: 300px; }
  .btn:hover { transform: translateY(-1px); box-shadow: 0 8px 25px rgba(124,58,237,0.35); }
  .btn:active { transform: translateY(0); }

  .btn.loading { opacity: 0.7; pointer-events: none; }

  .result-box {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 1.5rem;
    margin-top: 1.5rem;
    display: none;
    animation: fadeUp 0.4s ease both;
  }

  .result-box.show { display: block; }

  .result-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 1.25rem;
    padding-bottom: 1rem;
    border-bottom: 1px solid var(--border);
  }

  .result-title {
    font-size: 0.7rem;
    font-family: 'Space Mono', monospace;
    letter-spacing: 0.15em;
    color: var(--muted);
    text-transform: uppercase;
  }

  .verdict {
    font-size: 0.75rem;
    font-weight: 700;
    padding: 0.3rem 0.75rem;
    border-radius: 20px;
    font-family: 'Space Mono', monospace;
    letter-spacing: 0.05em;
  }

  .verdict.reject { background: rgba(239,68,68,0.15); color: var(--danger); border: 1px solid rgba(239,68,68,0.3); }
  .verdict.fail { background: rgba(16,185,129,0.15); color: var(--success); border: 1px solid rgba(16,185,129,0.3); }

  .stats-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
    gap: 1rem;
    margin-bottom: 1.25rem;
  }

  .stat-item {
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 7px;
    padding: 1rem;
    text-align: center;
  }

  .stat-label {
    font-size: 0.65rem;
    font-family: 'Space Mono', monospace;
    color: var(--muted);
    text-transform: uppercase;
    letter-spacing: 0.1em;
    margin-bottom: 0.35rem;
  }

  .stat-value {
    font-family: 'Space Mono', monospace;
    font-size: 1.2rem;
    font-weight: 700;
    color: var(--accent2);
  }

  .interpretation {
    background: rgba(124,58,237,0.07);
    border: 1px solid rgba(124,58,237,0.2);
    border-radius: 7px;
    padding: 1rem 1.1rem;
    font-size: 0.85rem;
    line-height: 1.6;
    color: var(--text);
  }

  .error-box {
    background: rgba(239,68,68,0.08);
    border: 1px solid rgba(239,68,68,0.25);
    border-radius: 7px;
    padding: 1rem;
    color: var(--danger);
    font-size: 0.85rem;
    font-family: 'Space Mono', monospace;
    margin-top: 1rem;
    display: none;
  }

  .error-box.show { display: block; }

  .alpha-row {
    display: flex;
    align-items: center;
    gap: 0.75rem;
  }

  .alpha-row input { flex: 1; }

  @keyframes fadeDown {
    from { opacity: 0; transform: translateY(-20px); }
    to { opacity: 1; transform: translateY(0); }
  }

  @keyframes fadeUp {
    from { opacity: 0; transform: translateY(15px); }
    to { opacity: 1; transform: translateY(0); }
  }
</style>
</head>
<body>
<div class="container">
  <header>
    <div class="label-tag">Statistical Analysis</div>
    <h1>T-Test Calculator</h1>
    <p class="subtitle">One-sample, two-sample independent & paired t-tests</p>
  </header>

  <div class="tabs">
    <button class="tab active" onclick="switchTab('one')">One-Sample</button>
    <button class="tab" onclick="switchTab('two')">Two-Sample</button>
    <button class="tab" onclick="switchTab('paired')">Paired</button>
  </div>

  <!-- ONE-SAMPLE -->
  <div class="panel active" id="panel-one">
    <div class="card">
      <div class="card-title">One-Sample T-Test</div>
      <div class="form-group">
        <label>Sample Data</label>
        <textarea id="one-data" placeholder="102, 98, 101, 105, 97, 99, 103"></textarea>
        <div class="hint">Comma-separated numbers</div>
      </div>
      <div class="grid-2">
        <div class="form-group">
          <label>Population Mean (H₀)</label>
          <input type="number" id="one-popmean" placeholder="100" step="any">
        </div>
        <div class="form-group">
          <label>Hypothesis (Alternative)</label>
          <select id="one-hyp">
            <option value="two-sided">Two-sided (≠)</option>
            <option value="greater">Greater (&gt;)</option>
            <option value="less">Less (&lt;)</option>
          </select>
        </div>
      </div>
      <div class="form-group">
        <label>Significance Level (α)</label>
        <input type="number" id="one-alpha" value="0.05" step="0.01" min="0.001" max="0.5">
      </div>
      <button class="btn" onclick="runTest('one')">Run T-Test →</button>
    </div>
    <div class="error-box" id="one-error"></div>
    <div class="result-box" id="one-result"></div>
  </div>

  <!-- TWO-SAMPLE -->
  <div class="panel" id="panel-two">
    <div class="card">
      <div class="card-title">Independent Two-Sample T-Test</div>
      <div class="grid-2">
        <div class="form-group">
          <label>Group 1 Data</label>
          <textarea id="two-data1" placeholder="12, 15, 14, 10, 13"></textarea>
        </div>
        <div class="form-group">
          <label>Group 2 Data</label>
          <textarea id="two-data2" placeholder="18, 20, 17, 22, 19"></textarea>
        </div>
      </div>
      <div class="grid-2">
        <div class="form-group">
          <label>Hypothesis (Alternative)</label>
          <select id="two-hyp">
            <option value="two-sided">Two-sided (≠)</option>
            <option value="greater">Group 1 &gt; Group 2</option>
            <option value="less">Group 1 &lt; Group 2</option>
          </select>
        </div>
        <div class="form-group">
          <label>Equal Variances</label>
          <select id="two-equal-var">
            <option value="false">No (Welch's t-test)</option>
            <option value="true">Yes (Student's t-test)</option>
          </select>
        </div>
      </div>
      <div class="form-group">
        <label>Significance Level (α)</label>
        <input type="number" id="two-alpha" value="0.05" step="0.01" min="0.001" max="0.5">
      </div>
      <button class="btn" onclick="runTest('two')">Run T-Test →</button>
    </div>
    <div class="error-box" id="two-error"></div>
    <div class="result-box" id="two-result"></div>
  </div>

  <!-- PAIRED -->
  <div class="panel" id="panel-paired">
    <div class="card">
      <div class="card-title">Paired T-Test</div>
      <div class="grid-2">
        <div class="form-group">
          <label>Before / Group A</label>
          <textarea id="paired-data1" placeholder="85, 90, 78, 92, 88"></textarea>
        </div>
        <div class="form-group">
          <label>After / Group B</label>
          <textarea id="paired-data2" placeholder="88, 94, 80, 97, 91"></textarea>
        </div>
      </div>
      <div class="grid-2">
        <div class="form-group">
          <label>Hypothesis (Alternative)</label>
          <select id="paired-hyp">
            <option value="two-sided">Two-sided (≠)</option>
            <option value="greater">Before &gt; After</option>
            <option value="less">Before &lt; After</option>
          </select>
        </div>
        <div class="form-group">
          <label>Significance Level (α)</label>
          <input type="number" id="paired-alpha" value="0.05" step="0.01" min="0.001" max="0.5">
        </div>
      </div>
      <button class="btn" onclick="runTest('paired')">Run T-Test →</button>
    </div>
    <div class="error-box" id="paired-error"></div>
    <div class="result-box" id="paired-result"></div>
  </div>
</div>

<script>
function switchTab(type) {
  document.querySelectorAll('.tab').forEach((t, i) => {
    t.classList.toggle('active', ['one','two','paired'][i] === type);
  });
  document.querySelectorAll('.panel').forEach(p => p.classList.remove('active'));
  document.getElementById('panel-' + type).classList.add('active');
}

function parseData(str) {
  return str.split(/[,\\n\\s]+/).map(s => s.trim()).filter(Boolean).map(Number);
}

async function runTest(type) {
  const btn = document.querySelector(`#panel-${type} .btn`);
  const resultBox = document.getElementById(type + '-result');
  const errorBox = document.getElementById(type + '-error');
  btn.classList.add('loading');
  btn.textContent = 'Computing...';
  resultBox.classList.remove('show');
  errorBox.classList.remove('show');

  try {
    let body = {};
    if (type === 'one') {
      body = {
        type: 'one_sample',
        data: parseData(document.getElementById('one-data').value),
        pop_mean: parseFloat(document.getElementById('one-popmean').value),
        hypothesis: document.getElementById('one-hyp').value,
        alpha: parseFloat(document.getElementById('one-alpha').value)
      };
    } else if (type === 'two') {
      body = {
        type: 'two_sample',
        data1: parseData(document.getElementById('two-data1').value),
        data2: parseData(document.getElementById('two-data2').value),
        hypothesis: document.getElementById('two-hyp').value,
        equal_var: document.getElementById('two-equal-var').value === 'true',
        alpha: parseFloat(document.getElementById('two-alpha').value)
      };
    } else {
      body = {
        type: 'paired',
        data1: parseData(document.getElementById('paired-data1').value),
        data2: parseData(document.getElementById('paired-data2').value),
        hypothesis: document.getElementById('paired-hyp').value,
        alpha: parseFloat(document.getElementById('paired-alpha').value)
      };
    }

    const res = await fetch('/api/ttest', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body)
    });
    const data = await res.json();

    if (!res.ok) throw new Error(data.error || 'Unknown error');

    renderResult(type, data, body.alpha);
  } catch (e) {
    errorBox.textContent = '⚠ ' + e.message;
    errorBox.classList.add('show');
  } finally {
    btn.classList.remove('loading');
    btn.textContent = 'Run T-Test →';
  }
}

function renderResult(type, data, alpha) {
  const box = document.getElementById(type + '-result');
  const reject = data.p_value < alpha;
  const verdict = reject
    ? `<span class="verdict reject">Reject H₀</span>`
    : `<span class="verdict fail">Fail to Reject H₀</span>`;

  const interp = reject
    ? `At α = ${alpha}, the p-value (${data.p_value.toFixed(4)}) is less than the significance level. There is sufficient statistical evidence to reject the null hypothesis.`
    : `At α = ${alpha}, the p-value (${data.p_value.toFixed(4)}) is greater than the significance level. There is insufficient evidence to reject the null hypothesis.`;

  let extraStats = '';
  if (data.mean1 !== undefined) {
    extraStats = `
      <div class="stat-item"><div class="stat-label">Mean 1</div><div class="stat-value">${data.mean1.toFixed(4)}</div></div>
      <div class="stat-item"><div class="stat-label">Mean 2</div><div class="stat-value">${data.mean2.toFixed(4)}</div></div>`;
  } else if (data.sample_mean !== undefined) {
    extraStats = `<div class="stat-item"><div class="stat-label">Sample Mean</div><div class="stat-value">${data.sample_mean.toFixed(4)}</div></div>`;
  }

  box.innerHTML = `
    <div class="result-header">
      <span class="result-title">Results</span>
      ${verdict}
    </div>
    <div class="stats-grid">
      <div class="stat-item"><div class="stat-label">T-Statistic</div><div class="stat-value">${data.t_statistic.toFixed(4)}</div></div>
      <div class="stat-item"><div class="stat-label">P-Value</div><div class="stat-value">${data.p_value.toFixed(4)}</div></div>
      <div class="stat-item"><div class="stat-label">Deg. of Freedom</div><div class="stat-value">${data.degrees_of_freedom !== undefined ? data.degrees_of_freedom.toFixed(2) : 'N/A'}</div></div>
      ${extraStats}
    </div>
    <div class="interpretation">${interp}</div>`;
  box.classList.add('show');
}
</script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML)

@app.route('/api/ttest', methods=['POST'])
def ttest():
    try:
        body = request.get_json()
        test_type = body.get('type')
        alpha = float(body.get('alpha', 0.05))

        if test_type == 'one_sample':
            data = np.array(body['data'], dtype=float)
            pop_mean = float(body['pop_mean'])
            hypothesis = body.get('hypothesis', 'two-sided')
            t_stat, p_val = stats.ttest_1samp(data, pop_mean, alternative=hypothesis)
            df = len(data) - 1
            return jsonify({
                't_statistic': float(t_stat),
                'p_value': float(p_val),
                'degrees_of_freedom': float(df),
                'sample_mean': float(np.mean(data)),
                'n': len(data)
            })

        elif test_type == 'two_sample':
            data1 = np.array(body['data1'], dtype=float)
            data2 = np.array(body['data2'], dtype=float)
            hypothesis = body.get('hypothesis', 'two-sided')
            equal_var = body.get('equal_var', False)
            t_stat, p_val = stats.ttest_ind(data1, data2, equal_var=equal_var, alternative=hypothesis)
            # Welch-Satterthwaite df approximation
            if not equal_var:
                s1, s2 = np.var(data1, ddof=1), np.var(data2, ddof=1)
                n1, n2 = len(data1), len(data2)
                df = (s1/n1 + s2/n2)**2 / ((s1/n1)**2/(n1-1) + (s2/n2)**2/(n2-1))
            else:
                df = len(data1) + len(data2) - 2
            return jsonify({
                't_statistic': float(t_stat),
                'p_value': float(p_val),
                'degrees_of_freedom': float(df),
                'mean1': float(np.mean(data1)),
                'mean2': float(np.mean(data2))
            })

        elif test_type == 'paired':
            data1 = np.array(body['data1'], dtype=float)
            data2 = np.array(body['data2'], dtype=float)
            hypothesis = body.get('hypothesis', 'two-sided')
            t_stat, p_val = stats.ttest_rel(data1, data2, alternative=hypothesis)
            df = len(data1) - 1
            return jsonify({
                't_statistic': float(t_stat),
                'p_value': float(p_val),
                'degrees_of_freedom': float(df),
                'mean1': float(np.mean(data1)),
                'mean2': float(np.mean(data2))
            })

        else:
            return jsonify({'error': 'Unknown test type'}), 400

    except KeyError as e:
        return jsonify({'error': f'Missing field: {str(e)}'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
