import cv2
import numpy as np
from src.graph import histogram

def analyze_colors(frame):
    """Analiza los colores en un frame dividiéndolo en 4 regiones"""
    height, width, _ = frame.shape
    mid_h, mid_w = height // 2, width // 2
    
    regions = {
        "Superior Izquierda": frame[:mid_h, :mid_w],
        "Superior Derecha": frame[:mid_h, mid_w:],
        "Inferior Izquierda": frame[mid_h:, :mid_w],
        "Inferior Derecha": frame[mid_h:, mid_w:]
    }
    
    avg_colors = {
        name: np.mean(region, axis=(0, 1)).astype(int) 
        for name, region in regions.items()
    }
    
    center_color = np.mean(list(avg_colors.values()), axis=0).astype(int)
    return avg_colors, center_color

def start_camera(cam_index):
    """Función de demostración para iniciar la cámara directamente"""
    cap = cv2.VideoCapture(cam_index)
    if not cap.isOpened():
        print("No se pudo abrir la cámara.")
        return

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break

            avg_colors, center_color = analyze_colors(frame)
            print("Colores por región:", avg_colors)
            print("Color estimado en el centro:", center_color)
            histogram.update_histogram(center_color)

            cv2.imshow("Video", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    finally:
        cap.release()
        cv2.destroyAllWindows()