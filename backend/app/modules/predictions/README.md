# predictions

Status: **not implemented**. Foundation provides only the module boundary and status registry.

Responsibility: Inference over versioned feature/model artifacts.

Contract: Return model version, data cutoff and uncertainty; no fabricated scores.

Add files only as behavior is implemented:
- `schemas.py`: versioned input/output contracts, timestamps, source and validation.
- `service.py`: application use cases; explicit dependency injection.
- `domain.py`: deterministic business rules with no FastAPI/provider imports.
- `ports.py`: narrow Protocol interfaces when external I/O is needed.
- `router.py`: thin HTTP adapter, registered explicitly in `app/main.py`.
- `models.py`: persistence models when required; Alembic migration accompanies changes.

Adapters belong in existing `app/infrastructure` directories. Cross-module access uses
public contracts/services, never another module's database tables. Unit tests belong
in `backend/tests`; provider and PostgreSQL tests in `backend/tests/integration`.
No empty success responses or simulated market results until actual logic exists.
