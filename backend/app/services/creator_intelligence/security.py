import ipaddress
import os
import re
from typing import Iterable, List, Tuple
from urllib.parse import urlparse


CONTROL_CHARS = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")
PROMPT_TAGS = re.compile(r"</?(system|assistant|user|tool|developer|script|iframe)[^>]*>", re.IGNORECASE)


def sanitize_untrusted_text(value: str, max_length: int = 4000) -> Tuple[str, List[str]]:
    warnings: List[str] = []
    if value is None:
        return "", ["empty_input"]

    text = str(value)
    if CONTROL_CHARS.search(text):
        warnings.append("control_characters_removed")
        text = CONTROL_CHARS.sub("", text)

    if PROMPT_TAGS.search(text):
        warnings.append("prompt_like_tags_escaped")
        text = PROMPT_TAGS.sub(lambda match: match.group(0).replace("<", "[").replace(">", "]"), text)

    if len(text) > max_length:
        warnings.append("truncated")
        text = text[:max_length]

    return text.strip(), warnings


def trusted_prompt_context(label: str, text: str) -> str:
    sanitized, _ = sanitize_untrusted_text(text)
    return f"[UNTRUSTED_SOURCE:{label}]\n{sanitized}\n[/UNTRUSTED_SOURCE]"


def normalize_allowed_path(path: str, allowed_roots: Iterable[str]) -> str:
    if not path:
        raise ValueError("path is required")

    expanded = os.path.abspath(os.path.expanduser(path))
    roots = [os.path.abspath(os.path.expanduser(root)) for root in allowed_roots if root]
    if not roots:
        raise ValueError("at least one allowed root is required")

    for root in roots:
        try:
            if os.path.commonpath([expanded, root]) == root:
                return expanded
        except ValueError:
            continue

    raise ValueError("path is outside configured model scan roots")


def split_model_roots(value: str) -> List[str]:
    return [part.strip() for part in (value or "").split(",") if part.strip()]


def is_safe_outbound_url(url: str, allowed_hosts: Iterable[str] = ()) -> bool:
    parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"} or not parsed.hostname:
        return False

    host = parsed.hostname.lower()
    allowed = {item.lower() for item in allowed_hosts if item}
    if allowed and host not in allowed:
        return False

    blocked_hosts = {"localhost", "0.0.0.0"}
    if host in blocked_hosts or host.endswith(".local"):
        return False

    try:
        ip = ipaddress.ip_address(host)
    except ValueError:
        return True

    return not (ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_reserved)
