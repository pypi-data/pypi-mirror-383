import logging
import inspect
import tarfile
import zipfile
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Optional
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup
from huggingface_hub import snapshot_download
from huggingface_hub.errors import RepositoryNotFoundError
from tqdm import tqdm


class DatasetDownloader:
    def __init__(self, download_dir: str = "datasets", max_workers: int = 1):
        self.download_dir = Path(download_dir)
        self.max_workers = max_workers
        self.logger = logging.getLogger(self.__class__.__name__)

        self.available_datasets = {
            "Rfam": self.download_rfam_hf,
            "Rfam_original": self.download_rfam,
            "RNA_Puzzles": self.download_rna_puzzles,
            "CASP15": self.download_casp15,
            "RNAsolo2": self.download_rnasolo2,
        }

    def list_available_datasets(self):
        """List available datasets for download"""
        return list(self.available_datasets.keys())

    def _call_dataset_function(self, func, download_dir: str = None, max_workers: int = None):
        """Helper method to safely call dataset functions with appropriate parameters"""
        sig = inspect.signature(func)
        kwargs = {}

        self.download_dir.mkdir(parents=True, exist_ok=True)

        # Only pass parameters that the function accepts
        if 'download_dir' in sig.parameters:
            kwargs['download_dir'] = download_dir
        if 'max_workers' in sig.parameters:
            kwargs['max_workers'] = max_workers

        return func(**kwargs)

    def download_datasets(self, dataset_name: str = "all", download_dir: str = None, max_workers: int = None):
        """Download specified datasets"""
        if dataset_name == "all":
            for name, func in self.available_datasets.items():
                self.logger.info(f"Downloading dataset: {name}")
                self._call_dataset_function(func, download_dir=download_dir, max_workers=max_workers)
        elif dataset_name in self.available_datasets:
            self.logger.info(f"Downloading dataset: {dataset_name}")
            self._call_dataset_function(self.available_datasets[dataset_name],
                                        download_dir=download_dir, max_workers=max_workers)
        else:
            available = self.list_available_datasets()
            raise ValueError(f"Unknown dataset: {dataset_name}. Available datasets: {available}")

    def download_rfam(self, download_dir: str = None, max_workers: int = None):
        """Download Rfam dataset"""
        rfam_url = "https://ftp.ebi.ac.uk/pub/databases/Rfam/CURRENT/fasta_files/"
        if download_dir is None:
            download_dir = self.download_dir / "rfam"
        else:
            download_dir = Path(download_dir)

        # Use provided max_workers or fall back to instance default
        workers = max_workers if max_workers is not None else self.max_workers
        self.download_from_ftp(rfam_url, download_dir, max_workers=workers)

    def download_rfam_hf(self, download_dir: str = None, max_workers: int = None):
        """Download Rfam dataset from Hugging Face"""
        if download_dir is None:
            download_dir = self.download_dir / "rfam-standard"
        else:
            download_dir = Path(download_dir)

        repo_id = "Linorman616/rfam-standard"
        workers = max_workers if max_workers is not None else self.max_workers

        self.download_dataset_from_huggingface(repo_id, str(download_dir), max_workers=workers)

    def download_rna_puzzles(self, download_dir: str = None):
        """Download RNA Puzzles dataset"""
        puzzles_url = "https://github.com/Linorman/RNA-Puzzles-Standardized-Submissions/archive/refs/tags/1.4.zip"
        if download_dir is None:
            download_dir = self.download_dir / "rna_puzzles"
        else:
            download_dir = Path(download_dir)

        self.logger.info(f"Downloading RNA Puzzles from {puzzles_url}")
        local_dir = download_dir
        local_dir.mkdir(parents=True, exist_ok=True)

        local_zip_path = local_dir / "RNA-Puzzles-Standardized-Submissions-1.4.zip"
        success = self.download_from_url(puzzles_url, local_zip_path)
        if success:
            self.logger.info(f"Extracting {local_zip_path} to {local_dir}")
            self._unzip_file(local_zip_path, local_dir)
            local_zip_path.unlink(missing_ok=True)
        else:
            self.logger.error(f"Failed to download RNA Puzzles dataset from {puzzles_url}")

    def download_casp15(self, download_dir: str = None, max_workers: int = None):
        """Download CASP15 dataset"""
        if download_dir is None:
            download_dir = self.download_dir / "casp15"
        else:
            download_dir = Path(download_dir)

        repo_id = "Linorman616/CASP15"
        workers = max_workers if max_workers is not None else self.max_workers

        self.download_dataset_from_huggingface(repo_id, str(download_dir), max_workers=workers)

    def download_rnasolo2(self, download_dir: str = None, max_workers: int = None):
        """Download RNAsolo2 dataset"""
        if download_dir is None:
            download_dir = self.download_dir / "rnasolo2"
        else:
            download_dir = Path(download_dir)

        repo_id = "Linorman616/rnasolo2"
        workers = max_workers if max_workers is not None else self.max_workers

        self.download_dataset_from_huggingface(repo_id, str(download_dir), max_workers=workers)

    def download_from_ftp(self, ftp_url: str, local_dir: Path, max_workers: int = None):
        """Download files from an FTP URL"""
        workers = max_workers if max_workers is not None else self.max_workers

        self.logger.info(f"Downloading from FTP: {ftp_url}")

        # List files in the FTP directory
        response = requests.get(ftp_url)
        if response.status_code != 200:
            self.logger.error(f"Failed to access FTP URL: {ftp_url}")
            return
        soup = BeautifulSoup(response.text, 'html.parser')
        files = [
            a['href'] for a in soup.find_all('a', href=True)
            if a['href']
               and not a['href'].startswith(('/', '?', '#'))
               and not a['href'].endswith('/')
               and a['href'] not in ('../', './')
               and not any(x in a['href'] for x in ['?C=', '&O='])
        ]

        self.logger.info(f"Found {len(files)} files to download from {ftp_url}")
        local_dir.mkdir(parents=True, exist_ok=True)

        # filter out already downloaded files
        files_to_download = []
        for file in files:
            local_path = local_dir / file
            if local_path.exists() and local_path.stat().st_size > 0:
                self.logger.info(f"Skipping {file} (already exists and non-empty)")
            else:
                files_to_download.append(file)

        if not files_to_download:
            self.logger.info("All files already downloaded")
            return

        self.logger.info(f"Need to download {len(files_to_download)} files")

        with ThreadPoolExecutor(max_workers=workers) as executor:
            futures = {
                executor.submit(self._download_file_url, urljoin(ftp_url, file), local_dir / file): file
                for file in files_to_download
            }
            
            failed_downloads = []
            for future in tqdm(as_completed(futures), total=len(futures), desc="Downloading files"):
                file = futures[future]
                try:
                    success = future.result()
                    if success:
                        self.logger.debug(f"Successfully downloaded {file}")
                    else:
                        failed_downloads.append(file)
                        self.logger.error(f"Failed to download {file}")
                except Exception as e:
                    failed_downloads.append(file)
                    self.logger.error(f"Failed to download {file}: {str(e)}")
                    
            if failed_downloads:
                self.logger.warning(f"Failed to download {len(failed_downloads)} files: {failed_downloads}")


    def download_from_url(self, file_url: str, local_path: Path):
        """Download a single file from a URL"""
        local_path = Path(local_path)
        local_path.parent.mkdir(parents=True, exist_ok=True)

        if local_path.exists() and local_path.stat().st_size > 0:
            self.logger.info(f"File {local_path} already exists and is non-empty, skipping download")
            return True

        return self._download_file_url(file_url, local_path)

    def download_dataset_from_huggingface(self, repo_id: str, local_dir: str, proxies: Optional[dict] = None,
                                          max_workers: int = 8):
        """Download a repository from Hugging Face.

        Args:
            repo_id: The repository ID on Hugging Face
            local_dir: The local directory to save the model
            proxies: Proxies to use for the download
            max_workers: Maximum number of workers for downloading
        """
        self.logger.info(f"Downloading repository {repo_id} to {local_dir}")

        try:
            snapshot_download(
                repo_type="dataset",
                repo_id=repo_id,
                local_dir=local_dir,
                proxies=proxies,
                max_workers=max_workers
            )
            self.logger.info(f"Successfully downloaded repository {repo_id}")
        except RepositoryNotFoundError:
            self.logger.error(f"Repository {repo_id} not found on Hugging Face")
            raise
        except Exception as e:
            self.logger.error(f"Failed to download repository {repo_id}: {str(e)}")
            raise

    def _unzip_file(self, zip_path: Path, extract_to: Path):
        if zip_path.suffix == '.zip':
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(extract_to)
        elif zip_path.suffix in ['.tar', '.gz', '.tgz', '.bz2']:
            with tarfile.open(zip_path, 'r:*') as tar_ref:
                tar_ref.extractall(extract_to)
        else:
            self.logger.warning(f"Unsupported archive format for {zip_path}, skipping extraction")
            return False

        return True


    def _download_file_url(self, url: str, local_path: Path):
        temp_path = local_path.with_suffix(local_path.suffix + '.tmp')
        
        try:
            response = requests.get(url, stream=True, timeout=30)
            if response.status_code != 200:
                self.logger.error(f"HTTP {response.status_code} for {url}")
                return False

            # get expected size from headers
            content_length = response.headers.get('content-length')
            expected_size = int(content_length) if content_length else None
            if content_length:
                if expected_size == 0:
                    self.logger.warning(f"File {url} has zero size")
                    return False

            # Stream download to temp file
            downloaded_size = 0
            with open(temp_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded_size += len(chunk)

            # validate size
            if downloaded_size == 0:
                self.logger.error(f"Downloaded file {url} is empty")
                temp_path.unlink(missing_ok=True)
                return False

            if content_length and downloaded_size != expected_size:
                self.logger.error(f"Size mismatch for {url}: expected {expected_size}, got {downloaded_size}")
                temp_path.unlink(missing_ok=True)
                return False

            # Move temp file to final location
            if local_path.exists():
                local_path.unlink()
            temp_path.rename(local_path)
            
            return True

        except Exception as e:
            self.logger.error(f"Error downloading {url}: {str(e)}")
            temp_path.unlink(missing_ok=True)
            return False
