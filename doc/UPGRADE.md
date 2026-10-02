# Upgrade Guide: `develop` → `feature/modernize-otm`

This document describes what changed on `feature/modernize-otm` relative to
`develop`, and the steps required to update an existing Ubuntu host (and your
local dev environment) to run the modernized application. The target OS for
this upgrade is **Ubuntu 26.04 LTS**, upgraded from the current
22.04.2 LTS.

> **Note:** the exact default package versions shipped in Ubuntu 26.04's
> repos (Python, PostgreSQL, etc.) are not verified in this document. The
> commands below pin to known-compatible versions via the PGDG, deadsnakes,
> and NodeSource apt repos so the result is consistent regardless of what
> 26.04 ships by default — confirm versions with `apt-cache policy <pkg>` on
> your actual host before relying on distro defaults.

## Summary of what changed

| Area | Before (`develop`) | After (`feature/modernize-otm`) |
|---|---|---|
| Python | 2.7 / early 3.x shims | 3.11 / 3.12 |
| Django | 1.11 | 4.2 (LTS) |
| Postgres driver | `psycopg2==2.7.3.2` | `psycopg[binary]>=3.2.0` (with a `psycopg2` compatibility shim) |
| Database | PostgreSQL + PostGIS (older) | PostgreSQL 18 + PostGIS 3 |
| Map tiles | Windshaft/`otm-tiler` raster tiles | `pg_tileserv`/`martin` vector tiles (legacy backend still supported) |
| Node/JS build | Webpack 1, node-sass, old loaders | Webpack 5, `sass` (Dart Sass), updated loaders, Node 24 |
| CI | Travis CI + `.github/workflows/django.yml` | GitHub Actions `.github/workflows/ci.yml` only |
| Misc | — | `on_delete` added to all `ForeignKey`s, `GeoManager` → `Manager`, `django.conf.urls.url` → `django.urls.re_path`, `is_authenticated()` → `is_authenticated`, removed `python_2_unicode_compatible` |

Key new/removed files:
- Added `opentreemap/psycopg2.py` / `opentreemap/psycopg2/__init__.py` — shim so code that still does `import psycopg2` transparently loads either the real `psycopg2` package or falls back to `psycopg` (v3).
- Added `opentreemap/sitecustomize.py` — Python startup customizations needed for the Django 4 / Python 3.11+ environment.
- Added `scripts/check_django_python_compatibility.py` — static checker for common Django 4 / Python 3.10+ incompatibilities (collections.abc moves, missing `on_delete`, removed `GeoManager`, deprecated imports). Not required at runtime, but useful to re-run if you have custom/forked code to port.
- Removed `.travis.yml`, `.github/workflows/django.yml`, `travis-requirements.txt` — CI now lives entirely in `.github/workflows/ci.yml`.
- `TILE_BACKEND` / `TILE_HOST` settings added (`opentreemap/opentreemap/settings/default_settings.py`) to select between `pg_tileserv` (new default) and `legacy` tiling.

---

## 1. OS release upgrade path (22.04.2 → 26.04)

Ubuntu does not support skipping LTS releases when using `do-release-upgrade`
— you must hop through each intermediate LTS:

```bash
# From 22.04.2:
sudo apt-get update && sudo apt-get upgrade -y
sudo apt-get install -y update-manager-core
sudo do-release-upgrade   # 22.04 -> 24.04

# Reboot, confirm `lsb_release -a` reports 24.04, then:
sudo do-release-upgrade   # 24.04 -> 26.04

# Reboot, confirm `lsb_release -a` reports 26.04
```

Alternatively, provision new 26.04 hosts/images directly rather than
in-place upgrading — this avoids leftover config from the old release and is
generally the safer option for production database servers. See §2 for the
fresh-host approach, including how to migrate data from the old 22.04 host.

Back up the database and any local settings before starting an in-place OS
upgrade (see §4 for DB-specific backup steps).

## 2. Fresh-host migration path (recommended)

Rather than upgrading production hosts in place, stand up new Ubuntu 26.04
hosts and migrate data across. This is safer (the old host is untouched and
serves as a rollback target until cutover is confirmed) and avoids any
leftover 22.04/24.04 package cruft.

### 2.1 Provision the new hosts

Create two new **Ubuntu 26.04 LTS** hosts (or reuse one host for both roles
in small deployments):

- **db-26** — new PostgreSQL 18 + PostGIS 3 server.
- **app-26** — new application host (Django app, Celery worker, ecoservice,
  tile service, nginx).

This is a from-scratch install, so unlike an in-place upgrade there is no
existing `otm` user, repo checkout, or config to build on — §2.2/§2.3 below
list every package needed, replacing the equivalents from the old
[installation-guide.md](wiki/installation-guide.md) (written for Ubuntu
14.04/18.04) with their modern replacements. Notably:

| Old guide (14.04/18.04) | Modern replacement (26.04) | Why |
|---|---|---|
| `python-setuptools`, `python-pip`, `python-dev` | `python3.12`, `python3.12-venv`, `python3.12-dev` | Python 2 is gone; app now requires 3.11/3.12 |
| `libgdal1-dev` | `libgdal-dev`, `gdal-bin` | package renamed/versioned upward with GDAL itself |
| `postgresql-9.3`, `postgresql-9.3-postgis-2.1` | `postgresql-18`, `postgresql-18-postgis-3` (via PGDG, §3) | matches the Postgres 18/PostGIS 3 stack used in CI |
| `nodejs` 6.x PPA | NodeSource Node **24** (§3) | Webpack 5 / current tooling requires a modern Node |
| `otm-tiler` (Windshaft/Mapnik, `libcairo2-dev`/`libpango1.0-dev`/node-canvas build deps) | `pg_tileserv`/`martin` vector tiles (§2.3.3) | default `TILE_BACKEND` is now `pg_tileserv`; the old raster tiler is optional/legacy only |
| `otm-ecoservice` built with Go 1.2 + `godep`/`GOPATH`/`mercurial` | Go 1.22+ with native Go modules (§2.3.2) | `godep`/`GOPATH` workflow is obsolete; modern Go modules don't need Mercurial |
| `upstart` scripts in `/etc/init` | `systemd` unit files (§2.3.5) | Ubuntu has shipped systemd (not upstart) as its init system since 15.04 |
| local `sendmail` package | SMTP relay (e.g. Postfix configured as a relay, or an external provider) via Django's `EMAIL_BACKEND`/`EMAIL_HOST` | plain local `sendmail` is unreliable/commonly blocked by cloud providers; `sendmail` is kept only as the local binary Django's SMTP backend can still shell out to if you prefer that route |

### 2.2 db-26: install PostgreSQL + PostGIS

```bash
sudo apt-get update
sudo apt-get install -y --no-install-recommends \
  ca-certificates curl gnupg lsb-release software-properties-common

curl -fsSL https://www.postgresql.org/media/keys/ACCC4CF8.asc | sudo gpg --dearmor -o /etc/apt/trusted.gpg.d/postgresql.gpg
echo "deb http://apt.postgresql.org/pub/repos/apt $(lsb_release -cs)-pgdg main" | sudo tee /etc/apt/sources.list.d/pgdg.list
sudo apt-get update

sudo DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
  postgresql-18 postgresql-client-18 postgresql-18-postgis-3 postgresql-18-postgis-3-scripts postgis
```

Create the database, role, and extensions (modern equivalent of the old
guide's `CREATE USER`/`CREATE DATABASE` step — note `hstore`/`postgis` are
created in the app database itself rather than `template1`, and
`fuzzystrmatch` is no longer required):

```bash
sudo -u postgres psql -c "CREATE USER otm WITH ENCRYPTED PASSWORD 'pick_a_strong_password'"
sudo -u postgres psql -c "CREATE DATABASE otm OWNER otm"
sudo -u postgres psql -d otm -c "CREATE EXTENSION IF NOT EXISTS postgis"
sudo -u postgres psql -d otm -c "CREATE EXTENSION IF NOT EXISTS hstore"
```

Open `pg_hba.conf`/`postgresql.conf` to accept TCP connections from
`app-26`'s address, then restart PostgreSQL. Do **not** run
`manage.py migrate` yet if you're migrating data in from an old host —
schema + data will arrive via the restore in §2.4.

### 2.3 app-26: install all required packages

#### 2.3.1 Base OS packages

```bash
sudo apt-get update
sudo apt-get install -y --no-install-recommends \
  ca-certificates curl gnupg lsb-release software-properties-common git \
  build-essential gettext \
  libffi-dev libssl-dev libldap2-dev libxml2-dev libxslt1-dev \
  libfreetype6-dev libjpeg-dev zlib1g-dev \
  gdal-bin libgdal-dev libgeos-dev libproj-dev libpq-dev \
  redis-server nginx
```

(Run `redis-server` on a separate host instead if you're splitting Celery's
broker out — `redis-server` here matches the Redis 7 used in CI.)

#### 2.3.2 Python 3.12, Node 24, and the app itself

```bash
# Python 3.12 (see §3 for repo setup)
sudo add-apt-repository -y ppa:deadsnakes/ppa
sudo apt-get update
sudo apt-get install -y python3.12 python3.12-venv python3.12-dev

# Node 24 (see §3 for repo setup)
curl -fsSL https://deb.nodesource.com/setup_24.x | sudo -E bash -
sudo apt-get install -y nodejs
corepack enable   # provides yarn, replacing the old `npm install -g yarn`

sudo mkdir -p /usr/local/otm
sudo chown "$USER" /usr/local/otm
cd /usr/local/otm
git clone https://github.com/cwardcode/otm-core.git app
cd app
git checkout feature/modernize-otm

python3.12 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
# Development/test host only:
pip install -r dev-requirements.txt -r test-requirements.txt

yarn install
```

Create `opentreemap/opentreemap/settings/local_settings.py` — same shape as
the old guide, plus the new `TILE_BACKEND`/`TILE_HOST` settings:

```python
STATIC_ROOT = '/usr/local/otm/static'
MEDIA_ROOT = '/usr/local/otm/media'

DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': 'otm',
        'USER': 'otm',
        'PASSWORD': 'pick_a_strong_password',
        'HOST': 'db-26',          # or the db host's private IP/hostname
        'PORT': '5432',
        'OPTIONS': {'sslmode': 'prefer'},
    }
}

CELERY_BROKER_URL = 'redis://localhost:6379/'
CELERY_RESULT_BACKEND = 'redis://localhost:6379/'

# Point this at an SMTP relay instead of relying on local `sendmail`
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'localhost'
EMAIL_PORT = 25

# Vector tile backend (replaces the old otm-tiler/Windshaft setup)
TILE_BACKEND = 'pg_tileserv'
TILE_HOST = 'http://localhost:7800'

DEBUG = False
ALLOWED_HOSTS = ['.example.com']  # substitute your domain name
```

```bash
mkdir -p /usr/local/otm/static /usr/local/otm/media
python opentreemap/manage.py collectstatic_js_reverse
npm run build
python opentreemap/manage.py collectstatic --noinput --clear
```

Skip `manage.py migrate`/`create_system_user` here if you're restoring an
existing database (§2.4 handles schema/data); run them as usual for a
brand-new, empty database.

#### 2.3.3 Tile backend: `pg_tileserv` (replaces `otm-tiler`)

The Windshaft-based `otm-tiler` from the old guide is **obsoleted** as the
default tile backend. Install `pg_tileserv` (or `martin`) on `app-26` (or its
own host) instead, pointed at `db-26`:

```bash
curl -L -o pg_tileserv.zip \
  https://postgisftw.s3.amazonaws.com/pg_tileserv_latest_linux.zip
sudo unzip pg_tileserv.zip -d /usr/local/pg_tileserv
sudo useradd --system --no-create-home pg_tileserv
```

Configure it (e.g. `/usr/local/pg_tileserv/config.toml`) with a
`DATABASE_URL` pointing at `db-26`'s `otm` database, then run it as a
systemd service (§2.3.5) listening on `7800`, matching `TILE_HOST` above.

Only install the legacy `otm-tiler` (Node/Windshaft, requiring
`libcairo2-dev`/`libpango1.0-dev`/`libgif-dev`/node-canvas build deps) if you
need `TILE_BACKEND=legacy` for compatibility — it is no longer the
recommended path.

#### 2.3.4 `otm-ecoservice` (Go)

Still required for ecosystem-benefit calculations. Modern Go uses Go
modules, so the old `GOPATH`/`godep`/Mercurial workflow is no longer needed:

```bash
curl -LO https://go.dev/dl/go1.22.6.linux-amd64.tar.gz
sudo tar -C /usr/local -xzf go1.22.6.linux-amd64.tar.gz
export PATH="$PATH:/usr/local/go/bin"

sudo apt-get install -y libgeos-dev

git clone https://github.com/cwardcode/otm-ecoservice.git /usr/local/otm/ecoservice
cd /usr/local/otm/ecoservice
git checkout feature/modernize-otm
go build ./...
```

(If this repo hasn't been migrated to Go modules yet, run `go mod init` /
`go mod tidy` once to generate `go.mod`/`go.sum` instead of using `godep`.)

> **Troubleshooting:** `go build ./...` failing with
> `module ./Godeps/_workspace/src/github.com/lib/pq: reading
> Godeps/_workspace/src/github.com/lib/pq/go.mod: ... no such file or
> directory` means a `go.mod` already exists in the repo with leftover
> `replace` directives pointing at the old `Godeps/_workspace/src/...`
> vendor paths — those directories are plain GOPATH-style vendoring and
> don't contain their own `go.mod`, which modern Go's module resolver
> requires for a local `replace` target. Fix it by dropping the Godeps
> vendoring in favor of real module dependencies:
>
> ```bash
> cd /usr/local/otm/ecoservice
>
> # Inspect go.mod for `replace ... => ./Godeps/...` lines and drop them
> grep -n "Godeps" go.mod
> go mod edit -dropreplace=github.com/lib/pq
> go mod edit -dropreplace=github.com/ungerik/go-rest
>
> # If go.mod doesn't exist yet, create one first:
> # go mod init github.com/OpenTreeMap/otm-ecoservice
>
> # Fetch the real modules from the proxy and resolve a go.sum
> go mod tidy
>
> # Once the build succeeds, the vendored copies are no longer needed
> rm -rf Godeps
>
> go build ./...
> ```
>
> If `github.com/ungerik/go-rest` fails to resolve (the upstream repo is
> largely unmaintained), pin a tagged commit explicitly
> (`go get github.com/ungerik/go-rest@<commit-sha>`) or point a `replace`
> directive at a maintained fork instead of the Godeps copy.

#### 2.3.5 systemd units (replaces `/etc/init` upstart scripts)

Ubuntu has used `systemd`, not `upstart`, as its init system since 15.04, so
the old guide's upstart `.conf` files no longer apply regardless of OS
version. Define each service as a systemd unit under
`/etc/systemd/system/`, for example `otm-gunicorn.service`:

```ini
[Unit]
Description=OpenTreeMap gunicorn
After=network.target

[Service]
User=otm
WorkingDirectory=/usr/local/otm/app/opentreemap
Environment="DJANGO_SETTINGS_MODULE=opentreemap.settings"
ExecStart=/usr/local/otm/app/.venv/bin/gunicorn opentreemap.wsgi:application --bind 127.0.0.1:8000
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

`otm-celery.service` (Celery worker for async tasks):

```ini
[Unit]
Description=OpenTreeMap Celery worker
After=network.target redis-server.service

[Service]
User=otm
WorkingDirectory=/usr/local/otm/app/opentreemap
Environment="DJANGO_SETTINGS_MODULE=opentreemap.settings"
ExecStart=/usr/local/otm/app/.venv/bin/python -m celery -A opentreemap worker --loglevel=info
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

> **Troubleshooting:** running the `celery` console script directly (e.g.
> `.venv/bin/celery -A opentreemap worker`) can fail with
> `Error: Unable to load celery application. The module opentreemap was not
> found.` even when run from the correct directory. Pip-installed
> console-script entry points (`celery`, `gunicorn`'s script form, etc.) set
> `sys.path[0]` to the script's own `bin/` directory, not the current
> working directory, so the `opentreemap` package next to `manage.py` never
> gets found. Invoking it as `python -m celery ...` (as above) fixes this,
> because `-m` adds the current directory to `sys.path`. Alternatively, set
> `Environment="PYTHONPATH=/usr/local/otm/app/opentreemap"` on the unit and
> keep using the `celery` binary directly.
>
> Fixing that can surface a second error:
> `ImportError: cannot import name 'smart_text' from
> 'django.utils.encoding'` (raised while importing the unmaintained
> `django-tagging` package). `opentreemap/sitecustomize.py` already shims
> `smart_text`/`smart_str`/`force_text`, but it only runs automatically when
> Python's `site` module finds it on `sys.path` at interpreter startup —
> which happens for `manage.py` (script-directory insertion) but not
> reliably for `celery`/`gunicorn`/other console-script entry points.
> `opentreemap/opentreemap/settings/__init__.py` now imports it explicitly
> (`import sitecustomize`) so the shim is applied regardless of entry
> point; make sure you're running code from this branch rather than an
> older checkout if you still hit this error.

`otm-ecoservice.service` (Go ecosystem-benefits service, built in §2.3.4):

```ini
[Unit]
Description=OpenTreeMap ecoservice
After=network.target

[Service]
User=otm
WorkingDirectory=/usr/local/otm/ecoservice
ExecStart=/usr/local/otm/ecoservice/otm-ecoservice
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

`pg_tileserv.service` (vector tile backend, installed in §2.3.3):

```ini
[Unit]
Description=pg_tileserv vector tile service
After=network.target

[Service]
User=pg_tileserv
WorkingDirectory=/usr/local/pg_tileserv
Environment="DATABASE_URL=postgresql://otm:pick_a_strong_password@db-26:5432/otm"
ExecStart=/usr/local/pg_tileserv/pg_tileserv --config /usr/local/pg_tileserv/config.toml
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

Enable and start all of them:

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now otm-gunicorn otm-celery otm-ecoservice pg_tileserv redis-server nginx
```

Check status/logs for any unit with `systemctl status <unit>` and
`journalctl -u <unit> -f`.

#### 2.3.6 nginx

Use a standard `sites-available`/`sites-enabled` layout and proxy to the
systemd services configured above.

1. Create nginx include directories used by the site config:

```bash
sudo mkdir -p /etc/nginx/includes/upstreams /etc/nginx/includes/locations
```

2. Define upstreams (`/etc/nginx/includes/upstreams/*.conf`):

`/etc/nginx/includes/upstreams/app.conf`

```nginx
upstream otm_app {
  server 127.0.0.1:8000;
  keepalive 32;
}
```

`/etc/nginx/includes/upstreams/tiles.conf`

```nginx
upstream otm_tiles {
  server 127.0.0.1:7800;
  keepalive 32;
}
```

`/etc/nginx/includes/upstreams/ecoservice.conf` (optional, only if you expose
ecoservice behind nginx)

```nginx
upstream otm_ecoservice {
  server 127.0.0.1:9001;
  keepalive 16;
}
```

3. Create the main site file at `/etc/nginx/sites-available/otm.conf`:

```nginx
include /etc/nginx/includes/upstreams/*.conf;

server {
  listen 80;
  server_name _;  # replace with your domain in production

  client_max_body_size 20m;

  proxy_set_header Host $host;
  proxy_set_header X-Real-IP $remote_addr;
  proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
  proxy_set_header X-Forwarded-Proto $scheme;

  # Static assets collected by Django
  location /static/ {
    alias /usr/local/otm/static/;
    access_log off;
    expires 7d;
  }

  # User uploads
  location /media/ {
    alias /usr/local/otm/media/;
    access_log off;
    expires 1d;
  }

  # pg_tileserv endpoint
  location /tiles/ {
    proxy_pass http://otm_tiles/;
    proxy_http_version 1.1;
  }

  # Optional: expose ecoservice under /ecoservice/
  # location /ecoservice/ {
  #   proxy_pass http://otm_ecoservice/;
  #   proxy_http_version 1.1;
  # }

  # Main Django app (gunicorn)
  location / {
    proxy_pass http://otm_app;
    proxy_http_version 1.1;
  }
}
```

4. Enable the site and reload nginx:

```bash
sudo rm -f /etc/nginx/sites-enabled/default
sudo ln -sf /etc/nginx/sites-available/otm.conf /etc/nginx/sites-enabled/otm.conf
sudo nginx -t
sudo systemctl restart nginx
```

5. Verify routing:

```bash
curl -I http://127.0.0.1/
curl -I http://127.0.0.1/static/
curl -I http://127.0.0.1/tiles/
```

If nginx fails while manual service commands work, check service-specific
logs with `journalctl -u <service>` and nginx logs at
`/var/log/nginx/error.log`.

When using this nginx layout, set `TILE_HOST` in
`opentreemap/opentreemap/settings/local_settings.py` to the externally
reachable nginx path (for example `https://maps.example.org/tiles`) rather
than the internal `http://localhost:7800` service address.

### 2.4 Migrate the database from the old host to db-26

On the **old 22.04 host**, take a fresh logical dump (use `-Fc` so you get
`pg_restore`'s parallelism and selective-restore options):

```bash
pg_dump -Fc -h localhost -U postgres -d <dbname> -f otm_migration.dump
```

Copy the dump to the new database host:

```bash
scp otm_migration.dump user@db-26:/tmp/
```

On **db-26**, create the database/extensions (if not already done in §2.2)
and restore:

```bash
sudo -u postgres createdb -O postgres <dbname>
sudo -u postgres psql -d <dbname> -c "CREATE EXTENSION IF NOT EXISTS postgis;"
sudo -u postgres psql -d <dbname> -c "CREATE EXTENSION IF NOT EXISTS hstore;"

sudo -u postgres pg_restore -d <dbname> --no-owner --no-privileges -j 4 /tmp/otm_migration.dump
```

Because `--no-owner --no-privileges` deliberately drops the dump's original
ownership/grants, every restored table/sequence ends up owned by the role
that ran `pg_restore` (`postgres` above) with no privileges granted to your
app's database role (`otm`). You must grant them explicitly, or Django/the
ecoservice will fail at runtime with errors like
`pq: permission denied for table treemap_itreecodeoverride`:

```bash
sudo -u postgres psql -d <dbname> <<'SQL'
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO otm;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO otm;
GRANT ALL PRIVILEGES ON ALL FUNCTIONS IN SCHEMA public TO otm;
-- so future migrations' tables/sequences inherit the same grants
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL PRIVILEGES ON TABLES TO otm;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL PRIVILEGES ON SEQUENCES TO otm;
SQL
```

For Django migrations, grants are not enough by themselves. `ALTER TABLE`
operations require ownership of the target table/sequence, so you must also
transfer object ownership to the app role you run migrations as (for example
`otm`), or you'll hit errors like `must be owner of table auth_group`:

```bash
sudo -u postgres psql -d <dbname> <<'SQL'
ALTER DATABASE <dbname> OWNER TO otm;
ALTER SCHEMA public OWNER TO otm;

DO $$
DECLARE obj record;
BEGIN
  FOR obj IN
    SELECT 'TABLE' AS kind, tablename AS name FROM pg_tables WHERE schemaname = 'public'
    UNION ALL
    SELECT 'SEQUENCE' AS kind, sequencename AS name FROM pg_sequences WHERE schemaname = 'public'
    UNION ALL
    SELECT 'VIEW' AS kind, viewname AS name FROM pg_views WHERE schemaname = 'public'
  LOOP
    EXECUTE format('ALTER %s public.%I OWNER TO otm', obj.kind, obj.name);
  END LOOP;
END $$;
SQL
```

If your migration role is not `otm`, replace it in both grant and owner
commands. After ownership transfer, rerun `python opentreemap/manage.py
migrate`.

Substitute `otm` with whatever role your `DATABASES`/ecoservice connection
string actually uses (and run the same grants for a separate read-only
ecoservice role if you use one). Re-run this after every restore — it is
not persisted in the dump when `--no-privileges` is used.

Notes:
- `pg_restore` from a PostgreSQL 18 client can restore dumps taken by older
  `pg_dump` versions (e.g. the 22.04 host's PostgreSQL 14), so the major
  version jump is safe to do via dump/restore even though `pg_upgrade`
  in-place requires matching the exact upgrade chain.
- `--no-owner --no-privileges` avoids failures from role names that may
  differ between hosts; re-apply grants/ownership afterward as shown above.
- For large databases where a maintenance window is tight, use
  `pg_dump --jobs=N -Fd` (directory format) for parallel dump, or set up
  logical replication from the old host to `db-26` ahead of time and only
  dump/replay the final delta at cutover.
- Validate row counts / `manage.py check` / a smoke-test query against
  `db-26` before switching the app over.

### 2.5 Migrate media/static files and secrets

```bash
# From the old host, sync uploaded media (not just static assets, which are rebuilt by npm run build)
rsync -avz /usr/local/otm/media/ user@app-26:/usr/local/otm/media/
```

Also copy over anything not stored in the database or git: `.env` files,
`opentreemap/opentreemap/settings/local_settings.py`,
`ROLLBAR_SERVER_SIDE_ACCESS_TOKEN`/`GOOGLE_MAPS_KEY` and any other secrets,
and TLS certificates.

### 2.6 Cutover

1. Point `app-26` at `db-26` (update `DATABASES` in local settings) and run
   `python opentreemap/manage.py migrate --noinput` to apply any Django
   migrations added since the dump was taken.
2. Run the full test suite (§9) against `app-26`/`db-26`.
3. Switch DNS/load balancer to `app-26`.
4. Keep the old host (and `db-26`'s source dump) around until you've
   confirmed the new host is stable, then decommission it.

---

## 3. Operating system packages (Ubuntu 26.04 LTS)

The CI pipeline targets **Ubuntu 24.04** with **PostgreSQL 18** and
**PostGIS 3**; these versions should carry forward cleanly to 26.04. The
stock 22.04 repos only ship PostgreSQL 14 and an older PostGIS, and 22.04's
default Python is 3.10, so regardless of which Ubuntu release you land on,
add the PGDG apt repository to guarantee compatible Postgres/PostGIS
packages, and install Python explicitly rather than relying on the distro
default.

```bash
sudo apt-get update
sudo apt-get install -y --no-install-recommends \
  ca-certificates curl gnupg lsb-release software-properties-common \
  build-essential libffi-dev libssl-dev libldap2-dev libxml2-dev libxslt1-dev \
  gdal-bin libgdal-dev libgeos-dev libproj-dev libpq-dev \
  postgresql-client-common

# Add the PostgreSQL PGDG apt repo (guarantees Postgres 18 + matching PostGIS 3
# regardless of what the base Ubuntu release ships by default)
curl -fsSL https://www.postgresql.org/media/keys/ACCC4CF8.asc | sudo gpg --dearmor -o /etc/apt/trusted.gpg.d/postgresql.gpg
echo "deb http://apt.postgresql.org/pub/repos/apt $(lsb_release -cs)-pgdg main" | sudo tee /etc/apt/sources.list.d/pgdg.list
sudo apt-get update

sudo DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
  postgresql-18 postgresql-client-18 postgresql-18-postgis-3 postgresql-18-postgis-3-scripts postgis
```

> If PGDG has not yet published packages for your 26.04 codename at the time
> you run this, fall back to whatever PostgreSQL/PostGIS version 26.04 ships
> by default and adjust package names (`postgresql-<version>`) accordingly.

### Python 3.11/3.12

Install 3.12 explicitly via the deadsnakes PPA (or pyenv) rather than
assuming it's the distro default, and create a fresh virtualenv:

```bash
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt-get update
sudo apt-get install -y python3.12 python3.12-venv python3.12-dev

python3.12 -m venv .venv
source .venv/bin/activate
```

### Node.js

Build tooling now requires a modern Node (CI uses Node 24):

```bash
curl -fsSL https://deb.nodesource.com/setup_24.x | sudo -E bash -
sudo apt-get install -y nodejs
```

### Redis

No version change, but confirm `redis-server` is installed/running (Redis 7
used in CI):

```bash
sudo apt-get install -y redis-server
```

---

## 4. Database migration (PostgreSQL + PostGIS)

If you're upgrading an existing server in place rather than using the
fresh-host path in §2:

1. **Back up your database first** (`pg_dumpall` or `pg_dump -Fc <db>`).
2. Install `postgresql-18`/`postgresql-18-postgis-3` alongside your existing
   cluster (apt will not remove the old version).
3. Use `pg_upgrade` (or dump/restore) to migrate your existing cluster's data
   from its current major version to 18. Run `pg_dropcluster`/
   `pg_createcluster` as needed if you want 18 to own port 5432 — see the
   commands in `.github/workflows/ci.yml` for an example of creating a fresh
   cluster.
4. Re-run `CREATE EXTENSION IF NOT EXISTS postgis;` and
   `CREATE EXTENSION IF NOT EXISTS hstore;` on the upgraded database.
5. Update `DATABASES` in your local/production settings — note
   `ci/local_settings.py` now sets an explicit `HOST`, `PORT`, `PASSWORD`,
   and `OPTIONS.sslmode`; mirror this pattern in your own settings instead of
   relying on peer auth/empty password.

### Database driver

`requirements.txt` now installs `psycopg[binary]>=3.2.0` and
`psycopg2-binary>=2.9.0` side by side. Code still imports `psycopg2`
(handled transparently by the new `opentreemap/psycopg2.py` shim), so no
application code changes are needed, but make sure both wheels install
cleanly — they require `libpq-dev` (installed above).

---

## 5. Python dependencies

```bash
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
pip install -r test-requirements.txt
pip install -r dev-requirements.txt   # dev only
```

Notable dependency changes in `requirements.txt`:
- `Django==1.11` → `Django==4.2`
- `psycopg2==2.7.3.2` → `psycopg[binary]>=3.2.0` + `psycopg2-binary>=2.9.0`
- `celery`, `boto3` (replacing `boto`), `jsonschema`, `Pillow`, `redis`,
  `rollbar`, `python-dateutil`, `pytz`, `urllib3`, etc. are now unpinned
  (`>=`) or pinned to current majors — expect newer versions than before.
- `six`, `functools32`, `anyjson`, `olefile`, `wsgiref`, `modgrammar-py2` and
  other Python 2-era packages were dropped (replaced by `modgrammar` and
  stdlib equivalents).
- `django-bower`, `django-tagging`, `django-icons`, `django-scheduler-otm`
  are retained but now resolve to current/compatible versions.

Custom wheel packages in `custom-packages/` (e.g. `django_scheduler-0.8.9`)
still need `pip install custom-packages/<file>.whl` as before.

### `test-requirements.txt`
- `selenium==2.53.6` → `selenium>=4.9.0` — if you run UI tests, make sure
  your installed Firefox/geckodriver is compatible with Selenium 4.
- `coverage`, `PyVirtualDisplay` are now unpinned majors.

---

## 6. Django settings / application code changes

These are already applied in the branch, but if you have **local
customizations or forks**, watch for:

- `django.conf.urls.url` is gone — use `django.urls.re_path` (or `path`).
  `url(...)` calls across every `urls.py` were converted to `re_path(...)`.
- `request.user.is_authenticated` is now a property, not a method — all
  `.is_authenticated()` calls were changed to `.is_authenticated`.
- Every `models.ForeignKey` now requires an explicit `on_delete=` argument
  (Django 2.0+ requirement) — added throughout migrations/models.
- `GeoManager` was removed in GeoDjango — replaced with the standard
  `Manager`.
- `@python_2_unicode_compatible` decorator and its import were removed
  (Python 3 only, no longer needed).
- New settings: `TILE_BACKEND` (`pg_tileserv` default, or `legacy`) and the
  existing `TILE_HOST` now point at your `pg_tileserv`/`martin` service
  instead of (or in addition to) `otm-tiler`. If you still run the old
  Windshaft-based `otm-tiler`, set `TILE_BACKEND=legacy`.
- Run `python scripts/check_django_python_compatibility.py` against any
  custom code you maintain outside this branch's diff to catch the same
  issues automatically.

After settings/driver changes, run migrations as usual:

```bash
python opentreemap/manage.py migrate --noinput
```

---

## 7. Frontend / build tooling

`package.json`, `webpack.*.config.js`, and `yarn.lock` were substantially
rewritten (Webpack 1 → 5, `node-sass` → Dart `sass`, old loaders → current
versions, `.css` vendor files renamed to `.scss`). Rebuild your `node_modules`
from scratch rather than trying to upgrade in place:

```bash
rm -rf node_modules
yarn install
npm run build        # production bundle (webpack.prod.config.js)
# or
npm run build-dev    # dev bundle
npm run watch         # now "webpack serve ..." instead of webpack-dev-server CLI
```

`npm run check` (jshint) and `npm run test` are unchanged entry points but
now run against the updated toolchain.

---

## 8. CI

`.travis.yml`, `travis-requirements.txt`, and
`.github/workflows/django.yml` were removed. All CI now runs through
`.github/workflows/ci.yml`, which is also the authoritative reference for
exact OS package / Postgres / Python / Node versions if this document drifts
from the workflow file.

---

## 9. Suggested upgrade order

1. Back up the database and local settings.
2. Upgrade the OS to 26.04 (§1) — either via `do-release-upgrade` hops, or
   (recommended) provision fresh 26.04 hosts and migrate data as described
   in §2.
3. Provision/upgrade OS packages (§3) — PostgreSQL 18 + PostGIS 3, Python
   3.12, Node 24, Redis.
4. Migrate the database to PostgreSQL 18 (§4), re-create `postgis`/`hstore`
   extensions (already covered by §2.2/§2.4 if using the fresh-host path).
5. Create a fresh Python 3.12 virtualenv and install
   `requirements.txt` / `test-requirements.txt` / `custom-packages/*.whl`
   (§5).
6. Update local/production Django settings for the new DB connection
   options and `TILE_BACKEND`/`TILE_HOST` (§6).
7. Run `manage.py migrate`.
8. Rebuild the frontend (`rm -rf node_modules && yarn install && npm run
   build`) (§7).
9. Run `flake8`, `npm run check`, `npm run test`, and the Django test suite
   to validate before deploying.
