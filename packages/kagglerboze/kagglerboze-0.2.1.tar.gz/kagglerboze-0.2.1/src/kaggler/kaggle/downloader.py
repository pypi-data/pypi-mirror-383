"""
Competition Data Downloader

Handles downloading and organizing competition data
"""

import os
import zipfile
from typing import List, Optional
from pathlib import Path


class CompetitionDownloader:
    """Download and organize competition data"""

    def __init__(self, api):
        self.api = api

    def download(
        self,
        competition: str,
        path: Optional[str] = None,
        files: Optional[List[str]] = None
    ) -> str:
        """
        Download competition data

        Args:
            competition: Competition name
            path: Download directory
            files: Specific files to download

        Returns:
            Path to downloaded data
        """
        # Set default path
        if path is None:
            path = f"./data/{competition}"

        # Create directory
        os.makedirs(path, exist_ok=True)

        # Download files
        if files:
            for file in files:
                print(f"Downloading {file}...")
                self.api.competition_download_file(competition, file, path=path)
        else:
            print(f"Downloading all files for {competition}...")
            self.api.competition_download_files(competition, path=path)

        # Unzip files
        self._unzip_files(path)

        print(f"✓ Downloaded to {path}")
        return path

    def _unzip_files(self, path: str):
        """Unzip downloaded files"""
        path_obj = Path(path)

        for zip_file in path_obj.glob("*.zip"):
            print(f"Extracting {zip_file.name}...")
            with zipfile.ZipFile(zip_file, 'r') as zip_ref:
                zip_ref.extractall(path)
            # Remove zip file after extraction
            zip_file.unlink()

    def list_competition_files(self, competition: str) -> List[str]:
        """
        List available files for competition

        Args:
            competition: Competition name

        Returns:
            List of file names
        """
        files = self.api.competition_list_files(competition)
        return [f.name for f in files]

    def get_file_info(self, competition: str) -> List[dict]:
        """
        Get detailed file information

        Args:
            competition: Competition name

        Returns:
            List of file info dicts
        """
        files = self.api.competition_list_files(competition)
        return [
            {
                "name": f.name,
                "size": f.totalBytes,
                "description": f.description,
            }
            for f in files
        ]
