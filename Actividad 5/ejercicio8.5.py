import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

TOTAL_HABITACIONES = 10
PRECIO_BAJO = 120000
PRECIO_ALTO = 160000
FORMATO_FECHA = "%d/%m/%Y"
TEXTO_FORMATO = "dd/mm/aaaa"


def formatear_pesos(valor):
    return f"${valor:,.0f}"


def leer_fecha(texto):
    """Convierte un texto dd/mm/aaaa en fecha. Lanza ValueError si es inválido."""
    try:
        return datetime.strptime(texto.strip(), FORMATO_FECHA).date()
    except ValueError:
        raise ValueError(f"La fecha debe tener el formato {TEXTO_FORMATO} y ser válida")


# ----------------------------- Modelo -----------------------------

class Huesped:

    def __init__(self, nombre, apellidos, documento):
        if not nombre or not apellidos or not documento:
            raise ValueError("El nombre, los apellidos y el documento son obligatorios")
        if not documento.isdigit():
            raise ValueError("El número de documento debe ser numérico")
        self._nombre = nombre
        self._apellidos = apellidos
        self._documento = documento

    @property
    def nombre(self):
        return self._nombre

    @property
    def apellidos(self):
        return self._apellidos

    @property
    def documento(self):
        return self._documento

    def nombre_completo(self):
        return f"{self._nombre} {self._apellidos}"


class Habitacion:

    def __init__(self, numero, precio_dia):
        self._numero = numero
        self._precio_dia = precio_dia
        self._huesped = None
        self._fecha_ingreso = None

    @property
    def numero(self):
        return self._numero

    @property
    def precio_dia(self):
        return self._precio_dia

    @property
    def huesped(self):
        return self._huesped

    @property
    def fecha_ingreso(self):
        return self._fecha_ingreso

    def esta_disponible(self):
        return self._huesped is None

    def ocupar(self, huesped, fecha_ingreso):
        if not self.esta_disponible():
            raise ValueError("La habitación seleccionada no está disponible")
        self._huesped = huesped
        self._fecha_ingreso = fecha_ingreso

    def liberar(self):
        self._huesped = None
        self._fecha_ingreso = None

    def calcular_dias(self, fecha_salida):
        if fecha_salida <= self._fecha_ingreso:
            raise ValueError("La fecha de salida debe ser mayor a la fecha de ingreso")
        return (fecha_salida - self._fecha_ingreso).days

    def calcular_total(self, fecha_salida):
        return self.calcular_dias(fecha_salida) * self._precio_dia


class Hotel:

    def __init__(self):
        self._habitaciones = []
        mitad = TOTAL_HABITACIONES // 2
        for numero in range(1, TOTAL_HABITACIONES + 1):
            precio = PRECIO_BAJO if numero <= mitad else PRECIO_ALTO
            self._habitaciones.append(Habitacion(numero, precio))

    def listar(self):
        return list(self._habitaciones)

    def buscar(self, numero):
        for habitacion in self._habitaciones:
            if habitacion.numero == numero:
                return habitacion
        raise ValueError(f"La habitación debe estar entre 1 y {TOTAL_HABITACIONES}")

    def buscar_ocupada(self, texto_numero):
        try:
            numero = int(texto_numero)
        except ValueError:
            raise ValueError("Debe ingresar un número de habitación válido")
        habitacion = self.buscar(numero)
        if habitacion.esta_disponible():
            raise ValueError("La habitación indicada no está ocupada")
        return habitacion


# ----------------------------- Ventanas -----------------------------

class VentanaRegistro(tk.Toplevel):
    """Datos del huésped y fecha de ingreso para la habitación elegida."""

    def __init__(self, maestro, hotel, habitacion, al_registrar):
        super().__init__(maestro)
        self._habitacion = habitacion
        self._al_registrar = al_registrar

        self.title(f"Registro - Habitación {habitacion.numero}")
        self.resizable(False, False)
        self.grab_set()

        tk.Label(self, text=f"Habitación {habitacion.numero} "
                            f"({formatear_pesos(habitacion.precio_dia)} por día)",
                 font=("Arial", 11, "bold")).grid(row=0, column=0, columnspan=2, pady=8)

        self._campos = {}
        etiquetas = (f"Fecha de ingreso ({TEXTO_FORMATO})", "Nombres",
                     "Apellidos", "Documento de identidad")
        for fila, etiqueta in enumerate(etiquetas, start=1):
            tk.Label(self, text=etiqueta).grid(row=fila, column=0, padx=8, pady=5, sticky="e")
            entrada = tk.Entry(self, width=28)
            entrada.grid(row=fila, column=1, padx=8, pady=5, sticky="w")
            self._campos[etiqueta] = entrada
        self._campo_fecha = self._campos[etiquetas[0]]
        self._campo_fecha.insert(0, datetime.now().strftime(FORMATO_FECHA))
        self._etiquetas = etiquetas

        marco = tk.Frame(self)
        marco.grid(row=5, column=0, columnspan=2, pady=12)
        tk.Button(marco, text="Registrar", bg="green", fg="white",
                  command=self.registrar).pack(side="left", padx=8)
        tk.Button(marco, text="Cancelar", bg="orange", fg="white",
                  command=self.destroy).pack(side="left", padx=8)

    def registrar(self):
        try:
            fecha = leer_fecha(self._campo_fecha.get())
            huesped = Huesped(
                self._campos[self._etiquetas[1]].get().strip(),
                self._campos[self._etiquetas[2]].get().strip(),
                self._campos[self._etiquetas[3]].get().strip(),
            )
            self._habitacion.ocupar(huesped, fecha)
        except ValueError as error:
            messagebox.showerror("Error", str(error), parent=self)
            return
        messagebox.showinfo("Aviso", "El huésped se registró correctamente", parent=self)
        self._al_registrar()
        self.destroy()


class VentanaHabitaciones(tk.Toplevel):
    """Lista las diez habitaciones y permite seleccionar la que se ocupará."""

    def __init__(self, maestro, hotel):
        super().__init__(maestro)
        self._hotel = hotel
        self.title("Consultar habitaciones")
        self.geometry("460x420")
        self.resizable(False, False)

        tk.Label(self, text="Habitaciones del hotel",
                 font=("Arial", 11, "bold")).pack(pady=8)

        marco = tk.Frame(self)
        marco.pack(fill="both", expand=True, padx=10)

        columnas = ("numero", "precio", "estado")
        self._tabla = ttk.Treeview(marco, columns=columnas, show="headings",
                                   height=10, selectmode="browse")
        self._tabla.heading("numero", text="Habitación")
        self._tabla.heading("precio", text="Precio por día")
        self._tabla.heading("estado", text="Estado")
        self._tabla.column("numero", width=100, anchor="center")
        self._tabla.column("precio", width=150, anchor="e")
        self._tabla.column("estado", width=150, anchor="center")
        self._tabla.pack(fill="both", expand=True)

        tk.Label(self, text="Seleccione una habitación y pulse «Ocupar».").pack(pady=4)

        marco_botones = tk.Frame(self)
        marco_botones.pack(pady=8)
        tk.Button(marco_botones, text="Ocupar", bg="green", fg="white",
                  command=self.ocupar).pack(side="left", padx=8)
        tk.Button(marco_botones, text="Cerrar",
                  command=self.destroy).pack(side="left", padx=8)

        self.actualizar()

    def actualizar(self):
        for fila in self._tabla.get_children():
            self._tabla.delete(fila)
        for habitacion in self._hotel.listar():
            estado = "Disponible" if habitacion.esta_disponible() else "No disponible"
            self._tabla.insert("", "end", iid=str(habitacion.numero),
                               values=(habitacion.numero,
                                       formatear_pesos(habitacion.precio_dia), estado))

    def ocupar(self):
        seleccion = self._tabla.selection()
        if not seleccion:
            messagebox.showwarning("Aviso", "Debe seleccionar una habitación", parent=self)
            return
        habitacion = self._hotel.buscar(int(seleccion[0]))
        if not habitacion.esta_disponible():
            messagebox.showerror("Error",
                                 f"La habitación {habitacion.numero} no está disponible",
                                 parent=self)
            return
        VentanaRegistro(self, self._hotel, habitacion, self.actualizar)


class VentanaSalida(tk.Toplevel):
    """Identifica la habitación, valida la fecha de salida y registra la salida."""

    def __init__(self, maestro, habitacion):
        super().__init__(maestro)
        self._habitacion = habitacion
        self._fecha_salida = None

        self.title(f"Salida - Habitación {habitacion.numero}")
        self.resizable(False, False)
        self.grab_set()

        tk.Label(self, text=f"Habitación a entregar: {habitacion.numero}",
                 font=("Arial", 11, "bold")).grid(row=0, column=0, columnspan=2, pady=8)

        datos = (
            ("Huésped", habitacion.huesped.nombre_completo()),
            ("Documento", habitacion.huesped.documento),
            ("Fecha de ingreso", habitacion.fecha_ingreso.strftime(FORMATO_FECHA)),
            ("Precio por día", formatear_pesos(habitacion.precio_dia)),
        )
        for fila, (etiqueta, valor) in enumerate(datos, start=1):
            tk.Label(self, text=etiqueta + ":").grid(row=fila, column=0, padx=8, pady=3, sticky="e")
            tk.Label(self, text=valor).grid(row=fila, column=1, padx=8, pady=3, sticky="w")

        tk.Label(self, text=f"Fecha de salida ({TEXTO_FORMATO}):").grid(
            row=5, column=0, padx=8, pady=8, sticky="e")
        self._entrada_fecha = tk.Entry(self, width=16)
        self._entrada_fecha.grid(row=5, column=1, padx=8, pady=8, sticky="w")
        self._entrada_fecha.bind("<KeyRelease>", lambda evento: self._invalidar_fecha())

        tk.Button(self, text="Validar fecha", command=self.validar_fecha).grid(
            row=6, column=0, columnspan=2, pady=4)

        self._boton_calcular = tk.Button(self, text="Calcular total", state="disabled",
                                         command=self.calcular)
        self._boton_calcular.grid(row=7, column=0, columnspan=2, pady=4)

        self._resultado = tk.Label(self, text="", font=("Arial", 10, "bold"),
                                   fg="darkgreen", justify="left")
        self._resultado.grid(row=8, column=0, columnspan=2, pady=6)

        self._boton_registrar = tk.Button(self, text="Registrar salida", bg="green",
                                          fg="white", state="disabled",
                                          command=self.registrar_salida)
        self._boton_registrar.grid(row=9, column=0, pady=12)
        tk.Button(self, text="Cancelar", bg="orange", fg="white",
                  command=self.destroy).grid(row=9, column=1, pady=12)

    def _invalidar_fecha(self):
        self._fecha_salida = None
        self._boton_calcular.config(state="disabled")
        self._boton_registrar.config(state="disabled")
        self._resultado.config(text="")

    def validar_fecha(self):
        try:
            fecha = leer_fecha(self._entrada_fecha.get())
            self._habitacion.calcular_dias(fecha)
        except ValueError as error:
            self._invalidar_fecha()
            messagebox.showerror("Error", str(error), parent=self)
            return
        self._fecha_salida = fecha
        self._boton_calcular.config(state="normal")

    def calcular(self):
        dias = self._habitacion.calcular_dias(self._fecha_salida)
        total = self._habitacion.calcular_total(self._fecha_salida)
        self._resultado.config(text=f"Días de alojamiento: {dias}\n"
                                    f"Total a pagar: {formatear_pesos(total)}")
        self._boton_registrar.config(state="normal")

    def registrar_salida(self):
        self._habitacion.liberar()
        messagebox.showinfo("Aviso", "La salida se registró correctamente. "
                                     "La habitación quedó disponible", parent=self)
        self.destroy()


class VentanaNumeroSalida(tk.Toplevel):
    """Solicita el número de habitación a entregar."""

    def __init__(self, maestro, hotel):
        super().__init__(maestro)
        self._hotel = hotel
        self.title("Salida de huéspedes")
        self.resizable(False, False)
        self.grab_set()

        tk.Label(self, text="Número de habitación a entregar",
                 font=("Arial", 11, "bold")).grid(row=0, column=0, columnspan=2, padx=20, pady=10)
        self._entrada = tk.Entry(self, width=12, justify="center")
        self._entrada.grid(row=1, column=0, columnspan=2, pady=6)
        self._entrada.focus()

        tk.Button(self, text="Continuar", bg="green", fg="white",
                  command=self.continuar).grid(row=2, column=0, pady=12)
        tk.Button(self, text="Cancelar", bg="orange", fg="white",
                  command=self.destroy).grid(row=2, column=1, pady=12)

    def continuar(self):
        try:
            habitacion = self._hotel.buscar_ocupada(self._entrada.get().strip())
        except ValueError as error:
            messagebox.showerror("Error", str(error), parent=self)
            return
        VentanaSalida(self.master, habitacion)
        self.destroy()


class VentanaPrincipal(tk.Tk):

    def __init__(self):
        super().__init__()
        self._hotel = Hotel()

        self.title("Hotel")
        self.geometry("520x200")
        self.resizable(False, False)

        tk.Label(self, text="Ejercicio 8.5 - Gestión de Hotel",
                 font=("Arial", 14, "bold")).pack(pady=25)
        tk.Label(self, text="Use el menú «Hotel» para consultar habitaciones\n"
                            "o registrar la salida de huéspedes.",
                 justify="center").pack()

        self._crear_menu()

    def _crear_menu(self):
        barra = tk.Menu(self)
        menu_hotel = tk.Menu(barra, tearoff=0)
        menu_hotel.add_command(label="Consultar habitaciones",
                               command=self.consultar_habitaciones)
        menu_hotel.add_command(label="Salida de huéspedes", command=self.salida_huespedes)
        menu_hotel.add_separator()
        menu_hotel.add_command(label="Salir", command=self.destroy)
        barra.add_cascade(label="Hotel", menu=menu_hotel)
        self.config(menu=barra)

    def consultar_habitaciones(self):
        VentanaHabitaciones(self, self._hotel)

    def salida_huespedes(self):
        VentanaNumeroSalida(self, self._hotel)


def main():
    app = VentanaPrincipal()
    app.mainloop()


if __name__ == "__main__":
    main()
