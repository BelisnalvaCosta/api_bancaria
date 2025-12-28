# Banco Digital (Projeto de Exemplo)

Uma pequena aplicação de banco digital criada com FastAPI (backend) e uma interface frontend estática simples. Este projeto é pensado para iniciantes: mostra como criar contas, fazer depósitos/saques, visualizar extratos e autenticar usuários com JWT.

---

## 📋 O que tem no projeto

- Backend em `app/` usando FastAPI e SQLAlchemy (banco SQLite assimilado via `aiosqlite`).
- Frontend estático em `frontend/` com `index.html`, `styles.css` e `app.js` (HTML + CSS + JS puro).
- Funcionalidades básicas: registro/login, criação de conta (por usuário), depósitos, saques e extrato.

---

## ✅ Requisitos

- Python 3.8+ instalado
- (Windows) PowerShell ou CMD para rodar comandos

---

## 🚀 Como rodar (modo rápido)

1. Clone o repositório ou abra a pasta local.
2. Instale dependências (num terminal/cmd/powershell):

```powershell
pip install -r requirements.txt
```

3. Inicie a aplicação:

```powershell
uvicorn app.main:app --reload
```

4. Abra no navegador:

- Interface web: `http://127.0.0.1:8000/`
- Documentação automática (OpenAPI): `http://127.0.0.1:8000/docs`

---

## 🧭 Uso (passo a passo para iniciantes)

1. Acesse `http://127.0.0.1:8000/`.
2. Na área de login, registre um usuário (botão **Registrar**) usando um nome de usuário e uma senha simples (apenas para testes).
3. Faça login com o usuário criado (senha pode ser simples durante testes).
4. Clique em **Criar Conta** para criar uma conta vinculada ao usuário.
5. Selecione a conta criada e faça depósitos ou saques na seção **Operação**.
6. Verifique o extrato na tabela **Extrato** — ele será recarregado automaticamente após operações.

> Nota: o frontend armazena o token (JWT) no `localStorage` e o envia automaticamente nas requisições protegidas.

---

## 🔌 Endpoints principais (exemplos com `curl`)

- Registrar:

```bash
curl -X POST "http://127.0.0.1:8000/api/auth/register" -H "Content-Type: application/json" -d '{"username":"alice","password":"1234"}'
```

- Login (retorna `access_token`):

```bash
curl -X POST "http://127.0.0.1:8000/api/auth/login" -H "Content-Type: application/json" -d '{"username":"alice","password":"1234"}'
```

- Criar conta (protegido):

```bash
curl -X POST "http://127.0.0.1:8000/api/accounts" -H "Authorization: Bearer <TOKEN>"
```

- Listar contas do usuário (protegido):

```bash
curl -X GET "http://127.0.0.1:8000/api/accounts" -H "Authorization: Bearer <TOKEN>"
```

- Criar transação (depósito/saque):

```bash
curl -X POST "http://127.0.0.1:8000/api/accounts/1/transactions" -H "Authorization: Bearer <TOKEN>" -H "Content-Type: application/json" -d '{"type":"deposit", "amount":100.0}'
```

- Extrato:

```bash
curl -X GET "http://127.0.0.1:8000/api/accounts/1/statement" -H "Authorization: Bearer <TOKEN>"
```

> Substitua `<TOKEN>` pelo token retornado no login.

---

## ⚠️ Avisos de segurança (simples e claros)

- Este projeto é um exemplo didático. **Não use** as configurações (ex.: `SECRET_KEY` embutida no código) em produção.
- As senhas são armazenadas como hash (bcrypt) para demonstrar prática correta, mas o fluxo de autenticação e políticas de segurança são minimalistas propositalmente.

---

## 🛠 Estrutura do projeto (onde encontrar as coisas)

- `app/` — código do backend
  - `main.py` — configuração do FastAPI, servindo frontend em `/`
  - `routes.py` — rotas da API (contas, transações, auth)
  - `models.py` — modelos do banco (Account, Transaction, User)
  - `auth.py` — funções de hashing e JWT
  - `schemas.py` — modelos pydantic
- `frontend/` — arquivos estáticos servidos pelo backend
  - `index.html`, `styles.css`, `app.js`

---

## Como contribuir (bem simples)

- Abra uma issue no GitHub com o que deseja melhorar ou corrigir.
- Faça um fork, crie uma branch com sua feature, e abra um Pull Request.