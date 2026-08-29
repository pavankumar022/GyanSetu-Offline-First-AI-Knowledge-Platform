import os
import json
import shutil
import hashlib
from typing import Dict, Any, List
from local_ai.vector_store import index_file, remove_pack_indices

# Root paths
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CLOUD_DIR = os.path.join(ROOT_DIR, "knowledge_packs")
DEVICE_DIR = os.path.join(ROOT_DIR, "device_storage")

os.makedirs(CLOUD_DIR, exist_ok=True)
os.makedirs(DEVICE_DIR, exist_ok=True)

def get_installed_packs() -> List[Dict[str, Any]]:
    """Scan device_storage directory for installed packs."""
    installed = []
    if not os.path.exists(DEVICE_DIR):
        return installed
        
    for item in os.listdir(DEVICE_DIR):
        item_path = os.path.join(DEVICE_DIR, item)
        if os.path.isdir(item_path) and item != "models":
            meta_path = os.path.join(item_path, "metadata.json")
            if os.path.exists(meta_path):
                try:
                    with open(meta_path, "r", encoding="utf-8") as f:
                        meta = json.load(f)
                        installed.append(meta)
                except Exception as e:
                    print(f"Error reading metadata for {item}: {e}")
    return installed

def get_pack_local_meta(pack_id: str) -> Dict[str, Any]:
    meta_path = os.path.join(DEVICE_DIR, pack_id, "metadata.json")
    if os.path.exists(meta_path):
        with open(meta_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def calculate_delta(pack_id: str, server_files: List[Dict[str, Any]]) -> List[str]:
    """Compare local files and server files using content hashes. Return list of files to download."""
    local_pack_dir = os.path.join(DEVICE_DIR, pack_id)
    files_to_download = []
    
    for s_file in server_files:
        filename = s_file["path"]
        server_hash = s_file["hash"]
        local_filepath = os.path.join(local_pack_dir, filename)
        
        if not os.path.exists(local_filepath):
            # Missing locally
            files_to_download.append(filename)
        else:
            # Check content hash
            with open(local_filepath, "rb") as f:
                content = f.read()
                local_hash = hashlib.md5(content).hexdigest()
            if local_hash != server_hash:
                files_to_download.append(filename)
                
    return files_to_download

def perform_sync(pack_id: str, pack_title: str, pack_icon: str, pack_category: str, server_version: str, server_files: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Execute a delta sync, copying only changed files, and indexing them."""
    local_pack_dir = os.path.join(DEVICE_DIR, pack_id)
    os.makedirs(local_pack_dir, exist_ok=True)
    
    cloud_pack_dir = os.path.join(CLOUD_DIR, pack_id)
    
    # 1. Identify which files need sync
    files_to_sync = calculate_delta(pack_id, server_files)
    
    sync_details = []
    bytes_transferred = 0
    
    # 2. Copy and re-index only the synced files
    for filename in files_to_sync:
        source_path = os.path.join(cloud_pack_dir, filename)
        dest_path = os.path.join(local_pack_dir, filename)
        
        if os.path.exists(source_path):
            # Read file text
            with open(source_path, "r", encoding="utf-8") as f:
                content = f.read()
                
            # Write to device storage
            with open(dest_path, "w", encoding="utf-8") as f:
                f.write(content)
                
            # Track transfer size
            bytes_transferred += os.path.getsize(dest_path)
            sync_details.append(f"Synced '{filename}'")
            
            # Re-index this specific file in vector store
            index_file(pack_id, os.path.join(pack_id, filename), content)
        else:
            sync_details.append(f"Error: source file '{filename}' missing on server")
            
    # 3. Update local metadata
    local_meta = {
        "id": pack_id,
        "title": pack_title,
        "icon": pack_icon,
        "category": pack_category,
        "version": server_version,
        "size_mb": int(os.path.getsize(local_pack_dir) / (1024 * 1024)) if os.path.exists(local_pack_dir) else 10,
        "files_count": len(server_files),
        "files_metadata": server_files
    }
    
    # Simple size estimate if size is 0
    if local_meta["size_mb"] == 0:
        # Generate a mock size for UI representation
        local_meta["size_mb"] = int(sum(f["size_bytes"] for f in server_files) / (1024 * 1024)) or 1
        
    with open(os.path.join(local_pack_dir, "metadata.json"), "w", encoding="utf-8") as f:
        json.dump(local_meta, f, indent=2)
        
    return {
        "files_synced": files_to_sync,
        "bytes_transferred": bytes_transferred,
        "details": ", ".join(sync_details) if sync_details else "Already up to date."
    }

def delete_local_pack(pack_id: str):
    """Delete a pack folder and remove all indices from vector store."""
    local_pack_dir = os.path.join(DEVICE_DIR, pack_id)
    if os.path.exists(local_pack_dir):
        shutil.rmtree(local_pack_dir)
        
    # Remove from vector index
    remove_pack_indices(pack_id)
