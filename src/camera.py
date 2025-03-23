import cv2

class Camera:
    def __init__(self):
        self.cap = None

    def get_available_cameras(self):
        """Devuelve una lista de cámaras disponibles."""
        available_cameras = []
        for i in range(3):  # Intentamos con 10 cámaras posibles
            cap = cv2.VideoCapture(i)
            if cap.isOpened():
                camera_name = cap.getBackendName() or f"Cámara {i}"
                available_cameras.append(f"{camera_name} (Índice {i})")
                cap.release()
        return available_cameras

    def select_camera(self, camera_index):
        """Selecciona la cámara por índice."""
        if self.cap is not None:
            self.cap.release()
        self.cap = cv2.VideoCapture(camera_index)
        if not self.cap.isOpened():
            print(f"Error: No se puede abrir la cámara con índice {camera_index}.")
            self.cap = None
        else:
            print(f"Cámara seleccionada: Índice {camera_index}.")

    def get_frame(self):
        """Obtiene un frame de la cámara seleccionada."""
        if self.cap is None or not self.cap.isOpened():
            return None
        ret, frame = self.cap.read()
        if not ret:
            return None
        return frame

    def release(self):
        """Libera la cámara."""
        if self.cap is not None:
            self.cap.release()
