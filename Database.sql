-- Creación de la base de datos
CREATE DATABASE reservas_eventos;

-- Tabla EVENTO
CREATE TABLE evento (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    fecha TIMESTAMP NOT NULL,
    descripcion TEXT,
    capacidad INTEGER NOT NULL
);

-- Tabla USUARIO
CREATE TABLE usuario (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(50) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL
);

-- Tabla ASIENTO
CREATE TABLE asiento (
    id SERIAL PRIMARY KEY,
    evento_id INTEGER NOT NULL,
    numero VARCHAR(10) NOT NULL,
    estado VARCHAR(20) NOT NULL DEFAULT 'disponible',
    FOREIGN KEY (evento_id) REFERENCES evento(id) ON DELETE CASCADE,
    UNIQUE (evento_id, numero)
);

-- Tabla RESERVA
CREATE TABLE reserva (
    id SERIAL PRIMARY KEY,
    asiento_id INTEGER NOT NULL,
    usuario_id INTEGER NOT NULL,
    fecha_hora TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    estado VARCHAR(20) NOT NULL DEFAULT 'activa',
    FOREIGN KEY (asiento_id) REFERENCES asiento(id) ON DELETE CASCADE,
    FOREIGN KEY (usuario_id) REFERENCES usuario(id) ON DELETE CASCADE
);

-- Índices para mejorar el rendimiento en consultas frecuentes
CREATE INDEX idx_asiento_evento ON asiento(evento_id);
CREATE INDEX idx_reserva_asiento ON reserva(asiento_id);
CREATE INDEX idx_reserva_usuario ON reserva(usuario_id);