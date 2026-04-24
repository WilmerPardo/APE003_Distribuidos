import threading
import time

N_TOTAL = 5

def _version_secuencial():
    log = []
    # Fase 1
    for i in range(N_TOTAL):
        log.append(f"[SEC] Hilo {i} completó Fase 1.")
    log.append("[SEC] --- Todos en Fase 1 completos. Inicia Fase 2 ---")
    # Fase 2
    for i in range(N_TOTAL):
        log.append(f"[SEC] Hilo {i} iniciando Fase 2.")
    return log


def _version_concurrente():
    contador         = 0        #hilos q han terminado fase 1
    mtx_barrera      = threading.Lock()     #impide q 2 hilos no anoten al mismo tiempo
    var_cond_barrera = threading.Condition(mtx_barrera) #hilos esperan hasta q los despierten
    log              = []
    log_lock         = threading.Lock()
    fase2_iniciadas  = []

    def llegar_a_barrera(id_hilo):
        nonlocal contador

        with mtx_barrera:                      
            contador += 1
            with log_lock:
                log.append(f"Hilo {id_hilo} completó Fase 1. Esperando barrera...")

            if contador == N_TOTAL:         #el contador es 5? 
                with log_lock:
                    log.append("--- Último hilo alcanzó la barrera. Inicia Fase 2 ---")
                var_cond_barrera.notify_all()           #despiertan simultaneamente
            else:       
                while contador < N_TOTAL:   #no, los pone a dormir        
                    var_cond_barrera.wait()         

        fase2_iniciadas.append(id_hilo)
        with log_lock:
            log.append(f"Hilo {id_hilo} iniciando Fase 2.")

    hilos = [threading.Thread(target=llegar_a_barrera, args=(i,)) for i in range(N_TOTAL)]
    for h in hilos: h.start()
    for h in hilos: h.join()

    return log, len(fase2_iniciadas)


def ejecutar_barrera():
    #secuencial
    t0 = time.perf_counter()
    log_sec = _version_secuencial()
    tiempo_sec = time.perf_counter() - t0

    #concurrente
    t0 = time.perf_counter()
    log_con, hilos_fase2 = _version_concurrente()
    tiempo_con = time.perf_counter() - t0

    valido      = hilos_fase2 == N_TOTAL

    return {
        "log":         log_con,
        "n_total":     N_TOTAL,
        "hilos_fase2": hilos_fase2,
        "valido":      valido,
        "criterio":    "Todos los hilos esperan antes de Fase 2. Ningún hilo inicia Fase 2 antes de que todos lleguen.",
        # rendimiento
        "tiempo_secuencial":  round(tiempo_sec, 6),
        "tiempo_concurrente": round(tiempo_con, 6),
    }