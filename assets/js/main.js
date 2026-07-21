/* ==========================================================================
   Shrimp Farm Record Management System - Main Global JavaScript
   ========================================================================== */

document.addEventListener('DOMContentLoaded', () => {
  initThemeToggle();
  initSidebarToggle();
  highlightActiveNav();
  initNotificationsPopover();
});

/* Theme Toggle (Light / Dark Mode with localStorage) */
function initThemeToggle() {
  const savedTheme = localStorage.getItem('shrimp_theme') || 'light';
  document.documentElement.setAttribute('data-theme', savedTheme);
  updateThemeIcon(savedTheme);

  const themeBtns = document.querySelectorAll('.theme-toggle-btn');
  themeBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      const currentTheme = document.documentElement.getAttribute('data-theme');
      const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
      document.documentElement.setAttribute('data-theme', newTheme);
      localStorage.setItem('shrimp_theme', newTheme);
      updateThemeIcon(newTheme);
      showToast(`Switched to ${newTheme.toUpperCase()} mode`, 'info');
      
      // Update charts if they exist
      if (typeof window.renderAllCharts === 'function') {
        window.renderAllCharts();
      }
    });
  });
}

function updateThemeIcon(theme) {
  const icons = document.querySelectorAll('.theme-toggle-btn i');
  icons.forEach(icon => {
    if (theme === 'dark') {
      icon.className = 'fa-solid fa-sun text-warning';
    } else {
      icon.className = 'fa-solid fa-moon';
    }
  });
}

/* Sidebar Toggle for Desktop & Mobile */
function initSidebarToggle() {
  const toggleBtns = document.querySelectorAll('.sidebar-toggle-btn');
  toggleBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      if (window.innerWidth <= 991) {
        document.body.classList.toggle('mobile-sidebar-open');
      } else {
        document.body.classList.toggle('sidebar-collapsed');
        const isCollapsed = document.body.classList.contains('sidebar-collapsed');
        localStorage.setItem('sidebar_collapsed', isCollapsed ? 'true' : 'false');
      }
    });
  });

  // Restore collapsed state
  if (window.innerWidth > 991 && localStorage.getItem('sidebar_collapsed') === 'true') {
    document.body.classList.add('sidebar-collapsed');
  }
}

/* Highlight Active Navigation Link */
function highlightActiveNav() {
  const currentPath = window.location.pathname.split('/').pop() || 'dashboard.html';
  const navItems = document.querySelectorAll('.sidebar-nav .nav-item');
  
  navItems.forEach(item => {
    const href = item.getAttribute('href');
    if (href && href.includes(currentPath)) {
      item.classList.add('active');
    } else {
      item.classList.remove('active');
    }
  });
}

/* Notifications Popover Toggle */
function initNotificationsPopover() {
  const notifBtn = document.getElementById('notifBtn');
  const notifDropdown = document.getElementById('notifDropdown');

  if (notifBtn && notifDropdown) {
    notifBtn.addEventListener('click', (e) => {
      e.stopPropagation();
      notifDropdown.classList.toggle('show');
    });

    document.addEventListener('click', (e) => {
      if (!notifDropdown.contains(e.target) && !notifBtn.contains(e.target)) {
        notifDropdown.classList.remove('show');
      }
    });
  }
}

/* Toast Notification Utility */
function showToast(message, type = 'success') {
  let container = document.getElementById('toast-container');
  if (!container) {
    container = document.createElement('div');
    container.id = 'toast-container';
    document.body.appendChild(container);
  }

  const toast = document.createElement('div');
  toast.className = `toast-item ${type}`;

  let iconClass = 'fa-circle-check text-success';
  if (type === 'danger') iconClass = 'fa-circle-exclamation text-danger';
  if (type === 'warning') iconClass = 'fa-triangle-exclamation text-warning';
  if (type === 'info') iconClass = 'fa-circle-info text-info';

  toast.innerHTML = `
    <i class="fa-solid ${iconClass} fs-5"></i>
    <div class="flex-grow-1">
      <div class="fw-semibold text-capitalize">${type}</div>
      <div class="small text-muted">${message}</div>
    </div>
    <button type="button" class="btn-close ms-2" onclick="this.parentElement.remove()"></button>
  `;

  container.appendChild(toast);

  setTimeout(() => {
    toast.style.opacity = '0';
    toast.style.transform = 'translateY(10px)';
    toast.style.transition = 'all 0.3s ease';
    setTimeout(() => toast.remove(), 300);
  }, 4000);
}

/* Reusable Modal Helper */
function openModal(modalId) {
  const modal = document.getElementById(modalId);
  if (modal) {
    modal.classList.add('active');
  }
}

function closeModal(modalId) {
  const modal = document.getElementById(modalId);
  if (modal) {
    modal.classList.remove('active');
  }
}
