# Redmine Docker Setup

Minimal Docker Compose setup for Redmine 6.1 with MySQL 5.7.

Included plugins:

- `redmine_issues_tree`
- `redmica_ui_extension`

Persistent volumes:

- `db_data`: MySQL data
- `redmine_data`: uploaded files

## Start

First start, or after changing the Dockerfile or plugin refs:

```powershell
docker compose up -d --build
docker compose exec redmine bundle exec rake redmine:plugins:migrate RAILS_ENV=production
```

Normal start:

```powershell
docker compose up -d
```

Access:

- URL: <http://localhost:3000>
- Default login: `admin` / `admin`

## Common commands

Check status:

```powershell
docker compose ps
```

Stop containers:

```powershell
docker compose down
```

Recreate everything including volumes:

```powershell
docker compose down -v
docker compose up -d --build
docker compose exec redmine bundle exec rake redmine:plugins:migrate RAILS_ENV=production
```

Open a shell in the Redmine container:

```powershell
docker compose exec redmine bash
```

## Notes

- Redmine and plugin refs are pinned in `docker-compose.yml` build args.
- When changing the Redmine version, update `REDMINE_IMAGE_TAG` and the plugin refs together.
