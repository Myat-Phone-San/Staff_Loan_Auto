import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv(override=False)

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")


def print_instructions():
    print("\n=== Supabase DB Preparation Helper ===\n")
    if not SUPABASE_URL or not SUPABASE_KEY:
        print("Environment variables SUPABASE_URL and SUPABASE_KEY are not both set.")
        print("Set them locally or in Vercel before running this script.\n")
    else:
        print("Env vars found. Will attempt a quick read test against Supabase using the provided key.\n")

    sql_path = os.path.join(os.path.dirname(__file__), 'templates', 'test.sql')
    if os.path.exists(sql_path):
        print(f"You can apply the SQL schema in Supabase SQL editor. File: {sql_path}\n")
        print("--- Begin SQL (first 4000 chars) ---")
        with open(sql_path, 'r', encoding='utf-8') as fh:
            content = fh.read()
            print(content[:4000])
            if len(content) > 4000:
                print('\n... (truncated) ...')
        print("--- End SQL ---\n")
    else:
        print("No templates/test.sql found in the repo. Create tables manually from Supabase UI.\n")


def quick_test():
    if not SUPABASE_URL or not SUPABASE_KEY:
        print("Skipping quick Supabase test because env vars are missing.")
        return

    print("Attempting quick Supabase read test...")
    try:
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        # Try a minimal read; this will fail if table doesn't exist or RLS blocks the key
        resp = supabase.table('staff_loan_application').select('id').limit(1).execute()
        if resp.error:
            print("Supabase returned an error:", resp.error)
        else:
            print("Supabase read OK. Rows returned:", len(resp.data or []))
    except Exception as exc:
        print("Exception while contacting Supabase:", exc)


if __name__ == '__main__':
    print_instructions()
    quick_test()
