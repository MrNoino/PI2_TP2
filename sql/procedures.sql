DROP PROCEDURE IF EXISTS `foodsaver`.`insert_admin` ;
DELIMITER $$
CREATE PROCEDURE insert_admin(IN a_username VARCHAR(45), IN a_nome VARCHAR(100), IN a_password VARCHAR(200))
BEGIN
	INSERT INTO admin (username, nome, password)
    VALUES
    (a_username, a_nome, a_password);
END $$
DELIMITER ;

DROP PROCEDURE IF EXISTS `foodsaver`.`admin_login` ;
DELIMITER $$
CREATE PROCEDURE admin_login(IN a_username VARCHAR(45)) 
BEGIN
    SELECT id, password
			FROM admin
            WHERE username = a_username;
END $$
DELIMITER ;

DROP PROCEDURE IF EXISTS `foodsaver`.`get_admin` ;
DELIMITER $$
CREATE PROCEDURE get_admin(IN a_id INT)
BEGIN
SELECT id, username, nome as "name", password
FROM admin
WHERE id = a_id;
END $$
DELIMITER ;

DROP PROCEDURE IF EXISTS `foodsaver`.`update_admin_password` ;
DELIMITER $$
CREATE PROCEDURE update_admin_password(IN a_id VARCHAR(45), IN a_password VARCHAR(200))
BEGIN
	UPDATE admin 
    SET 
    password = a_password
    WHERE id = a_id;
END $$
DELIMITER ;

DROP PROCEDURE IF EXISTS `foodsaver`.`insert_entity` ;
DELIMITER $$
CREATE PROCEDURE insert_entity(IN a_nome VARCHAR(45), IN a_descricao VARCHAR(256), IN a_logotipo VARCHAR(100), IN a_morada VARCHAR(200), IN a_telefone VARCHAR(45), IN a_email VARCHAR(150),  IN a_password VARCHAR(200), IN a_ativo TINYINT(1))
BEGIN
	INSERT INTO entidade (nome, descricao, logotipo, morada, telefone, email, password, ativo)
    VALUES
    (a_nome, a_descricao, a_logotipo, a_morada, a_telefone, a_email, a_password, a_ativo);
END $$
DELIMITER ;

DROP PROCEDURE IF EXISTS `foodsaver`.`get_entity` ;
DELIMITER $$
CREATE PROCEDURE get_entity(IN a_id INT)
BEGIN
	SELECT id, nome as "name", descricao as "description", logotipo as "logo", morada as "address", telefone as "phone_number", email, ativo as "active"
    FROM entidade
    WHERE id = a_id;
END $$
DELIMITER ;

DROP PROCEDURE IF EXISTS `foodsaver`.`entity_login` ;
DELIMITER $$
CREATE PROCEDURE entity_login(IN a_email VARCHAR(150)) 
BEGIN
    SELECT id, password
			FROM entidade
            WHERE email = a_email and ativo = 1;
END $$
DELIMITER ;

DROP PROCEDURE IF EXISTS `foodsaver`.`update_entity` ;
DELIMITER $$
CREATE PROCEDURE update_entity(IN a_id INT, IN a_nome VARCHAR(45), IN a_descricao VARCHAR(256), IN a_logotipo VARCHAR(100), IN a_morada VARCHAR(200), IN a_telefone VARCHAR(45), IN a_email VARCHAR(150), IN a_ativo TINYINT(1))
BEGIN
	UPDATE entidade
    SET 
    nome = a_nome,
    descricao = a_descricao,
    logotipo = IFNULL(a_logotipo, logotipo),
    morada = a_morada,
    telefone = a_telefone,
    email = a_email,
    ativo = a_ativo
    WHERE id = a_id;
END $$
DELIMITER ;

DROP PROCEDURE IF EXISTS `foodsaver`.`insert_offer` ;
DELIMITER $$
CREATE PROCEDURE insert_offer(IN a_entidade_id INT, IN a_nome VARCHAR(45), IN a_descricao VARCHAR(256), IN a_foto VARCHAR(100), IN a_preço FLOAT, IN a_data DATE, IN a_disponivel TINYINT(1))
BEGIN
	INSERT INTO oferta (entidade_id, nome, descricao, foto, preço, data, disponivel)
    VALUES
    (a_entidade_id, a_nome, a_descricao, a_foto, a_preço, a_data, a_disponivel);
END $$
DELIMITER ;

DROP PROCEDURE IF EXISTS `foodsaver`.`delete_offer` ;
DELIMITER $$
CREATE PROCEDURE delete_offer(IN a_id INT)
BEGIN
	DELETE FROM oferta 
    WHERE id = a_id;
END $$
DELIMITER ;

DROP PROCEDURE IF EXISTS `foodsaver`.`get_offers` ;
DELIMITER $$
CREATE PROCEDURE get_offers(IN a_entidade_id INT)
BEGIN
SELECT id, entidade_id as "entity_id", nome as "name", descricao as "description", foto as "image", preço as "price", data as "date", disponivel as "available"
FROM oferta
WHERE entidade_id = a_entidade_id;
END $$
DELIMITER ;

DROP PROCEDURE IF EXISTS `foodsaver`.`update_offer` ;
DELIMITER $$
CREATE PROCEDURE update_offer(IN a_id INT, IN a_entidade_id INT, IN a_nome VARCHAR(45), IN a_descricao VARCHAR(256), IN a_foto VARCHAR(100), IN a_preço FLOAT, IN a_data DATE, IN a_disponivel TINYINT(1))
BEGIN
	UPDATE oferta 
    SET entidade_id = a_entidade_id,
    nome = a_nome,
    descricao = a_descricao,
    foto = IFNULL(a_foto, foto),
    preço = a_preco,
    data = a_data,
    disponivel = a_disponivel
    WHERE id = a_id;
END $$
DELIMITER ;

DROP PROCEDURE IF EXISTS `foodsaver`.`get_today_offers_by_entity` ;
DELIMITER $$
CREATE PROCEDURE get_today_offers_by_entity(IN a_entidade_id INT)
BEGIN
SELECT id, entidade_id as "entity_id", nome as "name", descricao as "description", foto as "image", preço as "price", data as "date", disponivel as "available"
FROM oferta
WHERE entidade_id = a_entidade_id and data = CURDATE() and disponivel = 1;
END $$
DELIMITER ;

DROP PROCEDURE IF EXISTS `foodsaver`.`buy_offer` ;
DELIMITER $$
CREATE PROCEDURE buy_offer(IN a_oferta_id INT, IN a_cliente_id INT, IN a_pago TINYINT(1), IN a_levantado TINYINT(1), IN a_ativo TINYINT(1))
BEGIN
	UPDATE oferta
    SET disponivel = 0
    WHERE id = a_oferta_id;
    IF((SELECT COUNT(oferta_id) FROM compra WHERE oferta_id = a_oferta_id AND cliente_id = a_cliente_id) > 0) THEN
		UPDATE compra 
        SET 
        pago = a_pago,
        levantado = a_levantado,
        ativo = a_ativo
		WHERE oferta_id = a_oferta_id AND cliente_id = a_cliente_id;
    ELSE
		INSERT INTO compra (oferta_id, cliente_id, pago, levantado, ativo)
		VALUES
		(a_oferta_id, a_cliente_id, a_pago, a_levantado, a_ativo);
    END IF;
END $$
DELIMITER ;

DROP PROCEDURE IF EXISTS `foodsaver`.`get_offer` ;
DELIMITER $$
CREATE PROCEDURE get_offer(IN a_id INT)
BEGIN
	SELECT id, entidade_id as "entity_id", nome as "name", descricao as "description", foto as "image", preço as "price", data as "date", disponivel as "available"
	FROM oferta
	WHERE id = a_id;
END $$
DELIMITER ;

DROP PROCEDURE IF EXISTS `foodsaver`.`exists_user_email` ;
DELIMITER $$
CREATE PROCEDURE exists_user_email(IN a_email VARCHAR(100))
BEGIN
	SELECT COUNT(*) as "exists"
    FROM cliente
    WHERE email = a_email;
END $$
DELIMITER ;

DROP PROCEDURE IF EXISTS `foodsaver`.`insert_user` ;
DELIMITER $$
CREATE PROCEDURE insert_user(IN a_nome VARCHAR(45), IN a_email VARCHAR(100),  IN a_password VARCHAR(200), IN a_telefone VARCHAR(45), IN a_ativo TINYINT(1))
BEGIN
	INSERT INTO cliente (nome, email, password, telefone, ativo)
    VALUES
    (a_nome, a_email, a_password, a_telefone, a_ativo);
END $$
DELIMITER ;

DROP PROCEDURE IF EXISTS `foodsaver`.`user_login` ;
DELIMITER $$
CREATE PROCEDURE user_login(IN a_email VARCHAR(100)) 
BEGIN
    SELECT id, password
	FROM cliente
	WHERE email = a_email;
END $$
DELIMITER ;

DROP PROCEDURE IF EXISTS `foodsaver`.`is_user_active` ;
DELIMITER $$
CREATE PROCEDURE is_user_active(IN a_id INT) 
BEGIN
    SELECT ativo as "active"
	FROM cliente
	WHERE id = a_id;
END $$
DELIMITER ;

DROP PROCEDURE IF EXISTS `foodsaver`.`get_purchases` ;
DELIMITER $$
CREATE PROCEDURE get_purchases(IN a_cliente_id INT) 
BEGIN
    SELECT oferta_id as "offer_id", cliente_id as "user_id", pago as "payed", levantado as "picked_up", ativo as "active"
	FROM compra
	WHERE cliente_id = a_cliente_id
    ORDER BY oferta_id DESC;
END $$
DELIMITER ;

DROP PROCEDURE IF EXISTS `foodsaver`.`get_purchase` ;
DELIMITER $$
CREATE PROCEDURE get_purchase(IN a_oferta_id INT, IN a_cliente_id INT) 
BEGIN
    SELECT oferta_id as "offer_id", cliente_id as "user_id", pago as "payed", levantado as "picked_up", ativo as "active"
	FROM compra
	WHERE oferta_id = a_oferta_id AND cliente_id = a_cliente_id;
END $$
DELIMITER ;

DROP PROCEDURE IF EXISTS `foodsaver`.`cancel_purchase` ;
DELIMITER $$
CREATE PROCEDURE cancel_purchase(IN a_oferta_id INT, IN a_cliente_id INT) 
c_p:BEGIN
    IF (SELECT data FROM oferta WHERE id = a_oferta_id LIMIT 1) != CURDATE() THEN
		LEAVE c_p;
    END IF;
    UPDATE oferta
    SET
    disponivel = 1
    WHERE id = a_oferta_id;
    UPDATE compra
    SET
    ativo = 0,
    pago = 0,
    levantado = 0
    WHERE oferta_id = a_oferta_id AND cliente_id = a_cliente_id;
END $$
DELIMITER ;

DROP PROCEDURE IF EXISTS `foodsaver`.`update_token` ;
DELIMITER $$
CREATE PROCEDURE update_token(IN a_id INT, IN a_token VARCHAR(200))
BEGIN
    UPDATE cliente
    SET
    token = a_token
    WHERE id = a_id;
END $$
DELIMITER ;

DROP PROCEDURE IF EXISTS `foodsaver`.`check_token` ;
DELIMITER $$
CREATE PROCEDURE check_token(IN a_token VARCHAR(200))
BEGIN
    SELECT COUNT(id) as "exist"
    FROM cliente
    WHERE token = a_token;
END $$
DELIMITER ;