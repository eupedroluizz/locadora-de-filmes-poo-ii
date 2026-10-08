import json
import csv
import os

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
