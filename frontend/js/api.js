// Shared API helpers for AquaControl frontend
// Same-origin when FastAPI serves the UI; otherwise point at local or production API.
const API_BASE = (() => {
  const { hostname, port, protocol } = window.location;
  const isLocalHost =
    hostname === "localhost" ||
    hostname === "127.0.0.1" ||
    hostname === "0.0.0.0" ||
    hostname === "::1" ||
    hostname.startsWith("192.168.") ||
    hostname.startsWith("10.") ||
    hostname.endsWith(".local") ||
    protocol === "file:" ||
    hostname === "";

  if (isLocalHost) {
    if (port === "8000") {
      return ""; // FastAPI serves pages + API — first-party cookies work
    }
    const host = (hostname === "localhost" || hostname === "127.0.0.1") ? hostname : "127.0.0.1";
    return `http://${host}:8000`; // Live Server / local dev server → local backend
  }
  return "https://acqacontrol.onrender.com"; // Deployed frontend (e.g. Vercel)
})();

function pageUrl(name) {
  // Relative links work for both :8000/pages/... and Live Server .../pages/...
  return String(name || "").replace(/^\/pages\//, "");
}

function loginPageUrl() {
  // FastAPI serves login at /; static hosts use ../index.html from pages/
  const { port, pathname } = window.location;
  if (port === "8000" || pathname === "/" || pathname === "/index.html") {
    return "/";
  }
  if (pathname.startsWith("/pages/")) {
    // Same host static deploy (e.g. Vercel) — root index is login
    return "/";
  }
  return pageUrl("../index.html");
}

const API = {
  async request(path, options = {}) {
    const { headers: extraHeaders, ...rest } = options;
    const opts = {
      credentials: "include",
      ...rest,
      headers: {
        "Content-Type": "application/json",
        ...(extraHeaders || {}),
      },
    };
    let res;
    try {
      res = await fetch(`${API_BASE}${path}`, opts);
    } catch {
      throw Object.assign(
        new Error("Server is not reachable"),
        { status: 0 }
      );
    }
    let data = null;
    const text = await res.text();
    try {
      data = text ? JSON.parse(text) : null;
    } catch {
      data = { detail: text || "Unexpected response" };
    }
    if (!res.ok) {
      const detail = data?.detail;
      const message = Array.isArray(detail)
        ? detail.map((d) => d.msg || JSON.stringify(d)).join(", ")
        : detail || "Request failed";
      const err = new Error(message);
      err.status = res.status;
      throw err;
    }
    return data;
  },

  get(path) {
    return this.request(path);
  },

  post(path, body) {
    return this.request(path, { method: "POST", body: JSON.stringify(body ?? {}) });
  },

  put(path, body) {
    return this.request(path, { method: "PUT", body: JSON.stringify(body ?? {}) });
  },

  delete(path) {
    return this.request(path, { method: "DELETE" });
  },
};

function todayISO() {
  return new Date().toISOString().slice(0, 10);
}

function showAlert(el, message, type = "danger") {
  if (!el) return;
  el.className = `alert alert-${type} py-2 small rounded-3 mb-3`;
  el.textContent = message;
  el.classList.remove("d-none");
}

function hideAlert(el) {
  if (!el) return;
  el.classList.add("d-none");
  el.textContent = "";
}

function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#39;");
}

async function requireAuth() {
  try {
    return await API.get("/api/auth/me");
  } catch (err) {
    if (err?.status === 0 || err?.message === "Server is not reachable") {
      const appEl = document.getElementById("app");
      if (appEl && typeof mountAppShell === "function") {
        mountAppShell("", `
          <div class="alert alert-danger shadow-sm rounded-3 p-4 my-4">
            <h5 class="fw-bold mb-2"><i class="fa-solid fa-triangle-exclamation me-2"></i>Server is not reachable</h5>
            <p class="mb-0 text-muted small">Could not connect to the backend API. Please verify that the server is running and try again.</p>
          </div>
        `);
      }
      return null;
    }
    window.location.href = loginPageUrl();
    return null;
  }
}

async function logout() {
  try {
    await API.post("/api/auth/logout", {});
  } catch (_) {
    /* ignore */
  }
  window.location.href = loginPageUrl();
}
