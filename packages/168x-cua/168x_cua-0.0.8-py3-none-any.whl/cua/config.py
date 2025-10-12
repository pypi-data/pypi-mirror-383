import json
from pathlib import Path
from pydantic import BaseModel

class Config(BaseModel):
    backend_api_base_url: str
    agent_instance_id: str
    secret_key: str
    
    class Config:
        extra = "ignore"
    
    
# Global settings instance
_config = None
    
def init_config_from_json_file(config_path: str | Path):
    """Load configuration from a JSON file"""
    config_path = Path(config_path)
    
    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")
    
    with open(config_path, 'r') as f:
        config_data = json.load(f)
    
    global _config
    _config = Config(**config_data)


def get_config() -> Config:
    if _config is None:
        raise RuntimeError("Config not initialized")
    return _config

