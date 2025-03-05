# FLAC Downloader

## Descripción

FLAC Downloader es una aplicación en Python que permite descargar música en formato FLAC de plataformas como YouTube, SoundCloud y Bandcamp. La herramienta es sencilla de usar, cuenta con una interfaz gráfica desarrollada con Tkinter y permite descargar varias canciones a la vez o una sola canción desde un archivo de URLs. Además, incluye la posibilidad de agregar metadatos y miniaturas a los archivos FLAC descargados.

## Características

- **Interfaz Gráfica**: Desarrollada con Tkinter para facilitar la interacción con el usuario.
- **Descarga en FLAC**: Convierte automáticamente los archivos de audio a formato FLAC de alta calidad.
- **Soporte para múltiples plataformas**: Puedes descargar música desde YouTube, SoundCloud y Bandcamp.
- **Metadatos**: Agrega títulos y miniaturas a los archivos FLAC descargados.
- **Progreso en tiempo real**: Visualiza el progreso de las descargas mediante una barra de progreso.

## Requisitos

Antes de ejecutar la aplicación, asegúrate de tener instalados los siguientes paquetes:

- **yt-dlp**: Para la descarga de audio desde plataformas.
- **requests**: Para la descarga de miniaturas.
- **mutagen**: Para agregar metadatos a los archivos FLAC.
- **Pillow**: Para el manejo de imágenes.
- **Tkinter**: Para la creación de la interfaz gráfica.

Puedes instalar los paquetes necesarios ejecutando:

```bash
pip install yt-dlp requests mutagen Pillow
```
