import tkinter as tk
from tkinter import messagebox

OPERACIONES = [
    "Suma de 2 dígitos",
    "Resta de 2 dígitos",
    "Multiplicación (2 dígitos × 1)",
    "División exacta",
]

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Cálculo Mental")
        self.geometry("420x480")
        self.configure(bg="#f4f1fa")
        self.crear_menu()

    def crear_menu(self):
        tk.Label(self, text="Cálculo Mental", font=("Arial", 22, "bold"),
                 bg="#f4f1fa").pack(pady=15)

        tk.Label(self, text="Tu nombre:", bg="#f4f1fa").pack()
        self.nombre = tk.Entry(self, font=("Arial", 12), justify="center")
        self.nombre.pack(pady=5)

        tk.Label(self, text="Modo:", bg="#f4f1fa").pack(pady=(15, 0))
        self.modo = tk.StringVar(value="Práctica")
        for m in ("Práctica", "Competencia"):
            tk.Radiobutton(self, text=m, variable=self.modo, value=m,
                           bg="#f4f1fa").pack()

        tk.Label(self, text="¿Qué quieres practicar?", bg="#f4f1fa").pack(pady=(15, 5))
        for i, op in enumerate(OPERACIONES):
            tk.Button(self, text=op, width=30, height=2,
                      command=lambda i=i: self.elegir(i)).pack(pady=3)

    def elegir(self, indice):
        nombre = self.nombre.get().strip()
        if not nombre:
            messagebox.showwarning("Falta el nombre", "Escribe tu nombre primero.")
            return
        messagebox.showinfo("Elegiste",
                            f"{nombre} - {OPERACIONES[indice]} - {self.modo.get()}")

if __name__ == "__main__":
    App().mainloop()