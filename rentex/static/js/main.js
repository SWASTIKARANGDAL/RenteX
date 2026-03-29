/* RenteX Main JavaScript */

// ── Initialize Bootstrap tooltips & popovers ──
document.addEventListener('DOMContentLoaded', () => {
  // Tooltips
  document.querySelectorAll('[data-bs-toggle="tooltip"]').forEach(el => {
    new bootstrap.Tooltip(el);
  });

  // Popovers
  document.querySelectorAll('[data-bs-toggle="popover"]').forEach(el => {
    new bootstrap.Popover(el);
  });

  // Auto-close mobile nav on link click
  document.querySelectorAll('#navMain .nav-link:not(.dropdown-toggle)').forEach(link => {
    link.addEventListener('click', () => {
      const collapse = document.querySelector('#navMain');
      if (collapse.classList.contains('show')) {
        new bootstrap.Collapse(collapse).hide();
      }
    });
  });

  // Image preview on file input change
  document.querySelectorAll('input[type="file"][accept*="image"]').forEach(input => {
    input.addEventListener('change', function () {
      const file = this.files[0];
      if (!file) return;
      const reader = new FileReader();
      reader.onload = e => {
        let preview = this.nextElementSibling;
        if (!preview || !preview.classList.contains('img-preview')) {
          preview = document.createElement('img');
          preview.className = 'img-preview';
          this.parentNode.insertBefore(preview, this.nextSibling);
        }
        preview.src = e.target.result;
      };
      reader.readAsDataURL(file);
    });
  });

  // Notification bell live count
  refreshNotificationCount();
});

// ── CSRF helper ──
function getCsrfToken() {
  return document.cookie.split(';')
    .find(c => c.trim().startsWith('csrftoken='))
    ?.split('=')[1] || '';
}

// ── Refresh unread notification count ──
function refreshNotificationCount() {
  if (!document.querySelector('.rx-navbar')) return;
  fetch('/api/notifications/unread/')
    .then(r => r.json())
    .then(data => {
      const badge = document.querySelector('.notif-badge');
      if (data.count > 0) {
        if (!badge) {
          const bell = document.querySelector('.notif-bell');
          if (bell) {
            const b = document.createElement('span');
            b.className = 'position-absolute top-0 start-100 translate-middle badge rounded-pill bg-danger notif-badge';
            b.style.fontSize = '0.65rem';
            b.textContent = data.count;
            bell.appendChild(b);
          }
        } else {
          badge.textContent = data.count;
        }
      } else if (badge) {
        badge.remove();
      }
    })
    .catch(() => {});
}

// ── Wishlist toggle (used in product cards) ──
function toggleWishlistBtn(slug, btn) {
  fetch(`/products/${slug}/wishlist/`, {
    method: 'POST',
    headers: {
      'X-CSRFToken': getCsrfToken(),
      'X-Requested-With': 'XMLHttpRequest',
    }
  })
  .then(r => r.json())
  .then(data => {
    const icon = btn.querySelector('i');
    if (data.status === 'added') {
      icon.className = 'bi bi-heart-fill';
      icon.style.color = '#ef4444';
      showToast('Added to wishlist ❤️', 'success');
    } else {
      icon.className = 'bi bi-heart';
      icon.style.color = '';
      showToast('Removed from wishlist', 'info');
    }
  })
  .catch(() => showToast('Please log in to use wishlist', 'warning'));
}

// ── Toast utility ──
function showToast(message, type = 'info') {
  const colors = {
    success: 'bg-success',
    error: 'bg-danger',
    warning: 'bg-warning text-dark',
    info: 'bg-info',
  };
  const container = document.querySelector('.toast-container') || (() => {
    const c = document.createElement('div');
    c.className = 'toast-container';
    document.body.appendChild(c);
    return c;
  })();

  const toast = document.createElement('div');
  toast.className = `toast align-items-center text-white border-0 ${colors[type]} show mb-2`;
  toast.style.borderRadius = '12px';
  toast.style.boxShadow = '0 8px 32px rgba(0,0,0,0.15)';
  toast.innerHTML = `
    <div class="d-flex">
      <div class="toast-body fw-500">${message}</div>
      <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
    </div>`;
  container.appendChild(toast);
  new bootstrap.Toast(toast, { delay: 3500 }).show();
  toast.addEventListener('hidden.bs.toast', () => toast.remove());
}

// ── Date range picker helper ──
function initDateRange(startId, endId, onChangeCallback) {
  const start = document.getElementById(startId);
  const end = document.getElementById(endId);
  if (!start || !end) return;

  const today = new Date().toISOString().split('T')[0];
  start.min = today;
  end.min = today;

  start.addEventListener('change', () => {
    if (end.value && end.value <= start.value) {
      const d = new Date(start.value);
      d.setDate(d.getDate() + 1);
      end.value = d.toISOString().split('T')[0];
    }
    end.min = start.value;
    if (onChangeCallback) onChangeCallback();
  });

  end.addEventListener('change', () => {
    if (onChangeCallback) onChangeCallback();
  });
}

// ── Format currency ──
function formatINR(amount) {
  return new Intl.NumberFormat('en-IN', {
    style: 'currency', currency: 'INR', maximumFractionDigits: 0
  }).format(amount);
}

// ── Confirm action with custom dialog ──
function confirmAction(message, callback) {
  if (confirm(message)) callback();
}

// ── Smooth scroll to element ──
function scrollTo(selector) {
  const el = document.querySelector(selector);
  if (el) el.scrollIntoView({ behavior: 'smooth', block: 'start' });
}
