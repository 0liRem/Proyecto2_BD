'''Documentación  interna

Autores:
        Olivier Viau
        Osman De León 

Historial de modificaciones
    [000] 07/04/2025
    [001] 08/04/2025

Recursos:
    https://docs.python.org/es/3.8/library/threading.html
    https://www.psycopg.org/docs/
    https://docs.python.org/3/library/sys.html
    DeepSeek for inquiries about threading, and session transactions


'''

import psycopg2
from psycopg2 import errors
from psycopg2.extensions import ISOLATION_LEVEL_READ_COMMITTED,ISOLATION_LEVEL_REPEATABLE_READ,ISOLATION_LEVEL_SERIALIZABLE
import threading
from datetime import datetime
import time
import sys

# Configuración de la base de datos
# Cambiar a tus datos
DB_CONFIG = {
    "dbname": "reservas_eventos",
    "user": "postgres",
    "password": "admin",
    "host": "localhost"
}

# Configuración de pruebas
# Cambiar si se quiere probar otros datos
EVENTO_ID = 1 
ASIENTO_NUMERO = "A2"
NUM_USUARIOS = [5, 10, 20, 30]
#Declaración de los niveles de aislamiento para poder acceder a ellos por un ciclo for
ISOLATION_LEVELS = {
    "READ COMMITTED": ISOLATION_LEVEL_READ_COMMITTED,
    "REPEATABLE READ": ISOLATION_LEVEL_REPEATABLE_READ,
    "SERIALIZABLE": ISOLATION_LEVEL_SERIALIZABLE
}


resultados = []

def generar_tabla_resultados():
    print("\n\nRESUMEN DE RESULTADOS")
    print("+" + "-"*78 + "+")
    print("| {:^20} | {:^18} | {:^15} | {:^15} |".format(
        "Usuarios Concurrentes", "Nivel de Aislamiento", "Reservas Exitosas", "Reservas Fallidas"))
    print("+" + "-"*78 + "+")
    
    for resultado in resultados:
        print("| {:^20} | {:^18} | {:^15} | {:^15} |".format(
            resultado['usuarios'],
            resultado['nivel_aislamiento'],
            resultado['exitosas'],
            resultado['fallidas']))
    


def intentar_reserva(user_id, isolation_level_name, results):
    conn = None
    start_time = time.time()
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        conn.set_isolation_level(ISOLATION_LEVELS[isolation_level_name])
        conn.autocommit = False #Evita el autocommit para no tener errores de session
        
        with conn.cursor() as cur:
            # Transaction
            cur.execute(
                "SELECT id, estado FROM asiento WHERE evento_id = %s AND numero = %s FOR UPDATE",
                (EVENTO_ID, ASIENTO_NUMERO)
            )
            row = cur.fetchone()
            
            if not row:
                results.append((user_id, "asiento no encontrado", 0))
                return
            
            asiento_id, estado = row
            
            if estado == "disponible":
                
                cur.execute(
                    "INSERT INTO reserva (asiento_id, usuario_id, estado) VALUES (%s, %s, 'activa')",
                    (asiento_id, user_id)
                )
                cur.execute(
                    "UPDATE asiento SET estado = 'reservado' WHERE id = %s",
                    (asiento_id,)
                )
                conn.commit()
                execution_time = (time.time() - start_time) * 1000
                results.append((user_id, "éxito", execution_time))
            else:
                conn.rollback()
                execution_time = (time.time() - start_time) * 1000
                results.append((user_id, "asiento no disponible", execution_time))
                
    except (errors.SerializationFailure, errors.DeadlockDetected) as e:
        if conn:
            conn.rollback()
        execution_time = (time.time() - start_time) * 1000
        results.append((user_id, f"error de concurrencia: {type(e).__name__}", execution_time))
    except Exception as e:
        if conn:
            conn.rollback()
        execution_time = (time.time() - start_time) * 1000
        results.append((user_id, f"error general: {type(e).__name__}", execution_time))
    finally:
        if conn:
            try:
                if conn.closed == 0:
                    conn.close()
            except:
                pass

def ejecutar_prueba(num_usuarios, isolation_level_name):
    print(f"\nIniciando prueba con {num_usuarios} usuarios y nivel {isolation_level_name}")
    conn = None
    # Para las pruebas se reinicia el estado del asiento para agilizarlo, si se quiere probar con un asiento volver comentario
    
    
    #Inicia aqui
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        conn.autocommit = True
        with conn.cursor() as cur:
            cur.execute(
                "UPDATE asiento SET estado = 'disponible' WHERE evento_id = %s AND numero = %s",
                (EVENTO_ID, ASIENTO_NUMERO)
            )
            cur.execute(
                "DELETE FROM reserva WHERE asiento_id IN (SELECT id FROM asiento WHERE evento_id = %s AND numero = %s)",
                (EVENTO_ID, ASIENTO_NUMERO)
            )
    except Exception as e:
        print(f"Error al reiniciar estado: {e}", file=sys.stderr)
        return
    finally:
        if conn:
            conn.close()
    #Termina aqui

    # Seleccionar usuarios aleatorios, para simular un entorno real
    user_ids = []
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        conn.autocommit = True
        with conn.cursor() as cur:
            cur.execute("SELECT id FROM usuario ORDER BY random() LIMIT %s", (num_usuarios,))
            user_ids = [row[0] for row in cur.fetchall()]
    except Exception as e:
        print(f"Error al seleccionar usuarios: {e}", file=sys.stderr)
        return
    finally:
        if conn:
            conn.close()
    
    if not user_ids:
        print("No se pudieron obtener usuarios para la prueba")
        return
    
    # Ejecutar reservas paralelizadas
    threads = []
    results = []
    start_time = time.time()
    
    for user_id in user_ids:
        t = threading.Thread(
            target=intentar_reserva,
            args=(user_id, isolation_level_name, results)
        )
        threads.append(t)
        t.start()
    
    for t in threads:
        t.join()
    
    total_time = (time.time() - start_time) * 1000  
    

    exitosos = sum(1 for r in results if r[1] == "éxito")
    fallidos = len(results) - exitosos
    

    tiempos = [r[2] for r in results if r[2] > 0]
    tiempo_promedio = sum(tiempos) / len(tiempos) if tiempos else 0
    
    #Resultados
    resultados.append({
        'usuarios': num_usuarios,
        'nivel_aislamiento': isolation_level_name,
        'exitosas': exitosos,
        'fallidas': fallidos,
        'tiempo_promedio': tiempo_promedio,
        'tiempo_total': total_time
    })
    
    # Resultados por prueba
    print(f"Resultados para {num_usuarios} usuarios ({isolation_level_name}):")
    print(f"  Reservas exitosas: {exitosos}")
    print(f"  Reservas fallidas: {fallidos}")
    print(f"  Tiempo promedio por reserva: {tiempo_promedio:.2f} ms")
    print(f"  Tiempo total de prueba: {total_time:.2f} ms")

def main():
    # Ejecutar pruebas para cada nivel de aislamiento
    for isolation_level_name in ISOLATION_LEVELS:
        print(f"\n{'='*80}")
        print(f"INICIANDO PRUEBAS PARA NIVEL: {isolation_level_name}")
        print(f"{'='*80}")
        
        for num_usuarios in NUM_USUARIOS:
            ejecutar_prueba(num_usuarios, isolation_level_name)
        
        # Mostrar tabla comparativa
        generar_tabla_resultados()
        resultados.clear()


main()