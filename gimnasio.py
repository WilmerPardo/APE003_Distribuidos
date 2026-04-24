import threading
import time
import random

class MiSemaforo:
    def __init__(self, valor):
        self.contador    = valor
        self.cerrojo     = threading.Lock()
        self.cola_espera = threading.Condition(self.cerrojo)

    def esperar(self):
        with self.cerrojo:                          # BLOQUEAR(cerrojo)
            while self.contador == 0:
                self.cola_espera.wait()             # ESPERAR_CONDICION
            self.contador -= 1                      # contador <- contador - 1
                                                    # DESBLOQUEAR(cerrojo)

    def senial(self):
        with self.cerrojo:                          # BLOQUEAR(cerrojo)
            self.contador += 1                      # contador <- contador + 1
            self.cola_espera.notify()               # NOTIFICAR(cola_espera)
                                                    # DESBLOQUEAR(cerrojo)


def _simular_uso(id_atleta, log):
    log.append(f"Atleta {id_atleta} usando la máquina.")
    time.sleep(random.uniform(0.01, 0.05))
    log.append(f"Atleta {id_atleta} liberó la máquina.")


def _version_secuencial(N_ATLETAS):
    log = []
    for i in range(1, N_ATLETAS + 1):
        _simular_uso(i, log)
    return log


def _version_concurrente(N_ATLETAS, CAPACIDAD):
    semaforo = MiSemaforo(CAPACIDAD)
    log      = []
    log_lock = threading.Lock()
    uso_lock = threading.Lock()

    recursos_en_uso = [0]
    max_en_uso      = [0]   
    historial_uso   = []    

    def atleta(id_atleta):
        semaforo.esperar()                          

        with uso_lock:
            recursos_en_uso[0] += 1
            nivel = recursos_en_uso[0]
            if nivel > max_en_uso[0]:
                max_en_uso[0] = nivel
            historial_uso.append((id_atleta, "entra", nivel))

        with log_lock:
            log.append(
                f"Atleta {id_atleta} entra. "
                f"[en uso: {nivel}/{CAPACIDAD}]"
            )
            if nivel == max_en_uso[0] and nivel > 1:
                log.append(f"  >> Máximo alcanzado: {nivel} atletas simultáneos")

        time.sleep(random.uniform(0.01, 0.05))     

        with uso_lock:
            recursos_en_uso[0] -= 1
            nivel_sal = recursos_en_uso[0]
            historial_uso.append((id_atleta, "sale", nivel_sal))

        with log_lock:
            log.append(
                f"Atleta {id_atleta} sale.  "
                f"[en uso: {nivel_sal}/{CAPACIDAD}]"
            )

        semaforo.senial()                           # signal()

    hilos = [threading.Thread(target=atleta, args=(i,)) for i in range(1, N_ATLETAS + 1)]
    for h in hilos: h.start()
    for h in hilos: h.join()

    return log, max_en_uso[0], historial_uso


def ejecutar_gimnasio():
    CAPACIDAD = 3
    N_ATLETAS = 8

    # secuencial
    t0 = time.perf_counter()
    _version_secuencial(N_ATLETAS)
    tiempo_sec = time.perf_counter() - t0

    # concurrente
    t0 = time.perf_counter()
    log_con, max_en_uso, historial = _version_concurrente(N_ATLETAS, CAPACIDAD)
    tiempo_con = time.perf_counter() - t0

    valido      = max_en_uso <= CAPACIDAD

    # serie de valores de uso para graficar en el frontend
    serie_uso = [snap[2] for snap in historial]

    return {
        "log":              log_con,
        "max_en_uso":       max_en_uso,     
        "capacidad":        CAPACIDAD,
        "n_atletas":        N_ATLETAS,
        "serie_uso":        serie_uso,       
        "valido":           valido,
        "criterio":         f"resources_in_use nunca supera {CAPACIDAD}. Monitorear valor máximo alcanzado.",
        # rendimiento
        "tiempo_secuencial":  round(tiempo_sec, 6),
        "tiempo_concurrente": round(tiempo_con, 6),
        # comunicación
        "mecanismo_comunicacion": "Semáforo de Conteo (Mutex + Condition Variable)",
    }