// Relative path works because main.py serves this frontend and the API from
// the same FastAPI app/port. Always open the app via the server URL
// (e.g. http://localhost:8000) — never by double-clicking the HTML file.
const API_BASE = "/api";

const Auth = {
  getToken() { return localStorage.getItem("cc_token"); },
  setToken(t) { localStorage.setItem("cc_token", t); },
  getUser() {
    const raw = localStorage.getItem("cc_user");
    return raw ? JSON.parse(raw) : null;
  },
  setUser(u) { localStorage.setItem("cc_user", JSON.stringify(u)); },
  clear() {
    localStorage.removeItem("cc_token");
    localStorage.removeItem("cc_user");
  },
  isLoggedIn() { return !!this.getToken(); },
};

// FastAPI returns `detail` as a string for our own errors, but as an ARRAY of
// objects for request-validation errors (422). Turn either shape into readable
// text so the UI never shows "[object Object]".
function errorMessageFrom(detail) {
  if (!detail) return "Something went wrong";
  if (typeof detail === "string") return detail;
  if (Array.isArray(detail)) {
    return detail.map((d) => {
      if (typeof d === "string") return d;
      const field = Array.isArray(d.loc) ? d.loc[d.loc.length - 1] : "";
      const msg = (d.msg || "Invalid value").replace(/^Value error, /, "");
      return field && field !== "body" ? `${field}: ${msg}` : msg;
    }).join("; ");
  }
  if (typeof detail === "object") return detail.msg || detail.message || JSON.stringify(detail);
  return String(detail);
}

async function apiRequest(path, { method = "GET", body = null, auth = true, isForm = false } = {}) {
  const headers = {};
  if (!isForm) headers["Content-Type"] = "application/json";
  if (auth && Auth.getToken()) headers["Authorization"] = `Bearer ${Auth.getToken()}`;

  let res;
  try {
    res = await fetch(`${API_BASE}${path}`, {
      method,
      headers,
      body: isForm ? body : (body ? JSON.stringify(body) : null),
    });
  } catch (networkErr) {
    throw new Error("Can't reach the CivicCare server. Make sure the backend is running and you opened this page through its URL (e.g. http://localhost:8000), not as a local file.");
  }

  const data = await res.json().catch(() => ({}));

  // A 401 on a PROTECTED call means the session expired -> back to login.
  // A 401 on login/register (auth:false) just means wrong credentials, so it
  // must fall through and be shown inline instead of reloading the page.
  if (res.status === 401 && auth) {
    Auth.clear();
    window.location.href = "/";
    throw new Error("Session expired. Please log in again.");
  }

  if (!res.ok) throw new Error(errorMessageFrom(data.detail));
  return data;
}

function requireRole(roles) {
  const user = Auth.getUser();
  if (!Auth.isLoggedIn() || !user || !roles.includes(user.role)) window.location.href = "/";
  return user;
}

// Confirms the stored token against the server (GET /api/auth/me).
async function validateSession(roles) {
  try {
    const me = await apiRequest("/auth/me");
    if (!me || !roles.includes(me.role)) {
      Auth.clear();
      window.location.href = "/";
      return null;
    }
    Auth.setUser(me);
    return me;
  } catch (e) {
    Auth.clear();
    window.location.href = "/";
    return null;
  }
}

// Category list shared by every page. Names MUST match backend ComplaintCategory
// values exactly; priority mirrors backend CATEGORY_PRIORITY_MAP (display only —
// the server decides the real priority).
const CATEGORY_INFO = [
  { name: "Electricity",          priority: "High",   examples: "Power cuts, transformer faults, fallen or sparking wires" },
  { name: "Water Supply",         priority: "High",   examples: "No supply, contaminated water, pipeline leaks" },
  { name: "Public Safety",        priority: "High",   examples: "Open manholes, unsafe structures, hazards to the public" },
  { name: "Road / Pothole",       priority: "Medium", examples: "Potholes, damaged roads, broken footpaths" },
  { name: "Garbage / Sanitation", priority: "Medium", examples: "Uncollected waste, overflowing bins, illegal dumping" },
  { name: "Sewage / Drainage",    priority: "Medium", examples: "Blocked drains, sewage overflow, stagnant water" },
  { name: "Streetlight",          priority: "Low",    examples: "Lights not working, flickering or always on" },
  { name: "Noise Pollution",      priority: "Low",    examples: "Loud construction, events or machinery" },
  { name: "Others",               priority: "Low",    examples: "Any civic issue that is not listed above" },
];

function priorityBadgeClass(priority) {
  switch (priority) {
    case "High": return "bg-[#FCE8E8] text-[#A31F22] border-[#E8B4B4]";
    case "Medium": return "bg-[#FDF3D6] text-[#8A6A00] border-[#F0D889]";
    case "Low": return "bg-[#EAF3EA] text-[#2F6B2F] border-[#BFDCC0]";
    default: return "bg-stone-100 text-stone-700 border-stone-300";
  }
}

function priorityDotClass(priority) {
  return { High: "bg-[#C62828]", Medium: "bg-[#F2B705]", Low: "bg-[#2F8F4E]" }[priority] || "bg-stone-400";
}

function statusBadgeClass(status) {
  switch (status) {
    case "Submitted": return "bg-stone-100 text-stone-700";
    case "Verified": return "bg-[#FDF3D6] text-[#8A6A00]";
    case "Assigned": return "bg-[#F6E4C6] text-[#7A4E00]";
    case "In Progress": return "bg-[#F2B705]/20 text-[#8A6A00]";
    case "Resolved": return "bg-[#EAF3EA] text-[#2F6B2F]";
    case "Rejected": return "bg-[#FCE8E8] text-[#A31F22]";
    case "Closed": return "bg-stone-200 text-stone-600";
    default: return "bg-stone-100 text-stone-700";
  }
}

function formatDate(iso) {
  if (!iso) return "-";
  return new Date(iso).toLocaleString(undefined, { dateStyle: "medium", timeStyle: "short" });
}
