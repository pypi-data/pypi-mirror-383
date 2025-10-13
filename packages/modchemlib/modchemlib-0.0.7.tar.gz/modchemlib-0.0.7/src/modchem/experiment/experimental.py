from events import Events
class BaseExperiment():
    """Базовый класс описания эксперимента"""
    events = Events()
    def __init__(self):
        pass

    if __name__ == "__main__":
        print("Инициализация эксперимента")