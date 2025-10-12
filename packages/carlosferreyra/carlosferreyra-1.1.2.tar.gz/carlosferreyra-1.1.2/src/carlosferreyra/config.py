"""Configuration for the CLI business card."""

import json
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional


@dataclass
class PersonalInfo:
    name: str
    title: str
    company: Optional[str]
    location: str
    skills: List[str]


@dataclass
class URLs:
    email: str
    resume: str
    portfolio: str
    github: str
    linkedin: str
    twitter: Optional[str]


@dataclass
class ThemeConfig:
    border_color: str
    background_color: str
    animation_speed: dict


@dataclass
class AppConfig:
    personal_info: PersonalInfo
    urls: URLs
    theme: ThemeConfig


def load_config() -> AppConfig:
    """Load configuration from the central config.json file."""
    try:
        # Try to load from the root of the project (during development)
        config_path = Path(__file__).parent.parent.parent.parent.parent / "config.json"
        if not config_path.exists():
            # Fallback to bundled config
            config_path = Path(__file__).parent / "config.json"

        with open(config_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        # Convert animation speed values (JSON uses milliseconds, Python uses seconds)
        # TypeScript: {fast: 8, medium: 25, slow: 40} ms
        # Python needs: {fast: 0.008, medium: 0.025, slow: 0.04} seconds
        animation_speed = {
            "fast": data["theme"]["animationSpeed"]["fast"] / 1000,
            "medium": data["theme"]["animationSpeed"]["medium"] / 1000,
            "slow": data["theme"]["animationSpeed"]["slow"] / 1000,
        }

        return AppConfig(
            personal_info=PersonalInfo(
                name=data["personalInfo"]["name"],
                title=data["personalInfo"]["title"],
                company=data["personalInfo"].get("company"),
                location=data["personalInfo"]["location"],
                skills=data["personalInfo"]["skills"],
            ),
            urls=URLs(
                email=data["urls"]["email"],
                resume=data["urls"]["resume"],
                portfolio=data["urls"]["portfolio"],
                github=data["urls"]["github"],
                linkedin=data["urls"]["linkedin"],
                twitter=data["urls"].get("twitter"),
            ),
            theme=ThemeConfig(
                border_color=data["theme"]["borderColor"],
                background_color=data["theme"]["backgroundColor"],
                animation_speed=animation_speed,
            ),
        )
    except (FileNotFoundError, KeyError, json.JSONDecodeError) as e:
        raise RuntimeError(
            f"Failed to load configuration file: {e}. "
            "Please ensure config.json exists and is valid."
        ) from e


# Configuration instance
CONFIG = load_config()
