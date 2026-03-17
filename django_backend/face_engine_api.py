"""Motor facial local do backend Django.

Este módulo existe para produção (ex.: Railway) quando o deploy usa
apenas a pasta django_backend e não inclui arquivos da raiz do repositório.
"""

from pathlib import Path
import urllib.request

import cv2
import mediapipe as mp
import numpy as np
from mediapipe.tasks import python
from mediapipe.tasks.python import vision


MODEL_URL = (
    "https://storage.googleapis.com/mediapipe-models/"
    "face_landmarker/face_landmarker/float16/1/face_landmarker.task"
)
SFACE_MODEL_URL = (
    "https://github.com/opencv/opencv_zoo/raw/main/models/"
    "face_recognition_sface/face_recognition_sface_2021dec.onnx"
)


class FaceEngine:
    """Extrai embedding facial a partir de um frame RGB."""

    def __init__(self):
        base_dir = Path(__file__).resolve().parent
        models_dir = base_dir / "models"
        models_dir.mkdir(parents=True, exist_ok=True)

        self.model_path = models_dir / "face_landmarker.task"
        self.sface_model_path = models_dir / "face_recognition_sface_2021dec.onnx"

        self._ensure_file(self.model_path, MODEL_URL)
        self._ensure_file(self.sface_model_path, SFACE_MODEL_URL)

        base_options = python.BaseOptions(model_asset_path=str(self.model_path))
        options = vision.FaceLandmarkerOptions(
            base_options=base_options,
            running_mode=vision.RunningMode.IMAGE,
            num_faces=5,
            min_face_detection_confidence=0.5,
            min_face_presence_confidence=0.5,
            output_face_blendshapes=False,
            output_facial_transformation_matrixes=False,
        )
        self.landmarker = vision.FaceLandmarker.create_from_options(options)

        self.face_recognizer = cv2.FaceRecognizerSF.create(
            str(self.sface_model_path),
            "",
        )

    @staticmethod
    def _ensure_file(file_path: Path, url: str):
        if file_path.exists():
            return
        urllib.request.urlretrieve(url, str(file_path))

    def detect_faces(self, frame_rgb):
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame_rgb)
        result = self.landmarker.detect(mp_image)
        return result.face_landmarks

    def extract_embedding(self, landmarks, frame_rgb):
        h, w = frame_rgb.shape[:2]

        re_x = (landmarks[33].x + landmarks[133].x) / 2 * w
        re_y = (landmarks[33].y + landmarks[133].y) / 2 * h
        le_x = (landmarks[362].x + landmarks[263].x) / 2 * w
        le_y = (landmarks[362].y + landmarks[263].y) / 2 * h
        nose_x = landmarks[4].x * w
        nose_y = landmarks[4].y * h
        rm_x = landmarks[61].x * w
        rm_y = landmarks[61].y * h
        lm_x = landmarks[291].x * w
        lm_y = landmarks[291].y * h

        xs = [lm.x * w for lm in landmarks]
        ys = [lm.y * h for lm in landmarks]
        x_min = max(0, min(xs) - 10)
        y_min = max(0, min(ys) - 10)
        x_max = min(w, max(xs) + 10)
        y_max = min(h, max(ys) + 10)
        bw = x_max - x_min
        bh = y_max - y_min

        face_info = np.array(
            [
                x_min,
                y_min,
                bw,
                bh,
                re_x,
                re_y,
                le_x,
                le_y,
                nose_x,
                nose_y,
                rm_x,
                rm_y,
                lm_x,
                lm_y,
                1.0,
            ],
            dtype=np.float32,
        )

        frame_bgr = cv2.cvtColor(frame_rgb, cv2.COLOR_RGB2BGR)
        aligned_face = self.face_recognizer.alignCrop(frame_bgr, face_info)
        embedding = self.face_recognizer.feature(aligned_face)
        return embedding.flatten()

    def detect_and_embed(self, frame_rgb):
        faces = self.detect_faces(frame_rgb)
        if not faces:
            return None
        return self.extract_embedding(faces[0], frame_rgb)
