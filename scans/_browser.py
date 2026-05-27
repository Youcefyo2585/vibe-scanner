"""Headless Chromium helper for VibeScan.

Vibe-coded apps deployed on Lovable, Vercel, Replit, and Base44 are almost
always client-rendered SPAs. A plain `requests.get` sees the empty HTML shell
(`<div id="root"></div>`), with no content, no attribution, no data class
keywords. This helper renders such pages in a real browser so the downstream
probe checks can see the same DOM a human would.

Uses the project-local Chromium installed under bin/chrome by
install-browser.sh; no new dependencies beyond the selenium package already
in requirements.txt.
"""

import logging
import os
from contextlib import contextmanager


logger = logging.getLogger(__name__)


_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_CHROME_BIN = os.path.join(_PROJECT_ROOT, "bin", "chrome", "chrome")
_CHROMEDRIVER_BIN = os.path.join(_PROJECT_ROOT, "bin", "chromedriver", "chromedriver")


def is_available() -> bool:
    """True when the bundled Chromium + driver exist on disk."""
    return os.path.isfile(_CHROME_BIN) and os.path.isfile(_CHROMEDRIVER_BIN)


@contextmanager
def _driver():
    """Spin up a short-lived headless Chrome instance.

    We import selenium lazily so the module stays importable in environments
    where Chromium hasn't been installed — the requests-only fast path still
    works without it.
    """
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        from selenium.webdriver.chrome.service import Service
    except ImportError as e:
        raise RuntimeError("selenium not installed — cannot run browser probe") from e

    opts = Options()
    opts.add_argument("--headless=new")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--disable-gpu")
    opts.add_argument("--window-size=1280,1024")
    opts.add_argument("--ignore-certificate-errors")
    opts.add_argument(
        "--user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    )
    opts.binary_location = _CHROME_BIN

    service = Service(executable_path=_CHROMEDRIVER_BIN)
    drv = webdriver.Chrome(service=service, options=opts)
    drv.set_page_load_timeout(20)
    try:
        yield drv
    finally:
        try:
            drv.quit()
        except Exception:
            logger.debug("driver.quit() raised", exc_info=True)


def render(url: str, settle_seconds: float = 2.0) -> str | None:
    """Fetch `url` in a real browser and return the fully-rendered HTML.

    Returns None on any failure (browser missing, navigation timeout, crash).
    Callers should treat None as 'browser probe unavailable, fall back to
    whatever the requests-only probe saw'.
    """
    if not is_available():
        logger.debug("Browser probe skipped — Chromium binary not at %s", _CHROME_BIN)
        return None

    try:
        with _driver() as drv:
            drv.get(url)
            # Let SPA frameworks finish their initial render. A fixed pause is
            # rougher than a wait condition but it's universal — we have no
            # idea what framework or selectors the random vibe-coded app uses.
            import time

            time.sleep(settle_seconds)
            return drv.page_source or ""
    except Exception as e:
        logger.warning("Browser render failed for %s: %s", url, e.__class__.__name__)
        return None


def looks_like_spa_shell(html: str) -> bool:
    """Heuristic: True when an HTML response looks like an empty SPA shell.

    Triggered by very small visible text on a page that mounts a known JS root
    element. Tuned to be a *cheap* check — anything fancier should run only
    after this returns True.
    """
    if not html:
        return True
    import re

    visible = re.sub(r"<script.*?</script>", " ", html, flags=re.S | re.I)
    visible = re.sub(r"<style.*?</style>", " ", visible, flags=re.S | re.I)
    visible = re.sub(r"<[^>]+>", " ", visible)
    visible = re.sub(r"\s+", " ", visible).strip()
    has_mount = bool(
        re.search(r'id\s*=\s*["\'](?:root|app|__next|__nuxt|svelte)["\']', html, re.I)
        or "__NEXT_DATA__" in html
        or "vite" in html.lower()
    )
    return has_mount and len(visible) < 400
