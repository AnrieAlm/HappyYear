// ===========================================================================
// Where the API lives.
//
// On localhost it defaults to the local FastAPI server. In production you must
// point it at your Render URL -- and you do NOT have to edit this file: the
// top-right "API" button stores the address in localStorage, so you can set it
// from the deployed site without a redeploy. Editing PROD_BASE below is just
// the tidier option.
// ===========================================================================

const PROD_BASE = "https://REPLACE-WITH-YOUR-SERVICE.onrender.com";

function defaultBase() {
  const host = location.hostname;
  if (host === "localhost" || host === "127.0.0.1" || host === "") {
    return "http://127.0.0.1:8000";
  }
  return PROD_BASE;
}

export function apiBase() {
  return (localStorage.getItem("sd_api") || defaultBase()).replace(/\/+$/, "");
}

export function setApiBase(url) {
  const clean = (url || "").trim().replace(/\/+$/, "");
  if (!clean) localStorage.removeItem("sd_api");
  else localStorage.setItem("sd_api", clean);
  return apiBase();
}
