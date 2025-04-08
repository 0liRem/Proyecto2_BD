TRUNCATE TABLE reserva, asiento, usuario, evento RESTART IDENTITY CASCADE;

-- Insert Eventos
-- Crear tabla temporal
CREATE TEMP TABLE temp_evento (
  nombre TEXT,
  fecha TEXT, 
  descripcion TEXT,
  capacidad INTEGER
);

-- Cargar datos
COPY temp_evento FROM 'C:\Users\Emadlg\Desktop\evento.csv' DELIMITER ',' CSV HEADER; --change for ur data location

-- Insertar convirtiendo el formato
INSERT INTO evento(nombre, fecha, descripcion, capacidad)
SELECT 
  nombre,
  TO_TIMESTAMP(fecha, 'MM/DD/YYYY HH24:MI:SS')::timestamp,
  descripcion,
  capacidad
FROM temp_evento;

-- Limpiar
DROP TABLE temp_evento;

----------------------------------------
-- Inserts Usuarios
COPY usuario(nombre, email)
FROM 'C:\Users\Emadlg\Desktop\usuario.csv' --change for ur data location

DELIMITER ',' CSV HEADER;

-------------------------------------------------
-- Insertar Asientos

CREATE TEMP TABLE temp_csv_raw (
    raw_data TEXT
);

COPY temp_csv_raw FROM 'C:/Users/Emadlg/Desktop/asiento.csv'  --change for ur data location

WITH (FORMAT text, ENCODING 'UTF8');

DELETE FROM temp_csv_raw 
WHERE raw_data LIKE '%evento_id%numero%estado%';

CREATE TEMP TABLE temp_csv_processed AS
WITH cleaned_data AS (
    SELECT 
        TRIM(BOTH '"' FROM raw_data) AS clean_data
    FROM temp_csv_raw
    WHERE raw_data !~ '^[[:space:]]*$'  -- Excluye líneas vacías
)
SELECT 
    split_part(clean_data, ',', 1)::INTEGER AS evento_id,
    TRIM(split_part(clean_data, ',', 2)) AS numero,
    CASE 
        WHEN TRIM(split_part(clean_data, ',', 3)) = '' THEN 'disponible'
        ELSE TRIM(split_part(clean_data, ',', 3))
    END AS estado
FROM cleaned_data
WHERE clean_data ~ '^[0-9]+,[^,]+,[^,]+';

INSERT INTO asiento (evento_id, numero, estado)
SELECT evento_id, numero, estado
FROM temp_csv_processed;



DROP TABLE temp_csv_raw;
DROP TABLE temp_csv_processed;

----------------------------------------------------------------------------

COPY reserva(asiento_id, usuario_id, fecha_hora, estado)
FROM 'C:\Users\Emadlg\Desktop\reserva.csv' --change for ur data location
DELIMITER ',' CSV HEADER;
----------------------------------------------------------------------------

-- Verificar datos insertados
select * from usuario
select * from evento
SELECT * FROM asiento
select * from reserva
