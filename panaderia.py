import threading
import time

N_PANES           = 5
CAPACIDAD_VITRINA = 10


def _version_secuencial():
    """Secuencial: primero produce TODOS los panes, luego el cliente los consume."""
    vitrina  = []
    log      = []
    producidos = []
    consumidos = []

    #produccion completa
    for i in range(N_PANES):
        pan = f"Pan {i}"
        vitrina.append(pan)
        producidos.append(pan)
        log.append(f"[SEC] Panadero horneó: {pan}")

    #consumo completo
    for _ in range(N_PANES):
        pan = vitrina.pop(0)
        consumidos.append(pan)
        log.append(f"[SEC] Cliente compró: {pan}")

    return log, producidos, consumidos


def _version_concurrente():
    """Concurrente: panadero y cliente operan en paralelo con semáforos + mutex."""
    espacios_vacios = threading.Semaphore(CAPACIDAD_VITRINA)  
    panes_listos    = threading.Semaphore(0)                   
    mutex_vitrina   = threading.Lock()                         
    vitrina    = []
    log        = []
    log_lock   = threading.Lock()
    producidos = []
    consumidos = []

    def panadero():
        for i in range(N_PANES):
            pan = f"Pan {i}"
            espacios_vacios.acquire()           
            with mutex_vitrina:                 
                vitrina.append(pan)
                producidos.append(pan)
                with log_lock:
                    log.append(f"Panadero horneó: {pan}")
                                                
            panes_listos.release()              

    def cliente():
        for _ in range(N_PANES):
            panes_listos.acquire()              
            with mutex_vitrina:                 
                pan = vitrina.pop(0)
                consumidos.append(pan)
                with log_lock:
                    log.append(f"Cliente compró: {pan}")
                                                
            espacios_vacios.release()           

    hp = threading.Thread(target=panadero)
    hc = threading.Thread(target=cliente)
    hp.start(); hc.start()
    hp.join();  hc.join()

    return log, producidos, consumidos


def ejecutar_panaderia():
    #secuencial
    t0 = time.perf_counter()
    log_sec, prod_sec, cons_sec = _version_secuencial()
    tiempo_sec = time.perf_counter() - t0

    #concurrente
    t0 = time.perf_counter()
    log_con, prod_con, cons_con = _version_concurrente()
    tiempo_con = time.perf_counter() - t0

    valido      = (set(prod_con) == set(cons_con)) and (len(prod_con) == len(cons_con))

    return {
        "log":        log_con,
        "producidos": len(prod_con),
        "consumidos": len(cons_con),
        "valido":     valido,
        "criterio":   "Todos los ítems producidos son consumidos. Verificar secuencia y completitud.",
        # rendimiento
        "tiempo_secuencial":  round(tiempo_sec, 6),
        "tiempo_concurrente": round(tiempo_con, 6),
    }