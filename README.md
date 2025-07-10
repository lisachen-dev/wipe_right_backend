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

## 🧪 Step 2: Create a Virtual Environment and Run the App

```bash
uv run main.py
```

> This will automatically create a `.venv` folder for your project if one doesn't already exist.

---

## 📥 Step 3: Install Dependencies

Install the project dependencies using:

```bash
uv add -r requirements.txt
```

This installs everything listed in `requirements.txt` and locks them using `uv.lock` for reproducibility.

---

## 🖥️ Step 4: Run the Server

Start the FastAPI development server with:

```bash
uv run uvicorn main:app --reload
```

---

## 🌐 Step 5: Access the API

Once the server is running, open your browser and navigate to:

```
http://127.0.0.1:8000
```

Or hold `Cmd` (Mac) or `Ctrl` (Windows/Linux) and click the link in your terminal.

---

## ✅ You're Ready!

You can now build and test your FastAPI backend locally. Happy coding!

## Notes

Adding a dependencies like so

```
uv add dependency name

```
