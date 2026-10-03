// Landing + sign-in. Only the two names in the USERS env var can get in.
import { api, setSession, token, player } from "./api.js";
import { apiBase, setApiBase } from "./config.js";
import { esc, renderNav, toast } from "./ui.js";

const form = () => document.getElementById("loginForm");

function paintSignedIn() {
  document.getElementById("signedOut").classList.add("hidden");
  document.getElementById("signedIn").classList.remove("hidden");
  document.getElementById("whoami").textContent = player();
}

async function boot() {
  renderNav("home");
  document.getElementById("apiShown").textContent = apiBase();

  if (token()) paintSignedIn();

  document.getElementById("apiSave").onclick = () => {
    const v = document.getElementById("apiInput").value;
    setApiBase(v);
    document.getElementById("apiShown").textContent = apiBase();
    toast("API address saved.", "ok");
  };

  form().addEventListener("submit", async (e) => {
    e.preventDefault();
    const name = document.getElementById("name").value.trim();
    const passcode = document.getElementById("passcode").value;
    const btn = document.getElementById("signInBtn");
    btn.disabled = true;
    btn.textContent = "Signing in...";
    try {
      const out = await api.login(name, passcode);
      setSession(out.token, out.name);
      const next = new URLSearchParams(location.search).get("next");
      location.href = next && !next.startsWith("//") ? next : "play.html";
    } catch (err) {
      toast(err.message, "lapse");
      btn.disabled = false;
      btn.textContent = "Sign in";
    }
  });
}

boot();
