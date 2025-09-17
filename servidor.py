from flask import Flask, request, url_for
import os
import mysql.connector
from mysql.connector import Error as MySQLError
from dotenv import load_dotenv

load_dotenv('.env')

config = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'database': os.getenv('DB_NAME', 'imoveis'),
    'port': int(os.getenv('DB_PORT', 3306)),
    'charset': 'utf8mb4',
    'use_pure': True,
}
ssl_ca_path = os.getenv('SSL_CA_PATH')
if ssl_ca_path:
    config['ssl_ca'] = ssl_ca_path

def connect_db():
    try:
        conn = mysql.connector.connect(**config)
        if conn.is_connected():
            return conn
    except MySQLError as err:
        print(f"Erro: {err}")
    return None

app = Flask(__name__)

def add_links_imovel(item: dict) -> dict:
    if not item or "id" not in item:
        return item
    _id = item["id"]
    return {
        **item,
        "links": {
            "self":   {"href": url_for("obter_imovel", imovel_id=_id), "method": "GET"},
            "update": {"href": url_for("atualizar_imovel", imovel_id=_id), "method": "PUT"},
            "delete": {"href": url_for("remover_imovel", imovel_id=_id), "method": "DELETE"},
        },
    }

SELECT_COLS = """
    id, logradouro, tipo_logradouro, bairro, cidade, cep, tipo, valor, data_aquisicao
"""
ALLOWED_FIELDS = {
    "logradouro", "tipo_logradouro", "bairro", "cidade", "cep", "tipo", "valor", "data_aquisicao"
}
REQUIRED_FIELDS = {"logradouro", "cidade"}

@app.get("/imoveis")
def listar_imoveis():
    conexao = connect_db()
    if conexao is None:
        return {"error": "Erro de conexão com o banco"}, 500
    try:
        cursor = conexao.cursor(dictionary=True)
        cursor.execute(f"SELECT {SELECT_COLS} FROM imoveis")
        imoveis = cursor.fetchall()
        imoveis = [add_links_imovel(i) for i in imoveis]
        return imoveis, 200
    except MySQLError as e:
        return {"error": f"Erro de banco de dados: {str(e)}"}, 500
    finally:
        try:
            cursor.close()
        except Exception:
            pass
        conexao.close()

@app.get("/imoveis/<int:imovel_id>")
def obter_imovel(imovel_id: int):
    conexao = connect_db()
    if conexao is None:
        return {"error": "Erro de conexão com o banco"}, 500
    try:
        cursor = conexao.cursor(dictionary=True)
        cursor.execute(
            f"SELECT {SELECT_COLS} FROM imoveis WHERE id = %s",
            (imovel_id,),
        )
        imovel = cursor.fetchone()
        if not imovel:
            return {"error": "Imóvel não encontrado"}, 404
        return add_links_imovel(imovel), 200
    finally:
        try:
            cursor.close()
        except Exception:
            pass
        conexao.close()

@app.post("/imoveis")
def criar_imovel():
    if not request.is_json:
        return {"error": "Corpo deve ser JSON"}, 400

    payload = request.get_json()
    faltando = [c for c in REQUIRED_FIELDS if c not in payload or payload[c] in (None, "")]
    if faltando:
        return {"error": f"Campos obrigatórios ausentes: {', '.join(faltando)}"}, 400

    campos = [k for k in payload.keys() if k in ALLOWED_FIELDS]
    if not campos:
        campos = ["logradouro", "cidade"]

    placeholders = ", ".join(["%s"] * len(campos))
    colunas = ", ".join(campos)

    conexao = connect_db()
    if conexao is None:
        return {"error": "Erro de conexão com o banco"}, 500

    try:
        cursor = conexao.cursor(dictionary=True)
        cursor.execute(
            f"INSERT INTO imoveis ({colunas}) VALUES ({placeholders})",
            tuple(payload.get(c) for c in campos),
        )
        new_id = cursor.lastrowid
        conexao.commit()

        cursor.execute(f"SELECT {SELECT_COLS} FROM imoveis WHERE id = %s", (new_id,))
        novo = cursor.fetchone()
        return add_links_imovel(novo), 201
    except MySQLError as e:
        conexao.rollback()
        return {"error": f"Erro de banco de dados: {str(e)}"}, 500
    finally:
        try:
            cursor.close()
        except Exception:
            pass
        conexao.close()

@app.put("/imoveis/<int:imovel_id>")
def atualizar_imovel(imovel_id: int):
    if not request.is_json:
        return {"error": "Corpo deve ser JSON"}, 400

    payload = request.get_json()
    campos = [k for k in payload.keys() if k in ALLOWED_FIELDS]

    conexao = connect_db()
    if conexao is None:
        return {"error": "Erro de conexão com o banco"}, 500

    try:
        cursor = conexao.cursor(dictionary=True)
        cursor.execute("SELECT id FROM imoveis WHERE id = %s", (imovel_id,))
        if cursor.fetchone() is None:
            return {"error": "Imóvel não encontrado"}, 404

        if campos:
            sets = ", ".join([f"{c} = %s" for c in campos])
            valores = [payload[c] for c in campos]
            cursor.execute(
                f"UPDATE imoveis SET {sets} WHERE id = %s",
                tuple(valores) + (imovel_id,),
            )
            conexao.commit()

        cursor.execute(f"SELECT {SELECT_COLS} FROM imoveis WHERE id = %s", (imovel_id,))
        imovel = cursor.fetchone()
        return add_links_imovel(imovel), 200
    except MySQLError as e:
        conexao.rollback()
        return {"error": f"Erro de banco de dados: {str(e)}"}, 500
    finally:
        try:
            cursor.close()
        except Exception:
            pass
        conexao.close()

@app.delete("/imoveis/<int:imovel_id>")
def remover_imovel(imovel_id: int):
    conexao = connect_db()
    if conexao is None:
        return {"error": "Erro de conexão com o banco"}, 500
    try:
        cursor = conexao.cursor()
        cursor.execute("DELETE FROM imoveis WHERE id = %s", (imovel_id,))
        linhas = cursor.rowcount
        conexao.commit()

        if linhas == 0:
            return {"error": "Imóvel não encontrado"}, 404
        return {"message": "Imóvel removido com sucesso"}, 200
    except MySQLError as e:
        conexao.rollback()
        return {"error": f"Erro de banco de dados: {str(e)}"}, 500
    finally:
        try:
            cursor.close()
        except Exception:
            pass
        conexao.close()

@app.get("/imoveis/tipo/<string:tipo>")
def listar_por_tipo(tipo: str):
    conexao = connect_db()
    if conexao is None:
        return {"error": "Erro de conexão com o banco"}, 500
    try:
        cursor = conexao.cursor(dictionary=True)
        cursor.execute(
            f"""
            SELECT {SELECT_COLS}
            FROM imoveis
            WHERE LOWER(COALESCE(tipo,'')) = LOWER(%s)
            ORDER BY id
            """,
            (tipo,),
        )
        data = cursor.fetchall()
        if data:
            data = [add_links_imovel(i) for i in data]
            return data, 200
        return {"error": "Tipo não encontrado"}, 404
    finally:
        try:
            cursor.close()
        except Exception:
            pass
        conexao.close()

@app.get("/imoveis/cidade/<string:cidade>")
def listar_por_cidade(cidade: str):
    conexao = connect_db()
    if conexao is None:
        return {"error": "Erro de conexão com o banco"}, 500
    try:
        cursor = conexao.cursor(dictionary=True)
        cursor.execute(
            f"""
            SELECT {SELECT_COLS}
            FROM imoveis
            WHERE LOWER(COALESCE(cidade,'')) = LOWER(%s)
            ORDER BY id
            """,
            (cidade,),
        )
        data = cursor.fetchall()
        if data:
            data = [add_links_imovel(i) for i in data]
            return data, 200
        return {"error": "Cidade não encontrada"}, 404
    finally:
        try:
            cursor.close()
        except Exception:
            pass
        conexao.close()

if __name__ == "__main__":
    app.run(debug=True)
