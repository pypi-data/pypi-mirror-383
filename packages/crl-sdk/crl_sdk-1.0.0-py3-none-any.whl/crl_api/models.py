"""Data models for CRL API."""

from enum import Enum
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field, ConfigDict


class ProductMode(str, Enum):
    """CRL product types."""
    CRL = "crl"
    ACRL = "acrl"
    DT_CRL = "dt-crl"


class Side(str, Enum):
    """Position side."""
    LONG = "long"
    SHORT = "short"


class State(str, Enum):
    """Position state."""
    INITIAL = "INITIAL"
    LEVERAGED = "LEVERAGED"
    CLOSED = "CLOSED"


class CalcRequest(BaseModel):
    """Request for /calc endpoint."""
    model_config = ConfigDict(use_enum_values=True)
    
    mode: ProductMode
    S0: float = Field(gt=0, description="Entry spot price")
    ST: float = Field(gt=0, description="Current spot price")
    K: float = Field(gt=0, description="Trigger barrier")
    L: int = Field(ge=2, le=10, description="Leverage multiplier")
    premium: float = Field(ge=0, description="Premium paid")
    side: Side
    params: Optional[Dict[str, Any]] = None


class Greeks(BaseModel):
    """Greeks data."""
    delta: Optional[float] = None


class CalcResponse(BaseModel):
    """Response from /calc endpoint."""
    pnl: float
    state: State
    retroJump: Optional[float] = None
    greeks: Optional[Greeks] = None
