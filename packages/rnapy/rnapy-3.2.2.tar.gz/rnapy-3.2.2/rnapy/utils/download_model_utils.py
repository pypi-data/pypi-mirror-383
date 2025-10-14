# Download pretrained models from Hugging Face
import os
import logging
from pathlib import Path
from typing import Optional, Dict

from huggingface_hub import snapshot_download, hf_hub_download, HfApi
from huggingface_hub.utils import RepositoryNotFoundError, EntryNotFoundError

logger = logging.getLogger("huggingface_hub")
logger.setLevel(logging.WARNING)

MODEL_REGISTRY = {
    "rna_fm": {
        "repo_id": "Linorman616/rnapy_models",
        "filename": "models/rna_fm_pretrained.pth",
        "local_dir": ".",
        "description": "RNA-FM pretrained model for RNA sequence analysis"
    },
    "rna-fm": {
        "repo_id": "Linorman616/rnapy_models",
        "filename": "models/rna_fm_pretrained.pth",
        "local_dir": ".",
        "description": "RNA-FM pretrained model for RNA sequence analysis"
    },
    "mrna_fm": {
        "repo_id": "Linorman616/rnapy_models",
        "filename": "models/mrna_fm_pretrained.pth",
        "local_dir": ".",
        "description": "mRNA-FM pretrained model for mRNA sequence analysis"
    },
    "mrna-fm": {
        "repo_id": "Linorman616/rnapy_models",
        "filename": "models/mrna_fm_pretrained.pth",
        "local_dir": ".",
        "description": "mRNA-FM pretrained model for mRNA sequence analysis"
    },
    "rhofold": {
        "repo_id": "Linorman616/rnapy_models",
        "filename": "models/rho_fold_pretrained.pt",
        "local_dir": ".",
        "description": "RhoFold pretrained model for RNA 3D structure prediction"
    },
    "rho-fold": {
        "repo_id": "Linorman616/rnapy_models",
        "filename": "models/rho_fold_pretrained.pt",
        "local_dir": ".",
        "description": "RhoFold pretrained model for RNA 3D structure prediction"
    },
    "rhodesign": {
        "repo_id": "Linorman616/rnapy_models",
        "filename": "models/rho_design_pretrained.pth",
        "local_dir": ".",
        "description": "RhoDesign pretrained model for RNA inverse folding"
    },
    "rho-design": {
        "repo_id": "Linorman616/rnapy_models",
        "filename": "models/rho_design_pretrained.pth",
        "local_dir": ".",
        "description": "RhoDesign pretrained model for RNA inverse folding"
    },
    "ribodiffusion": {
        "repo_id": "Linorman616/rnapy_models",
        "filename": "models/ribo_diffusion_pretrained.pth",
        "local_dir": ".",
        "description": "RiboDiffusion pretrained model for RNA sequence generation"
    },
    "ribo-diffusion": {
        "repo_id": "Linorman616/rnapy_models",
        "filename": "models/ribo_diffusion_pretrained.pth",
        "local_dir": ".",
        "description": "RiboDiffusion pretrained model for RNA sequence generation"
    },
    "rna_msm": {
        "repo_id": "Linorman616/rnapy_models",
        "filename": "models/rna_msm_pretrained.pt",
        "local_dir": "./",
        "description": "RNA-MSM pretrained model for MSA analysis"
    },
    "rna-msm": {
        "repo_id": "Linorman616/rnapy_models",
        "filename": "models/rna_msm_pretrained.pt",
        "local_dir": ".",
        "description": "RNA-MSM pretrained model for MSA analysis"
    },
}

def get_model_info_from_registry(model_name: str) -> Optional[Dict[str, str]]:
    """Get model information from registry
    
    Args:
        model_name: Name of the model
        
    Returns:
        Model info dict or None if not found
    """
    return MODEL_REGISTRY.get(model_name.lower())

def get_default_model_path(model_name: str) -> Optional[str]:
    """Get default local path for a model
    
    Args:
        model_name: Name of the model
        
    Returns:
        Default local file path or None
    """
    model_info = get_model_info_from_registry(model_name)
    if model_info:
        return os.path.join(model_info["local_dir"], model_info["filename"])
    return None

def auto_download_model(model_name: str, force_download: bool = False, 
                       proxies: Optional[dict] = None) -> str:
    """Automatically download model from Hugging Face Hub
    
    Args:
        model_name: Name of the model to download
        force_download: Force re-download even if file exists
        proxies: Proxies to use for download
        
    Returns:
        Path to downloaded model file
        
    Raises:
        ValueError: If model not found in registry
        ModelDownloadError: If download fails
    """
    model_info = get_model_info_from_registry(model_name)
    if not model_info:
        available_models = list(MODEL_REGISTRY.keys())
        raise ValueError(f"Model '{model_name}' not found in registry. Available models: {available_models}")
        
    local_dir = Path(model_info["local_dir"])
    local_file_path = local_dir / model_info["filename"] 
    
    # Check if file already exists
    if local_file_path.exists() and not force_download:
        logger.info(f"Model {model_name} already exists at {local_file_path}")
        return str(local_file_path)
        
    # Create directory 
    local_dir.mkdir(parents=True, exist_ok=True)
    
    logger.info(f"Downloading {model_name} from {model_info['repo_id']}")
    logger.info(f"Description: {model_info['description']}")
    logger.info(f"Target: {local_file_path}")
    
    try:
        downloaded_path = download_file_from_huggingface(
            repo_id = model_info["repo_id"],
            filename = model_info["filename"],
            local_dir = str(local_dir),
            proxies = proxies
        )
        
        logger.info(f"Successfully downloaded {model_name} to {downloaded_path}")
        return downloaded_path
        
    except Exception as e:
        logger.error(f"Failed to download {model_name}: {str(e)}")
        raise ModelDownloadError(f"Failed to download model {model_name}: {str(e)}")

def list_available_models() -> Dict[str, Dict[str, str]]:
    """List all available models in registry
    
    Returns:
        Dictionary of model names and their info
    """
    return MODEL_REGISTRY.copy()

def verify_model_file(model_path: str, min_size_mb: float = 1.0) -> bool:
    """Verify downloaded model file integrity
    
    Args:
        model_path: Path to model file
        min_size_mb: Minimum expected file size in MB
        
    Returns:
        True if file appears valid, False otherwise
    """
    try:
        path = Path(model_path)
        if not path.exists():
            return False
            
        file_size_mb = path.stat().st_size / (1024 * 1024)
        if file_size_mb < min_size_mb:
            logger.warning(f"Model file {model_path} seems too small ({file_size_mb:.2f} MB)")
            return False
            
        return True
        
    except Exception as e:
        logger.error(f"Error verifying model file {model_path}: {str(e)}")
        return False

class ModelDownloadError(Exception):
    """Exception raised when model download fails"""
    pass


def download_repo_from_huggingface(repo_id: str, local_dir: str, proxies: Optional[dict] = None, max_workers: int = 8):
    """Download a pretrained model repository from Hugging Face.

    Args:
        repo_id: The repository ID on Hugging Face
        local_dir: The local directory to save the model
        proxies: Proxies to use for the download
        max_workers: Maximum number of workers for downloading
    """
    logger.info(f"Downloading repository {repo_id} to {local_dir}")

    try:
        snapshot_download(
            repo_id=repo_id,
            local_dir=local_dir,
            proxies=proxies,
            max_workers=max_workers
        )
        logger.info(f"Successfully downloaded repository {repo_id}")
    except RepositoryNotFoundError:
        logger.error(f"Repository {repo_id} not found on Hugging Face")
        raise
    except Exception as e:
        logger.error(f"Failed to download repository {repo_id}: {str(e)}")
        raise


def download_file_from_huggingface(repo_id: str, filename: str, local_dir: str, proxies: Optional[dict] = None) -> str:
    """Download a specific file from a Hugging Face repository.

    Args:
        repo_id: The repository ID on Hugging Face
        filename: The name of the file to download
        local_dir: The local directory to save the file
        proxies: Proxies to use for the download

    Returns:
        Path to the downloaded file
    """
    logger.info(f"Downloading {filename} from {repo_id}")

    try:
        file_path = hf_hub_download(
            repo_id=repo_id,
            filename=filename,
            local_dir=local_dir,
            proxies=proxies
        )
        logger.info(f"Successfully downloaded {filename} to {file_path}")
        return file_path
    except EntryNotFoundError:
        logger.error(f"File {filename} not found in repository {repo_id}")
        raise
    except Exception as e:
        logger.error(f"Failed to download {filename}: {str(e)}")
        raise


def get_model_info(repo_id: str, filename: str) -> dict:
    """Get information about a model file without downloading it.

    Args:
        repo_id: The repository ID on Hugging Face
        filename: The name of the file

    Returns:
        Dictionary with model information
    """
    try:
        api = HfApi()

        repo_info = api.repo_info(repo_id)
        file_info = None

        for sibling in repo_info.siblings:
            if sibling.rfilename == filename:
                file_info = sibling
                break

        if file_info:
            return {
                "filename": filename,
                "size_mb": file_info.size / (1024*1024) if file_info.size else None,
                "last_modified": file_info.last_commit.date if file_info.last_commit else None,
                "exists": True
            }
        else:
            return {"filename": filename, "exists": False}

    except Exception as e:
        logger.warning(f"Could not get model info for {filename}: {str(e)}")
        return {"filename": filename, "exists": None, "error": str(e)}
