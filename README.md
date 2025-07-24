# 🚀 FastAPI Project Setup Guide

This guide will help you get the FastAPI server up and running using [`uv`](https://github.com/astral-sh/uv), a modern Python package manager and runtime.

---

## 📦 Step 1: Install `uv`

If you don't already have `uv` installed, you can install it with one of the following methods:

### MacOS / Linux

```bash
curl -Ls https://astral.sh/uv/install.sh | bash
```

### Windows (PowerShell)

```powershell
irm https://astral.sh/uv/install.ps1 | iex
```

Alternatively, check out the [official uv installation docs](https://github.com/astral-sh/uv#installation) for more options.

---

## Step 2: Install Dependencies

Install the project dependencies using:

```bash
uv add -r requirements.txt
```

Run this command to sync and update/remove dependencies as indicated in both the `requirements.txt` and `pyproject.toml`

```bash
uv sync
```

This installs everything listed in `requirements.txt` and locks them using `uv.lock` for reproducibility.

---

## Step 3: 🔐 Configure Environment Variables

We use a `.env` file to manage configuration, like database URLs.

1. Go to **Supabase > Database > Connect**
  * ![Supabase Database Connect](app/img/supabase_database_connect.png)

2. In the modal that appears, look for the **Direct Connection** section at the top:
  * ![Supabase API Token](app/img/supabase_api_token_temp.png)

3. Use the `.env_example` file as a template to create your own `.env`. _Also mentioned in next step._
4. Set the `DATABASE_URL` environment variable using:

   - The **DB password**
   - The **hostname** shown under **Transaction Pooler**

---

## 🖥️ Step 4: Run the Server

### Start the Server

Start the FastAPI development server to run your server:

```bash
uv run uvicorn app.main:app --reload
```

> This will automatically create a `.venv` folder for your project if one doesn't already exist.

---

### Access the API

Once the server is running, open your browser and navigate to:

```
http://127.0.0.1:8000
```

Or hold `Cmd` (Mac) or `Ctrl` (Windows/Linux) and click the link in your terminal.

### Access the API Docs (Swagger UI)

Once the server is running, FastAPI auto-generates interactive API docs at:

- Swagger UI: [`http://127.0.0.1:8000/docs`](http://127.0.0.1:8000/docs)
- ReDoc: [`http://127.0.0.1:8000/redoc`](http://127.0.0.1:8000/redoc)

#### To test an endpoint:

1. Go to `/docs`
2. Scroll to the endpoint you want to test
3. Click on it to expand
4. Click the "Try it out" button on the right
5. Enter any required parameters
6. Click "Execute"
7. Scroll down to view the response from the server

_This is super helpful during development to verify everything is working as expected._

---

## 🔑 Step 5. 🔐 Authentication (Supabase JWT)

We are using **Supabase Auth** to handle user authentication for both customers and providers. When a user logs in via Google or any other provider, Supabase issues a JWT (JSON Web Token). This token is passed in the `Authorization` header and validated with credentials in the FastAPI backend.
We extract the user ID from this token to access data accordingly.

### ✅ Auth is Now Fully Functional
* Google login is enabled in the frontend via Supabase
* FastAPI validates Supabase issued JWTs for all authenticated users
* Data is scoped for the logged in user through their unique `user_id` through Supabase' `auth` schema

All user routes now work as expected. Some examples are listed below:
* `POST /customers`
* `GET /providers/me`

### 🔐 Supabase JWT Setup in FastAPI
To validate Supabase JWTs, the backend needs to know what key Supabase uses to sign tokens.
> Note that Legacy JWT tokens are no longer in use

We now use Supabase's public signing keys which are located in the Supabase project's **Project Settings** > API Keys

### 🔧 Required Env Vars for JWT (Specifically Backend)
An example is located in `.env.example`
```
SUPABASE_PUBLISHABLE_KEY=sb_publishable_...
SUPABASE_SECRET_KEY=sb_secret_...
SUPABASE_URL=https://<PROJECT_ID>.supabase.co
```

---

### 🧪 For Testing: Use [`/docs`](http://127.0.0.1:8000/docs)

To explore the API interactively, visit [`http://127.0.0.1:8000/docs`](http://127.0.0.1:8000/docs) once your server is running.

We recommend starting with the `/inventory_items` routes — they **do not require authentication** and are safe to test directly via Swagger UI.

On the Swagger UI page, expand the `inventory_items` section
![Swagger Inventory Items](app/img/swagger_inventory_items.png)

Swagger makes you work, so click **"Try it out"**
![Swagger Try it out button](app/img/swagger_try_it_out.png)

Select the gigantic **"Execute"** button
![Swagger Execute](app/img/swagger_execute.png)

You know it works if you are able to pull open the same information as what shows on the `inventory_items` table in Supabase!
![Swagger Inventory Items 200](app/img/swagger_inventory_items_200.png)

> Happy Swaggering!

---

### 🔧 Dev-Only Auth Workaround

To simulate a logged-in user during local development, we've hardcoded a static UUID as a placeholder:

```
# app/utils/auth.py

async def get_current_user() -> UUID:
  return UUID("3fa85f64-5717-4562-b3fc-2c963f66afa6")
```

---

## 🧱 Step 6. Database & Model Setup

We're using [Supabase](https://supabase.com/) (PostgreSQL) as our database.

- We define our database tables using `SQLModel`, a library that makes it easy to work with both Python data and SQL databases.
- Supabase hosts our Postgres database and helps manage performance behind the scenes.
- Settings like the database URL are stored in a `.env` file (as seen in the previous step).

## 🧪 [Optional] Seed the Database

To test your database connection or seed example data (e.g. into the `providers` table), you can run the following:

```
uv run test_db.py
```

### You're Ready!

You can now build and test your FastAPI backend locally. Happy coding!

![Corgi Butt](app/img/b1.png)

---

## 📐 Code Style & Formatting

This project uses:

* `black`: an opinionated code formatter
    *
* `ruff`: a fast Python linter & formatter
    * [Download the extension here](https://marketplace.visualstudio.com/items?itemName=charliermarsh.ruff)

These tools ensure consistent style, enforce line length according to international standards and help catch issues early.

### Format Your Code

To format the full codebase:

``` bash
uv run format-all
```

To lint the full codebase:
``` bash
uv run lint-all
```

You can also run the following to let Ruff clean up the mess... it's got a nose for bad code.
```bash
uv run safe-fix
```

To format or lint specific files or folders:
```
uv run black app/models/customer.py
uv run ruff check app/routers/ --fix
```

> Configuration is handled via `pyproject.toml`, `.editorconfig`, and `.vscode/settings.json`.

## VSCode Extension - A Ruff Setup
To enable real-time linting and formatting on save:
1. [Install the Ruff extension](https://marketplace.visualstudio.com/items?itemName=charliermarsh.ruff)
2. Open the `backend/` folder in VSCode
3. VSCode will use the included `.vscode/settings.json` which automatically:
    * Formats on save (`black`)
    * Sorts imports (`ruff`)
    * Lints on save(`ruff`)

> That's it! You're ready to code with consistent styling!

---

## 🧰 Dependency Management

### Add Dependencies

```
uv add dependency name
```

### Remove Dependencies

```
uv pip uninstall package-name
uv remove package-name
uv sync
```

---

## 🧯 Troubleshooting

### Can't connect to Supabase?

If you're seeing errors like:

```
psycopg2.OperationalError: could not translate host name ...
```

Make sure your internet connection isn't blocking access to Supabase's cloud database.

We've seen cases where **some Wi-Fi networks block or throttle access**, especially on public or secured networks. If you're stuck:

- Try switching to a mobile hotspot
- Check your firewall or DNS settings
- Make sure `.env` is loading the correct `DATABASE_URL` (i.e. print the string)
