#!/usr/bin/env python3
"""
Gera dados de teste para o TP1 de ISI (loja online).
Cria em ../data/input:
  - clientes.xml   (2 clientes)
  - produtos.json  (20 produtos)
  - encomendas.csv (200 linhas)

Os dados contêm erros propositados para a Fase 2 (limpeza):
  nulos, duplicados, emails/telefones/NIF inválidos, nomes com maiúsculas
  inconsistentes e espaços a mais, quantidades inválidas e produtos inexistentes.

Uso:  python gerar_dados.py
(apenas biblioteca standard; seed fixa para resultados repetíveis)
"""
import csv
import json
import random
import unicodedata
from datetime import date, timedelta
from pathlib import Path
from xml.sax.saxutils import escape

random.seed(42)

N_CLIENTES = 2      # número de clientes (sem contar o duplicado)
N_ENCOMENDAS = 2    # número de encomendas (sem contar os duplicados)

DESTINO = Path(__file__).resolve().parent.parent / "data" / "input"
DESTINO.mkdir(parents=True, exist_ok=True)

NOMES = ["Ana", "Bruno", "Carla", "Daniel", "Eva", "Filipe", "Graça", "Hugo",
         "Inês", "João", "Karina", "Luís", "Marta", "Nuno", "Olga", "Pedro",
         "Rita", "Sérgio", "Teresa", "Vasco"]
APELIDOS = ["Silva", "Santos", "Ferreira", "Pereira", "Oliveira", "Costa",
            "Rodrigues", "Martins", "Sousa", "Fernandes", "Gonçalves", "Lopes"]
CIDADES = ["Braga", "Porto", "Barcelos", "Guimarães", "Famalicão",
           "Viana do Castelo", "Lisboa", "Coimbra", "Aveiro"]

# ---------------------------------------------------------------- produtos
CATEGORIAS = {
    "Informática": ["Rato sem fios", "Teclado mecânico", "Monitor 24 polegadas",
                    "Webcam HD", "Auscultadores USB", "Hub USB-C"],
    "Casa": ["Candeeiro de secretária", "Cadeira ergonómica", "Organizador de cabos",
             "Suporte para portátil", "Tapete de rato XL"],
    "Telemóveis": ["Capa de proteção", "Carregador rápido 30W", "Cabo USB-C 2m",
                   "Película de vidro", "Power bank 10000mAh"],
    "Escritório": ["Caderno A5", "Pack de canetas", "Agrafador", "Quadro branco"],
}
produtos = []
pid = 1
for categoria, lista in CATEGORIAS.items():
    for nome in lista:
        produtos.append({
            "id": pid,
            "nome": nome,
            "categoria": categoria,
            "preco": round(random.uniform(4.5, 189.9), 2),
            "stock": random.randint(0, 150),
        })
        pid += 1

with open(DESTINO / "produtos.json", "w", encoding="utf-8") as f:
    json.dump({"produtos": produtos}, f, ensure_ascii=False, indent=2)

# ---------------------------------------------------------------- clientes
def nif_valido():
    """Gera um NIF português com dígito de controlo correto."""
    base = [random.choice([1, 2, 3, 5]) ] + [random.randint(0, 9) for _ in range(7)]
    soma = sum(d * (9 - i) for i, d in enumerate(base))
    controlo = 11 - (soma % 11)
    controlo = 0 if controlo >= 10 else controlo
    return "".join(map(str, base)) + str(controlo)

def sem_acentos(s):
    normalizado = unicodedata.normalize("NFD", s)
    return "".join(c for c in normalizado if unicodedata.category(c) != "Mn").lower()

clientes = []
for cid in range(1, N_CLIENTES + 1):
    nome = f"{random.choice(NOMES)} {random.choice(APELIDOS)}"
    email = f"{sem_acentos(nome).replace(' ', '.')}@exemplo.pt"
    telefone = "9" + random.choice("1236") + "".join(str(random.randint(0, 9)) for _ in range(7))
    clientes.append({
        "id": cid, "nome": nome, "nif": nif_valido(), "email": email,
        "telefone": telefone, "cidade": random.choice(CIDADES),
    })

# --- erros propositados nos clientes
clientes[1]["nome"] = clientes[1]["nome"].upper()                 # tudo maiúsculas
clientes[2]["nome"] = "  " + clientes[2]["nome"].lower() + "  "  # minúsculas + espaços
clientes[4]["email"] = "email-invalido.exemplo.pt"                # sem @
clientes[5]["email"] = "ana@@exemplo"                            # inválido
clientes[6]["email"] = None                                      # nulo
clientes[7]["telefone"] = "+351 " + clientes[7]["telefone"][:3] + " " + clientes[7]["telefone"][3:6] + " " + clientes[7]["telefone"][6:]  # formato com espaços
clientes[8]["telefone"] = "12345"                                # inválido
clientes[9]["telefone"] = None                                   # nulo
clientes[10]["nif"] = "123456789"                                 # NIF com controlo errado
clientes[11]["nif"] = "12AB"                                      # NIF inválido
clientes[0]["cidade"] = "  braga "                               # espaços + minúsculas
clientes.append(dict(clientes[3], id=N_CLIENTES + 1))                         # duplicado (mesmo cliente, outro id)

with open(DESTINO / "clientes.xml", "w", encoding="utf-8") as f:
    f.write('<?xml version="1.0" encoding="UTF-8"?>\n<clientes>\n')
    for c in clientes:
        f.write("  <cliente>\n")
        for campo in ("id", "nome", "nif", "email", "telefone", "cidade"):
            valor = c[campo]
            if valor is None:
                f.write(f"    <{campo}/>\n")
            else:
                f.write(f"    <{campo}>{escape(str(valor))}</{campo}>\n")
        f.write("  </cliente>\n")
    f.write("</clientes>\n")

# --------------------------------------------------------------- encomendas
CAMPOS = ["id_encomenda", "id_cliente", "id_produto", "quantidade", "data_encomenda",
          "estado", "email_contacto"]
ESTADOS = ["entregue", "enviada", "pendente", "cancelada"]
inicio = date(2026, 1, 1)

linhas = []
for i in range(1, N_ENCOMENDAS + 1):
    cliente = random.choice(clientes[:N_CLIENTES])
    dt = inicio + timedelta(days=random.randint(0, 290))
    linhas.append({
        "id_encomenda": 1000 + i,
        "id_cliente": cliente["id"],
        "id_produto": random.randint(1, len(produtos)),
        "quantidade": random.randint(1, 5),
        "data_encomenda": dt.isoformat(),
        "estado": random.choice(ESTADOS),
        "email_contacto": cliente["email"] or "",
    })

# --- erros propositados nas encomendas
linhas[2]["quantidade"] = ""                       # nulo
linhas[5]["quantidade"] = -3                      # negativa
linhas[7]["quantidade"] = 0                       # zero
linhas[9]["id_produto"] = 999                     # produto inexistente (lookup falha)
linhas[11]["id_cliente"] = 888                     # cliente inexistente
linhas[13]["data_encomenda"] = "15/03/2026"        # formato de data diferente
linhas[15]["data_encomenda"] = "2026-13-45"        # data inválida
linhas[17]["estado"] = "ENTREGUE "                 # maiúsculas + espaço
linhas[19]["email_contacto"] = "sem-arroba.pt"     # email inválido
linhas[21]["email_contacto"] = ""                 # email em falta
linhas[23]["estado"] = ""                         # estado nulo
linhas.append(dict(linhas[3]))                    # duplicado exato
linhas.append(dict(linhas[16]))                    # duplicado exato
random.shuffle(linhas)

with open(DESTINO / "encomendas.csv", "w", encoding="utf-8", newline="") as f:
    w = csv.DictWriter(f, fieldnames=CAMPOS, delimiter=";")
    w.writeheader()
    w.writerows(linhas)

print(f"Gerados em {DESTINO}:")
print(f"  produtos.json   -> {len(produtos)} produtos")
print(f"  clientes.xml    -> {len(clientes)} clientes")
print(f"  encomendas.csv  -> {len(linhas)} linhas")