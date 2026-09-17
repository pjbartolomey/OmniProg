# 🛠️ OmniProg

OmniProg es una aplicación de escritorio desarrollada en Python con una interfaz gráfica interactiva, diseñada para la gestión, comunicación y control de firmware y drivers.

## 🚀 Características principales

* **Interfaz Gráfica Avanzada**: Diseñada con Qt (PySide) para una experiencia de usuario fluida.
* **Gestión de Firmware**: Módulos dedicados para la carga y verificación de firmware en dispositivos.
* **Control de Drivers**: Comunicación directa y manejo de librerías de hardware específicas.
* **Configuración Flexible**: Almacenamiento de parámetros mediante archivos de configuración `.ini`.

## 📦 Requisitos e Instalación

Para ejecutar este proyecto en tu entorno local (como Debian u otras distribuciones), asegúrate de tener instalado Python 3 y las librerías necesarias.

1. **Clonar el repositorio:**
   ```bash
   git clone git@github.com:pjbartolomey/OmniProg.git
   cd OmniProg
   ```

2. **Instalar dependencias:**
   *(Próximamente añadiremos el archivo de requerimientos exactos)*

3. **Ejecutar la aplicación:**
   ```bash
   python3 OmniProg.py
   ```

#  Convertir a ejecutable (Omniprog.exe)
   ```bash
   Usa pyinstaller
   ```
## 📂 Estructura del Proyecto

* `OmniProg.py`: Archivo principal que arranca la aplicación.
* `omni_firmware.py` y `omni_drivers.py`: Módulos de bajo nivel para interacción con hardware.
* `OmniProg.ui` y `OmniProg_ui.py`: Archivos de diseño de la interfaz gráfica.
* `OmniProg.ini`: Archivo para almacenar la configuración de la app.
