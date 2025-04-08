
# 📌 Proyecto 2: Sistema de Reservas con Concurrencia en Bases de Datos

**Universidad del Valle de Guatemala**  
**CC 3088 - Bases de Datos I**  
**Autores:** Olivier Viau (23544), Osman De León (23428)

---

## 📋 Descripción del Proyecto

Este proyecto simula un sistema de reservas de asientos para eventos, donde múltiples usuarios compiten por reservar el mismo asiento de forma concurrente.  
El objetivo es evaluar el manejo de **transacciones**, **bloqueos** y **niveles de aislamiento** en **PostgreSQL** para garantizar la integridad de los datos y evitar condiciones de carrera (_race conditions_).

---

## 🔹 Características principales

- ✔ **Transacciones ACID**: Garantizan que las reservas sean atómicas y consistentes.  
- ✔ **Concurrencia con Hilos**: Simula múltiples usuarios realizando reservas al mismo tiempo.  
- ✔ **Niveles de Aislamiento**: Pruebas con `READ COMMITTED`, `REPEATABLE READ` y `SERIALIZABLE`.  
- ✔ **Bloqueos (`FOR UPDATE`)**: Evita que dos usuarios reserven el mismo asiento simultáneamente.  
- ✔ **Resultados Detallados**: Muestra reservas exitosas, fallidas y tiempos de ejecución.

---

## ⚙️ Configuración Inicial

### 🧩 Requisitos

- Python 3.8+  
- PostgreSQL 14+  

### 📦 Librerías Python

```bash
pip install psycopg2-binary
```

---

### 🛠️ 1. Base de Datos

Crear la base de datos y las tablas:

```bash
psql -U postgres -f scripts/Database.sql
```

Cargar datos de prueba (ajustar rutas en `Tables.sql` si es necesario):

```bash
psql -U postgres -d reservas_eventos -f scripts/Tables.sql
```

> **Nota:** Los archivos CSV deben estar en la ruta especificada (por ejemplo: `evento.csv`, `usuario.csv`).

---

### 🧷 2. Configuración del Proyecto

Editar las variables en `concurrencia.py`:

```python
DB_CONFIG = {
    "dbname": "reservas_eventos",
    "user": "postgres",
    "password": "tu_password",
    "host": "localhost"
}

EVENTO_ID = 1
ASIENTO_NUMERO = "A2"
NUM_USUARIOS = [5, 10, 20, 30]
```

---

## 🚀 Ejecución del Programa

Iniciar la simulación:

```bash
python concurrencia.py
```

### 🔎 Salida esperada

```plaintext
INICIANDO PRUEBAS PARA NIVEL: READ COMMITTED
Resultados para 5 usuarios (READ COMMITTED):
  Reservas exitosas: 4
  Reservas fallidas: 1
  Tiempo promedio por reserva: 120 ms
+------------------------------------------------------------------------+
| Usuarios Concurrentes | Nivel de Aislamiento | Reservas Exitosas | ... |
+------------------------------------------------------------------------+
```

---

## 📊 Resultados y Análisis

Se probaron tres niveles de aislamiento con diferentes cargas de usuarios:

| Usuarios | Nivel de Aislamiento | Éxitos | Fallos | Tiempo Promedio (ms) |
|----------|----------------------|--------|--------|-----------------------|
| 5        | READ COMMITTED       | 4      | 1      | 120                   |
| 10       | REPEATABLE READ      | 8      | 2      | 150                   |
| 20       | SERIALIZABLE         | 15     | 5      | 300                   |

**Conclusiones:**

- `SERIALIZABLE` fue el más seguro (cero reservas duplicadas) pero más lento.
- `READ COMMITTED` tuvo mejor rendimiento pero requirió manejo de conflictos.

---


## ❓ Preguntas Frecuentes

### 1. ¿Cómo solucionar errores de conexión a PostgreSQL?

Verifica que el servicio esté activo:

```bash
sudo service postgresql status
```

Confirma las credenciales en la variable `DB_CONFIG`.

---

### 2. ¿Cómo agregar más eventos o asientos?

Edita los archivos CSV (`evento.csv`, `asiento.csv`) y vuelve a ejecutar:

```bash
psql -U postgres -d reservas_eventos -f scripts/Tables.sql
```

---

### 3. ¿Qué hacer si hay un **deadlock**?

El programa maneja _deadlocks_ automáticamente con reintentos.  
También puedes ajustar el nivel de aislamiento en el código para reducir la probabilidad de que ocurran.

---

## 📌 Licencia

Este proyecto está bajo la licencia [MIT](https://opensource.org/licenses/MIT).

---


