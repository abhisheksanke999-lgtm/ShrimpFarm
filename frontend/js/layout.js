// Shared sidebar + mobile menu (same UI as before, with mobile toggle)
function renderSidebar(active) {
  const items = [
    { key: "dashboard", href: "dashboard.html", icon: "fa-house", label: "Dashboard", color: "text-primary" },
    { key: "pond", href: "pond.html", icon: "fa-water", label: "Ponds", color: "text-primary" },
    { key: "seed", href: "seed-stocking.html", icon: "fa-seedling", label: "Seed Stocking", color: "text-success" },
    { key: "daily", href: "daily.html", icon: "fa-clipboard-list", label: "Daily Observation", color: "text-success" },
    { key: "feed", href: "feed.html", icon: "fa-wheat-awn", label: "Feed Records", color: "text-warning" },
    { key: "expense", href: "expense.html", icon: "fa-wallet", label: "Expense Records", color: "text-danger" },
    { key: "harvest", href: "harvest.html", icon: "fa-truck-ramp-box", label: "Harvest Records", color: "text-info" },
  ];

  const system = [
    { key: "reports", href: "reports.html", icon: "fa-file-pdf", label: "View Reports", color: "text-secondary" },
    { key: "settings", href: "settings.html", icon: "fa-gear", label: "Settings", color: "text-secondary" },
  ];

  const link = (item) => {
    const isActive = item.key === active;
    const cls = isActive
      ? "nav-link active bg-primary text-white rounded-3"
      : `nav-link text-dark rounded-3`;
    const iconCls = isActive ? "me-2" : `me-2 ${item.color}`;
    return `<a href="${item.href}" class="${cls}"><i class="fa-solid ${item.icon} ${iconCls}"></i> ${item.label}</a>`;
  };

  return `
  <aside class="sidebar bg-white border-end">
    <div class="p-3 border-bottom d-flex align-items-center justify-content-between gap-2">
      <div class="d-flex align-items-center gap-2">
        <div class="bg-primary text-white rounded-circle d-flex align-items-center justify-content-center" style="width: 38px; height: 38px;">
          <i class="fa-solid fa-shrimp"></i>
        </div>
        <div>
          <h6 class="fw-bold mb-0 text-primary">Aqua Farm</h6>
          <small class="text-muted">Record Management</small>
        </div>
      </div>
      <button type="button" class="btn btn-sm btn-outline-secondary d-lg-none" id="sidebarCloseBtn" aria-label="Close menu">
        <i class="fa-solid fa-xmark"></i>
      </button>
    </div>
    <div class="p-3">
      <div class="text-muted small fw-semibold mb-2">MAIN MENU</div>
      <div class="nav flex-column gap-1">
        ${items.map(link).join("")}
        <div class="text-muted small fw-semibold mt-4 mb-2">SYSTEM</div>
        ${system.map(link).join("")}
        <a href="#" id="logoutLink" class="nav-link text-danger rounded-3 mt-3 border border-danger-subtle bg-danger-subtle text-center">
          <i class="fa-solid fa-right-from-bracket me-2"></i> Logout
        </a>
      </div>
    </div>
  </aside>`;
}

function mountAppShell(activePage, mainHtml) {
  const root = document.getElementById("app");
  root.innerHTML = `
    <div class="mobile-topbar d-lg-none bg-white border-bottom px-3 py-2 d-flex align-items-center gap-2 sticky-top" style="z-index:110;">
      <button type="button" class="btn btn-sm btn-outline-primary" id="sidebarOpenBtn" aria-label="Open menu">
        <i class="fa-solid fa-bars"></i>
      </button>
      <strong class="text-primary">Aqua Farm</strong>
    </div>
    <div class="d-flex min-vh-100">
      ${renderSidebar(activePage)}
      <div class="sidebar-backdrop d-lg-none" id="sidebarBackdrop"></div>
      <main class="flex-grow-1 p-4">${mainHtml}</main>
    </div>
  `;

  document.getElementById("logoutLink")?.addEventListener("click", (e) => {
    e.preventDefault();
    logout();
  });

  const openBtn = document.getElementById("sidebarOpenBtn");
  const closeBtn = document.getElementById("sidebarCloseBtn");
  const backdrop = document.getElementById("sidebarBackdrop");

  const open = () => document.body.classList.add("mobile-sidebar-open");
  const close = () => document.body.classList.remove("mobile-sidebar-open");

  openBtn?.addEventListener("click", open);
  closeBtn?.addEventListener("click", close);
  backdrop?.addEventListener("click", close);
}
