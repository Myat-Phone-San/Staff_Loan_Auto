# Staffloan Flask App

This repo contains a Flask app that integrates with Supabase for storing staff loan application data.

Quick deploy (Vercel):

1. Push this repo to GitHub.
2. In Vercel, create a new project and import the repository.
3. Add environment variables in the Vercel project settings:
   - `SUPABASE_URL` = your Supabase URL (e.g. `https://xxxx.supabase.co`)
   - `SUPABASE_KEY` = your Supabase anon or service_role key (service_role should NOT be used in client-side code)
4. Ensure `requirements.txt` includes `Flask`, `supabase`, and `python-dotenv`.
5. Deploy — the serverless entrypoint is `api/index.py` which imports `index.py`.

Local testing:

- Create a `.env` file with `SUPABASE_URL` and `SUPABASE_KEY` for local development (do not commit secrets).
- Run locally:

```bash
python -m venv .venv
.venv\Scripts\activate    # Windows
pip install -r requirements.txt
python -m flask run
```

Security notes:
- Use anon key with RLS policies for safe public access.
- Use service role key only in trusted server contexts and never expose it in browser JavaScript.
