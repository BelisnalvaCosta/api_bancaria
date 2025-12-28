// app.js — lógica do frontend com autenticação
const apiBase = '/api';

const $ = id => document.getElementById(id);

function getToken(){ return localStorage.getItem('token') }
function setToken(t){ if(t) localStorage.setItem('token', t); else localStorage.removeItem('token') }

async function fetchJSON(url, opts){
  const res = await fetch(url, opts);
  if (!res.ok){
    const t = await res.json().catch(()=>null);
    throw new Error(t?.detail || (await res.text()) || res.statusText);
  }
  return res.json();
}

async function authFetchJSON(url, opts = {}){
  opts.headers = opts.headers || {};
  const token = getToken();
  if(token) opts.headers['Authorization'] = 'Bearer ' + token;
  return fetchJSON(url, opts);
}

async function loadAccounts(){
  try{
    const accounts = await authFetchJSON(`${apiBase}/accounts`);
    const list = $('accounts-list');
    const sel = $('active-account');
    list.innerHTML = '';
    sel.innerHTML = '';
    accounts.forEach(a => {
      const li = document.createElement('li');
      li.innerHTML = `<div class="meta"><div class="name">${escapeHtml(a.owner)}</div><div class="balance">ID ${a.id} • Saldo: ${formatCurrency(a.balance)}</div></div><div class="controls"><button data-id="${a.id}" class="btn-select">Selecionar</button></div>`;
      list.appendChild(li);

      const opt = document.createElement('option');
      opt.value = a.id; opt.text = `${a.owner} (ID ${a.id})`;
      sel.appendChild(opt);
    });

    Array.from(document.getElementsByClassName('btn-select')).forEach(b => {
      b.onclick = e => { $('active-account').value = e.target.dataset.id; loadStatement(e.target.dataset.id); }
    });
  }catch(err){
    console.error(err); /* não dar alerta direto: pode ser token inválido */
  }
}

async function createAccount(){
  try{
    await authFetchJSON(`${apiBase}/accounts`, {method:'POST'});
    await loadAccounts();
  }catch(err){ alert('Erro: '+err.message) }
}

async function sendOperation(){
  const id = $('active-account').value;
  if(!id) return alert('Selecione uma conta');
  const type = $('op-type').value;
  const amount = parseFloat($('op-amount').value);
  if(!amount || amount <= 0) return alert('Valor inválido');
  const msg = $('op-msg');
  msg.textContent = 'Processando...';
  try{
    const res = await authFetchJSON(`${apiBase}/accounts/${id}/transactions`, {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({type, amount})});
    msg.textContent = 'Operação realizada com sucesso ✅';
    $('op-amount').value = '';
    await loadAccounts();
    await loadStatement(id);
    setTimeout(()=>msg.textContent='', 2500);
  }catch(err){ msg.textContent = 'Erro: '+err.message }
}

async function loadStatement(accountId){
  if(!accountId) return;
  try{
    const rows = await authFetchJSON(`${apiBase}/accounts/${accountId}/statement`);
    const body = $('statement-body');
    body.innerHTML = '';
    rows.forEach(r => {
      const tr = document.createElement('tr');
      tr.innerHTML = `<td>${r.type === 'deposit' ? 'Depósito' : 'Saque'}</td><td>${formatCurrency(r.amount)}</td><td>${formatDate(r.timestamp)}</td>`;
      body.appendChild(tr);
    });
  }catch(err){ console.error(err); const body = $('statement-body'); body.innerHTML = '<tr><td colspan="3" style="color:#999">Sem extrato ou erro ao carregar</td></tr>' }
}

async function login(){
  const username = $('login-username').value.trim();
  const password = $('login-password').value;
  if(!username || !password) return alert('Digite usuário e senha');
  try{
    const res = await fetchJSON(`${apiBase}/auth/login`, {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({username, password})});
    setToken(res.access_token);
    await updateAuthState();
  }catch(err){ alert('Erro: '+err.message) }
}

async function register(){
  const username = $('login-username').value.trim();
  const password = $('login-password').value;
  if(!username || !password) return alert('Digite usuário e senha');
  try{
    await fetchJSON(`${apiBase}/auth/register`, {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({username, password})});
    alert('Registrado com sucesso — agora faça login');
  }catch(err){ alert('Erro: '+err.message) }
}

async function logout(){
  setToken(null);
  await updateAuthState();
}

async function updateAuthState(){
  const token = getToken();
  const logged = $('logged');
  const loginForm = $('login-form');
  if(!token){
    loginForm.style.display = 'flex';
    logged.style.display = 'none';
    // limpar dados de painel
    $('accounts-list').innerHTML = '';
    $('active-account').innerHTML = '';
    $('statement-body').innerHTML = '';
  }else{
    try{
      const me = await authFetchJSON(`${apiBase}/me`);
      $('user-name').textContent = me.username;
      loginForm.style.display = 'none';
      logged.style.display = 'block';
      await loadAccounts();
      const sel = $('active-account');
      if(sel.value) loadStatement(sel.value);
    }catch(err){
      // token inválido
      setToken(null);
      loginForm.style.display = 'flex';
      logged.style.display = 'none';
    }
  }
}

function formatCurrency(v){
  return Number(v).toLocaleString('pt-BR', {style:'currency', currency:'BRL'});
}
function formatDate(iso){
  try{ const d = new Date(iso); return d.toLocaleString(); }catch(e){ return iso }
}
function escapeHtml(s){ return String(s).replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c])) }

// event listeners
document.addEventListener('DOMContentLoaded', async ()=>{
  $('btn-create-account').onclick = createAccount;
  $('btn-send-op').onclick = sendOperation;
  $('active-account').onchange = e => loadStatement(e.target.value);
  $('btn-login').onclick = login;
  $('btn-register').onclick = register;
  $('btn-logout').onclick = logout;
  await updateAuthState();
});
