from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Tuple


@dataclass(frozen=True)
class BrowserSpec:
    name: str
    os_versions: Dict[str, List[str]]  # OS -> versions


BROWSERS: Dict[str, BrowserSpec] = {
    "Chrome": BrowserSpec(
        name="Chrome",
        os_versions={
            "Windows": ["129.0.6668.70", "130.0.6723.58", "131.0.6778.69"],
            "macOS": ["129.0.6668.90", "130.0.6723.91", "131.0.6778.85"],
            "Linux": ["129.0.6668.89", "130.0.6723.116", "131.0.6778.108"],
        },
    ),
    "Edge": BrowserSpec(
        name="Edge",
        os_versions={
            "Windows": ["129.0.2792.52", "130.0.2849.46", "131.0.2903.27"],
        },
    ),
    "Firefox": BrowserSpec(
        name="Firefox",
        os_versions={
            "Windows": ["130.0", "131.0", "132.0"],
            "macOS": ["130.0", "131.0", "132.0"],
            "Linux": ["130.0", "131.0", "132.0"],
        },
    ),
    "Safari": BrowserSpec(
        name="Safari",
        os_versions={
            "macOS": ["17.6", "18.0", "18.1"],
        },
    ),
}


