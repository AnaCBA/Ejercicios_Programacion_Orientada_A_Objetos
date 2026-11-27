import os
import re
import tkinter as tk
from tkinter import ttk, messagebox

NOMBRE_ARCHIVO = "contactos.txt"
SEPARADOR = "|"
PATRON_CORREO = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
PATRON_TELEFONO = re.compile(r"^\d{7,10}$")


class Contacto:

    def __init__(self, id_contacto, nombre, telefono, correo):
        nombre, telefono, correo = nombre.strip(), telefono.strip(), correo.strip()
        if not nombre or not telefono or not correo:
            raise ValueError("El nombre, el teléfono y el correo son obligatorios")
        if SEPARADOR in nombre or SEPARADOR in correo:
            raise ValueError(f"No se permite el carácter «{SEPARADOR}» en los datos")
        if not PATRON_TELEFONO.match(telefono):
            raise ValueError("El teléfono debe tener entre 7 y 10 dígitos")
        if not PATRON_CORREO.match(correo):
            raise ValueError("El correo electrónico no es válido")
        self._id = id_contacto
        self._nombre = nombre
        self._telefono = telefono
        self._correo = correo

    @property
    def id(self):
        return self._id

    @property
    def nombre(self):
        return self._nombre

    @property
    def telefono(self):
        return self._telefono

    @property
    def correo(self):
        return self._correo

    def a_linea(self):
        return SEPARADOR.join((str(self._id), self._nombre, self._telefono, self._correo))

    @staticmethod
    def desde_linea(linea):
        partes = linea.rstrip("\n").split(SEPARADOR)
        if len(partes) != 4:
            raise ValueError("Línea con formato inválido")
        return Contacto(int(partes[0]), partes[1], partes[2], partes[3])


class ArchivoContactos:
    """Acceso al archivo de texto: Create, Read, Update y Delete."""

    def __init__(self, ruta):
        self._ruta = ruta

    @property
    def ruta(self):
        return self._ruta

    def leer_todos(self):
        if not os.path.exists(self._ruta):
            return []
        contactos = []
        with open(self._ruta, "r", encoding="utf-8") as archivo:
            for linea in archivo:
                if linea.strip():
                    contactos.append(Contacto.desde_linea(linea))
        return contactos

    def _guardar_todos(self, contactos):
        with open(self._ruta, "w", encoding="utf-8") as archivo:
            for contacto in contactos:
                archivo.write(contacto.a_linea() + "\n")

    def _siguiente_id(self, contactos):
        return max((c.id for c in contactos), default=0) + 1

    def _validar_nombre_unico(self, contactos, nombre, id_excluido=None):
        for contacto in contactos:
            if contacto.id != id_excluido and contacto.nombre.lower() == nombre.strip().lower():
                raise ValueError("Ya existe un contacto con ese nombre")

    # Create
    def crear(self, nombre, telefono, correo):
        contactos = self.leer_todos()
        nuevo = Contacto(self._siguiente_id(contactos), nombre, telefono, correo)
        self._validar_nombre_unico(contactos, nuevo.nombre)
        contactos.append(nuevo)
        self._guardar_todos(contactos)
        return nuevo

    # Read
    def buscar(self, texto=""):
        texto = texto.strip().lower()
        return [c for c in self.leer_todos()
                if texto in c.nombre.lower() or texto in c.telefono or texto in c.correo.lower()]

    # Update
    def actualizar(self, id_contacto, nombre, telefono, correo):
        contactos = self.leer_todos()
        modificado = Contacto(id_contacto, nombre, telefono, correo)
        self._validar_nombre_unico(contactos, modificado.nombre, id_contacto)
        for indice, contacto in enumerate(contactos):
            if contacto.id == id_contacto:
                contactos[indice] = modificado
                self._guardar_todos(contactos)
                return modificado
        raise ValueError("El contacto que intenta actualizar no existe")

    # Delete
    def eliminar(self, id_contacto):
        contactos = self.leer_todos()
        restantes = [c for c in contactos if c.id != id_contacto]
        if len(restantes) == len(contactos):
            raise ValueError("El contacto que intenta eliminar no existe")
        self._guardar_todos(restantes)


class VentanaContactos(tk.Tk):

    def __init__(self, archivo):
        super().__init__()
        self._archivo = archivo
        self._id_seleccionado = None

        self.title("Actividad 6 - CRUD de contactos")
        self.geometry("640x560")
        self.resizable(False, False)

        tk.Label(self, text="Agenda de contactos",
                 font=("Arial", 14, "bold")).pack(pady=10)

        self._crear_formulario()
        self._crear_botones()
        self._crear_tabla()
        self.leer()

    def _crear_formulario(self):
        marco = tk.Frame(self)
        marco.pack(pady=5)
        self._campos = {}
        for fila, etiqueta in enumerate(("Nombre", "Teléfono", "Correo")):
            tk.Label(marco, text=etiqueta).grid(row=fila, column=0, padx=8, pady=5, sticky="e")
            entrada = tk.Entry(marco, width=40)
            entrada.grid(row=fila, column=1, padx=8, pady=5, sticky="w")
            self._campos[etiqueta] = entrada

    def _crear_botones(self):
        marco = tk.Frame(self)
        marco.pack(pady=8)
        botones = (("Create", "green", self.crear), ("Read", "royalblue", self.leer),
                   ("Update", "orange", self.actualizar), ("Delete", "firebrick", self.eliminar),
                   ("Limpiar", "gray", self.limpiar))
        for columna, (texto, color, comando) in enumerate(botones):
            tk.Button(marco, text=texto, width=10, bg=color, fg="white",
                      command=comando).grid(row=0, column=columna, padx=5)

        marco_busqueda = tk.Frame(self)
        marco_busqueda.pack(pady=4)
        tk.Label(marco_busqueda, text="Buscar al leer:").pack(side="left", padx=5)
        self._busqueda = tk.Entry(marco_busqueda, width=30)
        self._busqueda.pack(side="left")

    def _crear_tabla(self):
        marco = tk.Frame(self)
        marco.pack(fill="both", expand=True, padx=10, pady=8)
        columnas = ("id", "nombre", "telefono", "correo")
        self._tabla = ttk.Treeview(marco, columns=columnas, show="headings",
                                   height=10, selectmode="browse")
        for columna, texto, ancho in (("id", "ID", 40), ("nombre", "Nombre", 180),
                                      ("telefono", "Teléfono", 110), ("correo", "Correo", 250)):
            self._tabla.heading(columna, text=texto)
            self._tabla.column(columna, width=ancho)
        barra = ttk.Scrollbar(marco, orient="vertical", command=self._tabla.yview)
        self._tabla.configure(yscrollcommand=barra.set)
        self._tabla.pack(side="left", fill="both", expand=True)
        barra.pack(side="right", fill="y")
        self._tabla.bind("<<TreeviewSelect>>", self._al_seleccionar)

    def _datos_formulario(self):
        return (self._campos["Nombre"].get(), self._campos["Teléfono"].get(),
                self._campos["Correo"].get())

    def _al_seleccionar(self, evento):
        seleccion = self._tabla.selection()
        if not seleccion:
            return
        id_contacto, nombre, telefono, correo = self._tabla.item(seleccion[0], "values")
        self._id_seleccionado = int(id_contacto)
        for etiqueta, valor in (("Nombre", nombre), ("Teléfono", telefono), ("Correo", correo)):
            self._campos[etiqueta].delete(0, tk.END)
            self._campos[etiqueta].insert(0, valor)

    def crear(self):
        try:
            self._archivo.crear(*self._datos_formulario())
        except (ValueError, OSError) as error:
            messagebox.showerror("Error", str(error))
            return
        messagebox.showinfo("Aviso", "El contacto se creó correctamente")
        self.limpiar()
        self.leer()

    def leer(self):
        try:
            contactos = self._archivo.buscar(self._busqueda.get())
        except (ValueError, OSError) as error:
            messagebox.showerror("Error", f"No se pudo leer el archivo: {error}")
            return
        for fila in self._tabla.get_children():
            self._tabla.delete(fila)
        for contacto in contactos:
            self._tabla.insert("", "end", values=(contacto.id, contacto.nombre,
                                                  contacto.telefono, contacto.correo))

    def actualizar(self):
        if self._id_seleccionado is None:
            messagebox.showwarning("Aviso", "Seleccione un contacto de la tabla para actualizarlo")
            return
        try:
            self._archivo.actualizar(self._id_seleccionado, *self._datos_formulario())
        except (ValueError, OSError) as error:
            messagebox.showerror("Error", str(error))
            return
        messagebox.showinfo("Aviso", "El contacto se actualizó correctamente")
        self.limpiar()
        self.leer()

    def eliminar(self):
        if self._id_seleccionado is None:
            messagebox.showwarning("Aviso", "Seleccione un contacto de la tabla para eliminarlo")
            return
        if not messagebox.askyesno("Confirmar", "¿Desea eliminar el contacto seleccionado?"):
            return
        try:
            self._archivo.eliminar(self._id_seleccionado)
        except (ValueError, OSError) as error:
            messagebox.showerror("Error", str(error))
            return
        messagebox.showinfo("Aviso", "El contacto se eliminó correctamente")
        self.limpiar()
        self.leer()

    def limpiar(self):
        for entrada in self._campos.values():
            entrada.delete(0, tk.END)
        self._id_seleccionado = None
        self._tabla.selection_remove(self._tabla.selection())


def main():
    carpeta = os.path.dirname(os.path.abspath(__file__))
    archivo = ArchivoContactos(os.path.join(carpeta, NOMBRE_ARCHIVO))
    VentanaContactos(archivo).mainloop()


if __name__ == "__main__":
    main()
