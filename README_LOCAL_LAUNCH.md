# BorderSight / VeriLens AI — Local Launch Guide

Use this guide when returning to the project after a while.

> **Important:** Do not delete your only copy until you confirm your latest work is pushed to GitHub. A README cannot restore code that was never committed/pushed.

## 1. Repository

GitHub:
https://github.com/Roahith/hacktoberfest-hack-day-coimbatore-x-init-club-and-idea-club

The project has been called **BorderSight**; some backend responses/prompts still use **VeriLens AI**.

## 2. Clone the project again

If the folder is no longer on your PC:

```bash
cd ~
git clone https://github.com/Roahith/hacktoberfest-hack-day-coimbatore-x-init-club-and-idea-club.git
cd hacktoberfest-hack-day-coimbatore-x-init-club-and-idea-club
```

If it is already cloned:

```bash
cd ~/hacktoberfest-hack-day-coimbatore-x-init-club-and-idea-club
git pull
```

## 3. Create the Python environment

Linux:

```bash
cd ~/hacktoberfest-hack-day-coimbatore-x-init-club-and-idea-club
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
```

Install dependencies from whichever requirements files exist:

```bash
if [ -f requirements.txt ]; then pip install -r requirements.txt; fi
if [ -f backend/requirements.txt ]; then pip install -r backend/requirements.txt; fi
if [ -f p2_document_engine/requirements.txt ]; then pip install -r p2_document_engine/requirements.txt; fi
```

If no requirements file exists, inspect the repository's README and module requirements before installing packages manually.

## 4. Configure the Gemini API key

The Gemma 4 integration reads `GEMINI_API_KEY` from `.env` in the project root.

```bash
ls -la .env
```

If `.env` is missing, create it:

```bash
nano .env
```

Add your own valid key:

```dotenv
GEMINI_API_KEY=PASTE_YOUR_API_KEY_HERE
```

Save with **Ctrl+O**, Enter, then **Ctrl+X**. Never commit `.env` or share your API key. If you deleted the old `.env`, you must recreate it with a valid key.

## 5. Run the backend — Terminal 1

```bash
cd ~/hacktoberfest-hack-day-coimbatore-x-init-club-and-idea-club
source .venv/bin/activate
uvicorn backend.api:app --reload --host 127.0.0.1 --port 8000
```

Keep this terminal open.

- API root: http://127.0.0.1:8000/
- Health check: http://127.0.0.1:8000/health
- API docs: http://127.0.0.1:8000/docs

If you get `Address already in use`, another process is using port 8000. Stop the old backend process before starting another instance.

## 6. Run the frontend — Terminal 2

```bash
cd ~/hacktoberfest-hack-day-coimbatore-x-init-club-and-idea-club
python3 -m http.server 5500 --directory frontend
```

Open http://127.0.0.1:5500 and keep both terminals running.

**Important frontend note:** The static frontend has used relative API paths such as `/screen-document` and `/traveler/create`. Python's static server does not automatically proxy these paths to port 8000. If the page loads but API calls fail, check the frontend API base URL and configure it for `http://127.0.0.1:8000`, or use the intended frontend dev server/proxy if one has been added. Starting both servers does not by itself guarantee the frontend is connected to the backend.

## 7. Quick checks

In a third terminal:

```bash
cd ~/hacktoberfest-hack-day-coimbatore-x-init-club-and-idea-club
source .venv/bin/activate
python -m py_compile backend/api.py
curl http://127.0.0.1:8000/health
```

The previously observed health response was:

```json
{"status":"healthy"}
```

## 8. Project notes

- This is a **synthetic/demo** immigration pre-screening project. It does not connect to real government or INTERPOL databases.
- Automated results are decision-support signals; a human officer should make any final decision.
- The project has used OCR/MRZ extraction, synthetic passport/visa/security records, SFace biometric comparison, a deterministic risk engine, and Gemma 4 explanations.
- Check `data/`, `models/`, `test_documents/`, and biometric-reference folders before deleting anything important.
- Git does not preserve ignored files, `.env` secrets, local virtual environments, or untracked files. Recreate the environment and `.env` after cloning.
- If model files are missing after cloning, check the project instructions; large model files may not be stored in ordinary Git history.

## 9. Before deleting the current folder

From inside the project directory:

```bash
git status
git remote -v
git log -5 --oneline
git push
```

Review `git status`. If there are modified/untracked files you need, commit and push them first. Do not push secrets, `.env`, private data, or temporary files. Verify GitHub has the latest version before deleting the local folder.

## Fast launch summary

**Terminal 1 — backend**

```bash
cd ~/hacktoberfest-hack-day-coimbatore-x-init-club-and-idea-club
source .venv/bin/activate
uvicorn backend.api:app --reload --host 127.0.0.1 --port 8000
```

**Terminal 2 — frontend**

```bash
cd ~/hacktoberfest-hack-day-coimbatore-x-init-club-and-idea-club
python3 -m http.server 5500 --directory frontend
```

Then visit **http://127.0.0.1:5500**.
