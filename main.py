import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QLabel, QComboBox, QPushButton
from PyQt6.QtCore import QTimer
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

import matplotlib.pyplot as plt

from PyQt6.QtGui import QFont
from PyQt6.QtCore import QTimer
from src import camera, mathc
import numpy as np

class SpectrometerApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Espectrómetro en tiempo real")
        self.setGeometry(100, 100, 1200, 700)  # Ajusta el tamaño de la ventana

        # Widgets de la interfaz
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        # Layout principal
        main_layout = QHBoxLayout()
        self.central_widget.setLayout(main_layout)

        # Layout para las gráficas
        graph_layout = QVBoxLayout()
        main_layout.addLayout(graph_layout)

        # Curva del espectro
        self.figure, self.ax1 = plt.subplots(figsize=(6, 3), dpi=100)
        self.canvas1 = FigureCanvas(self.figure)
        graph_layout.addWidget(self.canvas1)

        # Curva de los colores
        self.figure2, self.ax2 = plt.subplots(figsize=(6, 2), dpi=100)
        self.canvas2 = FigureCanvas(self.figure2)
        graph_layout.addWidget(self.canvas2)

        # Datos a la derecha
        self.data_layout = QVBoxLayout()
        main_layout.addLayout(self.data_layout)

        # Información de la sustancia
        self.label = QLabel("Sustancia detectada: No identificada\nValor: ---")
        self.label.setFont(QFont("Arial", 14))
        self.label.setStyleSheet("color: #333; text-align: center;")
        self.data_layout.addWidget(self.label)

        # Selector de cámara
        self.camera_selector = QComboBox()
        self.camera_selector.setStyleSheet("font-size: 14px;")
        self.data_layout.addWidget(self.camera_selector)
        self.camera_selector.currentIndexChanged.connect(self.select_camera)

        # Botón para actualizar lista de cámaras
        self.refresh_button = QPushButton("Actualizar cámaras")
        self.refresh_button.setStyleSheet("font-size: 14px;")
        self.refresh_button.clicked.connect(self.update_camera_list)
        self.data_layout.addWidget(self.refresh_button)

        self.referencia_calibracion = None  # Almacena los valores de referencia

        # Botón para calibrar el espectro
        self.calibrate_button = QPushButton("Calibrar espectro")
        self.calibrate_button.setStyleSheet("font-size: 14px;")
        self.calibrate_button.clicked.connect(self.calibrate_spectrum)
        self.data_layout.addWidget(self.calibrate_button)

        # Inicialización de la cámara
        self.camera = camera.Camera()
        self.update_camera_list()

        # Temporizador para actualizar la interfaz
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_spectrum)
        self.timer.start(100)

    def update_camera_list(self):
        """Actualiza la lista de cámaras disponibles."""
        available_cameras = self.camera.get_available_cameras()
        self.camera_selector.clear()
        self.camera_selector.addItems(available_cameras)

        
    def select_camera(self):
        """Selecciona la cámara según el índice del combo box."""
        camera_index = self.camera_selector.currentIndex()
        self.camera.select_camera(camera_index)

    def calibrate_spectrum(self):
        """Inicia el proceso de calibración del espectro."""
        frame = self.camera.get_frame()
        if frame is None:
            self.label.setText("Error: No se pudo capturar el frame para calibrar.")
            return

        spectrum_data, _ = mathc.procesar_spectro(frame)
        self.referencia_calibracion = spectrum_data
        self.label.setText("Calibración completada con éxito.")

    def update_spectrum(self):
        frame = self.camera.get_frame()
        if frame is None:
            return

        spectrum_data, color_data = mathc.procesar_spectro(frame)

        # Aplicar calibración si está disponible
        if self.referencia_calibracion is not None:
            spectrum_data = mathc.calibrar_espectro(spectrum_data, self.referencia_calibracion)

        # Actualizar gráfica del espectro (optimizada)
        self.ax1.cla()  # Clear axis
        self.ax1.plot(range(0, len(spectrum_data), 10), spectrum_data[::10], color="#007acc", linewidth=1, label="Espectro")  # Muestra cada 10 puntos
        self.ax1.set_facecolor("#f5f5f5")
        self.ax1.set_xlabel("Longitud de onda (aprox.)", fontsize=10)
        self.ax1.set_ylabel("Intensidad", fontsize=10)
        self.ax1.legend()
        self.canvas1.draw()

        # Determinar el color dominante
        color_names = ["Rojo", "Verde", "Azul"]
        dominant_color_index = int(np.argmax(color_data))
        dominant_color = color_names[dominant_color_index]

        # Actualizar gráfica de colores
        self.ax2.cla()  # Clear axis
        self.ax2.bar([dominant_color], [color_data[dominant_color_index]], color=["#ff0000", "#00ff00", "#0000ff"][dominant_color_index], label=f"Color: {dominant_color}")
        self.ax2.set_facecolor("#f5f5f5")
        self.ax2.set_ylabel("Intensidad", fontsize=10)
        self.ax2.legend()
        self.canvas2.draw()

        # Actualizar texto con la sustancia detectada
        detected_value, substance = mathc.detectar_sustancia(spectrum_data)
        self.label.setText(f"Sustancia detectada: {substance}\nValor: {detected_value} nm")


    def closeEvent(self, event):
        self.camera.release()  # Liberar la cámara al cerrar
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SpectrometerApp()
    window.show()
    sys.exit(app.exec())
