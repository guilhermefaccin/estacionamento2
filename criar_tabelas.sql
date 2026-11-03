-- ParkControl: criacao manual das tabelas no MySQL.
-- Selecione o banco de dados desejado antes de executar este arquivo.
-- Exemplo: USE nome_do_seu_banco;
-- IF NOT EXISTS preserva tabelas e registros existentes; nao atualiza sua estrutura.
-- Colunas, tipos, ENUMs, chaves e relacionamentos seguem entidades/models.py.
-- Os valores padrao definidos apenas em Python continuam sendo preenchidos pela API.
-- Este script nao cadastra usuarios. Crie o administrador com criar_admin.py.


CREATE TABLE IF NOT EXISTS clientes (
	id_cliente INTEGER NOT NULL AUTO_INCREMENT, 
	nome VARCHAR(150) NOT NULL, 
	cpf_cnpj VARCHAR(18), 
	telefone VARCHAR(20), 
	email VARCHAR(150), 
	data_cadastro DATETIME NOT NULL, 
	data_alteracao DATETIME NOT NULL, 
	id_usuario_cadastro INTEGER NOT NULL, 
	id_usuario_alteracao INTEGER, 
	ativo BOOL NOT NULL, 
	PRIMARY KEY (id_cliente), 
	UNIQUE (cpf_cnpj)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS enderecos (
	id_endereco INTEGER NOT NULL AUTO_INCREMENT, 
	id_cliente INTEGER NOT NULL, 
	rua VARCHAR(150) NOT NULL, 
	numero VARCHAR(20) NOT NULL, 
	complemento VARCHAR(100), 
	bairro VARCHAR(100) NOT NULL, 
	cidade VARCHAR(100) NOT NULL, 
	estado VARCHAR(2) NOT NULL, 
	pais VARCHAR(60) NOT NULL, 
	cep VARCHAR(9) NOT NULL, 
	data_cadastro DATETIME, 
	data_alteracao DATETIME, 
	id_usuario_cadastro INTEGER NOT NULL, 
	id_usuario_alteracao INTEGER, 
	PRIMARY KEY (id_endereco)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS marcas (
	id_marca INTEGER NOT NULL AUTO_INCREMENT, 
	nome VARCHAR(100) NOT NULL, 
	data_cadastro DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP, 
	data_alteracao DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP, 
	id_usuario_cadastro INTEGER NOT NULL, 
	id_usuario_alteracao INTEGER, 
	ativo BOOL NOT NULL, 
	PRIMARY KEY (id_marca)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS mensalidades (
	id_mensalidade INTEGER NOT NULL AUTO_INCREMENT, 
	id_contrato INTEGER NOT NULL, 
	competencia DATE NOT NULL, 
	data_vencimento DATE NOT NULL, 
	valor NUMERIC(10, 2) NOT NULL, 
	status ENUM('PENDENTE','PAGO','VENCIDO','CANCELADO') NOT NULL, 
	data_pagamento DATETIME, 
	data_cadastro DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP, 
	data_alteracao DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP, 
	id_usuario_cadastro INTEGER NOT NULL, 
	id_usuario_alteracao INTEGER, 
	PRIMARY KEY (id_mensalidade)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS pagamentos (
	id_pagamento INTEGER NOT NULL AUTO_INCREMENT, 
	id_mensalidade INTEGER, 
	id_estacionamento INTEGER, 
	valor NUMERIC(10, 2) NOT NULL, 
	data_pagamento DATETIME, 
	forma_pagamento ENUM('DINHEIRO','PIX','CARTAO_CREDITO','CARTAO_DEBITO','TRANSFERENCIA') NOT NULL, 
	status ENUM('PENDENTE','PAGO','ESTORNADO','CANCELADO') NOT NULL, 
	id_usuario INTEGER NOT NULL, 
	data_cadastro DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP, 
	data_alteracao DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP, 
	id_usuario_cadastro INTEGER NOT NULL, 
	id_usuario_alteracao INTEGER, 
	PRIMARY KEY (id_pagamento)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS tarifas (
	id_tarifa INTEGER NOT NULL AUTO_INCREMENT, 
	nome VARCHAR(100) NOT NULL, 
	modalidade ENUM('horista','mensalista') NOT NULL, 
	valor NUMERIC(10, 2) NOT NULL, 
	intervalo_minutos INTEGER, 
	data_inicio_vigencia DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP, 
	data_fim_vigencia DATETIME, 
	ativo BOOL NOT NULL, 
	PRIMARY KEY (id_tarifa)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS usuarios_estacionamento (
	id_usuario INTEGER NOT NULL AUTO_INCREMENT, 
	nome VARCHAR(100) NOT NULL, 
	cpf VARCHAR(11) NOT NULL, 
	email VARCHAR(80) NOT NULL, 
	senha VARCHAR(255) NOT NULL, 
	perfil VARCHAR(10) NOT NULL, 
	ativo BOOL NOT NULL, 
	PRIMARY KEY (id_usuario), 
	UNIQUE (cpf)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS vagas (
	id_vaga INTEGER NOT NULL AUTO_INCREMENT, 
	numero_vaga VARCHAR(10) NOT NULL, 
	tipo_vaga ENUM('carro') NOT NULL, 
	status ENUM('livre','ocupada','bloqueada') NOT NULL, 
	tipo_uso ENUM('rotativa','mensalista') NOT NULL, 
	ativo BOOL NOT NULL, 
	PRIMARY KEY (id_vaga), 
	UNIQUE (numero_vaga)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS veiculos (
	id_veiculo INTEGER NOT NULL AUTO_INCREMENT, 
	id_cliente INTEGER NOT NULL, 
	id_marca INTEGER NOT NULL, 
	placa VARCHAR(10) NOT NULL, 
	modelo VARCHAR(80) NOT NULL, 
	cor VARCHAR(30), 
	data_cadastro DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP, 
	data_alteracao DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP, 
	id_usuario_cadastro INTEGER NOT NULL, 
	id_usuario_alteracao INTEGER, 
	ativo BOOL NOT NULL, 
	PRIMARY KEY (id_veiculo), 
	UNIQUE (placa)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS contratos_mensais (
	id_contrato INTEGER NOT NULL AUTO_INCREMENT, 
	id_cliente INTEGER NOT NULL, 
	id_vaga INTEGER, 
	id_tarifa INTEGER NOT NULL, 
	data_inicio DATE NOT NULL, 
	data_fim DATE, 
	dia_vencimento INTEGER NOT NULL, 
	valor_mensal NUMERIC(10, 2) NOT NULL, 
	status ENUM('ativo','suspenso','encerrado') NOT NULL DEFAULT 'ativo', 
	id_usuario_cadastro INTEGER NOT NULL, 
	id_usuario_alteracao INTEGER, 
	PRIMARY KEY (id_contrato), 
	FOREIGN KEY(id_cliente) REFERENCES clientes (id_cliente), 
	FOREIGN KEY(id_vaga) REFERENCES vagas (id_vaga), 
	FOREIGN KEY(id_tarifa) REFERENCES tarifas (id_tarifa), 
	FOREIGN KEY(id_usuario_cadastro) REFERENCES usuarios_estacionamento (id_usuario), 
	FOREIGN KEY(id_usuario_alteracao) REFERENCES usuarios_estacionamento (id_usuario)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS estacionamentos (
	id_estacionamento INTEGER NOT NULL AUTO_INCREMENT, 
	id_veiculo INTEGER NOT NULL, 
	id_vaga INTEGER NOT NULL, 
	id_contrato INTEGER, 
	id_tarifa INTEGER, 
	id_usuario_entrada INTEGER NOT NULL, 
	id_usuario_saida INTEGER, 
	data_hora_entrada DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP, 
	data_hora_saida DATETIME, 
	valor_calculado NUMERIC(10, 2), 
	status ENUM('aberto','finalizado','cancelado') NOT NULL DEFAULT 'aberto', 
	data_cadastro DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP, 
	data_alteracao DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP, 
	PRIMARY KEY (id_estacionamento), 
	FOREIGN KEY(id_usuario_entrada) REFERENCES usuarios_estacionamento (id_usuario), 
	FOREIGN KEY(id_usuario_saida) REFERENCES usuarios_estacionamento (id_usuario)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
