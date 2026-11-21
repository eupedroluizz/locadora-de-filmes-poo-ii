from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import banco

app = FastAPI(title="Locadora API - Completa")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ClienteEntrada(BaseModel):
    nome: str
    cpf: str

class FilmeEntrada(BaseModel):
    titulo: str
    ano: int
    genero: str
    preco: float
    quantidade: int

@app.get("/clientes")
def obter_clientes():
    try:
        return banco.listar_clientes()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/clientes", status_code=201)
def adicionar_cliente(cliente: ClienteEntrada):
    nome = cliente.nome.strip()
    cpf = cliente.cpf.strip()
    if not nome:
        raise HTTPException(status_code=400, detail="O nome do cliente e obrigatorio.")
    if len(nome) > 150:
        raise HTTPException(status_code=400, detail="O nome do cliente deve ter no maximo 150 caracteres.")
    if any(ch.isalpha() for ch in cpf):
        raise HTTPException(status_code=400, detail="O CPF deve conter apenas numeros, nao digite letras.")
    caracteres_permitidos = set("0123456789.-")
    if not set(cpf).issubset(caracteres_permitidos):
        raise HTTPException(status_code=400, detail="O CPF nao pode conter simbolos ou caracteres especiais.")
    digitos = "".join(ch for ch in cpf if ch.isdigit())
    if len(digitos) != 11:
        raise HTTPException(status_code=400, detail="O CPF deve conter exatamente 11 digitos numericos.")
    try:
        banco.inserir_cliente(nome, digitos)
        return {"status": "sucesso", "mensagem": "Cliente cadastrado com sucesso."}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        msg = str(e)
        if "unique" in msg.lower() or "duplicate" in msg.lower():
            raise HTTPException(status_code=400, detail="Cliente com este CPF ja esta cadastrado.")
        raise HTTPException(status_code=500, detail=msg)

@app.get("/filmes")
def obter_filmes():
    try:
        return banco.listar_filmes()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/filmes", status_code=201)
def adicionar_filme(filme: FilmeEntrada):
    titulo = filme.titulo.strip()
    genero = filme.genero.strip()
    if not titulo:
        raise HTTPException(status_code=400, detail="O titulo do filme e obrigatorio.")
    if len(titulo) > 150:
        raise HTTPException(status_code=400, detail="O titulo deve ter no maximo 150 caracteres.")
    if not genero:
        raise HTTPException(status_code=400, detail="O genero do filme e obrigatorio.")
    if len(genero) > 50:
        raise HTTPException(status_code=400, detail="O genero deve ter no maximo 50 caracteres.")
    if filme.ano < 1880 or filme.ano > 2100:
        raise HTTPException(status_code=400, detail="O ano deve estar entre 1880 e 2100.")
    if filme.preco <= 0 or filme.preco > 9999.99:
        raise HTTPException(status_code=400, detail="O preco da locacao deve ser maior que zero e no maximo 9999.99.")
    if filme.quantidade <= 0:
        raise HTTPException(status_code=400, detail="A quantidade de exemplares deve ser maior que zero.")
    try:
        banco.inserir_filme(titulo, filme.ano, genero, filme.preco, filme.quantidade)
        return {"status": "sucesso", "mensagem": "Filme cadastrado com sucesso."}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        msg = str(e)
        if "unique" in msg.lower() or "duplicate" in msg.lower():
            raise HTTPException(status_code=400, detail="Filme com este titulo ja esta cadastrado.")
        raise HTTPException(status_code=500, detail=msg)

class LocacaoEntrada(BaseModel):
    cliente_cpf: str
    filme_titulo: str
    data: str

@app.delete("/clientes/{cpf}")
def remover_cliente(cpf: str):
    cpf_limpo = "".join(ch for ch in cpf if ch.isdigit())
    alvo = cpf_limpo if len(cpf_limpo) == 11 else cpf.strip()
    try:
        banco.excluir_cliente(alvo)
        return {"status": "sucesso", "mensagem": "Cliente excluido com sucesso."}
    except ValueError as e:
        msg = str(e)
        if "nao encontrad" in msg.lower():
            raise HTTPException(status_code=404, detail=msg)
        raise HTTPException(status_code=400, detail=msg)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/filmes/{titulo:path}")
def remover_filme(titulo: str):
    try:
        banco.excluir_filme(titulo.strip())
        return {"status": "sucesso", "mensagem": "Filme excluido com sucesso."}
    except ValueError as e:
        msg = str(e)
        if "nao encontrad" in msg.lower():
            raise HTTPException(status_code=404, detail=msg)
        raise HTTPException(status_code=400, detail=msg)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/locacoes")
def obter_locacoes():
    try:
        return banco.listar_locacoes()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/locacoes", status_code=201)
def adicionar_locacao(locacao: LocacaoEntrada):
    cpf_limpo = "".join(ch for ch in locacao.cliente_cpf if ch.isdigit())
    cliente_cpf = cpf_limpo if len(cpf_limpo) == 11 else locacao.cliente_cpf.strip()
    filme_titulo = locacao.filme_titulo.strip()
    data = locacao.data.strip()
    if not cliente_cpf:
        raise HTTPException(status_code=400, detail="O CPF do cliente e obrigatorio.")
    if not filme_titulo:
        raise HTTPException(status_code=400, detail="O titulo do filme e obrigatorio.")
    if not data:
        raise HTTPException(status_code=400, detail="A data da locacao e obrigatoria.")
    if len(data) > 30:
        raise HTTPException(status_code=400, detail="A data deve ter no maximo 30 caracteres.")
    try:
        novo_id = banco.inserir_locacao(cliente_cpf, filme_titulo, data)
        return {"status": "sucesso", "mensagem": "Locacao realizada com sucesso.", "id": novo_id}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/locacoes/{locacao_id}")
def remover_locacao(locacao_id: int):
    try:
        banco.excluir_locacao(locacao_id)
        return {"status": "sucesso", "mensagem": "Locacao excluida e estoque restaurado."}
    except ValueError as e:
        msg = str(e)
        if "nao encontrad" in msg.lower():
            raise HTTPException(status_code=404, detail=msg)
        raise HTTPException(status_code=400, detail=msg)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
