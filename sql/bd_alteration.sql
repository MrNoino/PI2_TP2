ALTER TABLE `foodsaver`.`cliente` 
ADD COLUMN `token` VARCHAR(200) NULL;

ALTER TABLE `foodsaver`.`compra` 
ADD COLUMN `ativo` TINYINT(1) NULL;