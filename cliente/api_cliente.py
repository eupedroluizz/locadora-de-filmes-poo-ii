import os
import json
import urllib.request
import urllib.parse
import urllib.error

def obter_url_base():
    if "LOCADORA_API_URL" in os.environ and os.environ["LOCADORA_API_URL"].strip():
        return os.environ["LOCADORA_API_URL"].strip()
    caminho_config = os.path.join(os.path.dirname(__file__), "config.json")
    if os.path.exists(caminho_config):
        try:
            with open(caminho_config, "r", encoding="utf-8") as f:
                cfg = json.load(f)
                url = cfg.get("url_api", "").strip()
                if url:
                    return url
        except Exception:
            pass
    return "http://localhost:8000"

def fazer_requisicao(caminho, metodo="GET", dados=None):
    url_base = obter_url_base()
    url = f"{url_base.rstrip('/')}/{caminho.lstrip('/')}"
    cabecalhos = {}
    corpo = None
    if dados is not None:
        cabecalhos["Content-Type"] = "application/json"
        corpo = json.dumps(dados).encode("utf-8")

    req = urllib.request.Request(url, data=corpo, headers=cabecalhos, method=metodo)
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            conteudo = resp.read().decode("utf-8")
            return json.loads(conteudo) if conteudo else {}
    except urllib.error.HTTPError as e:
        erro_txt = e.read().decode("utf-8")
        try:
            dados_erro = json.loads(erro_txt)
            detalhe = dados_erro.get("detail", erro_txt)
            if isinstance(detalhe, list):
                mensagens = [item.get("msg", str(item)) if isinstance(item, dict) else str(item) for item in detalhe]
                detalhe = "; ".join(mensagens)
        except Exception:
            detalhe = erro_txt
        raise RuntimeError(str(detalhe))
    except (urllib.error.URLError, TimeoutError, ConnectionError):
        raise RuntimeError("Nao foi possivel conectar ao servidor da API.")

def listar_clientes():
    return fazer_requisicao("/clientes", metodo="GET")

def cadastrar_cliente(nome, cpf):
    return fazer_requisicao("/clientes", metodo="POST", dados={"nome": nome, "cpf": cpf})

def listar_filmes():
    return fazer_requisicao("/filmes", metodo="GET")

def cadastrar_filme(titulo, ano, genero, preco, quantidade):
    return fazer_requisicao(
        "/filmes",
        metodo="POST",
        dados={
            "titulo": titulo,
            "ano": ano,
            "genero": genero,
            "preco": preco,
            "quantidade": quantidade
        }
    )
