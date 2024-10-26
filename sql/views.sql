DROP VIEW IF EXISTS `foodsaver`.`get_total_admins`;
CREATE VIEW get_total_admins AS
SELECT COUNT(id)
FROM admin;

DROP VIEW IF EXISTS `foodsaver`.`get_entities`;
CREATE VIEW get_entities AS
SELECT id, nome as "name", descricao as "description", logotipo as "logo", morada as "address", telefone as "phone_number", email, password, ativo as "active"
FROM entidade;

DROP VIEW IF EXISTS `foodsaver`.`get_active_entities`;
CREATE VIEW get_active_entities AS
SELECT id, nome as "name", descricao as "description", logotipo as "logo", morada as "address", telefone as "phone_number", email, ativo as "active"
FROM entidade
WHERE ativo = 1;

DROP VIEW IF EXISTS `foodsaver`.`get_today_offers`;
CREATE VIEW get_today_offers AS
SELECT id, entidade_id as "entity_id", nome as "name", descricao as "description", foto as "image", preço as "price", data as "date", disponivel as "available"
FROM oferta
WHERE data = CURDATE() and disponivel = 1;
