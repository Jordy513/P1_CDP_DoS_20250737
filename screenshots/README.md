# Capturas de pantalla — CDP DoS

Capturas del laboratorio en orden de demostración.

| Archivo | Descripción |
|---------|-------------|
| `01_topologia.png` | Topología en GNS3 con nombre y matrícula visibles |
| `02_tabla_cdp_antes.png` | Salida de `show cdp neighbors` en el switch **antes** del ataque |
| `03_ataque_ejecutando.png` | Script corriendo — se ven los mensajes `[*] Lanzando inundación CDP` |
| `04_tabla_cdp_durante.png` | Salida de `show cdp neighbors` con vecinos falsos acumulados |
| `05_cpu_uso.png` | Salida de `show processes cpu` mostrando el impacto en el switch |
| `06_mitigacion_aplicada.png` | Configuración `no cdp enable` aplicada en la interfaz |
| `07_tabla_cdp_limpia.png` | Salida de `show cdp neighbors` después de aplicar la contramedida |
