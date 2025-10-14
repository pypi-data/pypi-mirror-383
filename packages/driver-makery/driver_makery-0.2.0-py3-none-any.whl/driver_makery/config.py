import os
import json
import yaml
import toml
from dotenv import load_dotenv

DEFAULTS = {
    "PDF_PATH": "cdn_ddr_ctrl_rrm_v1.20.pdf",
    "REG_START_PAGE": 79,
    "REG_END_PAGE": 368,
    "OUTPUT_TEXT_FILENAME": "DocToCodeBot.txt",
    "REG_SPLIT_UNIT": 20,
    "REG_NAME_PATTERN": r"DENALI_[A-Z0-9_]+_\d{2,3}",
    "CODE_OUTPUT_FILENAME_FORMAT": "Register_Definitions_Part_{part_number:02d}.h",
    "GEMINI_API_URL": "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-05-20:generateContent",
}

def _load_file_if_exists(fname: str):
    if not os.path.exists(fname):
        return {}
    if fname.endswith(".toml"):
        return toml.load(fname)
    if fname.endswith((".yaml", ".yml")):
        with open(fname, "r", encoding="utf-8") as f:
            return yaml.safe_load(f) or {}
    if fname.endswith(".json"):
        with open(fname, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def load_config() -> dict:
    load_dotenv()
    cfg = DEFAULTS.copy()
    for candidate in ("config.toml", "config.yaml", "config.yml", "config.json"):
        cfg.update(_load_file_if_exists(candidate))

    for k in list(cfg.keys()) + ["GEMINI_API_KEY", "GEMINI_API_URL"]:
        v = os.getenv(k)
        if v is not None:
            if k in ("REG_START_PAGE", "REG_END_PAGE", "REG_SPLIT_UNIT"):
                try:
                    cfg[k] = int(v)
                    continue
                except ValueError:
                    pass
            cfg[k] = v
    return cfg
