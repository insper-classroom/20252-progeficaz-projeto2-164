import os
import sqlite3
from typing import List, Dict, Optional

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DB_PATH = os.environ.get("DB_PATH", os.path.join(BASE_DIR, "imoveis.db"))

IMOVEIS_COLUMNS = [
    "logradouro",
    "tipo_logradouro",
    "bairro",
    "cidade",
    "cep",
    "tipo",
    "valor",
    "data_aquisicao",
]

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS imoveis(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    logradouro TEXT NOT NULL,
    tipo_logradouro TEXT,
    bairro TEXT,
    cidade TEXT NOT NULL,
    cep TEXT,
    tipo TEXT,
    valor REAL,
    data_aquisicao TEXT
);
"""

def _get_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def _init_db_if_needed() -> None:
    with _get_conn() as conn:
        conn.executescript(SCHEMA_SQL)
        conn.commit()

_init_db_if_needed()

def _row_to_dict(row: sqlite3.Row) -> Dict:
    return dict(row)

def get_all() -> List[Dict]:
    with _get_conn() as conn:
        rows = conn.execute("SELECT * FROM imoveis ORDER BY id;").fetchall()
    return [_row_to_dict(r) for r in rows]

def get_by_id(imovel_id: int) -> Optional[Dict]:
    with _get_conn() as conn:
        row = conn.execute("SELECT * FROM imoveis WHERE id = ?;", (imovel_id,)).fetchone()
    return _row_to_dict(row) if row else None

def add(imovel: Dict) -> Dict:
    data = {k: v for k, v in imovel.items() if k in IMOVEIS_COLUMNS}
    if not data:
        raise ValueError("Nenhum campo válido para inserir.")

    cols = ", ".join(data.keys())
    placeholders = ", ".join(["?"] * len(data))
    sql = f"INSERT INTO imoveis ({cols}) VALUES ({placeholders});"

    with _get_conn() as conn:
        cur = conn.execute(sql, tuple(data.values()))
        conn.commit()
        new_id = cur.lastrowid

    return get_by_id(new_id)

def update(imovel_id: int, payload: Dict) -> Optional[Dict]:
    data = {k: v for k, v in payload.items() if k in IMOVEIS_COLUMNS}
    if not data:
        return get_by_id(imovel_id)

    sets = ", ".join([f"{k}=?" for k in data.keys()])
    params = list(data.values()) + [imovel_id]
    sql = f"UPDATE imoveis SET {sets} WHERE id = ?;"

    with _get_conn() as conn:
        cur = conn.execute(sql, params)
        conn.commit()
        if cur.rowcount == 0:
            return None

    return get_by_id(imovel_id)

def delete(imovel_id: int) -> bool:
    with _get_conn() as conn:
        cur = conn.execute("DELETE FROM imoveis WHERE id = ?;", (imovel_id,))
        conn.commit()
        return cur.rowcount > 0

def filter_by_tipo(tipo: str) -> List[Dict]:
    with _get_conn() as conn:
        rows = conn.execute(
            "SELECT * FROM imoveis WHERE LOWER(tipo) = LOWER(?) ORDER BY id;", (tipo,)
        ).fetchall()
    return [_row_to_dict(r) for r in rows]

def filter_by_cidade(cidade: str) -> List[Dict]:
    with _get_conn() as conn:
        rows = conn.execute(
            "SELECT * FROM imoveis WHERE LOWER(cidade) = LOWER(?) ORDER BY id;", (cidade,)
        ).fetchall()
    return [_row_to_dict(r) for r in rows]
