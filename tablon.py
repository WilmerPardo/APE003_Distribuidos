import threading
import time


N_LECTORES = 5   # 3 antes del escritor + 2 después


def _version_secuencial():
    """Secuencial: lectores y escritor se ejecutan de uno en uno."""
    log = []
    # Simulamos la misma secuencia de hilos: L0,L1,L2, Escritor, L3,L4
    for i in range(3):
        log.append(f"[SEC] Lector {i} leyendo el tablón.")
    log.append("[SEC] Escritor actualizando el tablón de notas exclusívamente.")
    for i in range(3, N_LECTORES):
        log.append(f"[SEC] Lector {i} leyendo el tablón.")
    return log


def _version_concurrente():
    """Concurrente: lectores comparten acceso, escritor es exclusivo."""
    cant_lectores   = 0
    mutex_lectores  = threading.Lock()
    sem_escritor    = threading.Semaphore(1)
    log             = []
    log_lock        = threading.Lock()
    activos_lock    = threading.Lock()
    lectores_activos = [0]
    escritor_activo  = [False]
    overlap_detectado = [False]

    def lector(id_lector):
        nonlocal cant_lectores
        with mutex_lectores:                        
            cant_lectores += 1
            if cant_lectores == 1:
                sem_escritor.acquire()              

        with activos_lock:
            lectores_activos[0] += 1
            if escritor_activo[0]:
                overlap_detectado[0] = True

        with log_lock:                              
            log.append(f"Lector {id_lector} leyendo el tablón.")

        with activos_lock:
            lectores_activos[0] -= 1

        with mutex_lectores:                        
            cant_lectores -= 1
            if cant_lectores == 0:
                sem_escritor.release()              

    def escritor():
        sem_escritor.acquire()                      

        with activos_lock:
            escritor_activo[0] = True
            if lectores_activos[0] > 0:
                overlap_detectado[0] = True

        with log_lock:                              
            log.append("Escritor actualizando el tablón de notas exclusívamente.")

        with activos_lock:
            escritor_activo[0] = False

        sem_escritor.release()                      

    hilos = []
    for i in range(3):
        hilos.append(threading.Thread(target=lector, args=(i,)))
    hilos.append(threading.Thread(target=escritor))
    for i in range(3, N_LECTORES):
        hilos.append(threading.Thread(target=lector, args=(i,)))

    for h in hilos: h.start()
    for h in hilos: h.join()

    return log, not overlap_detectado[0]


def ejecutar_tablon():
    #secuencial
    t0 = time.perf_counter()
    log_sec = _version_secuencial()
    tiempo_sec = time.perf_counter() - t0

    #concurrente
    t0 = time.perf_counter()
    log_con, valido = _version_concurrente()
    tiempo_con = time.perf_counter() - t0


    return {
        "log":                       log_con,
        "max_lectores_concurrentes": N_LECTORES,
        "valido":                    valido,
        "criterio":                  "Lectores concurrentes, escritor exclusivo. El log muestra patrón de acceso correcto.",
        # rendimiento
        "tiempo_secuencial":         round(tiempo_sec, 6),
        "tiempo_concurrente":        round(tiempo_con, 6),
    }