#! /usr/bin/python3
"""
Módulo de Backend para el procesamiento de Firmware y SQTP en OmniProg
"""
import os
import io
from intelhex import IntelHex
import omni_lib
import psutil  # Para comprobar si el PID sigue vivo de forma multiplataforma
from PySide6.QtWidgets import QMessageBox, QFileDialog

import re
from intelhex import IntelHex

from PySide6.QtWidgets import QMessageBox  # Nota: Para mensajes de alerta es mejor QMessageBox que QFileDialog
import re
from intelhex import IntelHex

def generar_archivo_intel_hex_sqtp(sqtp_dir, sqtp_len, sqtp_num, ruta_salida, device):
    print('generar_archivo_intel_hex_sqtp:\t', sqtp_dir, sqtp_len, sqtp_num, ruta_salida, device)
    
    # 1. Normalizar el nombre del dispositivo para identificar la familia
    dev_upper = device.upper().strip()
    
    if re.search(r'PIC(10|12|16)', dev_upper):
        familia = "PIC16"
    elif "PIC18" in dev_upper:
        familia = "PIC18"
    elif "PIC24" in dev_upper or "DSPIC" in dev_upper:
        familia = "PIC24"
    else:
        # Mostramos la alerta visual en la interfaz UI
        QMessageBox.critical(
            None, 
            "Error de Dispositivo", 
            f"La familia del dispositivo '{device}' no es compatible o no fue reconocida.\n"
            "El proceso de programación se cancelará."
        )
        # FORZAMOS LA EXCEPCIÓN para detener la subrutina y activar el except externo
        raise ValueError(f"Familia no reconocida para el dispositivo: {device}")

    # --- El resto del código solo se ejecuta si NO entró al else ---
    try:
        # 2. Parsear parámetros básicos de entrada
        longitud_bytes = int(sqtp_len)
        direccion_base = int(sqtp_dir, 16)
        
        # Ajustar direccionamiento físico según la familia
        if familia in ["PIC18", "PIC24"]:
            direccion_inicio = direccion_base * 2
        else:  
            direccion_inicio = direccion_base

        # 3. Convertir el string hex a bytes crudos con el padding correcto
        hex_puro = sqtp_num.replace(" ", "").zfill(longitud_bytes * 2)
        datos_bytes = bytes.fromhex(hex_puro)
        
        if len(datos_bytes) > longitud_bytes:
            datos_bytes = datos_bytes[-longitud_bytes:]
            
        # 4. Invertir el orden a Little Endian
        datos_little_endian = datos_bytes[::-1]
        
        # 5. Construir el bloque binario empaquetado según la arquitectura
        bloque_final = bytearray()
        
        if familia == "PIC16":
            for b in datos_little_endian:
                bloque_final.append(b)       
                bloque_final.append(0x08)    
                
        elif familia == "PIC18":
            for b in datos_little_endian:
                bloque_final.append(b)       
                bloque_final.append(0x0C)    
                
        elif familia == "PIC24":
            for i in range(0, len(datos_little_endian), 2):
                b_bajo = datos_little_endian[i]
                b_alto = datos_little_endian[i+1] if (i+1) < len(datos_little_endian) else 0x00
                bloque_final.append(b_bajo)  
                bloque_final.append(b_alto)  
                bloque_final.append(0x00)    
                bloque_final.append(0x00)    

        # 6. Inicializar IntelHex e inyectar el bloque estructurado
        ih = IntelHex()
        ih.frombytes(bloque_final, offset=direccion_inicio)
        
        # 7. Exportar el archivo .num compatible con IPECMD
        ih.write_hex_file(ruta_salida)
        print(f"[{familia}] Archivo SQTP generado exitosamente en: {ruta_salida}")

    except Exception as e:
        # Si ocurre un error interno de parseo, lo relanzamos para que lo capture la rutina principal
        raise RuntimeError(f"Error interno generando Intel HEX: {e}")

def generar_consecutivos_sqtp(numero_inicial_hex, cantidad, longitud, directorio_defecto, parent=None):
    """
    Genera un archivo .sq con números de serie hexadecimales correlativos.
    Valida dinámicamente el límite de desbordamiento según la longitud en bytes.
    """
    # 1. Limpieza de texto inicial
    num_limpio = numero_inicial_hex.strip().replace("0x", "").replace("0X", "")
    caracteres_esperados = longitud * 2
    
    # 2. Validación de longitud máxima de caracteres del valor inicial
    if len(num_limpio) > caracteres_esperados:
        return False, (f"Error de Validación:\nEl número inicial ({num_limpio}) tiene {len(num_limpio)} caracteres. "
                       f"Para {longitud} byte(s) el máximo permitido son {caracteres_esperados} caracteres.")
    
    num_limpio = num_limpio.zfill(caracteres_esperados)

    # 3. Conversión al valor numérico base
    try:
        x_inicio = int(num_limpio, 16)
    except ValueError:
        return False, "Error: El número inicial no es un hexadecimal válido."

    # 4. VALIDACIÓN PREVENTIVA DE DESBORDAMIENTO (Antes de pedir el nombre)
    limite_maximo = (1 << (longitud * 8)) - 1
    
    # Calculamos de forma matemática cuál será el último número generado en el lote
    # Si sumamos la cantidad al número inicial, el valor máximo alcanzado será (x_inicio + cantidad - 1)
    valor_final_estimado = x_inicio + cantidad - 1
    
    if valor_final_estimado > limite_maximo:
        return False, (f"Fallo de Validación Preventiva:\nEl lote solicitado (Cantidad: {cantidad}) "
                       f"provocaría un desbordamiento físico en la memoria.\n"
                       f"El último número alcanzado sería {hex(valor_final_estimado).upper()}.\n"
                       f"El límite máximo para {longitud} byte(s) es {hex(limite_maximo).upper()}.")

    # 5. SOLICITUD ELEGANTE DEL NOMBRE DE ARCHIVO (Los datos ya están validados y son seguros)
    ruta_archivo_final, _ = QFileDialog.getSaveFileName(
        parent, 
        "Guardar archivo SQTP como...", 
        directorio_defecto, 
        "SQTP Files (*.sq)"
    )
    
    # Si el usuario presiona "Cancelar" en el diálogo, abortamos de forma silenciosa
    if not ruta_archivo_final:
        return False, "OPERACION_CANCELADA"
        
    if not ruta_archivo_final.endswith('.sq'):
        ruta_archivo_final += ".sq"

    if os.path.exists(ruta_archivo_final):
        return False, f"Warning! El archivo SQTP '{os.path.basename(ruta_archivo_final)}' ya existe en producción. No se permite sobreescribir."
        
    # 6. BUCLE DE ESCRITURA EN DISCO (Sin riesgos de fallo por cálculo)
    ancho_formato = (longitud * 2) + 2
    try:
        with open(ruta_archivo_final, 'w') as f:
            x = x_inicio
            for _ in range(cantidad):
                w = "{0:#0{1}x}".format(x, ancho_formato)
                f.write(":" + w.upper().replace("X", "x") + "\n")
                x += 1
                
        return True, ruta_archivo_final
    except IOError as e:
        return False, f"Error crítico de escritura en disco: {str(e)}"

def inyectar_sqtp(hex_target, sqtp_dir, sqtp_len, sqtp_num, ruta_salida, checksum_dir=None):
    """
    Inyecta el SQTP y calcula el checksum global de todo el firmware.
    Si se pasa 'checksum_dir', inyecta el checksum resultante (2 bytes, little endian) en esa dirección.
    """
    if os.path.exists(ruta_salida):
        try:
            os.remove(ruta_salida)
        except OSError:
            return False, "Error al eliminar el archivo antiguo."
           
    try:
        ih_master = IntelHex()
        ih_master.fromfile(hex_target, format='hex')

        # 1. Inyección del SQTP
        hexdir = int(sqtp_dir, 16) if isinstance(sqtp_dir, str) else int(sqtp_dir)
        hexvalue = int(sqtp_num, 16) if isinstance(sqtp_num, str) else int(sqtp_num)
        length = int(sqtp_len)

        hexvalue_bin = hexvalue.to_bytes(length, 'little')
        ih_master.puts(hexdir, hexvalue_bin)

        print ('inyectar_sqtp:\t',hex_target, sqtp_dir, sqtp_len, sqtp_num, ruta_salida, checksum_dir)
        # 2. Cálculo del Checksum Global (Suma de todos los bytes cargados)
        # 3. Inyección opcional del Checksum en el mapa de memoria
        if checksum_dir is not None:
            # Obtenemos un diccionario con todos los bytes rellenos en el archivo
            dict_bytes = ih_master.todict()
            
            # Sumamos el valor de cada byte y aplicamos máscara de 16 bits (0xFFFF)
            # Nota: Si tu firmware requiere excluir la zona del propio checksum, avísame.
            checksum_total = sum(dict_bytes.values()) & 0xFFFF
        
            print(f"Checksum calculado (16 bits): 0x{checksum_total:04X}")

            chk_dir_int = int(checksum_dir, 16) if isinstance(checksum_dir, str) else int(checksum_dir)
            checksum_bin = checksum_total.to_bytes(2, 'little')
            ih_master.puts(chk_dir_int, checksum_bin)
            print(f"Checksum guardado en la dirección: {checksum_dir}")

        # Guardado final
        ih_master.write_hex_file(ruta_salida)
        return True, f"Inyección y checksum (0x{checksum_total:04X}) completados."
        
    except Exception as e:
        return False, f"Fallo en procesamiento: {str(e)}"

def extraer_siguiente_sqtp(archivo_sq):
    """
    Busca la primera línea disponible que comience con ':' en el archivo .sq.
    Valida de forma estricta que cumpla con la longitud en bytes requerida.
    Devuelve (lineas, indice, numero_formateado) o (None, None, None) si falla/no coincide.
    """
    if not os.path.exists(archivo_sq):
        return None, None, None
        
    try:
        with open(archivo_sq, 'r') as f:
            lines = [line.rstrip('\n') for line in f]
            
        for idx, element in enumerate(lines):
            if element and element.startswith(':'):
                # Retorna el listado, el puntero del archivo y el número omitiendo el ':'
                numero_limpio = element[1:].replace('0x', '')
                return lines, idx, numero_limpio
                
        return None, None, None
    except IOError:
        return None, None, None
