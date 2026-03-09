/**
 * Lead form validation: disposable email blocking + honeypot spam trap
 * Include this script in all lead magnet pages.
 * 
 * Usage:
 *   1. Add <script src="/js/lead-validation.js"></script> before your form script
 *   2. Add honeypot field to form (see injectHoneypot)
 *   3. Call validateLeadForm(form) before fetch — returns {valid, error}
 */

// Disposable/temporary email domains (comprehensive list)
const DISPOSABLE_DOMAINS = new Set([
  // Major disposable services
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
  // Russian disposable
  'mailbox.in.ua','mail.ru','bk.ru',
]);

// Suspicious email patterns
function isDisposableEmail(email) {
  if (!email || !email.includes('@')) return true;
  const domain = email.split('@')[1].toLowerCase();
  
  // Check disposable domain list
  if (DISPOSABLE_DOMAINS.has(domain)) return true;
  
  // Check for plus-addressing abuse (not blocking, just flagging)
  // e.g. user+random123@gmail.com — allow but note
  
  // Check for very long random local parts (common in bot signups)
  const local = email.split('@')[0];
  if (local.length > 30) return true;
  
  // Check for excessive numbers in local part
  const digitRatio = (local.match(/\d/g) || []).length / local.length;
  if (digitRatio > 0.6 && local.length > 10) return true;
  
  return false;
}

// Basic email format validation
function isValidEmailFormat(email) {
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
}

// Phone validation (Indian numbers preferred)
function isValidPhone(phone) {
  if (!phone) return false;
  const digits = phone.replace(/\D/g, '');
  // Allow Indian (+91 + 10 digits) or international (7-15 digits)
  return digits.length >= 7 && digits.length <= 15;
}

/**
 * Inject honeypot field into a form. Call on page load.
 * The honeypot field is hidden via CSS and should remain empty.
 * Bots typically fill all fields, triggering the trap.
 */
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
  // Insert before the submit button
  const btn = formElement.querySelector('button[type="submit"]');
  if (btn) {
    formElement.insertBefore(honeypot, btn);
  } else {
    formElement.appendChild(honeypot);
  }
}

/**
 * Validate the lead form before submission.
 * Returns { valid: boolean, error: string|null }
 */
function validateLeadForm(formElement) {
  // 1. Honeypot check
  const honeypotField = formElement.querySelector('#website_url');
  if (honeypotField && honeypotField.value.trim() !== '') {
    // Bot detected — silently "succeed" so bot doesn't adapt
    return { valid: false, error: '__honeypot__' };
  }

  // 2. Email validation
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

  // 3. Phone validation
  const phoneField = formElement.querySelector('input[type="tel"]');
  if (phoneField && phoneField.value.trim()) {
    if (!isValidPhone(phoneField.value)) {
      return { valid: false, error: 'Please enter a valid phone number.' };
    }
  }

  // 4. Time-based check — form filled too fast (< 3 seconds) = likely bot
  if (formElement._loadTime && (Date.now() - formElement._loadTime) < 3000) {
    return { valid: false, error: '__toofast__' };
  }

  return { valid: true, error: null };
}

/**
 * Initialize lead form validation on a form element.
 * Call this on DOMContentLoaded.
 */
function initLeadFormValidation(formId) {
  const form = document.getElementById(formId);
  if (!form) return;
  
  // Record load time for timing check
  form._loadTime = Date.now();
  
  // Inject honeypot
  injectHoneypot(form);
}
