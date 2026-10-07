from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QMessageBox, QComboBox, QSpinBox, QDoubleSpinBox
)
from PySide6.QtCore import Signal
from modelos import Cliente, Filme


class DialogoAdicionarCliente(QDialog):
    cliente_adicionado = Signal(object)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Cadastrar Cliente")
        self.setFixedSize(300, 150)

        layout_principal = QVBoxLayout(self)

        box_nome = QHBoxLayout()
        box_nome.addWidget(QLabel("Nome:"))
        self.campo_nome = QLineEdit()
        box_nome.addWidget(self.campo_nome)
        layout_principal.addLayout(box_nome)

        box_cpf = QHBoxLayout()
        box_cpf.addWidget(QLabel("CPF:"))
        self.campo_cpf = QLineEdit()
        self.campo_cpf.setPlaceholderText("000.000.000-00")
        box_cpf.addWidget(self.campo_cpf)
        layout_principal.addLayout(box_cpf)


        box_botoes = QHBoxLayout()
        self.botao_salvar = QPushButton("Salvar")
        self.botao_cancelar = QPushButton("Cancelar")
        box_botoes.addWidget(self.botao_salvar)
        box_botoes.addWidget(self.botao_cancelar)
        layout_principal.addLayout(box_botoes)

        self.botao_salvar.clicked.connect(self.salvar)
        self.botao_cancelar.clicked.connect(self.reject)

    def salvar(self):
        nome = self.campo_nome.text().strip()
        cpf = self.campo_cpf.text().strip()

        if not nome or not cpf:
            QMessageBox.warning(self, "Atenção", "Preencha todos os campos!")
            return

        self.cliente_adicionado.emit(Cliente(nome, cpf))
        self.accept()


class DialogoAdicionarFilme(QDialog):
    filme_adicionado = Signal(object)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Adicionar Filme")
        self.setFixedSize(350, 250)

        layout_principal = QVBoxLayout(self)


        box_titulo = QHBoxLayout()
        box_titulo.addWidget(QLabel("Título:"))
        self.campo_titulo = QLineEdit()
        box_titulo.addWidget(self.campo_titulo)
        layout_principal.addLayout(box_titulo)


        box_ano = QHBoxLayout()
        box_ano.addWidget(QLabel("Ano:"))
        self.campo_ano = QSpinBox()
        self.campo_ano.setRange(1900, 2100)
        self.campo_ano.setValue(2025)
        box_ano.addWidget(self.campo_ano)
        layout_principal.addLayout(box_ano)


        box_genero = QHBoxLayout()
        box_genero.addWidget(QLabel("Gênero:"))
        self.campo_genero = QComboBox()
        self.campo_genero.addItems(["Ação", "Comédia", "Drama", "Ficção", "Terror"])
        box_genero.addWidget(self.campo_genero)
        layout_principal.addLayout(box_genero)


        box_preco = QHBoxLayout()
        box_preco.addWidget(QLabel("Preço:"))
        self.campo_preco = QDoubleSpinBox()
        self.campo_preco.setRange(0.0, 999.99)
        self.campo_preco.setValue(10.00)
        box_preco.addWidget(self.campo_preco)
        layout_principal.addLayout(box_preco)


        box_qtd = QHBoxLayout()
        box_qtd.addWidget(QLabel("Quantidade:"))
        self.campo_qtd = QSpinBox()
        self.campo_qtd.setRange(1, 100)
        self.campo_qtd.setValue(1)
        box_qtd.addWidget(self.campo_qtd)
        layout_principal.addLayout(box_qtd)


        box_botoes = QHBoxLayout()
        self.botao_salvar = QPushButton("Salvar")
        self.botao_cancelar = QPushButton("Cancelar")
        box_botoes.addWidget(self.botao_salvar)
        box_botoes.addWidget(self.botao_cancelar)
        layout_principal.addLayout(box_botoes)

        self.botao_salvar.clicked.connect(self.salvar)
        self.botao_cancelar.clicked.connect(self.reject)

    def salvar(self):
        titulo = self.campo_titulo.text().strip()
        ano = self.campo_ano.value()
        genero = self.campo_genero.currentText()
        preco = self.campo_preco.value()
        quantidade = self.campo_qtd.value()

        if not titulo:
            QMessageBox.warning(self, "Atenção.", "O título é obrigatório!")
            return

        self.filme_adicionado.emit(Filme(titulo, ano, genero, preco, quantidade))
        self.accept()


class DialogoAlugarFilme(QDialog):
    aluguel_confirmado = Signal(object)

    def __init__(self, clientes_disponiveis, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Alugar Filme")
        self.setFixedSize(300, 150)

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Para qual cliente?"))

        self.caixa_clientes = QComboBox()
        for cliente in clientes_disponiveis:
            self.caixa_clientes.addItem(f"{cliente.nome} (CPF: {cliente.cpf})", cliente)
        
        layout.addWidget(self.caixa_clientes)

        box_botoes = QHBoxLayout()
        self.botao_confirmar = QPushButton("Confirmar")
        self.botao_cancelar = QPushButton("Cancelar")
        box_botoes.addWidget(self.botao_confirmar)
        box_botoes.addWidget(self.botao_cancelar)
        layout.addLayout(box_botoes)

        self.botao_confirmar.clicked.connect(self.confirmar)
        self.botao_cancelar.clicked.connect(self.reject)

    def confirmar(self):
        if self.caixa_clientes.count() == 0:
            QMessageBox.warning(self, "Atenção", "Cadastre um cliente primeiro, por favor.")
            return
            
        cliente_escolhido = self.caixa_clientes.currentData()
        self.aluguel_confirmado.emit(cliente_escolhido)
        self.accept()
