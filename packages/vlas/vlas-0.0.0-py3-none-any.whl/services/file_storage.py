import json
from pathlib import Path
from typing import Dict, Any, Optional, List
import uuid
from datetime import datetime


class FileMetadataStorage:
    def __init__(self, storage_path: Path = Path("file_metadata.json")):
        self.storage_path = storage_path
        self.metadata = self._load_metadata()

    def _load_metadata(self) -> Dict[str, Any]:
        if self.storage_path.exists():
            with open(self.storage_path, "r") as f:
                return json.load(f)
        return {}

    def _save_metadata(self):
        with open(self.storage_path, "w") as f:
            json.dump(self.metadata, f, indent=2)

    def add_file(
        self,
        file_id: str,
        gemini_name: str,
        gemini_uri: str,
        original_name: str,
        mime_type: str,
        size_bytes: int,
        display_name: str,
        local_path: Optional[str] = None
    ) -> Dict[str, Any]:
        """Add file metadata"""
        file_data = {
            "file_id": file_id,
            "gemini_name": gemini_name,
            "gemini_uri": gemini_uri,
            "original_name": original_name,
            "mime_type": mime_type,
            "size_bytes": size_bytes,
            "display_name": display_name,
            "uploaded_at": datetime.utcnow().isoformat(),
        }

        if local_path:
            file_data["local_path"] = local_path

        self.metadata[file_id] = file_data
        self._save_metadata()
        return file_data

    def get_file(self, file_id: str) -> Optional[Dict[str, Any]]:
        """Get file metadata by ID"""
        return self.metadata.get(file_id)

    def get_file_by_gemini_name(self, gemini_name: str) -> Optional[Dict[str, Any]]:
        """Get file metadata by Gemini file name"""
        for file_data in self.metadata.values():
            if file_data.get("gemini_name") == gemini_name:
                return file_data
        return None

    def list_files(self) -> List[Dict[str, Any]]:
        """List all file metadata"""
        return list(self.metadata.values())

    def delete_file(self, file_id: str) -> bool:
        """Delete file metadata"""
        if file_id in self.metadata:
            del self.metadata[file_id]
            self._save_metadata()
            return True
        return False

    def delete_file_by_gemini_name(self, gemini_name: str) -> bool:
        """Delete file metadata by Gemini name"""
        for file_id, file_data in list(self.metadata.items()):
            if file_data.get("gemini_name") == gemini_name:
                del self.metadata[file_id]
                self._save_metadata()
                return True
        return False


# Global instance
file_storage = FileMetadataStorage()