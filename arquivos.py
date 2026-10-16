import json
import csv
import os
import threading
from PySide6.QtCore import QObject, Signal


class SinaisTrabalhador(QObject):
    sucesso = Signal(object)
    erro = Signal(str)
    finalizado = Signal()


class Trabalhador(QObject):
    def __init__(self, fn, *args, **kwargs):
        super().__init__()
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.sinais = SinaisTrabalhador()
        self._thread = threading.Thread(target=self._run, daemon=True)

    def _run(self):
        try:
            resultado = self.fn(*self.args, **self.kwargs)
            self.sinais.sucesso.emit(resultado)
        except Exception as e:
            self.sinais.erro.emit(str(e))
        finally:
            self.sinais.finalizado.emit()

    def start(self):
        self._thread.start()


def salvar_dados(filmes, clientes, locacoes, caminho):
    dados = {
        "filmes": [
            {
                "titulo": f.titulo,
                "ano": f.ano,
                "genero": f.genero,
                "preco": f.preco,
                "quantidade": f.quantidade
            } for f in filmes
        ],
        "clientes": [
            {
                "nome": c.nome,
                "cpf": c.cpf
            } for c in clientes
        ],
        "locacoes": [
            {
                "filme": l.filme.titulo,
                "cliente": l.cliente.cpf,
                "data": l.data
            } for l in locacoes
        ]
    }

    _, extensao = os.path.splitext(caminho)

    if extensao.lower() == ".json":
        with open(caminho, 'w', encoding='utf-8') as f:
            json.dump(dados, f, ensure_ascii=False, indent=4)
        return "Arquivo JSON salvo com sucesso."

    elif extensao.lower() == ".csv":
        base = os.path.splitext(caminho)[0]
        for sufixo in ["_filmes", "_clientes", "_locacoes"]:
            if base.endswith(sufixo):
                base = base[:-len(sufixo)]
                break

        with open(f"{base}_filmes.csv", 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=["titulo", "ano", "genero", "preco", "quantidade"])
            writer.writeheader()
            writer.writerows(dados["filmes"])

        with open(f"{base}_clientes.csv", 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=["nome", "cpf"])
            writer.writeheader()
            writer.writerows(dados["clientes"])

        with open(f"{base}_locacoes.csv", 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=["filme", "cliente", "data"])
            writer.writeheader()
            writer.writerows(dados["locacoes"])

        return "Arquivos CSV salvos com sucesso."

    else:
        raise ValueError(f"Formato '{extensao}' não suportado. Utilize .json ou .csv.")


def carregar_dados(caminho):
    _, extensao = os.path.splitext(caminho)
    dados = {"filmes": [], "clientes": [], "locacoes": []}

    if extensao.lower() == ".json":
        with open(caminho, 'r', encoding='utf-8') as f:
            dados = json.load(f)
        return dados

    elif extensao.lower() == ".csv":
        base = os.path.splitext(caminho)[0]
        for sufixo in ["_filmes", "_clientes", "_locacoes"]:
            if base.endswith(sufixo):
                base = base[:-len(sufixo)]
                break

        arq_filmes = f"{base}_filmes.csv"
        arq_clientes = f"{base}_clientes.csv"
        arq_locacoes = f"{base}_locacoes.csv"

        if not os.path.exists(arq_filmes) and not os.path.exists(arq_clientes) and not os.path.exists(arq_locacoes):
            if os.path.exists(caminho):
                with open(caminho, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    cabecalhos = reader.fieldnames or []
                    if "ano" in cabecalhos:
                        dados["filmes"] = list(reader)
                    elif "cpf" in cabecalhos:
                        dados["clientes"] = list(reader)
                    elif "data" in cabecalhos:
                        dados["locacoes"] = list(reader)
                return dados

        if os.path.exists(arq_filmes):
            with open(arq_filmes, 'r', encoding='utf-8') as f:
                dados["filmes"] = list(csv.DictReader(f))

        if os.path.exists(arq_clientes):
            with open(arq_clientes, 'r', encoding='utf-8') as f:
                dados["clientes"] = list(csv.DictReader(f))

        if os.path.exists(arq_locacoes):
            with open(arq_locacoes, 'r', encoding='utf-8') as f:
                dados["locacoes"] = list(csv.DictReader(f))

        return dados

    else:
        raise ValueError(f"Formato '{extensao}' não suportado. Utilize .json ou .csv.")