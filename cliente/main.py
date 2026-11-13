import sys
import signal
from PySide6.QtWidgets import QApplication
from janela_principal import JanelaPrincipal

signal.signal(signal.SIGINT, signal.SIG_DFL)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    janela = JanelaPrincipal()
    janela.show()
    sys.exit(app.exec())
