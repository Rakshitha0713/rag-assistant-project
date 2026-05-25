// ── Session management ───────────────────
function generateSessionId() {
  return 'sess_' + Date.now() + '_' + Math.random().toString(36).slice(2, 7);
}

function getOrCreateSessionId() {
  var id = localStorage.getItem('ragSessionId');
  if (!id) {
    id = generateSessionId();
    localStorage.setItem('ragSessionId', id);
  }
  return id;
}

var SESSION_ID = getOrCreateSessionId();

// ── Get DOM elements ─────────────────────
var messagesContainer = document.getElementById('messagesContainer');
var messageInput      = document.getElementById('messageInput');
var btnSend           = document.getElementById('btnSend');
var btnNewChat        = document.getElementById('btnNewChat');
var btnSidebarToggle  = document.getElementById('btnSidebarToggle');
var sidebar           = document.querySelector('.sidebar');
var typingIndicator   = document.getElementById('typingIndicator');
var welcomeCard       = document.getElementById('welcomeCard');
var sessionDisplay    = document.getElementById('sessionDisplay');

// ── Show session ID ──────────────────────
sessionDisplay.textContent = 'Session · ' + SESSION_ID.slice(-8);

// ── Sidebar toggle ───────────────────────
btnSidebarToggle.addEventListener('click', function() {
  sidebar.classList.toggle('hidden');
});

// ── New Chat button ──────────────────────
btnNewChat.addEventListener('click', function() {
  SESSION_ID = generateSessionId();
  localStorage.setItem('ragSessionId', SESSION_ID);
  sessionDisplay.textContent = 'Session · ' + SESSION_ID.slice(-8);
  messagesContainer.innerHTML = '';
  if (welcomeCard) {
    messagesContainer.appendChild(welcomeCard);
    welcomeCard.style.display = 'flex';
  }
  messageInput.value = '';
  messageInput.style.height = 'auto';
  btnSend.disabled = true;
});

// ── Input auto-resize ────────────────────
messageInput.addEventListener('input', function() {
  messageInput.style.height = 'auto';
  messageInput.style.height = Math.min(messageInput.scrollHeight, 160) + 'px';
  btnSend.disabled = messageInput.value.trim() === '';
});

// ── Enter key sends message ──────────────
messageInput.addEventListener('keydown', function(e) {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault();
    if (!btnSend.disabled) {
      sendMessage();
    }
  }
});

// ── Send button click ────────────────────
btnSend.addEventListener('click', function() {
  sendMessage();
});

// ── Suggestion chips ─────────────────────
document.addEventListener('click', function(e) {
  if (e.target && e.target.classList.contains('chip')) {
    var msg = e.target.getAttribute('data-msg');
    if (msg) {
      messageInput.value = msg;
      messageInput.style.height = 'auto';
      messageInput.style.height = Math.min(messageInput.scrollHeight, 160) + 'px';
      btnSend.disabled = false;
      sendMessage();
    }
  }
});

// ── Format time ──────────────────────────
function formatTime() {
  var now = new Date();
  var h = now.getHours();
  var m = now.getMinutes();
  var ampm = h >= 12 ? 'PM' : 'AM';
  h = h % 12 || 12;
  return h + ':' + (m < 10 ? '0' + m : m) + ' ' + ampm;
}

// ── Add message to chat ──────────────────
function addMessage(role, text, chunks, tokens, isError) {

  // Hide welcome card
  if (welcomeCard) {
    welcomeCard.style.display = 'none';
  }

  // Create row div
  var row = document.createElement('div');
  row.style.width = '100%';
  row.style.padding = '6px 24px';
  row.style.display = 'flex';
  row.style.flexDirection = 'row';
  row.style.boxSizing = 'border-box';

  if (role === 'user') {
    row.style.justifyContent = 'flex-end';
  } else {
    row.style.justifyContent = 'flex-start';
  }

  // Create wrapper div (holds label + bubble + meta)
  var wrapper = document.createElement('div');
  wrapper.style.display = 'flex';
  wrapper.style.flexDirection = 'column';
  wrapper.style.maxWidth = '70%';

  if (role === 'user') {
    wrapper.style.alignItems = 'flex-end';
  } else {
    wrapper.style.alignItems = 'flex-start';
  }

  // Add label for assistant
  if (role === 'assistant') {
    var label = document.createElement('div');
    label.style.fontFamily = 'DM Mono, monospace';
    label.style.fontSize = '10px';
    label.style.color = '#c8a96e';
    label.style.marginBottom = '4px';
    label.style.paddingLeft = '2px';
    label.textContent = '◈ RAGmind';
    wrapper.appendChild(label);
  }

  // Create the bubble
  var bubble = document.createElement('div');
  bubble.style.padding = '14px 18px';
  bubble.style.borderRadius = '18px';
  bubble.style.fontSize = '14.5px';
  bubble.style.lineHeight = '1.75';
  bubble.style.wordBreak = 'break-word';
  bubble.style.overflowWrap = 'break-word';
  bubble.style.maxWidth = '100%';
  bubble.style.display = 'block';
  bubble.style.writingMode = 'horizontal-tb';

  if (role === 'user') {
    bubble.style.background = '#1e2a3a';
    bubble.style.border = '1px solid #2a3d54';
    bubble.style.borderBottomRightRadius = '6px';
    bubble.style.color = '#e8eaf0';
  } else if (isError) {
    bubble.style.background = 'rgba(224,92,92,0.1)';
    bubble.style.border = '1px solid #e05c5c';
    bubble.style.borderBottomLeftRadius = '6px';
    bubble.style.color = '#e05c5c';
  } else {
    bubble.style.background = '#161a22';
    bubble.style.border = '1px solid #252a35';
    bubble.style.borderBottomLeftRadius = '6px';
    bubble.style.color = '#e8eaf0';
  }

  // Set text content — use textContent to avoid HTML injection issues
  bubble.textContent = text;

  wrapper.appendChild(bubble);

  // Meta line (time + badges)
  var meta = document.createElement('div');
  meta.style.display = 'flex';
  meta.style.flexDirection = 'row';
  meta.style.alignItems = 'center';
  meta.style.gap = '8px';
  meta.style.marginTop = '5px';
  meta.style.paddingLeft = '4px';
  meta.style.flexWrap = 'wrap';

  var timeSpan = document.createElement('span');
  timeSpan.style.fontFamily = 'DM Mono, monospace';
  timeSpan.style.fontSize = '10px';
  timeSpan.style.color = '#525c6e';
  timeSpan.textContent = formatTime();
  meta.appendChild(timeSpan);

  if (role === 'assistant' && typeof chunks === 'number') {
    var chunkBadge = document.createElement('span');
    chunkBadge.style.fontFamily = 'DM Mono, monospace';
    chunkBadge.style.fontSize = '10px';
    chunkBadge.style.padding = '1px 7px';
    chunkBadge.style.borderRadius = '99px';
    chunkBadge.style.background = 'rgba(200,169,110,0.15)';
    chunkBadge.style.border = '1px solid #8a6e3a';
    chunkBadge.style.color = '#c8a96e';
    chunkBadge.textContent = chunks + ' chunks retrieved';
    meta.appendChild(chunkBadge);
  }

  if (role === 'assistant' && typeof tokens === 'number') {
    var tokenBadge = document.createElement('span');
    tokenBadge.style.fontFamily = 'DM Mono, monospace';
    tokenBadge.style.fontSize = '10px';
    tokenBadge.style.padding = '1px 7px';
    tokenBadge.style.borderRadius = '99px';
    tokenBadge.style.background = '#1a1e26';
    tokenBadge.style.border = '1px solid #252a35';
    tokenBadge.style.color = '#525c6e';
    tokenBadge.textContent = tokens + ' tokens';
    meta.appendChild(tokenBadge);
  }

  wrapper.appendChild(meta);
  row.appendChild(wrapper);
  messagesContainer.appendChild(row);

  // Scroll to bottom
  messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

// ── Show/hide typing indicator ────────────
function setLoading(on) {
  if (on) {
    typingIndicator.style.display = 'flex';
    btnSend.disabled = true;
    messageInput.disabled = true;
  } else {
    typingIndicator.style.display = 'none';
    messageInput.disabled = false;
    btnSend.disabled = messageInput.value.trim() === '';
    messageInput.focus();
  }
  messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

// ── Send message to backend ───────────────
async function sendMessage() {
  var text = messageInput.value.trim();
  if (!text) return;

  // Show user message
  addMessage('user', text, null, null, false);

  // Clear input
  messageInput.value = '';
  messageInput.style.height = 'auto';
  setLoading(true);

  try {
    var response = await fetch('/api/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        sessionId: SESSION_ID,
        message: text
      })
    });

    var data = await response.json();

    if (!response.ok) {
      var errMsg = data.error || 'Something went wrong. Please try again.';
      addMessage('assistant', errMsg, null, null, true);
    } else {
      var reply  = data.reply          || 'No response received.';
      var chunks = data.retrievedChunks;
      var tokens = data.tokensUsed;
      addMessage('assistant', reply, chunks, tokens, false);
    }

  } catch (err) {
    addMessage('assistant', 'Could not reach the server. Please check your connection.', null, null, true);
  }

  setLoading(false);
}

// ── Health check on load ──────────────────
window.addEventListener('load', async function() {
  var statusDot  = document.querySelector('.status-dot');
  var statusText = document.getElementById('statusText');

  try {
    var res = await fetch('/health');
    if (res.ok) {
      statusDot.style.background = '#4ade80';
      statusDot.style.boxShadow  = '0 0 6px rgba(74,222,128,0.6)';
      statusText.textContent = 'System Online';
    } else {
      throw new Error('not ok');
    }
  } catch (e) {
    statusDot.style.background = '#e05c5c';
    statusText.textContent = 'System Offline';
  }
});