import os
from dotenv import load_dotenv

def verify():
    print("--- Setup Verification ---")
    
    # Check if .env.example exists
    if os.path.exists(".env.example"):
        print("[OK] .env.example exists.")
    else:
        print("[FAIL] .env.example missing.")

    # Check for venv
    if os.path.exists("venv"):
        print("[OK] Virtual environment (venv) exists.")
    else:
        print("[FAIL] Virtual environment (venv) missing.")

    # Check for agent.py
    if os.path.exists("agent.py"):
        print("[OK] agent.py exists.")
    else:
        print("[FAIL] agent.py missing.")

    # Check dependencies
    try:
        import groq
        import dotenv
        print("[OK] Dependencies (groq, python-dotenv) are installed.")
    except ImportError as e:
        print(f"[FAIL] Dependency missing: {e}")

    # Check .env
    load_dotenv()
    if os.getenv("GROQ_API_KEY"):
        print("[OK] GROQ_API_KEY found in .env.")
    else:
        print("[INFO] GROQ_API_KEY not found in .env (this is expected if you haven't added it yet).")

if __name__ == "__main__":
    verify()
