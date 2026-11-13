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
    if filme.preco <= 0:
        raise HTTPException(status_code=400, detail="O preco da locacao deve ser maior que zero.")
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
