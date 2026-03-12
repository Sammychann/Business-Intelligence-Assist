/**
 * BI Assist — Live Interview Coaching
 * Socket.IO client + Web Speech API + session management.
 */

(function () {
  'use strict';

  // ── DOM References ──────────────────────────────────
  const statusDot = document.querySelector('.status-dot');
  const statusText = document.getElementById('status-text');
  const bannerCompany = document.getElementById('banner-company');
  const bannerRole = document.getElementById('banner-role');
  const btnStart = document.getElementById('btn-start');
  const btnEnd = document.getElementById('btn-end');
  const btnSend = document.getElementById('btn-send');
  const btnMic = document.getElementById('btn-mic');
  const micLabel = document.getElementById('mic-label');
  const transcriptInput = document.getElementById('transcript-input');
  const speechStatus = document.getElementById('speech-status');
  const cardsContainer = document.getElementById('cards-container');
  const insightsBody = document.getElementById('insights-body');
  const talkingBody = document.getElementById('talking-body');
  const flagsBody = document.getElementById('flags-body');
  const insightsCounter = document.getElementById('insights-counter');
  const talkingCounter = document.getElementById('talking-counter');
  const flagsCounter = document.getElementById('flags-counter');
  const postSession = document.getElementById('post-session');
  const postSummary = document.getElementById('post-summary');
  const postTranscriptText = document.getElementById('post-transcript-text');
  const btnProcessKB = document.getElementById('btn-process-kb');
  const btnCopyTranscript = document.getElementById('btn-copy-transcript');
  const btnNewSession = document.getElementById('btn-new-session');
  const processResult = document.getElementById('process-result');
  const transcriptArea = document.getElementById('transcript-area');

  // ── State ───────────────────────────────────────────
  let sessionActive = false;
  let speechRecognition = null;
  let isListening = false;
  let updateCount = 0;
  let sessionData = null;

  // ── Read context from URL params or sessionStorage ──
  const urlParams = new URLSearchParams(window.location.search);
  const companyName = urlParams.get('company') || sessionStorage.getItem('live_company') || '';
  const role = urlParams.get('role') || sessionStorage.getItem('live_role') || '';
  let companyReport = {};

  try {
    const stored = sessionStorage.getItem('live_company_report');
    if (stored) companyReport = JSON.parse(stored);
  } catch (e) { /* ignore */ }

  // Display company info
  bannerCompany.textContent = companyName || 'No company specified';
  bannerRole.textContent = role ? `Interviewing: ${role}` : 'No role specified';

  // ── Socket.IO Connection ────────────────────────────
  const socket = io();

  socket.on('connect', () => {
    console.log('[Live] Socket.IO connected');
    statusDot.className = 'status-dot online';
    statusText.textContent = 'Connected';
  });

  socket.on('disconnect', () => {
    console.log('[Live] Socket.IO disconnected');
    statusDot.className = 'status-dot offline';
    statusText.textContent = 'Disconnected';
  });

  socket.on('session_started', (data) => {
    console.log('[Live] Session started:', data);
    sessionActive = true;
    updateCount = 0;
    btnStart.style.display = 'none';
    btnEnd.style.display = 'inline-flex';
    btnSend.disabled = false;
    statusText.textContent = `Live — ${data.company_name || 'Session Active'}`;
    postSession.style.display = 'none';
    cardsContainer.style.display = '';
    transcriptArea.style.display = '';

    // Show loading state on cards while initial insights are generated
    const loadingHTML = '<div class="card-placeholder" style="color:var(--accent-orange)">⏳ Generating initial insights...</div>';
    insightsBody.innerHTML = loadingHTML;
    talkingBody.innerHTML = loadingHTML;
    flagsBody.innerHTML = loadingHTML;
    showProcessingIndicator();
  });

  socket.on('coaching_update', (data) => {
    console.log('[Live] Coaching update received:', data);
    updateCount++;
    renderInsights(data.top_insights || []);
    renderTalkingPoints(data.talking_points || []);
    renderFlags(data.red_flags_opportunities || []);
  });

  socket.on('coaching_error', (data) => {
    console.error('[Live] Coaching error:', data);
    showToast(data.message || 'Coaching error occurred', 'error');
  });

  socket.on('session_ended', (data) => {
    sessionActive = false;
    sessionData = data;
    btnStart.style.display = 'inline-flex';
    btnEnd.style.display = 'none';
    btnSend.disabled = true;
    statusText.textContent = 'Session ended';
    stopSpeechRecognition();

    // Show post-session panel
    cardsContainer.style.display = 'none';
    transcriptArea.style.display = 'none';
    postSession.style.display = '';
    postSummary.textContent = `Processed ${data.total_chunks} transcript chunks for ${data.company_name} / ${data.role}.`;
    postTranscriptText.textContent = data.full_transcript || '(empty)';
    processResult.style.display = 'none';
  });

  socket.on('error', (data) => {
    showToast(data.message || 'Connection error', 'error');
  });

  // ── Session Controls ────────────────────────────────
  btnStart.addEventListener('click', () => {
    console.log('[Live] Starting session with:', { companyName, role });
    socket.emit('start_live_session', {
      company_name: companyName || 'Unknown Company',
      role: role || 'General',
      company_report: companyReport
    });
  });

  btnEnd.addEventListener('click', () => {
    if (confirm('End the live coaching session?')) {
      socket.emit('end_session');
    }
  });

  // ── Transcript Send ─────────────────────────────────
  btnSend.addEventListener('click', sendTranscript);
  transcriptInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendTranscript();
    }
  });

  function sendTranscript() {
    const text = transcriptInput.value.trim();
    if (!text || !sessionActive) return;

    console.log('[Live] Sending transcript chunk:', text.substring(0, 50) + '...');
    socket.emit('transcript_chunk', { text });
    transcriptInput.value = '';

    // Show processing indicator on cards
    showProcessingIndicator();
    showToast('Transcript sent — processing...', 'success');
  }

  // ── Web Speech API ──────────────────────────────────
  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;

  btnMic.addEventListener('click', () => {
    if (!SpeechRecognition) {
      showToast('Speech recognition not supported in this browser. Try Chrome.', 'error');
      return;
    }
    if (!sessionActive) {
      showToast('Start a session first before enabling speech recognition.', 'error');
      return;
    }
    if (isListening) {
      stopSpeechRecognition();
    } else {
      startSpeechRecognition();
    }
  });

  function startSpeechRecognition() {
    if (!SpeechRecognition) return;

    speechRecognition = new SpeechRecognition();
    speechRecognition.continuous = true;
    speechRecognition.interimResults = false;
    speechRecognition.lang = 'en-US';

    speechRecognition.onresult = (event) => {
      let transcript = '';
      for (let i = event.resultIndex; i < event.results.length; i++) {
        if (event.results[i].isFinal) {
          transcript += event.results[i][0].transcript + ' ';
        }
      }
      if (transcript.trim()) {
        socket.emit('transcript_chunk', { text: transcript.trim() });
        showProcessingIndicator();
      }
    };

    speechRecognition.onerror = (event) => {
      if (event.error !== 'no-speech') {
        showToast(`Speech recognition error: ${event.error}`, 'error');
      }
    };

    speechRecognition.onend = () => {
      // Restart if still listening
      if (isListening && sessionActive) {
        try { speechRecognition.start(); } catch (e) { /* ignore */ }
      }
    };

    speechRecognition.start();
    isListening = true;
    btnMic.classList.add('active');
    micLabel.textContent = 'On';
    speechStatus.style.display = 'flex';
  }

  function stopSpeechRecognition() {
    if (speechRecognition) {
      isListening = false;
      speechRecognition.stop();
      speechRecognition = null;
    }
    btnMic.classList.remove('active');
    micLabel.textContent = 'Off';
    speechStatus.style.display = 'none';
  }

  // ── Card Renderers ──────────────────────────────────
  function renderInsights(insights) {
    if (!insights.length) return;
    insightsCounter.textContent = insights.length;
    const display = insights.slice(0, 3);
    insightsBody.innerHTML = display.map((item, i) => {
      const text = typeof item === 'string' ? item : (item.insight || '');
      return `
        <div class="coach-item fade-in" style="animation-delay:${i * 0.06}s">
          <span class="item-number">${i + 1}</span>
          <div class="item-text">${esc(text)}</div>
        </div>
      `;
    }).join('');
    pulseCard('card-insights');
  }

  function renderTalkingPoints(points) {
    if (!points.length) return;
    talkingCounter.textContent = points.length;
    const display = points.slice(0, 3);
    talkingBody.innerHTML = display.map((item, i) => {
      const text = typeof item === 'string' ? item : (item.point || '');
      return `
        <div class="coach-item fade-in" style="animation-delay:${i * 0.06}s">
          <span class="item-bullet">✦</span>
          <div class="item-text">${esc(text)}</div>
        </div>
      `;
    }).join('');
    pulseCard('card-talking');
  }

  function renderFlags(flags) {
    if (!flags.length) return;
    flagsCounter.textContent = flags.length;
    const display = flags.slice(0, 3);
    flagsBody.innerHTML = display.map((item, i) => {
      const text = typeof item === 'string' ? item : (item.item || '');
      const type = typeof item === 'object' ? (item.type || 'opportunity') : 'opportunity';
      const isRed = type.toLowerCase().includes('red');
      return `
        <div class="flag-item ${isRed ? 'flag-red' : 'flag-green'} fade-in" style="animation-delay:${i * 0.06}s">
          <span class="flag-badge ${isRed ? 'badge-red' : 'badge-green'}">${isRed ? '⚠️' : '🚀'}</span>
          <div class="flag-text">${esc(text)}</div>
        </div>
      `;
    }).join('');
    pulseCard('card-flags');
  }

  function pulseCard(cardId) {
    const card = document.getElementById(cardId);
    card.classList.add('card-pulse');
    setTimeout(() => card.classList.remove('card-pulse'), 600);
  }

  function showProcessingIndicator() {
    const dots = document.querySelectorAll('.card-header');
    dots.forEach(h => h.classList.add('processing'));
    setTimeout(() => dots.forEach(h => h.classList.remove('processing')), 2000);
  }

  // ── Post-Session Actions ────────────────────────────
  btnProcessKB.addEventListener('click', async () => {
    if (!sessionData || !sessionData.full_transcript) {
      showToast('No transcript to process.', 'error');
      return;
    }

    btnProcessKB.disabled = true;
    btnProcessKB.textContent = '⏳ Processing...';

    try {
      const resp = await fetch('/api/process-transcript', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          transcript: sessionData.full_transcript,
          company_name: sessionData.company_name,
          role: sessionData.role,
          save_to_kb: true
        })
      });

      const result = await resp.json();

      if (!resp.ok) throw new Error(result.error || 'Processing failed');

      processResult.style.display = '';
      processResult.innerHTML = `
        <div class="result-success">
          <h4>✅ Transcript Processed & Saved</h4>
          <p><strong>Summary:</strong> ${esc(result.summary || '')}</p>
          <p><strong>Key Insights:</strong> ${(result.key_insights || []).length} extracted</p>
          <p><strong>Notable Quotes:</strong> ${(result.notable_quotes || []).length} found</p>
          <p><strong>Follow-up Items:</strong> ${(result.follow_up_items || []).length} identified</p>
          ${result.improvement_suggestions ? `<p><strong>Interview Tips:</strong> ${(result.improvement_suggestions || []).join('; ')}</p>` : ''}
        </div>
      `;

      showToast('Transcript processed and saved to knowledge base!', 'success');
    } catch (err) {
      showToast(err.message || 'Processing failed', 'error');
    } finally {
      btnProcessKB.disabled = false;
      btnProcessKB.textContent = '📊 Process & Save to Knowledge Base';
    }
  });

  btnCopyTranscript.addEventListener('click', () => {
    if (sessionData && sessionData.full_transcript) {
      navigator.clipboard.writeText(sessionData.full_transcript).then(() => {
        showToast('Transcript copied to clipboard!', 'success');
      });
    }
  });

  btnNewSession.addEventListener('click', () => {
    postSession.style.display = 'none';
    cardsContainer.style.display = '';
    transcriptArea.style.display = '';
    resetCards();
    sessionData = null;
    processResult.style.display = 'none';
  });

  function resetCards() {
    insightsBody.innerHTML = '<div class="card-placeholder">Start a session to see live insights...</div>';
    talkingBody.innerHTML = '<div class="card-placeholder">Talking points will appear here...</div>';
    flagsBody.innerHTML = '<div class="card-placeholder">Flags & opportunities will appear here...</div>';
    insightsCounter.textContent = '0';
    talkingCounter.textContent = '0';
    flagsCounter.textContent = '0';
  }

  // ── Toast Notifications ─────────────────────────────
  function showToast(message, type) {
    const existing = document.querySelector('.toast');
    if (existing) existing.remove();

    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.textContent = message;
    document.body.appendChild(toast);

    setTimeout(() => toast.classList.add('show'), 10);
    setTimeout(() => {
      toast.classList.remove('show');
      setTimeout(() => toast.remove(), 300);
    }, 3500);
  }

  // ── Utility ─────────────────────────────────────────
  function esc(str) {
    if (!str) return '';
    const div = document.createElement('div');
    div.textContent = String(str);
    return div.innerHTML;
  }

})();
