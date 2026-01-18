from typing import Any, Dict, Optional, Tuple


def parse_link_header(link_value: str) -> Dict[str, str]:
    """
    Parse básico de RFC5988 Link header.
    Ej:
    <https://api.github.com/...page=2>; rel="next", <...page=5>; rel="last"
    """
    result: Dict[str, str] = {}
    parts = [p.strip() for p in link_value.split(",")]
    for part in parts:
        section = [s.strip() for s in part.split(";")]
        if len(section) < 2:
            continue

        url_part = section[0]
        if not (url_part.startswith("<") and url_part.endswith(">")):
            continue
        url = url_part[1:-1]

        rel = None
        for seg in section[1:]:
            if seg.startswith('rel="') and seg.endswith('"'):
                rel = seg[5:-1]
        if rel:
            result[rel] = url

    return result


def extract_items(payload: Any) -> Tuple[list, Optional[dict]]:
    """
    Algunas APIs devuelven lista directa, otras devuelven dict con 'items'.
    Retorna (items, meta_opcional)
    """
    if isinstance(payload, list):
        return payload, None
    if isinstance(payload, dict) and "items" in payload and isinstance(payload["items"], list):
        return payload["items"], payload
    return [], None
