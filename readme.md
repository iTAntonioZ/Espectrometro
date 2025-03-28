# 📷 Espectrómetro de Colores con Cámara

![Demo del Espectrómetro](src/assets/img/test.png) <!-- Reemplaza con una imagen real de tu proyecto -->

Un aplicativo que analiza los colores en tiempo real utilizando la cámara de tu dispositivo, mostrando un histograma de los componentes RGB del área central de la imagen.

## ✨ Características

- 🎥 Captura de video en tiempo real con selección de cámara
- 🎨 Análisis de color por cuadrantes y área central
- 📊 Visualización de histograma RGB minimalista
- 🖥️ Interfaz intuitiva con TKinter
- 🔄 Actualización en tiempo real (~60 FPS)

## 📦 Requisitos

- Python 3.8+
- OpenCV (`opencv-python`)
- NumPy
- Pillow (PIL)
- Matplotlib
- TKinter (normalmente incluido con Python)

## 🚀 Instalación

1. Clona el repositorio:

```bash
git clone https://github.com/iTAntonioZ/Espectrometro.git
cd espectrometro
```

2. Instala las dependencias:

```bash
pip install #Para instalar cada una de las dependencias
```

## 🏗️ Estructura del Proyecto

```
espectrometro-camara/
├── src/
│   ├── cam.py           # Lógica de análisis de color
│   ├── graph.py         # Visualización del histograma
│   ├── assets/          # Recursos gráficos
│   └── icon/            # Icono de la app
|   ├── img/             # Recursos de la documentación
├── index.py             # Aplicación principal
└── README.md            # Este archivo
```

## 🖥️ Uso

Ejecuta la aplicación principal:

```bash
python index.py
```

### Controles:
- **Cambiar cámara**: Botón para seleccionar entre cámaras disponibles
- **Salir**: Cierra la aplicación correctamente

## 📄 Licencia

De uso libre, la base del programa fue escrito por @iTAntonioZ