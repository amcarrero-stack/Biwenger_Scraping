import time
import pandas as pd
from pathlib import Path
from datetime import datetime
from config import EXCEL_BBDD, NOMBRE_MI_EQUIPO, SALDO_INICIAL
from utils import log_message

import logging

# Crear carpeta logs si no existe
import os
os.makedirs("logs", exist_ok=True)

# Configuración general de logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("logs/mi_script.log", mode='a', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

# Subir el nivel de logging de librerías externas (Selenium, urllib3, etc.)
for logger_name in ['selenium', 'urllib3']:
    logging.getLogger(logger_name).setLevel(logging.WARNING)

def cargar_o_crear_excel(usuarios_actuales):
    """
    Carga Excel si existe, si no, crea con saldo inicial.
    Actualiza nombres si hay cambios detectados.
    """
    logging.debug(f'ExcelBBDD es: {EXCEL_BBDD}')

    if not EXCEL_BBDD.exists():
        log_message("No existe Excel. Creando archivo nuevo.")
        from excel_handler import crear_excel_inicial
        crear_excel_inicial(usuarios_actuales)
        df = pd.read_excel(EXCEL_BBDD, sheet_name="Principal")
        return df

    df = pd.read_excel(EXCEL_BBDD, sheet_name="Principal")


    # Detectar cambios de nombre
    nombres_excel = set(df["Nombre"].tolist())
    logging.debug(f'nombres_excel es: {df["Nombre"].tolist()}')
    nombres_actuales = set(usuarios_actuales)
    logging.debug(f'nombres_actuales es: {EXCEL_BBDD}')
    #
    # # Usuarios nuevos que no están en excel: añadir con saldo inicial
    nuevos = nombres_actuales - nombres_excel
    for usuario in nuevos:
        if usuario == NOMBRE_MI_EQUIPO:
            continue
        df = pd.concat([df, pd.DataFrame([{
            "Nombre": usuario,
            "Nº jugadores": 0,
            "Saldo": SALDO_INICIAL,
            "Fecha/Hora": ""
        }])], ignore_index=True)
        log_message(f"Usuario nuevo añadido: {usuario}")

    # Usuarios que desaparecieron (posible cambio de nombre)
    desaparecidos = nombres_excel - nombres_actuales
    if desaparecidos:
        log_message(f"Usuarios desaparecidos (posible cambio de nombre): {desaparecidos}")

    # Aquí podrías implementar lógica para detectar a qué usuarios nuevos corresponden estos cambios de nombre,
    # por ejemplo con heurísticas o una tabla de correspondencia guardada (pendiente de ampliar).

    # Finalmente, guardar cambios si hay alguno
    df.to_excel(EXCEL_BBDD, index=False, sheet_name="Principal")

    return df

def actualizar_datos_excel(df, movimientos, plantilla_por_usuario):
    """
    Aplica movimientos de saldo y actualiza nº jugadores en df.
    """
    # Actualizar saldo
    for usuario, diff in movimientos.items():
        if usuario in df["Nombre"].values:
            idx = df.index[df["Nombre"] == usuario][0]
            saldo_viejo = df.at[idx, "Saldo"]
            saldo_nuevo = saldo_viejo + diff
            df.at[idx, "Saldo"] = max(saldo_nuevo, 0)  # No saldo negativo
            log_message(f"Saldo actualizado {usuario}: {saldo_viejo} -> {df.at[idx, 'Saldo']}")

    # Actualizar nº jugadores según plantilla scrapeada
    for usuario, plantilla in plantilla_por_usuario.items():
        if usuario in df["Nombre"].values:
            idx = df.index[df["Nombre"] == usuario][0]
            total_jugadores = sum(len(jug_list) for jug_list in plantilla.values())
            df.at[idx, "Nº jugadores"] = total_jugadores
            log_message(f"Nº jugadores actualizado {usuario}: {total_jugadores}")

    # Actualizar fecha/hora ejecución actual
    fecha_ejecucion = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    df["Fecha/Hora"] = fecha_ejecucion

    # Guardar historial
    with pd.ExcelWriter(EXCEL_BBDD, engine="openpyxl", mode="a", if_sheet_exists="overlay") as writer:
        # Guardar hoja Principal
        df.to_excel(writer, index=False, sheet_name="Principal")

        # Leer historial
        df_historial = pd.read_excel(EXCEL_BBDD, sheet_name="Historial")
        df_historial = pd.concat([df_historial, df], ignore_index=True)
        df_historial.to_excel(writer, index=False, sheet_name="Historial")

    return df
