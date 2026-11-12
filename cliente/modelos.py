class Cliente:
    def __init__(self, nome, cpf):
        self.nome = nome
        self.cpf = cpf

class Filme:
    def __init__(self, titulo, ano, genero, preco, quantidade):
        self.titulo = titulo
        self.ano = ano
        self.genero = genero
        self.preco = preco
        self.quantidade = quantidade

class Locacao:
    def __init__(self, filme, cliente, data):
        self.filme = filme
        self.cliente = cliente
        self.data = data
