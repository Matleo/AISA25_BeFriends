import json
from pathlib import Path
import streamlit as st

class ProfileManager:
    DEFAULT_PROFILE = {
        "name": "Karolina",
        "age": 33,
        "city": "Basel (CH)",
        "address": "Dornacherstr.",
        "interests": [
            "dance (zouk, salsa)",
            "water sports",
            "swimming in the Rhine",
            "being around water",
            "music (guitar, ukulele)",
            "concerts",
            "festivals",
            "jam sessions",
            "dogs",
            "kids",
            "fun social activities",
            "outdoor activities",
            "dog-friendly gatherings",
            "cultural festivals"
        ]
    }

    @staticmethod
    def load_profile(profile_path: str = "karolina_profile.json") -> dict:
        from json import JSONDecodeError
        profile_file = Path(profile_path)
        if profile_file.exists():
            try:
                with open(profile_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except JSONDecodeError:
                st.warning(f"Profile file {profile_path} is malformed. Using fallback profile.")
                return ProfileManager.DEFAULT_PROFILE.copy()
        st.warning(f"Profile file {profile_path} not found. Using fallback profile.")
        return ProfileManager.DEFAULT_PROFILE.copy()

    @staticmethod
    def ensure_profile_in_session():
        if "profile" not in st.session_state:
            st.session_state["profile"] = ProfileManager.load_profile()
        return st.session_state["profile"]

    @staticmethod
    def get_default_city() -> str:
        return ProfileManager.ensure_profile_in_session()["city"]

    @staticmethod
    def get_default_filters() -> dict:
        import sqlite3
        from befriends.common.config import AppConfig
        config = AppConfig.from_env()
        db_path = config.db_url.replace("sqlite:///", "") if config.db_url.startswith("sqlite:///") else config.db_url
        city_value = ProfileManager.ensure_profile_in_session()["city"]
        try:
            with sqlite3.connect(db_path) as conn:
                cur = conn.cursor()
                cur.execute('SELECT COUNT(*) FROM events WHERE city IS NOT NULL AND city != "";')
                city_count = cur.fetchone()[0]
                if city_count == 0:
                    city_value = ""
        except Exception:
            city_value = ""
        return {
            "city": city_value,
            "category": "",
            "date_from": None,
            "date_to": None,
            "price_min": None,
            "price_max": None,
            "apply_filters": True,
        }
