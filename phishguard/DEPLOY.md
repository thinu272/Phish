# Deploy PhishGuard free on Vercel (frontend + API in one project)

Result: `https://<your-project>.vercel.app`  (free Hobby plan, HTTPS included)

## Option A — GitHub + Vercel dashboard (easiest)
1. Create a free GitHub account, make a new repo, and push this folder:
   ```bash
   cd phishguard
   git init && git add . && git commit -m "PhishGuard"
   git branch -M main
   git remote add origin https://github.com/<you>/phishguard.git
   git push -u origin main
   ```
2. Go to https://vercel.com/signup (sign in with GitHub, choose Hobby / free).
3. **Add New → Project →** import the `phishguard` repo.
4. Leave everything as-is (settings come from `vercel.json`), click **Deploy**.
5. In ~1–2 min you get `https://phishguard-xxxx.vercel.app`.

## Option B — Vercel CLI
```bash
npm i -g vercel
cd phishguard
vercel login
vercel --prod
```

## Choose a nicer free domain
Vercel dashboard → your project → **Settings → Domains → Add** → type
`yourname-phishguard.vercel.app` (any free name that isn't taken) → Add.

## How it works
- `frontend/` is built by Vite to `frontend/dist` and served as static files.
- `api/index.py` runs the FastAPI app from `backend/` as a serverless function;
  `backend/data/*.csv` is bundled with it (`includeFiles` in `vercel.json`).
- `/api/*` is rewritten to that function; everything else serves the React app.

## Notes
- First request after idle takes a few seconds (cold start, loads the CSVs). Later ones are fast.
- Data is read-only on Vercel. To change data, regenerate/replace the CSVs locally, commit, push.
- Every `git push` auto-redeploys.
- Local dev is unchanged (see README.md).
