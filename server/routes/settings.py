import os
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional

from server.auth.security import get_current_user
from server.models.user import User
from config import Config

router = APIRouter()

ENV_PATH = os.path.join(Config.BASE_DIR, ".env")


class LLMConfig(BaseModel):
    llm_provider: str = ""
    llm_api_key: str = ""
    llm_base_url: str = ""
    llm_model: str = ""


def _read_env() -> dict[str, str]:
    env = {}
    if os.path.exists(ENV_PATH):
        with open(ENV_PATH, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if "=" in line:
                    key, _, value = line.partition("=")
                    env[key.strip()] = value.strip()
    return env


def _write_env(env: dict[str, str]) -> None:
    lines = []
    if os.path.exists(ENV_PATH):
        with open(ENV_PATH, "r", encoding="utf-8") as f:
            lines = f.readlines()

    updated_keys = set()
    new_lines = []
    for line in lines:
        stripped = line.strip()
        if stripped and not stripped.startswith("#") and "=" in stripped:
            key = stripped.partition("=")[0].strip()
            if key in env:
                new_lines.append(f"{key}={env[key]}\n")
                updated_keys.add(key)
                continue
        new_lines.append(line)

    for key, value in env.items():
        if key not in updated_keys:
            new_lines.append(f"{key}={value}\n")

    with open(ENV_PATH, "w", encoding="utf-8") as f:
        f.writelines(new_lines)


@router.get("/settings/llm")
def get_llm_config(current_user: User = Depends(get_current_user)):
    env = _read_env()
    return {
        "llm_provider": env.get("LLM_PROVIDER", Config.LLM_PROVIDER),
        "llm_api_key": env.get("LLM_API_KEY", ""),
        "llm_base_url": env.get("LLM_BASE_URL", Config.LLM_BASE_URL),
        "llm_model": env.get("LLM_MODEL", Config.LLM_MODEL),
    }


@router.put("/settings/llm")
def update_llm_config(config: LLMConfig, current_user: User = Depends(get_current_user)):

    updates = {}
    if config.llm_provider:
        updates["LLM_PROVIDER"] = config.llm_provider
    if config.llm_api_key:
        updates["LLM_API_KEY"] = config.llm_api_key
    if config.llm_base_url:
        updates["LLM_BASE_URL"] = config.llm_base_url
    if config.llm_model:
        updates["LLM_MODEL"] = config.llm_model

    if updates:
        _write_env(updates)
        if "LLM_PROVIDER" in updates:
            Config.LLM_PROVIDER = updates["LLM_PROVIDER"]
        if "LLM_API_KEY" in updates:
            Config.LLM_API_KEY = updates["LLM_API_KEY"]
        if "LLM_BASE_URL" in updates:
            Config.LLM_BASE_URL = updates["LLM_BASE_URL"]
        if "LLM_MODEL" in updates:
            Config.LLM_MODEL = updates["LLM_MODEL"]

    from server.dependencies import reset_all_kb
    reset_all_kb()

    return {"status": "success", "message": "LLM configuration updated"}
