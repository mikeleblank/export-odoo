#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Convierte un dump SQL (MySQL/MariaDB) a un Excel con las columnas:
descripcion, codigo, precio, stock
uniendo codigo.idstock = stock.idstock.

Uso:
  python sql_to_excel.py --sql BACKUP.sql --out productos.xlsx
  # Extras (opcional):
  # --stock-table stock --codigo-table codigo

Requisitos:
  pip install pandas openpyxl
"""

import argparse
import re
import sys
from pathlib import Path

import pandas as pd


def parse_args():
    ap = argparse.ArgumentParser(
        description="Extrae descripcion/codigo/precio/stock desde un dump SQL y exporta a Excel."
    )
    ap.add_argument("--sql", required=True, help="Ruta al archivo .sql (dump)")
    ap.add_argument("--out", required=True, help="Ruta al .xlsx de salida")
    ap.add_argument("--csv", help="(Opcional) Ruta adicional para CSV")
    ap.add_argument("--stock-table", default="stock", help="Nombre de la tabla 'stock' (default: stock)")
    ap.add_argument("--codigo-table", default="codigo", help="Nombre de la tabla 'codigo' (default: codigo)")
    return ap.parse_args()


# ------------------------ PARSER DE INSERTS ------------------------ #
def extract_inserts(sql_text: str, table: str):
    """
    Devuelve una lista de dataframes para cada bloque INSERT INTO `table` (...) VALUES (...),(...);
    Soporta comillas simples y tuplas múltiples.
    """
    blocks = []
    # Captura: INSERT INTO `table` (cols) VALUES (tuplas...);
    rx = re.compile(rf"INSERT\s+INTO\s+`?{re.escape(table)}`?\s*\(([^)]+)\)\s*VALUES\s*(.*?);",
                    re.I | re.S)

    for m in rx.finditer(sql_text):
        cols_raw = m.group(1)
        body = m.group(2).strip()
        cols = [c.strip(" `") for c in cols_raw.split(",")]

        # separar tuplas top-level: (...) , (...) , ...
        tuples = []
        i, n = 0, len(body)
        in_str = False
        depth = 0
        while i < n:
            ch = body[i]
            if ch == "'" and (i == 0 or body[i - 1] != "\\"):
                in_str = not in_str
            elif ch == "(" and not in_str:
                depth = 1
                i += 1
                tbuf = ""
                while i < n and depth > 0:
                    c2 = body[i]
                    if c2 == "'" and body[i - 1] != "\\":
                        in_str = not in_str
                        tbuf += c2
                    elif not in_str and c2 == "(":
                        depth += 1
                        tbuf += c2
                    elif not in_str and c2 == ")":
                        depth -= 1
                        if depth == 0:
                            tuples.append(tbuf)
                            break
                        else:
                            tbuf += c2
                    else:
                        tbuf += c2
                    i += 1
            i += 1

        def split_fields(t):
            out, field, ins = [], "", False
            for j, ch in enumerate(t):
                if ch == "'" and (j == 0 or t[j - 1] != "\\"):
                    ins = not ins
                    field += ch
                elif ch == "," and not ins:
                    out.append(field.strip())
                    field = ""
                else:
                    field += ch
            out.append(field.strip())
            return out

        rows = []
        for tup in tuples:
            raw_fields = split_fields(tup)
            vals = []
            for v in raw_fields:
                v = v.strip()
                if v.upper() in ("NULL", "null"):
                    vals.append(None)
                elif v.startswith("'") and v.endswith("'"):
                    vals.append(v[1:-1].replace("\\'", "'"))
                else:
                    # intentar numérico
                    try:
                        if "." in v:
                            vals.append(float(v))
                        else:
                            vals.append(int(v))
                    except Exception:
                        vals.append(v)
            rows.append(vals)

        if rows:
            blocks.append(pd.DataFrame(rows, columns=cols))

    return blocks


def load_tables_from_sql(sql_path: Path, stock_table: str, codigo_table: str):
    text = sql_path.read_text(encoding="utf-8", errors="ignore")
    stock_blocks = extract_inserts(text, stock_table)
    codigo_blocks = extract_inserts(text, codigo_table)

    df_stock = pd.concat(stock_blocks, ignore_index=True) if stock_blocks else pd.DataFrame()
    df_codigo = pd.concat(codigo_blocks, ignore_index=True) if codigo_blocks else pd.DataFrame()

    return df_stock, df_codigo


def build_output(df_stock: pd.DataFrame, df_codigo: pd.DataFrame) -> pd.DataFrame:
    # Columnas mínimas esperadas
    need_stock_cols = ["idstock", "descripcion", "precio", "stock"]
    for col in need_stock_cols:
        if col not in df_stock.columns:
            raise SystemExit(
                f"[ERROR] No encuentro columna '{col}' en la tabla stock. "
                f"Columnas disponibles: {list(df_stock.columns)}"
            )

    if not {"idstock", "codigo"}.issubset(df_codigo.columns):
        raise SystemExit(
            f"[ERROR] La tabla codigo debe tener 'idstock' y 'codigo'. "
            f"Columnas disponibles: {list(df_codigo.columns)}"
        )

    # Unir por idstock (left para no perder productos sin código)
    df = (
        df_stock[["idstock", "descripcion", "precio", "stock"]]
        .merge(df_codigo[["idstock", "codigo"]], on="idstock", how="left")
        [["descripcion", "codigo", "precio", "stock"]]
        .copy()
    )
    return df


def main():
    args = parse_args()
    sql_path = Path(args.sql)
    out_xlsx = Path(args.out)

    if not sql_path.exists():
        print(f"[ERROR] No existe el archivo SQL: {sql_path}", file=sys.stderr)
        sys.exit(1)

    print(f"[INFO] Leyendo SQL: {sql_path}")
    df_stock, df_codigo = load_tables_from_sql(sql_path, args.stock_table, args.codigo_table)

    if df_stock.empty:
        print(f"[ERROR] No se extrajo ninguna fila de la tabla '{args.stock_table}'.", file=sys.stderr)
        sys.exit(2)
    if df_codigo.empty:
        print(f"[WARN] Tabla '{args.codigo_table}' sin filas. Continuo, pero algunos productos no tendrán código.")

    print(f"[INFO] Filas stock:  {len(df_stock)}  | columnas: {list(df_stock.columns)}")
    print(f"[INFO] Filas codigo: {len(df_codigo)}  | columnas: {list(df_codigo.columns)}")

    df_final = build_output(df_stock, df_codigo)

    # Exportar Excel
    print(f"[INFO] Exportando Excel: {out_xlsx}")
    with pd.ExcelWriter(out_xlsx, engine="openpyxl") as w:
        df_final.to_excel(w, index=False, sheet_name="Productos")

    # CSV opcional
    if args.csv:
        csv_path = Path(args.csv)
        print(f"[INFO] Exportando CSV: {csv_path}")
        df_final.to_csv(csv_path, index=False)

    print(f"[OK] Listo. Filas exportadas: {len(df_final)}")


if __name__ == "__main__":
    main()
