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

def inserir_locacao(cliente_cpf, filme_titulo, data):
    conn = obter_conexao()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT 1 FROM clientes WHERE cpf = %s;", (cliente_cpf,))
            if not cur.fetchone():
                raise ValueError("Cliente nao encontrado.")

            cur.execute("SELECT quantidade FROM filmes WHERE titulo = %s FOR UPDATE;", (filme_titulo,))
            linha = cur.fetchone()
            if not linha:
                raise ValueError("Filme nao encontrado.")
            qtd_atual = linha[0]
            if qtd_atual <= 0:
                raise ValueError("Nao ha exemplares disponiveis para locacao.")

            cur.execute(
                "UPDATE filmes SET quantidade = quantidade - 1 WHERE titulo = %s;",
                (filme_titulo,)
            )
            cur.execute(
                "INSERT INTO locacoes (cliente_cpf, filme_titulo, data) VALUES (%s, %s, %s) RETURNING id;",
                (cliente_cpf, filme_titulo, data)
            )
            novo_id = cur.fetchone()[0]
        conn.commit()
        return novo_id
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

def listar_locacoes():
    conn = obter_conexao()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            sql = (
                "SELECT l.id, c.nome AS cliente_nome, c.cpf AS cliente_cpf, "
                "f.titulo AS filme_titulo, l.data "
                "FROM locacoes l "
                "JOIN clientes c ON l.cliente_cpf = c.cpf "
                "JOIN filmes f ON l.filme_titulo = f.titulo "
                "ORDER BY l.id DESC;"
            )
            cur.execute(sql)
            return list(cur.fetchall())
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()
