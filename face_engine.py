"""
Motor de Reconhecimento Facial usando MediaPipe + OpenCV SFace.

MediaPipe FaceLandmarker é usado para detecção de rostos e localização de landmarks.
OpenCV FaceRecognizerSF (SFace) é usado para extração de embeddings de identidade
e comparação de similaridade.
"""

import os
import csv
import pickle
import platform
import urllib.request
from datetime import datetime
from pathlib import Path

import cv2
import numpy as np
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

# ======================== CONFIGURAÇÕES ========================

BASE_DIR = Path(__file__).parent
MODELS_DIR = BASE_DIR / "models"
DATA_DIR = BASE_DIR / "data"

MODEL_URL = (
    "https://storage.googleapis.com/mediapipe-models/"
    "face_landmarker/face_landmarker/float16/1/face_landmarker.task"
)
MODEL_PATH = MODELS_DIR / "face_landmarker.task"
SFACE_MODEL_PATH = MODELS_DIR / "face_recognition_sface_2021dec.onnx"
EMBEDDINGS_PATH = DATA_DIR / "embeddings.pkl"
LOG_PATH = DATA_DIR / "registros.csv"

SFACE_MODEL_URL = (
    "https://github.com/opencv/opencv_zoo/raw/main/models/"
    "face_recognition_sface/face_recognition_sface_2021dec.onnx"
)

# Limiar de similaridade de cosseno para SFace (recomendado: 0.363)
SIMILARITY_THRESHOLD = 0.40

# Intervalo mínimo (em segundos) entre registros do mesmo funcionário
COOLDOWN_SECONDS = 60

# Quantidade de frames capturados durante o cadastro
NUM_CAPTURE_FRAMES = 15


# ======================== FUNÇÕES AUXILIARES ========================

def ensure_directories():
    """Cria os diretórios necessários caso não existam."""
    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    DATA_DIR.mkdir(parents=True, exist_ok=True)


def download_model(progress_callback=None):
    """
    Baixa o modelo FaceLandmarker do MediaPipe se não estiver presente.
    progress_callback: função opcional chamada com mensagens de progresso.
    """
    ensure_directories()
    if MODEL_PATH.exists():
        return True

    msg = "Baixando modelo do MediaPipe (primeira execução)..."
    if progress_callback:
        progress_callback(msg)
    print(msg)

    try:
        urllib.request.urlretrieve(MODEL_URL, str(MODEL_PATH))
        msg = "Modelo baixado com sucesso."
        if progress_callback:
            progress_callback(msg)
        print(msg)
        return True
    except Exception as e:
        msg = f"Erro ao baixar modelo: {e}"
        if progress_callback:
            progress_callback(msg)
        print(msg)
        return False


def download_sface_model(progress_callback=None):
    """Baixa o modelo SFace para reconhecimento facial se não estiver presente."""
    ensure_directories()
    if SFACE_MODEL_PATH.exists():
        return True

    msg = "Baixando modelo SFace para reconhecimento facial..."
    if progress_callback:
        progress_callback(msg)
    print(msg)

    try:
        urllib.request.urlretrieve(SFACE_MODEL_URL, str(SFACE_MODEL_PATH))
        msg = "Modelo SFace baixado com sucesso."
        if progress_callback:
            progress_callback(msg)
        print(msg)
        return True
    except Exception as e:
        msg = f"Erro ao baixar modelo SFace: {e}"
        if progress_callback:
            progress_callback(msg)
        print(msg)
        return False


def open_camera():
    """Abre a webcam com o backend adequado ao sistema operacional."""
    if platform.system() == "Windows":
        cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    else:
        cap = cv2.VideoCapture(0)
    return cap


# ======================== CLASSE PRINCIPAL ========================

class FaceEngine:
    """Motor de reconhecimento facial baseado em MediaPipe FaceLandmarker."""

    def __init__(self):
        """Inicializa o engine, baixa os modelos se necessário e carrega a base de dados."""
        if not download_model():
            raise RuntimeError(
                "Não foi possível baixar o modelo do MediaPipe.\n"
                "Verifique sua conexão com a internet e tente novamente."
            )
        if not download_sface_model():
            raise RuntimeError(
                "Não foi possível baixar o modelo SFace.\n"
                "Verifique sua conexão com a internet e tente novamente."
            )

        # Configurar o FaceLandmarker no modo IMAGE (detecção)
        base_options = python.BaseOptions(model_asset_path=str(MODEL_PATH))
        options = vision.FaceLandmarkerOptions(
            base_options=base_options,
            running_mode=vision.RunningMode.IMAGE,
            num_faces=10,
            min_face_detection_confidence=0.5,
            min_face_presence_confidence=0.5,
            output_face_blendshapes=False,
            output_facial_transformation_matrixes=False,
        )
        self.landmarker = vision.FaceLandmarker.create_from_options(options)

        # Configurar o SFace para reconhecimento facial
        self.face_recognizer = cv2.FaceRecognizerSF.create(
            str(SFACE_MODEL_PATH), ""
        )

        # Base de dados: {emp_id: {"nome": str, "embedding": np.array}}
        self.database = self._load_database()

        # Controle de cooldown: {emp_id: datetime do último registro}
        self.last_registered = {}

    # -------------------- Persistência --------------------

    def _load_database(self):
        """Carrega a base de dados de embeddings do disco."""
        if EMBEDDINGS_PATH.exists():
            try:
                with open(EMBEDDINGS_PATH, "rb") as f:
                    return pickle.load(f)
            except Exception:
                return {}
        return {}

    def _save_database(self):
        """Salva a base de dados de embeddings no disco."""
        ensure_directories()
        with open(EMBEDDINGS_PATH, "wb") as f:
            pickle.dump(self.database, f)

    # -------------------- Detecção e Embedding --------------------

    def detect_faces(self, frame_rgb):
        """
        Detecta rostos em um frame RGB usando o MediaPipe FaceLandmarker.

        Args:
            frame_rgb: Imagem em formato numpy array RGB.

        Returns:
            Lista de landmarks para cada rosto detectado.
            Cada item é uma lista de NormalizedLandmark com 478 pontos.
        """
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame_rgb)
        result = self.landmarker.detect(mp_image)
        return result.face_landmarks

    def extract_embedding(self, landmarks, frame_rgb):
        """
        Extrai um embedding de identidade facial usando OpenCV SFace.

        Usa os landmarks do MediaPipe para localizar os pontos-chave do rosto,
        depois alimenta o SFace para gerar um embedding de 128 dimensões
        treinado especificamente para reconhecimento de identidade.

        Args:
            landmarks: Lista de NormalizedLandmark (478 pontos do MediaPipe).
            frame_rgb: Frame RGB original (numpy array).

        Returns:
            Vetor numpy 1D de 128 dimensões.
        """
        h, w = frame_rgb.shape[:2]

        # Extrair pontos-chave dos landmarks do MediaPipe
        # Olho direito: média entre cantos externo (33) e interno (133)
        re_x = (landmarks[33].x + landmarks[133].x) / 2 * w
        re_y = (landmarks[33].y + landmarks[133].y) / 2 * h
        # Olho esquerdo: média entre cantos externo (362) e interno (263)
        le_x = (landmarks[362].x + landmarks[263].x) / 2 * w
        le_y = (landmarks[362].y + landmarks[263].y) / 2 * h
        # Nariz
        nose_x = landmarks[4].x * w
        nose_y = landmarks[4].y * h
        # Cantos da boca
        rm_x = landmarks[61].x * w
        rm_y = landmarks[61].y * h
        lm_x = landmarks[291].x * w
        lm_y = landmarks[291].y * h

        # Bounding box a partir dos landmarks
        xs = [lm.x * w for lm in landmarks]
        ys = [lm.y * h for lm in landmarks]
        x_min = max(0, min(xs) - 10)
        y_min = max(0, min(ys) - 10)
        x_max = min(w, max(xs) + 10)
        y_max = min(h, max(ys) + 10)
        bw = x_max - x_min
        bh = y_max - y_min

        # Formato esperado pelo SFace alignCrop:
        # [x, y, w, h, re_x, re_y, le_x, le_y, nose_x, nose_y, rm_x, rm_y, lm_x, lm_y, score]
        face_info = np.array(
            [x_min, y_min, bw, bh, re_x, re_y, le_x, le_y, nose_x, nose_y, rm_x, rm_y, lm_x, lm_y, 1.0],
            dtype=np.float32,
        )

        # Converter RGB para BGR (OpenCV espera BGR)
        frame_bgr = cv2.cvtColor(frame_rgb, cv2.COLOR_RGB2BGR)

        # Alinhar e recortar o rosto
        aligned_face = self.face_recognizer.alignCrop(frame_bgr, face_info)

        # Extrair embedding de 128 dimensões
        embedding = self.face_recognizer.feature(aligned_face)
        return embedding.flatten()

    # -------------------- Similaridade --------------------

    @staticmethod
    def cosine_similarity(a, b):
        """Calcula a similaridade de cosseno entre dois embeddings SFace."""
        norm_a = np.linalg.norm(a)
        norm_b = np.linalg.norm(b)
        if norm_a < 1e-8 or norm_b < 1e-8:
            return 0.0
        return float(np.dot(a, b) / (norm_a * norm_b))

    # -------------------- Cadastro --------------------

    def register_employee(self, emp_id, name, embeddings):
        """
        Registra um funcionário com seus embeddings na base de dados.

        Calcula o embedding médio a partir de múltiplas capturas para maior robustez.

        Args:
            emp_id: Identificador único do funcionário.
            name: Nome do funcionário.
            embeddings: Lista de vetores numpy com os embeddings capturados.
        """
        avg_embedding = np.mean(embeddings, axis=0)
        self.database[emp_id] = {
            "nome": name,
            "embedding": avg_embedding,
        }
        self._save_database()

    def find_duplicate_face(self, embedding, exclude_id=None):
        """
        Verifica se um embedding corresponde a um funcionário já cadastrado.

        Args:
            embedding: Vetor numpy do rosto a verificar.
            exclude_id: ID a ignorar na comparação (ex: recadastro do mesmo funcionário).

        Returns:
            Tupla (emp_id, nome, similaridade) se encontrar duplicata, ou None.
        """
        for emp_id, data in self.database.items():
            if emp_id == exclude_id:
                continue
            sim = self.cosine_similarity(embedding, data["embedding"])
            print(f"  [DUPLICATE CHECK] vs '{data['nome']}' (ID: {emp_id}) | Similaridade: {sim:.4f}")
            if sim >= SIMILARITY_THRESHOLD:
                return emp_id, data["nome"], sim
        return None

    # -------------------- Reconhecimento --------------------

    def recognize(self, embedding):
        """
        Compara um embedding com todos os funcionários cadastrados.

        Args:
            embedding: Vetor numpy do rosto a ser reconhecido.

        Returns:
            Tupla (emp_id, nome, similaridade) do melhor match se a similaridade
            for >= SIMILARITY_THRESHOLD, ou None caso contrário.
        """
        best_match = None
        best_similarity = -1.0

        for emp_id, data in self.database.items():
            sim = self.cosine_similarity(embedding, data["embedding"])
            if sim > best_similarity:
                best_similarity = sim
                best_match = (emp_id, data["nome"], sim)

        if best_match and best_similarity >= SIMILARITY_THRESHOLD:
            return best_match
        return None

    # -------------------- Controle de Ponto --------------------

    def get_today_status(self, emp_id):
        """
        Verifica o status do funcionário no dia de hoje.

        Returns:
            "absent"   — sem registro hoje
            "entered"  — já registrou entrada, mas não saída
            "exited"   — já registrou entrada e saída
        """
        today = datetime.now().strftime("%Y-%m-%d")
        if not LOG_PATH.exists():
            return "absent"

        with open(LOG_PATH, "r", encoding="utf-8") as f:
            reader = csv.reader(f)
            next(reader, None)  # Pular cabeçalho
            for row in reader:
                if len(row) >= 5 and row[0] == emp_id and row[2] == today:
                    if row[4]:  # Coluna Saída preenchida
                        return "exited"
                    else:
                        return "entered"
        return "absent"

    def can_register(self, emp_id, mode):
        """
        Verifica se o funcionário pode registrar entrada ou saída.
        Implementa cooldown e verifica status do dia.

        Args:
            mode: "entrada" ou "saida"

        Returns:
            (bool, str) — (pode registrar, mensagem explicativa)
        """
        now = datetime.now()

        # Cooldown: evitar registros duplicados em curto intervalo
        key = f"{emp_id}_{mode}"
        if key in self.last_registered:
            elapsed = (now - self.last_registered[key]).total_seconds()
            if elapsed < COOLDOWN_SECONDS:
                return False, "Aguarde antes de registrar novamente."

        status = self.get_today_status(emp_id)

        if mode == "entrada":
            if status == "entered":
                return False, "Entrada já registrada hoje. Registre a saída primeiro."
            if status == "exited":
                return False, "Entrada e saída já registradas hoje."
            return True, ""
        else:  # saida
            if status == "absent":
                return False, "Registre a entrada primeiro."
            if status == "exited":
                return False, "Saída já registrada hoje."
            return True, ""

    def log_entry(self, emp_id, name):
        """
        Registra a ENTRADA do funcionário no CSV.
        Formato: ID, Nome, Data, Entrada, Saida (vazia)
        """
        ensure_directories()
        now = datetime.now()
        self.last_registered[f"{emp_id}_entrada"] = now

        file_exists = LOG_PATH.exists()
        with open(LOG_PATH, "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            if not file_exists:
                writer.writerow(["ID", "Nome", "Data", "Entrada", "Saida"])
            writer.writerow([
                emp_id,
                name,
                now.strftime("%Y-%m-%d"),
                now.strftime("%H:%M:%S"),
                "",  # Saída ainda não registrada
            ])

    def log_exit(self, emp_id):
        """
        Registra a SAÍDA do funcionário, atualizando a linha de entrada do dia.
        """
        now = datetime.now()
        today = now.strftime("%Y-%m-%d")
        self.last_registered[f"{emp_id}_saida"] = now

        if not LOG_PATH.exists():
            return

        rows = []
        updated = False
        with open(LOG_PATH, "r", encoding="utf-8") as f:
            reader = csv.reader(f)
            for row in reader:
                # Encontrar a linha de entrada do dia (sem saída)
                if (not updated and len(row) >= 5
                        and row[0] == emp_id and row[2] == today and row[4] == ""):
                    row[4] = now.strftime("%H:%M:%S")
                    updated = True
                rows.append(row)

        if updated:
            with open(LOG_PATH, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerows(rows)

    def get_logs(self, max_entries=50):
        """
        Retorna os últimos registros de ponto.

        Returns:
            Lista de listas [ID, Nome, Data, Entrada, Saida].
        """
        if not LOG_PATH.exists():
            return []

        entries = []
        with open(LOG_PATH, "r", encoding="utf-8") as f:
            reader = csv.reader(f)
            next(reader, None)  # Pular cabeçalho
            for row in reader:
                entries.append(row)

        return entries[-max_entries:]

    # -------------------- Utilitários de Desenho --------------------

    def get_face_bbox(self, landmarks, frame_width, frame_height):
        """
        Calcula o bounding box de um rosto a partir dos seus landmarks.

        Returns:
            Tupla (x_min, y_min, x_max, y_max) em pixels.
        """
        xs = [lm.x * frame_width for lm in landmarks]
        ys = [lm.y * frame_height for lm in landmarks]
        margin = 20
        x_min = int(max(0, min(xs) - margin))
        y_min = int(max(0, min(ys) - margin))
        x_max = int(min(frame_width, max(xs) + margin))
        y_max = int(min(frame_height, max(ys) + margin))
        return x_min, y_min, x_max, y_max

    # -------------------- Limpeza --------------------

    def clear_all_data(self):
        """Remove todos os cadastros e registros de ponto."""
        self.database.clear()
        self.last_registered.clear()
        if EMBEDDINGS_PATH.exists():
            EMBEDDINGS_PATH.unlink()
        if LOG_PATH.exists():
            LOG_PATH.unlink()

    def close(self):
        """Libera os recursos do MediaPipe."""
        if self.landmarker:
            self.landmarker.close()
            self.landmarker = None
