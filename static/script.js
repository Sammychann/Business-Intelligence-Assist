/**
 * Business Intelligence Assist — Client-side application logic
 * Handles form submission, API calls, and dashboard rendering.
 */

(function () {
  'use strict';

  // ── DOM References ──────────────────────────────────
  const searchForm = document.getElementById('search-form');
  const companyInput = document.getElementById('company-input');
  const analyzeBtn = document.getElementById('analyze-btn');
  const btnText = document.getElementById('btn-text');
  const btnSpinner = document.getElementById('btn-spinner');
  const errorBanner = document.getElementById('error-banner');
  const loadingOverlay = document.getElementById('loading-overlay');
  const loadingSteps = document.getElementById('loading-steps');
  const reportDashboard = document.getElementById('report-dashboard');
  const heroSection = document.getElementById('hero-section');

  // ── Loading Step Messages ───────────────────────────
  const LOADING_MESSAGES = [
    '🔍 Searching public data sources...',
    '📊 Gathering financial information...',
    '🏢 Analyzing company structure...',
    '🤖 Running AI intelligence engine...',
    '📈 Building SWOT analysis...',
    '⚡ Generating strategic insights...',
    '✅ Finalizing report...'
  ];

  // ── Event Listeners ─────────────────────────────────
  searchForm.addEventListener('submit', handleSubmit);

  async function handleSubmit(e) {
    e.preventDefault();
    const companyName = companyInput.value.trim();
    if (!companyName) return;

    setLoading(true);
    hideError();
    hideReport();

    try {
      const response = await fetch('/api/analyze', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ company_name: companyName })
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || 'Analysis failed. Please try again.');
      }

      renderReport(data);
    } catch (err) {
      showError(err.message || 'Network error. Please check your connection and try again.');
    } finally {
      setLoading(false);
    }
  }

  // ── UI State Helpers ────────────────────────────────
  function setLoading(active) {
    analyzeBtn.disabled = active;
    btnText.textContent = active ? 'Analyzing...' : 'Analyze';
    btnSpinner.style.display = active ? 'block' : 'none';
    loadingOverlay.classList.toggle('active', active);

    if (active) {
      loadingSteps.innerHTML = '';
      startLoadingSteps();
    }
  }

  let loadingInterval = null;
  function startLoadingSteps() {
    let i = 0;
    clearInterval(loadingInterval);
    loadingInterval = setInterval(() => {
      if (i >= LOADING_MESSAGES.length) {
        clearInterval(loadingInterval);
        return;
      }
      const step = document.createElement('div');
      step.className = 'loading-step';
      step.style.animationDelay = '0s';
      step.textContent = LOADING_MESSAGES[i];
      loadingSteps.appendChild(step);
      i++;
    }, 2500);
  }

  function showError(msg) {
    errorBanner.textContent = '⚠️ ' + msg;
    errorBanner.classList.add('active');
  }

  function hideError() {
    errorBanner.classList.remove('active');
  }

  function hideReport() {
    reportDashboard.classList.remove('active');
  }

  // ── Report Renderer ─────────────────────────────────
  function renderReport(data) {
    clearInterval(loadingInterval);
    reportDashboard.innerHTML = '';

    // Header
    const confidenceLevel = (data.analysis_confidence || 'Medium').toLowerCase();
    const confidenceClass = confidenceLevel.includes('high') ? 'confidence-high' :
      confidenceLevel.includes('low') ? 'confidence-low' : 'confidence-medium';

    reportDashboard.innerHTML = `
      <div class="report-header">
        <h2 class="report-company-name">${escHtml(data.company_name || 'Company')}</h2>
        <span class="report-confidence ${confidenceClass}">
          ● ${escHtml(data.analysis_confidence || 'Medium')} Confidence
        </span>
      </div>
    `;

    // 1. Executive Summary
    addSection(reportDashboard, {
      icon: '📋', iconClass: 'blue', title: 'Executive Summary',
      body: `<p>${escHtml(data.executive_summary || 'N/A')}</p>`
    });

    // 2-col row: Financial + Competitive
    const row1 = createRow2Col();
    reportDashboard.appendChild(row1);

    // 2. Financial Snapshot
    const fin = data.financial_snapshot || {};
    addSection(row1, {
      icon: '💰', iconClass: 'emerald', title: 'Financial Snapshot',
      body: `
        <div class="finance-grid">
          ${financeItem('Revenue', fin.revenue)}
          ${financeItem('Trend', fin.revenue_trend)}
          ${financeItem('Employees', fin.employees)}
          ${financeItem('Funding', fin.funding_status)}
          ${financeItem('Profitability', fin.profitability_status)}
        </div>
      `
    });

    // 4. Competitive Positioning
    const comp = data.competitive_positioning || {};
    addSection(row1, {
      icon: '🎯', iconClass: 'cyan', title: 'Competitive Positioning',
      body: `
        <div class="positioning-grid">
          ${positioningItem('Market Category', comp.market_category)}
          ${positioningItem('Differentiation', comp.differentiation)}
          ${positioningItem('Market Maturity', comp.market_maturity)}
        </div>
      `
    });

    // 3. Business Model Analysis
    addSection(reportDashboard, {
      icon: '🏗️', iconClass: 'purple', title: 'Business Model Analysis',
      body: `<p>${escHtml(data.business_model_analysis || 'N/A')}</p>`
    });

    // 5. SWOT Analysis
    const swot = data.swot_analysis || {};
    addSection(reportDashboard, {
      icon: '🧭', iconClass: 'amber', title: 'SWOT Analysis',
      body: `
        <div class="swot-grid">
          ${swotQuadrant('Strengths', 'strengths', swot.strengths)}
          ${swotQuadrant('Weaknesses', 'weaknesses', swot.weaknesses)}
          ${swotQuadrant('Opportunities', 'opportunities', swot.opportunities)}
          ${swotQuadrant('Threats', 'threats', swot.threats)}
        </div>
      `
    });

    // 2-col row: Market Outlook + Risk
    const row2 = createRow2Col();
    reportDashboard.appendChild(row2);

    // 6. Market & Growth Outlook
    const mgo = data.market_growth_outlook || {};
    const growthLevel = (mgo.growth_potential || 'moderate').toLowerCase();
    addSection(row2, {
      icon: '📈', iconClass: 'emerald', title: 'Market & Growth Outlook',
      body: `
        <div class="outlook-grid">
          ${outlookItem('Industry Trend', mgo.industry_trend)}
          <div class="outlook-item">
            <div class="outlook-label">Growth Potential</div>
            <span class="growth-badge ${growthLevel}">${escHtml(mgo.growth_potential || 'N/A')}</span>
          </div>
          ${outlookItem('Expansion', mgo.expansion_opportunities)}
        </div>
      `
    });

    // 7. Risk Assessment
    const risk = data.risk_assessment || {};
    const riskScore = risk.overall_risk_score || 0;
    const riskColor = riskScore <= 3 ? 'var(--accent-emerald)' :
      riskScore <= 6 ? 'var(--accent-amber)' : 'var(--accent-rose)';

    addSection(row2, {
      icon: '⚠️', iconClass: 'rose', title: 'Risk Assessment',
      body: `
        <div class="risk-list">
          ${riskItem('Regulatory', risk.regulatory_risk)}
          ${riskItem('Competitive', risk.competitive_risk)}
          ${riskItem('Market', risk.market_risk)}
          ${riskItem('Operational', risk.operational_risk)}
          ${riskItem('Financial', risk.financial_risk)}
        </div>
        <div class="risk-score-display">
          <span class="risk-score-label">Overall Risk Score</span>
          <span class="risk-score-value" style="color:${riskColor}">${riskScore}/10</span>
        </div>
      `
    });

    // 8. AI Opportunities
    const aiOps = data.ai_opportunities || [];
    addSection(reportDashboard, {
      icon: '🤖', iconClass: 'purple', title: 'AI / Technology Opportunities',
      body: `
        <div class="ai-list">
          ${aiOps.map(item => `
            <div class="ai-item">
              <span class="ai-item-icon">◆</span>
              <span>${escHtml(item)}</span>
            </div>
          `).join('')}
        </div>
      `
    });

    // 9. Key Insights
    const insights = data.key_insights || [];
    addSection(reportDashboard, {
      icon: '💡', iconClass: 'amber', title: 'Key Strategic Insights',
      body: `
        <div class="insights-list">
          ${insights.map((item, i) => `
            <div class="insight-item">
              <span class="insight-number">${i + 1}</span>
              <span>${escHtml(item)}</span>
            </div>
          `).join('')}
        </div>
      `
    });

    // Show the dashboard
    reportDashboard.classList.add('active');

    // Scroll to report
    setTimeout(() => {
      reportDashboard.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }, 200);

    // Apply staggered animation
    const cards = reportDashboard.querySelectorAll('.section-card');
    cards.forEach((card, i) => {
      card.style.animationDelay = `${i * 0.08}s`;
    });
  }

  // ── Component Builders ──────────────────────────────
  function addSection(parent, { icon, iconClass, title, body }) {
    const card = document.createElement('div');
    card.className = 'section-card';
    card.innerHTML = `
      <div class="section-header">
        <div class="section-icon ${iconClass}">${icon}</div>
        <h3 class="section-title">${escHtml(title)}</h3>
      </div>
      <div class="section-body">${body}</div>
    `;
    parent.appendChild(card);
  }

  function createRow2Col() {
    const row = document.createElement('div');
    row.className = 'report-grid-2col';
    return row;
  }

  function financeItem(label, value) {
    return `
      <div class="finance-item">
        <div class="finance-label">${escHtml(label)}</div>
        <div class="finance-value">${escHtml(value || 'Not Public')}</div>
      </div>
    `;
  }

  function positioningItem(label, value) {
    return `
      <div class="positioning-item">
        <div class="positioning-label">${escHtml(label)}</div>
        <div class="positioning-value">${escHtml(value || 'N/A')}</div>
      </div>
    `;
  }

  function outlookItem(label, value) {
    return `
      <div class="outlook-item">
        <div class="outlook-label">${escHtml(label)}</div>
        <div class="outlook-value">${escHtml(value || 'N/A')}</div>
      </div>
    `;
  }

  function swotQuadrant(title, cls, items) {
    const list = (items || []).map(i => `<li>${escHtml(i)}</li>`).join('');
    return `
      <div class="swot-quadrant">
        <div class="swot-quadrant-title ${cls}">
          ${cls === 'strengths' ? '💪' : cls === 'weaknesses' ? '⚡' : cls === 'opportunities' ? '🚀' : '🛡️'}
          ${escHtml(title)}
        </div>
        <ul class="swot-list">${list || '<li>N/A</li>'}</ul>
      </div>
    `;
  }

  function riskItem(label, level) {
    const l = (level || 'low').toLowerCase();
    const cls = l.includes('high') ? 'high' : l.includes('medium') ? 'medium' : 'low';
    return `
      <div class="risk-item">
        <span class="risk-label">${escHtml(label)}</span>
        <div class="risk-bar-track">
          <div class="risk-bar-fill ${cls}"></div>
        </div>
        <span class="risk-level ${cls}">${escHtml(level || 'Low')}</span>
      </div>
    `;
  }

  // ── Utility ─────────────────────────────────────────
  function escHtml(str) {
    if (!str) return '';
    const div = document.createElement('div');
    div.textContent = String(str);
    return div.innerHTML;
  }

})();
