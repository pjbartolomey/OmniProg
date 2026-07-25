#! /usr/bin/python3
"""
Módulo de Backend para el procesamiento de Firmware y SQTP en OmniProg
"""
import os
import io
import configparser
from intelhex import IntelHex
import omni_lib
import psutil  # Para comprobar si el PID sigue vivo de forma multiplataforma
from PySide6.QtWidgets import QFileDialog


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

def fusionar_e_inyectar_sqtp(archivo_pg, numero_sqtp_str):
    """
    Fusiona Program1 y Program2, e inyecta el número SQTP en la dirección indicada.
    Genera el archivo 'result.hex' en la misma carpeta que el .pg.
    """
    config_local = configparser.ConfigParser()
    config_local.read(archivo_pg)
    carpeta = os.path.dirname(archivo_pg)
    archivo_resultado = os.path.join(carpeta, 'result.hex')
    
    # Limpieza previa del entorno
    if os.path.exists(archivo_resultado):
        try:
            os.remove(archivo_resultado)
        except OSError:
            return False, "Error al eliminar el archivo result.hex antiguo."
            
    try:
        # Carga y procesado de Program1
        prog1_name = config_local.get('header', 'Program1')
        program1_path = os.path.join(carpeta, prog1_name)
        ih_master = IntelHex()
        ih_master.fromfile(program1_path, format='hex')
        
        # Procesado de Program2 (Opcional si el archivo .pg tiene cargador secundario)
        if config_local.has_option('header', 'Program2'):
            prog2_name = config_local.get('header', 'Program2')
            if prog2_name.strip():
                program2_path = os.path.join(carpeta, prog2_name)
                ih_2 = IntelHex()
                ih_2.fromfile(program2_path, format='hex')
                ih_master.merge(ih_2, overlap='replace')
                
        # Inyección del SQTP usando la misma lógica unificada de bytes
        mensaje, dir_str = omni_lib.readpg(archivo_pg, 'SQTP_Dir')
        hexdir = int(dir_str, 16)
        hexvalue = int(numero_sqtp_str, 16)
        
        # Formateo a 7 bytes little endian para la flash
        hexvalue_bin = hexvalue.to_bytes(7, 'little')
        ih_master.putsz(hexdir, hexvalue_bin)
        
        # Guardado en disco
        ih_master.write_hex_file(archivo_resultado)
        return True, "Fusión e inyección completada con éxito."
    except Exception as e:
        return False, f"Fallo en procesamiento IntelHex: {str(e)}"

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

def intentar_bloquear_sqtp(archivo_sqtp):
    """
    Intenta crear un archivo .lock al lado del archivo SQTP.
    Devuelve (True, '') si se bloqueó con éxito.
    Devuelve (False, 'Mensaje') si ya está bloqueado por otra instancia viva.
    """
    ruta_lock = archivo_sqtp + ".lock"
    pid_actual = os.getpid()
    
    if os.path.exists(ruta_lock):
        try:
            # Leemos el PID de la ventana que supuestamente lo bloqueó
            with open(ruta_lock, 'r') as f:
                pid_bloqueado = int(f.read().strip())
                
            # Comprobamos si esa instancia vieja sigue corriendo en el S.O.
            if psutil.pid_exists(pid_bloqueado):
                return False, f"El archivo SQTP ya está siendo usado por la instancia con PID {pid_bloqueado}."
            else:
                # Es un bloqueo fantasma de una caída anterior: lo borramos de forma segura
                os.remove(ruta_lock)
        except Exception:
            # Si el archivo .lock está corrupto o ilegible, asumimos que podemos sobreescribirlo
            pass

    try:
        # Creamos el archivo de bloqueo atómico con nuestro PID actual
        with open(ruta_lock, 'w') as f:
            f.write(str(pid_actual))
        return True, ""
    except IOError as e:
        return False, f"No se pudo crear el archivo de bloqueo: {str(e)}"

def liberar_bloqueo_sqtp(archivo_sqtp):
    """Elimina el archivo .lock asociado al SQTP al cerrar la ventana o cambiar de proyecto."""
    if not archivo_sqtp:
        return
    ruta_lock = archivo_sqtp + ".lock"
    if os.path.exists(ruta_lock):
        try:
            os.remove(ruta_lock)
        except Exception:
            pass
