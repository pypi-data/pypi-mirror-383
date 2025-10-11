from pathlib import Path

BASE_DIR = Path(__file__).parent.absolute()

SECRET_KEY = "secret"

DEBUG = True

INSTALLED_PACKAGES = [
    "plain.auth",
    "plain.sessions",
    "plainx.sentry",
]

MIDDLEWARE = [
    "plain.middleware.security.SecurityMiddleware",
    "plain.sessions.middleware.SessionMiddleware",
    "plain.middleware.common.CommonMiddleware",
    "plain.csrf.middleware.CsrfViewMiddleware",
    "plain.middleware.clickjacking.XFrameOptionsMiddleware",
    "plainx.sentry.middleware.SentryFeedbackMiddleware",
]

DATABASES = {
    "default": {
        "ENGINE": "plain.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

ROOT_URLCONF = "urls"

USE_TZ = True
