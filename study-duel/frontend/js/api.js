// Thin fetch wrapper. Holds the bearer token and turns every failure into a
// sentence a human can act on -- no raw status codes surfaced to the player.
import { apiBase } from "./config.js";

const TOKEN_KEY = "sd_token";
const NAME_KEY = "sd_name";

export const token = () => localStorage.getItem(TOKEN_KEY) || "";
export const player = () => localStorage.getItem(NAME_KEY) || "";

export function setSession(t, name) {
  localStorage.setItem(TOKEN_KEY, t);
  localStorage.setItem(NAME_KEY, name);
}

export function clearSession() {
  localStorage.removeItem(TOKEN_KEY);
  localStorage.removeItem(NAME_KEY);
}

async function request(path, { method = "GET", body, anon = false } = {}) {
  const headers = { "Content-Type": "application/json" };
  const t = token();
  if (t && !anon) headers.Authorization = "Bearer " + t;

  let res;
  try {
    res = await fetch(apiBase() + path, {
      method,
      headers,
      body: body === undefined ? undefined : JSON.stringify(body),
    });
  } catch {
    throw new Error(
      "Cannot reach the API. Check the address via the API button in the top right."
    );
  }

  if (res.status === 401) {
    clearSession();
    throw new Error("Not signed in, or your session ran out. Sign in again.");
  }

  if (!res.ok) {
    let detail = "";
    try {
      const data = await res.json();
      detail = typeof data.detail === "string" ? data.detail : "";
    } catch {
      /* non-JSON error body */
    }
    throw new Error(detail || `Request failed (${res.status})`);
  }

  if (res.status === 204) return null;
  return res.json();
}

export const api = {
  get: (path) => request(path),
  post: (path, body) => request(path, { method: "POST", body }),
  login: (name, passcode) =>
    request("/api/auth/login", { method: "POST", body: { name, passcode }, anon: true }),
};
