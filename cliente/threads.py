import threading
from PySide6.QtCore import QObject, Signal

class Sinais(QObject):
    sucesso = Signal(object)
    erro = Signal(str)
    finalizado = Signal()

class Trabalhador(QObject):
    def __init__(self, fn, *args, **kwargs):
        super().__init__()
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.sinais = Sinais()
        self._thread = threading.Thread(target=self._run, daemon=True)

    def _run(self):
        try:
            resultado = self.fn(*self.args, **self.kwargs)
            self.sinais.sucesso.emit(resultado)
        except Exception as e:
            self.sinais.erro.emit(str(e))
        finally:
            self.sinais.finalizado.emit()

    def start(self):
        self._thread.start()
