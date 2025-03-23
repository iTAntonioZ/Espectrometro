import numpy as np

def procesar_spectro(frame):
    """Procesa el espectro a partir del frame capturado."""
    # Verifica si el frame tiene 3 dimensiones (alto, ancho, canales de color)
    if len(frame.shape) == 3:
        height, width, _ = frame.shape  # Descartamos el canal de color
    else:
        height, width = frame.shape

    # Calcula la intensidad promedio por columna de píxeles (en el eje x)
    spectrum_data = np.mean(frame, axis=0).tolist()
    
    # Obtiene los valores promedio de cada canal (R, G, B)
    color_data = np.mean(frame, axis=(0, 1))  # Promedio de R, G, B
    color_data = [color_data[0], color_data[1], color_data[2]]  # R, G, B

    return spectrum_data, color_data

def detectar_sustancia(spectrum_data):
    """Detecta la sustancia según la intensidad del espectro."""
    detected_value = np.argmax(spectrum_data)  # Índice con la mayor intensidad
    substance = "No identificada"
    
    # Identificación basada en rangos de longitud de onda
    if 400 <= detected_value <= 500:
        substance = "Sustancia Azul"
    elif 500 < detected_value <= 600:
        substance = "Sustancia Verde"
    elif 600 < detected_value <= 700:
        substance = "Sustancia Roja"

    return detected_value, substance

def calibrar_espectro(spectrum_data, referencia):
    """
    Calibra el espectro utilizando valores de referencia.
    :param spectrum_data: Datos del espectro original.
    :param referencia: Valores de referencia para la calibración.
    :return: Datos del espectro calibrado.
    """
    factor_calibracion = np.array(referencia) / np.max(spectrum_data)
    spectrum_calibrado = np.array(spectrum_data) * factor_calibracion
    return spectrum_calibrado.tolist()
