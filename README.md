# HemoSoft (ex DRACULATOR 3000)

Sistema de registro de donantes de sangre — Ing. SW, grupo 7.

Reemplaza el registro en papel del profesional de recolección: registra donantes, evalúa su
elegibilidad antes de donar y entrega un código de barras único por cada unidad extraída para que sea
trazable. En el Sprint 01 los datos se guardan en archivos de texto dentro de `datos/` (no se usa base
de datos todavía).

## Cómo usarlo

Requiere Python 3.10 o superior, con tkinter (viene incluido en el instalador de python.org). No hay
que instalar librerías extra.

```bash
python main.py
```

La ventana tiene cuatro pestañas, que siguen el orden de la atención de un donante:

| Pestaña | Historia | Qué hace |
|---|---|---|
| Donantes | H1 | Registra un donante y lo busca por RUT |
| Evaluación | H2 | Registra la evaluación de elegibilidad y muestra APTO, DIFERIDO o NO APTO |
| Donación | H3 | Registra la extracción y genera la unidad con su código de barras |
| Buscar unidad | H3 | Muestra la traza completa de una unidad a partir de su código |

`python consola.py` abre el menú de consola del inicio del sprint (solo como herramienta de prueba).

### Pruebas

```bash
python -m unittest discover -s tests -v
```

Las pruebas de interfaz se saltan solas si el equipo no tiene pantalla.

## Historias del Sprint 01

**H1 · Registrar donante:** RUT con dígito verificador, nombre, fecha de nacimiento, sexo, peso, tipo de
sangre (8 grupos) y teléfono. Rechaza RUT duplicados, marca cada campo con error y permite buscar por RUT.

**H2 · Evaluación de elegibilidad** (reglas acordadas con el PO):

| Resultado | Cuándo |
|---|---|
| NO APTO | Causa permanente declarada o edad sobre 65 años |
| DIFERIDO | Menor de 18, peso bajo 50 kg, hemoglobina bajo 12,5 (F) / 13,5 (M) g/dL, presión fuera de 90–180 / 50–100 mmHg o causa temporal declarada. Indica desde qué fecha puede volver a evaluarse |
| APTO | Cumple todo lo anterior |

**H3 · Código de barras por unidad:** solo dona quien tiene una evaluación APTO del mismo día y cumplió el
plazo mínimo desde su última donación (3 meses hombres, 4 meses mujeres). Cada unidad recibe un código
`SSS AAMMDD NNNN V` (sede, fecha, correlativo y dígito verificador), se dibuja en Code 39 y vence a los
42 días. La unidad se puede buscar por su código para ver donante, sede, fechas y si está vigente.

## Estructura

| Archivo | Task | Qué hace |
|---|---|---|
| `donantes/rut.py` | T1.2 | Formato y dígito verificador del RUT |
| `donantes/validaciones.py` | T1.2 | Reglas de cada campo del donante |
| `donantes/repositorio.py` | T1.1 | Guarda donantes en `datos/donantes.txt` |
| `donantes/servicio.py` | T1.5 | Registro sin duplicados y búsqueda por RUT |
| `interfaz/form_donante.py` | T1.3, T1.4 | Pestaña Donantes y sus mensajes |
| `donantes/EvaluacionElegibilidad.py` | T2.1 | Modelo de la evaluación |
| `donantes/repositorio_evaluaciones.py` | T2.2 | Guarda evaluaciones en `datos/evaluaciones.txt` |
| `donantes/elegibilidad.py`, `servicio_evaluaciones.py` | T2.3 | Cálculo del resultado y registro |
| `interfaz/form_evaluacion.py` | T2.4 | Pestaña Evaluación |
| `donantes/donacion.py`, `sedes.py` | T3.1 | Modelos de donación, hemocomponente y sede; sedes iniciales |
| `donantes/repositorio_donaciones.py` | T3.2 | Guarda donaciones y unidades |
| `donantes/requisitos_donacion.py` | T3.3 | Verifica APTO del día y plazo mínimo |
| `donantes/codigo_barras.py`, `interfaz/dibujo_codigo.py` | T3.4 | Código único, vencimiento y dibujo Code 39 |
| `donantes/servicio_donaciones.py`, `interfaz/form_donacion.py` | T3.5, T3.6 | Pestaña Donación y sus mensajes |
| `interfaz/busqueda_unidad.py` | T3.7 | Pestaña Buscar unidad |
| `donantes/archivo_txt.py` | — | Lectura y escritura común de los `.txt` |
