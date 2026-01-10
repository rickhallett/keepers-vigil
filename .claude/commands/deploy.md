# Deploy to Vercel

Deploy the frontend and/or backend to Vercel production.

## Usage

- `/deploy` - Deploy both frontend and backend
- `/deploy --frontend` - Deploy frontend only
- `/deploy --backend` - Deploy backend only
- `/deploy --frontend --backend` - Deploy both

## Arguments

$ARGUMENTS

## Instructions

Parse the arguments to determine what to deploy:
- If `--frontend` is present (or no arguments), deploy frontend
- If `--backend` is present (or no arguments), deploy backend

### Backend Deployment

```bash
cd /home/kai/code/repo/keepers-vigil/backend
vercel --prod --yes
```

- **Project**: team-diamond-9c4b1eca/backend
- **Production URL**: https://backend-six-chi-53.vercel.app
- **Config**: `backend/vercel.json` (Python/FastAPI)
- **Note**: The `builds` warning is expected and can be ignored

### Frontend Deployment

```bash
cd /home/kai/code/repo/keepers-vigil/frontend
vercel --prod --yes
```

- **Project**: team-diamond-9c4b1eca/frontend
- **Production URL**: https://frontend-sigma-gray-52.vercel.app
- **Framework**: Vite (auto-detected)
- **Environment**: `VITE_API_URL` points to backend

### CORS Configuration

If the frontend URL changes, update `backend/main.py` CORS origins:

```python
allow_origins=[
    ...
    "https://frontend-sigma-gray-52.vercel.app",  # Update this
]
```

Then redeploy the backend.

### Post-Deployment

After deployment, report the production URLs to the user:
- Backend: https://backend-six-chi-53.vercel.app
- Frontend: https://frontend-sigma-gray-52.vercel.app
