# User‑Management API Microservice

A lightweight Flask + PostgreSQL micro‑service that supports full user lifecycle management, JWT authentication, and runs entirely in Docker.  
This README shows you how to **spin it up**, **exercise every endpoint from Postman (no cURL)**, and **rebuild the stack with one click** using the provided **`rebuild‑api.bat`** script.

---

## Features
| Area | Highlights |
|------|------------|
| **Auth** | `/login` issues a **JWT (HS256)** &mdash; all `/users` routes require a `Bearer` token |
| **CRUD** | Create, list, search (by name substring or e‑mail), update, delete users |
| **DB** | Auto‑creates tables on first run, keeps ID sequence aligned after deletes |
| **Logging** | Color‑coded Loguru output, plus a separate “API logs” window when using the batch script |
| **Dev workflow** | One‑shot `rebuild‑api.bat` → stop, rebuild (no‑cache), start, and tail logs in a new console |

---

## Prerequisites
* **Docker Desktop** (Windows/macOS) ‑ *or* Docker Engine + docker‑compose plugin (Linux)
* **Postman** (≥ v10)

---

## First‑run

```bash
# in the project root (where docker-compose.yml lives)
docker compose up -d        # pulls Postgres image, builds the API, starts both
```

*Wait until the API container logs “*Database schema ready ✅*”.*  
Health check: browse to **<http://localhost:5000/health>** → `{"status":"ok"}`.

---

## Authenticating in Postman

1. **Create a new request**  
   * **Method:** `POST`  
   * **URL:** `http://localhost:5000/login`
2. **Body → raw → JSON**  
   ```json
   {
     "username": "admin",
     "password": "admin123"
   }
   ```
3. **Send** – the response contains  
   ```json
   { "access_token": "<long‑jwt‑string>" }
   ```
4. **Save the token for later requests**         *(two common ways)*  

   | Option | How |
   |--------|-----|
   | **Bearer Token auth tab (per request)** | Open the **Authorization** tab → **TYPE = Bearer Token** → paste token |
   | **Environment / collection variable** *(preferred)* | Create variable `TOKEN` = *the JWT*.<br>Then set **Authorization** to **Bearer Token** and use `{{TOKEN}}`.<br>All requests inside the collection inherit it automatically. |

---

## Endpoint cheat‑sheet (ready for Postman)

> Replace `{{TOKEN}}` with the variable or paste directly in the **Authorization** tab.

| Purpose | Method & URL | Body → raw JSON (where required) |
|---------|--------------|----------------------------------|
| **Login (get token)** | `POST` `/login` | `{ "username":"admin", "password":"admin123" }` |
| **Create user** | `POST` `/users` | `{ "name":"Kartheek", "email":"kartheek@example.com" }` |
| **List all users** | `GET` `/users` | *(none)* |
| **Find by **name substring** | `GET` `/users/name/<namePart>` | *(none)* |
| **Find by **e‑mail** | `GET` `/users/email/<email>` | *(none)* |
| **Get by ID** | `GET` `/users/<id>` | *(none)* |
| **Update** | `PUT` `/users/<id>` | `{"name":"Kartheek Mukkavilli"}` *(any subset of fields)* |
| **Delete** | `DELETE` `/users/<id>` | *(none)* |

**Headers needed on every `/users*` request**

```
Authorization: Bearer {{TOKEN}}
Content-Type: application/json        # only for POST/PUT bodies
```

---

## Fast rebuild loop ‑ `rebuild‑api.bat`

```bat
@echo off
REM 1) stop containers          2) rebuild api image (no‑cache)
REM 3) start stack detached     4) open new window & tail logs
docker compose down || goto :err
docker compose build --no-cache api || goto :err
docker compose up -d || goto :err
start "API logs" cmd /k "docker compose logs -f api"
echo Done! Press any key to close this window.
pause >nul
exit /b
:err
echo Something went wrong – check the message above.
pause
```

### How it works
| Step | What happens |
|------|--------------|
| **down** | Gracefully stops and removes existing containers (frees file locks) |
| **build --no-cache api** | Forces a fresh image build so code/requirements changes are guaranteed to apply |
| **up -d** | Relaunches Postgres + API containers in detached mode |
| **start … logs -f api** | Spawns a **new console window** titled “API logs” that streams colored Loguru output; your original terminal is free immediately |

#### Running the script
* Double‑click **`rebuild‑api.bat`** in Explorer **or** from a terminal:  
  ```cmd
  C:\path\to\project> rebuild-api
  ```
* Watch the separate *API logs* window for “*Running on http://0.0.0.0:5000*”, then hit Postman.

---

## Customisation tips

| Change | Where |
|--------|-------|
| Admin login credentials | `.env` or `docker-compose.yml` → `ADMIN_USER`, `ADMIN_PASSWORD` |
| JWT secret / expiry | `JWT_SECRET`, `JWT_TTL_MIN` env vars |
| DB connection string | `DATABASE_URL` env var (default points at the bundled Postgres service) |
| Add more tables/fields | Extend **`models.py`** → rebuild → tables auto‑migrate (simple apps) |
| Swagger docs | `pip install flasgger` then `Swagger(app)` → browse `/apidocs` |

---

## Troubleshooting

* **“parent snapshot does not exist” during build** → run  
  ```bash
  docker builder prune -af   # clears corrupted BuildKit cache
  ```  
  then re‑run `rebuild-api.bat`.
* **401 Unauthorized** → ensure you pasted the token into the request’s **Bearer Token** field and it hasn’t expired (default TTL = 60 min).