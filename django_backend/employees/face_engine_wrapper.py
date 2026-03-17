import os
import sys
from pathlib import Path

_engine_instance = None


def _find_face_engine_root():
    """Encontra a pasta que contém face_engine_api.py."""
    current = Path(__file__).resolve()
    for parent in current.parents:
        candidate = parent / 'face_engine_api.py'
        if candidate.exists():
            return str(parent)
    return None


def get_engine():
    """Retorna uma instância singleton do motor facial do projeto."""
    global _engine_instance
    if _engine_instance is None:
        project_root = _find_face_engine_root()
        if project_root and project_root not in sys.path:
            sys.path.insert(0, project_root)
        from face_engine_api import FaceEngine
        _engine_instance = FaceEngine()
    return _engine_instance
