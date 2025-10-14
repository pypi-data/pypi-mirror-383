from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Dict, List, Optional

from .models import Header
from .datasets import BROWSERS


# 最简 UA 与规则数据（使用字典，避免每次构建临时 dict）
CHROME_VERSIONS = BROWSERS["Chrome"].os_versions
FIREFOX_VERSIONS = BROWSERS["Firefox"].os_versions
SAFARI_VERSIONS = BROWSERS["Safari"].os_versions
EDGE_VERSIONS = BROWSERS["Edge"].os_versions


HTTP11_ORDER_BY_BROWSER: Dict[str, List[str]] = {
    # 常见浏览器的排序特征（抓包近似，有网站侧反爬校验排序）
    "Chrome": [
        "Host",
        "Connection",
        "Pragma",
        "Cache-Control",
        "Upgrade-Insecure-Requests",
        "User-Agent",
        "Accept",
        "Sec-Fetch-Site",
        "Sec-Fetch-Mode",
        "Sec-Fetch-User",
        "Sec-Fetch-Dest",
        "Referer",
        "Accept-Encoding",
        "Accept-Language",
    ],
    "Edge": [
        "Host",
        "Connection",
        "Pragma",
        "Cache-Control",
        "Upgrade-Insecure-Requests",
        "User-Agent",
        "Accept",
        "Sec-Fetch-Site",
        "Sec-Fetch-Mode",
        "Sec-Fetch-User",
        "Sec-Fetch-Dest",
        "Referer",
        "Accept-Encoding",
        "Accept-Language",
    ],
    "Firefox": [
        "Host",
        "User-Agent",
        "Accept",
        "Accept-Language",
        "Accept-Encoding",
        "Referer",
        "Connection",
        "Upgrade-Insecure-Requests",
        "Sec-Fetch-Dest",
        "Sec-Fetch-Mode",
        "Sec-Fetch-Site",
        "Sec-Fetch-User",
    ],
    "Safari": [
        "Host",
        "Connection",
        "Upgrade-Insecure-Requests",
        "User-Agent",
        "Accept",
        "Referer",
        "Accept-Language",
        "Accept-Encoding",
    ],
}


def _pick(lst: List[str]) -> str:
    return random.choice(lst)


def _random_accept(browser: str) -> str:
    # Chrome/Edge/Firefox 基本一致；Safari 稍有不同
    if browser in ("Chrome", "Edge", "Firefox"):
        return "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8"
    if browser == "Safari":
        return "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
    return "*/*"


def _random_accept_language(os_name: str) -> str:
    # 简化的语言分布
    return "zh-CN,zh;q=0.9,en;q=0.7"


def _random_accept_encoding(browser: str) -> str:
    # 现代浏览器基本一致
    return "gzip, deflate, br"


def _random_sec_fetch(browser: str) -> Dict[str, str]:
    # 默认模拟跨站导航（各浏览器基本一致）
    return {
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-User": "?1",
        "Sec-Fetch-Dest": "document",
    }


def _random_client_hints(browser: str, os_name: str, version: str) -> Dict[str, str]:
    # 针对 Chromium 系列生成 Client Hints
    if browser == "Chrome":
        major_version = version.split('.')[0]
        base = {
            "Sec-CH-UA": f'"Google Chrome";v="{major_version}", "Chromium";v="{major_version}", "Not?A_Brand";v="24"',
            "Sec-CH-UA-Mobile": "?0",
            "Sec-CH-UA-Platform": f'"{os_name}"',
        }
        return base
    elif browser == "Edge":
        major_version = version.split('.')[0]
        base = {
            "Sec-CH-UA": f'"Microsoft Edge";v="{major_version}", "Chromium";v="{major_version}", "Not?A_Brand";v="24"',
            "Sec-CH-UA-Mobile": "?0",
            "Sec-CH-UA-Platform": f'"{os_name}"',
        }
        return base
    return {}


def _platform_token(os_name: str, browser: str) -> str:
    if os_name == "Windows":
        return "Windows NT 10.0; Win64; x64"
    if os_name == "macOS":
        # Firefox 在 UA 中常带 rv，但这里保持简化
        return "Macintosh; Intel Mac OS X 10_15_7"
    return "X11; Linux x86_64"


def _pick_version(os_versions: Dict[str, List[str]], os_name: str) -> str:
    versions = os_versions.get(os_name) or next(iter(os_versions.values()))
    return _pick(versions)


def _build_ua(browser: str, os_name: str) -> tuple[str, str]:
    """Build User-Agent string and return (ua_string, version)"""
    if browser == "Chrome":
        version = _pick_version(CHROME_VERSIONS, os_name)
        platform = _platform_token(os_name, browser)
        ua = f"Mozilla/5.0 ({platform}) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{version} Safari/537.36"
        return ua, version
    if browser == "Edge":
        version = _pick_version(EDGE_VERSIONS, os_name)
        platform = _platform_token("Windows", browser)
        # Edge uses current Chrome base version (130.0.0.0 for current versions)
        chrome_base = "130.0.0.0"
        ua = f"Mozilla/5.0 ({platform}) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{chrome_base} Safari/537.36 Edg/{version}"
        return ua, version
    if browser == "Firefox":
        version = _pick_version(FIREFOX_VERSIONS, os_name)
        platform = _platform_token(os_name, browser)
        ua = f"Mozilla/5.0 ({platform}) Gecko/20100101 Firefox/{version}"
        return ua, version
    if browser == "Safari":
        version = _pick_version(SAFARI_VERSIONS, os_name)
        platform = _platform_token("macOS", browser)
        ua = f"Mozilla/5.0 ({platform}) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/{version} Safari/605.1.15"
        return ua, version
    # fallback
    return "Mozilla/5.0", "1.0"


@dataclass
class FakeHeader:
    os: str = "Windows"
    browser: str = "Chrome"  # Chrome, Edge, Firefox, Safari
    
    def __post_init__(self):
        """Validate browser/OS combinations"""
        if self.browser not in BROWSERS:
            raise ValueError(f"Unsupported browser: {self.browser}. Supported browsers: {list(BROWSERS.keys())}")
        
        browser_spec = BROWSERS[self.browser]
        if self.os not in browser_spec.os_versions:
            supported_os = list(browser_spec.os_versions.keys())
            raise ValueError(f"Browser {self.browser} does not support OS {self.os}. Supported OS: {supported_os}")
        
        # Safari only runs on macOS
        if self.browser == "Safari" and self.os != "macOS":
            raise ValueError("Safari browser only runs on macOS")
        
        # Edge primarily runs on Windows (though technically available on other platforms)
        if self.browser == "Edge" and self.os != "Windows":
            raise ValueError("Edge browser in this implementation only supports Windows")

    def random(self, referer: Optional[str] = None) -> Header:
        ua, version = _build_ua(self.browser, self.os)
        accept = _random_accept(self.browser)
        accept_lang = _random_accept_language(self.os)
        accept_enc = _random_accept_encoding(self.browser)
        sec_fetch = _random_sec_fetch(self.browser)
        ch = _random_client_hints(self.browser, self.os, version)

        h = Header(
            **{
                "User-Agent": ua,
                "Accept": accept,
                "Accept-Language": accept_lang,
                "Accept-Encoding": accept_enc,
                "Upgrade-Insecure-Requests": "1",
                **sec_fetch,
                **ch,
            }
        )
        if referer:
            h.referer = referer
        return h

    def to_dict(self, header: Optional[Header] = None, overrides: Optional[Dict[str, str]] = None) -> Dict[str, str]:
        """返回适用于字典格式头部"""
        h = header or self.random()
        order = HTTP11_ORDER_BY_BROWSER.get(self.browser, [])
        base = dict(h.to_ordered_list(order))
        if overrides:
            base.update(overrides)
        return base
