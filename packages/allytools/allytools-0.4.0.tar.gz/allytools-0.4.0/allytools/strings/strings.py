from typing import Any, Optional

FALSEY_TOKENS = {"", "none", "null", "nan", "n/a", "-"}

def clean_str(val: Any) -> Optional[str]:
    if val is None:
        return None
    s = str(val).strip()
    if not s:
        return None
    s_norm = " ".join(s.split())  # collapse multiple spaces/tabs/newlines
    return None if s_norm.lower() in FALSEY_TOKENS else s_norm