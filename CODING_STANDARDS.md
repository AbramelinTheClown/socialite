# AstroToon Development Standards

## Python Conventions
```python
# Astronomy calculations pattern
def calculate_ascendant(
    observer_lat: Annotated[float, GeospatialConstraint()],
    observer_lon: Annotated[float, GeospatialConstraint()],
    dt: datetime
) -> Constellation:
    """Calculate rising zodiac sign with strict type validation"""
    # Timezone-aware datetime required
    utc_time = dt.astimezone(timezone.utc)  
    # Decimal precision for astronomical calc
    return compute_rising_sign(
        lat=Decimal(observer_lat).quantize(Decimal('1.0000')),
        lon=Decimal(observer_lon).quantize(Decimal('1.0000')),
        moment=utc_time
    )
```

## Poetry Dependency Management
```toml
[tool.poetry.dependencies]
python = "3.10.13"  # Pinned to patch version
skyfield = { version = "1.53", extras = ["jplephem"] }
pytz = "^2024.1"

[tool.poetry.group.test.dependencies]
pytest = "8.1.1"
pytest-docker = "2.0.0"
```

## Docker Standards
```dockerfile
# Multi-stage build for planets service
FROM python:3.10-slim as builder

WORKDIR /install
COPY planets/pyproject.toml planets/poetry.lock .
RUN pip install --user poetry && \
    /root/.local/bin/poetry install --no-root

FROM python:3.10-slim

COPY --from=builder /root/.local /root/.local
COPY planets/get_planets.py .
ENV PATH=/root/.local/bin:$PATH

CMD ["python", "-u", "get_planets.py"]
```

## Testing Requirements
1. Astronomical calculations require ±0.5° tolerance
2. Docker builds must include security scans
3. Volume mounts need user namespace validation