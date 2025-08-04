import pandas as pd
from pathlib import Path
from datetime import datetime
from config import EXCEL_BBDD, NOMBRE_MI_EQUIPO, SALDO_INICIAL

def crear_excel_inicial(usuarios):
    """
    Crea el archivo Excel con hoja Principal e Historial.
    Inicializa saldo a 20M y fecha/hora vacía.
    """
    usuarios_filtrados = [u for u in usuarios if u != NOMBRE_MI_EQUIPO]

    df_principal = pd.DataFrame({
        "Nombre": usuarios_filtrados,
        "Nº jugadores": 0,
        "Saldo": SALDO_INICIAL,
        "Fecha/Hora": ""
    })

    df_historial = pd.DataFrame(columns=df_principal.columns)

    with pd.ExcelWriter(EXCEL_BBDD, engine="openpyxl") as writer:
        df_principal.to_excel(writer, index=False, sheet_name="Principal")
        df_historial.to_excel(writer, index=False, sheet_name="Historial")

def leer_excel():
    """
    Lee la hoja Principal y devuelve DataFrame.
    """
    if not EXCEL_BBDD.exists():
        return None
    df = pd.read_excel(EXCEL_BBDD, sheet_name="Principal")
    return df

def guardar_excel(df_principal):
    """
    Guarda la tabla principal y añade copia a Historial con fecha/hora actual.
    """
    fecha_ejecucion = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    df_principal.loc[:, "Fecha/Hora"] = fecha_ejecucion

    with pd.ExcelWriter(EXCEL_BBDD, engine="openpyxl", mode="a", if_sheet_exists="overlay") as writer:
        # Actualizar hoja Principal
        df_principal.to_excel(writer, index=False, sheet_name="Principal")

        # Leer hoja Historial
        df_historial = pd.read_excel(EXCEL_BBDD, sheet_name="Historial")

        # Añadir nuevo registro al Historial
        df_historial = pd.concat([df_historial, df_principal], ignore_index=True)

        # Guardar Historial actualizado
        df_historial.to_excel(writer, index=False, sheet_name="Historial")

def actualizar_saldo(df, movimientos):
    """
    Actualiza el saldo en df en base a movimientos dict {usuario: diferencia}.
    Suma o resta valores según sea venta o compra.
    """
    for usuario, diff in movimientos.items():
        if usuario in df["Nombre"].values:
            idx = df.index[df["Nombre"] == usuario][0]
            df.at[idx, "Saldo"] += diff
    return df
