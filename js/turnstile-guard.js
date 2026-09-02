/**
 * Turnstile guard for lead-magnet forms.
 *
 * Renders a Cloudflare Turnstile widget into every form on the page that has an
 * email input, and injects the resulting token as `cf-turnstile-response` into
 * any JSON POST to leads.gheware-ai.com. The leads API verifies the token
 * server-side and rejects submits without one (403).
 *
 * Why patch fetch instead of editing each page: 16 of the 18 landing pages build
 * their POST body by hand in an inline script, each slightly differently. One
 * shared injection point is the only way to be sure every form is covered.
 *
 * Why this exists at all: every one of the 359 "leads" captured between March
 * and August 2026 was a bot posting straight at the API with a Faker name, a
 * harvested real email and a US phone number. The checks in
 * lead-validation.js run only in the browser, so a direct POST never met them.
 *
 * Requires, before this file:
 *   <script src="https://challenges.cloudflare.com/turnstile/v0/api.js?render=explicit" async defer></script>
 */
(function () {
  var SITE_KEY = '0x4AAAAAAEkpzgE2LjZb5Ipw';
  var API_RE = /^https:\/\/leads\.gheware-ai\.com\/hg-lead-/;
  var widgets = [];           // { form, id, token }
  var lastSubmitted = null;   // the form whose submit handler is running

  function render(form) {
    if (form.__turnstile || !form.querySelector('input[type="email"]')) return;
    var holder = document.createElement('div');
    holder.style.margin = '12px 0';
    var btn = form.querySelector('button[type="submit"], input[type="submit"]');
    if (btn) btn.parentNode.insertBefore(holder, btn); else form.appendChild(holder);
    var entry = { form: form, id: null, token: '' };
    entry.id = window.turnstile.render(holder, {
      sitekey: SITE_KEY,
      callback: function (t) { entry.token = t; },
      'expired-callback': function () { entry.token = ''; },
      'error-callback': function () { entry.token = ''; }
    });
    form.__turnstile = entry;
    widgets.push(entry);
  }

  function renderAll() {
    if (!window.turnstile) return;
    document.querySelectorAll('form').forEach(render);
  }

  function ready(fn) {
    if (window.turnstile) return fn();
    var prev = window.onloadTurnstileCallback;
    window.onloadTurnstileCallback = function () { if (prev) prev(); fn(); };
    // api.js may already have loaded before this file ran
    var tries = 0, iv = setInterval(function () {
      if (window.turnstile || ++tries > 100) { clearInterval(iv); if (window.turnstile) fn(); }
    }, 100);
  }

  ready(function () {
    renderAll();
    // forms added later (modals, popups)
    new MutationObserver(renderAll).observe(document.body, { childList: true, subtree: true });
  });

  document.addEventListener('submit', function (e) {
    if (e.target && e.target.tagName === 'FORM') lastSubmitted = e.target;
  }, true);

  function waitForToken(entry, ms) {
    return new Promise(function (resolve) {
      var waited = 0, iv = setInterval(function () {
        if (entry.token || (waited += 100) >= ms) { clearInterval(iv); resolve(entry.token); }
      }, 100);
    });
  }

  var origFetch = window.fetch;
  window.fetch = function (input, init) {
    var url = typeof input === 'string' ? input : (input && input.url) || '';
    if (!API_RE.test(url) || !init || typeof init.body !== 'string') return origFetch.apply(this, arguments);
    var entry = (lastSubmitted && lastSubmitted.__turnstile) || widgets[0];
    if (!entry) return origFetch.apply(this, arguments);   // server will 403; page shows its error
    return waitForToken(entry, 15000).then(function (token) {
      var body;
      try { body = JSON.parse(init.body); } catch (_) { return origFetch.call(window, input, init); }
      body['cf-turnstile-response'] = token;
      var next = Object.assign({}, init, { body: JSON.stringify(body) });
      return origFetch.call(window, input, next).then(function (resp) {
        // tokens are single-use — reset so a retry/resubmit gets a fresh one
        try { entry.token = ''; window.turnstile.reset(entry.id); } catch (_) {}
        return resp;
      });
    });
  };
})();
