"""
Motor de Reconhecimento Facial com integração à API Django.

Esta versão se comunica com o backend Django via API REST
em vez de usar arquivos CSV e Pickle locais.
"""

import os
import platform
import urllib.request
from datetime import datetime
from pathlib import Path
import requests

import cv2
import numpy as np
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

# Importar configurações
try:
    from config import config, get_resource_path
    CONFIG_LOADED = True
except ImportError:
    # Modo compatibilidade (sem config.py)
    CONFIG_LOADED = False
    print("⚠ Módulo config.py não encontrado, usando configurações padrão")

# ======================== CONFIGURAÇÕES ========================

if CONFIG_LOADED:
    # Usar configurações do arquivo config.ini
    BASE_DIR = config.models_dir.parent
    MODELS_DIR = config.models_dir
    API_BASE_URL = config.api_url
    SIMILARITY_THRESHOLD = config.recognition_threshold
    NUM_CAPTURE_FRAMES = config.capture_frames
else:
    # Configurações padrão
    BASE_DIR = Path(__file__).parent
    MODELS_DIR = BASE_DIR / "models"
    API_BASE_URL = "http://localhost:8000/api"
    SIMILARITY_THRESHOLD = 0.40
    NUM_CAPTURE_FRAMES = 10

MODEL_URL = (
    "https://storage.googleapis.com/mediapipe-models/"
    "face_landmarker/face_landmarker/float16/1/face_landmarker.task"
)
MODEL_PATH = MODELS_DIR / "face_landmarker.task"
SFACE_MODEL_PATH = MODELS_DIR / "face_recognition_sface_2021dec.onnx"

SFACE_MODEL_URL = (
    "https://github.com/opencv/opencv_zoo/raw/main/models/"
    "face_recognition_sface/face_recognition_sface_2021dec.onnx"
)


# ======================== FUNÇÕES AUXILIARES ========================

def ensure_directories():
    """Cria os diretórios necessários caso não existam."""
    MODELS_DIR.mkdir(parents=True, exist_ok=True)


def download_model(progress_callback=None):
    """Baixa o modelo FaceLandmarker do MediaPipe se não estiver presente."""
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
    """Motor de reconhecimento facial baseado em MediaPipe com integração Django API."""

    def __init__(self, api_url=None):
        """Inicializa o engine, baixa os modelos se necessário e configura API."""
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

        # Configurar URL da API
        self.api_url = api_url or API_BASE_URL
        
        # Session HTTP persistente para performance
        self.session = requests.Session()
        self.session.headers.update({'Content-Type': 'application/json'})
        
        # Cache de employees (TTL: 5 segundos)
        self._employees_cache = None
        self._cache_timestamp = 0
        self._cache_ttl = 5

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

        # Verificar conexão com a API
        try:
            response = self.session.get(f"{self.api_url}/employees/", timeout=3)
            if response.status_code != 200:
                print(f"Aviso: API retornou status {response.status_code}")
        except Exception as e:
            print(f"Aviso: Não foi possível conectar à API Django: {e}")
            print("Certifique-se de que o servidor Django está rodando em http://localhost:8000")

    # -------------------- Detecção e Embedding --------------------

    def detect_faces(self, frame_rgb):
        """Detecta rostos em um frame RGB usando o MediaPipe FaceLandmarker."""
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame_rgb)
        result = self.landmarker.detect(mp_image)
        return result.face_landmarks

    def extract_embedding(self, landmarks, frame_rgb):
        """Extrai um embedding de identidade facial usando OpenCV SFace."""
        h, w = frame_rgb.shape[:2]

        # Extrair pontos-chave dos landmarks do MediaPipe
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

        # Bounding box a partir dos landmarks
        xs = [lm.x * w for lm in landmarks]
        ys = [lm.y * h for lm in landmarks]
        x_min = max(0, min(xs) - 10)
        y_min = max(0, min(ys) - 10)
        x_max = min(w, max(xs) + 10)
        y_max = min(h, max(ys) + 10)
        bw = x_max - x_min
        bh = y_max - y_min

        # Formato esperado pelo SFace alignCrop
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

    def detect_and_embed(self, frame_rgb):
        """Detecta o primeiro rosto do frame e retorna seu embedding."""
        faces = self.detect_faces(frame_rgb)
        if not faces:
            return None
        return self.extract_embedding(faces[0], frame_rgb)

    # -------------------- API Calls --------------------

    def get_next_emp_id(self):
        """Gera o próximo ID de funcionário de forma incremental."""
        employees = self.get_all_employees()
        if not employees:
            return "001"
        
        # Extrair IDs numéricos
        numeric_ids = []
        for emp in employees:
            emp_id = emp.get('emp_id', '')
            if emp_id.isdigit():
                numeric_ids.append(int(emp_id))
        
        if numeric_ids:
            next_id = max(numeric_ids) + 1
        else:
            next_id = len(employees) + 1
        
        return f"{next_id:03d}"
    
    def register_employee(self, emp_id, name, embeddings, department=None, position=None):
        """Registra um funcionário com embeddings via API Django."""
        url = f"{self.api_url}/register-employee/"
        
        # Converter embeddings numpy para listas
        embeddings_list = [emb.tolist() for emb in embeddings]
        
        data = {
            "emp_id": emp_id,
            "name": name,
            "embeddings": embeddings_list,
            "department": department or ""
        }
        
        try:
            response = self.session.post(url, json=data, timeout=10)
            response.raise_for_status()
            # Limpar cache após registro
            self._employees_cache = None
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Erro ao registrar funcionário: {e}")
            if hasattr(e.response, 'text'):
                print(f"Resposta: {e.response.text}")
            raise

    def find_duplicate_face(self, embedding, exclude_id=None):
        """Verifica se um embedding corresponde a um funcionário já cadastrado via API."""
        url = f"{self.api_url}/check-duplicate/"
        
        data = {
            "embedding": embedding.tolist(),
            "threshold": SIMILARITY_THRESHOLD,
            "exclude_emp_id": exclude_id
        }
        
        try:
            response = self.session.post(url, json=data, timeout=5)
            response.raise_for_status()
            result = response.json()
            
            if result.get('is_duplicate'):
                emp = result['employee']
                return emp['emp_id'], emp['name'], result['similarity']
            return None
        except requests.exceptions.RequestException as e:
            print(f"Erro ao verificar duplicata: {e}")
            return None

    def recognize(self, embedding):
        """Compara um embedding com todos os funcionários cadastrados via API."""
        url = f"{self.api_url}/recognize/"
        
        data = {
            "embedding": embedding.tolist(),
            "threshold": SIMILARITY_THRESHOLD
        }
        
        try:
            response = self.session.post(url, json=data, timeout=5)
            response.raise_for_status()
            result = response.json()
            
            if result.get('recognized'):
                emp = result['employee']
                return emp['emp_id'], emp['name'], result['similarity']
            return None
        except requests.exceptions.RequestException as e:
            print(f"Erro ao reconhecer rosto: {e}")
            return None

    def get_today_status(self, emp_id):
        """Verifica o status do funcionário no dia de hoje via API."""
        url = f"{self.api_url}/employees/"
        
        try:
            # Buscar funcionário por emp_id
            response = self.session.get(url, params={'emp_id': emp_id}, timeout=5)
            response.raise_for_status()
            data = response.json()
            
            # Verificar se a resposta é uma lista ou um dict com 'results'
            if isinstance(data, list):
                employees = data
            elif isinstance(data, dict) and 'results' in data:
                employees = data['results']
            else:
                employees = []
            
            if employees and len(employees) > 0:
                return employees[0].get('today_status', 'absent')
            return 'absent'
        except requests.exceptions.RequestException as e:
            print(f"Erro ao verificar status: {e}")
            return 'absent'
        except (KeyError, IndexError, TypeError) as e:
            print(f"Erro ao processar status: {e}")
            return 'absent'

    def can_register(self, emp_id, mode):
        """Verifica se o funcionário pode registrar entrada ou saída via API."""
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

    def log_entry(self, emp_id, name, confidence):
        """Registra a ENTRADA do funcionário via API."""
        return self._register_log(emp_id, 'entrada', confidence)

    def log_exit(self, emp_id, name, confidence):
        """Registra a SAÍDA do funcionário via API."""
        return self._register_log(emp_id, 'saida', confidence)

    def _register_log(self, emp_id, mode, confidence):
        """Método interno para registrar entrada ou saída via API."""
        url = f"{self.api_url}/register-log/"
        
        data = {
            "emp_id": emp_id,
            "mode": mode,
            "confidence": float(confidence)
        }
        
        try:
            response = self.session.post(url, json=data, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Erro ao registrar {mode}: {e}")
            if hasattr(e.response, 'text'):
                print(f"Resposta: {e.response.text}")
            raise

    def get_all_employees(self, force_refresh=False):
        """Retorna todos os funcionários cadastrados via API (com cache)."""
        import time
        
        # Verificar cache
        if not force_refresh and self._employees_cache is not None:
            if (time.time() - self._cache_timestamp) < self._cache_ttl:
                return self._employees_cache
        
        url = f"{self.api_url}/employees/"
        
        try:
            response = self.session.get(url, timeout=5)
            response.raise_for_status()
            data = response.json()
            
            # Verificar se a resposta é uma lista ou um dict com 'results'
            if isinstance(data, list):
                result = data
            elif isinstance(data, dict) and 'results' in data:
                result = data['results']
            else:
                result = []
            
            # Atualizar cache
            self._employees_cache = result
            self._cache_timestamp = time.time()
            return result
        except requests.exceptions.RequestException as e:
            print(f"Erro ao buscar funcionários: {e}")
            # Retornar cache antigo se disponível
            if self._employees_cache is not None:
                return self._employees_cache
            return []

    def get_employee_logs(self, emp_id):
        """Retorna os logs de um funcionário específico via API."""
        url = f"{self.api_url}/logs/"
        
        try:
            response = self.session.get(url, params={'employee__emp_id': emp_id}, timeout=5)
            response.raise_for_status()
            data = response.json()
            
            # Verificar se a resposta é uma lista ou um dict com 'results'
            if isinstance(data, list):
                return data
            elif isinstance(data, dict) and 'results' in data:
                return data['results']
            else:
                return []
        except requests.exceptions.RequestException as e:
            print(f"Erro ao buscar logs: {e}")
            return []

    def get_logs(self, max_entries=50):
        """
        Retorna os últimos registros de ponto via API Django.

        Returns:
            Lista de listas [ID, Nome, Data, Entrada, Saida].
        """
        url = f"{self.api_url}/logs/"
        
        try:
            response = self.session.get(url, timeout=5)
            response.raise_for_status()
            data = response.json()
            
            # Verificar se a resposta é uma lista ou um dict com 'results'
            if isinstance(data, list):
                logs = data
            elif isinstance(data, dict) and 'results' in data:
                logs = data['results']
            else:
                logs = []
            
            # Converter logs do formato da API para o formato esperado pelo main.py
            entries = []
            for log in logs[-max_entries:]:
                emp_id = log.get('employee_emp_id', 'N/A')
                name = log.get('employee_name', 'N/A')
                date = log.get('date', 'N/A')
                entry_time = log.get('entry_time', '') or ''
                exit_time = log.get('exit_time', '') or ''
                
                entries.append([emp_id, name, date, entry_time, exit_time])
            
            return entries
        except requests.exceptions.RequestException as e:
            print(f"Erro ao buscar logs: {e}")
            return []

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

    def close(self):
        """Libera os recursos do MediaPipe."""
        if self.landmarker:
            self.landmarker.close()
            self.landmarker = None
