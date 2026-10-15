# Adquisición de datos - Proyecto 2 PDS (ESP32 + MicroPython + MPU6050 / GY-521)
#
# Graba 20 s del eje Z del acelerómetro a 100 Hz, SIN filtrar ni modificar el dato
# (cuentas crudas del sensor, escala +-2 g -> 16384 cuentas = 1 g).
# El motor (con TIP120 en GPIO 25, alimentado a 5 V) se prende al PWM indicado,
# se esperan 2 s para que la vibración se estabilice y luego se graba.
#
# Cómo se usó:
#   R1 -> NOMBRE = "R1", PWM_PCT = 0    (motor apagado)
#   R2 -> NOMBRE = "R2", PWM_PCT = 60   (perturbación baja)
#   R3 -> NOMBRE = "R3", PWM_PCT = 100  (perturbación alta)
#
# Conexiones: GY-521 VCC->3.3V, GND->GND, SCL->GPIO22, SDA->GPIO21 (dirección 0x68).

from machine import I2C, Pin, PWM
from time import ticks_us, ticks_add, ticks_diff, sleep_ms
import struct

# ---------- CONFIGURACIÓN (lo único que se cambia) ----------
NOMBRE = "R1"     # "R1", "R2" o "R3"
PWM_PCT = 0       # 0, 60 o 100
# ------------------------------------------------------------
FS = 100          # muestras por segundo
DURACION = 20     # segundos
N = FS * DURACION
DIR_MPU = 0x68

i2c = I2C(0, scl=Pin(22), sda=Pin(21), freq=400000)
i2c.writeto_mem(DIR_MPU, 0x6B, b'\x00')   # salir de modo sueño
i2c.writeto_mem(DIR_MPU, 0x1C, b'\x00')   # +-2 g, 16384 cuentas = 1 g
sleep_ms(200)

motor = PWM(Pin(25), freq=1000)
motor.duty_u16(0)

tiempos = [0] * N
valores = [0] * N

try:
    motor.duty_u16(int(65535 * PWM_PCT / 100))
    print("Motor al", PWM_PCT, "% - esperando 2 s...")
    sleep_ms(2000)

    print("Grabando", NOMBRE, "... NO toques nada")
    periodo = 1000000 // FS
    inicio = ticks_us()
    for i in range(N):
        objetivo = ticks_add(inicio, i * periodo)
        while ticks_diff(ticks_us(), objetivo) < 0:
            pass
        tiempos[i] = ticks_diff(ticks_us(), inicio)
        # registro 0x3F = ACCEL_ZOUT (eje Z), 2 bytes con signo
        valores[i] = struct.unpack('>h', i2c.readfrom_mem(DIR_MPU, 0x3F, 2))[0]
finally:
    motor.duty_u16(0)
    print("Motor apagado")

fs_real = (N - 1) * 1000000 / (tiempos[-1] - tiempos[0])

with open(NOMBRE + ".csv", "w") as f:
    f.write("timestamp_us,az_crudo,unidad,fs_hz,pwm_pct\n")
    for i in range(N):
        f.write("%d,%d,cuentas(16384=1g),%.2f,%d\n" % (tiempos[i], valores[i], fs_real, PWM_PCT))

prom = sum(valores) / N
print("Listo:", NOMBRE + ".csv")
print("Frecuencia real: %.2f Hz" % fs_real)
print("Promedio: %.0f | Minimo: %d | Maximo: %d" % (prom, min(valores), max(valores)))
