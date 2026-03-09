/**
 * Exit-Intent Popup — Book Pre-Launch Lead Capture
 * Triggers on mouse exit (desktop) or after 45s (mobile)
 * Shows once per visitor via localStorage
 */
(function() {
  if (localStorage.getItem('exitPopupShown')) return;

  var popupHTML = '<div id="exit-popup-overlay" style="display:none;position:fixed;top:0;left:0;width:100%;height:100%;background:rgba(0,0,0,0.6);z-index:99999;justify-content:center;align-items:center;">' +
    '<div style="background:#fff;border-radius:12px;max-width:480px;width:90%;position:relative;overflow:hidden;box-shadow:0 20px 60px rgba(0,0,0,0.3);">' +
    '<div style="background:linear-gradient(135deg,#2e7d32,#43a047);padding:24px 28px;color:#fff;">' +
    '<button id="exit-popup-close" style="position:absolute;top:12px;right:16px;background:none;border:none;color:#fff;font-size:24px;cursor:pointer;line-height:1;">&times;</button>' +
    '<h2 style="margin:0 0 8px;font-size:1.3rem;">🎉 We\'re writing the ultimate Diabetes Management Guide for India!</h2>' +
    '<p style="margin:0;font-size:0.95rem;opacity:0.95;">Get notified when it launches + a FREE chapter</p>' +
    '</div>' +
    '<form id="exit-popup-form" style="padding:24px 28px;">' +
    '<input type="text" name="full_name" placeholder="Your Name" required style="width:100%;padding:12px;margin-bottom:12px;border:1px solid #ccc;border-radius:6px;font-size:1rem;box-sizing:border-box;">' +
    '<input type="email" name="email" placeholder="Your Email" required style="width:100%;padding:12px;margin-bottom:16px;border:1px solid #ccc;border-radius:6px;font-size:1rem;box-sizing:border-box;">' +
    '<div style="position:absolute;left:-9999px;"><input type="text" name="website" tabindex="-1" autocomplete="off"></div>' +
    '<button type="submit" style="width:100%;padding:14px;background:#2e7d32;color:#fff;border:none;border-radius:6px;font-size:1.05rem;cursor:pointer;font-weight:600;">Get My Free Chapter →</button>' +
    '<p id="exit-popup-msg" style="margin:10px 0 0;text-align:center;font-size:0.9rem;"></p>' +
    '</form>' +
    '</div></div>';

  document.body.insertAdjacentHTML('beforeend', popupHTML);

  var overlay = document.getElementById('exit-popup-overlay');
  var shown = false;

  function showPopup() {
    if (shown) return;
    shown = true;
    localStorage.setItem('exitPopupShown', '1');
    overlay.style.display = 'flex';
  }

  // Desktop: mouse leaves viewport top
  document.addEventListener('mouseout', function(e) {
    if (e.clientY < 5 && !e.relatedTarget && !e.toElement) showPopup();
  });

  // Mobile: after 45 seconds
  if (/Mobi|Android/i.test(navigator.userAgent)) {
    setTimeout(showPopup, 45000);
  }

  // Close
  document.getElementById('exit-popup-close').addEventListener('click', function() {
    overlay.style.display = 'none';
  });
  overlay.addEventListener('click', function(e) {
    if (e.target === overlay) overlay.style.display = 'none';
  });

  // Form submit
  document.getElementById('exit-popup-form').addEventListener('submit', function(e) {
    e.preventDefault();
    var form = this;
    var msg = document.getElementById('exit-popup-msg');

    if (typeof validateLeadForm === 'function') {
      var check = validateLeadForm(form);
      if (!check.valid) { msg.style.color = '#c62828'; msg.textContent = check.error; return; }
    }

    var data = new FormData(form);
    var body = {};
    data.forEach(function(v,k) { if (k !== 'website') body[k] = v; });
    body.source = 'exit-popup';
    body.page = window.location.pathname;

    fetch('https://leads.gheware-ai.com/hg-lead-book-prelaunch', {
      method: 'POST', headers: {'Content-Type':'application/json'}, body: JSON.stringify(body)
    }).then(function() {
      msg.style.color = '#2e7d32';
      msg.textContent = '✅ You\'re on the list! We\'ll notify you.';
      form.querySelector('button[type=submit]').disabled = true;
    }).catch(function() {
      msg.style.color = '#c62828';
      msg.textContent = 'Something went wrong. Please try again.';
    });
  });
})();
