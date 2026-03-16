/**
 * Lead form validation: multi-layer bot protection
 * v2 — Added: PoW challenge, mouse/touch tracking, scroll detection, enhanced timing
 * 
 * Usage:
 *   1. Add <script src="/js/lead-validation.js"></script> before your form script
 *   2. Call initLeadFormValidation('formId') on page load
 *   3. Call validateLeadForm(form) before fetch — returns {valid, error}
 */

// Disposable/temporary email domains
const DISPOSABLE_DOMAINS = new Set([
  'tempmail.com','temp-mail.org','guerrillamail.com','guerrillamail.net',
  'guerrillamailblock.com','sharklasers.com','grr.la','guerrillamail.info',
  'guerrillamail.de','throwaway.email','yopmail.com','yopmail.fr',
  'mailinator.com','maildrop.cc','dispostable.com','trashmail.com',
  'trashmail.net','trashmail.me','trashmail.io','fakeinbox.com',
  'mailnesia.com','tempr.email','discard.email','discardmail.com',
  'discardmail.de','10minutemail.com','10minutemail.net','minutemail.com',
  'tempail.com','mohmal.com','emailondeck.com','getnada.com',
  'burnermail.io','inboxes.com','mailcatch.com','mailsac.com',
  'mytemp.email','nada.email','spamgourmet.com','throwaway.email',
  'tmpmail.net','tmpmail.org','temp-mail.io','emailfake.com',
  'crazymailing.com','mailbox92.biz','mailtothis.com','tmail.ws',
  'harakirimail.com','33mail.com','mail-temporaire.fr','jetable.org',
  'trash-mail.com','binkmail.com','bobmail.info','chammy.info',
  'devnullmail.com','dead.letter','despammed.com','disposeamail.com',
  'dodgeit.com','dontreg.com','e4ward.com','enterto.com',
  'filzmail.com','getairmail.com','guardsmail.com','haltospam.com',
  'hidemail.de','incognitomail.com','kasmail.com','klassmaster.com',
  'mailexpire.com','mailforspam.com','mailme.lv','mailmetrash.com',
  'mailmoat.com','mailnull.com','mailshell.com','mailsiphon.com',
  'mailtemp.info','mailzilla.com','mintemail.com','no-spam.ws',
  'nomail.xl.cx','objectmail.com','obobbo.com','oneoffemail.com',
  'pjjkp.com','proxymail.eu','putthisinyouremail.com','rcpt.at',
  'reallymymail.com','recode.me','regbypass.com','safetymail.info',
  'skeefmail.com','slaskpost.se','slipry.net','spambox.us',
  'spamcero.com','spamcorptastic.com','spamex.com','spamfree24.com',
  'spamfree24.info','spamfree24.net','spamgoes.in','spamhereplease.com',
  'spaml.com','spamspot.com','supergreatmail.com','supermailer.jp',
  'suremail.info','teleworm.us','tempomail.fr','temporaryemail.net',
  'temporaryemail.us','temporaryforwarding.com','temporaryinbox.com',
  'thankmail.info','tyldd.com','uggsrock.com','veryrealemail.com',
  'vidchart.com','viditag.com','viewcastmedia.com','webm4il.info',
  'wegwerfmail.de','wegwerfmail.net','wetrainbayarea.com','wh4f.org',
  'whatiaas.com','whatpaas.com','wilemail.com','willhackforfood.biz',
  'woolydogs.com','wronghead.com','wuzup.net','wuzupmail.net',
  'wwwnew.eu','xagloo.com','xemaps.com','xents.com','xjoi.com',
  'xoxy.net','yep.it','yogamaven.com','yuurok.com','zehnminutenmail.de',
  'zippymail.info','zoaxe.com','zoemail.org',
  'mailbox.in.ua','mail.ru','bk.ru',
]);

function isDisposableEmail(email) {
  if (!email || !email.includes('@')) return true;
  const domain = email.split('@')[1].toLowerCase();
  if (DISPOSABLE_DOMAINS.has(domain)) return true;
  const local = email.split('@')[0];
  if (local.length > 30) return true;
  const digitRatio = (local.match(/\d/g) || []).length / local.length;
  if (digitRatio > 0.6 && local.length > 10) return true;
  return false;
}

function isValidEmailFormat(email) {
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
}

function isValidPhone(phone) {
  if (!phone) return false;
  const digits = phone.replace(/\D/g, '');
  return digits.length >= 7 && digits.length <= 15;
}

// ─── Behavioral signals (bots can't fake these easily) ───

const _bhv = {
  mouseMovements: 0,
  keystrokes: 0,
  scrolled: false,
  touchEvents: 0,
  fieldFocusTimes: {},  // track per-field focus durations
  lastFocusField: null,
  lastFocusTime: 0,
};

function _trackMouse() { _bhv.mouseMovements++; }
function _trackKey()   { _bhv.keystrokes++; }
function _trackScroll(){ _bhv.scrolled = true; }
function _trackTouch() { _bhv.touchEvents++; }

function _trackFocus(e) {
  if (_bhv.lastFocusField && _bhv.lastFocusTime) {
    const dur = Date.now() - _bhv.lastFocusTime;
    _bhv.fieldFocusTimes[_bhv.lastFocusField] = (_bhv.fieldFocusTimes[_bhv.lastFocusField] || 0) + dur;
  }
  _bhv.lastFocusField = e.target.name || e.target.id;
  _bhv.lastFocusTime = Date.now();
}

function _startBehaviorTracking() {
  document.addEventListener('mousemove', _trackMouse, { passive: true });
  document.addEventListener('keydown', _trackKey, { passive: true });
  document.addEventListener('scroll', _trackScroll, { passive: true });
  document.addEventListener('touchstart', _trackTouch, { passive: true });
  document.addEventListener('focusin', _trackFocus, { passive: true });
}

function _getBehaviorScore() {
  let score = 0;
  if (_bhv.mouseMovements > 5) score += 2;
  if (_bhv.mouseMovements > 20) score += 1;
  if (_bhv.keystrokes > 5) score += 2;
  if (_bhv.scrolled) score += 1;
  if (_bhv.touchEvents > 0) score += 2; // mobile user
  const fieldCount = Object.keys(_bhv.fieldFocusTimes).length;
  if (fieldCount >= 2) score += 2; // interacted with multiple fields
  return score; // max ~10, bots typically score 0-1
}

// ─── Proof-of-Work challenge (makes mass submissions expensive) ───

function _generateChallenge() {
  const ts = Date.now().toString(36);
  const rand = Math.random().toString(36).slice(2, 8);
  return { prefix: ts + rand, difficulty: 4 }; // find hash starting with 4 zeros
}

async function _solveChallenge(challenge) {
  // Simple PoW: find a nonce such that SHA-256(prefix + nonce) starts with N zeros
  const target = '0'.repeat(challenge.difficulty);
  for (let nonce = 0; nonce < 1000000; nonce++) {
    const input = challenge.prefix + nonce;
    const hash = await _sha256(input);
    if (hash.startsWith(target)) {
      return { prefix: challenge.prefix, nonce, hash };
    }
  }
  return null; // shouldn't happen with difficulty 4
}

async function _sha256(message) {
  const msgBuffer = new TextEncoder().encode(message);
  const hashBuffer = await crypto.subtle.digest('SHA-256', msgBuffer);
  const hashArray = Array.from(new Uint8Array(hashBuffer));
  return hashArray.map(b => b.toString(16).padStart(2, '0')).join('');
}

// ─── Honeypot injection ───

function injectHoneypot(formElement) {
  const honeypot = document.createElement('div');
  honeypot.style.position = 'absolute';
  honeypot.style.left = '-9999px';
  honeypot.style.opacity = '0';
  honeypot.style.height = '0';
  honeypot.style.overflow = 'hidden';
  honeypot.setAttribute('aria-hidden', 'true');
  honeypot.innerHTML = `
    <label for="website_url">Website</label>
    <input type="text" id="website_url" name="website_url" tabindex="-1" autocomplete="off">
  `;
  // Second honeypot with different field name
  const honeypot2 = document.createElement('div');
  honeypot2.style.position = 'absolute';
  honeypot2.style.left = '-9999px';
  honeypot2.style.opacity = '0';
  honeypot2.style.height = '0';
  honeypot2.style.overflow = 'hidden';
  honeypot2.setAttribute('aria-hidden', 'true');
  honeypot2.innerHTML = `
    <label for="company_name">Company</label>
    <input type="text" id="company_name" name="company_name" tabindex="-1" autocomplete="off">
  `;
  
  const btn = formElement.querySelector('button[type="submit"]');
  if (btn) {
    formElement.insertBefore(honeypot, btn);
    formElement.insertBefore(honeypot2, btn);
  } else {
    formElement.appendChild(honeypot);
    formElement.appendChild(honeypot2);
  }
}

// ─── Name validation (detect faker-generated names) ───

function _isLikelyFakeName(name) {
  if (!name || name.trim().length < 2) return true;
  const parts = name.trim().split(/\s+/);
  // Single character names
  if (parts.some(p => p.length === 1)) return true;
  // Check for common faker patterns — unusual surname combinations
  // Names with uncommon characters
  if (/[^a-zA-Z\s.\-']/.test(name)) return false; // non-latin = probably real (Indian names etc)
  // Very uncommon names often have rare letter combos
  return false; // can't reliably detect without a dictionary; rely on other signals
}

// ─── Math CAPTCHA (stops bots using real emails) ───

function injectMathChallenge(formElement) {
  const a = Math.floor(Math.random() * 9) + 1;
  const b = Math.floor(Math.random() * 9) + 1;
  formElement._mathAnswer = a + b;

  const wrapper = document.createElement('div');
  wrapper.style.cssText = 'margin-bottom:12px;';
  wrapper.innerHTML =
    '<label style="display:block;font-size:0.95rem;margin-bottom:4px;font-weight:600;">🔒 Quick verify: What is ' + a + ' + ' + b + '?</label>' +
    '<input type="number" id="_math_check" name="_math_check" required ' +
    'style="width:100%;padding:10px;border:1px solid #ccc;border-radius:6px;font-size:1rem;box-sizing:border-box;" ' +
    'placeholder="Enter your answer">';

  const btn = formElement.querySelector('button[type="submit"]');
  if (btn) {
    formElement.insertBefore(wrapper, btn);
  } else {
    formElement.appendChild(wrapper);
  }
}

// ─── Main validation ───

function validateLeadForm(formElement) {
  // 0. Math CAPTCHA check
  if (formElement._mathAnswer !== undefined) {
    const mathInput = formElement.querySelector('#_math_check');
    if (!mathInput || parseInt(mathInput.value, 10) !== formElement._mathAnswer) {
      return { valid: false, error: 'Please solve the math question correctly.' };
    }
  }

  // 1. Honeypot check
  const hp1 = formElement.querySelector('#website_url');
  const hp2 = formElement.querySelector('#company_name');
  if ((hp1 && hp1.value.trim() !== '') || (hp2 && hp2.value.trim() !== '')) {
    return { valid: false, error: '__honeypot__' };
  }

  // 2. Timing check — must spend at least 5 seconds (raised from 3)
  if (formElement._loadTime && (Date.now() - formElement._loadTime) < 5000) {
    return { valid: false, error: '__toofast__' };
  }

  // 3. Behavioral score — must show human-like interactions
  const behScore = _getBehaviorScore();
  if (behScore < 2) {
    // No mouse, no keystrokes, no scroll, no touch — almost certainly a bot
    return { valid: false, error: '__nointeraction__' };
  }

  // 4. Email validation
  const emailField = formElement.querySelector('input[type="email"]');
  if (emailField) {
    const email = emailField.value.trim().toLowerCase();
    if (!isValidEmailFormat(email)) {
      return { valid: false, error: 'Please enter a valid email address.' };
    }
    if (isDisposableEmail(email)) {
      return { valid: false, error: 'Please use a permanent email address (not a temporary/disposable one).' };
    }
  }

  // 5. Phone validation
  const phoneField = formElement.querySelector('input[type="tel"]');
  if (phoneField && phoneField.value.trim()) {
    if (!isValidPhone(phoneField.value)) {
      return { valid: false, error: 'Please enter a valid phone number.' };
    }
  }

  return { valid: true, error: null };
}

// ─── Solve PoW before submission (adds ~200-500ms for humans, expensive for mass bots) ───

async function validateAndSolveChallenge(formElement) {
  const validation = validateLeadForm(formElement);
  if (!validation.valid) return validation;

  // Solve PoW
  const challenge = _generateChallenge();
  const solution = await _solveChallenge(challenge);
  if (!solution) {
    return { valid: false, error: 'Verification failed. Please try again.' };
  }

  // Attach PoW proof as hidden fields
  let powField = formElement.querySelector('#_pow_proof');
  if (!powField) {
    powField = document.createElement('input');
    powField.type = 'hidden';
    powField.id = '_pow_proof';
    powField.name = '_pow_proof';
    formElement.appendChild(powField);
  }
  powField.value = JSON.stringify(solution);

  return { valid: true, error: null, powSolution: solution };
}

// ─── Init ───

function initLeadFormValidation(formId) {
  const form = document.getElementById(formId);
  if (!form) return;
  
  form._loadTime = Date.now();
  injectHoneypot(form);
  injectMathChallenge(form);
  _startBehaviorTracking();
}
