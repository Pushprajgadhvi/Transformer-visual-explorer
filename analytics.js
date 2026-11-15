// Vercel Web Analytics - Inline injection
// This script initializes Vercel Web Analytics for tracking page views
(function() {
  window.va = window.va || function () { (window.vaq = window.vaq || []).push(arguments); };
  
  // Create and inject the analytics script
  var script = document.createElement('script');
  script.defer = true;
  script.src = '/_vercel/insights/script.js';
  document.head.appendChild(script);
})();
