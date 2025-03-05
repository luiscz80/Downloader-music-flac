import os
import yt_dlp
import requests
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from io import StringIO
from mutagen.flac import FLAC, Picture
from PIL import Image, ImageTk

# Carpeta por defecto
DEFAULT_FOLDER = os.path.expanduser("~/Music")

# Colores minimalistas
BG_COLOR = "#1E1E1E"
FG_COLOR = "#FFFFFF"
BTN_COLOR = "#0078D7"
PROGRESS_COLOR = "#00A300"

# Crear ventana principal
app = tk.Tk()
app.title("FLAC Downloader")
app.geometry("650x500")
app.configure(bg=BG_COLOR)
app.resizable(False, False)

# Estilos
estilo = ttk.Style()
estilo.theme_use("clam")
estilo.configure("TLabel", foreground=FG_COLOR, background=BG_COLOR, font=("Segoe UI", 10))
estilo.configure("TButton", background=BTN_COLOR, foreground=FG_COLOR, font=("Segoe UI", 10, "bold"))
estilo.configure("TEntry", padding=5, font=("Segoe UI", 10))
estilo.map("TButton", background=[("active", "#005a9e")])

# Función para seleccionar carpeta
def seleccionar_carpeta():
    carpeta = filedialog.askdirectory(title="Selecciona la carpeta de descarga")
    if carpeta:
        entrada_carpeta.delete(0, tk.END)
        entrada_carpeta.insert(0, carpeta)

# Función para seleccionar archivo .txt con URLs
def seleccionar_archivo_urls():
    archivo = filedialog.askopenfilename(title="Selecciona el archivo con URLs", filetypes=[("Text files", "*.txt")])
    if archivo:
        entrada_urls_txt.delete(0, tk.END)
        entrada_urls_txt.insert(0, archivo)

# Función para capturar la salida de consola y redirigirla al área de texto
class ConsoleRedirector:
    def __init__(self, text_widget):
        self.text_widget = text_widget
        self.console_output = StringIO()
        self.original_stdout = os.sys.stdout
        os.sys.stdout = self

    def write(self, text):
        self.console_output.write(text)
        self.text_widget.insert(tk.END, text)
        self.text_widget.yview(tk.END)

    def flush(self):
        pass

# Función para descargar audio
def descargar_audio(url, carpeta_destino, calidad="0"):
    if not os.path.exists(carpeta_destino):
        os.makedirs(carpeta_destino)
    
    opciones = {
        'format': 'bestaudio/best',
        'outtmpl': f'{carpeta_destino}/%(title)s.%(ext)s',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'flac',
            'preferredquality': calidad,
        }],
        'writethumbnail': True,
        'progress_hooks': [progreso_hook]
    }
    
    with yt_dlp.YoutubeDL(opciones) as ydl:
        info = ydl.extract_info(url, download=True)
        return os.path.join(carpeta_destino, f"{info.get('title', 'Sin título')}.flac")

# Función que maneja el progreso de descarga
def progreso_hook(d):
    if d['status'] == 'downloading':
        porcentaje = d.get('_percent_str', '0%').strip()
        porcentaje_valor = float(d.get('downloaded_bytes', 0)) / float(d.get('total_bytes', 1)) * 100
        progreso["value"] = porcentaje_valor
        etiqueta_progreso.config(text=f"{porcentaje}")
        texto_progreso.insert(tk.END, f"Descargando... {porcentaje}\n")
        texto_progreso.yview(tk.END)
        app.update_idletasks()

    elif d['status'] == 'finished':
        etiqueta_progreso.config(text="100% Completado")
        progreso["value"] = 100
        texto_progreso.insert(tk.END, "Descarga completada.\n")
        texto_progreso.yview(tk.END)
        app.update_idletasks()


# Función activar inputs con checkbox
def activar_input_urls():
    if descargar_var.get():
        etiqueta_url.grid_remove()
        entrada_url.grid_remove()
        etiqueta_archivo_urls.grid()
        entrada_urls_txt.grid()
        boton_seleccionar_archivo.grid()
    else:
        etiqueta_url.grid()
        entrada_url.grid()
        etiqueta_archivo_urls.grid_remove()
        entrada_urls_txt.grid_remove()
        boton_seleccionar_archivo.grid_remove()

# Función para descargar miniatura
def descargar_imagen(url, ruta_destino):
    try:
        response = requests.get(url, stream=True)
        if response.status_code == 200:
            with open(ruta_destino, "wb") as img_file:
                for chunk in response.iter_content(1024):
                    img_file.write(chunk)
    except Exception as e:
        messagebox.showerror("Error", f"Error al descargar la imagen: {e}")

# Función para agregar metadata
def agregar_metadata(archivo, imagen, titulo):
    try:
        audio = FLAC(archivo)
        audio["title"] = titulo
        if os.path.exists(imagen):
            with open(imagen, "rb") as img_file:
                picture = Picture()
                picture.type = 3
                picture.mime = "image/jpeg"
                picture.data = img_file.read()
                audio.add_picture(picture)
        audio.save()
    except Exception as e:
        messagebox.showerror("Error", f"Error al agregar metadata: {e}")

# Función para iniciar la descarga
def iniciar_descarga():
    carpeta = entrada_carpeta.get() or DEFAULT_FOLDER
    if descargar_var.get():
        # Descargar varias canciones
        if not entrada_urls_txt.get():
            messagebox.showerror("Error", "Por favor, selecciona un archivo con URLs.")
            return

        try:
            with open(entrada_urls_txt.get(), "r") as file:
                urls = file.readlines()

            if not urls:
                messagebox.showerror("Error", "El archivo no contiene URLs válidas.")
                return

            boton_descargar.config(state=tk.DISABLED)
            progreso.start()

            for url in urls:
                url = url.strip()
                if url:
                    try:
                        archivo = descargar_audio(url, carpeta)
                        progreso.step(100 / len(urls))
                        agregar_mensaje(f"Descarga completada: {archivo}")
                    except Exception as e:
                        agregar_mensaje(f"Error en la descarga: {e}")
                else:
                    agregar_mensaje("URL vacía ignorada.")
            
            messagebox.showinfo("Descargas completadas", "Todas las descargas han finalizado.")
        except Exception as e:
            messagebox.showerror("Error", f"Error al procesar el archivo: {e}")
    else:
        # Descargar una sola canción
        url = entrada_url.get()
        if not url:
            messagebox.showerror("Error", "Por favor, ingresa una URL válida.")
            return

        boton_descargar.config(state=tk.DISABLED)
        progreso["value"] = 0
        etiqueta_progreso.config(text="Iniciando...")
        
        try:
            archivo = descargar_audio(url, carpeta)
            agregar_mensaje(f"Descarga completada: {archivo}")
            etiqueta_progreso.config(text="100% Completado")
            progreso["value"] = 100

        except Exception as e:
            agregar_mensaje(f"Error en la descarga: {e}")
        
    boton_descargar.config(state=tk.NORMAL)
    progreso.stop()

# Función para agregar mensajes en el área de texto
def agregar_mensaje(mensaje):
    texto_progreso.insert(tk.END, f"{mensaje}\n")
    texto_progreso.yview(tk.END)
    app.update_idletasks()


# UI Principal
frame = ttk.Frame(app, padding=10, style="TFrame")
frame.pack(fill=tk.BOTH, expand=True)

# Checkbox para seleccionar si se descargan varias canciones
descargar_var = tk.BooleanVar()
checkbox_varios = ttk.Checkbutton(frame, text="Descargar varias canciones", variable=descargar_var, command=activar_input_urls)
checkbox_varios.grid(row=0, column=0, sticky="w", pady=5, columnspan=2)

# Etiqueta y entrada para la URL del video
etiqueta_url = ttk.Label(frame, text="URL del video:")
etiqueta_url.grid(row=1, column=0, sticky="w", pady=5)
entrada_url = ttk.Entry(frame, width=50)
entrada_url.grid(row=1, column=1, pady=5)

# Carpeta de descarga
ttk.Label(frame, text="Carpeta de descarga:").grid(row=2, column=0, sticky="w", pady=5)
entrada_carpeta = ttk.Entry(frame, width=40)
entrada_carpeta.insert(0, DEFAULT_FOLDER)
entrada_carpeta.grid(row=2, column=1, pady=5, sticky="ew")
ttk.Button(frame, text="Seleccionar", command=seleccionar_carpeta).grid(row=2, column=2, padx=5)

# Etiqueta y entrada para seleccionar archivo de URLs (inicialmente ocultos)
etiqueta_archivo_urls = ttk.Label(frame, text="Seleccionar archivo de URLs:")
etiqueta_archivo_urls.grid(row=3, column=0, sticky="w", pady=5)
etiqueta_archivo_urls.grid_remove() 
entrada_urls_txt = ttk.Entry(frame, width=40)
entrada_urls_txt.grid(row=3, column=1, pady=5, sticky="ew")
entrada_urls_txt.grid_remove()
boton_seleccionar_archivo = ttk.Button(frame, text="Seleccionar archivo de URLs", command=seleccionar_archivo_urls)
boton_seleccionar_archivo.grid(row=3, column=2, padx=5)
boton_seleccionar_archivo.grid_remove()

# Botón de descarga
boton_descargar = ttk.Button(frame, text="Descargar FLAC", command=iniciar_descarga)
boton_descargar.grid(row=4, column=1, pady=15)

# Barra de progreso
progreso = ttk.Progressbar(frame, mode="indeterminate", length=200, style="TProgressbar")
etiqueta_progreso = ttk.Label(frame, text="0% completado", background=BG_COLOR, foreground=FG_COLOR)
etiqueta_progreso.grid(row=6, column=1, pady=5)
progreso.grid(row=5, column=1, pady=5)

# Función para actualizar la barra de progreso
def actualizar_progreso(valor, total):
    porcentaje = int((valor / total) * 100)
    progreso["value"] = porcentaje
    etiqueta_progreso.config(text=f"{porcentaje}% completado")
    texto_progreso.insert(tk.END, f"Progreso: {porcentaje}%\n")
    texto_progreso.yview(tk.END)
    app.update_idletasks()

# Área de texto para mostrar el progreso de las descargas
texto_progreso = tk.Text(frame, height=10, width=70, wrap=tk.WORD)
texto_progreso.grid(row=10, column=0, columnspan=3, pady=10)

# Redirigir la salida de consola al área de texto
console_redirector = ConsoleRedirector(texto_progreso)

# Botón de Acerca de en la parte superior izquierda
boton_acerca_de = ttk.Button(app, text="ℹ Acerca de", command=lambda: mostrar_acerca_de())
boton_acerca_de.place(x=535, y=10)

# Función para mostrar el modal de información
def mostrar_acerca_de():
    ventana_acerca = tk.Toplevel(app)
    ventana_acerca.title("Acerca de FLAC Downloader")
    ventana_acerca.geometry("400x300")
    ventana_acerca.configure(bg=BG_COLOR)
    ventana_acerca.resizable(False, False)
    
    ttk.Label(ventana_acerca, text="FLAC Downloader", font=("Segoe UI", 14, "bold"), background=BG_COLOR, foreground=FG_COLOR).pack(pady=10)
    ttk.Label(ventana_acerca, text="Versión: 1.0", font=("Segoe UI", 10), background=BG_COLOR, foreground=FG_COLOR).pack()
    ttk.Label(ventana_acerca, text="Desarrollado por: Luis", font=("Segoe UI", 10), background=BG_COLOR, foreground=FG_COLOR).pack(pady=5)
    
    ttk.Label(ventana_acerca, text="Tipos de URL soportadas:", font=("Segoe UI", 10, "bold"), background=BG_COLOR, foreground=FG_COLOR).pack(pady=5)
    ttk.Label(ventana_acerca, text="- YouTube", font=("Segoe UI", 10), background=BG_COLOR, foreground=FG_COLOR).pack()
    ttk.Label(ventana_acerca, text="- SoundCloud", font=("Segoe UI", 10), background=BG_COLOR, foreground=FG_COLOR).pack()
    ttk.Label(ventana_acerca, text="- Bandcamp", font=("Segoe UI", 10), background=BG_COLOR, foreground=FG_COLOR).pack()
    
    ttk.Label(ventana_acerca, text="Descargas en formato FLAC con metadatos y miniaturas.", wraplength=350, justify="center", font=("Segoe UI", 10), background=BG_COLOR, foreground=FG_COLOR).pack(pady=10)
    
    ttk.Button(ventana_acerca, text="Cerrar", command=ventana_acerca.destroy).pack(pady=10)

app.mainloop()
