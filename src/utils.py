def safe_int(v, fallback=None):
    try:
        if v is None or (isinstance(v,str) and not v.strip()):
            return fallback
        return int(float(v))
    except:
        return fallback

def norm_header(h: str) -> str:
    return "" if h is None else str(h).strip()

def parse_bool(v):
    if v is None: return None
    s = str(v).strip().lower()
    if s in ("1","true","yes","是","y","on"): return True
    if s in ("0","false","no","否","n","off"): return False
    return None
