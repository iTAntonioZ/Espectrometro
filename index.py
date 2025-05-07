import tkinter as tk
from tkinter import ttk
from threading import Thread, Lock
import cv2
import numpy as np
from PIL import Image, ImageTk
from src.cam import analyze_colors
from src.graph import histogram


class SpectrometerApp:
    def __init__(self, root):
        self.root = root
        self._setup_window()
        self._init_variables()
        self._setup_ui()
        self._start_threads()
        
    def _setup_window(self):
        """Configura la ventana principal"""
        self.root.title("Espectrómetro con cámara | Realizado por iTAntonioZ")
        self.root.geometry("1000x700")
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_columnconfigure(1, weight=1)
        
        try:
            icon_image = Image.open("src/assets/icon/img2.png")
            self.root.iconphoto(True, ImageTk.PhotoImage(icon_image))
        except Exception as e:
            print(f"No se pudo cargar el icono: {e}")

    def _init_variables(self):
        """Inicializa variables de estado"""
        self.running = True
        self.frame_lock = Lock()
        self.current_frame = None
        self.current_imgtk = None
        self.cam_index = 0
        self.cap = None
        self.update_interval = 16  # ms (~60 FPS)

    def _setup_ui(self):
        """Configura la interfaz de usuario"""
        self._setup_video_frame()
        self._setup_graph_frame()
        self._setup_controls()

    def _setup_video_frame(self):
        """Configura el frame del video"""
        self.video_frame = ttk.LabelFrame(self.root, text="Vista de la Cámara")
        self.video_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        self.video_frame.grid_rowconfigure(0, weight=1)
        self.video_frame.grid_columnconfigure(0, weight=1)
        
        self.video_label = tk.Label(self.video_frame)
        self.video_label.pack(fill="both", expand=True)

    def _setup_graph_frame(self):
        """Configura el frame del gráfico"""
        self.graph_frame = ttk.LabelFrame(self.root, text="Histograma de Color")
        self.graph_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        self.graph_frame.grid_rowconfigure(0, weight=1)
        self.graph_frame.grid_columnconfigure(0, weight=1)
        
        self.canvas = histogram.get_minimalist_canvas(self.graph_frame)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

    def _setup_controls(self):
        """Configura los controles inferiores"""
        self.controls_frame = tk.Frame(self.root)
        self.controls_frame.grid(row=1, column=0, columnspan=2, sticky="ew")
        self.controls_frame.grid_columnconfigure(0, weight=1)
        
        self.switch_button = tk.Button(
            self.controls_frame, 
            text="Cambiar cámara", 
            command=self.show_camera_list
        )
        self.switch_button.grid(row=0, column=1, padx=10, pady=5, sticky="e")

    def _start_threads(self):
        """Inicia los hilos necesarios"""
        self.capture_thread = Thread(target=self._capture_frames, daemon=True)
        self.capture_thread.start()
        self.root.after(self.update_interval, self._update_display)
        self.root.protocol("WM_DELETE_WINDOW", self.close_window)

    def _capture_frames(self):
        """Captura frames de la cámara"""
        self.cap = cv2.VideoCapture(self.cam_index)
        
        if not self.cap.isOpened():
            print("No se pudo abrir la cámara.")
            return

        while self.running:
            ret, frame = self.cap.read() #se rompe los frames en 2 partes
            if frame is None:
                print("No se pudo leer el frame.")
                break
            if not ret:
                continue

            self._process_frame(frame)

    def _process_frame(self, frame):
        """Procesa un frame de video"""
        height, width = frame.shape[:2]
        
        # Dibujar cuadrantes
        cv2.line(frame, (width // 2, 0), (width // 2, height), (0, 255, 0), 2)
        cv2.line(frame, (0, height // 2), (width, height // 2), (0, 255, 0), 2)

        # Analizar colores
        _, center_color = analyze_colors(frame)
        histogram.update_histogram(center_color)

        # Convertir y guardar frame
        with self.frame_lock:
            self.current_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    def _update_display(self):
        """Actualiza la interfaz de usuario"""
        if not self.running:
            return

        self._update_camera_view()
        self._update_histogram()
        self.root.after(self.update_interval, self._update_display)

    def _update_camera_view(self):
        """Actualiza la vista de la cámara"""
        with self.frame_lock:
            if self.current_frame is None:
                return

            img = Image.fromarray(self.current_frame)
            label_width = self.video_label.winfo_width()
            label_height = self.video_label.winfo_height()

            if label_width > 1 and label_height > 1:
                img = self._resize_image(img, label_width, label_height)

            self.current_imgtk = ImageTk.PhotoImage(image=img)
            self.video_label.config(image=self.current_imgtk)

    def _resize_image(self, img, target_width, target_height):
        """Redimensiona la imagen manteniendo la relación de aspecto"""
        img_width, img_height = img.size
        aspect_ratio = img_width / img_height

        if target_width / target_height > aspect_ratio:
            new_height = target_height
            new_width = int(aspect_ratio * new_height)
        else:
            new_width = target_width
            new_height = int(new_width / aspect_ratio)

        return img.resize((new_width, new_height), Image.LANCZOS)

    def _update_histogram(self):
        """Actualiza el histograma"""
        self.canvas.flush_events()
        self.canvas.draw_idle()

    def close_window(self):
        """Cierra la aplicación correctamente"""
        self.running = False
        if self.cap:
            self.cap.release()
        self.root.quit()

    def show_camera_list(self):
        """Muestra la lista de cámaras disponibles"""
        available_cameras = self._get_available_cameras()

        if not available_cameras:
            tk.messagebox.showinfo("Cámaras disponibles", "No se encontraron cámaras disponibles.")
            return

        self._create_camera_selection_window(available_cameras)

    def _get_available_cameras(self):
        """Devuelve las cámaras disponibles"""
        cameras = []
        for i in range(3): 
            cap = cv2.VideoCapture(i)
            if cap.isOpened():
                cameras.append(f"Cámara {i}")
                cap.release()
                
        return cameras

    def _create_camera_selection_window(self, cameras):
        """Crea la ventana de selección de cámara"""
        window = tk.Toplevel(self.root)
        window.title("Seleccionar cámara")
        window.geometry("300x200")

        listbox = tk.Listbox(window, height=len(cameras), width=30)
        listbox.pack(padx=10, pady=10)

        for cam in cameras:
            listbox.insert(tk.END, cam)

        select_button = tk.Button(
            window, 
            text="Seleccionar", 
            command=lambda: self._select_camera(listbox, window)
        )
        select_button.pack(pady=5)

    def _select_camera(self, listbox, window):
        """Selecciona una cámara de la lista"""
        selected_index = listbox.curselection()
        if not selected_index:
            return

        self.cam_index = int(selected_index[0])
        self._restart_camera()
        window.destroy()

    def _restart_camera(self):
        """Reinicia la cámara con el nuevo índice"""
        self.running = False
        if self.cap:
            self.cap.release()

        self.running = True
        self.capture_thread = Thread(target=self._capture_frames, daemon=True)
        self.capture_thread.start()


def main():
    root = tk.Tk()
    app = SpectrometerApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()