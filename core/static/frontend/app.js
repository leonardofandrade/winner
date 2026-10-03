const PRICES = {
  15: "R$ 3,50",
  16: "R$ 56,00",
  17: "R$ 476,00",
  18: "R$ 2.856,00",
  19: "R$ 13.566,00",
  20: "R$ 54.264,00",
};

const state = {
  user: null,
  picked: new Set(),
  setName: "",
  suggestions: [],
  suggestSize: 15,
  suggestCount: 1,
};

const main = () => document.querySelector("#main");

function esc(value) {
  return String(value ?? "").replace(/[&<>"']/g, (char) => ({
    "&": "&amp;",
    "<": "&lt;",
    ">": "&gt;",
    '"': "&quot;",
    "'": "&#39;",
  }[char]));
}

function money(value) {
  if (value === null || value === undefined || value === "") return "—";
  const number = Number(value);
  if (Number.isNaN(number)) return esc(value);
  return number.toLocaleString("pt-BR", { style: "currency", currency: "BRL" });
}

function dateLabel(iso) {
  if (!iso) return "";
  const [year, month, day] = iso.slice(0, 10).split("-");
  return `${day}/${month}/${year}`;
}

function csrfToken() {
  const row = document.cookie.split("; ").find((part) => part.startsWith("csrftoken="));
  return row ? decodeURIComponent(row.split("=").slice(1).join("=")) : "";
}

function errorMessage(data) {
  if (!data) return "Não foi possível concluir.";
  if (typeof data.detail === "string") return data.detail;
  if (Array.isArray(data.detail)) return data.detail.join(" ");
  const lines = [];
  for (const [key, value] of Object.entries(data)) {
    const text = Array.isArray(value) ? value.join(" ") : String(value);
    lines.push(key === "non_field_errors" ? text : `${key}: ${text}`);
  }
  return lines.join(" ") || "Não foi possível concluir.";
}

async function api(path, options = {}) {
  const method = options.method || "GET";
  const headers = { Accept: "application/json" };
  if (options.body !== undefined) headers["Content-Type"] = "application/json";
  if (method !== "GET" && method !== "HEAD") headers["X-CSRFToken"] = csrfToken();
  const response = await fetch(path, {
    method,
    headers,
    credentials: "same-origin",
    body: options.body !== undefined ? JSON.stringify(options.body) : undefined,
  });
  if (response.status === 204) return null;
  const text = await response.text();
  let data = null;
  if (text) {
    try {
      data = JSON.parse(text);
    } catch {
      data = { detail: "Resposta inesperada do servidor." };
    }
  }
  if (!response.ok) {
    const error = new Error(errorMessage(data));
    error.status = response.status;
    throw error;
  }
  return data;
}

function toast(message) {
  const node = document.querySelector("#toast");
  node.hidden = false;
  node.textContent = message;
  clearTimeout(toast.timer);
  toast.timer = setTimeout(() => {
    node.hidden = true;
  }, 3200);
}

function go(hash) {
  if (location.hash === hash) return route();
  location.hash = hash;
  return Promise.resolve();
}

function locationState() {
  const raw = (location.hash || "#/concursos").replace(/^#/, "");
  const [path, query] = raw.split("?");
  return { parts: path.split("/").filter(Boolean), params: new URLSearchParams(query || "") };
}

function paintSession() {
  const slot = document.querySelector("#session");
  if (state.user) {
    slot.innerHTML = `<span class="muted">${esc(state.user.username)}</span><button type="button" class="ghost" data-action="logout">Sair</button>`;
  } else {
    slot.innerHTML = `<a href="#/entrar">Entrar</a>`;
  }
  const loc = locationState();
  const section = loc.parts[0] || "concursos";
  for (const link of document.querySelectorAll("[data-nav]")) {
    if (link.dataset.nav === section) link.setAttribute("aria-current", "page");
    else link.removeAttribute("aria-current");
  }
}

function balls(numbers, extra = "") {
  return `<div class="${extra || "mini-balls"}">${numbers.map((n) => `<span>${String(n).padStart(2, "0")}</span>`).join("")}</div>`;
}

function board(selected) {
  const cells = [];
  for (let number = 1; number <= 25; number += 1) {
    const on = selected.has(number) ? " on" : "";
    cells.push(`<span class="ball${on}">${String(number).padStart(2, "0")}</span>`);
  }
  return `<div class="balls">${cells.join("")}</div>`;
}

function picker() {
  const cells = [];
  for (let number = 1; number <= 25; number += 1) {
    const on = state.picked.has(number) ? " on" : "";
    cells.push(`<button type="button" class="${on.trim()}" data-action="toggle" data-number="${number}" aria-pressed="${state.picked.has(number)}">${number}</button>`);
  }
  return `<div class="picker" aria-label="Dezenas de 1 a 25">${cells.join("")}</div>`;
}

async function renderContests() {
  const page = locationState().params.get("page") || "1";
  const data = await api(`/api/contests/?page=${encodeURIComponent(page)}`);
  const latest = page === "1" ? data.results[0] : null;
  const hero = latest ? `
    <section class="hero">
      <div>
        <p class="muted">Último concurso</p>
        <h1>#${latest.number}</h1>
        <div class="meta">
          <span class="chip">${dateLabel(latest.draw_date)}</span>
          <span class="chip quiet">${latest.accumulated ? "Acumulou" : "Não acumulou"}</span>
          <span class="chip quiet">${money(latest.prize_pool)}</span>
        </div>
        <a class="primary" href="#/concursos/${latest.number}">Ver rateio</a>
      </div>
      ${board(new Set(latest.winning_numbers))}
    </section>` : "";
  const rows = data.results.map((contest) => `
    <a class="ticket" href="#/concursos/${contest.number}">
      <strong>#${contest.number}</strong>
      ${balls(contest.winning_numbers)}
      <span class="muted">${dateLabel(contest.draw_date)}</span>
    </a>`).join("");
  const prev = Number(page) > 1 ? `<a class="ghost" href="#/concursos?page=${Number(page) - 1}">Anterior</a>` : "";
  const next = data.next ? `<a class="ghost" href="#/concursos?page=${Number(page) + 1}">Próxima</a>` : "";
  main().innerHTML = `
    ${hero}
    <div class="row" style="justify-content:space-between;margin-bottom:12px">
      <h2>Histórico</h2>
      <form class="row" data-action="find">
        <input name="number" inputmode="numeric" placeholder="Número" aria-label="Número do concurso" required>
        <button class="ghost" type="submit">Abrir</button>
      </form>
    </div>
    <div class="list">${rows || `<p class="muted">Nenhum concurso importado.</p>`}</div>
    <div class="pager">${prev}${next}</div>`;
}

async function renderContest(number) {
  const contest = await api(`/api/contests/${number}/`);
  const tiers = contest.prize_tiers || {};
  const tierHtml = Object.keys(tiers)
    .sort((a, b) => Number(b) - Number(a))
    .map((hits) => `<span><strong>${hits} acertos</strong><br>${money(tiers[hits])}</span>`)
    .join("");
  main().innerHTML = `
    <p><a href="#/concursos">Concursos</a></p>
    <section class="hero">
      <div>
        <p class="muted">${dateLabel(contest.draw_date)}</p>
        <h1>#${contest.number}</h1>
        <div class="meta">
          <span class="chip">${contest.accumulated ? "Acumulou" : "Não acumulou"}</span>
          <span class="chip quiet">Arrecadação ${money(contest.prize_pool)}</span>
        </div>
        <form class="row" data-action="import-one">
          <input name="number" inputmode="numeric" placeholder="Outro número" aria-label="Importar concurso">
          <button class="ghost" type="submit">Importar da Caixa</button>
          <button class="primary" type="button" data-action="import-latest">Atualizar o último</button>
        </form>
      </div>
      ${board(new Set(contest.winning_numbers))}
    </section>
    <section class="panel">
      <h2>Rateio</h2>
      <div class="tiers">${tierHtml || `<p class="muted">Este concurso não tem rateio gravado.</p>`}</div>
    </section>`;
}

function gameForm() {
  return `
    <section class="panel stack">
      <h2>Novo jogo</h2>
      <p class="muted" data-picked-count>${state.picked.size} dezena(s) selecionada(s). Escolha de 15 a 20.</p>
      ${picker()}
      <form class="row" data-action="save-game">
        <label>Apelido do conjunto
          <input name="set_name" value="${esc(state.setName)}" placeholder="bolão da firma" maxlength="40">
        </label>
        <button class="primary" type="submit">Salvar</button>
      </form>
    </section>`;
}

async function renderGames() {
  if (!state.user) {
    main().innerHTML = `<section class="panel"><h1>Seus jogos</h1><p class="lede">Entre com o usuário do Winner para cadastrar jogos e calcular os acertos.</p><a class="primary" href="#/entrar">Entrar</a></section>`;
    return;
  }
  const data = await api("/api/games/");
  const groups = new Map();
  for (const game of data.results) {
    const key = game.set_name || "";
    if (!groups.has(key)) groups.set(key, []);
    groups.get(key).push(game);
  }
  const cards = [...groups.entries()].map(([name, games]) => `
    <section class="stack">
      <h2>${name ? esc(name) : "Sem apelido"}</h2>
      ${games.map((game) => `
        <article class="game-card stack">
          <div class="row" style="justify-content:space-between">
            <strong>Jogo #${game.id}</strong>
            <span class="muted">${game.numbers.length} dezenas</span>
          </div>
          ${balls(game.numbers)}
          <div class="actions">
            <button type="button" class="primary" data-action="calculate" data-id="${game.id}">Calcular acertos</button>
            <button type="button" class="danger" data-action="delete" data-id="${game.id}">Apagar</button>
          </div>
          <div id="results-${game.id}"></div>
        </article>`).join("")}
    </section>`).join("");
  main().innerHTML = `
    <h1>Jogos</h1>
    <p class="lede">Cada conjunto leva um apelido. O cálculo compara o jogo com o histórico importado.</p>
    ${gameForm()}
    <div class="stack" style="margin-top:22px">${cards || `<p class="muted">Nenhum jogo salvo.</p>`}</div>`;
}

async function renderSuggestions() {
  const cards = state.suggestions.map((numbers, index) => `
    <article class="game-card stack">
      <strong>Sugestão ${index + 1}</strong>
      ${balls(numbers)}
      <p class="muted">${PRICES[numbers.length] || ""}</p>
      <button type="button" class="primary" data-action="keep" data-index="${index}">Salvar nos meus jogos</button>
    </article>`).join("");
  main().innerHTML = `
    <h1>Sugestões</h1>
    <p class="lede">Sorteio ponderado pela frequência dos últimos 100 concursos. Um jogo de 15 dezenas que já saiu é descartado.</p>
    <form class="panel row" data-action="suggest">
      <label>Dezenas
        <select name="size">${[15, 16, 17, 18, 19, 20].map((size) => `<option value="${size}" ${size === state.suggestSize ? "selected" : ""}>${size} · ${PRICES[size]}</option>`).join("")}</select>
      </label>
      <label>Quantidade
        <select name="count">${[1, 2, 3, 4, 5, 6, 7, 8, 9, 10].map((count) => `<option value="${count}" ${count === state.suggestCount ? "selected" : ""}>${count}</option>`).join("")}</select>
      </label>
      <button class="primary" type="submit">Gerar</button>
    </form>
    <div class="stack" style="margin-top:16px">${cards}</div>`;
}

function renderLogin() {
  main().innerHTML = `
    <section class="panel stack" style="max-width:420px">
      <h1>Entrar</h1>
      <p class="muted">Use o mesmo usuário criado no Winner.</p>
      <form class="stack" data-action="login">
        <label>Usuário<input name="username" autocomplete="username" required></label>
        <label>Senha<input name="password" type="password" autocomplete="current-password" required></label>
        <button class="primary" type="submit">Entrar</button>
      </form>
    </section>`;
}

async function route() {
  paintSession();
  const { parts } = locationState();
  const section = parts[0] || "concursos";
  main().innerHTML = `<p class="muted">Carregando…</p>`;
  try {
    if (section === "entrar") renderLogin();
    else if (section === "jogos") await renderGames();
    else if (section === "sugestoes") await renderSuggestions();
    else if (section === "concursos" && parts[1]) await renderContest(parts[1]);
    else await renderContests();
  } catch (error) {
    main().innerHTML = `<p class="error">${esc(error.message)}</p>`;
  }
  paintSession();
}

async function showResults(gameId, page = 1) {
  const data = await api(`/api/games/${gameId}/results/?page=${page}`);
  const slot = document.querySelector(`#results-${gameId}`);
  if (!slot) return;
  const rows = data.results.map((result) => {
    const strong = result.hits >= 11 ? "chip" : "chip quiet";
    return `<span class="${strong}">#${result.contest_number} · ${result.hits} · ${money(result.prize)}</span>`;
  }).join("");
  const prev = page > 1 ? `<button type="button" class="ghost" data-action="results" data-id="${gameId}" data-page="${page - 1}">Anterior</button>` : "";
  const next = data.next ? `<button type="button" class="ghost" data-action="results" data-id="${gameId}" data-page="${page + 1}">Próxima</button>` : "";
  slot.innerHTML = `<div class="meta">${rows || `<span class="muted">Sem acertos calculados.</span>`}</div><div class="pager">${prev}${next}</div>`;
}

document.addEventListener("click", async (event) => {
  const button = event.target.closest("[data-action]");
  if (!button || button.type === "submit") return;
  const action = button.dataset.action;
  try {
    if (action === "logout") {
      await api("/api/auth/logout/", { method: "POST" });
      state.user = null;
      await go("#/concursos");
    } else if (action === "import-latest") {
      button.disabled = true;
      const contest = await api("/api/contests/import/", { method: "POST", body: {} });
      toast(`Concurso #${contest.number} atualizado.`);
      await go(`#/concursos/${contest.number}`);
    } else if (action === "toggle") {
      const number = Number(button.dataset.number);
      if (state.picked.has(number)) state.picked.delete(number);
      else if (state.picked.size < 20) state.picked.add(number);
      else {
        toast("Um jogo tem no máximo 20 dezenas.");
        return;
      }
      button.classList.toggle("on", state.picked.has(number));
      button.setAttribute("aria-pressed", String(state.picked.has(number)));
      const count = document.querySelector("[data-picked-count]");
      if (count) count.textContent = `${state.picked.size} dezena(s) selecionada(s). Escolha de 15 a 20.`;
      const input = document.querySelector('input[name="set_name"]');
      if (input) state.setName = input.value;
    } else if (action === "calculate") {
      button.disabled = true;
      button.textContent = "Calculando…";
      const summary = await api(`/api/games/${button.dataset.id}/calculate/`, { method: "POST", body: {} });
      toast(`${summary.calculated} concursos comparados.`);
      await showResults(button.dataset.id);
      button.disabled = false;
      button.textContent = "Calcular acertos";
    } else if (action === "results") {
      await showResults(button.dataset.id, Number(button.dataset.page));
    } else if (action === "delete") {
      if (!confirm("Apagar este jogo?")) return;
      await api(`/api/games/${button.dataset.id}/`, { method: "DELETE" });
      toast("Jogo apagado.");
      await renderGames();
    } else if (action === "keep") {
      if (!state.user) {
        location.hash = "#/entrar";
        return;
      }
      const numbers = state.suggestions[Number(button.dataset.index)];
      await api("/api/games/", { method: "POST", body: { numbers, set_name: "Sugestões" } });
      toast("Sugestão salva no conjunto Sugestões.");
    }
  } catch (error) {
    toast(error.message);
    button.disabled = false;
  }
});

document.addEventListener("submit", async (event) => {
  const form = event.target.closest("form[data-action]");
  if (!form) return;
  event.preventDefault();
  const action = form.dataset.action;
  const body = Object.fromEntries(new FormData(form).entries());
  try {
    if (action === "find" || action === "import-one") {
      const number = String(body.number || "").trim();
      if (action === "find") {
        await go(`#/concursos/${number}`);
        return;
      }
      const contest = await api("/api/contests/import/", { method: "POST", body: { number: Number(number) } });
      toast(`Concurso #${contest.number} importado.`);
      await go(`#/concursos/${contest.number}`);
    } else if (action === "login") {
      state.user = await api("/api/auth/login/", { method: "POST", body });
      toast(`Olá, ${state.user.username}.`);
      await go("#/jogos");
    } else if (action === "save-game") {
      state.setName = String(body.set_name || "");
      const numbers = [...state.picked].sort((a, b) => a - b);
      await api("/api/games/", { method: "POST", body: { numbers, set_name: state.setName } });
      state.picked = new Set();
      toast("Jogo salvo.");
      await renderGames();
    } else if (action === "suggest") {
      state.suggestSize = Number(body.size);
      state.suggestCount = Number(body.count);
      const data = await api("/api/suggestions/", {
        method: "POST",
        body: { size: state.suggestSize, count: state.suggestCount },
      });
      state.suggestions = data.games;
      await renderSuggestions();
    }
  } catch (error) {
    toast(error.message);
  }
});

window.addEventListener("hashchange", () => { route(); });

api("/api/auth/me/")
  .then((user) => { state.user = user; })
  .catch(() => { state.user = null; })
  .finally(() => { route(); });
