from threading import Thread
class BaseExperiment():
    """Базовый класс описания эксперимента"""
    def __init__(self):
        pass

    def init(self, title: str):
        print("Initialization experiment on thread...")

class Experiment(BaseExperiment):
    def __init__(self):
        super().__init__()
    
    def init(self):
        threading = Thread(target=self._thread_body)
        threading.start()

    def _thread_body(self):
        print("The experiment has been launched on thread #1.")
        try:
            print("Empty Body")
        except KeyboardInterrupt:
            print("thread is stopped")

    def before_init():
        print("Loading parameters before init...")
