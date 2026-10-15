# Proyecto 2 – Mejora de la SNR de una IMU con filtros FIR e IIR

**Universidad Militar Nueva Granada** · Ingeniería Mecatrónica
**Asignatura:** Procesamiento Digital de Señales – Teoría · **Periodo:** 2026-2 · **Segundo corte**
**Equipo 2:** Andrés Sánchez · Daniel Andrés Gutiérrez

## Qué se hizo

Se midió el ruido del eje Z de un acelerómetro (MPU6050) en reposo con tres condiciones de un motor cercano (apagado, PWM 60 %, PWM 100 %) y se compararon un filtro **FIR** (ventana de Hamming, orden 20) y un **IIR Butterworth** (orden 2), ambos pasa-bajas con corte en 5 Hz, sobre exactamente los mismos datos. Se calcularon SNR de entrada, SNR de salida, ΔSNR, cambio del valor medio, retardo, tiempo de ejecución y estabilidad. Además se estudió el efecto de cambiar el corte y el orden.

- **Plataforma:** ESP32 con MicroPython + IMU MPU6050 (módulo GY-521)
- **Muestreo:** 100 Hz (frecuencia real medida: 100.00 Hz), 20 s por registro (2000 muestras), escala ±2 g (16384 cuentas = 1 g)
- **Motor:** alimentado a 5 V mediante TIP120, PWM de 1 kHz
- **Dataset:** R1, R2 y R3 — versión del 14/10/2026

## Archivos

| Archivo | Contenido |
|---|---|
| `R1.csv`, `R2.csv`, `R3.csv` | Datos crudos: `timestamp_us`, `az_crudo`, `unidad`, `fs_hz`, `pwm_pct` |
| `adquisicion_esp32.py` | Código MicroPython con el que se grabaron los CSV |
| `PDS_Proyecto2_Notebook.ipynb` | Notebook reproducible: lee los CSV, calcula Ps, Pn, SNR, filtros, tablas y figuras |
| `tabla_resultados.csv` | Tabla de resultados R1–R3 |
| `tabla_cortes_ordenes.csv` | Barrido de frecuencia de corte y orden |
| `fig1_senales_espectro.png`, `fig2_filtradas.png`, `fig3_respuesta_polos.png`, `fig4_cortes_ordenes.png` | Gráficas del informe |
| `pds_proyecto2_notebook.py` | Copia del notebook exportada como script de Python |
| `PDS_Proyecto2_Equipo02.pdf` | Informe (6 páginas) |

## Cómo reproducir

1. Abrir `PDS_Proyecto2_Notebook.ipynb` en Google Colab (o Jupyter).
2. Subir `R1.csv`, `R2.csv` y `R3.csv` al mismo directorio del notebook.
3. Ejecutar todas las celdas (en Colab: *Entorno de ejecución → Reiniciar y ejecutar todo*).

Requiere `numpy`, `pandas`, `scipy` y `matplotlib`.

## Modelo de SNR

Con la IMU fija, la media es la señal útil y la variación alrededor de la media es el ruido:

- `Ps = media(x)²`
- `Pn = media((x − media(x))²)`
- `SNR = 10·log10(Ps / Pn)` [dB]

A las salidas filtradas (y a la entrada, para comparar con los mismos datos) se les descarta el primer segundo.

## Resultados principales (corte 5 Hz)

| Registro | SNR entrada [dB] | ΔSNR FIR [dB] | ΔSNR IIR [dB] |
|---|---|---|---|
| R1 (motor apagado) | 44.48 | +9.86 | +8.99 |
| R2 (PWM 60 %) | 39.10 | +4.27 | +3.36 |
| R3 (PWM 100 %) | 34.76 | +13.21 | +12.82 |
## Conclusión y regla de selección mecatrónica

- **IIR Butterworth (orden 2):** Recomendado para **sistemas de control en tiempo real** en el ESP32. Ejecuta **3.3 veces más rápido** (~21 µs/muestra) y genera la **mitad de retardo** (~5 muestras / 0.05 s) con una atenuación de ruido casi idéntica a la del FIR.
- **FIR Ventana Hamming (orden 20):** Recomendado para **posprocesamiento y análisis offline**, donde la **fase lineal exacta** es indispensable para no deformar morfológicamente la señal.

## Análisis del segundo eje (Requisito N5)

Se analizó el **Eje X** (sin componente principal de gravedad, $\bar{x}_X \approx 0.05\text{ m/s}^2$). Al aplicar el modelo $P_s = (\bar{x})^2$ y $P_n = \sigma^2$, la $\text{SNR}_{\text{in}}$ cae de $34.76\text{ dB}$ (Eje Z) a $18.25\text{ dB}$ (Eje X) en R3. Esto evidencia la limitación del modelo: la SNR en dB es relativa a la componente DC; en ejes sin gravedad la SNR disminuye drásticamente a pesar de que la potencia de ruido absoluto ($P_n$) generada por el motor es la misma.

## Entrega

- **Etiqueta de entrega:** `entrega-proy2`
- **Fecha de entrega:** 15/10/2026
- **Último commit evaluado:** f2d7dc0
- **Responsabilidad individual:**
  - Andrés Sánchez (código 7004389): montaje, circuito del motor, código del ESP32 y secciones 1–3 del notebook.
  - Daniel Andrés Gutiérrez (código 7004055): informe, GitHub y sección 4 del notebook.
