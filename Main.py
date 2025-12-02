import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import os

class InterfazDemo:
    def __init__(self, root):
        self.root = root
        root.title("4 Imágenes 1 Palabra - Demo")
        root.geometry("650x700")
        root.configure(bg="#1e1e1e")  # fondo oscuro elegante

        # ======== ESTILOS =========
        self.color_bg = "#1e1e1e"
        self.color_panel = "#2b2b2b"
        self.color_btn = "#4caf50"
        self.color_btn_hover = "#45a049"
        self.color_text = "#ffffff"

        # ======== TÍTULO =========
        lbl_titulo = tk.Label(
            root, 
            text="4 Imágenes 1 Palabra",
            font=("Helvetica", 28, "bold"),
            bg=self.color_bg,
            fg=self.color_text
        )
        lbl_titulo.pack(pady=20)

        # ======== FRAME DE IMÁGENES (estilizado) =========
        frame_imgs = tk.Frame(root, bg=self.color_panel, bd=2, relief="ridge")
        frame_imgs.pack(pady=20)

        # ======== RUTAS DE IMÁGENES =========
        BASE = os.path.dirname(__file__)
        carpeta_mem = os.path.join(BASE, "Imagenes", "memoria")

        rutas = [
            os.path.join(carpeta_mem, "img1.png"),
            os.path.join(carpeta_mem, "img2.jpg"),
            os.path.join(carpeta_mem, "img3.jpg"),
            os.path.join(carpeta_mem, "img4.png")
        ]

        self.imagenes_tk = []  # evitar GC

        for i, ruta in enumerate(rutas):
            print("Cargando:", ruta)

            img = Image.open(ruta).resize((180, 180))
            tk_img = ImageTk.PhotoImage(img)

            lbl = tk.Label(frame_imgs, image=tk_img, bg=self.color_panel)
            lbl.image = tk_img
            lbl.grid(row=i // 2, column=i % 2, padx=15, pady=15)

            self.imagenes_tk.append(tk_img)

        # ======== CUADRO DE ENTRADA =========
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

        # ======== BOTÓN ESTILIZADO =========
        self.btn = tk.Button(
            root,
            text="Responder",
            font=("Helvetica", 18, "bold"),
            bg=self.color_btn,
            fg="white",
            activebackground=self.color_btn,
            relief="flat",
            command=self.boton_responder
        )
        self.btn.pack(pady=20, ipadx=15, ipady=5)

        # Hover del botón
        self.btn.bind("<Enter>", lambda e: self.btn.config(bg=self.color_btn_hover))
        self.btn.bind("<Leave>", lambda e: self.btn.config(bg=self.color_btn))

    def boton_responder(self):
        texto = self.entry.get()
        messagebox.showinfo("Respuesta recibida", f"Tú escribiste: {texto}")


# ========================
# MAIN
# ========================
if __name__ == "__main__":
    root = tk.Tk()
    app = InterfazDemo(root)
    root.mainloop()
