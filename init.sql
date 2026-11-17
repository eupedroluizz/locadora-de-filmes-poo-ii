CREATE TABLE IF NOT EXISTS clientes (
    cpf VARCHAR(14) PRIMARY KEY,
    nome VARCHAR(150) NOT NULL CHECK (trim(nome) <> '')
);

CREATE TABLE IF NOT EXISTS filmes (
    titulo VARCHAR(150) PRIMARY KEY CHECK (trim(titulo) <> ''),
    ano INT NOT NULL CHECK (ano BETWEEN 1880 AND 2100),
    genero VARCHAR(50) NOT NULL CHECK (trim(genero) <> ''),
    preco NUMERIC(6,2) NOT NULL CHECK (preco > 0),
    quantidade INT NOT NULL CHECK (quantidade >= 0)
);

CREATE TABLE IF NOT EXISTS locacoes (
    id SERIAL PRIMARY KEY,
    cliente_cpf VARCHAR(14) NOT NULL REFERENCES clientes(cpf) ON UPDATE CASCADE,
    filme_titulo VARCHAR(150) NOT NULL REFERENCES filmes(titulo) ON UPDATE CASCADE,
    data VARCHAR(30) NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_locacoes_cliente ON locacoes(cliente_cpf);
CREATE INDEX IF NOT EXISTS idx_locacoes_filme ON locacoes(filme_titulo);
