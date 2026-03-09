/**
 * BI Assist — Transcript & Interview Coach
 * Client-side application logic.
 *
 * Use case: Student is preparing to INTERVIEW someone at a company.
 * - Company Insights tab: non-obvious intelligence, talking points, red flags
 * - Questions to Ask tab: smart questions the student should ASK the interviewee
 */

(function () {
  'use strict';

  // ── DOM References ──────────────────────────────────
  const searchForm = document.getElementById('search-form');
  const companyInput = document.getElementById('company-input');
  const roleInput = document.getElementById('role-input');
  const analyzeBtn = document.getElementById('analyze-btn');
  const btnText = document.getElementById('btn-text');
  const btnSpinner = document.getElementById('btn-spinner');
  const errorBanner = document.getElementById('error-banner');
  const loadingOverlay = document.getElementById('loading-overlay');
  const loadingSteps = document.getElementById('loading-steps');
  const reportDashboard = document.getElementById('report-dashboard');

  const tabBtns = document.querySelectorAll('.tab-btn');
  const contentIntelligence = document.getElementById('content-intelligence');
  const contentInterview = document.getElementById('content-interview');
  const contentPostInterview = document.getElementById('content-post-interview');
  const pipelineTrace = document.getElementById('pipeline-trace');
  const goLiveBar = document.getElementById('go-live-bar');
  const btnGoLive = document.getElementById('btn-go-live');
  const postTranscriptInput = document.getElementById('post-transcript-input');
  const btnProcessTranscript = document.getElementById('btn-process-transcript');
  const processBtnText = document.getElementById('process-btn-text');
  const processSpinner = document.getElementById('process-spinner');
  const postInterviewResults = document.getElementById('post-interview-results');

  // Store last analysis data for Go Live context
  let lastAnalysisData = null;

  // ── Loading Step Messages ───────────────────────────
  const LOADING_MESSAGES = [
    '🔍 Agent 1: Checking business directory...',
    '🌐 Agent 1: Running web search for latest data...',
    '🤖 Agent 1: Synthesizing hidden insights...',
    '🎯 Agent 2: Searching role-specific context...',
    '📝 Agent 2: Consulting interview knowledge base...',
    '💡 Agent 2: Generating questions you should ask...',
    '⚡ Orchestrator: Merging agent outputs...',
    '✅ Pipeline complete — building your prep sheet...'
  ];

  // ── Tab Navigation ──────────────────────────────────
  const allTabContents = [contentIntelligence, contentInterview, contentPostInterview];
  tabBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      const tab = btn.dataset.tab;
      tabBtns.forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      allTabContents.forEach(c => c.classList.remove('active'));
      if (tab === 'intelligence') {
        contentIntelligence.classList.add('active');
      } else if (tab === 'interview') {
        contentInterview.classList.add('active');
      } else if (tab === 'post-interview') {
        contentPostInterview.classList.add('active');
      }
    });
  });

  // ── Event Listeners ─────────────────────────────────
  searchForm.addEventListener('submit', handleSubmit);

  async function handleSubmit(e) {
    e.preventDefault();
    const companyName = companyInput.value.trim();
    const role = roleInput.value.trim();

    if (!companyName || !role) {
      showError('Both company name and role are required.');
      return;
    }

    setLoading(true);
    hideError();
    hideReport();

    try {
      const response = await fetch('/api/analyze', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ company_name: companyName, role: role })
      });

      const data = await response.json();
      if (!response.ok) {
        throw new Error(data.error || 'Analysis failed. Please try again.');
      }

      renderReport(data);
    } catch (err) {
      showError(err.message || 'Network error. Please check your connection.');
    } finally {
      setLoading(false);
    }
  }

  // ── UI State Helpers ────────────────────────────────
  function setLoading(active) {
    analyzeBtn.disabled = active;
    btnText.textContent = active ? 'Running Agents...' : 'Prepare My Interview';
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
      if (i >= LOADING_MESSAGES.length) { clearInterval(loadingInterval); return; }
      const step = document.createElement('div');
      step.className = 'loading-step';
      step.textContent = LOADING_MESSAGES[i];
      loadingSteps.appendChild(step);
      i++;
    }, 3000);
  }

  function showError(msg) {
    errorBanner.textContent = '⚠️ ' + msg;
    errorBanner.classList.add('active');
  }

  function hideError() { errorBanner.classList.remove('active'); }
  function hideReport() { reportDashboard.classList.remove('active'); }

  // ── Report Renderer ─────────────────────────────────
  function renderReport(data) {
    clearInterval(loadingInterval);
    contentIntelligence.innerHTML = '';
    contentInterview.innerHTML = '';
    pipelineTrace.innerHTML = '';

    // Reset tabs
    tabBtns.forEach(b => b.classList.remove('active'));
    document.getElementById('tab-intelligence').classList.add('active');
    contentIntelligence.classList.add('active');
    contentInterview.classList.remove('active');

    // ── REPORT HEADER ─────────────────────────────
    const confidenceLevel = (data.analysis_confidence || 'Medium').toLowerCase();
    const confidenceClass = confidenceLevel.includes('high') ? 'confidence-high' :
      confidenceLevel.includes('low') ? 'confidence-low' : 'confidence-medium';

    const headerDiv = document.createElement('div');
    headerDiv.className = 'report-header';
    headerDiv.innerHTML = `
      <div>
        <h2 class="report-company-name">${esc(data.company_name || 'Company')}</h2>
      </div>
      <div style="display:flex;gap:8px;align-items:center;flex-wrap:wrap">
        <span class="report-role-badge">👤 Interviewing: ${esc(data.role_analyzed || '')}</span>
        <span class="report-confidence ${confidenceClass}">
          ● ${esc(data.analysis_confidence || 'Medium')} Confidence
        </span>
      </div>
    `;
    contentIntelligence.appendChild(headerDiv);

    // ── COMPANY INSIGHTS TAB ──────────────────────

    // 1. Company Snapshot (brief)
    const snap = data.company_snapshot || {};
    addSection(contentIntelligence, {
      icon: '🏢', iconClass: 'black', title: 'Company at a Glance',
      body: `
        <div class="snapshot-grid">
          ${snapItem('What They Do', snap.what_they_do)}
          ${snapItem('Industry', snap.industry)}
          ${snapItem('Size', snap.size)}
          ${snapItem('Founded', snap.founded)}
          ${snapItem('HQ', snap.headquarters)}
        </div>
      `
    });

    // 2. Hidden Insights (main value)
    const insights = data.hidden_insights || [];
    if (insights.length > 0) {
      addSection(contentIntelligence, {
        icon: '💡', iconClass: 'orange', title: 'Hidden Insights — What You Won\'t Find on Google',
        body: `
          <div class="insights-list">
            ${insights.map((item, i) => {
          const insight = typeof item === 'string' ? item : item.insight || '';
          const sig = typeof item === 'object' ? (item.significance || '') : '';
          return `
                <div class="insight-item">
                  <span class="insight-number">${i + 1}</span>
                  <div>
                    <div style="font-weight:600;color:var(--gray-900);margin-bottom:4px">${esc(insight)}</div>
                    ${sig ? `<div style="font-size:12px;color:var(--gray-500);font-style:italic">↳ ${esc(sig)}</div>` : ''}
                  </div>
                </div>
              `;
        }).join('')}
          </div>
        `
      });
    }

    // 3. Talking Points
    const talkingPoints = data.talking_points || [];
    if (talkingPoints.length > 0) {
      addSection(contentIntelligence, {
        icon: '🗣️', iconClass: 'emerald', title: 'Talking Points — Sound Impressively Prepared',
        body: `
          <div class="ai-list">
            ${talkingPoints.map(tp => `
              <div class="ai-item">
                <span class="ai-item-icon">✦</span>
                <span>${esc(tp)}</span>
              </div>
            `).join('')}
          </div>
        `
      });
    }

    // 4. Red Flags & Opportunities
    const rfos = data.red_flags_opportunities || [];
    if (rfos.length > 0) {
      addSection(contentIntelligence, {
        icon: '🔎', iconClass: 'amber', title: 'Red Flags & Opportunities — What to Probe',
        body: `
          <div class="rfo-list">
            ${rfos.map(rfo => {
          const item = typeof rfo === 'string' ? rfo : rfo.item || '';
          const type = typeof rfo === 'object' ? (rfo.type || 'opportunity') : 'opportunity';
          const probe = typeof rfo === 'object' ? (rfo.probe_question || '') : '';
          const isRedFlag = type.toLowerCase().includes('red');
          return `
                <div class="rfo-item ${isRedFlag ? 'rfo-red' : 'rfo-green'}">
                  <div class="rfo-header">
                    <span class="rfo-badge ${isRedFlag ? 'rfo-badge-red' : 'rfo-badge-green'}">${isRedFlag ? '⚠️ Red Flag' : '🚀 Opportunity'}</span>
                    <span class="rfo-text">${esc(item)}</span>
                  </div>
                  ${probe ? `<div class="rfo-probe">💬 Ask: "${esc(probe)}"</div>` : ''}
                </div>
              `;
        }).join('')}
          </div>
        `
      });
    }

    // ── INTERVIEW TAB ────────────────────────────
    renderInterviewSection(data);

    // ── PIPELINE TRACE ───────────────────────────
    renderPipelineTrace(data._pipeline);

    // Store for Go Live context
    lastAnalysisData = data;

    // Show Go Live bar
    goLiveBar.style.display = 'flex';

    // Show dashboard
    reportDashboard.classList.add('active');
    setTimeout(() => {
      reportDashboard.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }, 200);

    // Staggered animation
    reportDashboard.querySelectorAll('.section-card').forEach((card, i) => {
      card.style.animationDelay = `${i * 0.06}s`;
    });
  }

  // ── Interview Section Renderer ──────────────────────
  function renderInterviewSection(data) {
    const questions = data.interview_questions || [];
    const tips = data.coaching_tips || [];
    const role = data.role_analyzed || '';
    const company = data.company_name || '';

    contentInterview.innerHTML = '';

    // Header
    const headerDiv = document.createElement('div');
    headerDiv.className = 'interview-header';
    headerDiv.innerHTML = `
      <h3>🎯 Questions to Ask the ${esc(role)} at ${esc(company)}</h3>
      <p>${questions.length} smart questions generated from company intelligence, web research, and interview knowledge base. Click any question to see the expected answer and why it's worth asking.</p>
    `;
    contentInterview.appendChild(headerDiv);

    if (questions.length === 0) {
      const empty = document.createElement('p');
      empty.style.cssText = 'color:var(--gray-400);text-align:center;padding:40px 0';
      empty.textContent = 'No questions generated. Please try again.';
      contentInterview.appendChild(empty);
      return;
    }

    const catLabels = {
      'role_specific': '👤 Role-Specific',
      'strategic': '📈 Strategic',
      'culture_insight': '🏢 Culture & Team',
      // Fallbacks for old categories
      'technical': '🔧 Technical',
      'company_specific': '🏢 Company',
      'behavioral': '🤝 Behavioral'
    };

    // Category filters
    const categories = [...new Set(questions.map(q => q.category || 'general'))];
    const filterDiv = document.createElement('div');
    filterDiv.className = 'interview-categories';

    const allBtn = document.createElement('button');
    allBtn.className = 'category-filter active';
    allBtn.dataset.cat = 'all';
    allBtn.textContent = `All (${questions.length})`;
    filterDiv.appendChild(allBtn);

    categories.forEach(cat => {
      const count = questions.filter(q => q.category === cat).length;
      const btn = document.createElement('button');
      btn.className = 'category-filter';
      btn.dataset.cat = cat;
      btn.textContent = `${catLabels[cat] || cat} (${count})`;
      filterDiv.appendChild(btn);
    });

    contentInterview.appendChild(filterDiv);

    // Question cards
    const listDiv = document.createElement('div');
    listDiv.className = 'question-list';

    questions.forEach((q, i) => {
      const card = document.createElement('div');
      card.className = 'question-card';
      card.dataset.category = q.category || 'general';

      const difficulty = (q.difficulty || 'medium').toLowerCase();
      const category = q.category || 'general';
      const whyAsk = q.why_ask_this || q.reasoning || '';

      card.innerHTML = `
        <div class="question-card-header">
          <span class="question-number">${i + 1}</span>
          <div class="question-content">
            <div class="question-text">${esc(q.question || '')}</div>
            <div class="question-meta">
              <span class="question-category-badge badge-${escAttr(category)}">${esc(catLabels[category] || category)}</span>
              <span class="difficulty-badge difficulty-${escAttr(difficulty)}">${esc(difficulty)}</span>
            </div>
          </div>
          <span class="question-expand-icon">▾</span>
        </div>
        <div class="question-answer">
          <div class="answer-label">What They'll Likely Say</div>
          <div class="answer-text">${esc(q.expected_answer || 'N/A')}</div>
          ${whyAsk ? `<div class="answer-reasoning">🎯 <strong>Why ask this:</strong> ${esc(whyAsk)}</div>` : ''}
        </div>
      `;

      card.querySelector('.question-card-header').addEventListener('click', () => {
        card.classList.toggle('expanded');
      });

      listDiv.appendChild(card);
    });

    contentInterview.appendChild(listDiv);

    // Category filter delegation
    filterDiv.addEventListener('click', (e) => {
      const btn = e.target.closest('.category-filter');
      if (!btn) return;
      filterDiv.querySelectorAll('.category-filter').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      const cat = btn.dataset.cat;
      listDiv.querySelectorAll('.question-card').forEach(card => {
        card.style.display = (cat === 'all' || card.dataset.category === cat) ? '' : 'none';
      });
    });

    // Coaching Tips
    if (tips.length > 0) {
      const coachingSection = document.createElement('div');
      coachingSection.className = 'coaching-section';
      coachingSection.innerHTML = `
        <div class="coaching-card">
          <div class="coaching-title">🎓 Interview Coaching Tips for You</div>
          <ul class="coaching-list">
            ${tips.map(tip => `<li>${esc(tip)}</li>`).join('')}
          </ul>
        </div>
      `;
      contentInterview.appendChild(coachingSection);
    }
  }

  // ── Pipeline Trace Renderer ─────────────────────────
  function renderPipelineTrace(pipeline) {
    if (!pipeline) return;
    const agents = pipeline.agent_trace || [];
    const total = pipeline.total_elapsed_seconds || 0;

    let html = '<div class="pipeline-title">Agentic Pipeline Trace</div>';
    html += '<div class="pipeline-agents">';
    agents.forEach(agent => {
      html += `
        <div class="pipeline-agent">
          <span class="pipeline-agent-status ${agent.status || 'unknown'}"></span>
          <span>${esc(agent.agent || 'Agent')}</span>
          <span class="pipeline-agent-time">${agent.elapsed_seconds || 0}s</span>
        </div>
      `;
    });
    html += '</div>';
    html += `<div class="pipeline-total">Total pipeline time: <strong>${total}s</strong></div>`;
    pipelineTrace.innerHTML = html;
  }

  // ── Component Builders ──────────────────────────────
  function addSection(parent, { icon, iconClass, title, body }) {
    const card = document.createElement('div');
    card.className = 'section-card';
    card.innerHTML = `
      <div class="section-header">
        <div class="section-icon ${iconClass}">${icon}</div>
        <h3 class="section-title">${esc(title)}</h3>
      </div>
      <div class="section-body">${body}</div>
    `;
    parent.appendChild(card);
  }

  function snapItem(label, value) {
    return `
      <div class="snapshot-item">
        <div class="snapshot-label">${esc(label)}</div>
        <div class="snapshot-value">${esc(value || 'N/A')}</div>
      </div>
    `;
  }

  // ── Go Live Handler ─────────────────────────────────
  btnGoLive.addEventListener('click', () => {
    if (!lastAnalysisData) {
      showError('Please run an analysis first before going live.');
      return;
    }
    // Store context for the live page
    sessionStorage.setItem('live_company', lastAnalysisData.company_name || '');
    sessionStorage.setItem('live_role', lastAnalysisData.role_analyzed || '');
    sessionStorage.setItem('live_company_report', JSON.stringify(lastAnalysisData));

    // Open live coaching in a new window
    const params = new URLSearchParams({
      company: lastAnalysisData.company_name || '',
      role: lastAnalysisData.role_analyzed || ''
    });
    window.open(`/live?${params.toString()}`, '_blank',
      'width=500,height=800,menubar=no,toolbar=no,location=no,status=no');
  });

  // ── Post-Interview Transcript Processing ────────────
  postTranscriptInput.addEventListener('input', () => {
    btnProcessTranscript.disabled = !postTranscriptInput.value.trim();
  });

  btnProcessTranscript.addEventListener('click', async () => {
    const transcript = postTranscriptInput.value.trim();
    if (!transcript) return;

    const companyName = companyInput.value.trim() || (lastAnalysisData && lastAnalysisData.company_name) || '';
    const role = roleInput.value.trim() || (lastAnalysisData && lastAnalysisData.role_analyzed) || '';

    if (!companyName || !role) {
      showError('Please enter a company name and role first (or run an analysis).');
      return;
    }

    // Show loading state
    btnProcessTranscript.disabled = true;
    processBtnText.textContent = 'Processing...';
    processSpinner.style.display = 'inline-block';

    try {
      const resp = await fetch('/api/process-transcript', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          transcript,
          company_name: companyName,
          role: role,
          save_to_kb: true
        })
      });

      const result = await resp.json();
      if (!resp.ok) throw new Error(result.error || 'Processing failed');

      renderPostInterviewResults(result);
    } catch (err) {
      showError(err.message || 'Transcript processing failed.');
    } finally {
      btnProcessTranscript.disabled = false;
      processBtnText.textContent = '📊 Process & Save to KB';
      processSpinner.style.display = 'none';
    }
  });

  function renderPostInterviewResults(data) {
    postInterviewResults.style.display = '';
    postInterviewResults.innerHTML = `
      <div class="section-card">
        <div class="section-header">
          <div class="section-icon emerald">✅</div>
          <h3 class="section-title">Transcript Processed & Saved</h3>
        </div>
        <div class="section-body">
          <p style="margin-bottom:12px;color:var(--gray-600)">${esc(data.summary || '')}</p>

          ${data.key_insights && data.key_insights.length ? `
            <h4 style="margin:12px 0 6px;font-size:14px">Key Insights (${data.key_insights.length})</h4>
            <div class="insights-list">
              ${data.key_insights.map((item, i) => `
                <div class="insight-item">
                  <span class="insight-number">${i + 1}</span>
                  <div>
                    <div style="font-weight:600;margin-bottom:2px">${esc(item.insight || '')}</div>
                    ${item.source_quote ? `<div style="font-size:12px;color:var(--gray-500);font-style:italic">"${esc(item.source_quote)}"</div>` : ''}
                  </div>
                </div>
              `).join('')}
            </div>
          ` : ''}

          ${data.notable_quotes && data.notable_quotes.length ? `
            <h4 style="margin:12px 0 6px;font-size:14px">Notable Quotes</h4>
            <div class="ai-list">
              ${data.notable_quotes.map(q => `
                <div class="ai-item">
                  <span class="ai-item-icon">💬</span>
                  <div>
                    <div style="font-style:italic">"${esc(q.quote || '')}"</div>
                    ${q.context ? `<div style="font-size:12px;color:var(--gray-500);margin-top:2px">${esc(q.context)}</div>` : ''}
                  </div>
                </div>
              `).join('')}
            </div>
          ` : ''}

          ${data.follow_up_items && data.follow_up_items.length ? `
            <h4 style="margin:12px 0 6px;font-size:14px">Follow-Up Items</h4>
            <div class="ai-list">
              ${data.follow_up_items.map(item => `
                <div class="ai-item">
                  <span class="ai-item-icon">📌</span>
                  <span>${esc(item)}</span>
                </div>
              `).join('')}
            </div>
          ` : ''}
        </div>
      </div>
    `;

    postInterviewResults.scrollIntoView({ behavior: 'smooth', block: 'start' });
  }

  // ── Utility ─────────────────────────────────────────
  function esc(str) {
    if (!str) return '';
    const div = document.createElement('div');
    div.textContent = String(str);
    return div.innerHTML;
  }

  function escAttr(str) {
    return String(str || '').replace(/[^a-zA-Z0-9_-]/g, '_');
  }

})();
