import sys, importlib.util
from pathlib import Path
import pytest

@pytest.fixture
def client(tmp_path, monkeypatch):
    proj_root = Path(__file__).resolve().parents[1]
    sys.path.insert(0, str(proj_root))

    db_path = tmp_path / "test_imoveis.db"
    monkeypatch.setenv("DB_PATH", str(db_path))

    for m in ("utils", "views", "servidor"):
        sys.modules.pop(m, None)

    try:
        from servidor import app
    except ModuleNotFoundError:
        spec = importlib.util.spec_from_file_location("servidor", proj_root / "servidor.py")
        servidor = importlib.util.module_from_spec(spec)
        sys.modules["servidor"] = servidor
        spec.loader.exec_module(servidor)
        app = servidor.app

    app.config.update(TESTING=True)
    return app.test_client()

def test_crud_e_filtros(client):
    novo = {
        "logradouro": "Rua das Laranjeiras, 100",
        "tipo_logradouro": "Rua",
        "bairro": "Centro",
        "cidade": "Rio Claro",
        "cep": "13500-000",
        "tipo": "casa",
        "valor": 450000.00,
        "data_aquisicao": "2024-10-30"
    }
    r = client.post("/imoveis", json=novo); assert r.status_code == 201
    created = r.get_json(); imovel_id = created["id"]

    r = client.get("/imoveis"); assert r.status_code == 200
    assert any(i["id"] == imovel_id for i in r.get_json())

    r = client.get(f"/imoveis/{imovel_id}"); assert r.status_code == 200

    r = client.put(f"/imoveis/{imovel_id}", json={"valor": 470000.00, "bairro": "Jardim Novo"})
    assert r.status_code == 200
    updated = r.get_json()
    assert updated["valor"] == 470000.00 and updated["bairro"] == "Jardim Novo"

    r = client.get("/imoveis/tipo/casa"); assert r.status_code == 200
    assert any(i["id"] == imovel_id for i in r.get_json())

    r = client.get("/imoveis/cidade/Rio Claro"); assert r.status_code == 200
    assert any(i["id"] == imovel_id for i in r.get_json())

    r = client.delete(f"/imoveis/{imovel_id}"); assert r.status_code == 200
    r = client.get(f"/imoveis/{imovel_id}"); assert r.status_code == 404

def test_validacao_campos_obrigatorios(client):
    r = client.post("/imoveis", json={"tipo": "apartamento"})
    assert r.status_code == 400

def test_put_inexistente_retorna_404(client):
    r = client.put("/imoveis/999999", json={"valor": 1})
    assert r.status_code == 404

def test_delete_inexistente_retorna_404(client):
    r = client.delete("/imoveis/999999")
    assert r.status_code == 404

def test_filtro_case_insensitive(client):
    r = client.post("/imoveis", json={"logradouro":"A","cidade":"Rio Claro","tipo":"APARTAMENTO"})
    assert r.status_code == 201
    r = client.get("/imoveis/tipo/apartamento")
    assert r.status_code == 200
    assert any(i["tipo"] for i in r.get_json())
