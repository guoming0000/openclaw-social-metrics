from __future__ import annotations

import re

from .base import BasePlatform, MetricsResult
from utils.browser import BrowserManager, parse_follower_text, extract_follower_count


class DouyinPlatform(BasePlatform):
    name = "douyin"

    CAPTCHA_CLOSE_SELECTORS = [
        '#captcha-verify-close',
        'div[class*="captcha"] div[class*="close"]',
        '[class*="verify-bar-close"]',
        'div[class*="captcha_verify"] [class*="close"]',
        'div[class*="verify"] [class*="close"]',
    ]

    async def _dismiss_captcha(self, page) -> None:
        """Detect and close the CAPTCHA verification popup if present."""
        for selector in self.CAPTCHA_CLOSE_SELECTORS:
            try:
                close_btn = await page.query_selector(selector)
                if close_btn and await close_btn.is_visible():
                    await close_btn.click()
                    await page.wait_for_timeout(1000)
                    return
            except Exception:
                continue

    async def fetch_by_url(self, url: str) -> MetricsResult:
        mgr = await BrowserManager.get_instance()
        async with mgr.new_cdp_page() as page:
            try:
                await page.goto(url, wait_until="domcontentloaded", timeout=30000)
                await page.wait_for_timeout(3000)

                await self._dismiss_captcha(page)

                follower_el = await page.query_selector(
                    '[data-e2e="user-info"] .fan .num'
                )
                if not follower_el:
                    follower_el = await page.query_selector(
                        'span[class*="follower"] span[class*="num"]'
                    )
                count = None
                if follower_el:
                    text = (await follower_el.inner_text()).strip()
                    count = parse_follower_text(text)

                if count is None:
                    all_spans = await page.query_selector_all("span, div")
                    for span in all_spans:
                        text = (await span.inner_text()).strip()
                        if not text or len(text) > 50:
                            continue
                        for kw in ("粉丝", "关注者"):
                            c = extract_follower_count(text, kw)
                            if c is not None:
                                count = c
                                break
                        if count is not None:
                            break

                if count is None:
                    body_text = await page.inner_text("body")
                    count = extract_follower_count(body_text)

                if count is None:
                    return self._error_result(
                        "Could not find follower count element", url=url
                    )

                name_el = await page.query_selector(
                    '[data-e2e="user-info"] .name, h1[class*="name"]'
                )
                username = (await name_el.inner_text()).strip() if name_el else None

                return MetricsResult(
                    platform=self.name,
                    username=username,
                    url=url,
                    metrics={"followers": count},
                )
            except Exception as e:
                return self._error_result(f"Browser scraping error: {e}", url=url)

    async def _find_search_result_user(self, page) -> str | None:
        """Find the first real user profile link from search results,
        skipping navigation links like /user/self."""
        all_links = await page.query_selector_all('a[href*="/user/"]')
        for link in all_links:
            href = await link.get_attribute("href") or ""
            if "/user/self" in href:
                continue
            if not re.search(r"/user/\w{10,}", href):
                continue
            if not await link.is_visible():
                continue
            return href
        return None

    async def fetch_by_nickname(self, nickname: str) -> MetricsResult:
        search_url = f"https://www.douyin.com/search/{nickname}"
        mgr = await BrowserManager.get_instance()
        async with mgr.new_cdp_page() as page:
            try:
                await page.goto(
                    search_url, wait_until="domcontentloaded", timeout=30000
                )
                await page.wait_for_timeout(5000)

                await self._dismiss_captcha(page)

                href = await self._find_search_result_user(page)
                if not href:
                    await page.wait_for_timeout(3000)
                    await self._dismiss_captcha(page)
                    href = await self._find_search_result_user(page)

                if not href:
                    return self._error_result(
                        f"User '{nickname}' not found on Douyin", username=nickname
                    )

                if href.startswith("//"):
                    href = "https:" + href
                elif not href.startswith("http"):
                    href = "https://www.douyin.com" + href

                result = await self.fetch_by_url(href)
                result.username = result.username or nickname
                return result
            except Exception as e:
                return self._error_result(f"Search error: {e}", username=nickname)
