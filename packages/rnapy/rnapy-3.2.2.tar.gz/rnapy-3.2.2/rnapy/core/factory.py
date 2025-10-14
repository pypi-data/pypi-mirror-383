from typing import Dict, Any, Type, List
from .base import BaseModel, ModelRegistry
import logging


class ModelFactory:
    def __init__(self):
        self.registry = ModelRegistry()
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def create_model(self, model_name: str, config: Dict[str, Any], 
                    device: str = "cpu") -> BaseModel:
        model_class = self.registry.get_model(model_name)
        if model_class is None:
            available_models = self.registry.list_models()
            raise ValueError(f"Unknown model: {model_name}. Available models: {available_models}")
        
        self.logger.info(f"Creating model: {model_name} on device: {device}")
        return model_class(config=config, device=device)
    
    def register_model(self, name: str, model_class: Type[BaseModel]):
        self.registry.register(name, model_class)
        self.logger.info(f"Registered model: {name}")
    
    def list_models(self) -> List[str]:
        return self.registry.list_models()
    
    def get_model_info(self, model_name: str) -> Dict[str, Any]:
        model_class = self.registry.get_model(model_name)
        if model_class is None:
            return {}
        
        return {
            'name': model_name,
            'class': model_class.__name__,
            'module': model_class.__module__,
            'doc': model_class.__doc__
        } 