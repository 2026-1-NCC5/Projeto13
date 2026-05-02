create database LE;

use LE;

create table grupo(
id int primary key auto_increment,
nomeGrupo varchar(30) unique,
mentor varchar(30) unique,
kgArrecadados double
);

create table alimento(
id int primary key auto_increment,
nome varchar(30),
marca varchar(30),
quantidade int,
peso float,
dataHora datetime,
framecaminho varchar(50),
idGrupo int,
nomeIntegrante varchar(30),
foreign key (idGrupo) references grupo(id)
);

create table usuario(
id int primary key auto_increment,
nome varchar(30),
email varchar(50) unique,
senha varchar(50),
foto varchar(255),
idgrupo int,
foreign key (idgrupo) references grupo(id)
);

DELIMITER //

CREATE TRIGGER trg_alimento_after_insert
AFTER INSERT ON alimento
FOR EACH ROW
BEGIN
    UPDATE grupo
    SET kgArrecadados = IFNULL(kgArrecadados, 0) + NEW.peso * NEW.quantidade
    WHERE id = NEW.idGrupo;
END //

DELIMITER ;

DELIMITER //

CREATE TRIGGER trg_alimento_after_update
AFTER UPDATE ON alimento
FOR EACH ROW
BEGIN
    -- Remove o peso antigo do saldo do grupo anterior
    UPDATE grupo
    SET kgArrecadados = IFNULL(kgArrecadados, 0) - OLD.peso * OLD.quantidade
    WHERE id = OLD.idGrupo;

    -- Adiciona o peso novo ao saldo do grupo atual
    UPDATE grupo
    SET kgArrecadados = IFNULL(kgArrecadados, 0) + NEW.peso * NEW.quantidade
    WHERE id = NEW.idGrupo;
END //

DELIMITER ;

DELIMITER //

CREATE TRIGGER trg_alimento_after_delete
AFTER DELETE ON alimento
FOR EACH ROW
BEGIN
    UPDATE grupo
    SET kgArrecadados = IFNULL(kgArrecadados, 0) - OLD.peso * OLD.quantidade
    WHERE id = OLD.idGrupo;
END //

DELIMITER ;

