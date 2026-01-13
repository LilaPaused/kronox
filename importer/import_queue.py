from __future__ import annotations

import re
from datetime import datetime
from typing import Dict, List, Tuple

import gspread
from google.oauth2.service_account import Credentials

# -----------------------
# CONFIG
# -----------------------
SPREADSHEET_ID = "1VQjhaEX7iUVmhPsNyIHlWtRrgx_zgbXMsYWJoTNGjDc"  # el ID del Google Sheet
SHEET_REGISTRO = "Registro"
SHEET_QUEUE = "INPUT_QUEUE"

REGISTRO_DATE_RANGE = "B2:B783"  # diaTurno
# Columnas en Registro
COL_CLAVE = "A"
COL_EXTRAS_ANTES = "C"
COL_EXTRAS_DESPUES = "D"

# Columnas en INPUT_QUEUE (por índice 1-based)
# A timestamp, B diaTurno, C claveHoraria, D extrasAntes, E extrasDespues, F source, G status, H error_msg
QUEUE_COL_DATE = 2
QUEUE_COL_CLAVE = 3
QUEUE_COL_ANTES = 4
QUEUE_COL_DESPUES = 5
QUEUE_COL_STATUS = 7
QUEUE_COL_ERR = 8


import re

def normalize_time_hhmm(s: str) -> str:
    if not s:
        return ""

    s = str(s).strip()

    # Acepta H:MM o HH:MM
    if re.fullmatch(r"\d{1,2}:\d{2}", s):
        h, m = s.split(":")
        h = int(h)
        m = int(m)
        if 0 <= h <= 23 and 0 <= m <= 59:
            return f"{h:02d}:{m:02d}"

    raise ValueError(f"extras inválido: {s}")

def is_time_hhmm(s: str) -> bool:
    """Compatibilidad: devuelve True/False, pero acepta H:MM también."""
    try:
        normalize_time_hhmm(s)
        return True
    except ValueError:
        return False


def normalize_date_ddmmyyyy(s: str) -> str:
    """
    Acepta DD/MM/YYYY o YYYY-MM-DD y devuelve DD/MM/YYYY.
    """
    s = (s or "").strip()
    if not s:
        raise ValueError("diaTurno vacío")

    # DD/MM/YYYY
    if re.fullmatch(r"\d{2}/\d{2}/\d{4}", s):
        # valida fecha real
        datetime.strptime(s, "%d/%m/%Y")
        return s

    # YYYY-MM-DD
    if re.fullmatch(r"\d{4}-\d{2}-\d{2}", s):
        dt = datetime.strptime(s, "%Y-%m-%d")
        return dt.strftime("%d/%m/%Y")

    raise ValueError(f"Formato de fecha inválido: {s}")


def build_registro_date_index(ws_registro) -> Dict[str, int]:
    """
    Devuelve dict: "DD/MM/YYYY" -> row_number en Registro
    """
    dates = ws_registro.get(REGISTRO_DATE_RANGE)  # lista de listas [[val], [val]...]
    index: Dict[str, int] = {}
    start_row = 2
    for i, row in enumerate(dates):
        raw = (row[0] if row else "") or ""
        raw = str(raw).strip()
        if not raw:
            continue
        # aquí asumimos que la celda ya está formateada como DD/MM/YYYY
        # si viniera como serial, habría que leer formatted values via API avanzada;
        # con gspread normalmente te devuelve el display.
        try:
            ddmmyyyy = normalize_date_ddmmyyyy(raw)
        except Exception:
            # si hay algo raro, lo ignoramos
            continue
        index[ddmmyyyy] = start_row + i
    return index


def main():
    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive",
    ]
    creds = Credentials.from_service_account_file("service_account.json", scopes=scopes)
    gc = gspread.authorize(creds)

    sh = gc.open_by_key(SPREADSHEET_ID)
    ws_registro = sh.worksheet(SHEET_REGISTRO)
    ws_queue = sh.worksheet(SHEET_QUEUE)

    # 1) Index de fechas de Registro
    date_to_row = build_registro_date_index(ws_registro)

    # 2) Leer toda la cola (fila 2 en adelante)
    queue_values = ws_queue.get_all_values()
    if len(queue_values) <= 1:
        print("INPUT_QUEUE vacía.")
        return

    headers = queue_values[0]
    rows = queue_values[1:]

    registro_updates: List[gspread.Cell] = []
    queue_status_updates: List[gspread.Cell] = []
    queue_error_updates: List[gspread.Cell] = []

    for idx0, r in enumerate(rows):
        sheet_row = idx0 + 2  # porque headers en fila 1

        status = (r[QUEUE_COL_STATUS - 1] if len(r) >= QUEUE_COL_STATUS else "").strip()
        if status:  # ya procesada
            continue

        dia_raw = r[QUEUE_COL_DATE - 1] if len(r) >= QUEUE_COL_DATE else ""
        clave = (r[QUEUE_COL_CLAVE - 1] if len(r) >= QUEUE_COL_CLAVE else "").strip()
        antes = normalize_time_hhmm(
            r[QUEUE_COL_ANTES - 1] if len(r) >= QUEUE_COL_ANTES else ""
            )
        despues = normalize_time_hhmm(
            r[QUEUE_COL_DESPUES - 1] if len(r) >= QUEUE_COL_DESPUES else ""
            )

        try:
            dia = normalize_date_ddmmyyyy(dia_raw)
            if not clave:
                raise ValueError("claveHoraria vacía")
            if not is_time_hhmm(antes):
                raise ValueError(f"extrasAntes inválido: {antes}")
            if not is_time_hhmm(despues):
                raise ValueError(f"extrasDespues inválido: {despues}")

            if dia not in date_to_row:
                raise ValueError(f"diaTurno {dia} no existe en Registro (B2:B783)")

            reg_row = date_to_row[dia]

            # Preparar celdas a actualizar en Registro (A, C, D)
            registro_updates.append(gspread.Cell(reg_row, 1, clave))      # A
            registro_updates.append(gspread.Cell(reg_row, 3, antes))      # C
            registro_updates.append(gspread.Cell(reg_row, 4, despues))    # D

            # Marcar OK en cola
            queue_status_updates.append(gspread.Cell(sheet_row, QUEUE_COL_STATUS, "OK"))
            queue_error_updates.append(gspread.Cell(sheet_row, QUEUE_COL_ERR, ""))

        except Exception as e:
            queue_status_updates.append(gspread.Cell(sheet_row, QUEUE_COL_STATUS, "ERROR"))
            queue_error_updates.append(gspread.Cell(sheet_row, QUEUE_COL_ERR, str(e)))

    # 3) Escribir en lote (MUY importante para eficiencia)
    if registro_updates:
        ws_registro.update_cells(registro_updates, value_input_option="USER_ENTERED")

    if queue_status_updates:
        ws_queue.update_cells(queue_status_updates, value_input_option="RAW")
        ws_queue.update_cells(queue_error_updates, value_input_option="RAW")

    print("Procesado OK.")


if __name__ == "__main__":
    main()
