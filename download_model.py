import os
import sys

workspace_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(workspace_dir)

from src.embedding_utils import get_embedding_model

print("Initializing download of all-MiniLM-L6-v2 to local cache...")
model = get_embedding_model(local_files_only=False)
print("Model download and cache completed successfully.")
