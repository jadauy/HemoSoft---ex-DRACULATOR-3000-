"""Formulario de evaluación de elegibilidad del donante (H2 · T2.4)."""

from tkinter import BooleanVar, Checkbutton, Frame, Label, LabelFrame, messagebox

from donantes.EvaluacionElegibilidad import APTO, DIFERIDO
from donantes.servicio_evaluaciones import (DatosEvaluacionInvalidosError, DonanteNoRegistradoError,
                                            ServicioEvaluaciones)
from interfaz.comun import (FUENTE, FUENTE_CHICA, FUENTE_TITULO, NARANJO, ROJO, TITULO_VENTANA, VERDE, boton,
                            crear_entrada, limpiar_campo, titulo)

CAMPOS = [
    ("rut", "RUT del donante"),
    ("peso", "Peso (kg)"),
    ("hemoglobina", "Hemoglobina (g/dL)"),
    ("presion_sistolica", "Presión sistólica (mmHg)"),
    ("presion_diastolica", "Presión diastólica (mmHg)"),
]
COLORES = {APTO: VERDE, DIFERIDO: NARANJO}


class FormularioEvaluacion(Frame):
    def __init__(self, padre, servicio=None):
        super().__init__(padre)
        self.servicio = servicio or ServicioEvaluaciones()
        self.entradas, self.errores = {}, {}

        titulo(self, "Evaluación de elegibilidad")
        marco = LabelFrame(self, text="Datos medidos", font=FUENTE, padx=5, pady=5)
        marco.pack(padx=10)
        for fila, (campo, etiqueta) in enumerate(CAMPOS):
            self.entradas[campo] = crear_entrada(marco, fila, etiqueta)
            self.errores[campo] = Label(marco, text="", fg=ROJO, font=FUENTE_CHICA, wraplength=170, justify="left")
            self.errores[campo].grid(row=fila, column=2, sticky="w")

        cuestionario = LabelFrame(self, text="Cuestionario", font=FUENTE, padx=5, pady=5)
        cuestionario.pack(padx=10, pady=8, fill="x")
        self.causa_temporal = BooleanVar()
        self.causa_permanente = BooleanVar()
        Checkbutton(cuestionario, variable=self.causa_temporal, font=FUENTE,
                    text="Declara una causa temporal (ej: tatuaje o cirugía reciente, resfrío)").pack(anchor="w")
        Checkbutton(cuestionario, variable=self.causa_permanente, font=FUENTE,
                    text="Declara una causa permanente (ej: enfermedad crónica que impide donar)").pack(anchor="w")

        boton(self, "Evaluar", self.evaluar).pack(pady=8)

        self.resultado = Label(self, text="", font=(FUENTE_TITULO[0], 16, "bold"))
        self.resultado.pack()
        self.detalle = Label(self, text="", font=FUENTE, wraplength=520, justify="left")
        self.detalle.pack(padx=10)

    def leer_datos(self):
        datos = {campo: entrada.get() for campo, entrada in self.entradas.items()}
        datos["causa_temporal"] = self.causa_temporal.get()
        datos["causa_permanente"] = self.causa_permanente.get()
        return datos

    def limpiar(self):
        for entrada in self.entradas.values():
            limpiar_campo(entrada)
        self.causa_temporal.set(False)
        self.causa_permanente.set(False)

    def mostrar_errores(self, errores):
        for campo, etiqueta in self.errores.items():
            etiqueta.config(text=errores.get(campo, ""))

    def evaluar(self):
        self.mostrar_errores({})
        self.resultado.config(text="")
        try:
            evaluacion = self.servicio.evaluar(self.leer_datos())
        except DatosEvaluacionInvalidosError as e:
            self.mostrar_errores(e.errores)
            self.detalle.config(text="Revise los campos marcados en rojo.", fg=ROJO)
            return None
        except DonanteNoRegistradoError as e:
            self.mostrar_errores({"rut": "Donante no registrado."})
            self.detalle.config(text=f"{e} Regístrelo primero en la pestaña Donantes.", fg=ROJO)
            messagebox.showwarning(TITULO_VENTANA, str(e))
            return None

        self.resultado.config(text=evaluacion.resultado, fg=COLORES.get(evaluacion.resultado, ROJO))
        lineas = [f"Evaluación N° {evaluacion.idEvaluacion} del {evaluacion.fechaEvaluacion} "
                  f"para el RUT {evaluacion.rut_donante}."]
        if evaluacion.motivos:
            lineas += ["Motivos:"] + [f"• {m}" for m in evaluacion.motivos.split(" | ")]
        if evaluacion.resultado == DIFERIDO:
            lineas.append(f"Puede volver a evaluarse desde el {evaluacion.fechaHabilitacion}.")
        elif evaluacion.resultado == APTO:
            lineas.append("Puede donar hoy.")
        self.detalle.config(text="\n".join(lineas), fg="black")
        self.limpiar()
        return evaluacion
