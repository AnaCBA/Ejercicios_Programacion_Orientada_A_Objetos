import os
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

CARGOS = ("Directivo", "Estratégico", "Operativo")
GENEROS = ("Masculino", "Femenino")
DIAS_MINIMOS = 1
DIAS_MAXIMOS = 31
NOMBRE_ARCHIVO = "Nómina.txt"
CAMPOS_EN_CERO = ("Otros ingresos", "Pagos por salud", "Aporte pensiones")


def formatear_pesos(valor):
    return f"${valor:,.2f}"


class Empleado:

    def __init__(self, nombre, apellidos, cargo, genero, salario_dia,
                 dias_trabajados, otros_ingresos, pagos_salud, aporte_pensiones):
        if not nombre or not apellidos:
            raise ValueError("El nombre y los apellidos son obligatorios")
        if cargo not in CARGOS:
            raise ValueError("Debe seleccionar un cargo válido")
        if genero not in GENEROS:
            raise ValueError("Debe seleccionar un género válido")
        if not isinstance(dias_trabajados, int) or not DIAS_MINIMOS <= dias_trabajados <= DIAS_MAXIMOS:
            raise ValueError(f"Los días trabajados deben estar entre {DIAS_MINIMOS} y {DIAS_MAXIMOS}")
        if salario_dia <= 0:
            raise ValueError("El salario por día debe ser mayor que cero")
        if otros_ingresos < 0 or pagos_salud < 0 or aporte_pensiones < 0:
            raise ValueError("Los valores de dinero no pueden ser negativos")

        self._nombre = nombre
        self._apellidos = apellidos
        self._cargo = cargo
        self._genero = genero
        self._salario_dia = salario_dia
        self._dias_trabajados = dias_trabajados
        self._otros_ingresos = otros_ingresos
        self._pagos_salud = pagos_salud
        self._aporte_pensiones = aporte_pensiones

    @property
    def nombre(self):
        return self._nombre

    @property
    def apellidos(self):
        return self._apellidos

    def calcular_salario_mensual(self):
        ingresos = (self._dias_trabajados * self._salario_dia) + self._otros_ingresos
        return ingresos - self._pagos_salud - self._aporte_pensiones

    def a_texto(self):
        return (
            f"Nombres:           {self._nombre}\n"
            f"Apellidos:         {self._apellidos}\n"
            f"Cargo:             {self._cargo}\n"
            f"Género:            {self._genero}\n"
            f"Salario por día:   {formatear_pesos(self._salario_dia)}\n"
            f"Días trabajados:   {self._dias_trabajados}\n"
            f"Otros ingresos:    {formatear_pesos(self._otros_ingresos)}\n"
            f"Pagos por salud:   {formatear_pesos(self._pagos_salud)}\n"
            f"Aporte pensiones:  {formatear_pesos(self._aporte_pensiones)}\n"
            f"Sueldo mensual:    {formatear_pesos(self.calcular_salario_mensual())}\n"
        )


class Nomina:

    def __init__(self):
        self._empleados = []

    def agregar_empleado(self, empleado):
        self._empleados.append(empleado)

    def listar(self):
        return list(self._empleados)

    def esta_vacia(self):
        return len(self._empleados) == 0

    def calcular_total(self):
        return sum(empleado.calcular_salario_mensual() for empleado in self._empleados)

    def guardar_archivo(self, carpeta):
        ruta = os.path.join(carpeta, NOMBRE_ARCHIVO)
        with open(ruta, "w", encoding="utf-8") as archivo:
            archivo.write("NÓMINA DE LA EMPRESA\n")
            archivo.write("=" * 60 + "\n\n")
            for empleado in self._empleados:
                archivo.write(empleado.a_texto())
                archivo.write("-" * 60 + "\n")
            archivo.write(f"\nTOTAL NÓMINA DE LA EMPRESA: {formatear_pesos(self.calcular_total())}\n")
        return ruta


class VentanaAgregar(tk.Toplevel):

    def __init__(self, maestro, nomina):
        super().__init__(maestro)
        self._nomina = nomina

        self.title("Agregar empleado")
        self.geometry("420x430")
        self.resizable(False, False)

        tk.Label(self, text="Ingrese los datos del empleado",
                 font=("Arial", 11, "bold")).grid(row=0, column=0, columnspan=2, pady=8)

        self._genero = tk.StringVar(value=GENEROS[0])
        self._campos = {}

        self._crear_campo(1, "Nombres", tk.Entry(self, width=28))
        self._crear_campo(2, "Apellidos", tk.Entry(self, width=28))

        combo_cargo = ttk.Combobox(self, width=26, values=CARGOS, state="readonly")
        combo_cargo.current(0)
        self._crear_campo(3, "Cargo", combo_cargo)

        marco_generos = tk.Frame(self)
        for genero in GENEROS:
            tk.Radiobutton(marco_generos, text=genero, value=genero,
                           variable=self._genero).pack(side="left")
        self._crear_campo(4, "Género", marco_generos)

        self._crear_campo(5, "Salario por día", tk.Entry(self, width=28))

        spin_dias = tk.Spinbox(self, width=26, from_=DIAS_MINIMOS, to=DIAS_MAXIMOS)
        self._crear_campo(6, "Días trabajados", spin_dias)

        self._crear_campo(7, "Otros ingresos", tk.Entry(self, width=28))
        self._crear_campo(8, "Pagos por salud", tk.Entry(self, width=28))
        self._crear_campo(9, "Aporte pensiones", tk.Entry(self, width=28))

        tk.Button(self, text="Agregar", bg="green", fg="white",
                  command=self.agregar).grid(row=10, column=0, pady=15)
        tk.Button(self, text="Limpiar", bg="orange", fg="white",
                  command=self.limpiar).grid(row=10, column=1, pady=15)

        self.limpiar()

    def _crear_campo(self, fila, etiqueta, widget):
        tk.Label(self, text=etiqueta).grid(row=fila, column=0, padx=8, pady=5, sticky="e")
        widget.grid(row=fila, column=1, padx=8, pady=5, sticky="w")
        self._campos[etiqueta] = widget

    def _leer(self, etiqueta):
        return self._campos[etiqueta].get().strip()

    def agregar(self):
        try:
            salario_dia = float(self._leer("Salario por día"))
            dias_trabajados = int(self._leer("Días trabajados"))
            otros_ingresos = float(self._leer("Otros ingresos"))
            pagos_salud = float(self._leer("Pagos por salud"))
            aporte_pensiones = float(self._leer("Aporte pensiones"))
        except ValueError:
            messagebox.showerror("Error", "Los campos de dinero y de días deben ser numéricos")
            return

        try:
            empleado = Empleado(
                nombre=self._leer("Nombres"),
                apellidos=self._leer("Apellidos"),
                cargo=self._leer("Cargo"),
                genero=self._genero.get(),
                salario_dia=salario_dia,
                dias_trabajados=dias_trabajados,
                otros_ingresos=otros_ingresos,
                pagos_salud=pagos_salud,
                aporte_pensiones=aporte_pensiones
            )
        except ValueError as error:
            messagebox.showerror("Error", str(error))
            return

        self._nomina.agregar_empleado(empleado)
        messagebox.showinfo("Aviso", "El empleado se agregó correctamente")
        self.limpiar()

    def limpiar(self):
        for etiqueta, widget in self._campos.items():
            if isinstance(widget, tk.Entry):
                widget.delete(0, tk.END)
            elif isinstance(widget, tk.Spinbox):
                widget.delete(0, tk.END)
                widget.insert(0, DIAS_MINIMOS)
        for etiqueta in CAMPOS_EN_CERO:
            self._campos[etiqueta].insert(0, "0")
        self._campos["Cargo"].current(0)
        self._genero.set(GENEROS[0])


class VentanaNomina(tk.Toplevel):

    def __init__(self, maestro, nomina):
        super().__init__(maestro)
        self.title("Calcular nómina")
        self.geometry("560x360")
        self.resizable(False, False)

        tk.Label(self, text="Nómina de los empleados",
                 font=("Arial", 11, "bold")).pack(pady=8)

        marco = tk.Frame(self)
        marco.pack(fill="both", expand=True, padx=10)

        columnas = ("nombres", "apellidos", "sueldo")
        tabla = ttk.Treeview(marco, columns=columnas, show="headings", height=8)
        tabla.heading("nombres", text="Nombres")
        tabla.heading("apellidos", text="Apellidos")
        tabla.heading("sueldo", text="Sueldo mensual")
        tabla.column("nombres", width=190)
        tabla.column("apellidos", width=190)
        tabla.column("sueldo", width=140, anchor="e")

        barra = ttk.Scrollbar(marco, orient="vertical", command=tabla.yview)
        tabla.configure(yscrollcommand=barra.set)
        tabla.pack(side="left", fill="both", expand=True)
        barra.pack(side="right", fill="y")

        for empleado in nomina.listar():
            tabla.insert("", "end", values=(empleado.nombre, empleado.apellidos,
                                            formatear_pesos(empleado.calcular_salario_mensual())))

        tk.Label(self, text=f"Total de la nómina de la empresa: {formatear_pesos(nomina.calcular_total())}",
                 font=("Arial", 11, "bold"), fg="darkgreen").pack(pady=8)

        tk.Button(self, text="Cerrar", command=self.destroy).pack(pady=5)


class VentanaPrincipal(tk.Tk):

    def __init__(self):
        super().__init__()
        self._nomina = Nomina()

        self.title("Nómina de la empresa")
        self.geometry("520x200")
        self.resizable(False, False)

        tk.Label(self, text="Ejercicio 8.4 - Nómina",
                 font=("Arial", 14, "bold")).pack(pady=25)
        tk.Label(self, text="Use el menú «Nómina» para agregar empleados,\n"
                            "calcular la nómina o guardar el archivo.",
                 justify="center").pack()

        self._crear_menu()

    def _crear_menu(self):
        barra = tk.Menu(self)
        menu_nomina = tk.Menu(barra, tearoff=0)
        menu_nomina.add_command(label="Agregar empleado", command=self.agregar_empleado)
        menu_nomina.add_command(label="Calcular nómina", command=self.calcular_nomina)
        menu_nomina.add_separator()
        menu_nomina.add_command(label="Guardar archivo", command=self.guardar_archivo)
        menu_nomina.add_separator()
        menu_nomina.add_command(label="Salir", command=self.destroy)

        barra.add_cascade(label="Nómina", menu=menu_nomina)
        self.config(menu=barra)

    def agregar_empleado(self):
        VentanaAgregar(self, self._nomina)

    def calcular_nomina(self):
        if self._nomina.esta_vacia():
            messagebox.showwarning("Aviso", "Todavía no ha ingresado ningún empleado")
            return
        VentanaNomina(self, self._nomina)

    def guardar_archivo(self):
        if self._nomina.esta_vacia():
            messagebox.showwarning("Aviso", "Todavía no ha ingresado ningún empleado")
            return
        carpeta = filedialog.askdirectory(title="Seleccione la carpeta donde guardar la nómina")
        if not carpeta:
            return
        try:
            ruta = self._nomina.guardar_archivo(carpeta)
        except OSError as error:
            messagebox.showerror("Error", str(error))
            return
        messagebox.showinfo("Aviso", f"El archivo se guardó en:\n{ruta}")


def main():
    app = VentanaPrincipal()
    app.mainloop()


if __name__ == "__main__":
    main()
