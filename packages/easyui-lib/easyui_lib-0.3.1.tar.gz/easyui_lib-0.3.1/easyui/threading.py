"""
Módulo de threading para EasyUI.

Permite ejecutar la interfaz gráfica en un hilo separado para evitar
bloqueo del hilo principal y permitir procesamiento en background.
"""

import queue
import threading
import time
from contextlib import contextmanager
from typing import Any, Callable, Dict

# Queue para comunicación entre hilos
_ui_queue: queue.Queue[Any] = queue.Queue()
_background_tasks = {}
_task_counter = 0  # Definir aquí para acceso global


class UITask:
    """Representa una tarea que debe ejecutarse en el hilo de la interfaz."""

    def __init__(self, func: Callable, args: tuple = (), kwargs: dict = None):
        self.func = func
        self.args = args
        self.kwargs = kwargs or {}
        self.result = None
        self.completed = False


def run_in_ui_thread(func: Callable, *args, **kwargs) -> Any:
    """
    Ejecuta una función en el hilo de la interfaz gráfica.

    Args:
        func: Función a ejecutar
        *args: Argumentos posicionales
        **kwargs: Argumentos nombrados

    Returns:
        Resultado de la función
    """
    if threading.current_thread() == threading.main_thread():
        # Ya estamos en el hilo principal, ejecutar directamente
        return func(*args, **kwargs)
    else:
        # Crear tarea y enviar a la cola de la UI
        task = UITask(func, args, kwargs)

        # Enviar tarea a la cola de la UI
        _ui_queue.put(task)

        # Esperar resultado (bloqueante)
        while not task.completed:
            time.sleep(0.01)  # Pequeña pausa para no consumir CPU

        return task.result


def run_in_background(func: Callable, *args, daemon: bool = True, **kwargs) -> str:
    """
    Ejecuta una función en segundo plano.

    Args:
        func: Función a ejecutar en background
        *args: Argumentos posicionales
        daemon: Si el hilo debe ser daemon (termina cuando termina el hilo principal)
        **kwargs: Argumentos nombrados

    Returns:
        ID de la tarea para seguimiento
    """
    global _task_counter

    task_id = f"task_{_task_counter}"
    _task_counter += 1

    def wrapper():
        try:
            result = func(*args, **kwargs)
            _background_tasks[task_id] = {"status": "completed", "result": result}
        except Exception as e:
            _background_tasks[task_id] = {"status": "error", "error": str(e)}

    thread = threading.Thread(target=wrapper, daemon=daemon, name=task_id)
    thread.start()
    _background_tasks[task_id] = {"status": "running", "thread": thread}

    return task_id


def get_background_task_status(task_id: str) -> Dict[str, Any]:
    """
    Obtiene el estado de una tarea en background.

    Args:
        task_id: ID de la tarea

    Returns:
        Diccionario con el estado de la tarea
    """
    return _background_tasks.get(task_id, {"status": "not_found"})


def cancel_background_task(task_id: str) -> bool:
    """
    Cancela una tarea en background (si es posible).

    Args:
        task_id: ID de la tarea

    Returns:
        True si se pudo cancelar, False en caso contrario
    """
    task_info = _background_tasks.get(task_id)
    if task_info and task_info.get("status") == "running":
        thread = task_info.get("thread")
        if thread:
            # Nota: No podemos cancelar threads directamente en Python
            # pero podemos marcar como cancelado
            task_info["status"] = "cancelled"
            return True
    return False


def execute_after_delay(delay_ms: int, func: Callable, *args, **kwargs):
    """
    Ejecuta una función después de un retraso específico.

    Args:
        delay_ms: Retraso en milisegundos
        func: Función a ejecutar
        *args: Argumentos posicionales
        **kwargs: Argumentos nombrados
    """

    def delayed_func():
        time.sleep(delay_ms / 1000)
        run_in_ui_thread(func, *args, **kwargs)

    run_in_background(delayed_func, daemon=True)


def process_ui_queue():
    """
    Procesa la cola de tareas de la interfaz.
    Esta función debe llamarse periódicamente desde el hilo de la UI.
    """
    try:
        while True:
            task = _ui_queue.get_nowait()
            try:
                task.result = task.func(*task.args, **task.kwargs)
            except Exception as e:
                task.result = e
            finally:
                task.completed = True
    except queue.Empty:
        pass


@contextmanager
def ui_context():
    """
    Contexto que permite ejecutar código en el hilo de la UI de forma segura.
    """
    if threading.current_thread() == threading.main_thread():
        yield
    else:
        # Crear una cola de resultado
        result_queue = queue.Queue()

        def ui_func():
            try:
                yield
                result_queue.put(("success", None))
            except Exception as e:
                result_queue.put(("error", e))

        run_in_ui_thread(ui_func)

        # Esperar resultado
        status, value = result_queue.get()
        if status == "error":
            raise value


def schedule_repeating_task(interval_ms: int, func: Callable, *args, **kwargs) -> str:
    """
    Programa una tarea que se ejecuta repetidamente.

    Args:
        interval_ms: Intervalo en milisegundos
        func: Función a ejecutar
        *args: Argumentos posicionales
        **kwargs: Argumentos nombrados

    Returns:
        ID de la tarea para poder cancelarla
    """
    global _task_counter

    task_id = f"repeating_{_task_counter}"
    _task_counter += 1

    def repeating_wrapper():
        while (
            task_id in _background_tasks
            and _background_tasks[task_id].get("status") == "running"
        ):
            try:
                run_in_ui_thread(func, *args, **kwargs)
                time.sleep(interval_ms / 1000)
            except Exception as e:
                _background_tasks[task_id] = {"status": "error", "error": str(e)}
                break

    _background_tasks[task_id] = {"status": "running"}
    thread = threading.Thread(target=repeating_wrapper, daemon=True, name=task_id)
    thread.start()
    _background_tasks[task_id]["thread"] = thread

    return task_id


def stop_repeating_task(task_id: str):
    """
    Detiene una tarea repetitiva.

    Args:
        task_id: ID de la tarea a detener
    """
    if task_id in _background_tasks:
        _background_tasks[task_id]["status"] = "stopped"


# Funciones helper para el usuario
def async_button_action(func: Callable):
    """
    Decorador para hacer que las acciones de botones sean asíncronas.

    Args:
        func: Función a decorar

    Returns:
        Función wrapper que ejecuta en background
    """

    def wrapper(*args, **kwargs):
        def ui_feedback():
            # Aquí podrías mostrar un indicador de carga
            pass

        def background_work():
            try:
                result = func(*args, **kwargs)
                # Aquí podrías actualizar la UI con el resultado
                return result
            except Exception as e:
                # Aquí podrías mostrar un mensaje de error
                print(f"Error en tarea asíncrona: {e}")

        # Ejecutar en background
        run_in_background(background_work)

        # Mostrar feedback inmediato en UI
        run_in_ui_thread(ui_feedback)

    return wrapper


def wait_for_task(task_id: str, timeout: float = None) -> Dict[str, Any]:
    """
    Espera a que una tarea en background termine.

    Args:
        task_id: ID de la tarea
        timeout: Tiempo máximo de espera en segundos

    Returns:
        Estado final de la tarea
    """
    start_time = time.time()

    while timeout is None or (time.time() - start_time) < timeout:
        status = get_background_task_status(task_id)
        if status["status"] in ["completed", "error", "cancelled", "stopped"]:
            return status
        time.sleep(0.1)

    return {"status": "timeout"}


# Información de debug
def get_threading_info() -> Dict[str, Any]:
    """
    Obtiene información sobre el estado del threading.

    Returns:
        Diccionario con información de debug
    """
    return {
        "current_thread": threading.current_thread().name,
        "is_main_thread": threading.current_thread() == threading.main_thread(),
        "active_tasks": len(
            [t for t in _background_tasks.values() if t.get("status") == "running"]
        ),
        "total_tasks": len(_background_tasks),
        "ui_queue_size": _ui_queue.qsize(),
    }
