CREATE EXTENSION IF NOT EXISTS "pgcrypto";

CREATE TABLE usuarios (
  id             UUID          PRIMARY KEY DEFAULT gen_random_uuid(),
  nome           VARCHAR(100)  NOT NULL,
  email          VARCHAR(150)  NOT NULL UNIQUE,
  senha_usuario  VARCHAR(255)  NOT NULL,
  tipo_usuario   VARCHAR(20)   NOT NULL,
  criado_em      TIMESTAMP     NOT NULL DEFAULT NOW(),
  ultimo_acesso  TIMESTAMP
);

CREATE TABLE sensores (
  id          UUID         PRIMARY KEY DEFAULT gen_random_uuid(),
  usuario_id  UUID         NOT NULL REFERENCES usuarios(id),
  nome        VARCHAR(100) NOT NULL,
  mac_address VARCHAR(17)  UNIQUE,
  local       VARCHAR(150),
  ativo       BOOLEAN      NOT NULL DEFAULT TRUE,
  criado_em   TIMESTAMP    NOT NULL DEFAULT NOW()
);

CREATE TABLE plantas (
  id          UUID         PRIMARY KEY DEFAULT gen_random_uuid(),
  usuario_id  UUID         NOT NULL REFERENCES usuarios(id),
  nome        VARCHAR(100) NOT NULL,
  especie     VARCHAR(150),
  icone       VARCHAR(10),
  umidade_min SMALLINT     NOT NULL,
  umidade_max SMALLINT     NOT NULL,
  criado_em   TIMESTAMP    NOT NULL DEFAULT NOW()
);

CREATE TABLE leituras (
  id        UUID          PRIMARY KEY DEFAULT gen_random_uuid(),
  sensor_id UUID          NOT NULL REFERENCES sensores(id),
  planta_id UUID          REFERENCES plantas(id),
  umidade   NUMERIC(5,2)  NOT NULL,
  data_hora TIMESTAMP     NOT NULL DEFAULT NOW() 
); 