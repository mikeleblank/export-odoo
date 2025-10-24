# 🧾 SQL ➜ Excel Exporter  
![Python](https://img.shields.io/badge/Python-3.9%2B-blue.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)
![Build](https://img.shields.io/badge/Status-Stable-success.svg)

Convierte fácilmente tus respaldos `.sql` en hojas de cálculo `.xlsx` o `.csv` organizadas.  
Ideal para migrar datos de inventario, productos y códigos de barra a sistemas como **Odoo**, **ERPNext** o **Dolibarr**.

---

## 🚀 Características
✅ Extrae datos automáticamente desde archivos `.sql`.  
✅ Exporta a **Excel (.xlsx)** y/o **CSV (.csv)**.  
✅ Permite definir tablas personalizadas (stock, códigos de barras, precios).  
✅ Ligero, portable y rápido: solo requiere `pandas` y `openpyxl`.

---

## ⚙️ Requisitos

**Python 3.9 o superior**  
Dependencias: `pandas`, `openpyxl`

### 🔧 Instalación de dependencias

**Linux / macOS**
```bash
python -m venv .venv
source .venv/bin/activate
pip install -U pip
pip install pandas openpyxl
```

**Windows (PowerShell)**
```bash
python -m venv .venv
.venv\Scripts\activate
pip install -U pip
pip install pandas openpyxl
```

---

## ▶️ Uso básico

```bash
python sql_to_excel.py --sql "BACKUP.sql" --out "productos.xlsx"
```

Esto generará un archivo Excel con todos los productos, códigos, precios y stock detectados.

---

## 💾 Exportar también a CSV

```bash
python sql_to_excel.py --sql "BACKUP.sql" --out "productos.xlsx" --csv "productos.csv"
```

Obtendrás ambos archivos: `productos.xlsx` y `productos.csv`.

---

## ⚙️ Parámetros personalizados

Si tus tablas no se llaman exactamente `stock` y `codigo`, podés especificarlas:

```bash
python sql_to_excel.py --sql BACKUP.sql --out productos.xlsx \
  --stock-table stock_productos --codigo-table codigos_barras
```

| Parámetro | Descripción | Ejemplo |
|------------|-------------|----------|
| `--sql` | Archivo SQL de entrada | `BACKUP.sql` |
| `--out` | Archivo Excel de salida | `productos.xlsx` |
| `--csv` | (Opcional) Exporta también a CSV | `productos.csv` |
| `--stock-table` | Nombre de la tabla de stock | `stock_productos` |
| `--codigo-table` | Nombre de la tabla de códigos | `codigos_barras` |

---

## 🧠 Ejemplo completo

```bash
python sql_to_excel.py \
  --sql "BACKUP 20250923 1141.sql" \
  --out "productos.xlsx" \
  --csv "productos.csv" \
  --stock-table stock_items \
  --codigo-table codigos_barras
```

Salida esperada:
```
✅ Extrayendo datos de BACKUP 20250923 1141.sql...
✅ Tabla de stock: stock_items
✅ Tabla de códigos: codigos_barras
✅ Archivo Excel generado: productos.xlsx
✅ Archivo CSV generado: productos.csv
```

---

## 📁 Estructura del proyecto

```
sql_to_excel/
│
├── sql_to_excel.py
├── BACKUP.sql
├── productos.xlsx
├── productos.csv
├── README.md
└── requirements.txt
```

**requirements.txt**
```
pandas
openpyxl
```

---

## 🧩 Recomendaciones

- Usá siempre **Python 3.9+** para compatibilidad total.  
- Evitá nombres de archivo con espacios o caracteres especiales.  
- Si tu archivo SQL es muy grande, ejecutá desde consola (no IDE).

---

## 📜 Licencia
Distribuido bajo licencia **MIT**.  
Libre para uso personal y comercial.

---

## 👨‍💻 Autor
**Desarrollado por:** Miguel Blanco  
🌐 [miguelblanco.ar](https://miguelblanco.ar)  
📦 Compatible con Python ≥ 3.9

---

⭐ **Si te resultó útil, dejá una estrella en GitHub y compartilo.**
