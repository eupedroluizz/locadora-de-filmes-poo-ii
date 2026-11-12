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
        self.setMinimumSize(320, 160)

        layout_principal = QVBoxLayout(self)

        box_nome = QHBoxLayout()
        box_nome.addWidget(QLabel("Nome:"))
        self.campo_nome = QLineEdit()
        self.campo_nome.setMaxLength(150)
        box_nome.addWidget(self.campo_nome)
        layout_principal.addLayout(box_nome)

        box_cpf = QHBoxLayout()
        box_cpf.addWidget(QLabel("CPF:"))
        self.campo_cpf = QLineEdit()
        self.campo_cpf.setMaxLength(14)
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
            QMessageBox.warning(self, "Atencao", "Preencha todos os campos!")
            return

        if any(ch.isalpha() for ch in cpf):
            QMessageBox.warning(self, "Atencao", "O CPF deve conter apenas numeros, nao digite letras!")
            return

        caracteres_permitidos = set("0123456789.-")
        if not set(cpf).issubset(caracteres_permitidos):
            QMessageBox.warning(self, "Atencao", "O CPF nao pode conter simbolos ou caracteres especiais. Digite apenas numeros.")
            return

        digitos = "".join(ch for ch in cpf if ch.isdigit())
        if len(digitos) != 11:
            QMessageBox.warning(self, "Atencao", "O CPF deve conter exatamente 11 digitos numericos.")
            return

        self.cliente_adicionado.emit(Cliente(nome, digitos))
        self.accept()

class DialogoAdicionarFilme(QDialog):
    filme_adicionado = Signal(object)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Adicionar Filme")
        self.setMinimumSize(360, 270)

        layout_principal = QVBoxLayout(self)

        box_titulo = QHBoxLayout()
        box_titulo.addWidget(QLabel("Titulo:"))
        self.campo_titulo = QLineEdit()
        self.campo_titulo.setMaxLength(150)
        box_titulo.addWidget(self.campo_titulo)
        layout_principal.addLayout(box_titulo)

        box_ano = QHBoxLayout()
        box_ano.addWidget(QLabel("Ano:"))
        self.campo_ano = QSpinBox()
        self.campo_ano.setRange(1880, 2100)
        self.campo_ano.setValue(2026)
        box_ano.addWidget(self.campo_ano)
        layout_principal.addLayout(box_ano)

        box_genero = QHBoxLayout()
        box_genero.addWidget(QLabel("Genero:"))
        self.campo_genero = QComboBox()
        self.campo_genero.addItems([
            "Acao", "Comedia", "Drama", "Ficcao Cientifica",
            "Terror", "Romance", "Animacao", "Documentario", "Outro"
        ])
        box_genero.addWidget(self.campo_genero)
        layout_principal.addLayout(box_genero)

        box_preco = QHBoxLayout()
        box_preco.addWidget(QLabel("Preco (R$):"))
        self.campo_preco = QDoubleSpinBox()
        self.campo_preco.setRange(0.01, 999.99)
        self.campo_preco.setValue(10.00)
        self.campo_preco.setPrefix("R$ ")
        box_preco.addWidget(self.campo_preco)
        layout_principal.addLayout(box_preco)

        box_qtd = QHBoxLayout()
        box_qtd.addWidget(QLabel("Quantidade:"))
        self.campo_qtd = QSpinBox()
        self.campo_qtd.setRange(1, 9999)
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
            QMessageBox.warning(self, "Atencao", "O titulo do filme e obrigatorio!")
            return

        if preco <= 0:
            QMessageBox.warning(self, "Atencao", "O preco deve ser maior que zero!")
            return

        self.filme_adicionado.emit(Filme(titulo, ano, genero, preco, quantidade))
        self.accept()

class DialogoAlugarFilme(QDialog):
    aluguel_confirmado = Signal(object)

    def __init__(self, filme, clientes_disponiveis, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Alugar Filme")
        self.setMinimumSize(380, 180)

        layout_principal = QVBoxLayout(self)

        info_filme = QLabel(f"Filme: {filme.titulo} | Preco: R$ {filme.preco:.2f}")
        layout_principal.addWidget(info_filme)

        layout_principal.addWidget(QLabel("Selecione o Cliente:"))
        self.caixa_clientes = QComboBox()

        for c in clientes_disponiveis:
            self.caixa_clientes.addItem(f"{c.nome} (CPF: {c.cpf})", c)

        layout_principal.addWidget(self.caixa_clientes)

        box_botoes = QHBoxLayout()
        self.botao_confirmar = QPushButton("Confirmar")
        self.botao_cancelar = QPushButton("Cancelar")
        box_botoes.addWidget(self.botao_confirmar)
        box_botoes.addWidget(self.botao_cancelar)
        layout_principal.addLayout(box_botoes)

        self.botao_confirmar.clicked.connect(self.confirmar)
        self.botao_cancelar.clicked.connect(self.reject)

    def confirmar(self):
        cliente_selecionado = self.caixa_clientes.currentData()
        if not cliente_selecionado:
            QMessageBox.warning(self, "Atencao", "Nenhum cliente selecionado!")
            return

        self.aluguel_confirmado.emit(cliente_selecionado)
        self.accept()
