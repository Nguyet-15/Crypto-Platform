from fastapi import APIRouter

from app.modules.registry import MODULES, ModuleStatus

router = APIRouter(prefix="/modules", tags=["modules"])


@router.get("", response_model=list[ModuleStatus])
def module_status() -> list[ModuleStatus]:
    return list(MODULES)
