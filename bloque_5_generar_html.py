from datetime import datetime
from pathlib import Path
from config import CARPETA_RESULTADOS
from utils import get_html_path

def generar_html(plantillas, saldos):
    """
    plantillas: dict de usuarios -> dict posiciones -> lista jugadores
    saldos: dict de usuarios -> saldo disponible (int)
    """

    fecha_hora = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    html_path = get_html_path()

    html_header = f"""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <title>Biwenger INFO</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                background-color: #f8f9fa;
                margin: 20px;
            }}
            header {{
                display: flex;
                justify-content: flex-end;
                color: red;
                font-weight: bold;
                margin-bottom: 20px;
            }}
            h1 {{
                text-align: center;
                margin-bottom: 30px;
            }}
            .card {{
                background: white;
                border-radius: 8px;
                box-shadow: 0 2px 5px rgba(0,0,0,0.15);
                padding: 15px;
                margin-bottom: 20px;
                width: 320px;
                display: inline-block;
                vertical-align: top;
                margin-right: 15px;
            }}
            .card h2 {{
                margin-top: 0;
                margin-bottom: 10px;
                font-size: 1.4em;
                border-bottom: 1px solid #ccc;
                padding-bottom: 5px;
            }}
            .position-group {{
                margin-bottom: 10px;
            }}
            .position-group strong {{
                display: block;
                margin-bottom: 5px;
                color: #333;
            }}
            ul {{
                list-style-type: none;
                padding-left: 10px;
                margin-top: 0;
                margin-bottom: 0;
            }}
            li {{
                margin-bottom: 3px;
            }}
            .saldo {{
                margin-top: 10px;
                font-weight: bold;
                color: #007bff;
            }}
        </style>
    </head>
    <body>
        <header>Última actualización: {fecha_hora}</header>
        <h1>Biwenger INFO</h1>
    """

    html_footer = """
    </body>
    </html>
    """

    # Crear las cards para cada usuario
    cards_html = ""
    for usuario, plantilla in plantillas.items():
        saldo_str = f"{saldos.get(usuario, 0):,.0f} €".replace(",", ".")
        card = f"<div class='card'>"
        card += f"<h2>{usuario}</h2>"
        for posicion in ["Porteros", "Defensas", "Centrocampistas", "Delanteros"]:
            jugadores = plantilla.get(posicion, [])
            card += f"<div class='position-group'><strong>{posicion}</strong><ul>"
            for jugador in jugadores:
                card += f"<li>{jugador}</li>"
            card += "</ul></div>"
        card += f"<div class='saldo'>Saldo: {saldo_str}</div>"
        card += "</div>"
        cards_html += card

    # Escribir el HTML completo
    html_completo = html_header + cards_html + html_footer
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html_completo)

    print(f"HTML generado en {html_path}")
