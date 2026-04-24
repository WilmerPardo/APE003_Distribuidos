import threading
import time

def _version_secuencial(N_HILOS, M_VENTAS):
    #un solo hilo
    boletos = 0
    for _ in range(N_HILOS * M_VENTAS):
        boletos += 1
    return boletos


def _version_concurrente(N_HILOS, M_VENTAS):
    #mutex
    boletos_vendidos = 0
    cerrojo = threading.Lock()      #candado

    def ejecutar_venta():
        nonlocal boletos_vendidos   #modifica la externa
        for _ in range(M_VENTAS):
            with cerrojo:                       #bloquear cerrojo
                boletos_vendidos += 1           #incrementar atomico
                                                #desbloquear cerrojo
    hilos = []
    for _ in range(N_HILOS):
        h = threading.Thread(target=ejecutar_venta)
        hilos.append(h)
        h.start()

    for h in hilos:                           #pausa hasta q el hilo termine
        h.join()

    return boletos_vendidos


def ejecutar_taquilla():
    N_HILOS  = 5
    M_VENTAS = 1_000_000
    N_RUNS   = 10          # criterio: ejecutar 10 veces sin variacion
    esperado = N_HILOS * M_VENTAS

    #secuencial (1 sola vez como baseline)
    t0 = time.perf_counter()
    _version_secuencial(N_HILOS, M_VENTAS)
    tiempo_sec = time.perf_counter() - t0

    #concurrente — 10 ejecuciones para comprobar variacion
    resultados  = []
    tiempos_con = []

    for _ in range(N_RUNS):
        t0  = time.perf_counter()
        res = _version_concurrente(N_HILOS, M_VENTAS)
        tiempos_con.append(round(time.perf_counter() - t0, 6))
        resultados.append(res)

    variacion       = max(resultados) - min(resultados)
    todos_correctos = all(r == esperado for r in resultados)
    valido          = todos_correctos and variacion == 0
    tiempo_con_avg  = round(sum(tiempos_con) / N_RUNS, 6)

    return {
        # resultado
        "mensaje":          "Ventas Totales",
        "boletos_vendidos": resultados[-1],     # ultima ejecucion
        "esperado":         esperado,
        "n_runs":           N_RUNS,
        "resultados_runs":  resultados,         # historial de las 10
        "variacion":        variacion,
        "todos_correctos":  todos_correctos,
        "valido":           valido,
        "criterio":         "Counter siempre = N x M (5,000,000). Ejecutar 10 veces sin variacion.",
        # rendimiento
        "tiempo_secuencial":  round(tiempo_sec, 6),
        "tiempo_concurrente": tiempo_con_avg,   # promedio de 10 runs
        "tiempos_runs":       tiempos_con,      # detalle por run
    }