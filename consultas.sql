-- Consulta todos os produtos
SELECT * FROM produtos;

-- Consulta somente produtos ativos
SELECT *
FROM produtos
WHERE status = 'Ativo';

-- Consulta produtos inativos
SELECT *
FROM produtos
WHERE status = 'Inativo';

-- Consulta produtos com estoque baixo
SELECT *
FROM produtos
WHERE estoque <= 5;

-- Consulta produtos por categoria
SELECT categoria, COUNT(*) AS quantidade
FROM produtos
GROUP BY categoria;

-- Consulta produtos com preço acima de R$ 100,00
SELECT *
FROM produtos
WHERE preco >= 100
ORDER BY preco DESC;

-- Consulta produtos ativos ordenados pelo estoque
SELECT *
FROM produtos
WHERE status = 'Ativo'
ORDER BY estoque ASC;