# Credential and database cleanup

## Confirmed scope and provider status

The owner confirmed this application is retired on 21 October 2026. The owner deleted the exposed Gemini key from the dk-to-fo translation project, and Google Cloud confirmed the deletion. No replacement provider or Django signing credentials, deployment, or live database migration are needed for this retired application. Do not restore the exposed key. The instructions below apply only if an installation is revived.

This change removes credentials and runtime files from the proposed branch. Old commits and other branches still contain exposed material. Provider status is recorded above. Never reuse an exposed signing key in a future installation.

## If reviving or updating an existing installation

1. Identify the running host and branch. GitHub has no deployment records. Do not merge into an automatically deployed branch until the remaining steps are complete.
2. Stop writes and back up the live SQLite database to private storage outside the checkout. A pull that removes a tracked `db.sqlite3` can delete the deployed copy. Use the running service's actual database path, not a newly cloned database. Verify the backup with `PRAGMA integrity_check` and compare table counts locally. Do not publish database contents or backups.
3. Place a working database copy outside the checkout and configure `DJANGO_DB_PATH` to its absolute path. Preserve the original backup. Verify that the service account can read and write the database and parent directory. For example, while the service is stopped, use Python's SQLite backup API:

   ```python
   import sqlite3
   from pathlib import Path

   source = Path("db.sqlite3").resolve()  # Replace if the live database is elsewhere.
   target = Path("/private/path/outside-the-checkout/db.sqlite3")
   # Create and restrict the parent directory yourself. Refuse to overwrite a backup.
   if not source.is_file() or target.exists() or not target.parent.is_dir():
       raise RuntimeError("Check the live source and a new private destination first")
   with sqlite3.connect(source.as_uri() + "?mode=ro", uri=True) as original:
       with sqlite3.connect(target) as backup:
           original.backup(backup)
           assert backup.execute("PRAGMA integrity_check").fetchone()[0] == "ok"
   target.chmod(0o600)
   ```

4. Set a new, unique `DJANGO_SECRET_KEY` in the server environment. Generate it privately with `python -c "import secrets; print(secrets.token_urlsafe(64))"`. The application deliberately refuses to start with a missing or empty signing key. Replacing it invalidates existing signed sessions and reset links. Do not keep the exposed value in `SECRET_KEY_FALLBACKS`.
5. Set `GEMINI_API_KEY` to a replacement provider key and `DJANGO_ALLOWED_HOSTS` to the real host names, comma separated. Keep `DJANGO_DEBUG=false` on the live service. Export these variables in the shell or configure them in the hosting service. This application does not automatically load `.env`.
6. Deploy, restart, and verify login, existing records and a provider request in a controlled maintenance window. The exposed Gemini key has been deleted. Use a fresh key if restarting and review past provider usage privately.

## New local installation

Use a fresh virtual environment and install `requirements.txt`. Set a private `DJANGO_SECRET_KEY`, the provider key, `DJANGO_DEBUG=true`, and `DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1`. Export these variables in the shell or configure them in the hosting service. This application does not automatically load `.env`.

Run `python manage.py migrate` to create a clean local database, then `python manage.py createsuperuser` if administration is needed. Existing migrations are kept. Never use the old committed database as seed data. Do not overwrite a live database with an empty local one.

## Remaining exposure

The removed databases and provider/signing credentials remain recoverable from Git history, existing branches, clones and caches. This PR does not rewrite history, revoke keys, reset user passwords or change a live deployment. For the public scheduler database, treat account email addresses and password hashes as disclosed. Reset affected account passwords and invalidate sessions on any active installation. For the public translation database, treat stored document and translation content as disclosed. Review the exposure privately; do not copy it into an issue or PR.

## Validation

Five security configuration and mocked Gemini regression tests, Django system checks and a fresh migration against a disposable database passed with Django 5.2.3. No real Gemini request was made. The key-shaped credential was confirmed in the removed bytecode; the old source value was a placeholder.
