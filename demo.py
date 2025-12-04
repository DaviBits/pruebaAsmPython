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
#  GUI CORREGIDA - TECLADO FUNCIONAL
# ============================
class InterfazDemo:
    def __init__(self, root, dificultad=0):
        self.root = root
        root.title("4 Imágenes 1 Palabra - Teclado Funcional")
        root.geometry("900x1000")
        root.configure(bg="#1e1e1e")
        
        # Variables
        self.tiempo_corriendo = False
        self.tiempo_actual_ms = 0
        self.intentos = 0
        self.dificultad = dificultad
        
        self.color_bg = "#1e1e1e"
        self.color_panel = "#2b2b2b"
        self.color_btn = "#4caf50"
        self.color_text = "#ffffff"
        self.color_correct = "#4caf50"
        self.color_incorrect = "#ff4444"
        self.color_partial = "#ffa500"
        self.color_tiempo = "#FFD700"

        # Palabra correcta
        self.categoria = obtener_categoria(dificultad)
        print(f"Palabra elegida: {self.categoria}")
        
        self.word = self.categoria.upper()
        self.carpeta = os.path.join(BASE, "Imagenes", self.categoria)
        
        # Inicializar letras disponibles PRIMERO
        self.letras_disponibles = self.obtener_letras_disponibles()
        print(f"Letras disponibles: {self.letras_disponibles}")

        # ========== INTERFAZ ==========
        
        # Header
        frame_header = tk.Frame(root, bg=self.color_bg)
        frame_header.pack(pady=10, fill="x", padx=20)
        
        tk.Label(
            frame_header,
            text="🎯 ADIVINA LA PALABRA",
            font=("Helvetica", 22, "bold"),
            bg=self.color_bg,
            fg=self.color_text
        ).pack(side="left")
        
        # Temporizador
        self.label_tiempo = tk.Label(
            frame_header,
            text="⏱️ 00:00.000",
            font=("Courier", 16, "bold"),
            bg=self.color_bg,
            fg=self.color_tiempo
        )
        self.label_tiempo.pack(side="right")
        
        # Información
        palabra_sin_espacios = "".join(ch for ch in self.word if ch != " ")
        longitud = lib.lenCad(palabra_sin_espacios.encode())
        
        tk.Label(
            root,
            text=f"Dificultad: {['Fácil','Medio','Difícil'][dificultad]} | Letras: {longitud}",
            font=("Helvetica", 12),
            bg=self.color_bg,
            fg="#aaaaaa"
        ).pack(pady=(0, 10))
        
        # Debug info
        tk.Label(
            root,
            text=f"Letras disponibles ({len(self.letras_disponibles)}): {self.letras_disponibles}",
            font=("Courier", 10),
            bg=self.color_bg,
            fg="#888888"
        ).pack()

        # IMÁGENES
        frame_imgs = tk.Frame(root, bg=self.color_panel, bd=2, relief="ridge")
        frame_imgs.pack(pady=15)

        num_imagenes = 4 if dificultad == 0 else 2
        self.imagenes_tk = []
        
        for i in range(1, num_imagenes + 1):
            try:
                ruta = os.path.join(self.carpeta, f"img{i}.png")
                img = Image.open(ruta).resize((150, 150))
                tk_img = ImageTk.PhotoImage(img)
                lbl = tk.Label(frame_imgs, image=tk_img, bg=self.color_panel)
                lbl.image = tk_img
                lbl.grid(row=0, column=i-1, padx=10, pady=10)
                self.imagenes_tk.append(tk_img)
            except:
                lbl = tk.Label(frame_imgs, text=f"Img {i}", 
                             bg=self.color_panel, fg="white", width=20, height=8)
                lbl.grid(row=0, column=i-1, padx=10, pady=10)

        # SLOTS
        palabra_sin_espacios = "".join(ch for ch in self.word if ch != " ")
        num_slots = lib.lenCad(palabra_sin_espacios.encode())
        self.slots = []
        self.letras_bloqueadas = [False] * num_slots
        
        # Frame para slots
        frame_slots_container = tk.Frame(root, bg=self.color_bg)
        frame_slots_container.pack(pady=20)
        
        # Instrucción clara
        tk.Label(
            frame_slots_container,
            text="Escribe con el teclado o haz clic en letras para borrar",
            font=("Helvetica", 12),
            bg=self.color_bg,
            fg="#4CAF50"
        ).pack(pady=(0, 10))
        
        # Slots organizados
        self.crear_slots(frame_slots_container)
        
        # Mostrar letras disponibles DE NUEVO para referencia
        frame_letras_ref = tk.Frame(root, bg=self.color_bg)
        frame_letras_ref.pack(pady=10)
        
        tk.Label(
            frame_letras_ref,
            text=f"Puedes usar estas letras:",
            font=("Helvetica", 11),
            bg=self.color_bg,
            fg="#cccccc"
        ).pack()
        
        # Mostrar letras en grupos para mejor visibilidad
        letras_grupos = [self.letras_disponibles[i:i+10] for i in range(0, len(self.letras_disponibles), 10)]
        for grupo in letras_grupos:
            tk.Label(
                frame_letras_ref,
                text=grupo,
                font=("Courier", 14, "bold"),
                bg=self.color_bg,
                fg="#4CAF50"
            ).pack()

        # CONTROLES
        frame_controles = tk.Frame(root, bg=self.color_bg)
        frame_controles.pack(pady=20)
        
        self.btn_validar = tk.Button(
            frame_controles,
            text="✅ VALIDAR (ENTER)",
            font=("Helvetica", 14, "bold"),
            bg="#4caf50",
            fg="white",
            command=self.validar,
            width=15,
            height=2
        )
        self.btn_validar.pack(side="left", padx=10)
        
        btn_limpiar = tk.Button(
            frame_controles,
            text="🗑️ LIMPIAR TODO",
            font=("Helvetica", 12),
            bg="#F44336",
            fg="white",
            command=self.limpiar_todo,
            width=12,
            height=2
        )
        btn_limpiar.pack(side="left", padx=10)
        
        btn_reiniciar = tk.Button(
            frame_controles,
            text="🔄 REINICIAR",
            font=("Helvetica", 12),
            bg="#2196F3",
            fg="white",
            command=self.reiniciar,
            width=10,
            height=2
        )
        btn_reiniciar.pack(side="left", padx=10)

        # Configurar teclado - ¡VERSIÓN SIMPLIFICADA!
        self.root.bind("<Key>", self.manejar_tecla_simple)
        self.root.focus_set()  # Asegurar que la ventana tenga foco
        
        # Iniciar temporizador
        self.iniciar_temporizador()
        self.actualizar_tiempo()

    def obtener_letras_disponibles(self):
        """Obtiene letras disponibles de forma más simple"""
        palabra = self.categoria.upper().replace(" ", "")
        
        # Letras de la palabra
        letras_palabra = list(palabra)
        
        # Añadir letras aleatorias si es necesario
        import random
        while len(letras_palabra) < 12:
            letra = chr(random.randint(65, 90))  # A-Z
            letras_palabra.append(letra)
        
        # Mezclar
        random.shuffle(letras_palabra)
        return ''.join(letras_palabra[:12])  # Tomar solo 12 letras

    def crear_slots(self, parent):
        """Crea slots de forma simple"""
        self.slots = []
        
        frame_slots = tk.Frame(parent, bg=self.color_bg)
        frame_slots.pack()
        
        col = 0
        row_frame = None
        
        for i, ch in enumerate(self.word):
            if col == 0 or col >= 15:
                if row_frame:
                    row_frame.pack()
                row_frame = tk.Frame(frame_slots, bg=self.color_bg)
                row_frame.pack(pady=5)
                col = 0
            
            if ch == " ":
                tk.Label(row_frame, text="   ", bg=self.color_bg).grid(row=0, column=col, padx=2)
                col += 1
                continue
            
            slot = tk.Label(
                row_frame,
                text="",
                font=("Helvetica", 24, "bold"),
                width=2,
                height=1,
                bg="#333333",
                fg="white",
                relief="solid",
                bd=2
            )
            slot.grid(row=0, column=col, padx=2)
            slot.bind("<Button-1>", lambda e, idx=len(self.slots): self.remover_letra(idx))
            self.slots.append(slot)
            col += 1
        
        if row_frame:
            row_frame.pack()

    def manejar_tecla_simple(self, event):
        """Manejo SIMPLE del teclado - ¡ESTA FUNCIONA!"""
        print(f"Tecla presionada: {event.keysym} - Char: '{event.char}'")
        
        # Enter para validar
        if event.keysym in ["Return", "KP_Enter"]:
            self.validar()
            return
        
        # Backspace para borrar
        if event.keysym in ["BackSpace", "Delete"]:
            for i in range(len(self.slots)-1, -1, -1):
                if self.slots[i].cget("text") and not self.letras_bloqueadas[i]:
                    self.remover_letra(i)
                    break
            return
        
        # Letras normales
        letra = event.char.upper()
        if letra and letra.isalpha():
            print(f"Intentando colocar letra: {letra}")
            print(f"Letras disponibles: {self.letras_disponibles}")
            print(f"¿Está '{letra}' en disponibles? {letra in self.letras_disponibles}")
            
            # Verificación SIMPLE en Python
            if letra in self.letras_disponibles:
                self.colocar_letra_simple(letra)
            else:
                print(f"Letra '{letra}' no está en las disponibles")
        
        # Forzar actualización
        self.root.update()

    def colocar_letra_simple(self, letra):
        """Coloca letra de forma simple"""
        print(f"Colocando letra '{letra}'...")
        
        for i, slot in enumerate(self.slots):
            if not slot.cget("text") and not self.letras_bloqueadas[i]:
                print(f"  Slot {i} disponible, colocando...")
                slot.config(text=letra, fg="yellow", bg="#444444")
                
                # Verificar si está en posición correcta
                palabra_completa = self.word.replace(" ", "")
                if i < len(palabra_completa) and letra == palabra_completa[i]:
                    slot.config(bg="#8bc34a", fg="white")
                    print(f"  ¡Letra en posición correcta!")
                
                break
        else:
            print("  No hay slots disponibles")

    def remover_letra(self, index):
        """Remueve letra"""
        if index < len(self.slots) and not self.letras_bloqueadas[index]:
            self.slots[index].config(text="", bg="#333333", fg="white")

    def limpiar_todo(self):
        """Limpia todos los slots no bloqueados"""
        for i, slot in enumerate(self.slots):
            if not self.letras_bloqueadas[i]:
                slot.config(text="", bg="#333333", fg="white")

    def reiniciar(self):
        """Reinicia el juego"""
        self.limpiar_todo()
        lib.iniciar_temporizador()
        self.tiempo_corriendo = True
        self.intentos = 0
        messagebox.showinfo("Reiniciado", "Juego reiniciado. ¡Buena suerte!")

    # ========== TEMPORIZADOR ==========
    
    def iniciar_temporizador(self):
        lib.iniciar_temporizador()
        self.tiempo_corriendo = True
    
    def actualizar_tiempo(self):
        if self.tiempo_corriendo:
            self.tiempo_actual_ms = lib.obtener_tiempo_actual()
            
            # Formatear
            minutos = self.tiempo_actual_ms // 60000
            segundos = (self.tiempo_actual_ms % 60000) // 1000
            milisegundos = self.tiempo_actual_ms % 1000
            
            tiempo_str = f"{minutos:02d}:{segundos:02d}.{milisegundos:03d}"
            self.label_tiempo.config(text=f"⏱️ {tiempo_str}")
        
        self.root.after(100, self.actualizar_tiempo)

    # ========== VALIDACIÓN ==========
    
    def validar(self):
        """Valida la palabra"""
        palabra_usuario = ""
        for slot in self.slots:
            palabra_usuario += slot.cget("text") or ""
        
        palabra_correcta = self.word.replace(" ", "")
        
        print(f"Validando: '{palabra_usuario}' vs '{palabra_correcta}'")
        
        if not palabra_usuario:
            messagebox.showwarning("Vacío", "Ingresa al menos una letra")
            return
        
        # Usar cmpCad de C para comparar
        usuario_b = palabra_usuario.encode()
        correcta_b = palabra_correcta.encode()
        
        son_iguales = lib.cmpCad(usuario_b, correcta_b)
        
        self.intentos += 1
        
        if son_iguales == 1:
            self.nivel_completado(palabra_usuario)
        else:
            self.analizar_error(palabra_usuario, palabra_correcta)
    
    def nivel_completado(self, palabra_usuario):
        """Nivel completado correctamente"""
        tiempo_final = lib.detener_temporizador()
        self.tiempo_corriendo = False
        
        minutos = tiempo_final // 60000
        segundos = (tiempo_final % 60000) // 1000
        milisegundos = tiempo_final % 1000
        tiempo_str = f"{minutos:02d}:{segundos:02d}.{milisegundos:03d}"
        
        mensaje = f"🎉 ¡CORRECTO!\n\n"
        mensaje += f"Palabra: {self.categoria}\n"
        mensaje += f"Tiempo: {tiempo_str}\n"
        mensaje += f"Intentos: {self.intentos}\n\n"
        
        if tiempo_final < 30000:
            mensaje += "🏆 ¡Excelente tiempo!"
        elif tiempo_final < 60000:
            mensaje += "👍 ¡Buen trabajo!"
        else:
            mensaje += "✅ ¡Completado!"
        
        messagebox.showinfo("¡Felicidades!", mensaje)
        
        # Marcar todo como correcto
        for i, slot in enumerate(self.slots):
            slot.config(bg=self.color_correct, fg="white")
            self.letras_bloqueadas[i] = True
        
        # Deshabilitar validación
        self.btn_validar.config(state="disabled", bg="#666666")
        self.root.unbind("<Key>")
    
    def analizar_error(self, palabra_usuario, palabra_correcta):
        """Analiza error"""
        posiciones_correctas = []
        
        for i in range(min(len(palabra_usuario), len(palabra_correcta))):
            if palabra_usuario[i] == palabra_correcta[i]:
                posiciones_correctas.append(i)
                if i < len(self.slots):
                    self.letras_bloqueadas[i] = True
                    self.slots[i].config(bg=self.color_partial, fg="white")
        
        if posiciones_correctas:
            mensaje = f"✅ {len(posiciones_correctas)} letra(s) correcta(s)\n"
        else:
            # Verificar letras correctas en mala posición
            correctas_mal_pos = 0
            for letra in set(palabra_usuario):
                if letra in palabra_correcta:
                    correctas_mal_pos += 1
            
            if correctas_mal_pos > 0:
                mensaje = f"🔀 {correctas_mal_pos} letra(s) en mala posición\n"
            else:
                mensaje = "❌ Ninguna letra correcta\n"
        
        mensaje += f"Intento: {self.intentos}"
        messagebox.showwarning("Incorrecto", mensaje)
        
        # Limpiar incorrectos después de 1 segundo
        self.root.after(1000, self.limpiar_incorrectos)
    
    def limpiar_incorrectos(self):
        """Limpia letras incorrectas"""
        for i, slot in enumerate(self.slots):
            if not self.letras_bloqueadas[i] and slot.cget("text"):
                slot.config(text="", bg="#333333", fg="white")


# ============================
#  MENÚ SIMPLE
# ============================
class MenuSimple:
    def __init__(self, root):
        self.root = root
        root.title("4 Imágenes 1 Palabra")
        root.geometry("500x400")
        root.configure(bg="#1e1e1e")
        
        tk.Label(
            root,
            text="🎮 4 IMÁGENES 1 PALABRA",
            font=("Helvetica", 28, "bold"),
            bg="#1e1e1e",
            fg="#4CAF50"
        ).pack(pady=40)
        
        tk.Label(
            root,
            text="Con funciones en Assembler",
            font=("Helvetica", 14),
            bg="#1e1e1e",
            fg="#FFD700"
        ).pack(pady=(0, 30))
        
        frame = tk.Frame(root, bg="#1e1e1e")
        frame.pack()
        
        tk.Label(
            frame,
            text="Selecciona dificultad:",
            font=("Helvetica", 16),
            bg="#1e1e1e",
            fg="white"
        ).pack(pady=(0, 20))
        
        btn_facil = tk.Button(
            frame,
            text="FÁCIL (4 imágenes)",
            font=("Helvetica", 12, "bold"),
            bg="#4CAF50",
            fg="white",
            width=20,
            height=2,
            command=lambda: self.iniciar(0)
        )
        btn_facil.pack(pady=5)
        
        btn_medio = tk.Button(
            frame,
            text="MEDIO (2 imágenes)",
            font=("Helvetica", 12, "bold"),
            bg="#FF9800",
            fg="white",
            width=20,
            height=2,
            command=lambda: self.iniciar(1)
        )
        btn_medio.pack(pady=5)
        
        btn_dificil = tk.Button(
            frame,
            text="DIFÍCIL (2 imágenes)",
            font=("Helvetica", 12, "bold"),
            bg="#F44336",
            fg="white",
            width=20,
            height=2,
            command=lambda: self.iniciar(2)
        )
        btn_dificil.pack(pady=5)
        
        # Instrucción
        tk.Label(
            root,
            text="Usa el TECLADO para escribir letras",
            font=("Helvetica", 11),
            bg="#1e1e1e",
            fg="#888888"
        ).pack(pady=30)

    def iniciar(self, dificultad):
        self.root.destroy()
        root = tk.Tk()
        app = InterfazDemo(root, dificultad)
        root.mainloop()


if __name__ == "__main__":
    print("="*60)
    print("INICIANDO JUEGO - TECLADO FUNCIONAL")
    print("="*60)
    
    root = tk.Tk()
    menu = MenuSimple(root)
    root.mainloop()