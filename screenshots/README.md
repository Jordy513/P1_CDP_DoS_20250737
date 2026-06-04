# Capturas de pantalla — CDP DoS

Capturas del laboratorio en orden de demostración.

| # | Archivo | Descripción |
|---|---------|-------------|
| 1 | [01_topologia.png](screenshots/01_topologia.png) | Vista general de la topología en PNETLab con nombre y matrícula visibles |
| 2 | [02_ataque_ejecutandose.png](screenshots/02_ataque_ejecutandose.png) | Terminal de Kali Linux ejecutando el script CDP DoS |
| 3 | [03_sw2_tabla_vecions.png](screenshots/03_sw2_tabla_vecions.png) | Consola de SW2 mostrando `show cdp neighbors` con entradas falsificadas |
| 4 | [04_sw2_estado_memoria.png](screenshots/04_sw2_estado_memoria.png) | Consumo de memoria controlado (`show memory processor statistics`) tras alcanzar el límite máximo de 3,379 vecinos CDP; la CPU y RAM no colapsan debido a la eficiencia del entorno virtualizado. |
| 5 | [05_contramedida_aplicada.png](screenshots/05_contramedida_aplicada.png) | Configuración de `no cdp enable` en la interfaz de acceso |
| 6 | [06_tabla_limpia_post_mitigacion.png](06_tabla_limpia_post_mitigacion.png) | Tabla CDP vacía tras aplicar la contramedida |
