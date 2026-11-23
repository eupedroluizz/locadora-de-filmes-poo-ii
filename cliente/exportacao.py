import json
import csv

def exportar_dados_json(filmes, clientes, locacoes, caminho):
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
                "id": l.locacao_id,
                "filme_titulo": l.filme.titulo,
                "cliente_nome": l.cliente.nome,
                "cliente_cpf": l.cliente.cpf,
                "data": l.data
            } for l in locacoes
        ]
    }
    with open(caminho, "w", encoding="utf-8") as f:
        json.dump(dados, f, indent=4, ensure_ascii=False)
    return f"Exportacao JSON concluida com sucesso no arquivo:\n{caminho}"

def exportar_dados_csv(filmes, clientes, locacoes, caminho):
    base = caminho[:-4] if caminho.lower().endswith(".csv") else caminho
    for sufixo in ["_filmes", "_clientes", "_locacoes"]:
        if base.endswith(sufixo):
            base = base[:-len(sufixo)]
            break

    arq_filmes = f"{base}_filmes.csv"
    with open(arq_filmes, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["titulo", "ano", "genero", "preco", "quantidade"])
        writer.writeheader()
        for f_obj in filmes:
            writer.writerow({
                "titulo": f_obj.titulo,
                "ano": f_obj.ano,
                "genero": f_obj.genero,
                "preco": f_obj.preco,
                "quantidade": f_obj.quantidade
            })

    arq_clientes = f"{base}_clientes.csv"
    with open(arq_clientes, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["nome", "cpf"])
        writer.writeheader()
        for c_obj in clientes:
            writer.writerow({"nome": c_obj.nome, "cpf": c_obj.cpf})

    arq_locacoes = f"{base}_locacoes.csv"
    with open(arq_locacoes, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["id", "filme_titulo", "cliente_nome", "cliente_cpf", "data"])
        writer.writeheader()
        for l_obj in locacoes:
            writer.writerow({
                "id": l_obj.locacao_id,
                "filme_titulo": l_obj.filme.titulo,
                "cliente_nome": l_obj.cliente.nome,
                "cliente_cpf": l_obj.cliente.cpf,
                "data": l_obj.data
            })

    return f"Exportacao CSV concluida com sucesso.\nArquivos gerados:\n- {arq_filmes}\n- {arq_clientes}\n- {arq_locacoes}"
