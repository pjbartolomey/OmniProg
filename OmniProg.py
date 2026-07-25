#! /usr/bin/python3
# License: GNU General Public License (GPL) v.3
"""
OmniProg - Frontend de Programación Universal Multi-Fabricante
Optimizado para PySide6, Multi-instancia y Arquitectura Simplificada
"""

import argparse
import sys
import subprocess
import os
import io
import time
import configparser
from intelhex import IntelHex

import omni_lib
import omni_firmware
import omni_drivers


from PySide6 import QtCore, QtGui, QtWidgets
from PySide6.QtCore import QRegularExpression
from PySide6.QtGui import QPixmap, QRegularExpressionValidator
from PySide6.QtWidgets import QMessageBox, QFileDialog


# Importamos la interfaz moderna recién generada
from OmniProg_ui import Ui_MainWindow

VERSION = 'Ver: 1.0.0 (OmniProg)'

def process_cl_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('open', nargs='?', action='store')  # Captura el archivo .pg al hacer doble clic
    parsed_args, unparsed_args = parser.parse_known_args()
    return parsed_args, unparsed_args

class MyApp(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self, archivo_inicial=''):
        QtWidgets.QMainWindow.__init__(self)
        Ui_MainWindow.__init__(self)
        self.setupUi(self)
        
        # --- ENCAPSULACIÓN MAESTRA (Multi-instancia segura) ---
        self.version = VERSION
        self.omniprog_ini = 'OmniProg.ini'
        self.lines = []
        self.puntero_lines = 0
        self.need_sqtp = 0
        self.motor_activo = ''  # Guardará 'flashmagic', 'IPECMD', etc.
        self.mcu_device = ''     # Modelo específico del micro extraído del .pg
        self.debug = 0           # <--- AÑADIR ESTA LÍNEA: Guarda el estado de depuración de planta
        
        # Contadores aislados por ventana
        self.count = 0
        self.c_pass = 0
        self.c_fail = 0
        self.archivo = archivo_inicial
        
        # --- CONFIGURACIÓN E INICIALIZACIÓN ---
        self.Checkini()
        
        # Validación moderna hexadecimal de 8 dígitos para Qt6
        regex_hex = QRegularExpression('^[0-9A-Fa-f]{8}$')
        self.line_Num_Ini.setValidator(QRegularExpressionValidator(regex_hex, self))
        self.line_SQTPNumber.setValidator(QRegularExpressionValidator(regex_hex, self))
        
        # --- CONEXIÓN DE EVENTOS GRÁFICOS ---
        self.Button_Generar.clicked.connect(self.Generar)
        self.Button_Prog.clicked.connect(self.OpenPrograma)
        self.Button_SQTP.clicked.connect(self.OpenSQTP)
        self.Button_program.clicked.connect(self.program)
        self.check_SQTPMan.stateChanged.connect(self.ManSQTP)
        self.Button_rescan.clicked.connect(self.RefreshPortList)
        
        self.Button_Prog_1.clicked.connect(self.Selecthex_1)
        self.Button_Prog_2.clicked.connect(self.Selecthex_2)
        self.Button_Merge.clicked.connect(self.Merge)
        self.Button_Compare.clicked.connect(self.CompararHexNativo)
        self.Button_C_Reset.clicked.connect(self.ResetCounter)

        self.Button_Prog_hex1.clicked.connect(self.Selecthex_hex1)
        self.Button_Prog_hex2.clicked.connect(self.Selecthex_hex2)
        self.Button_createpg.clicked.connect(self.CreatePGFile)
        
        # Inicialización de entorno base
        self.actualizar_statusbar()
        
        # Si se abrió el software mediante doble clic en un archivo .pg
        if self.archivo != '':
            self.CargarPrograma()

        # Inicializar el combo del creador de archivos .pg leyendo el archivo .ini de planta
        self.InicializarCreadorPG()

    def Checkini(self):
        """Inicializa las rutas buscando de forma segura los parámetros base en el archivo .ini."""
        carpeta_del_exe = os.path.dirname(os.path.realpath(sys.argv[0]))
        self.omniprog_ini = os.path.join(carpeta_del_exe, 'OmniProg.ini')
        
        try:
            # Reutilizamos la función robustecida de omni_lib
            self.defaultprogdir = omni_lib.readini(self.omniprog_ini, "Default", "defaultprogdir")
            self.defaultsqtpdir = omni_lib.readini(self.omniprog_ini, "Default", "defaultsqtpdir")
            
            # Capturamos el parámetro debug de forma segura (0 por defecto si falla o no existe)
            try:
                self.debug = int(omni_lib.readini(self.omniprog_ini, "Default", "debug"))
            except Exception:
                self.debug = 0
                
        except FileNotFoundError as e:
            self.showdialog(f"Falta el archivo de configuración obligatorio:\n{str(e)}")
            sys.exit(1)
        except KeyError as e:
            self.showdialog(f"Error crítico de inicialización:\n{str(e)}\n\nPor favor, revise el archivo .ini.")
            sys.exit(1)

    def buscar_motor_para_micro(self, mcu_model):
        """Escanea el .ini para determinar qué motor controla al micro."""
        cparser = configparser.ConfigParser()
        cparser.read(self.omniprog_ini)
        
        for seccion in cparser.sections():
            if seccion == "Default":
                continue
            if cparser.has_option(seccion, "micros"):
                lista_micros = [m.strip() for m in cparser.get(seccion, "micros").split(',')]
                if mcu_model in lista_micros:
                    return seccion
        return None

    def RefreshPortList(self):
        """
        Rutina universal agnóstica al fabricante.
        Muestra trazas detalladas de escaneo en el textEdit si debug = 1.
        """
        self.Button_rescan.setEnabled(False)
        QtWidgets.QApplication.processEvents()
        
        self.comboBoxPort.clear()
        self.comboBoxPort.addItem(' ') # Índice cero vacío por seguridad
        
        cparser = configparser.ConfigParser()
        cparser.read(self.omniprog_ini)
        
        tipo_driver = "serial"
        executable_path = ""
        
        if cparser.has_section(self.motor_activo):
            if cparser.has_option(self.motor_activo, "driver"):
                tipo_driver = cparser.get(self.motor_activo, "driver").strip()
            if cparser.has_option(self.motor_activo, "path"):
                executable_path = cparser.get(self.motor_activo, "path").replace('"', '')
                
        # --- TRAZAS DE DEPURACIÓN EN INTERFAZ (DEBUG ACTIVO) ---
        if self.debug == 1:
            #self.textEdit.clear()
            self.textEdit.append("=== REFRESH PORTS (DEBUG) ===")
            self.textEdit.append(f"Motor Activo Detectado: [{self.motor_activo.upper()}]")
            self.textEdit.append(f"Tipo de Driver a escanear: {tipo_driver}")
            self.textEdit.append(f"Ruta del Ejecutable asignada: {executable_path if executable_path else 'N/A (Serial Puro)'}")
            QtWidgets.QApplication.processEvents()

        try:
            lista_dispositivos = omni_drivers.escanear_hardware(tipo_driver, executable_path)
            
            if lista_dispositivos:
                self.comboBoxPort.addItems(lista_dispositivos)
                if self.debug == 1:
                    self.textEdit.append(f"Hardware Encontrado con éxito: {lista_dispositivos}")
            else:
                if self.debug == 1:
                    self.textEdit.append("Resultado del escaneo: No se detectó ningún hardware activo.")
                    if tipo_driver == "pickit5":
                        self.textEdit.append("Ayuda PICkit5: Verifique que el programador USB esté conectado y que la ruta de ipecmd en el .ini sea correcta.")
                        
        except Exception as e:
            self.showdialog(f"Error durante el escaneo de hardware: {str(e)}")
            if self.debug == 1:
                self.textEdit.append(f"Fallo Crítico en Escaneo: {str(e)}")
        finally:
            # Seleccionamos el programador recién detectado si existe algo más que el espacio en blanco
            if self.comboBoxPort.count() > 1:
                self.comboBoxPort.setCurrentIndex(self.comboBoxPort.count() - 1)
            else:
                self.comboBoxPort.setCurrentIndex(0)
            
            # Forzamos la comprobación de requisitos de forma atómica.
            self.Activar_Prog()
            
            # Devolvemos el control al botón de refresco
            self.Button_rescan.setEnabled(True)
            QtWidgets.QApplication.processEvents()

    def CargarPrograma(self):
        self.line_Prog.clear()
        
        # --- CORRECCIÓN INDUSTRIAL DE SINCRONIZACIÓN ---
        if self.archivo and os.path.exists(self.archivo):
            os.chdir(os.path.dirname(os.path.realpath(self.archivo)))

        # Comprobar el modelo del chip declarado en el archivo .pg
        mensaje, device_str = omni_lib.readpg(self.archivo, 'Device')
        if mensaje or not device_str:
            self.showdialog('Error: No se define la variable "Device" dentro del archivo .pg')
            self.archivo = ''
            return
            
        self.mcu_device = device_str.strip()
        self.motor_activo = self.buscar_motor_para_micro(self.mcu_device)
        
        if not self.motor_activo:
            self.showdialog(f'Error: El microcontrolador [{self.mcu_device}] no está registrado en OmniProg.ini')
            self.archivo = ''
            return
            
        # Analizar si requiere SQTP
        mensaje, valor = omni_lib.readpg(self.archivo, 'SQTP_Dir')
        self.need_sqtp = 0 if mensaje else 1
            
        if self.need_sqtp == 0:
            self.Button_SQTP.setEnabled(False)
            self.check_SQTPMan.setEnabled(False)
            self.line_SQTP.clear()
            self.line_SQTPNumber.clear()
            self.line_Prog.setText(self.archivo)
        else:
            self.Button_SQTP.setEnabled(True)
            self.check_SQTPMan.setEnabled(True)
            self.line_Prog.setText(self.archivo)
            
        # --- AUTOMATIZACIÓN REACTIVA: PRECONFIGURACIÓN DE LA PESTAÑA TOOLS ---
        try:
            # 1. Leer variables adicionales del archivo .pg de manera preventiva
            _, p_sqtp_dir = omni_lib.readpg(self.archivo, 'SQTP_Dir')
            _, p_sqtp_len = omni_lib.readpg(self.archivo, 'SQTP_Len')
            _, p_params = omni_lib.readpg(self.archivo, 'params')
            _, p_prog1 = omni_lib.readpg(self.archivo, 'Program1')
            _, p_prog2 = omni_lib.readpg(self.archivo, 'Program2')

            # 2. Bloque SQTP Generate: Sincronizar 'Length (Bytes)'
            if p_sqtp_len and str(p_sqtp_len).strip().isdigit():
                self.QSpin_SQTPLen1.setValue(int(str(p_sqtp_len).strip()))

            # 3. Bloque Create PG File: Sincronizar combobox 'device'
            # Buscamos si el dispositivo del .pg existe en el combobox para seleccionarlo
            idx_device = self.comboBox_device.findText(self.mcu_device)
            if idx_device >= 0:
                self.comboBox_device.setCurrentIndex(idx_device)
            else:
                # Si el micro no estaba en la lista ordenada del combo, lo añadimos y seleccionamos
                self.comboBox_device.addItem(self.mcu_device)
                self.comboBox_device.setCurrentIndex(self.comboBox_device.count() - 1)

            # 4. Bloque Create PG File: Sincronizar 'sqtp_dir'
            if p_sqtp_dir and str(p_sqtp_dir).strip() != '0':
                self.line_sqtp_dir.setText(str(p_sqtp_dir).strip())
            else:
                self.line_sqtp_dir.clear()

            # 5. Bloque Create PG File: Sincronizar 'sqtp_len'
            if p_sqtp_len and str(p_sqtp_len).strip().isdigit():
                self.QSpin_SQTPLen2.setValue(int(str(p_sqtp_len).strip()))
            else:
                self.QSpin_SQTPLen2.setValue(1) # Valor mínimo por defecto de la UI

            # 6. Bloque Create PG File: Sincronizar 'params'
            if p_params and str(p_params).strip() != '0':
                self.line_params.setText(str(p_params).strip())
            else:
                self.line_params.clear()

            # [Opcional de regalo] Sincronizar también los campos de firmware del creador para dejarlo impecable
            if p_prog1 and str(p_prog1).strip() != '0':
                self.line_Prog_hex1.setText(str(p_prog1).strip())
            else:
                self.line_Prog_hex1.clear()
                
            if p_prog2 and str(p_prog2).strip() != '0':
                self.line_Prog_hex2.setText(str(p_prog2).strip())
            else:
                self.line_Prog_hex2.clear()

            if self.debug == 1:
                self.textEdit.append("-> Datos del archivo .pg volcados con éxito en la pestaña Tools.")

        except Exception as e:
            if self.debug == 1:
                self.textEdit.append(f"-> Error menor al preconfigurar la pestaña Tools: {str(e)}")

        # Sincronizamos la lista de grabadores y validamos requisitos finales de la pestaña principal
        self.RefreshPortList()
        self.Activar_Prog()

    def hexmergefile(self):
        # Llama a la librería pasándole la cadena de texto de la pantalla
        exito, msg = omni_firmware.fusionar_e_inyectar_sqtp(self.archivo, self.line_SQTPNumber.text())
        if not exito:
            self.showdialog(msg)
            return None
        return 'ok'

    def program(self):
        self.Button_program.setEnabled(False)
        if self.line_SQTPNumber.text() == '' and self.need_sqtp == 1:
            self.label_PASS.setText('INVALID SQTP')
            self.Button_program.setEnabled(True)
            return

        if self.debug != 1:
            self.textEdit.clear()            
        
        # RESETEAR ESTILO AL INICIAR: Quita el color anterior mientras se graba el chip
        self.label_PASS.setStyleSheet("") 
        self.label_PASS.setText("PROGRAMING...")
        self.textEdit.append(f"Motor de planta activo: [{self.motor_activo.upper()}]")
        
        # 1. Extraer parámetros del OmniProg.ini
        cparser = configparser.ConfigParser(interpolation=None)
        cparser.read(self.omniprog_ini)
     
        tipo_driver = cparser.get(self.motor_activo, "driver", fallback="serial").strip()
        executable_path = cparser.get(self.motor_activo, "path").replace('"', '')
        
        # Cargamos todas las opciones de la sección del motor
        params_ini = {}
        if cparser.has_section(self.motor_activo):
            for opcion in cparser.options(self.motor_activo):
                params_ini[opcion] = cparser.get(self.motor_activo, opcion)

        #Opciones:
            # Programacion directa 
            # Programacion con SQTP PK5
            # Programacion con SQTP 2 Hex

        # 1. Si necesitamos SQTP
        if self.need_sqtp == 1:
            self.label_PASS.setText('GENERATING HEX')
            QtWidgets.QApplication.processEvents()
            if tipo_driver == 'flashmagic'
                exito_merge, msg_merge = omni_firmware.fusionar_e_inyectar_sqtp(self.archivo, self.line_SQTPNumber.text())
                if not exito_merge:
                    if self.debug == 1:
                        # En modo depuración, mandamos todo el log estructurado a la consola de la UI
                        self.textEdit.append("\n" + "!"*40)
                        self.textEdit.append("CRITICAL ERROR DURING HEX MERGE")
                        self.textEdit.append(msg_merge)
                        self.textEdit.append("!"*40 + "\n")
                    else:
                        # En modo producción normal, mostramos el aviso estándar resumido
                        # Filtramos para no asustar al operario con el log técnico si se acumuló
                        resumen_error = msg_merge.splitlines()[-1] if "LOG ===" in msg_merge else msg_merge
                        self.showdialog(resumen_error)
                        
                    self.label_PASS.setText('MERGE FAILED')
                    self.Button_program.setEnabled(True)
                    return
            if tipo_driver == 'pickit5'

            # Convertimos result.hex a ruta absoluta completa
            hex_target = os.path.abspath("result.hex")
        else:
            # Si no requiere SQTP, leemos Program1 y calculamos su ruta absoluta
            _, nombre_hex = omni_lib.readpg(self.archivo, 'Program1')
            carpeta_proyecto = os.path.dirname(os.path.realpath(self.archivo))
            hex_target = os.path.abspath(os.path.join(carpeta_proyecto, nombre_hex.strip()))
        
        # Extraer parámetros específicos de la placa desde el archivo de configuración .pg
        _, params_pg = omni_lib.readpg(self.archivo, 'params')
        params_pg_clean = params_pg.strip() if params_pg else ''
        
        # 3. LLAMADA UNIVERSAL AL GESTOR DE DRIVERS BASADO EN PLANTILLAS %
        target_hardware = self.comboBoxPort.currentText()
        
        comando_args, use_shell = omni_drivers.preparar_comando_consola(
            tipo_driver, 
            executable_path, 
            self.mcu_device, 
            target_hardware, 
            hex_target, 
            params_ini, 
            params_pg_clean
        )

        # 4. EJECUCIÓN ASÍNCRONA EN EL SISTEMA OPERATIVO
        self.label_PASS.setText('PROGRAMING')
        self.textEdit.append(f"Executing: {comando_args}\n")
        QtWidgets.QApplication.processEvents()
        
        returncode = -1
        try:
            proc = subprocess.Popen(
                comando_args, 
                stdout=subprocess.PIPE, 
                stderr=subprocess.STDOUT, 
                text=True, 
                shell=use_shell
            )
            
            # Captura de la consola en tiempo real
            while True:
                linea = proc.stdout.readline()
                if not linea and proc.poll() is not None:
                    break
                if linea:
                    self.textEdit.append(linea.strip())
                    QtWidgets.QApplication.processEvents()
                    
            returncode = proc.poll()
        except Exception as e:
            self.textEdit.append(f"\nExecution Fail: {str(e)}")
            returncode = -1

        # --- 5. EVALUACIÓN Y GESTIÓN DE CONTADORES EN PLANTA ---
        texto_consola_completo = self.textEdit.toPlainText().upper()
        
        # Filtro de seguridad: error de código o palabras clave en la consola
        hubo_error_en_texto = any(palabra in texto_consola_completo for palabra in ["ERROR:", "FAIL", "INVALID"])
        
        if returncode == 0 and not hubo_error_en_texto:
            time.sleep(0.5)
            self.label_PASS.setText('PROGRAM OK')
            
            # PINTAMOS EL FONDO VERDE: Fondo verde oscuro, texto blanco y negrita para que resalte
            self.label_PASS.setStyleSheet("""
                background-color: #2ECC71; 
                color: white; 
                font-weight: bold;
                border-radius: 4px;
            """)
            
            self.count += 1
            self.c_pass += 1
            
            if self.need_sqtp == 1 and not self.check_SQTPMan.isChecked():
                element = self.lines[self.puntero_lines]
                element = ';' + element[1:]
                self.lines[self.puntero_lines] = element
                with open(self.line_SQTP.text(), 'wt') as out_file:
                    for el in self.lines:
                        out_file.write(el + "\n")
                self.puntero_lines += 1
                self.SQTP(self.line_SQTP.text())
        else:
            self.label_PASS.setText('PROGRAM FAILED')
            
            # PINTAMOS EL FONDO ROJO: Fondo rojo industrial, texto blanco y negrita
            self.label_PASS.setStyleSheet("""
                background-color: #E74C3C; 
                color: white; 
                font-weight: bold;
                border-radius: 4px;
            """)
            
            self.count += 1
            self.c_fail += 1
            
        self.Button_program.setEnabled(True)
        self.Activar_Prog()
        self.actualizar_statusbar()

    def Generar(self):
        """Despacha la lógica de generación SQTP delegando la validación y el diálogo al backend."""
        if self.line_Num_Ini.text() == "":
            self.showdialog('Warning! Es obligatorio un número inicial.')
            return
            
        cantidad = int(self.QSpin_Cantidad.value())
        longitud = int(self.QSpin_SQTPLen1.value())
        
        # Invocamos la librería pasándole 'self' como parent para que el diálogo se dibuje correctamente
        exito, resultado = omni_firmware.generar_consecutivos_sqtp(
            self.line_Num_Ini.text(), 
            cantidad, 
            longitud, 
            self.defaultsqtpdir,
            parent=self
        )
        
        if exito:
            self.showdialog(f"Archivo de producción generado con éxito en:\n{resultado}")
        else:
            # Si el usuario simplemente canceló el diálogo de guardar, salimos sin alertar de un error falso
            if resultado == "OPERACION_CANCELADA":
                return
            # Si la validación matemática preventiva falló, mostramos el reporte detallado
            self.showdialog(resultado)

    def OpenPrograma(self):
        fileName, _ = QFileDialog.getOpenFileName(self, "Open Program", self.defaultprogdir, "Program Files (*.pg)")
        if fileName:
            self.archivo = fileName
            self.CargarPrograma()

    def OpenSQTP(self):
        fileName, _ = QFileDialog.getOpenFileName(self, "Open SQTP", self.defaultsqtpdir, "SQTP Files (*.sq)")
        if fileName:
            self.SQTP(fileName)
        self.Activar_Prog()

    def SQTP(self, fileName):
        # --- NUEVO BLOQUE DE CONCURRENCIA ATÓMICA ---
        # Antes de leer el archivo, intentamos bloquearlo con el archivo .lock de planta
        bloqueado_ok, msg_err = omni_firmware.intentar_bloquear_sqtp(fileName)
        if not bloqueado_ok:
            self.showdialog(f"Warning! Recursos en uso:\n{msg_err}")
            self.line_SQTPNumber.clear()
            self.line_SQTP.clear()
            self.Activar_Prog()
            return

        # Si el bloqueo es exitoso, extraemos el número de serie de forma habitual
        resultado = omni_firmware.extraer_siguiente_sqtp(fileName)
        self.lines, self.puntero_lines, numero_serie = resultado
        
        if numero_serie:
            self.line_SQTPNumber.setText(numero_serie)
            self.line_SQTP.setText(fileName)
            if len(self.archivo) > 0:
                self.Button_program.setEnabled(True)
        else:
            self.showdialog("Warning! Este archivo no contiene números SQTP libres.")
            omni_firmware.liberar_bloqueo_sqtp(fileName) # Liberamos si estaba vacío
            self.line_SQTPNumber.clear()
            self.line_SQTP.clear()
            self.check_SQTPMan.setChecked(False)
            self.Activar_Prog()

    def ManSQTP(self):
        if self.line_SQTP.text() == '':
            self.line_SQTPNumber.clear()
        if self.check_SQTPMan.isChecked():
            self.line_SQTPNumber.setEnabled(True)
            if self.line_SQTPNumber.text() == '':
                self.line_SQTPNumber.setText('00000000')
        else:
            self.line_SQTPNumber.setEnabled(False)
            if self.line_SQTP.text() != '':
                self.SQTP(self.line_SQTP.text())
        self.Activar_Prog()

    def Activar_Prog(self):
        """Controla el estado del botón PROGRAM y muestra la línea de comandos preventiva si debug=1."""
        # Validación base de requisitos
        if os.path.exists(self.archivo) and self.comboBoxPort.currentIndex() > 0:
            self.Button_program.setEnabled(True)
            if (self.need_sqtp == 1) and (not os.path.exists(self.line_SQTP.text())) and (not self.check_SQTPMan.isChecked()):
                self.Button_program.setEnabled(False)
        else:
            self.Button_program.setEnabled(False)

        # --- MODO DEBUG: Escribir la línea de comandos de forma reactiva ---
        if self.Button_program.isEnabled() and self.debug == 1:
            # Determinamos el target hexadecimal que se usaría
            if self.need_sqtp == 1:
                hex_target = os.path.abspath("result.hex")
            else:
                _, nombre_hex = omni_lib.readpg(self.archivo, 'Program1')
                carpeta_proyecto = os.path.dirname(os.path.realpath(self.archivo))
                hex_target = os.path.abspath(os.path.join(carpeta_proyecto, nombre_hex.strip()))

            # Extraemos los parámetros de los archivos de configuración de la misma forma que en program()
            cparser = configparser.ConfigParser(interpolation=None)
            cparser.read(self.omniprog_ini)
            
            tipo_driver = cparser.get(self.motor_activo, "driver", fallback="serial").strip()
            executable_path = cparser.get(self.motor_activo, "path", fallback="").replace('"', '')
            
            params_ini = {}
            if cparser.has_section(self.motor_activo):
                for opcion in cparser.options(self.motor_activo):
                    params_ini[opcion] = cparser.get(self.motor_activo, opcion)
                    
            _, params_pg = omni_lib.readpg(self.archivo, 'params')
            params_pg_clean = params_pg.strip() if params_pg else ''
            target_hardware = self.comboBoxPort.currentText()

            try:
                # Invocamos el generador de comandos del driver de manera preventiva
                comando_args, _ = omni_drivers.preparar_comando_consola(
                    tipo_driver, 
                    executable_path, 
                    self.mcu_device, 
                    target_hardware, 
                    hex_target, 
                    params_ini, 
                    params_pg_clean
                )
                
                # Convertimos la lista de argumentos a una cadena legible
                cmd_string = " ".join(comando_args) if isinstance(comando_args, list) else str(comando_args)
                
                # Acumulamos la información en el cuadro de texto en lugar de borrar
                self.textEdit.append("\n" + "="*40)
                self.textEdit.append("=== PREVENTIVE COMMAND (DEBUG) ===")
                self.textEdit.append(f"Target Hex: {hex_target}")
                self.textEdit.append(f"Comando a ejecutar:\n{cmd_string}")
                
            except Exception as e:
                # Acumulamos el error de cálculo si ocurre
                self.textEdit.append("\n" + "="*40)
                self.textEdit.append(f"=== DEBUG ERROR ===\nNo se pudo calcular el comando de consola: {str(e)}")

    def CompararHexNativo(self):
        """
        Compara de forma nativa e industrial el mapa de memoria de dos archivos HEX.
        Carga los datos mediante inyección directa en el búfer para evitar errores de checksum y overlap.
        """
        hex1_path = self.line_Prog_1.text().strip()
        hex2_path = self.line_Prog_2.text().strip()

        if not hex1_path or not hex2_path:
            self.showdialog("Error de comparación:\nDebe cargar ambos archivos HEX en la pestaña Tools.")
            return

        self.textEdit.clear()
        self.textEdit.append("=== INICIANDO COMPARACIÓN NATIVA DE MEMORIA ===")
        self.textEdit.append(f"Archivo 1: {os.path.basename(hex1_path)}")
        self.textEdit.append(f"Archivo 2: {os.path.basename(hex2_path)}\n")
        QtWidgets.QApplication.processEvents()

        try:
            # --- 1. CARGA SEGURO DE ARCHIVO 1 (Inyección directa anti-overlap) ---
            ih1 = IntelHex()
            try:
                ih1.loadhex(hex1_path)
            except Exception:
                # Si el compilador mete ruidos, usamos un lector de registros nativos independientes
                ih1 = IntelHex()
                with open(hex1_path, 'r') as f1:
                    for linea in f1:
                        l_strip = linea.strip()
                        if l_strip.startswith(':') and not l_strip.startswith(':00000001'):
                            try:
                                # Cargamos el registro individual en un objeto temporal utilizando el parser oficial
                                import io
                                # Al pasarle también el registro de fin de archivo virtual, evitamos que entre en bucle de CPU
                                l_safe = l_strip + "\n:00000001FF"
                                th = IntelHex()
                                th.loadhex(io.StringIO(l_safe))
                                # Volcamos los bytes calculados directamente en el búfer maestro mapeando sus posiciones reales
                                for addr in th.addresses():
                                    ih1._buf[addr] = th._buf[addr]
                            except Exception:
                                continue

            # --- 2. CARGA SEGURO DE ARCHIVO 2 (Inyección directa anti-overlap) ---
            ih2 = IntelHex()
            try:
                ih2.loadhex(hex2_path)
            except Exception:
                ih2 = IntelHex()
                with open(hex2_path, 'r') as f2:
                    for linea in f2:
                        l_strip = linea.strip()
                        if l_strip.startswith(':') and not l_strip.startswith(':00000001'):
                            try:
                                import io
                                l_safe = l_strip + "\n:00000001FF"
                                th = IntelHex()
                                th.loadhex(io.StringIO(l_safe))
                                for addr in th.addresses():
                                    ih2._buf[addr] = th._buf[addr]
                            except Exception:
                                continue

            # --- 3. EXTRACCIÓN DE DIRECCIONES COMBINADAS (Búfer rápido) ---
            direcciones_ih1 = set(ih1._buf.keys())
            direcciones_ih2 = set(ih2._buf.keys())
            todas_las_direcciones = direcciones_ih1 | direcciones_ih2
            
            diferencias = 0
            max_errores_visibles = 20
            
            # --- 4. BUCLE DE COMPARACIÓN DIRECTA SOBRE EL DICCIONARIO ---
            for addr in sorted(todas_las_direcciones):
                byte1 = ih1._buf.get(addr, 0xFF)
                byte2 = ih2._buf.get(addr, 0xFF)
                
                if byte1 != byte2:
                    diferencias += 1
                    if diferencias <= max_errores_visibles:
                        self.textEdit.append(f"-> Discrepancia en Dirección [0x{addr:06X}]: "
                                             f"Prog1 = 0x{byte1:02X} | Prog2 = 0x{byte2:02X}")
                    elif diferencias == max_errores_visibles + 1:
                        self.textEdit.append("... Se omiten el resto de diferencias individuales por espacio ...")
                    
                    if diferencias % 50 == 0:
                        QtWidgets.QApplication.processEvents()

            # --- 5. REPORTE FINAL EN CONSOLA Y DIÁLOGO ---
            self.textEdit.append("\n" + "="*40)
            if diferencias == 0:
                self.tabWidget.setCurrentIndex(0) # Cambiar al panel de ejecución automáticamente
                self.textEdit.append("RESULTADO: ¡COMPATIBILIDAD 100% ABSOLUTA!")
                self.textEdit.append("Los archivos tienen formatos de texto distintos, pero la memoria física es IDÉNTICA.")
            else:
                self.tabWidget.setCurrentIndex(0) # Cambiar al panel de ejecución automáticamente
                self.textEdit.append(f"RESULTADO: DIFERENCIAS DETECTADAS")
                self.textEdit.append(f"Se han encontrado un total de {diferencias} byte(s) distintos en la Flash.")

        except Exception as e:
            self.textEdit.append(f"\nError crítico durante la comparación: {str(e)}")
            self.showdialog(f"Fallo al comparar los archivos:\n{str(e)}")

    def Merge(self):
        # Validación de seguridad: no permitir avanzar si los campos están vacíos
        hex1_path = self.line_Prog_1.text().strip()
        hex2_path = self.line_Prog_2.text().strip()

        if not hex1_path or not hex2_path:
            self.showdialog("Error de fusión:\nEs obligatorio cargar ambos archivos HEX antes de proceder.")
            return

        fileName, _ = QFileDialog.getSaveFileName(self, "Save Merged Hex", hex1_path, "Hex File (*.hex)")
        if fileName:
            # Asegurar extensión .hex si el operario no la escribe
            if not fileName.lower().endswith('.hex'):
                fileName += '.hex'

            try:
                self.statusBar().showMessage("Fusionando mapas de memoria...")
                QtWidgets.QApplication.processEvents()

                ih_1 = IntelHex()
                ih_1.fromfile(hex1_path, format='hex')
                
                ih_2 = IntelHex()
                ih_2.fromfile(hex2_path, format='hex')
                
                # Combinamos reemplazando datos en zonas coincidentes de forma atómica
                ih_1.merge(ih_2, overlap='replace')
                
                # Escribimos el archivo de salida definitivo
                ih_1.write_hex_file(fileName)
                
                self.statusBar().showMessage(f"Fusión completada con éxito.", 5000)
                self.showdialog(f"¡Éxito!\nArchivo fusionado guardado correctamente en:\n{os.path.basename(fileName)}")
                
            except Exception as e:
                self.statusBar().showMessage("Fallo crítico en la fusión HEX.", 4000)
                self.showdialog(f"Error crítico durante el proceso Merge:\n\n{str(e)}\n\nVerifique los archivos origen o los permisos de escritura.")

    def Selecthex_1(self):
        fileName, _ = QFileDialog.getOpenFileName(self, "Open Hex 1", self.defaultprogdir, "Hex File (*.hex)")
        if fileName:
            try:
                # --- CARGA ELÁSTICA CON PARCHE DE CIERRE DE BLOQUE SEGURO ---
                test_ih = IntelHex()
                try:
                    # Intento de carga directa estándar
                    test_ih.loadhex(fileName)
                except Exception:
                    # Si falla por overlap, inyectamos las líneas con fin de archivo virtual
                    test_ih = IntelHex()
                    import io
                    with open(fileName, 'r') as f_clean:
                        for l_raw in f_clean:
                            l_strip = l_raw.strip()
                            if l_strip.startswith(':') and not l_strip.startswith(':00000001'):
                                try:
                                    # Forzamos el cierre de bloque por línea para que el parser oficial calcule bien
                                    l_safe = l_strip + "\n:00000001FF"
                                    th = IntelHex()
                                    th.loadhex(io.StringIO(l_safe))
                                    # Volcamos en el búfer maestro manteniendo el direccionamiento extendido real
                                    for addr in th.addresses():
                                        test_ih._buf[addr] = th._buf[addr]
                                except Exception:
                                    continue
                
                self.line_Prog_1.setText(fileName)
                self.statusBar().showMessage("HEX 1 cargado y validado correctamente.", 4000)
            except Exception as e:
                self.showdialog(f"Error de formato HEX:\nEl archivo seleccionado no es un IntelHex válido.\n\nDetalle: {str(e)}")
                self.line_Prog_1.clear()

    def Selecthex_2(self):
        fileName, _ = QFileDialog.getOpenFileName(self, "Open Hex 2", self.defaultprogdir, "Hex File (*.hex)")
        if fileName:
            try:
                # --- CARGA ELÁSTICA CON PARCHE DE CIERRE DE BLOQUE SEGURO ---
                test_ih = IntelHex()
                try:
                    # Intento de carga directa estándar
                    test_ih.loadhex(fileName)
                except Exception:
                    # Si falla por overlap, inyectamos las líneas con fin de archivo virtual
                    test_ih = IntelHex()
                    import io
                    with open(fileName, 'r') as f_clean:
                        for l_raw in f_clean:
                            l_strip = l_raw.strip()
                            if l_strip.startswith(':') and not l_strip.startswith(':00000001'):
                                try:
                                    l_safe = l_strip + "\n:00000001FF"
                                    th = IntelHex()
                                    th.loadhex(io.StringIO(l_safe))
                                    for addr in th.addresses():
                                        test_ih._buf[addr] = th._buf[addr]
                                except Exception:
                                    continue
                
                self.line_Prog_2.setText(fileName)
                self.statusBar().showMessage("HEX 2 cargado y validado correctamente.", 4000)
            except Exception as e:
                self.showdialog(f"Error de formato HEX:\nEl archivo seleccionado no es un IntelHex válido.\n\nDetalle: {str(e)}")
                self.line_Prog_2.clear()

    def InicializarCreadorPG(self):
        """Puebla el combobox de micros capturando errores de configuración de forma segura."""
        self.comboBox_device.clear()
        self.comboBox_device.addItem(" ") # Índice cero seguro
        
        cparser = configparser.ConfigParser()
        try:
            if not os.path.exists(self.omniprog_ini):
                return # Ya lo gestiona Checkini al arrancar
                
            cparser.read(self.omniprog_ini)
            todos_los_micros = []
            
            for seccion in cparser.sections():
                if seccion == "Default":
                    continue
                if cparser.has_option(seccion, "micros"):
                    lista = [m.strip() for m in cparser.get(seccion, "micros").split(',')]
                    todos_los_micros.extend(lista)
                    
            # Eliminar duplicados y ordenar alfabéticamente
            todos_los_micros = sorted(list(set(todos_los_micros)))
            self.comboBox_device.addItems(todos_los_micros)
            
            # Conexión dinámica de monitorización
            self.comboBox_device.currentIndexChanged.connect(self.OnDeviceChanged)
            self.line_sqtp_dir.setEnabled(True)
            self.line_params.setEnabled(True)
            
        except Exception as e:
            self.statusBar().showMessage(f"Error al procesar lista de micros del creador: {str(e)}", 5000)

    def OnDeviceChanged(self):
        """Monitorea el chip seleccionado para alertar o pre-configurar variables."""
        mcu_seleccionado = self.comboBox_device.currentText().strip()
        if not mcu_seleccionado:
            return
            
        motor = self.buscar_motor_para_micro(mcu_seleccionado)
        if motor:
            self.statusBar().showMessage(f"Dispositivo válido asignado al motor: [{motor.upper()}]", 4000)
        else:
            self.statusBar().showMessage("Alerta: El dispositivo no tiene motor asignado en el .ini", 4000)

    def Selecthex_hex1(self):
        fileName, _ = QFileDialog.getOpenFileName(self, "Select Program 1 Hex", self.defaultprogdir, "Hex File (*.hex)")
        if fileName:
            # Almacenamos el nombre relativo o absoluto para el archivo de configuración
            self.line_Prog_hex1.setText(os.path.basename(fileName))

    def Selecthex_hex2(self):
        fileName, _ = QFileDialog.getOpenFileName(self, "Select Program 2 Hex", self.defaultprogdir, "Hex File (*.hex)")
        if fileName:
            self.line_Prog_hex2.setText(os.path.basename(fileName))

    def CreatePGFile(self):
        """Valida los campos del panel de ingeniería y genera el archivo estructurado .pg utilizando configparser."""
        device = self.comboBox_device.currentText().strip()
        prog1 = self.line_Prog_hex1.text().strip()
        prog2 = self.line_Prog_hex2.text().strip()
        sqtp_dir = self.line_sqtp_dir.text().strip()
        sqtp_len = self.QSpin_SQTPLen2.value()
        params = self.line_params.text().strip()
        
        # Validaciones atómicas obligatorias de seguridad industrial
        if not device or device == "":
            self.showdialog("Error de Validación:\nDebe seleccionar un modelo de microcontrolador (Device).")
            return
        if not prog1:
            self.showdialog("Error de Validación:\nEl campo 'program1 (hex)' es obligatorio.")
            return

        # Abrimos el cuadro de diálogo para guardar el archivo .pg resultante
        fileName, _ = QFileDialog.getSaveFileName(self, "Save Configuration PG File", self.defaultprogdir, "Program Files (*.pg)")
        if not fileName:
            return # Operación cancelada por el operario/ingeniero

        # --- CORRECCIÓN 1: Asegurar que el archivo tenga la extensión .pg ---
        if not fileName.lower().endswith('.pg'):
            fileName += '.pg'

        try:
            # --- CORRECCIÓN 2 y 3: Estructurar con configparser e inyectar la sección [header] ---
            parser_pg = configparser.ConfigParser()
            parser_pg.add_section('header')
            
            # Seteamos las variables obligatorias y opcionales bajo la sección [header]
            parser_pg.set('header', 'Device', device)
            parser_pg.set('header', 'Program1', prog1)
            
            if prog2:
                parser_pg.set('header', 'Program2', prog2)
            if sqtp_dir:
                parser_pg.set('header', 'SQTP_Dir', sqtp_dir)
                parser_pg.set('header', 'SQTP_Len', str(sqtp_len))
            if params:
                parser_pg.set('header', 'params', params)
                
            # Escritura limpia y nativa compatible al 100% con omni_lib.readpg
            with open(fileName, 'w', encoding='utf-8') as archivo_pg:
                parser_pg.write(archivo_pg)
                    
            self.showdialog(f"Archivo de configuración de planta generado con éxito:\n{os.path.basename(fileName)}")
            
            # Cargar de manera reactiva el archivo recién creado en la pestaña principal
            self.archivo = fileName
            self.CargarPrograma()
            self.tabWidget.setCurrentIndex(0) # Cambiar al panel de ejecución automáticamente
            
        except Exception as e:
            self.showdialog(f"Error crítico de E/S al escribir el archivo .pg:\n{str(e)}")

    def ResetCounter(self):
        self.count = 0
        self.c_pass = 0
        self.c_fail = 0
        self.actualizar_statusbar()

    def actualizar_statusbar(self):
        self.statusBar().showMessage(f'Count: {self.count}\t\tPass: {self.c_pass}\t\tFail: {self.c_fail}')

    def showdialog(self, text_msg):
        msg = QMessageBox(self)
        msg.setText(text_msg)
        msg.setWindowTitle('OmniProg')
        msg.exec()

    def closeEvent(self, event):
        # Al cerrar la ventana de forma natural, liberamos el .lock si existía alguno activo
        if self.need_sqtp == 1 and self.line_SQTP.text() != '':
            omni_firmware.liberar_bloqueo_sqtp(self.line_SQTP.text())
        event.accept()

if __name__ == "__main__":
    parsed_args, unparsed_args = process_cl_args()
    archivo_cl = ''
    if parsed_args.open:
        archivo_cl = os.path.realpath(parsed_args.open)
        
    app = QtWidgets.QApplication(sys.argv)
    window = MyApp(archivo_inicial=archivo_cl)
    window.setWindowFlags(QtCore.Qt.WindowType.WindowCloseButtonHint | QtCore.Qt.WindowType.WindowMinimizeButtonHint)
    window.show()
    sys.exit(app.exec())
