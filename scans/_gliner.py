"""Lazy GLiNER inference helper for VibeScan classifier + attribution.

Implements the labels and data-class mapping from vibescan_v2_tech_spec.md §4.
The model is loaded once on first call and cached process-wide. If the
`gliner` package is missing, the model fails to load, or inference errors
out, every helper returns None — callers must treat None as
"GLiNER unavailable" and fall back to regex.
"""

import logging
import os
import re
import threading
from collections.abc import Iterable


logger = logging.getLogger(__name__)

_MODEL = None
_LOAD_FAILED = False
_LOCK = threading.Lock()

MODEL_NAME = "urchade/gliner_medium-v2.1"

# GLiNER tokenizer is roughly 4 chars/token; spec §4.3 caps at 2000 tokens.
_MAX_CHARS = 8000

# gliner_medium-v2.1's per-sentence sequence limit is 384 tokens. Pages with
# little punctuation (minified inline JS, JSON, code blocks) leave one giant
# "sentence" after HTML stripping which GLiNER then truncates to 384 tokens,
# dropping real content. Chunking the prepared text at this byte size keeps
# every chunk safely under the model's token budget (~4 chars/token).
_CHUNK_CHARS = 1200

# Spec §4.2
ENTITY_LABELS = [
    # PII
    "person name",
    "email address",
    "phone number",
    "home address",
    "social security number",
    "date of birth",
    "credit card number",
    "bank account number",
    # Corporate sensitive
    "customer record",
    "employee record",
    "salary or compensation",
    "go-to-market strategy",
    "competitive analysis",
    "unreleased product feature",
    "financial budget",
    "vendor contract value",
    "medical or health record",
    "legal document",
    # Technical
    "api key or secret",
    "database connection string",
    "internal ip address",
    "source code",
]

# Spec §4.4 — first label-set hit assigns the data class. Multiple classes
# can apply to one page (we iterate the full list).
DATA_CLASS_MAP: list[tuple[set[str], str]] = [
    ({"person name", "email address", "phone number", "home address"}, "pii_contact"),
    ({"customer record"}, "crm"),
    ({"employee record", "salary or compensation"}, "hr"),
    ({"go-to-market strategy", "competitive analysis", "unreleased product feature"}, "strategy"),
    ({"financial budget", "vendor contract value"}, "finance"),
    ({"medical or health record"}, "healthcare"),
    ({"api key or secret", "database connection string"}, "credentials"),
    ({"source code"}, "source_code"),
]


def _prepare(text: str) -> str:
    return re.sub(r"<[^>]+>", " ", text or "")[:_MAX_CHARS]


def _chunked(text: str) -> list[str]:
    """Split prepared text into chunks small enough for GLiNER's 384-token
    per-sentence limit. Prefers sentence boundaries; force-breaks runs
    without punctuation (minified JS / JSON / code) at fixed byte intervals
    so no single chunk triggers the truncation warning.
    """
    if not text:
        return []
    parts = re.split(r"(?<=[.!?\n])\s+", text)
    out: list[str] = []
    for part in parts:
        part = part.strip()
        if not part:
            continue
        if len(part) <= _CHUNK_CHARS:
            out.append(part)
        else:
            for i in range(0, len(part), _CHUNK_CHARS):
                end = i + _CHUNK_CHARS
                piece = part[i:end].strip()
                if piece:
                    out.append(piece)
    return out


def _ensure_hf_token() -> None:
    """If HF_TOKEN isn't in env, pull it from SSM (same path the rest of
    the scanner uses) and set it so huggingface_hub picks it up before the
    first model download. Anonymous downloads are heavily rate-limited and
    slow cold starts in CI / Docker.
    """
    if os.environ.get("HF_TOKEN"):
        return
    try:
        from utils.secrets import get_secret

        token = get_secret("HF_TOKEN")
    except Exception:
        token = None
    if token:
        os.environ["HF_TOKEN"] = token


def _load():
    global _MODEL, _LOAD_FAILED
    if _LOAD_FAILED:
        return None
    if _MODEL is not None:
        return _MODEL
    with _LOCK:
        if _LOAD_FAILED:
            return None
        if _MODEL is not None:
            return _MODEL
        _ensure_hf_token()
        try:
            from gliner import GLiNER

            _MODEL = GLiNER.from_pretrained(MODEL_NAME)
            logger.info("GLiNER model %s loaded", MODEL_NAME)
            return _MODEL
        except Exception as e:
            logger.info("GLiNER unavailable, falling back to regex: %s", e.__class__.__name__)
            _LOAD_FAILED = True
            return None


def _predict(text: str, labels: Iterable[str], threshold: float = 0.4) -> list[dict] | None:
    model = _load()
    if model is None or not text:
        return None
    chunks = _chunked(_prepare(text))
    if not chunks:
        return []
    labels = list(labels)
    out: list[dict] = []
    try:
        for chunk in chunks:
            entities = model.predict_entities(chunk, labels, threshold=threshold)
            if entities:
                out.extend(entities)
        return out
    except Exception:
        logger.exception("GLiNER inference failed")
        return None


def classify_text(text: str) -> list[str] | None:
    """Return the data classes detected in `text`, or None if GLiNER is
    unavailable. Empty list means "GLiNER ran but found nothing"."""
    entities = _predict(text, ENTITY_LABELS)
    if entities is None:
        return None
    detected = {(e.get("label") or "").lower() for e in entities}
    return sorted({cls for labels, cls in DATA_CLASS_MAP if labels & detected})


def find_organization(text: str, company_name: str) -> bool | None:
    """True iff GLiNER detects an `organization` span overlapping the target
    company name (case-insensitive substring either direction). Returns None
    if GLiNER is unavailable so callers know to skip silently."""
    if not company_name:
        return False
    entities = _predict(text, ["organization"], threshold=0.5)
    if entities is None:
        return None
    target = company_name.strip().lower()
    for e in entities:
        span = (e.get("text") or "").strip().lower()
        if span and (target in span or span in target):
            return True
    return False
