-- Carregado automaticamente pelo container na primeira inicialização
-- (só roda se o volume de dados estiver vazio)

CREATE TABLE cliente (
    id SERIAL,
    nome TEXT NOT NULL,
    email TEXT NOT NULL,
    criado_em TIMESTAMP NOT NULL DEFAULT now(),
    CONSTRAINT pk_cliente PRIMARY KEY (id),
    CONSTRAINT uq_cliente_email UNIQUE (email)
);

COMMENT ON TABLE cliente IS 'Clientes cadastrados na loja.';
COMMENT ON COLUMN cliente.id IS 'Identificador único do cliente.';
COMMENT ON COLUMN cliente.nome IS 'Nome completo do cliente.';
COMMENT ON COLUMN cliente.email IS 'E-mail único usado como contato.';
COMMENT ON COLUMN cliente.criado_em IS 'Data/hora de cadastro do cliente.';

CREATE TABLE produto (
    id SERIAL,
    nome TEXT NOT NULL,
    preco NUMERIC(10, 2) NOT NULL,
    estoque INTEGER NOT NULL DEFAULT 0,
    CONSTRAINT pk_produto PRIMARY KEY (id),
    CONSTRAINT ck_produto_preco_positivo CHECK (preco >= 0),
    CONSTRAINT ck_produto_estoque_nao_negativo CHECK (estoque >= 0)
);

COMMENT ON TABLE produto IS 'Produtos disponíveis para venda.';
COMMENT ON COLUMN produto.id IS 'Identificador único do produto.';
COMMENT ON COLUMN produto.nome IS 'Nome do produto.';
COMMENT ON COLUMN produto.preco IS 'Preço unitário de venda, em reais.';
COMMENT ON COLUMN produto.estoque IS 'Quantidade disponível em estoque.';

CREATE TABLE pedido (
    id SERIAL,
    cliente_id INTEGER NOT NULL,
    produto_id INTEGER NOT NULL,
    quantidade INTEGER NOT NULL,
    criado_em TIMESTAMP NOT NULL DEFAULT now(),
    CONSTRAINT pk_pedido PRIMARY KEY (id),
    CONSTRAINT fk_pedido_cliente FOREIGN KEY (cliente_id) REFERENCES cliente (id),
    CONSTRAINT fk_pedido_produto FOREIGN KEY (produto_id) REFERENCES produto (id),
    CONSTRAINT ck_pedido_quantidade_positiva CHECK (quantidade > 0)
);

COMMENT ON TABLE pedido IS 'Pedidos feitos por clientes.';
COMMENT ON COLUMN pedido.id IS 'Identificador único do pedido.';
COMMENT ON COLUMN pedido.cliente_id IS 'Cliente que fez o pedido.';
COMMENT ON COLUMN pedido.produto_id IS 'Produto pedido.';
COMMENT ON COLUMN pedido.quantidade IS 'Quantidade do produto pedida.';
COMMENT ON COLUMN pedido.criado_em IS 'Data/hora em que o pedido foi criado.';

INSERT INTO cliente (nome, email) VALUES
    ('Ana Souza', 'ana@exemplo.com'),
    ('Bruno Lima', 'bruno@exemplo.com'),
    ('Carla Dias', 'carla@exemplo.com');

INSERT INTO produto (nome, preco, estoque) VALUES
    ('Teclado mecânico', 350.00, 20),
    ('Mouse sem fio', 120.00, 50),
    ('Monitor 27"', 1200.00, 10);

INSERT INTO pedido (cliente_id, produto_id, quantidade) VALUES
    (1, 1, 1),
    (2, 3, 1),
    (3, 2, 2);
