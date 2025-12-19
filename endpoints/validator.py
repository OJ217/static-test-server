from fractions import Fraction
from typing import TypedDict, Tuple, Optional, Any

class InputPayload(TypedDict):
    name: Any
    mass_loss: Any
    time_interval: Any

class ValidatedPayload(TypedDict):
    name: str
    mass_loss: float
    time_interval: float

class ErrorPayload(TypedDict):
    error: str

def validate_meta_payload(
    payload: InputPayload,
) -> Tuple[Optional[ValidatedPayload], Optional[ErrorPayload]]:
    if not payload:
        return None, {"error": "Invalid payload"}

    name = payload.get("name")
    if name is None:
        return None, {"error": "Invalid payload: name"}
    name = str(name)

    # Validate mass_loss
    mass_loss = payload.get("mass_loss")
    if mass_loss is None:
        return None, {"error": "Invalid payload: mass_loss"}
    mass_loss = float(mass_loss)

    # Validate time_interval
    raw_time_interval = payload.get("time_interval")
    if raw_time_interval is None:
        return None, {"error": "Invalid payload: time_interval"}

    try:
        cleaned = str(raw_time_interval).replace(" ", "")
        time_interval = float(Fraction(cleaned))
    except Exception:
        return None, {"error": "Invalid payload: time_interval"}

    return {
        "name": name,
        "mass_loss": mass_loss,
        "time_interval": time_interval,
    }, None
