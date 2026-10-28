from typing import Literal

from pydantic import BaseModel


class ModuleStatus(BaseModel):
    name: str
    status: Literal["not_implemented"] = "not_implemented"
    description: str


MODULES = (
    ModuleStatus(
        name="market_data",
        description="Validated historical candles and provider provenance",
    ),
    ModuleStatus(
        name="market_structure", description="Confirmed swings and structural breaks"
    ),
    ModuleStatus(name="smc", description="Explicit, versioned SMC detection rules"),
    ModuleStatus(name="ict", description="Explicit ICT session and liquidity rules"),
    ModuleStatus(
        name="candlestick", description="Deterministic candle pattern detectors"
    ),
    ModuleStatus(
        name="chart_patterns", description="Confirmed chart pattern detectors"
    ),
    ModuleStatus(
        name="predictions",
        description="Versioned inference with uncertainty and evaluation",
    ),
    ModuleStatus(
        name="backtesting", description="Historical simulations with fees and slippage"
    ),
)
