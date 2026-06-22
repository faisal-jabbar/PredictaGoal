"""
Script 01 — Environment Check.
Verifies Python version, required packages, directory structure, and env configuration.
"""
import sys
import os

# Allow imports from project root
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.utils.logger import get_logger

log = get_logger("01_check_environment")


def check_python_version():
    major, minor = sys.version_info[:2]
    status = "OK" if (major == 3 and minor >= 9) else "WARNING (Python 3.9+ recommended)"
    print(f"  Python version : {sys.version.split()[0]}  [{status}]")


def check_packages():
    packages = {
        "pandas": "pandas",
        "numpy": "numpy",
        "sklearn": "scikit-learn",
        "joblib": "joblib",
        "dotenv": "python-dotenv",
        "firebase_admin": "firebase-admin",
        "kagglehub": "kagglehub",
    }
    all_ok = True
    for module, pkg in packages.items():
        try:
            __import__(module)
            print(f"  {pkg:<25} OK")
        except ImportError:
            print(f"  {pkg:<25} MISSING  (pip install {pkg})")
            all_ok = False

    # Optional
    try:
        import xgboost
        print(f"  {'xgboost':<25} OK (optional)")
    except ImportError:
        print(f"  {'xgboost':<25} not installed (optional)")

    return all_ok


def check_directories():
    from src.config import settings
    dirs = {
        "data/raw": settings.DATA_RAW_DIR,
        "data/processed": settings.DATA_PROCESSED_DIR,
        "data/reports": settings.DATA_REPORTS_DIR,
        "models/artifacts": settings.MODELS_ARTIFACTS_DIR,
        "models/reports": settings.MODELS_REPORTS_DIR,
        "logs": settings.LOGS_DIR,
    }
    for label, path in dirs.items():
        exists = os.path.isdir(path)
        print(f"  {label:<25} {'OK' if exists else 'MISSING (will be created)'}")
        if not exists:
            os.makedirs(path, exist_ok=True)


def check_env_file():
    from src.config import settings
    root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    env_path = os.path.join(root, ".env")
    env_example_path = os.path.join(root, ".env.example")

    print(f"  .env file      : {'Found' if os.path.isfile(env_path) else 'NOT found (copy .env.example to .env and fill credentials)'}")
    print(f"  .env.example   : {'Found' if os.path.isfile(env_example_path) else 'NOT found'}")

    fb_ok = settings.firebase_credentials_available()
    sa_path = settings.FIREBASE_SERVICE_ACCOUNT_PATH
    if sa_path:
        sa_status = "Found" if os.path.isfile(sa_path) else f"NOT found at: {sa_path}"
        print(f"  Firebase SA    : {sa_status}")
    print(f"  Firebase creds : {'Configured' if fb_ok else 'NOT configured (local fallback will be used)'}")

    kaggle_ok = settings.kaggle_token_available()
    print(f"  Kaggle token   : {'Detected' if kaggle_ok else 'NOT set (set KAGGLE_API_TOKEN in .env)'}")


def main():
    print("\n" + "=" * 60)
    print("  ENVIRONMENT CHECK — AI Football Match Prediction Agent")
    print("=" * 60)

    print("\n[1] Python Version")
    check_python_version()

    print("\n[2] Required Packages")
    all_ok = check_packages()

    print("\n[3] Project Directories")
    check_directories()

    print("\n[4] Configuration")
    check_env_file()

    print("\n" + "=" * 60)
    if all_ok:
        print("  Result: Environment ready. Proceed to script 02.")
    else:
        print("  Result: Some packages are missing. Run: pip install -r requirements.txt")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()
