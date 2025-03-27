import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
from threading import Lock

class ColorHistogram:
    def __init__(self):
        self.fig, self.ax = plt.subplots(figsize=(4, 2.5), dpi=100)
        self.fig.patch.set_alpha(0)
        self._setup_axes()
        self._setup_bars()
        self.lock = Lock()

    def _setup_axes(self):
        """Configura los ejes del gráfico"""
        self.ax.set_facecolor('#f5f5f5')
        for spine in ['top', 'right']:
            self.ax.spines[spine].set_visible(False)
        for spine in ['left', 'bottom']:
            self.ax.spines[spine].set_color('#aaaaaa')
        self.ax.set_ylim(0, 10)
        self.ax.set_ylabel("Intensidad", fontsize=8)
        self.ax.tick_params(axis='both', which='major', labelsize=7)
        self.ax.grid(False)

    def _setup_bars(self):
        """Configura las barras del histograma"""
        self.colors = ["R", "G", "B"]
        self.bar_colors = ["#ff5555", "#55aa55", "#5555ff"]
        self.values = [0, 0, 0]
        self.bars = self.ax.bar(
            self.colors, 
            self.values, 
            color=self.bar_colors,
            width=0.6
        )

    def update_histogram(self, center_color):
        """Actualiza el histograma con nuevos valores"""
        normalized = np.clip(center_color / 255 * 10, 0, 10)
        
        with self.lock:
            for i, bar in enumerate(self.bars):
                bar.set_height(normalized[i])
            
            self.ax.draw_artist(self.ax.patch)
            for bar in self.bars:
                self.ax.draw_artist(bar)
            
            self.ax.relim()
            self.ax.autoscale_view(scaley=False)

    def get_minimalist_canvas(self, parent):
        """Devuelve el canvas para Tkinter"""
        canvas = FigureCanvasTkAgg(self.fig, parent)
        canvas.draw()
        return canvas

# Instancia global del histograma
histogram = ColorHistogram()