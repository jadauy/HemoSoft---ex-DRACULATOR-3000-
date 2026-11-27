"""Vista de stock por grupo sanguíneo y alertas de vencimiento."""

from tkinter import Frame, Label, LabelFrame, messagebox, ttk

from donantes.inventario import Inventario
from donantes.sedes import SEDES
from donantes.validaciones import TIPOS_SANGRE
from donantes.vencimientos import Vencimientos
from interfaz.comun import FUENTE, ROJO, boton, titulo

UMBRAL_STOCK_BAJO = 4


class VistaInventario(Frame):
    def __init__(self, padre, inventario=None, vencimientos=None):
        super().__init__(padre)
        self.inventario = inventario or Inventario()
        self.vencimientos = vencimientos or Vencimientos(self.inventario)

        titulo(self, "Inventario de unidades")
        controles = Frame(self)
        controles.pack(fill="x", padx=10, pady=(0, 6))
        Label(controles, text="Sede:", font=FUENTE).pack(side="left", padx=(0, 6))
        opciones = ["Todas"] + [sede.nombre for sede in SEDES]
        self.selector_sede = ttk.Combobox(
            controles, values=opciones, state="readonly", width=22, font=FUENTE
        )
        self.selector_sede.set("Todas")
        self.selector_sede.pack(side="left")
        self.selector_sede.bind("<<ComboboxSelected>>", lambda _: self.actualizar())
        boton(controles, "Actualizar", self.actualizar).pack(side="right")

        marco_stock = LabelFrame(self, text="Stock vigente por grupo", font=FUENTE, padx=5, pady=4)
        marco_stock.pack(fill="x", padx=10, pady=4)
        self.tabla_stock = ttk.Treeview(
            marco_stock, columns=("grupo", "cantidad"), show="headings", height=8
        )
        self.tabla_stock.heading("grupo", text="Grupo sanguíneo")
        self.tabla_stock.heading("cantidad", text="Unidades vigentes")
        self.tabla_stock.column("grupo", width=180, anchor="center")
        self.tabla_stock.column("cantidad", width=180, anchor="center")
        self.tabla_stock.tag_configure("stock_bajo", foreground=ROJO)
        self.tabla_stock.pack(fill="x")

        self.tabla_por_vencer = self._crear_tabla_vencimientos(
            "Unidades por vencer (menos de 7 días)", "tabla_por_vencer"
        )
        self.tabla_vencidas = self._crear_tabla_vencimientos(
            "Unidades vencidas (no suman al stock)", "tabla_vencidas"
        )
        self.actualizar()

    def _crear_tabla_vencimientos(self, titulo_seccion, atributo):
        marco = LabelFrame(self, text=titulo_seccion, font=FUENTE, padx=5, pady=4)
        marco.pack(fill="both", expand=True, padx=10, pady=4)
        tabla = ttk.Treeview(
            marco, columns=("codigo", "grupo", "fecha"), show="headings", height=4
        )
        for columna, encabezado, ancho in (
            ("codigo", "Código", 220),
            ("grupo", "Grupo sanguíneo", 150),
            ("fecha", "Fecha de vencimiento", 180),
        ):
            tabla.heading(columna, text=encabezado)
            tabla.column(columna, width=ancho, anchor="center")
        barra = ttk.Scrollbar(marco, orient="vertical", command=tabla.yview)
        tabla.configure(yscrollcommand=barra.set)
        tabla.pack(side="left", fill="both", expand=True)
        barra.pack(side="right", fill="y")
        setattr(self, atributo, tabla)
        return tabla

    def _sede_seleccionada(self):
        sede = self.selector_sede.get()
        return None if sede == "Todas" else sede

    @staticmethod
    def _agregar_unidades(tabla, unidades):
        for unidad in unidades:
            tabla.insert(
                "", "end",
                values=(
                    unidad.unidad.codigo_barras,
                    unidad.tipo_sangre or "-",
                    unidad.unidad.fecha_vencimiento,
                ),
            )

    def actualizar(self):
        sede = self._sede_seleccionada()
        try:
            stock = self.inventario.stock_por_grupo(sede=sede)
            por_vencer = self.vencimientos.unidades_por_vencer(sede=sede)
            vencidas = self.vencimientos.unidades_vencidas(sede=sede)
        except (OSError, ValueError, KeyError) as error:
            messagebox.showerror(
                "Error al actualizar inventario",
                f"No se pudieron leer o procesar los datos guardados:\n{error}",
                parent=self.winfo_toplevel(),
            )
            return

        self.tabla_stock.delete(*self.tabla_stock.get_children())
        self.tabla_por_vencer.delete(*self.tabla_por_vencer.get_children())
        self.tabla_vencidas.delete(*self.tabla_vencidas.get_children())
        for grupo in TIPOS_SANGRE:
            cantidad = stock[grupo]
            etiquetas = ("stock_bajo",) if cantidad <= UMBRAL_STOCK_BAJO else ()
            self.tabla_stock.insert(
                "", "end", values=(grupo, cantidad), tags=etiquetas
            )
        self._agregar_unidades(self.tabla_por_vencer, por_vencer)
        self._agregar_unidades(self.tabla_vencidas, vencidas)
