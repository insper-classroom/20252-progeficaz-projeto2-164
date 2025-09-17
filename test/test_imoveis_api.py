import pytest
from unittest.mock import patch, MagicMock
from servidor import app

@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client

def add_links(_id: int):
    return {
        "self":   {"href": f"/imoveis/{_id}", "method": "GET"},
        "update": {"href": f"/imoveis/{_id}", "method": "PUT"},
        "delete": {"href": f"/imoveis/{_id}", "method": "DELETE"},
    }

def row(
    _id: int,
    logradouro="Nicole Common",
    tipo_logradouro="Travessa",
    bairro="Lake Danielle",
    cidade="Judymouth",
    cep="85184",
    tipo="casa em condominio",
    valor=488423.52,
    data_aquisicao="2017-07-29",
):
    return {
        "id": _id,
        "logradouro": logradouro,
        "tipo_logradouro": tipo_logradouro,
        "bairro": bairro,
        "cidade": cidade,
        "cep": cep,
        "tipo": tipo,
        "valor": valor,
        "data_aquisicao": data_aquisicao,
    }

def make_conn_and_cursor():
    mock_conn = MagicMock(name="conn")
    mock_cursor = MagicMock(name="cursor")
    mock_conn.cursor.return_value = mock_cursor
    return mock_conn, mock_cursor



@patch("servidor.connect_db")
def test_get_imoveis_ok(mock_connect_db, client):
    mock_conn, mock_cursor = make_conn_and_cursor()
    mock_connect_db.return_value = mock_conn

    mock_cursor.fetchall.return_value = [row(1), row(2, logradouro="Price Prairie", cidade="North Garyville", data_aquisicao="2017-07-30")]
    resp = client.get("/imoveis")
    assert resp.status_code == 200

    expected = [ dict(**row(1), links=add_links(1)),
                 dict(**row(2, logradouro="Price Prairie", cidade="North Garyville", data_aquisicao="2017-07-30"), links=add_links(2)) ]
    assert resp.get_json() == expected

@patch("servidor.connect_db")
def test_get_imovel_por_id_ok(mock_connect_db, client):
    mock_conn, mock_cursor = make_conn_and_cursor()
    mock_connect_db.return_value = mock_conn

    mock_cursor.fetchone.return_value = row(1)
    resp = client.get("/imoveis/1")
    assert resp.status_code == 200
    assert resp.get_json() == dict(**row(1), links=add_links(1))

@patch("servidor.connect_db")
def test_get_imovel_por_id_404(mock_connect_db, client):
    mock_conn, mock_cursor = make_conn_and_cursor()
    mock_connect_db.return_value = mock_conn

    mock_cursor.fetchone.return_value = None
    resp = client.get("/imoveis/999999")
    assert resp.status_code == 404
    assert resp.get_json()["error"] == "Imóvel não encontrado"

@patch("servidor.connect_db")
def test_criar_imovel_ok(mock_connect_db, client):
    mock_conn, mock_cursor = make_conn_and_cursor()
    mock_connect_db.return_value = mock_conn

    mock_cursor.lastrowid = 42
    criado = row(42, logradouro="Rua Teste 123", tipo="apartamento", valor=260000.00, data_aquisicao="2024-10-30")
    mock_cursor.fetchone.return_value = criado

    payload = {
        "logradouro": "Rua Teste 123",
        "tipo_logradouro": "Rua",
        "bairro": "Centro",
        "cidade": "São Paulo",
        "cep": "01000-000",
        "tipo": "apartamento",
        "valor": 260000.00,
        "data_aquisicao": "2024-10-30",
    }
    resp = client.post("/imoveis", json=payload)
    assert resp.status_code == 201
    assert resp.get_json() == dict(**criado, links=add_links(42))
    mock_conn.commit.assert_called()

@patch("servidor.connect_db")
def test_criar_imovel_400_campos_obrigatorios(mock_connect_db, client):
    mock_connect_db.return_value = MagicMock()
    resp = client.post("/imoveis", json={"tipo": "apartamento"})
    assert resp.status_code == 400
    assert "Campos obrigatórios" in resp.get_json()["error"]

@patch("servidor.connect_db")
def test_atualizar_imovel_ok(mock_connect_db, client):
    mock_conn, mock_cursor = make_conn_and_cursor()
    mock_connect_db.return_value = mock_conn

    existente = {"id": 1}
    atualizado = row(1, logradouro="Nicole nova", tipo_logradouro="T", bairro="lago novo",
                     cidade="cidade nova", cep="11111", tipo="casa", valor=481223.52, data_aquisicao="2025-09-15")
    mock_cursor.fetchone.side_effect = [existente, atualizado]

    resp = client.put("/imoveis/1", json={
        "logradouro": "Nicole nova",
        "tipo_logradouro": "T",
        "bairro": "lago novo",
        "cidade": "cidade nova",
        "cep": "11111",
        "tipo": "casa",
        "valor": 481223.52,
        "data_aquisicao": "2025-09-15"
    })
    assert resp.status_code == 200
    assert resp.get_json() == dict(**atualizado, links=add_links(1))
    mock_conn.commit.assert_called()

@patch("servidor.connect_db")
def test_atualizar_imovel_404(mock_connect_db, client):
    mock_conn, mock_cursor = make_conn_and_cursor()
    mock_connect_db.return_value = mock_conn

    mock_cursor.fetchone.return_value = None
    resp = client.put("/imoveis/999999", json={"valor": 1})
    assert resp.status_code == 404
    assert resp.get_json()["error"] == "Imóvel não encontrado"

@patch("servidor.connect_db")
def test_remover_imovel_ok(mock_connect_db, client):
    mock_conn, mock_cursor = make_conn_and_cursor()
    mock_connect_db.return_value = mock_conn

    mock_cursor.rowcount = 1
    resp = client.delete("/imoveis/2")
    assert resp.status_code == 200
    assert resp.get_json() == {"message": "Imóvel removido com sucesso"}
    mock_conn.commit.assert_called()

@patch("servidor.connect_db")
def test_remover_imovel_404(mock_connect_db, client):
    mock_conn, mock_cursor = make_conn_and_cursor()
    mock_connect_db.return_value = mock_conn

    mock_cursor.rowcount = 0
    resp = client.delete("/imoveis/999999")
    assert resp.status_code == 404
    assert resp.get_json()["error"] == "Imóvel não encontrado"

@patch("servidor.connect_db")
def test_listar_por_tipo_ok(mock_connect_db, client):
    mock_conn, mock_cursor = make_conn_and_cursor()
    mock_connect_db.return_value = mock_conn

    mock_cursor.fetchall.return_value = [
        row(1, tipo="casa em condominio"),
        row(2, logradouro="Price Prairie", tipo="casa em condominio", cidade="North Garyville", data_aquisicao="2021-11-30"),
    ]
    resp = client.get("/imoveis/tipo/casa%20em%20condominio")
    assert resp.status_code == 200
    expected = [
        dict(**row(1, tipo="casa em condominio"), links=add_links(1)),
        dict(**row(2, logradouro="Price Prairie", tipo="casa em condominio", cidade="North Garyville", data_aquisicao="2021-11-30"), links=add_links(2)),
    ]
    assert resp.get_json() == expected

@patch("servidor.connect_db")
def test_listar_por_tipo_404(mock_connect_db, client):
    mock_conn, mock_cursor = make_conn_and_cursor()
    mock_connect_db.return_value = mock_conn

    mock_cursor.fetchall.return_value = []
    resp = client.get("/imoveis/tipo/chacara")
    assert resp.status_code == 404
    assert resp.get_json()["error"] == "Tipo não encontrado"

@patch("servidor.connect_db")
def test_listar_por_cidade_ok(mock_connect_db, client):
    mock_conn, mock_cursor = make_conn_and_cursor()
    mock_connect_db.return_value = mock_conn

    mock_cursor.fetchall.return_value = [
        row(1, cidade="Judymouth"),
        row(2, logradouro="Price Prairie", cidade="Judymouth", data_aquisicao="2021-11-30"),
    ]
    resp = client.get("/imoveis/cidade/Judymouth")
    assert resp.status_code == 200
    expected = [
        dict(**row(1, cidade="Judymouth"), links=add_links(1)),
        dict(**row(2, logradouro="Price Prairie", cidade="Judymouth", data_aquisicao="2021-11-30"), links=add_links(2)),
    ]
    assert resp.get_json() == expected

@patch("servidor.connect_db")
def test_listar_por_cidade_404(mock_connect_db, client):
    mock_conn, mock_cursor = make_conn_and_cursor()
    mock_connect_db.return_value = mock_conn

    mock_cursor.fetchall.return_value = []
    resp = client.get("/imoveis/cidade/CidadeQueNaoExiste")
    assert resp.status_code == 404
    assert resp.get_json()["error"] == "Cidade não encontrada"
