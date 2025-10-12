"""Configuration management for DataSage MCP server."""

import os
import yaml
from pathlib import Path
from typing import Dict, Any, List, Optional


DEFAULT_CONFIG = {
    "server": {
        "name": "DataSage",
        "description": "Local file server for AI assistants"
    },
    "paths": [],
    "settings": {
        "max_depth": 10,
        "max_file_size": 10485760,  # 10MB
        "text_detection": "auto",
        "excluded_extensions": [
            ".exe", ".bin", ".dll", ".so", ".dylib",
            ".jpg", ".jpeg", ".png", ".gif", ".bmp", ".ico",
            ".pdf", ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx",
            ".zip", ".tar", ".gz", ".bz2", ".7z", ".rar",
            ".mp3", ".mp4", ".avi", ".mov", ".wav", ".flac"
        ]
    },
    "tools": {
        "search": {
            "description": "Search files by content or filename",
            "max_results": 50
        },
        "get_page": {
            "description": "Retrieve file content"
        },
        "get_page_children": {
            "description": "List directory contents"
        }
    },
    "search": {
        "fuzzy_threshold": 0.8,
        "enable_regex": True,
        "index_content": True,
        "enable_semantic": False,
        "semantic_model": "paraphrase-MiniLM-L3-v2"
    }
}


def load_config(config_path: str = "datasage.yaml") -> Dict[str, Any]:
    """Load configuration from YAML file with environment variable overrides."""
    config = DEFAULT_CONFIG.copy()
    
    # Load from YAML file if it exists
    if os.path.exists(config_path):
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                file_config = yaml.safe_load(f) or {}
                config = _merge_config(config, file_config)
        except Exception as e:
            print(f"Warning: Failed to load config file {config_path}: {e}")
    
    # Override with environment variables
    config = _apply_env_overrides(config)
    
    # Validate configuration
    _validate_config(config)
    
    return config


def _merge_config(base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
    """Recursively merge configuration dictionaries."""
    result = base.copy()
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = _merge_config(result[key], value)
        else:
            result[key] = value
    return result


def _apply_env_overrides(config: Dict[str, Any]) -> Dict[str, Any]:
    """Apply environment variable overrides to configuration."""
    # Server overrides
    if os.getenv("DATASAGE_NAME"):
        config["server"]["name"] = os.getenv("DATASAGE_NAME")
    if os.getenv("DATASAGE_DESCRIPTION"):
        config["server"]["description"] = os.getenv("DATASAGE_DESCRIPTION")
    
    # Paths override
    if os.getenv("DATASAGE_PATHS"):
        paths = os.getenv("DATASAGE_PATHS").split(",")
        config["paths"] = [{"path": p.strip()} for p in paths if p.strip()]
    
    # Settings overrides
    if os.getenv("DATASAGE_MAX_DEPTH"):
        try:
            config["settings"]["max_depth"] = int(os.getenv("DATASAGE_MAX_DEPTH"))
        except ValueError:
            pass
    
    if os.getenv("DATASAGE_MAX_FILE_SIZE"):
        try:
            config["settings"]["max_file_size"] = int(os.getenv("DATASAGE_MAX_FILE_SIZE"))
        except ValueError:
            pass
    
    if os.getenv("DATASAGE_TEXT_DETECTION"):
        text_detection = os.getenv("DATASAGE_TEXT_DETECTION")
        if text_detection in ["auto", "extension", "content"]:
            config["settings"]["text_detection"] = text_detection
    
    if os.getenv("DATASAGE_EXCLUDED_EXTENSIONS"):
        extensions = [ext.strip() for ext in os.getenv("DATASAGE_EXCLUDED_EXTENSIONS").split(",")]
        config["settings"]["excluded_extensions"] = [ext for ext in extensions if ext]
    
    # Tool overrides
    if os.getenv("DATASAGE_SEARCH_MAX_RESULTS"):
        try:
            config["tools"]["search"]["max_results"] = int(os.getenv("DATASAGE_SEARCH_MAX_RESULTS"))
        except ValueError:
            pass
    
    # Tool description overrides
    if os.getenv("DATASAGE_TOOL_SEARCH_DESC"):
        config["tools"]["search"]["description"] = os.getenv("DATASAGE_TOOL_SEARCH_DESC")
    if os.getenv("DATASAGE_TOOL_GET_PAGE_DESC"):
        config["tools"]["get_page"]["description"] = os.getenv("DATASAGE_TOOL_GET_PAGE_DESC")
    if os.getenv("DATASAGE_TOOL_GET_PAGE_CHILDREN_DESC"):
        config["tools"]["get_page_children"]["description"] = os.getenv("DATASAGE_TOOL_GET_PAGE_CHILDREN_DESC")
    
    # Search configuration overrides
    if os.getenv("DATASAGE_FUZZY_THRESHOLD"):
        try:
            threshold = float(os.getenv("DATASAGE_FUZZY_THRESHOLD"))
            if 0.0 <= threshold <= 1.0:
                config["search"]["fuzzy_threshold"] = threshold
        except ValueError:
            pass
    
    if os.getenv("DATASAGE_ENABLE_REGEX"):
        regex_val = os.getenv("DATASAGE_ENABLE_REGEX").lower()
        if regex_val in ["true", "false"]:
            config["search"]["enable_regex"] = regex_val == "true"
    
    if os.getenv("DATASAGE_INDEX_CONTENT"):
        index_val = os.getenv("DATASAGE_INDEX_CONTENT").lower()
        if index_val in ["true", "false"]:
            config["search"]["index_content"] = index_val == "true"
    
    if os.getenv("DATASAGE_ENABLE_SEMANTIC"):
        semantic_val = os.getenv("DATASAGE_ENABLE_SEMANTIC").lower()
        if semantic_val in ["true", "false"]:
            config["search"]["enable_semantic"] = semantic_val == "true"
    
    if os.getenv("DATASAGE_SEMANTIC_MODEL"):
        config["search"]["semantic_model"] = os.getenv("DATASAGE_SEMANTIC_MODEL")
    
    return config


def _validate_config(config: Dict[str, Any]) -> None:
    """Validate configuration values."""
    # Validate max_depth
    max_depth = config["settings"]["max_depth"]
    if not isinstance(max_depth, int) or max_depth < 1 or max_depth > 20:
        raise ValueError("max_depth must be an integer between 1 and 20")
    
    # Validate max_file_size
    max_file_size = config["settings"]["max_file_size"]
    if not isinstance(max_file_size, int) or max_file_size < 1:
        raise ValueError("max_file_size must be a positive integer")
    
    # Validate paths
    if not config["paths"]:
        print("Warning: No paths configured. Server will have limited functionality.")
    
    for path_config in config["paths"]:
        if isinstance(path_config, str):
            # Convert string paths to dict format
            path_config = {"path": path_config}
        
        if not isinstance(path_config, dict) or "path" not in path_config:
            raise ValueError("Each path must be a string or dict with 'path' key")
        
        path = Path(path_config["path"]).expanduser().resolve()
        if not path.exists():
            print(f"Warning: Configured path does not exist: {path}")


def get_allowed_paths(config: Dict[str, Any], config_path: str = "datasage.yaml") -> List[Path]:
    """Get list of allowed paths from configuration."""
    paths = []
    config_dir = Path(config_path).parent.resolve() if config_path != "datasage.yaml" else Path.cwd()
    
    for path_config in config["paths"]:
        if isinstance(path_config, str):
            path_str = path_config
        else:
            path_str = path_config["path"]
        
        path = Path(path_str)
        
        # If path is relative, resolve it relative to config file location
        if not path.is_absolute():
            path = (config_dir / path).resolve()
        else:
            path = path.expanduser().resolve()
            
        paths.append(path)
    
    return paths
