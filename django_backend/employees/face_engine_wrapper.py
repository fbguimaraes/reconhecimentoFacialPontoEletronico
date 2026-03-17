import os
import sys

_engine_instance = None


def get_engine():
    """Retorna uma instância singleton do motor facial do projeto."""
    global _engine_instance
    if _engine_instance is None:
        project_root = os.path.dirname(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        )
        if project_root not in sys.path:
            sys.path.insert(0, project_root)
        from face_engine_api import FaceEngine
        _engine_instance = FaceEngine()
    return _engine_instance
