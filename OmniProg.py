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

import omni_lib
import omni_firmware
import omni_drivers

from PySide6 import QtCore, QtGui, QtWidgets
from PySide6.QtCore import QRegularExpression
from PySide6.QtGui import QPixmap, QRegularExpressionValidator
from PySide6.QtWidgets import QMessageBox, QFileDialog
from datetime import datetime
from intelhex import IntelHex
from pathlib import Path

# Importamos la interfaz moderna recién generada
from OmniProg_ui import Ui_MainWindow

VERSION = 'Ver: 1 (OmniProg)'

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
        self.omniprog_log = 'Error.log'
        self.lines = []
        self.puntero_lines = 0
        self.need_sqtp = 0
        self.driver_activo = ''  # Guardará 'flashmagic', 'IPECMD', etc.
        self.mcu_device = ''     # Modelo específico del micro extraído del .pg
        
        # Contadores aislados por ventana
        self.count = 0
        self.c_pass = 0
        self.c_fail = 0
        self.archivo = archivo_inicial
        
        # --- CONFIGURACIÓN E INICIALIZACIÓN ---
        self.Checkini()
        
        # Validación moderna hexadecimal de 8 dígitos para Qt6
        regex_hex = QRegularExpression('^[0-9A-Fa-f]{16}$')
        self.line_Num_Ini.setValidator(QRegularExpressionValidator(regex_hex, self))
        self.line_SQTPNumber.setValidator(QRegularExpressionValidator(regex_hex, self))
        self.line_sqtp_dir.setValidator(QRegularExpressionValidator(regex_hex, self))
        # Ejecuta la función una vez al inicio para aplicar la validación inicial
        #self.FormatoSQTP(self.QSpin_SQTPLen1.value())
        #self.Formatoline_Num_Ini(16)
        
        # --- CONEXIÓN DE EVENTOS GRÁFICOS ---
        self.Button_Generar.clicked.connect(self.Generar)
        self.Button_Prog.clicked.connect(self.OpenPrograma)
        self.Button_SQTP.clicked.connect(self.OpenSQTP)
        self.Button_program.clicked.connect(self.LaunchProgram)
        self.check_SQTPMan.stateChanged.connect(self.ManSQTP)
        self.Button_rescan.clicked.connect(self.RefreshPortList)
        
        self.Button_Prog_1.clicked.connect(self.Selecthex_1)
        self.Button_Prog_2.clicked.connect(self.Selecthex_2)
        self.Button_Merge.clicked.connect(self.Merge)
        self.Button_Compare.clicked.connect(self.CompararHexNativo)
        self.Button_C_Reset.clicked.connect(self.ResetCounter)

        self.QSpin_SQTPLen1.valueChanged.connect(self.Formatoline_Num_Ini)
        self.Button_Prog_hex1.clicked.connect(self.Selecthex_hex1)
        self.Button_createpg.clicked.connect(self.CreatePGFile)
        
        # Inicialización de entorno base
        self.actualizar_statusbar()
        
        # Si se abrió el software mediante doble clic en un archivo .pg
        if self.archivo != '':
            self.CargarPrograma()

        # Inicializar el combo del creador de archivos .pg leyendo el archivo .ini de planta
        self.InicializarCreadorPGdriver()

        # Inicializar el combo del creador de archivos .pg leyendo el archivo .ini de planta
        self.InicializarCreadorPGdevice()

    def Checkini(self):
        """Inicializa las rutas buscando de forma segura los parámetros base en el archivo .ini."""
        carpeta_del_exe = os.path.dirname(os.path.realpath(sys.argv[0]))
        self.omniprog_ini = os.path.join(carpeta_del_exe, 'OmniProg.ini')
        self.omniprog_log = os.path.join(carpeta_del_exe, 'Error.log')        
        try:
            # Reutilizamos la función robustecida de omni_lib
            self.defaultprogdir = omni_lib.readini(self.omniprog_ini, "Default", "defaultprogdir")
            self.defaultsqtpdir = omni_lib.readini(self.omniprog_ini, "Default", "defaultsqtpdir")
        except FileNotFoundError as e:
            self.showdialog(f"Falta el archivo de configuración obligatorio:\n{str(e)}")
            sys.exit(1)
        except KeyError as e:
            self.showdialog(f"Error crítico de inicialización:\n{str(e)}\n\nPor favor, revise el archivo .ini.")
            sys.exit(1)

    def RefreshPortList(self):
        """
        Rutina universal agnóstica al fabricante.
        #La llamada a esta rutina puede venir del boton refrescar o de la carga de un archivo pg.
        Si hay programa programa solo cargaremos los dispositivos validos para el driver. 
        """
        self.Button_rescan.setEnabled(False)
        QtWidgets.QApplication.processEvents()
        
        self.comboBoxPort.clear()
        self.comboBoxPort.addItem(' ') # Índice cero vacío por seguridad

        tipo_driver = "serial"
        executable_path = ""
        if (self.archivo):
            _, self.driver_activo = omni_lib.readpg(self.archivo, 'Driver')
            tipo_driver = omni_lib.readini(self.omniprog_ini, self.driver_activo, "com_method").strip()
            executable_path = omni_lib.readini(self.omniprog_ini, self.driver_activo, "path").replace('"', '')
                
        # --- TRAZAS DE DEPURACIÓN EN INTERFAZ ---
        self.textEdit.clear()
        self.textEdit.append("=== REFRESH PORTS ===")
        self.textEdit.append(f"Driver Activo detectado: {self.driver_activo}")
        self.textEdit.append(f"Tipo de Driver a escanear: {tipo_driver}")
        self.textEdit.append(f"Ruta del Ejecutable asignada: {executable_path if executable_path else 'N/A (Serial Puro)'}")
        QtWidgets.QApplication.processEvents()

        try:
            lista_dispositivos = omni_drivers.escanear_hardware(tipo_driver, executable_path)
            
            if lista_dispositivos:
                self.comboBoxPort.addItems(lista_dispositivos)
                self.textEdit.append(f"Hardware Encontrado con éxito: {lista_dispositivos}")
            else:
                self.textEdit.append("Resultado del escaneo: No se detectó ningún hardware activo.")
                        
        except Exception as e:
            self.showdialog(f"Error durante el escaneo de hardware: {str(e)}")
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

    def Formatoline_Num_Ini(self, valor):
        self.line_Num_Ini.clear()
        caracteres_hex = valor * 2
        # Genera el regex dinámicamente con la cantidad de caracteres actual del QSpinBox
        regex_dinamico = f'^[0-9A-Fa-f]{{{caracteres_hex}}}$'
        # Crea y aplica el nuevo validador
        regex_hex = QRegularExpression(regex_dinamico)
        self.line_Num_Ini.setValidator(QRegularExpressionValidator(regex_hex, self))

    def FormatoSQTP(self, valor):
        caracteres_hex = valor * 2
        #print ('len:',len(self.line_SQTPNumber.text()),'\t',caracteres_hex)
        if (len(self.line_SQTPNumber.text()) != caracteres_hex):
            self.line_SQTPNumber.setText('0' * caracteres_hex)
        regex_dinamico = f'^[0-9A-Fa-f]{{{caracteres_hex}}}$'
        # Crea y aplica el nuevo validador
        regex_hex = QRegularExpression(regex_dinamico)
        self.line_SQTPNumber.setValidator(QRegularExpressionValidator(regex_hex, self))

    def ManSQTP(self):
        if self.check_SQTPMan.isChecked():
            self.FormatoSQTP(self.QSpin_SQTPLen1.value())
            self.line_SQTPNumber.setEnabled(True)
        else:
            self.line_SQTPNumber.setEnabled(False)
            if self.line_SQTP.text() != '':
                self.SQTP(self.line_SQTP.text())
        self.Activar_Prog()

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
            # Cargar de manera reactiva el archivo recién creado en la pestaña principal
            self.SQTP(resultado)
            self.CargarPrograma()
            self.tabWidget.setCurrentIndex(0) # Cambiar al panel de ejecución automáticamente
            #self.showdialog(f"Archivo de producción generado con éxito en:\n{resultado}")
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
        # Extraemos el número de serie de forma habitual
        resultado = omni_firmware.extraer_siguiente_sqtp(fileName)
        self.lines, self.puntero_lines, numero_serie = resultado
        if numero_serie:
            if (len(numero_serie) == (self.need_sqtp * 2)):
                self.line_SQTPNumber.setText(numero_serie)
                self.line_SQTP.setText(fileName)
                if len(self.archivo) > 0:
                    self.Button_program.setEnabled(True)
            else:
                self.showdialog("Warning! Este archivo no tiene el numero de bytes correcto.")
                self.line_SQTPNumber.clear()
                self.line_SQTP.clear()
                self.check_SQTPMan.setChecked(False)
                self.Activar_Prog()
        else:
            self.showdialog("Warning! Este archivo no contiene números SQTP libres.")
            self.line_SQTPNumber.clear()
            self.line_SQTP.clear()
            self.check_SQTPMan.setChecked(False)
            self.Activar_Prog()

    def Activar_Prog(self):
        """Controla el estado del botón PROGRAM."""
        # Validación base de requisitos
        if os.path.exists(self.archivo) and self.comboBoxPort.currentIndex() > 0:
            self.Button_program.setEnabled(True)
            if (self.need_sqtp != 0) and (not os.path.exists(self.line_SQTP.text())) and (not self.check_SQTPMan.isChecked()):
                self.Button_program.setEnabled(False)
        else:
            self.Button_program.setEnabled(False)

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
                                             f"Prog1 = 0x{byte1:02X} | 0x{byte2:02X} = Prog2")
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
        #Primero comparamos los archivos.
        self.CompararHexNativo()
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
                # 1. Intentar cargar el archivo directamente con el parser oficial
                test_ih = IntelHex()
                test_ih.loadhex(fileName)
                
                # 2. Si pasa la línea anterior sin lanzar excepción, el archivo es 100% válido.
                # Cargamos la ruta en el campo de texto y avisamos en el status bar.
                self.line_Prog_1.setText(fileName)
                self.statusBar().showMessage("HEX 1 cargado y validado correctamente.", 4000)

            except Exception as e:
                # 3. Si el parser encuentra CUALQUIER fallo (overlap, fin de archivo ausente, sintaxis), salta aquí.
                # Muestra el diálogo de error y limpia el campo para mayor seguridad.
                self.showdialog(f"Error de formato HEX:\nEl archivo seleccionado no cumple con el estándar IntelHex válido.\n\nDetalle: {str(e)}")
                self.line_Prog_1.clear()

    def Selecthex_2(self):
        fileName, _ = QFileDialog.getOpenFileName(self, "Open Hex 2", self.defaultprogdir, "Hex File (*.hex)")
        if fileName:
            try:
                # 1. Intentar cargar el archivo directamente con el parser oficial
                test_ih = IntelHex()
                test_ih.loadhex(fileName)
                
                # 2. Si pasa la línea anterior sin lanzar excepción, el archivo es 100% válido.
                # Cargamos la ruta en el campo de texto y avisamos en el status bar.
                self.line_Prog_2.setText(fileName)
                self.statusBar().showMessage("HEX 2 cargado y validado correctamente.", 4000)

            except Exception as e:
                # 3. Si el parser encuentra CUALQUIER fallo (overlap, fin de archivo ausente, sintaxis), salta aquí.
                # Muestra el diálogo de error y limpia el campo para mayor seguridad.
                self.showdialog(f"Error de formato HEX:\nE2 archivo seleccionado no cumple con el estándar IntelHex válido.\n\nDetalle: {str(e)}")
                self.line_Prog_2.clear()

    def InicializarCreadorPGdriver(self):
        """Puebla el combobox de driver capturando errores de configuración."""
        self.comboBox_driver.clear()
        self.comboBox_driver.addItem(" ")

        try:
            self.comboBox_driver.addItems(
                omni_lib.getsections(self.omniprog_ini, excluir=["Default"])
            )
        except Exception as e:
            self.showdialog(
                f"Error al procesar lista de drivers del creador: {e}"
            )

    def InicializarCreadorPGdevice(self):
        self.comboBox_device.clear()
        self.comboBox_device.addItem(" ")

        try:
            self.comboBox_device.addItems(omni_lib.getdevices(self.omniprog_ini))
        except Exception as e:
            self.showdialog(
                f"Error al procesar lista de microcontroladores del creador: {e}"
            )


    def Selecthex_hex1(self):
        fileName, _ = QFileDialog.getOpenFileName(self, "Select Program 1 Hex", self.defaultprogdir, "Hex File (*.hex)")
        if fileName:
            # Almacenamos el nombre relativo o absoluto para el archivo de configuración
            self.line_Prog_hex1.setText(os.path.basename(fileName))

    def CreatePGFile(self):
        """Valida los campos del panel de ingeniería y genera el archivo estructurado .pg
           Ejemplo de archivo pg: Program / Driver / Device / Params / SQTP_Dir / SQTP_Len"""
        prog1 = self.line_Prog_hex1.text().strip()
        driver = self.comboBox_driver.currentText().strip()
        device = self.comboBox_device.currentText().strip()
        params = self.line_params.text().strip()
        sqtp_dir = self.line_sqtp_dir.text().strip()
        sqtp_len = self.QSpin_SQTPLen2.value()
        
        # Validaciones atómicas obligatorias de seguridad industrial
        if not driver or driver == "":
            self.showdialog("Error de Validación:\nDebe seleccionar un driver.")
            return
        if not device or device == "":
            self.showdialog("Error de Validación:\nDebe seleccionar un modelo de microcontrolador (Device).")
            return
        if not prog1:
            self.showdialog("Error de Validación:\nEl campo 'program (hex)' es obligatorio.")
            return

        # Abrimos el cuadro de diálogo para guardar el archivo .pg resultante
        fileName, _ = QFileDialog.getSaveFileName(self, "Save Configuration PG File", self.defaultprogdir, "Program Files (*.pg)")
        if not fileName:
            return # Operación cancelada por el operario/ingeniero

        # --- CORRECCIÓN 1: Asegurar que el archivo tenga la extensión .pg ---
        if not fileName.lower().endswith('.pg'):
            fileName += '.pg'

        try:
            omni_lib.writepg(fileName, 'header', 'Program', prog1)
            omni_lib.writepg(fileName, 'header', 'driver', driver)
            omni_lib.writepg(fileName, 'header', 'Device', device)
            if sqtp_dir:
                omni_lib.writepg(fileName, 'header', 'SQTP_Dir', sqtp_dir)
                omni_lib.writepg(fileName, 'header', 'SQTP_Len', str(sqtp_len))
            if params:
                omni_lib.writepg(fileName, 'header', 'params', params)
                
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

    def CargarPrograma(self): 
        # Esta subrutina se ejecuta al recibir un archivo pg y su mision es comprobar que disponemos de los datos necesarios
        # Ejemplo de archivo pg:        
        #Program / Driver / Device / Params / SQTP_Dir / SQTP_Len
        try:
            # 1. Leer variables del archivo .pg de manera preventiva
            _, p_Program = omni_lib.readpg(self.archivo, 'Program')
            _, p_Driver = omni_lib.readpg(self.archivo, 'Driver')
            _, p_Device = omni_lib.readpg(self.archivo, 'Device')
            _, p_Params = omni_lib.readpg(self.archivo, 'Params')
            _, p_SQTP_Len = omni_lib.readpg(self.archivo, 'SQTP_Len')
            mensaje, p_SQTP_Dir = omni_lib.readpg(self.archivo, 'SQTP_Dir')
            # Analizar si requiere SQTP
            mensaje, valor = omni_lib.readpg(self.archivo, 'SQTP_Dir')
            self.need_sqtp = 0 if mensaje else 1
            # Configuramos el entorno grafico
            if self.need_sqtp == 0:
                self.Button_SQTP.setEnabled(False)
                self.check_SQTPMan.setEnabled(False)
                self.line_SQTP.clear()
                self.line_SQTPNumber.clear()
                self.line_SQTPNumber.setEnabled(False)
                self.line_Prog.setText(self.archivo)
                self.check_SQTPMan.setChecked(False)
            else:
                self.Button_SQTP.setEnabled(True)
                self.check_SQTPMan.setEnabled(True)
                self.line_Prog.setText(self.archivo)
                self.FormatoSQTP(int(p_SQTP_Len))
                self.need_sqtp = int(p_SQTP_Len)
        except Exception as e:
            self.showdialog(f"Error al cargar el archivo .pg:\n{str(e)}")

        # Cambiar el directorio de trabajo a la carpeta donde reside el archivo pg.
        if self.archivo and os.path.exists(self.archivo):
            os.chdir(os.path.dirname(os.path.realpath(self.archivo)))

        # Sincronizamos la lista de grabadores y validamos requisitos finales de la pestaña principal
        self.RefreshPortList()
        self.precarga_tools(p_Program, p_Driver, p_Device, p_Params, p_SQTP_Len, p_SQTP_Dir)
        self.Activar_Prog()

    def precarga_tools(self, p_Program, p_Driver, p_Device, p_Params, p_SQTP_Len, p_SQTP_Dir):
        try:
            # 1. Bloque SQTP Generate: Sincronizar 'Length (Bytes)'
            if p_SQTP_Len and str(p_SQTP_Len).strip().isdigit():
                self.QSpin_SQTPLen1.setValue(int(str(p_SQTP_Len).strip()))
            # 2. Bloque Create PG File
            # Buscamos si el driver del .pg existe en el combobox para seleccionarlo
            idx_device = self.comboBox_driver.findText(p_Driver)
            if idx_device >= 0:
                self.comboBox_driver.setCurrentIndex(idx_device)
            # Buscamos si el dispositivo del .pg existe en el combobox para seleccionarlo
            idx_device = self.comboBox_device.findText(p_Device)
            if idx_device >= 0:
                self.comboBox_device.setCurrentIndex(idx_device)
            # Sincronizar 'sqtp_dir'
            if p_SQTP_Dir and str(p_SQTP_Dir).strip() != '0':
                self.line_sqtp_dir.setText(str(p_SQTP_Dir).strip())
            else:
                self.line_sqtp_dir.clear()
            # Sincronizar 'sqtp_len'
            if p_SQTP_Len and str(p_SQTP_Len).strip().isdigit():
                self.QSpin_SQTPLen2.setValue(int(str(p_SQTP_Len).strip()))
            else:
                self.QSpin_SQTPLen2.setValue(1) # Valor mínimo por defecto de la UI
            # Sincronizar 'params'
            if p_Params and str(p_Params).strip() != '0':
                self.line_params.setText(str(p_Params).strip())
            else:
                self.line_params.clear()
            # [Opcional de regalo] Sincronizar también los campos de firmware del creador para dejarlo impecable
            if p_Program and str(p_Program).strip() != '0':
                self.line_Prog_hex1.setText(str(p_Program).strip())
            else:
                self.line_Prog_hex1.clear()
        except Exception as e:
            self.textEdit.append(f"-> Error menor al preconfigurar la pestaña Tools: {str(e)}")

    def LaunchProgram(self):
        self.Button_program.setEnabled(False)
        # Comprobacion extra para los SQTP
        if self.line_SQTPNumber.text() == '' and self.need_sqtp != 0:
            self.label_PASS.setText('INVALID SQTP')
            self.Button_program.setEnabled(True)
            return

        # 1. RESETEAR ESTILO AL INICIAR: Quita el color anterior mientras se graba el chip
        self.textEdit.clear()
        self.label_PASS.setStyleSheet("") 
        self.label_PASS.setText("Prep. PROGRAMING...")
        self.textEdit.append(f"Driver activo: {self.driver_activo}")

        # 2. RECOPILAMOS DATOS
        # Extraer parámetros del OmniProg.ini
        tipo_driver = omni_lib.readini(self.omniprog_ini, self.driver_activo, "com_method").strip()
        executable_path = omni_lib.readini(self.omniprog_ini, self.driver_activo, "path").replace('"', '')
        returncode_ok = str(omni_lib.readini(self.omniprog_ini, self.driver_activo, "returncode_ok"))
        returncode_bad = str(omni_lib.readini(self.omniprog_ini, self.driver_activo, "returncode_bad"))
        # Recopilamos los datos del archivo pg
        _, nombre_hex = omni_lib.readpg(self.archivo, 'Program')
        carpeta_proyecto = os.path.dirname(os.path.realpath(self.archivo))
        hex_target = os.path.abspath(os.path.join(carpeta_proyecto, nombre_hex.strip()))
        _, self.mcu_device = omni_lib.readpg(self.archivo, 'device')        
        # Extraer parámetros específicos de la placa desde el archivo de configuración .pg
        _, params_pg = omni_lib.readpg(self.archivo, 'Params')
        params_pg_clean = params_pg.strip() if params_pg else ''
        params_ini = {}
        params_ini['path'] = omni_lib.readini(self.omniprog_ini, self.driver_activo, "path")
        params_ini['linea_comando'] = omni_lib.readini(self.omniprog_ini, self.driver_activo, "linea_comando")
        num_result = ''
        program_name = Path(self.archivo).stem

        # 2. Si necesitamos SQTP
        if self.need_sqtp != 0:
            print('NEED SQTP')
            SQTP_method = omni_lib.readini(self.omniprog_ini, self.driver_activo, "SQTP_method")
            _, sqtp_dir = omni_lib.readpg(self.archivo, 'SQTP_Dir')
            _, sqtp_len = omni_lib.readpg(self.archivo, 'SQTP_Len')
            _, device = omni_lib.readpg(self.archivo, 'device')
            if (SQTP_method == 'inject'):
                print ('inject')
                nombre_result = 'result.hex'
                carpeta_proyecto = os.path.dirname(os.path.realpath(self.archivo))
                hex_result = os.path.abspath(os.path.join(carpeta_proyecto, nombre_result.strip()))
                omni_firmware.inyectar_sqtp(hex_target, sqtp_dir, sqtp_len, self.line_SQTPNumber.text(), hex_result)
                hex_target = hex_result
            elif (SQTP_method == 'file'):
                print ('file')
                nombre_result = 'sqtp_temp.num'
                carpeta_proyecto = os.path.dirname(os.path.realpath(self.archivo))
                num_result = os.path.abspath(os.path.join(carpeta_proyecto, nombre_result.strip()))
                try:
                    # Intentamos generar el archivo temporal para ipecmd
                    omni_firmware.generar_archivo_intel_hex_sqtp(sqtp_dir, sqtp_len, self.line_SQTPNumber.text(), num_result, device)
                except (ValueError, RuntimeError) as e:
                    return
            else:
                self.label_PASS.setText('INVALID SQTP METHOD')
                self.Button_program.setEnabled(True)
            self.textEdit.append(f"Num/File SQTP creating\n")
            time.sleep(1.5)
        else:
            print('NO NEED SQTP')
        
        # 3. LLAMADA UNIVERSAL AL GESTOR DE DRIVERS BASADO EN PLANTILLAS %
        target_hardware = self.comboBoxPort.currentText()
        comando_args, use_shell = omni_drivers.preparar_comando_consola(
            tipo_driver, 
            executable_path, 
            self.mcu_device, 
            target_hardware, 
            hex_target,
            params_ini, 
            params_pg_clean,
            num_result,
            program_name
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
            self.textEdit.append(f"Returncode: {returncode}\n")
        except Exception as e:
            self.textEdit.append(f"\nExecution Fail: {str(e)}")
            return

        # 5. EVALUACIÓN Y GESTIÓN DE CONTADORES EN PLANTA ---
        texto_consola_completo = self.textEdit.toPlainText().upper()

        # Filtro de seguridad: error de código o palabras clave en la consola
        result = self.evaluar_resultado_programacion(returncode, texto_consola_completo, returncode_ok, returncode_bad)
        if (result == 0):
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
            
            if self.need_sqtp != 0 and not self.check_SQTPMan.isChecked():
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
            # Escribimos en un log
            self.guardar_log(texto_consola_completo)
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


    def evaluar_resultado_programacion(self, returncode, texto_consola, texto_ok, texto_mal):
        print("texto_consola:\n", str(texto_consola))
        print("texto_ok:", texto_ok.upper())
        print("texto_mal:", texto_mal.upper())
        print("returncode:", returncode)
        """
        Evalúa el éxito de la programación (0 = Éxito, 1 = Fallo).
        Fuerza el éxito si el texto_ok está presente y es posterior al texto_mal.
        """
        # 1. Buscar las últimas posiciones de los textos (-1 si no existen)
        pos_ok = texto_consola.rfind(texto_ok.upper())
        print(f"Find Texto Pass: {str(pos_ok)}")
        pos_mal = texto_consola.rfind(texto_mal.upper())
        print(f"Find Texto Fail: {str(pos_mal)}")
        encontrado_ok = pos_ok != -1
        encontrado_mal = pos_mal != -1
        self.textEdit.append(f"ok: {str(pos_ok)} bad: {str(pos_mal)}")
        if (encontrado_ok >= encontrado_mal):
            texto = 0 #texto bien al final
        else:
            texto = 1 #texto mal al final
        if returncode == 0  and texto == 0:
            return 0
        elif returncode == 0  and texto == 1:
            return 1
        elif returncode != 0  and texto == 0:
            return 0
        elif returncode != 0  and texto == 1:
            return 1


    def guardar_log(self, texto_consola):
        """
        Guarda el texto de la consola en un archivo 'errores.log' 
        antecediendo la fecha y hora en formato AAAA/MM/DD HH:MM:SS.
        """
        self.textEdit.append(f"Log: {self.omniprog_log}\n")
        # 1. Obtener la fecha y hora actual en el formato deseado
        ahora = datetime.now()
        fecha_formateada = ahora.strftime("%Y/%m/%d %H:%M:%S")
        
        # 2. Abrir el archivo en modo 'a' (append / añadir al final) con codificación UTF-8
        with open(self.omniprog_log, "a", encoding="utf-8") as archivo:
            # Escribimos el encabezado con la fecha
            archivo.write(f"\n========================================\n")
            archivo.write(f"REGISTRO: {fecha_formateada}\n")
            archivo.write(f"========================================\n")
            
            # Escribimos el volcado de la consola
            archivo.write(texto_consola)
            archivo.write("\n") # Un salto de línea final para separar del siguiente registro


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
