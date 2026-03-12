"""
Sistema de Reconhecimento Facial para Controle de Ponto Eletrônico.

Interface gráfica (Tkinter) com funcionalidades de:
- Cadastro de funcionários com captura facial via webcam
- Reconhecimento facial em tempo real para registro de entrada e saída
- Visualização de logs de ponto
"""

import threading
import time
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

import cv2
import numpy as np
from PIL import Image, ImageTk

from face_engine_api import FaceEngine, NUM_CAPTURE_FRAMES, open_camera


# ======================== CORES DO TEMA ========================

BG_DARK = "#2c3e50"
BG_CARD = "#34495e"
FG_WHITE = "#ecf0f1"
FG_MUTED = "#95a5a6"
COLOR_GREEN = "#27ae60"
COLOR_GREEN_HOVER = "#2ecc71"
COLOR_BLUE = "#2980b9"
COLOR_BLUE_HOVER = "#3498db"
COLOR_PURPLE = "#8e44ad"
COLOR_PURPLE_HOVER = "#9b59b6"
COLOR_RED = "#c0392b"
COLOR_RED_HOVER = "#e74c3c"
COLOR_ORANGE = "#e67e22"
COLOR_ORANGE_HOVER = "#f39c12"

VIDEO_WIDTH = 640
VIDEO_HEIGHT = 480
REG_VIDEO_WIDTH = 480
REG_VIDEO_HEIGHT = 360


class MainApp:
    """Aplicação principal do sistema de ponto eletrônico com reconhecimento facial."""

    def __init__(self, root):
        self.root = root
        self.root.title("Sistema de Ponto Eletrônico — Reconhecimento Facial")
        self.root.geometry("800x600")
        self.root.resizable(False, False)
        self.root.configure(bg=BG_DARK)

        # Estado da câmera
        self.camera = None
        self.running = False

        # Inicializar o engine de reconhecimento facial
        try:
            self.engine = FaceEngine()
        except RuntimeError as e:
            messagebox.showerror("Erro Fatal", str(e))
            root.destroy()
            return

        self._build_main_screen()

    # ======================== TELA PRINCIPAL ========================

    def _build_main_screen(self):
        """Constrói a tela principal com os botões de navegação."""
        for widget in self.root.winfo_children():
            widget.destroy()

        self.root.geometry("800x700")

        frame = tk.Frame(self.root, bg=BG_DARK)
        frame.pack(fill=tk.BOTH, expand=True)

        # Título
        tk.Label(
            frame,
            text="Controle de Ponto Eletrônico",
            font=("Helvetica", 24, "bold"),
            fg=FG_WHITE,
            bg=BG_DARK,
        ).pack(pady=(30, 5))

        tk.Label(
            frame,
            text="Reconhecimento Facial com MediaPipe",
            font=("Helvetica", 13),
            fg=FG_MUTED,
            bg=BG_DARK,
        ).pack(pady=(0, 20))

        # Botões
        btn_frame = tk.Frame(frame, bg=BG_DARK)
        btn_frame.pack()

        btn_cfg = {"font": ("Helvetica", 13), "width": 30, "height": 2, "bd": 0, "cursor": "hand2"}

        tk.Button(
            btn_frame,
            text="📷   Cadastrar Novo Funcionário",
            bg=COLOR_GREEN,
            fg="white",
            activebackground=COLOR_GREEN_HOVER,
            command=self._open_registration,
            **btn_cfg,
        ).pack(pady=5)

        tk.Button(
            btn_frame,
            text="⬇️   Registrar Entrada",
            bg=COLOR_BLUE,
            fg="white",
            activebackground=COLOR_BLUE_HOVER,
            command=lambda: self._open_recognition("entrada"),
            **btn_cfg,
        ).pack(pady=5)

        tk.Button(
            btn_frame,
            text="⬆️   Registrar Saída",
            bg=COLOR_ORANGE,
            fg="white",
            activebackground=COLOR_ORANGE_HOVER,
            command=lambda: self._open_recognition("saida"),
            **btn_cfg,
        ).pack(pady=5)

        tk.Button(
            btn_frame,
            text="📋   Ver Logs de Ponto",
            bg=COLOR_PURPLE,
            fg="white",
            activebackground=COLOR_PURPLE_HOVER,
            command=self._open_logs,
            **btn_cfg,
        ).pack(pady=5)

        tk.Button(
            btn_frame,
            text="❌   Sair",
            bg=COLOR_RED,
            fg="white",
            activebackground=COLOR_RED_HOVER,
            command=self._on_close,
            **btn_cfg,
        ).pack(pady=5)

        tk.Button(
            btn_frame,
            text="🗑️   Limpar Todos os Cadastros",
            bg="#7f8c8d",
            fg="white",
            activebackground="#95a5a6",
            command=self._clear_all_data,
            **btn_cfg,
        ).pack(pady=5)

        # Rodapé com contagem de funcionários cadastrados
        try:
            employees = self.engine.get_all_employees()
            n = len(employees)
        except:
            n = 0
        tk.Label(
            frame,
            text=f"Funcionários cadastrados: {n}",
            font=("Helvetica", 11),
            fg=FG_MUTED,
            bg=BG_DARK,
        ).pack(side=tk.BOTTOM, pady=20)

    def _clear_all_data(self):
        """Limpa todos os cadastros e registros após confirmação."""
        try:
            employees = self.engine.get_all_employees()
            n = len(employees)
        except:
            n = 0
        if n == 0:
            messagebox.showinfo("Nenhum cadastro", "Não há funcionários cadastrados para remover.")
            return
        messagebox.showwarning(
            "Funcionalidade não disponível",
            "Para remover funcionários, use o Admin Panel do Django:\n"
            "http://localhost:8000/admin/"
        )

    # ======================== GERENCIAMENTO DA CÂMERA ========================

    def _stop_camera(self):
        """Para a câmera de forma segura."""
        self.running = False
        time.sleep(0.1)  # Aguarda o loop de captura finalizar
        if self.camera is not None and self.camera.isOpened():
            self.camera.release()
            self.camera = None

    # ======================== CADASTRO DE FUNCIONÁRIOS ========================

    def _open_registration(self):
        """Abre a janela de cadastro de um novo funcionário."""
        self._stop_camera()

        win = tk.Toplevel(self.root)
        win.title("Cadastrar Novo Funcionário")
        win.geometry("560x600")
        win.resizable(False, False)
        win.configure(bg="#f5f6fa")
        win.grab_set()

        # ---- Formulário ----
        form = tk.Frame(win, bg="#f5f6fa", padx=20, pady=10)
        form.pack(fill=tk.X)

        # ID automático (não editável)
        next_id = self.engine.get_next_emp_id()
        tk.Label(form, text="ID (Automático):", font=("Helvetica", 12), bg="#f5f6fa").grid(
            row=0, column=0, sticky="w", pady=5
        )
        id_label = tk.Label(form, text=next_id, font=("Helvetica", 12, "bold"), bg="#f5f6fa", fg=COLOR_GREEN)
        id_label.grid(row=0, column=1, padx=10, pady=5, sticky="w")

        tk.Label(form, text="Nome Completo:", font=("Helvetica", 12), bg="#f5f6fa").grid(
            row=1, column=0, sticky="w", pady=5
        )
        name_entry = tk.Entry(form, font=("Helvetica", 12), width=30)
        name_entry.grid(row=1, column=1, padx=10, pady=5, sticky="w")

        # ---- Status ----
        status_var = tk.StringVar(value="Preencha os campos e clique em 'Iniciar Captura'.")
        tk.Label(
            win, textvariable=status_var, font=("Helvetica", 10), fg=COLOR_BLUE, bg="#f5f6fa"
        ).pack(pady=5)

        # ---- Barra de progresso ----
        progress_var = tk.DoubleVar(value=0)
        progress_bar = ttk.Progressbar(win, variable=progress_var, maximum=NUM_CAPTURE_FRAMES, length=400)
        progress_bar.pack(pady=(0, 5))

        # ---- Área de vídeo (tamanho em pixels via imagem placeholder) ----
        placeholder = ImageTk.PhotoImage(Image.new("RGB", (REG_VIDEO_WIDTH, REG_VIDEO_HEIGHT), "black"))
        video_label = tk.Label(win, image=placeholder, bg="black")
        video_label.imgtk = placeholder  # Manter referência
        video_label.pack(pady=5)

        # ---- Botões ----
        btn_frame = tk.Frame(win, bg="#f5f6fa")
        btn_frame.pack(pady=10)

        capture_btn = tk.Button(
            btn_frame,
            text="Iniciar Captura",
            font=("Helvetica", 12),
            bg=COLOR_GREEN,
            fg="white",
            width=15,
            cursor="hand2",
            command=lambda: self._start_capture(
                win, id_label, name_entry, video_label, status_var, progress_var, capture_btn
            ),
        )
        capture_btn.pack(side=tk.LEFT, padx=5)

        tk.Button(
            btn_frame,
            text="Cancelar",
            font=("Helvetica", 12),
            bg=COLOR_RED,
            fg="white",
            width=15,
            cursor="hand2",
            command=lambda: self._close_registration(win),
        ).pack(side=tk.LEFT, padx=5)

        win.protocol("WM_DELETE_WINDOW", lambda: self._close_registration(win))

    def _start_capture(self, win, id_label, name_entry, video_label, status_var, progress_var, capture_btn):
        """Valida os campos e inicia a captura em thread separada."""
        emp_id = id_label.cget("text").strip()
        name = name_entry.get().strip()

        if not name:
            messagebox.showwarning("Campo obrigatório", "Preencha o Nome.", parent=win)
            return

        # Desabilitar campos durante a captura
        capture_btn.config(state=tk.DISABLED)
        name_entry.config(state=tk.DISABLED)

        thread = threading.Thread(
            target=self._capture_loop,
            args=(win, emp_id, name, video_label, status_var, progress_var, capture_btn, name_entry),
            daemon=True,
        )
        thread.start()

    def _capture_loop(self, win, emp_id, name, video_label, status_var, progress_var, capture_btn, name_entry):
        """Loop de captura de frames para cadastro. Executa em thread separada."""
        self.camera = open_camera()
        if not self.camera.isOpened():
            status_var.set("❌ Erro: Webcam não encontrada!")
            capture_btn.config(state=tk.NORMAL)
            return

        self.running = True
        embeddings = []
        frame_count = 0
        skip_frames = 2  # Processar 1 a cada 2 frames para performance

        status_var.set(f"Olhe para a câmera... (0/{NUM_CAPTURE_FRAMES})")

        while self.running and len(embeddings) < NUM_CAPTURE_FRAMES:
            ret, frame = self.camera.read()
            if not ret:
                continue

            frame_count += 1
            
            # Skip frames para otimização
            if frame_count % skip_frames != 0:
                self._update_video(video_label, frame, size=(REG_VIDEO_WIDTH, REG_VIDEO_HEIGHT))
                continue

            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            faces = self.engine.detect_faces(frame_rgb)

            display = frame.copy()
            h, w = frame.shape[:2]

            if faces:
                landmarks = faces[0]
                x1, y1, x2, y2 = self.engine.get_face_bbox(landmarks, w, h)
                cv2.rectangle(display, (x1, y1), (x2, y2), (0, 255, 0), 2)

                # Captura embedding
                embedding = self.engine.extract_embedding(landmarks, frame_rgb)
                embeddings.append(embedding)
                progress_var.set(len(embeddings))
                status_var.set(f"Capturando... ({len(embeddings)}/{NUM_CAPTURE_FRAMES})")

                cv2.putText(
                    display,
                    f"Capturado: {len(embeddings)}/{NUM_CAPTURE_FRAMES}",
                    (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    (0, 255, 0),
                    2,
                )
            else:
                cv2.putText(
                    display,
                    "Nenhum rosto detectado - posicione-se",
                    (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6,
                    (0, 0, 255),
                    2,
                )

            self._update_video(video_label, display, size=(REG_VIDEO_WIDTH, REG_VIDEO_HEIGHT))
            time.sleep(0.005)  # Otimizado

        self._stop_camera()
        if len(embeddings) >= NUM_CAPTURE_FRAMES:
            # Verificar se o rosto já está cadastrado (outro ID)
            avg_embedding = np.mean(embeddings, axis=0)
            duplicate = self.engine.find_duplicate_face(avg_embedding, exclude_id=emp_id)
            if duplicate:
                dup_id, dup_name, sim = duplicate
                status_var.set(f"❌ Rosto já cadastrado como '{dup_name}' (ID: {dup_id})")
                try:
                    messagebox.showerror(
                        "Rosto já cadastrado",
                        f"Este rosto já pertence ao funcionário '{dup_name}' (ID: {dup_id}).\n"
                        f"Similaridade: {sim:.0%}\n\n"
                        "Não é possível cadastrar o mesmo rosto novamente.",
                        parent=win,
                    )
                except tk.TclError:
                    pass
                try:
                    capture_btn.config(state=tk.NORMAL)
                    name_entry.config(state=tk.NORMAL)
                except tk.TclError:
                    pass
                return

            self.engine.register_employee(emp_id, name, embeddings)
            status_var.set(f"✅ '{name}' (ID: {emp_id}) cadastrado com sucesso!")
            try:
                messagebox.showinfo(
                    "Sucesso",
                    f"Funcionário '{name}' cadastrado com sucesso!\n"
                    f"Embedding médio gerado a partir de {NUM_CAPTURE_FRAMES} capturas.",
                    parent=win,
                )
                self._close_registration(win)
            except tk.TclError:
                pass
            return
        else:
            status_var.set("❌ Captura cancelada ou insuficiente.")

        try:
            capture_btn.config(state=tk.NORMAL)
        except tk.TclError:
            pass

    def _close_registration(self, win):
        """Fecha a janela de cadastro, para a câmera e atualiza o menu principal."""
        self._stop_camera()
        try:
            win.destroy()
        except tk.TclError:
            pass
        self._build_main_screen()

    # ======================== RECONHECIMENTO EM TEMPO REAL ========================

    def _open_recognition(self, mode="entrada"):
        """Abre a janela de reconhecimento facial em tempo real."""
        try:
            employees = self.engine.get_all_employees()
            has_employees = len(employees) > 0
        except:
            has_employees = False
        
        if not has_employees:
            messagebox.showwarning(
                "Nenhum cadastro",
                "Nenhum funcionário cadastrado.\nCadastre ao menos um funcionário primeiro.",
            )
            return

        self._stop_camera()

        is_entry = mode == "entrada"
        title = "Registrar Entrada" if is_entry else "Registrar Saída"
        accent_color = COLOR_BLUE if is_entry else COLOR_ORANGE

        win = tk.Toplevel(self.root)
        win.title(title)
        win.geometry("750x680")
        win.resizable(False, False)
        win.configure(bg="#f5f6fa")
        win.grab_set()

        # ---- Título do modo ----
        mode_label = "⬇️  MODO: ENTRADA" if is_entry else "⬆️  MODO: SAÍDA"
        tk.Label(
            win, text=mode_label, font=("Helvetica", 14, "bold"),
            fg="white", bg=accent_color, pady=6,
        ).pack(fill=tk.X)

        # ---- Status ----
        status_var = tk.StringVar(value="Iniciando câmera...")
        tk.Label(
            win, textvariable=status_var, font=("Helvetica", 11, "bold"), fg=accent_color, bg="#f5f6fa"
        ).pack(pady=5)

        # ---- Vídeo ----
        placeholder = ImageTk.PhotoImage(Image.new("RGB", (VIDEO_WIDTH, VIDEO_HEIGHT), "black"))
        video_label = tk.Label(win, image=placeholder, bg="black")
        video_label.imgtk = placeholder
        video_label.pack(pady=5)

        # ---- Log em tempo real ----
        log_frame = tk.Frame(win, bg="#f5f6fa")
        log_frame.pack(fill=tk.X, padx=20, pady=5)

        log_var = tk.StringVar(value="Aguardando detecções...")
        tk.Label(
            log_frame, textvariable=log_var, font=("Helvetica", 10), fg=COLOR_GREEN, bg="#f5f6fa",
            wraplength=700, justify="left",
        ).pack(fill=tk.X)

        # ---- Botão parar ----
        tk.Button(
            win,
            text="⏹  Parar",
            font=("Helvetica", 12),
            bg=COLOR_RED,
            fg="white",
            width=22,
            cursor="hand2",
            command=lambda: self._close_window(win),
        ).pack(pady=10)

        win.protocol("WM_DELETE_WINDOW", lambda: self._close_window(win))

        # Iniciar reconhecimento em thread
        thread = threading.Thread(
            target=self._recognition_loop,
            args=(win, video_label, status_var, log_var, mode),
            daemon=True,
        )
        thread.start()

    def _recognition_loop(self, win, video_label, status_var, log_var, mode):
        """Loop de reconhecimento em tempo real. Executa em thread separada."""
        self.camera = open_camera()
        if not self.camera.isOpened():
            status_var.set("❌ Erro: Webcam não encontrada!")
            return

        self.running = True
        is_entry = mode == "entrada"
        action_text = "ENTRADA" if is_entry else "SAÍDA"
        
        # ===== PERÍODO DE PREPARAÇÃO (5 segundos) =====
        preparation_time = 5
        start_time = time.time()
        
        while self.running and (time.time() - start_time) < preparation_time:
            ret, frame = self.camera.read()
            if not ret:
                continue
            
            display = frame.copy()
            remaining = int(preparation_time - (time.time() - start_time) + 1)
            
            # Exibir contagem regressiva na tela
            countdown_text = f"Prepare-se: {remaining}s"
            status_var.set(f"⏳ {countdown_text}")
            
            # Adicionar texto grande na imagem
            font_scale = 2.5
            thickness = 4
            (tw, th), _ = cv2.getTextSize(countdown_text, cv2.FONT_HERSHEY_SIMPLEX, font_scale, thickness)
            
            h, w = display.shape[:2]
            x = (w - tw) // 2
            y = (h + th) // 2
            
            # Fundo semi-transparente para o texto
            overlay = display.copy()
            cv2.rectangle(overlay, (x - 20, y - th - 20), (x + tw + 20, y + 20), (0, 0, 0), -1)
            cv2.addWeighted(overlay, 0.6, display, 0.4, 0, display)
            
            # Texto da contagem
            cv2.putText(
                display, countdown_text, (x, y),
                cv2.FONT_HERSHEY_SIMPLEX, font_scale, (255, 255, 0), thickness,
            )
            
            self._update_video(video_label, display)
            time.sleep(0.1)
        
        if not self.running:
            self._stop_camera()
            return
        
        # ===== INICIAR RECONHECIMENTO FACIAL =====
        status_var.set(f"🔍 Reconhecimento ativo — Modo: {action_text}")

        while self.running:
            ret, frame = self.camera.read()
            if not ret:
                continue

            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            faces = self.engine.detect_faces(frame_rgb)

            display = frame.copy()
            h, w = frame.shape[:2]

            for landmarks in faces:
                x1, y1, x2, y2 = self.engine.get_face_bbox(landmarks, w, h)
                embedding = self.engine.extract_embedding(landmarks, frame_rgb)
                result = self.engine.recognize(embedding)

                if result:
                    emp_id, emp_name, similarity = result
                    can, reason = self.engine.can_register(emp_id, mode)

                    if can:
                        color = (0, 255, 0)
                        if is_entry:
                            self.engine.log_entry(emp_id, emp_name, similarity)
                        else:
                            self.engine.log_exit(emp_id, emp_name, similarity)
                        now = datetime.now().strftime("%H:%M:%S")
                        log_var.set(f"✅ {action_text} registrada: {emp_name} (ID: {emp_id}) às {now}")
                        label_text = f"{emp_name} ({similarity:.0%})"

                        # Mostrar confirmação e retornar ao menu principal
                        self.running = False
                        self._update_video(video_label, display)
                        win.after(0, lambda n=emp_name, i=emp_id, t=now, a=action_text: self._show_registration_confirmation(win, n, i, t, a))
                        self._stop_camera()
                        return
                    else:
                        color = (255, 165, 0)  # Laranja = reconhecido mas não pode registrar
                        label_text = f"{emp_name} - {reason}"
                        log_var.set(f"⚠️ {emp_name}: {reason}")
                else:
                    color = (0, 0, 255)
                    label_text = "Desconhecido"

                cv2.rectangle(display, (x1, y1), (x2, y2), color, 2)

                # Fundo do texto para melhor legibilidade
                (tw, th), _ = cv2.getTextSize(label_text, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2)
                cv2.rectangle(display, (x1, y1 - th - 10), (x1 + tw, y1), color, -1)
                cv2.putText(
                    display, label_text, (x1, y1 - 5),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2,
                )

            if not faces:
                cv2.putText(
                    display,
                    "Nenhum rosto detectado",
                    (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    (128, 128, 128),
                    2,
                )

            self._update_video(video_label, display)
            time.sleep(0.005)  # Otimizado para máxima responsividade

        self._stop_camera()

    # ======================== VISUALIZAÇÃO DE LOGS ========================

    def _open_logs(self):
        """Abre a janela de visualização dos registros de ponto."""
        win = tk.Toplevel(self.root)
        win.title("Registros de Ponto")
        win.geometry("720x520")
        win.resizable(True, True)
        win.configure(bg="#f5f6fa")
        win.grab_set()

        tk.Label(
            win,
            text="Últimos Registros de Ponto",
            font=("Helvetica", 14, "bold"),
            bg="#f5f6fa",
        ).pack(pady=10)

        # Treeview com estilo
        style = ttk.Style(win)
        style.theme_use("clam")
        style.configure("Treeview", font=("Helvetica", 11), rowheight=28)
        style.configure("Treeview.Heading", font=("Helvetica", 11, "bold"))

        columns = ("ID", "Nome", "Data", "Entrada", "Saida")
        tree_frame = tk.Frame(win, bg="#f5f6fa")
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=(0, 10))

        tree = ttk.Treeview(tree_frame, columns=columns, show="headings", height=16)

        tree.heading("ID", text="ID")
        tree.heading("Nome", text="Nome")
        tree.heading("Data", text="Data")
        tree.heading("Entrada", text="Entrada")
        tree.heading("Saida", text="Saída")

        tree.column("ID", width=70, anchor="center")
        tree.column("Nome", width=200, anchor="w")
        tree.column("Data", width=110, anchor="center")
        tree.column("Entrada", width=90, anchor="center")
        tree.column("Saida", width=90, anchor="center")

        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)

        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Popular com dados
        logs = self.engine.get_logs()
        for entry in reversed(logs):  # Mais recentes primeiro
            if len(entry) >= 5:
                saida = entry[4] if entry[4] else "—"
                tree.insert("", tk.END, values=(entry[0], entry[1], entry[2], entry[3], saida))

        if not logs:
            tree.insert("", tk.END, values=("—", "Nenhum registro encontrado", "—", "—", "—"))

        # Botão fechar
        tk.Button(
            win,
            text="Fechar",
            font=("Helvetica", 12),
            bg=COLOR_BLUE,
            fg="white",
            width=15,
            cursor="hand2",
            command=win.destroy,
        ).pack(pady=10)

    # ======================== UTILITÁRIOS ========================

    def _update_video(self, label, frame_bgr, size=None):
        """Atualiza o widget Label do Tkinter com um frame OpenCV (BGR)."""
        try:
            if size is None:
                size = (VIDEO_WIDTH, VIDEO_HEIGHT)
            frame_rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
            frame_resized = cv2.resize(frame_rgb, size)
            img = Image.fromarray(frame_resized)
            imgtk = ImageTk.PhotoImage(image=img)
            label.imgtk = imgtk  # Manter referência para evitar garbage collection
            label.configure(image=imgtk)
        except (tk.TclError, Exception):
            pass  # Widget pode ter sido destruído

    def _show_registration_confirmation(self, win, emp_name, emp_id, time_str, action_text):
        """Exibe mensagem de confirmação de registro e retorna ao menu principal."""
        try:
            messagebox.showinfo(
                f"{action_text} Registrada",
                f"{action_text} registrada com sucesso!\n\n"
                f"Funcionário: {emp_name}\n"
                f"ID: {emp_id}\n"
                f"Horário: {time_str}",
                parent=win,
            )
            win.destroy()
        except tk.TclError:
            pass
        self._build_main_screen()

    def _close_window(self, window):
        """Fecha uma janela filha e para a câmera."""
        self._stop_camera()
        try:
            window.destroy()
        except tk.TclError:
            pass
        self._build_main_screen()

    def _on_close(self):
        """Encerra a aplicação completamente."""
        self._stop_camera()
        self.engine.close()
        self.root.destroy()


# ======================== PONTO DE ENTRADA ========================

def main():
    root = tk.Tk()
    app = MainApp(root)
    root.protocol("WM_DELETE_WINDOW", app._on_close)
    root.mainloop()


if __name__ == "__main__":
    main()
