import os
import shutil


def safe_delete(file_path: str | None):
    """Safely delete a file and its temporary directory."""
    if not file_path:
        return
    try:
        if os.path.exists(file_path):
            tmp_dir = os.path.dirname(file_path)
            os.remove(file_path)
            # Attempt to delete temp dir
            shutil.rmtree(tmp_dir, ignore_errors=True)
    except Exception as e:
        print(f"Cleanup error: {e}")
      
