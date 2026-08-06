# Migrations (future)

For this MVP, tables are created directly via `scripts/create_db.py`
using `Base.metadata.create_all()`. This is fine for a single-client
deployment where the schema is fixed at delivery time.

If/when the schema needs to evolve after a client is live (e.g. adding
a column without losing their data), wire up Alembic here:

```
alembic init app/database/migrations
```

Then point `env.py`'s `target_metadata` to `app.database.base.Base.metadata`
and generate migrations with `alembic revision --autogenerate`.
