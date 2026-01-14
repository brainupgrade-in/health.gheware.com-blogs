/**
 * Google Analytics Loader - Dynamically loads GA tracking code
 *
 * Usage: Add this script to the <head> of your HTML pages:
 * <script src="/js/analytics-loader.js"></script>
 *
 * This will automatically inject Google Analytics tracking.
 */

(function() {
  'use strict';

  // Google Analytics 4 (GA4) Measurement ID for www.gheware.com
  const GA_MEASUREMENT_ID = 'G-2P4SEV0MH2';

  // Skip loading if Measurement ID not configured
  if (GA_MEASUREMENT_ID === 'GA_MEASUREMENT_ID') {
    console.warn('Google Analytics: Measurement ID not configured. Please update analytics-loader.js');
    return;
  }

  // Load Google Analytics gtag.js
  const script = document.createElement('script');
  script.async = true;
  script.src = `https://www.googletagmanager.com/gtag/js?id=${GA_MEASUREMENT_ID}`;
  document.head.appendChild(script);

  // Initialize dataLayer and gtag function
  window.dataLayer = window.dataLayer || [];
  function gtag(){window.dataLayer.push(arguments);}
  window.gtag = gtag;

  gtag('js', new Date());
  gtag('config', GA_MEASUREMENT_ID, {
    'send_page_view': true,
    'anonymize_ip': true,
    'cookie_flags': 'SameSite=None;Secure'
  });

  // Track source parameter for product-specific analytics
  const urlParams = new URLSearchParams(window.location.search);
  const source = urlParams.get('source');
  if (source) {
    gtag('event', 'page_view', {
      'source': source,
      'page_location': window.location.href
    });
  }

  // Helper functions for event tracking
  window.trackEvent = function(category, action, label, value) {
    if (typeof gtag !== 'undefined') {
      gtag('event', action, {
        'event_category': category,
        'event_label': label,
        'value': value
      });
    }
  };

  window.trackNewsletterSubscribe = function(location) {
    if (typeof gtag !== 'undefined') {
      gtag('event', 'newsletter_subscribe', {
        'event_category': 'engagement',
        'event_label': location
      });
    }
  };

  window.trackCTA = function(ctaName, location) {
    if (typeof gtag !== 'undefined') {
      gtag('event', 'cta_click', {
        'event_category': 'conversion',
        'event_label': ctaName,
        'value': location
      });
    }
  };

  console.log('Google Analytics loaded:', GA_MEASUREMENT_ID);
})();
