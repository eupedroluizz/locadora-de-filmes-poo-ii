import json
import csv
import os
import threading
import sys
from PySide6.QtCore import QObject, Signal

class Sinais(QObject):
    finalizado = Signal()
    erro = Signal(str)
    resultado_salvar = Signal(str)
    resultado_carregar = Signal(dict)

class Trabalhador(QObject):
    def __init__(self, fn, *args, **kwargs):
        super().__init__()
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.sinais = Sinais()
        self._thread = threading.Thread(target=self._run, daemon=True)

    def _run(self):
        try:
            resultado = self.fn(*self.args, **self.kwargs)
            if self.fn.__name__.startswith("salvar"):
                self.sinais.resultado_salvar.emit(resultado)
            elif self.fn.__name__.startswith("carregar"):
                self.sinais.resultado_carregar.emit(resultado)
        except Exception as e:
            self.sinais.erro.emit(str(e))
        finally:
            self.sinais.finalizado.emit()

    def start(self):
        self._thread.start()

def salvar_dados(filmes, clientes, locacoes, caminho):
    dados = {
        "filmes": [{"titulo": f.titulo, "ano": f.ano, "genero": f.genero, "preco": f.preco, "quantidade": f.quantidade} for f in filmes],
        "clientes": [{"nome": c.nome, "cpf": c.cpf} for c in clientes],
        "locacoes": [{"filme": l.filme.titulo, "cliente": l.cliente.cpf, "data": l.data} for l in locacoes]
    }
    
    _, extensao = os.path.splitext(caminho)
    
    if extensao.lower() == ".json":
        with open(caminho, 'w', encoding='utf-8') as f:
            json.dump(dados, f, ensure_ascii=False, indent=4)
        return "Arquivo JSON salvo."
    elif extensao.lower() == ".csv":
        base = os.path.splitext(caminho)[0]
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
            
        return "Arquivos CSV salvos."
    else:
        raise ValueError("Formato nao suportado.")

def carregar_dados(caminho):
    _, extensao = os.path.splitext(caminho)
    dados = {"filmes": [], "clientes": [], "locacoes": []}
    
    if extensao.lower() == ".json":
        with open(caminho, 'r', encoding='utf-8') as f:
            dados = json.load(f)
        return dados
    elif extensao.lower() == ".csv":
        base = os.path.splitext(caminho)[0]
        
        if os.path.exists(f"{base}_filmes.csv"):
            with open(f"{base}_filmes.csv", 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                dados["filmes"] = list(reader)
                
        if os.path.exists(f"{base}_clientes.csv"):
            with open(f"{base}_clientes.csv", 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                dados["clientes"] = list(reader)
                
        if os.path.exists(f"{base}_locacoes.csv"):
            with open(f"{base}_locacoes.csv", 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                dados["locacoes"] = list(reader)
                
        return dados
    else:
        raise ValueError("Formato nao suportado.")
