import os
import psycopg2
from psycopg2.extras import RealDictCursor

def obter_conexao():
    return psycopg2.connect(
        host=os.environ.get("BANCO_HOST", "localhost"),
        port=int(os.environ.get("BANCO_PORT", 5432)),
        user=os.environ.get("BANCO_USER", "postgres"),
        password=os.environ.get("BANCO_PASSWORD", "postgrespassword"),
        dbname=os.environ.get("BANCO_NOME", "locadora"),
        connect_timeout=5
    )

def inserir_cliente(nome, cpf):
    conn = obter_conexao()
    try:
        with conn.cursor() as cur:
            cur.execute("INSERT INTO clientes (nome, cpf) VALUES (%s, %s);", (nome, cpf))
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

def listar_clientes():
    conn = obter_conexao()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("SELECT nome, cpf FROM clientes ORDER BY nome ASC;")
            return list(cur.fetchall())
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

def inserir_filme(titulo, ano, genero, preco, quantidade):
    conn = obter_conexao()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO filmes (titulo, ano, genero, preco, quantidade) VALUES (%s, %s, %s, %s, %s);",
                (titulo, ano, genero, preco, quantidade)
            )
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

def listar_filmes():
    conn = obter_conexao()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("SELECT titulo, ano, genero, preco, quantidade FROM filmes ORDER BY titulo ASC;")
            resultado = cur.fetchall()
            for item in resultado:
                item["preco"] = float(item["preco"])
            return list(resultado)
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()
