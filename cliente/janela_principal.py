import sys
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTableWidget, QTableWidgetItem, QPushButton,
    QLabel, QLineEdit, QHeaderView, QMessageBox,
    QTabWidget, QAbstractItemView
)
from modelos import Cliente, Filme
from dialogos import DialogoAdicionarCliente, DialogoAdicionarFilme
from threads import Trabalhador
import api_cliente

class JanelaPrincipal(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Locadora de Filmes - Interface Inicial")
        self.setMinimumSize(850, 550)

        self.filmes = []
        self.clientes = []
        self.trabalhadores = []

        self.construir_interface()
        self.carregar_dados_completos()

    def construir_interface(self):
        widget_central = QWidget()
        self.setCentralWidget(widget_central)
        layout_central = QVBoxLayout(widget_central)

        self.abas = QTabWidget()
        layout_central.addWidget(self.abas)

        aba_filmes = QWidget()
        layout_f = QVBoxLayout(aba_filmes)

        box_acoes_f = QHBoxLayout()
        self.btn_novo_filme = QPushButton("Cadastrar Filme")
        self.btn_novo_filme.clicked.connect(self.abrir_dialogo_filme)
        self.btn_atualizar = QPushButton("Atualizar Dados")
        self.btn_atualizar.clicked.connect(self.carregar_dados_completos)
        box_acoes_f.addWidget(self.btn_novo_filme)
        box_acoes_f.addWidget(self.btn_atualizar)
        box_acoes_f.addStretch()
        layout_f.addLayout(box_acoes_f)

        box_busca_f = QHBoxLayout()
        box_busca_f.addWidget(QLabel("Pesquisar:"))
        self.busca_filme = QLineEdit()
        self.busca_filme.setPlaceholderText("Filtrar filmes por titulo ou genero...")
        self.busca_filme.textChanged.connect(self.filtrar_filmes)
        box_busca_f.addWidget(self.busca_filme)
        layout_f.addLayout(box_busca_f)

        self.tabela_filmes = self.criar_tabela(["Titulo", "Ano", "Genero", "Preco (R$)", "Quantidade"])
        self.tabela_filmes.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        for i in range(1, 5):
            self.tabela_filmes.horizontalHeader().setSectionResizeMode(i, QHeaderView.ResizeToContents)
        layout_f.addWidget(self.tabela_filmes)

        self.abas.addTab(aba_filmes, "Acervo de Filmes")

        aba_clientes = QWidget()
        layout_c = QVBoxLayout(aba_clientes)

        box_acoes_c = QHBoxLayout()
        self.btn_novo_cliente = QPushButton("Cadastrar Cliente")
        self.btn_novo_cliente.clicked.connect(self.abrir_dialogo_cliente)
        box_acoes_c.addWidget(self.btn_novo_cliente)
        box_acoes_c.addStretch()
        layout_c.addLayout(box_acoes_c)

        box_busca_c = QHBoxLayout()
        box_busca_c.addWidget(QLabel("Pesquisar:"))
        self.busca_cliente = QLineEdit()
        self.busca_cliente.setPlaceholderText("Filtrar clientes por nome ou CPF...")
        self.busca_cliente.textChanged.connect(self.filtrar_clientes)
        box_busca_c.addWidget(self.busca_cliente)
        layout_c.addLayout(box_busca_c)

        self.tabela_clientes = self.criar_tabela(["Nome", "CPF"])
        self.tabela_clientes.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.tabela_clientes.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        layout_c.addWidget(self.tabela_clientes)

        self.abas.addTab(aba_clientes, "Clientes")

    def criar_tabela(self, colunas):
        tabela = QTableWidget()
        tabela.setColumnCount(len(colunas))
        tabela.setHorizontalHeaderLabels(colunas)
        tabela.setSelectionBehavior(QAbstractItemView.SelectRows)
        tabela.setEditTriggers(QAbstractItemView.NoEditTriggers)
        return tabela

    def definir_botoes_habilitados(self, habilitado):
        self.btn_novo_filme.setEnabled(habilitado)
        self.btn_novo_cliente.setEnabled(habilitado)
        self.btn_atualizar.setEnabled(habilitado)

    def carregar_dados_completos(self):
        self.definir_botoes_habilitados(False)
        self.statusBar().showMessage("Carregando dados da API...")
        def rotina():
            c = api_cliente.listar_clientes()
            f = api_cliente.listar_filmes()
            return {"clientes": c, "filmes": f}

        t = Trabalhador(rotina)
        t.sinais.sucesso.connect(self.processar_dados_completos)
        t.sinais.erro.connect(self.mostrar_erro)
        t.sinais.finalizado.connect(lambda: self.finalizar_operacao(t))
        self.trabalhadores.append(t)
        t.start()

    def finalizar_operacao(self, t):
        self.definir_botoes_habilitados(True)
        self.limpar_trabalhador(t)

    def processar_dados_completos(self, dados):
        self.clientes.clear()
        for c in dados.get("clientes", []):
            self.clientes.append(Cliente(c["nome"], c["cpf"]))

        self.filmes.clear()
        for f in dados.get("filmes", []):
            self.filmes.append(
                Filme(f["titulo"], int(f["ano"]), f["genero"], float(f["preco"]), int(f["quantidade"]))
            )

        self.atualizar_tabela_clientes()
        self.atualizar_tabela_filmes()
        self.statusBar().showMessage("Dados atualizados da API com sucesso.", 3000)

    def mostrar_erro(self, erro):
        self.definir_botoes_habilitados(True)
        self.statusBar().showMessage(f"Erro: {erro}", 5000)
        QMessageBox.critical(self, "Erro", str(erro))

    def abrir_dialogo_cliente(self):
        dialogo = DialogoAdicionarCliente(self)
        dialogo.cliente_adicionado.connect(self.requisitar_cadastro_cliente)
        dialogo.exec()

    def requisitar_cadastro_cliente(self, cliente):
        self.definir_botoes_habilitados(False)
        self.statusBar().showMessage(f"Cadastrando {cliente.nome}...")
        t = Trabalhador(api_cliente.cadastrar_cliente, cliente.nome, cliente.cpf)
        t.sinais.sucesso.connect(lambda r: self.carregar_dados_completos())
        t.sinais.erro.connect(self.mostrar_erro)
        t.sinais.finalizado.connect(lambda: self.limpar_trabalhador(t))
        self.trabalhadores.append(t)
        t.start()

    def abrir_dialogo_filme(self):
        dialogo = DialogoAdicionarFilme(self)
        dialogo.filme_adicionado.connect(self.requisitar_cadastro_filme)
        dialogo.exec()

    def requisitar_cadastro_filme(self, filme):
        self.definir_botoes_habilitados(False)
        self.statusBar().showMessage(f"Cadastrando {filme.titulo}...")
        t = Trabalhador(
            api_cliente.cadastrar_filme,
            filme.titulo, filme.ano, filme.genero, filme.preco, filme.quantidade
        )
        t.sinais.sucesso.connect(lambda r: self.carregar_dados_completos())
        t.sinais.erro.connect(self.mostrar_erro)
        t.sinais.finalizado.connect(lambda: self.limpar_trabalhador(t))
        self.trabalhadores.append(t)
        t.start()

    def atualizar_tabela_filmes(self):
        self.filtrar_filmes(self.busca_filme.text())

    def filtrar_filmes(self, termo):
        termo = termo.strip().lower()
        self.tabela_filmes.setRowCount(0)
        filmes_filtrados = [
            f for f in self.filmes
            if termo in f.titulo.lower() or termo in f.genero.lower()
        ]
        for f in filmes_filtrados:
            row = self.tabela_filmes.rowCount()
            self.tabela_filmes.insertRow(row)
            self.tabela_filmes.setItem(row, 0, QTableWidgetItem(f.titulo))
            self.tabela_filmes.setItem(row, 1, QTableWidgetItem(str(f.ano)))
            self.tabela_filmes.setItem(row, 2, QTableWidgetItem(f.genero))
            self.tabela_filmes.setItem(row, 3, QTableWidgetItem(f"R$ {f.preco:.2f}"))
            self.tabela_filmes.setItem(row, 4, QTableWidgetItem(str(f.quantidade)))

    def atualizar_tabela_clientes(self):
        self.filtrar_clientes(self.busca_cliente.text())

    def filtrar_clientes(self, termo):
        termo = termo.strip().lower()
        self.tabela_clientes.setRowCount(0)
        clientes_filtrados = [
            c for c in self.clientes
            if termo in c.nome.lower() or termo in c.cpf.lower()
        ]
        for c in clientes_filtrados:
            row = self.tabela_clientes.rowCount()
            self.tabela_clientes.insertRow(row)
            self.tabela_clientes.setItem(row, 0, QTableWidgetItem(c.nome))
            self.tabela_clientes.setItem(row, 1, QTableWidgetItem(c.cpf))

    def limpar_trabalhador(self, t):
        if t in self.trabalhadores:
            self.trabalhadores.remove(t)

    def closeEvent(self, event):
        for t in self.trabalhadores:
            t.sinais.sucesso.disconnect()
            t.sinais.erro.disconnect()
            t.sinais.finalizado.disconnect()
        event.accept()
