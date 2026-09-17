#! /usr/bin/python3
"""
Módulo Gestor de Drivers de Hardware y Ejecución por Plantillas para OmniProg
"""
import os
import subprocess
import shlex
import serial.tools.list_ports
from intelhex import IntelHex
import struct

def buscar_puertos_serial():
    """
    Buscador universal de puertos COM / ttyUSB.
    Utilizado por drivers de tipo 'serial' (FlashMagic, Toshiba UART, ST UART, etc.).
    """
    coms = []
    for potentialPort in list(serial.tools.list_ports.comports()):
        coms.append(potentialPort.device)
    return coms

def buscar_pickit5(executable_path):
    """
    Consulta a IPECMD para listar las herramientas conectadas por USB de forma rápida.
    Hereda el entorno del S.O. (os.environ) para resolver librerías nativas de Java/USB en Linux.
    """
    if not executable_path:
        print("Error: La ruta de IPECMD está vacía.")
        return []
        
    serial_numbers = []
    try:
        # Dividimos el comando complejo del .ini de forma segura
        partes_comando = shlex.split(executable_path)
        # Configuración correcta para Windows (posix=False)
        #partes_comando = shlex.split(executable_path,posix=False))
        if not partes_comando:
            return []
            
        ejecutable_base = partes_comando[0]
        
        # Validación preventiva: si el ejecutable base existe, seguimos adelante
        if not os.path.exists(ejecutable_base):
            print(f"Error: El ejecutable base no existe: {ejecutable_base}")
            return []
            
        # Forzamos los flags oficiales de listado de herramientas: -T (Tool) junto a -OL (List)
        comando_ejecucion = partes_comando + ["-T", "-OL"]
        print ('comando_ejecucion:\t',comando_ejecucion)
        # --- SOLUCIÓN INDUSTRIAL: Clonar e inyectar el entorno del sistema ---
        # Esto asegura que Java localice las librerías nativas (.so) de Microchip y los permisos de USB de Linux
        entorno_planta = os.environ.copy()
        
        proc = subprocess.run(
            comando_ejecucion, 
            stdin=subprocess.DEVNULL,
            capture_output=True,
            text=True, 
            env=entorno_planta, # Inyección de variables de entorno
            timeout=20          # Subimos ligeramente a 10s por el retardo de inicialización de Java en Linux
        )
        
        # Microchip a veces vuelca la lista de herramientas en stderr en lugar de stdout según la versión de JRE
        salida_consola = ""
        if proc.stdout:
            salida_consola += proc.stdout
        if proc.stderr:
            salida_consola += proc.stderr
            
        # Procesamos línea por línea el resultado combinado
        if salida_consola:
            for linea in salida_consola.splitlines():
                # Buscamos patrones típicos de listado de Microchip (S.No, BUR, PICkit, etc.)
                if any(palabra in linea for palabra in ["S.No", "PICkit", "Tool", "Connected"]):
                    if ":" in linea:
                        partes = linea.split(":")
                        serial_number = partes[-1].strip()
                        # Evitamos registrar cadenas vacías o literales de error
                        if serial_number and not any(err in serial_number.upper() for err in ["NONE", "ERROR", "NOT FOUND"]):
                            serial_numbers.append(serial_number)
                            
    except subprocess.TimeoutExpired:
        print("Warning: La consulta de IPECMD excedió el tiempo límite (10s).")
    except Exception as e:
        print(f"Error en buscador pickit5: {str(e)}")
                
    return serial_numbers



# --- CORRECCIÓN CRÍTICA DE ORDENACIÓN INVERSA ---
# MAPA_HARDWARE debe declararse OBLIGATORIAMENTE antes de ser invocado por escanear_hardware()
MAPA_HARDWARE = {
    "serial": lambda path: buscar_puertos_serial(),
    "pickit5": lambda path: buscar_pickit5(path)
}

def escanear_hardware(tipo_driver, executable_path):
    """Invoca el escaneo físico basándose en el tipo de driver del .ini."""
    # Ahora MAPA_HARDWARE ya existe en memoria y no provocará el error NameError
    buscador = MAPA_HARDWARE.get(tipo_driver, lambda path: buscar_puertos_serial())
    return buscador(executable_path)

def preparar_comando_consola(tipo_driver, executable_path, mcu_device, target_port, hex_file, params_ini, params_pg, num_file, program_name):
    print ('preparar_comando_consola')
    print ('tipo_driver:\t',tipo_driver)
    print ('executable_path:\t',executable_path)
    print ('mcu_device:\t',mcu_device)
    print ('target_port:\t',target_port)
    print ('hex_file:\t',hex_file)
    print ('params_ini:\t',params_ini)
    print ('params_pg:\t',params_pg)
    print ('num_file:\t',num_file)
    print ('program_name:\t',program_name)

    """
    Motor universal de OmniProg basado en plantillas con marcadores % de posición.
    Sustituye dinámicamente las variables de planta en la plantilla del .ini.
    Devuelve: (comando_final, usa_shell)
    """
    plantilla = params_ini.get("linea_comando", "")
    if not plantilla:
        return "", False
        
    port_full = target_port.strip()
    port_number = "".join(filter(str.isdigit, port_full))
    if not port_number:
        port_number = "1"  
        
    mcu_clean = mcu_device.upper()
    if tipo_driver == "pickit5":
        mcu_clean = mcu_clean.replace("PIC", "")
        
    valores_sustitucion = {
        "%path": executable_path,
        "%device": mcu_clean,
        "%params": params_pg.strip(),
        "%port": port_full,
        "%portn": port_number,
        "%hex": hex_file,
        "%num": num_file,
        "%program": program_name
    }

    comando_parseado = plantilla
    marcadores_ordenados = sorted(valores_sustitucion.keys(), key=len, reverse=True)
    
    for marcador in marcadores_ordenados:
        valor_real = valores_sustitucion[marcador]
        comando_parseado = comando_command = comando_parseado.replace(marcador, valor_real)

    if tipo_driver == "pickit5_":
        lista_argumentos = shlex.split(comando_parseado)
        # Configuración correcta para Windows (posix=False)
        #lista_argumentos = shlex.split(comando_parseado, posix=False)
        return lista_argumentos, False
    print ('comando_parseado: ',comando_parseado) 
    return comando_parseado, True
