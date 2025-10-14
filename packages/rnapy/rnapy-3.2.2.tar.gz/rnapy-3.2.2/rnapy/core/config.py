import logging
from pathlib import Path
from typing import Dict, Optional, Union, Type

import yaml
from pydantic import Field, field_validator
from pydantic_settings import SettingsConfigDict, BaseSettings


class BaseConfig(BaseSettings):
    """Base configuration class defining common settings"""

    # Device and performance settings
    device: str = Field(default="auto", description="Compute device: cpu, cuda, cuda:0, auto")
    precision: str = Field(default="fp32", description="Model precision: fp16, fp32")
    batch_size: int = Field(default=1, ge=1, description="Batch size")

    # Sequence processing settings
    max_sequence_length: int = Field(default=1024, ge=1, description="Maximum sequence length")

    # Path settings
    checkpoint_path: Optional[Path] = Field(default=None, description="Model checkpoint path")
    cache_dir: Path = Field(default=Path("./cache"), description="Cache directory")

    # Output settings
    output_dir: Path = Field(default=Path("./outputs"), description="Output directory")
    validate_output: bool = Field(default=True, description="Validate output results")

    # Performance settings
    num_workers: int = Field(default=4, ge=0, description="Number of data loader workers")
    timeout_seconds: int = Field(default=3600, ge=1, description="Timeout in seconds")

    model_config = SettingsConfigDict(
        # Load from environment variables with prefix RNAPY_
        env_prefix='RNAPY_',
        # Load from .env file
        env_file='.env',
        env_file_encoding='utf-8',
        # Allow extra fields
        extra='allow',
        # Case-insensitive
        case_sensitive=False,
        # Validate on assignment
        validate_assignment=True
    )
    
    def update(self, other: Union['BaseConfig', Dict, None]) -> 'BaseConfig':
        """
        Update configuration from another config instance or dictionary

        Args:
            other: Another configuration instance or a dictionary

        Returns:
            self to support chaining
        """
        if other is None:
            return self
            
        if isinstance(other, BaseConfig):
            # Update from another config instance
            update_dict = other.model_dump(exclude_unset=True)
        elif isinstance(other, dict):
            # Update from dictionary
            update_dict = other
        else:
            raise TypeError(f"Cannot update config from type: {type(other)}")
        
        # Update fields
        for key, value in update_dict.items():
            if hasattr(self, key):
                setattr(self, key, value)
        
        return self
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'BaseConfig':
        """Create configuration instance from a dictionary"""
        return cls(**data)
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return self.model_dump()
    
    @field_validator('device')
    def validate_device(cls, v):
        """Validate device setting"""
        if v == "auto":
            try:
                import torch
                return 'cuda' if torch.cuda.is_available() else 'cpu'
            except ImportError:
                return 'cpu'
        valid_devices = ['cpu', 'cuda']
        if v not in valid_devices and not v.startswith('cuda:'):
            raise ValueError(f"Invalid device: {v}. Must be one of {valid_devices} or 'cuda:N'")
        return v
    
    @field_validator('precision')
    def validate_precision(cls, v):
        """Validate precision setting"""
        valid_precision = ['fp16', 'fp32', 'float16', 'float32']
        if v not in valid_precision:
            raise ValueError(f"Invalid precision: {v}. Must be one of {valid_precision}")
        # Normalize values
        if v in ['float16', 'fp16']:
            return 'fp16'
        elif v in ['float32', 'fp32']:
            return 'fp32'
        return v
    
    @field_validator('cache_dir', 'output_dir', 'checkpoint_path', mode="before")
    def convert_to_path(cls, v):
        """Convert string to Path object"""
        if v is None:
            return v
        return Path(v)


class GlobalConfig(BaseConfig):
    """Global configuration"""

    # Logging settings
    log_level: str = Field(default="INFO", description="Log level")
    log_format: str = Field(
        default="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        description="Log format"
    )
    
    # Global performance settings
    enable_mixed_precision: bool = Field(default=False, description="Enable mixed precision")
    gradient_checkpointing: bool = Field(default=False, description="Gradient checkpointing")
    dataloader_pin_memory: bool = Field(default=True, description="Pin memory for data loader")

    @field_validator('log_level')
    def validate_log_level(cls, v):
        """Validate log level"""
        valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        if v.upper() not in valid_levels:
            raise ValueError(f"Invalid log level: {v}. Must be one of {valid_levels}")
        return v.upper()


class ConfigManager:
    """Unified configuration manager"""

    def __init__(self, config_dir: Union[str, Path] = "configs"):
        self.config_dir = Path(config_dir)
        self.config_dir.mkdir(exist_ok=True, parents=True)
        self.logger = logging.getLogger(self.__class__.__name__)
        self._configs: Dict[str, BaseConfig] = {}

    def _plainify(self, obj):
        """Recursively convert non-serializable objects (like Path) to plain types (e.g., str)."""
        if isinstance(obj, Path):
            return str(obj)
        if isinstance(obj, dict):
            return {k: self._plainify(v) for k, v in obj.items()}
        if isinstance(obj, (list, tuple, set)):
            t = type(obj)
            return t(self._plainify(v) for v in obj)
        return obj
    
    def load_config(
        self,
        config_class: Type[BaseConfig],
        config_name: Optional[str] = None,
        config_file: Optional[Union[str, Path]] = None,
        **kwargs
    ) -> BaseConfig:
        """
        Load configuration

        Args:
            config_class: Configuration class
            config_name: Configuration name for caching
            config_file: Path to configuration file
            **kwargs: Additional configuration parameters

        Returns:
            Configuration instance
        """
        # If a config file is provided, load it first
        file_config = {}
        if config_file:
            config_path = Path(config_file)
            # Only prepend config_dir when config_file has no parent directory (bare filename)
            if not config_path.is_absolute():
                if config_path.parent == Path('.'):
                    config_path = self.config_dir / config_path
            
            if config_path.exists():
                # Use SafeLoader with custom constructor for WindowsPath tags
                class _SafePathLoader(yaml.SafeLoader):
                    pass
                
                def _construct_windows_path(loader, node):
                    seq = loader.construct_sequence(node)
                    try:
                        p = Path(*seq)
                    except Exception:
                        # Fallback: join as string
                        p = Path("/".join(str(s) for s in seq))
                    return str(p)
                
                _SafePathLoader.add_constructor(
                    'tag:yaml.org,2002:python/object/apply:pathlib.WindowsPath',
                    _construct_windows_path
                )
                
                with open(config_path, 'r', encoding='utf-8') as f:
                    if config_path.suffix.lower() in ['.yaml', '.yml']:
                        try:
                            file_config = yaml.load(f, Loader=_SafePathLoader) or {}
                        except Exception as e:
                            self.logger.warning(f"Failed to load YAML config safely from {config_path}: {e}. Using empty config.")
                            file_config = {}
                    elif config_path.suffix.lower() == '.json':
                        import json
                        file_config = json.load(f)
                self.logger.info(f"Loaded config from file: {config_path}")
            else:
                self.logger.warning(f"Config file not found: {config_path}")
        
        # Merge configuration: file config + kwargs
        merged_config = {**file_config, **kwargs}
        
        # Create configuration instance
        config_instance = config_class(**merged_config)
        
        # Cache configuration
        if config_name:
            self._configs[config_name] = config_instance
            
        return config_instance
    
    def get_config(self, config_name: str) -> BaseConfig:
        """
        Get configuration; create a default one if not exists

        Args:
            config_name: Configuration name

        Returns:
            Configuration instance
        """
        # Return from cache if available
        if config_name in self._configs:
            return self._configs[config_name]
        
        # If not cached, try to create a default configuration
        if config_name == "default" or config_name == "global":
            config_instance = GlobalConfig()
        else:
            # For provider configuration, create a basic configuration
            config_instance = BaseConfig()
        
        # Cache configuration
        self._configs[config_name] = config_instance
        return config_instance
    
    def save_config(self, config_name: str, config: BaseConfig, file_format: str = 'yaml'):
        """
        Save configuration to file

        Args:
            config_name: Configuration name
            config: Configuration instance
            file_format: File format ('yaml' or 'json')
        """
        data = self._plainify(config.model_dump())
        if file_format == 'yaml':
            config_path = self.config_dir / f"{config_name}.yaml"
            with open(config_path, 'w', encoding='utf-8') as f:
                yaml.safe_dump(data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
        elif file_format == 'json':
            config_path = self.config_dir / f"{config_name}.json"
            with open(config_path, 'w', encoding='utf-8') as f:
                import json
                json.dump(data, f, indent=2, ensure_ascii=False)
        else:
            raise ValueError("file_format must be 'yaml' or 'json'")
            
        self.logger.info(f"Saved config to: {config_path}")
    
    def create_default_configs(self):
        """Create default configuration files"""
        if not (self.config_dir / "default.yaml").exists():
            global_config = GlobalConfig()
            self.save_config("default", global_config)
        
        self.logger.info("Default configs created")


config_manager = ConfigManager()
