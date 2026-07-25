#! /usr/bin/python3
# License: GNU General Public License (GPL) v.3
import configparser
from os import path

# Usamos ConfigParser estándar
cparser = configparser.ConfigParser()

def readini(inifile, seccion, variable):
    """Lee variables del archivo ini lanzando excepciones controladas."""
    if not path.exists(inifile):
        raise FileNotFoundError(f"El archivo de configuración {inifile} no existe.")
        
    cparser.read(inifile)
    if cparser.has_section(seccion):
        if cparser.has_option(seccion, variable):
            return cparser.get(seccion, variable)
        else:
            raise KeyError(f"Variable '{variable}' no encontrada en la sección [{seccion}] dentro de {inifile}.")
    else:
        raise KeyError(f"Sección [{seccion}] no encontrada en el archivo {inifile}.")

def writeini(inifile, seccion, variable, valor):
    """Escribe variables en el archivo ini de forma segura."""
    cparser.read(inifile)
    if not cparser.has_section(seccion):
        cparser.add_section(seccion)
    cparser.set(seccion, variable, valor)
    with open(inifile, 'w', encoding='utf-8') as archivo:
        cparser.write(archivo)

def readpg(pgfile, variable):
    """Lee variables del archivo de configuración del microcontrolador (.pg)."""
    if not path.exists(pgfile):
        return (f"Error: El archivo {pgfile} no existe.", 0)
        
    parser_pg = configparser.ConfigParser()
    parser_pg.read(pgfile)
    
    if parser_pg.has_section('header'):
        if parser_pg.has_option('header', variable):
            return ('', parser_pg.get('header', variable))
        else:
            return (f"Error en readpg: Variable '{variable}' no encontrada en [header].", 0)
    else:
        return ("Error en readpg: No existe la sección [header] en el archivo .pg", 0)

def writevarini(inifile, seccion, variable, valor):
    """Escribe o actualiza una variable en una sección específica."""
    cparser.read(inifile)
    if cparser.has_section(seccion):
        cparser.set(seccion, variable, valor)
        with open(inifile, 'w', encoding='utf-8') as archivo:
            cparser.write(archivo)
    else:
        raise KeyError(f"Sección [{seccion}] no existe en {inifile} para actualizar la variable.")

def delvarcini(inifile, seccion, variable):
    """Elimina una variable de una sección."""
    cparser.read(inifile)
    if cparser.has_section(seccion): 
        if cparser.remove_option(seccion, variable):
            with open(inifile, 'w', encoding='utf-8') as archivo:
                cparser.write(archivo)
        else:
            raise KeyError(f"No se pudo eliminar la variable '{variable}' de la sección [{seccion}].")
    else:
        raise KeyError(f"Sección [{seccion}] no encontrada para eliminar variables.")
