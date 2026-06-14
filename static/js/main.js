// Auto-refresh alerts badge in navbar every 30 seconds
(function() {
  function refreshAlertCount() {
    fetch('/api/alerts/')
      .then(function(r) { return r.json(); })
      .then(function(data) {
        var count = data.alerts ? data.alerts.length : 0;
        var badge = document.querySelector('.badge-count');
        if (badge) badge.textContent = count;
      })
      .catch(function() {});
  }
  setInterval(refreshAlertCount, 30000);
})();
