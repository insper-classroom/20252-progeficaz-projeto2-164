from itertools import count

IMOVEIS_DB = [
    {
        "id": 1,
        "tipo": "casa",
        "cidade": "São Paulo",
        "endereco": "Rua A, 123",
        "quartos": 3,
        "banheiros": 2,
        "area_m2": 120,
        "preco": 650000.0,
    },
    {
        "id": 2,
        "tipo": "apartamento",
        "cidade": "Rio Claro",
        "endereco": "Av. B, 456, ap 12",
        "quartos": 2,
        "banheiros": 1,
        "area_m2": 65,
        "preco": 280000.0,
    },
]

_id_counter = count(start=(max([i["id"] for i in IMOVEIS_DB]) + 1) if IMOVEIS_DB else 1)

def _next_id():
    return next(_id_counter)

def get_all():
    return IMOVEIS_DB

def get_by_id(imovel_id: int):
    return next((i for i in IMOVEIS_DB if i["id"] == imovel_id), None)

def add(imovel: dict):
    novo = imovel.copy()
    novo["id"] = _next_id()
    IMOVEIS_DB.append(novo)
    return novo

def update(imovel_id: int, data: dict):
    imovel = get_by_id(imovel_id)
    if not imovel:
        return None
    data = {k: v for k, v in data.items() if k != "id"}
    imovel.update(data)
    return imovel

def delete(imovel_id: int) -> bool:
    imovel = get_by_id(imovel_id)
    if not imovel:
        return False
    IMOVEIS_DB.remove(imovel)
    return True

def filter_by_tipo(tipo: str):
    t = tipo.strip().lower()
    return [i for i in IMOVEIS_DB if str(i.get("tipo", "")).lower() == t]

def filter_by_cidade(cidade: str):
    c = cidade.strip().lower()
    return [i for i in IMOVEIS_DB if str(i.get("cidade", "")).lower() == c]
