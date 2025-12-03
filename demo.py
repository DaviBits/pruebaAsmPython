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
#  GUI
# ============================
class InterfazDemo:
    def __init__(self, root, dificultad=0):
        self.root = root
        root.title("4 Imágenes 1 Palabra - Demo")
        root.geometry("650x700")
        root.configure(bg="#1e1e1e")

        self.color_bg = "#1e1e1e"
        self.color_panel = "#2b2b2b"
        self.color_btn = "#4caf50"
        self.color_btn_hover = "#45a049"
        self.color_text = "#ffffff"

        # 1️⃣ OBTENER CATEGORÍA DESDE ASM
        self.categoria = obtener_categoria(dificultad)
        print("Categoría elegida:", self.categoria)

        # 2️⃣ ARMAR LA RUTA
        self.carpeta = os.path.join(BASE, "Imagenes", self.categoria)

        # ======== TÍTULO =========
        tk.Label(
            root,
            text=f"Palabra oculta ({self.categoria})",
            font=("Helvetica", 28, "bold"),
            bg=self.color_bg,
            fg=self.color_text
        ).pack(pady=20)

        # ======== FRAME IMÁGENES =========
        frame_imgs = tk.Frame(root, bg=self.color_panel, bd=2, relief="ridge")
        frame_imgs.pack(pady=20)

        # 3️⃣ ARCHIVOS DE LAS IMÁGENES
        rutas = [
            os.path.join(self.carpeta, "img1.png"),
            os.path.join(self.carpeta, "img2.png"),
            os.path.join(self.carpeta, "img3.png"),
            os.path.join(self.carpeta, "img4.png")
        ]

        self.imagenes_tk = []

        for i, ruta in enumerate(rutas):
            print("Cargando:", ruta)
            try:
                img = Image.open(ruta).resize((180, 180))
                tk_img = ImageTk.PhotoImage(img)

                lbl = tk.Label(frame_imgs, image=tk_img, bg=self.color_panel)
                lbl.image = tk_img
                lbl.grid(row=i // 2, column=i % 2, padx=15, pady=15)

                self.imagenes_tk.append(tk_img)

            except:
                print("❌ ERROR cargando:", ruta)
                lbl = tk.Label(frame_imgs, text="(no img)", fg="white", bg=self.color_panel)
                lbl.grid(row=i // 2, column=i % 2, padx=15, pady=15)

        # ======== ENTRY =========
        self.entry = tk.Entry(
            root,
            font=("Helvetica", 20),
            justify="center",
            bg="#333333",
            fg="white",
            insertbackground="white",
            relief="flat"
        )
        self.entry.pack(pady=15, ipadx=10, ipady=5)

        # ======== BOTÓN =========
        self.btn = tk.Button(
            root,
            text="Responder",
            font=("Helvetica", 18, "bold"),
            bg=self.color_btn,
            fg="white",
            relief="flat",
            command=self.boton_responder
        )
        self.btn.pack(pady=20, ipadx=15, ipady=5)

        self.btn.bind("<Enter>", lambda e: self.btn.config(bg=self.color_btn_hover))
        self.btn.bind("<Leave>", lambda e: self.btn.config(bg=self.color_btn))

    def boton_responder(self):
        texto = self.entry.get().strip().lower()
        if texto == self.categoria.lower():
            messagebox.showinfo("Correcto", "¡Bien hecho!")
        else:
            messagebox.showwarning("Incorrecto", "Esa no es la palabra.")


# ============================
#  MAIN
# ============================
if __name__ == "__main__":
    root = tk.Tk()
    app = InterfazDemo(root, dificultad=0)
    root.mainloop()
