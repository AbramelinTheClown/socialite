# Database Configuration

## PostgreSQL Connection
```python
import psycopg2
from os import environ

conn = psycopg2.connect(
    dbname=environ['DB_NAME'],
    user=environ['DB_ROLE'],
    password=environ['DB_PASSWORD'],
    host=environ['DB_HOST'],
    port=environ['DB_PORT']
)
```

## Folder Structure
```
database/
├── migrations/
├── queries/
└── schema/
```

## Security Practices
1. Never commit .env files
2. Rotate credentials quarterly
3. Use connection pooling