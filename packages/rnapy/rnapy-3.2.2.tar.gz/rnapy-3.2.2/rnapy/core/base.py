from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Union
import torch
import logging


class BaseModel(ABC):
    def __init__(self, config: Dict[str, Any], device: str = "cpu"):
        self.config = config
        self.device = device
        self.model = None
        self.logger = logging.getLogger(self.__class__.__name__)
        
    @abstractmethod
    def load_model(self, checkpoint_path: str) -> None:
        pass
    
    @abstractmethod
    def predict(self, input_data: Any) -> Dict[str, Any]:
        pass
    
    @abstractmethod
    def preprocess(self, raw_input: Any) -> Any:
        pass
    
    @abstractmethod
    def postprocess(self, raw_output: Any) -> Dict[str, Any]:
        pass
    
    def to_device(self, data: Any) -> Any:
        if isinstance(data, torch.Tensor):
            return data.to(self.device)
        elif isinstance(data, dict):
            return {k: self.to_device(v) for k, v in data.items()}
        elif isinstance(data, list):
            return [self.to_device(item) for item in data]
        else:
            return data


class BasePredictor(ABC):
    def __init__(self, model: BaseModel):
        self.model = model
        self.logger = logging.getLogger(self.__class__.__name__)
    
    @abstractmethod
    def predict_single(self, input_data: Any) -> Dict[str, Any]:
        pass
    
    @abstractmethod
    def predict_batch(self, input_batch: List[Any]) -> List[Dict[str, Any]]:
        pass
    
    def validate_input(self, input_data: Any) -> bool:
        return True


class ModelRegistry:
    def __init__(self):
        self._models = {}
    
    def register(self, name: str, model_class: type):
        if not issubclass(model_class, BaseModel):
            raise ValueError(f"Model class must inherit from BaseModel")
        self._models[name] = model_class
    
    def get_model(self, name: str) -> Optional[type]:
        return self._models.get(name)
    
    def list_models(self) -> List[str]:
        return list(self._models.keys()) 