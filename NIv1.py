import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import os
from cffi import FFI
import _game_lib

# ============================
#  CONEXIÓN C/ASM
# ============================
lib = _game_lib.lib
ffi = FFI()
lib.init_rand_seed()

BASE = os.path.abspath(os.path.dirname(__file__))

ARCHIVOS = [
    os.path.join(BASE, "niveles", "facil.txt").encode(),
    os.path.join(BASE, "niveles", "medio.txt").encode(),
    os.path.join(BASE, "niveles", "dificil.txt").encode(),
]

def obtener_categoria(dificultad: int) -> str:
    txt_buffer = ffi.new("char[]", 4096)
    categoria = ffi.new("char[]", 256)

    leidos = lib.leerArchivo(ARCHIVOS[dificultad], txt_buffer, 4096)
    if leidos <= 0:
        raise FileNotFoundError("No se pudo leer archivo")

    lib.obtenerLineaRandom(txt_buffer, categoria)
    return ffi.string(categoria).decode().strip()


# ============================
#  GUI PANTALLA GRANDE 50/50
# ============================
class InterfazDemo:
    def __init__(self, root, dificultad=0):
        self.root = root
        root.title("4 Imágenes 1 Palabra")
        root.geometry("1100x900")  # ¡MÁS GRANDE!
        root.configure(bg="#1e1e1e")
        
        # Centrar ventana en pantalla
        root.update_idletasks()
        ancho = 1100
        alto = 900
        x = (root.winfo_screenwidth() // 2) - (ancho // 2)
        y = (root.winfo_screenheight() // 2) - (alto // 2)
        root.geometry(f'{ancho}x{alto}+{x}+{y}')

        self.color_bg = "#1e1e1e"
        self.color_panel = "#2b2b2b"
        self.color_text = "#ffffff"
        self.color_accent = "#4CAF50"

        # 1️⃣ OBTENER CATEGORÍA DESDE ASM
        self.categoria = obtener_categoria(dificultad)
        print("Categoría elegida:", self.categoria)

        # 2️⃣ ARMAR LA RUTA
        self.carpeta = os.path.join(BASE, "Imagenes", self.categoria)

        # ======== TÍTULO =========
        titulo_frame = tk.Frame(root, bg=self.color_bg, height=80)
        titulo_frame.pack(fill="x", pady=15)
        
        tk.Label(
            titulo_frame,
            text="🎯 4 IMÁGENES 1 PALABRA",
            font=("Helvetica", 32, "bold"),
            bg=self.color_bg,
            fg=self.color_accent
        ).pack()
        
        tk.Label(
            titulo_frame,
            text="Observa las imágenes y adivina la palabra oculta",
            font=("Helvetica", 16),
            bg=self.color_bg,
            fg="#aaaaaa"
        ).pack(pady=(5, 0))

        # ======== CONTENEDOR PRINCIPAL (divide pantalla 50/50) =========
        main_container = tk.Frame(root, bg=self.color_bg)
        main_container.pack(fill="both", expand=True, padx=30, pady=20)

        # ======== PARTE SUPERIOR: IMÁGENES (50%) =========
        top_frame = tk.LabelFrame(
            main_container, 
            text="  IMÁGENES  ",
            font=("Helvetica", 16, "bold"),
            bg=self.color_bg,
            fg=self.color_accent,
            bd=2,
            relief="ridge",
            height=400  # Mitad de 800px
        )
        top_frame.pack(fill="both", pady=(0, 20))
        top_frame.pack_propagate(False)  # Fijar altura

        # Frame para grid de imágenes
        grid_frame = tk.Frame(top_frame, bg=self.color_panel)
        grid_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Configurar grid 2x3 para las 6 imágenes
        for i in range(3):  # 3 columnas
            grid_frame.grid_columnconfigure(i, weight=1, minsize=250)
        for i in range(2):  # 2 filas
            grid_frame.grid_rowconfigure(i, weight=1, minsize=180)

        # 3️⃣ CARGAR Y MOSTRAR 6 IMÁGENES
        self.imagenes_tk = []
        rutas = []
        
        print(f"Buscando imágenes en: {self.carpeta}")
        
        # Buscar las 6 imágenes
        for i in range(1, 7):
            encontrada = False
            for ext in ['.png', '.jpg', '.jpeg', '.PNG', '.JPG', '.JPEG']:
                ruta = os.path.join(self.carpeta, f"img{i}{ext}")
                if os.path.exists(ruta):
                    rutas.append(ruta)
                    encontrada = True
                    print(f"✓ Encontrada: img{i}{ext}")
                    break
            
            if not encontrada:
                # También buscar sin número (img.png, img.jpg)
                for ext in ['.png', '.jpg', '.jpeg']:
                    ruta = os.path.join(self.carpeta, f"img{ext}")
                    if os.path.exists(ruta) and i == 1:  # Solo para primera imagen
                        rutas.append(ruta)
                        encontrada = True
                        print(f"✓ Encontrada: img{ext}")
                        break
            
            if not encontrada:
                rutas.append(None)
                print(f"✗ No encontrada: img{i}")

        # Mostrar imágenes en grid
        for i in range(6):
            row = i // 3
            col = i % 3
            
            # Frame para cada imagen
            img_frame = tk.Frame(
                grid_frame,
                bg="#333333",
                relief="solid",
                bd=1
            )
            img_frame.grid(row=row, column=col, padx=15, pady=15, sticky="nsew")
            
            # Número de imagen pequeño
            num_label = tk.Label(
                img_frame,
                text=str(i+1),
                font=("Helvetica", 10, "bold"),
                bg="#555555",
                fg="white",
                width=3
            )
            num_label.place(x=5, y=5)
            
            if rutas[i] and os.path.exists(rutas[i]):
                try:
                    # Cargar imagen
                    img = Image.open(rutas[i])
                    
                    # Redimensionar manteniendo proporción (tamaño más grande)
                    ancho_original, alto_original = img.size
                    ancho_max, alto_max = 220, 220  # Más grande en pantalla grande
                    
                    ratio = min(ancho_max/ancho_original, alto_max/alto_original)
                    nuevo_ancho = int(ancho_original * ratio)
                    nuevo_alto = int(alto_original * ratio)
                    
                    img_resized = img.resize((nuevo_ancho, nuevo_alto), Image.Resampling.LANCZOS)
                    
                    # Crear fondo para centrar imagen
                    fondo = Image.new('RGB', (ancho_max, alto_max), color="#333333")
                    x_offset = (ancho_max - nuevo_ancho) // 2
                    y_offset = (alto_max - nuevo_alto) // 2
                    fondo.paste(img_resized, (x_offset, y_offset))
                    
                    tk_img = ImageTk.PhotoImage(fondo)
                    
                    lbl = tk.Label(
                        img_frame,
                        image=tk_img,
                        bg="#333333"
                    )
                    lbl.image = tk_img
                    lbl.place(relx=0.5, rely=0.5, anchor="center")
                    
                    self.imagenes_tk.append(tk_img)
                    
                except Exception as e:
                    print(f"Error cargando {rutas[i]}: {e}")
                    lbl = tk.Label(
                        img_frame,
                        text=f"Imagen {i+1}\nError al cargar",
                        font=("Helvetica", 12),
                        bg="#333333",
                        fg="#ff6666",
                        wraplength=180
                    )
                    lbl.place(relx=0.5, rely=0.5, anchor="center")
            else:
                # Placeholder para imagen faltante
                lbl = tk.Label(
                    img_frame,
                    text=f"Imagen {i+1}\n\nNo disponible",
                    font=("Helvetica", 14),
                    bg="#333333",
                    fg="#888888",
                    wraplength=180
                )
                lbl.place(relx=0.5, rely=0.5, anchor="center")

        # ======== SEPARADOR =========
        separator = tk.Frame(main_container, height=3, bg="#444444")
        separator.pack(fill="x", pady=15)

        # ======== PARTE INFERIOR: ÁREA DE JUEGO (50%) =========
        bottom_frame = tk.LabelFrame(
            main_container,
            text="  JUEGO - ADIVINA LA PALABRA  ",
            font=("Helvetica", 16, "bold"),
            bg=self.color_bg,
            fg=self.color_accent,
            bd=2,
            relief="ridge",
            height=400  # Mitad de 800px
        )
        bottom_frame.pack(fill="both")
        bottom_frame.pack_propagate(False)  # Fijar altura

        # Contenido del área de juego (placeholder)
        game_content = tk.Frame(bottom_frame, bg=self.color_bg)
        game_content.pack(fill="both", expand=True, padx=30, pady=30)
        
        # Mensaje central
        tk.Label(
            game_content,
            text="🎮 ZONA DE JUEGO 🎮",
            font=("Helvetica", 24, "bold"),
            bg=self.color_bg,
            fg=self.color_accent
        ).pack(pady=(30, 10))
        
        tk.Label(
            game_content,
            text="Aquí irá toda la interfaz del juego:\n• Slots para las letras\n• Botones con letras disponibles\n• Controles de validación\n• Pistas y ayudas",
            font=("Helvetica", 14),
            bg=self.color_bg,
            fg="#cccccc",
            justify="center"
        ).pack(pady=20)
        
        # Ejemplo de slots (placeholder)
        slots_frame = tk.Frame(game_content, bg=self.color_panel, height=60)
        slots_frame.pack(fill="x", pady=20, padx=50)
        
        tk.Label(
            slots_frame,
            text="M _ M _ R _ _",
            font=("Courier", 32, "bold"),
            bg=self.color_panel,
            fg="white",
            padx=20,
            pady=10
        ).pack()
        
        # Ejemplo de botones (placeholder)
        buttons_frame = tk.Frame(game_content, bg=self.color_bg)
        buttons_frame.pack(pady=20)
        
        tk.Label(
            buttons_frame,
            text="Letras disponibles:",
            font=("Helvetica", 14),
            bg=self.color_bg,
            fg="#aaaaaa"
        ).pack()
        
        letters_label = tk.Label(
            buttons_frame,
            text="A B C D E F G H I J K L M N O P Q R S T U V W X Y Z",
            font=("Courier", 16),
            bg=self.color_bg,
            fg="#4CAF50"
        )
        letters_label.pack(pady=10)

        # ======== BARRA INFERIOR CON INFO =========
        status_bar = tk.Frame(root, bg="#2b2b2b", height=40)
        status_bar.pack(side="bottom", fill="x")
        
        tk.Label(
            status_bar,
            text=f"📁 Carpeta: {os.path.basename(self.carpeta)}  |  🔤 Palabra: '{self.categoria}'  |  ⚙️ Dificultad: {['Fácil','Medio','Difícil'][dificultad]}",
            font=("Helvetica", 10),
            bg="#2b2b2b",
            fg="#888888",
            padx=20
        ).pack(side="left")
        
        tk.Label(
            status_bar,
            text="🔄 Listo para implementar juego",
            font=("Helvetica", 10),
            bg="#2b2b2b",
            fg="#4CAF50",
            padx=20
        ).pack(side="right")


# ============================
#  MAIN
# ============================
if __name__ == "__main__":
    root = tk.Tk()
    app = InterfazDemo(root, dificultad=0)
    root.mainloop()