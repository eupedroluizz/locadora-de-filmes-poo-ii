import os
import datetime
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox,
    QToolBar, QStatusBar, QAbstractItemView, QTabWidget, QFileDialog,
    QLineEdit, QLabel
)
from PySide6.QtGui import QAction, QCloseEvent
from dialogos import DialogoAdicionarCliente, DialogoAdicionarFilme, DialogoAlugarFilme
from modelos import Cliente, Filme, Locacao
from arquivos import Trabalhador, salvar_dados, carregar_dados


class JanelaPrincipal(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Locadora de Filmes")
        self.setMinimumSize(800, 550)

        self.clientes = []
        self.filmes = []
        self.locacoes = []
        self.trabalhadores = []

        self.montar_menus()
        self.montar_abas()

        self.setStatusBar(QStatusBar())
        self.statusBar().showMessage("Sistema pronto.")

        #Somente para demonstarção
        """ self.cadastrar_cliente(Cliente("Jaiminho da Vila Santos", "067.123.897-67"))
        self.cadastrar_filme(Filme("Superman", 2025, "Ação", 12.00, 3))
        self.cadastrar_filme(Filme("Pelé: O Filme", 1978, "Ação", 25.00, 1))
        self.cadastrar_filme(Filme("It: A Coisa", 2017, "Terror", 7.00, 2))
        self.cadastrar_filme(Filme("Resident Evil", 2026, "Terror", 10.00, 5)) """

    def montar_menus(self):
        menu = self.menuBar().addMenu("Arquivo")

        btn_novo_filme = QAction("Adicionar Filme", self)
        btn_novo_filme.triggered.connect(self.abrir_dialogo_filme)
        menu.addAction(btn_novo_filme)

        btn_novo_cliente = QAction("Cadastrar Cliente", self)
        btn_novo_cliente.triggered.connect(self.abrir_dialogo_cliente)
        menu.addAction(btn_novo_cliente)

        menu.addSeparator()

        btn_salvar = QAction("Salvar Dados", self)
        btn_salvar.triggered.connect(self.acao_salvar_dados)
        menu.addAction(btn_salvar)

        btn_carregar = QAction("Carregar Dados", self)
        btn_carregar.triggered.connect(self.acao_carregar_dados)
        menu.addAction(btn_carregar)

        menu.addSeparator()

        btn_sair = QAction("Sair", self)
        btn_sair.triggered.connect(self.close)
        menu.addAction(btn_sair)

        ajuda = self.menuBar().addMenu("Ajuda")
        btn_sobre = QAction("Sobre", self)
        btn_sobre.triggered.connect(self.mostrar_sobre)
        ajuda.addAction(btn_sobre)

        barra = QToolBar("Atalhos")
        self.addToolBar(barra)
        barra.addAction(btn_novo_filme)
        barra.addAction(btn_novo_cliente)
        barra.addAction(btn_salvar)
        barra.addAction(btn_carregar)

    def montar_abas(self):
        central = QWidget()
        self.setCentralWidget(central)
        layout_base = QVBoxLayout(central)

        self.abas = QTabWidget()
        layout_base.addWidget(self.abas)

        tela_filmes = QWidget()
        layout_f = QVBoxLayout(tela_filmes)

        box_busca_filme = QHBoxLayout()
        box_busca_filme.addWidget(QLabel("Consultar Filme:"))
        self.busca_filme = QLineEdit()
        self.busca_filme.setPlaceholderText("Digite o título ou gênero para pesquisar...")
        self.busca_filme.textChanged.connect(self.filtrar_filmes)
        box_busca_filme.addWidget(self.busca_filme)
        layout_f.addLayout(box_busca_filme)

        self.tabela_filmes = self.criar_tabela(["Título", "Ano", "Gênero", "Preço", "Quantidade"])
        layout_f.addWidget(self.tabela_filmes)

        box_botoes_f = QHBoxLayout()
        btn_alugar = QPushButton("Alugar Filme Selecionado")
        btn_alugar.clicked.connect(self.abrir_alugar)
        box_botoes_f.addWidget(btn_alugar)

        btn_excluir_filme = QPushButton("Excluir Filme Selecionado")
        btn_excluir_filme.clicked.connect(self.excluir_filme)
        box_botoes_f.addWidget(btn_excluir_filme)
        layout_f.addLayout(box_botoes_f)

        self.abas.addTab(tela_filmes, "Filmes")

        tela_clientes = QWidget()
        layout_c = QVBoxLayout(tela_clientes)

        box_busca_cliente = QHBoxLayout()
        box_busca_cliente.addWidget(QLabel("Consultar Cliente:"))
        self.busca_cliente = QLineEdit()
        self.busca_cliente.setPlaceholderText("Digite o nome ou CPF para pesquisar...")
        self.busca_cliente.textChanged.connect(self.filtrar_clientes)
        box_busca_cliente.addWidget(self.busca_cliente)
        layout_c.addLayout(box_busca_cliente)

        self.tabela_clientes = self.criar_tabela(["Nome", "CPF"])
        layout_c.addWidget(self.tabela_clientes)

        btn_excluir_cliente = QPushButton("Excluir Cliente Selecionado")
        btn_excluir_cliente.clicked.connect(self.excluir_cliente)
        layout_c.addWidget(btn_excluir_cliente)

        self.abas.addTab(tela_clientes, "Clientes")

        tela_historico = QWidget()
        layout_h = QVBoxLayout(tela_historico)

        box_busca_loc = QHBoxLayout()
        box_busca_loc.addWidget(QLabel("Consultar Locação:"))
        self.busca_locacao = QLineEdit()
        self.busca_locacao.setPlaceholderText("Digite o filme ou cliente para pesquisar...")
        self.busca_locacao.textChanged.connect(self.filtrar_locacoes)
        box_busca_loc.addWidget(self.busca_locacao)
        layout_h.addLayout(box_busca_loc)

        self.tabela_historico = self.criar_tabela(["Filme Alugado", "Cliente", "Data"])
        layout_h.addWidget(self.tabela_historico)

        btn_excluir_locacao = QPushButton("Excluir Locação Selecionada")
        btn_excluir_locacao.clicked.connect(self.excluir_locacao)
        layout_h.addWidget(btn_excluir_locacao)

        self.abas.addTab(tela_historico, "Histórico de Locações")

    def criar_tabela(self, colunas):
        tabela = QTableWidget(0, len(colunas))
        tabela.setHorizontalHeaderLabels(colunas)
        tabela.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        tabela.setSelectionBehavior(QAbstractItemView.SelectRows)
        tabela.setEditTriggers(QAbstractItemView.NoEditTriggers)
        return tabela

    def filtrar_filmes(self, termo):
        termo = termo.strip().lower()
        for linha in range(self.tabela_filmes.rowCount()):
            item_titulo = self.tabela_filmes.item(linha, 0)
            item_genero = self.tabela_filmes.item(linha, 2)
            titulo = item_titulo.text().lower() if item_titulo else ""
            genero = item_genero.text().lower() if item_genero else ""
            corresponde = termo in titulo or termo in genero
            self.tabela_filmes.setRowHidden(linha, not corresponde)

    def filtrar_clientes(self, termo):
        termo = termo.strip().lower()
        for linha in range(self.tabela_clientes.rowCount()):
            item_nome = self.tabela_clientes.item(linha, 0)
            item_cpf = self.tabela_clientes.item(linha, 1)
            nome = item_nome.text().lower() if item_nome else ""
            cpf = item_cpf.text().lower() if item_cpf else ""
            corresponde = termo in nome or termo in cpf
            self.tabela_clientes.setRowHidden(linha, not corresponde)

    def filtrar_locacoes(self, termo):
        termo = termo.strip().lower()
        for linha in range(self.tabela_historico.rowCount()):
            item_filme = self.tabela_historico.item(linha, 0)
            item_cliente = self.tabela_historico.item(linha, 1)
            filme = item_filme.text().lower() if item_filme else ""
            cliente = item_cliente.text().lower() if item_cliente else ""
            corresponde = termo in filme or termo in cliente
            self.tabela_historico.setRowHidden(linha, not corresponde)

    def abrir_dialogo_cliente(self):
        janela = DialogoAdicionarCliente(self)
        janela.cliente_adicionado.connect(self.cadastrar_cliente)
        janela.exec()

    def cadastrar_cliente(self, cliente):
        for c in self.clientes:
            if c.cpf == cliente.cpf:
                QMessageBox.warning(self, "Atenção", f"Já existe um cliente cadastrado com o CPF {cliente.cpf}.")
                return

        self.clientes.append(cliente)
        self.atualizar_tabela_clientes()
        self.statusBar().showMessage(f"Cliente '{cliente.nome}' salvo com sucesso!", 3000)

    def atualizar_tabela_clientes(self):
        self.tabela_clientes.setRowCount(0)
        for cliente in self.clientes:
            linha = self.tabela_clientes.rowCount()
            self.tabela_clientes.insertRow(linha)
            self.tabela_clientes.setItem(linha, 0, QTableWidgetItem(cliente.nome))
            self.tabela_clientes.setItem(linha, 1, QTableWidgetItem(cliente.cpf))
        self.filtrar_clientes(self.busca_cliente.text())

    def excluir_cliente(self):
        selecionados = self.tabela_clientes.selectionModel().selectedRows()
        if not selecionados:
            QMessageBox.information(self, "Aviso", "Selecione um cliente para excluir.")
            return
        idx = selecionados[0].row()
        cliente_alvo = self.clientes[idx]

        for loc in self.locacoes:
            if loc.cliente.cpf == cliente_alvo.cpf:
                QMessageBox.warning(self, "Bloqueado", f"O cliente {cliente_alvo.nome} tem locações ativas e não pode ser excluído.")
                return

        cliente = self.clientes.pop(idx)
        self.atualizar_tabela_clientes()
        self.statusBar().showMessage(f"Cliente {cliente.nome} excluído.", 3000)

    def abrir_dialogo_filme(self):
        janela = DialogoAdicionarFilme(self)
        janela.filme_adicionado.connect(self.cadastrar_filme)
        janela.exec()

    def cadastrar_filme(self, filme):
        self.filmes.append(filme)
        self.atualizar_tabela_filmes()
        self.statusBar().showMessage(f"Filme '{filme.titulo}' salvo!", 3000)

    def atualizar_tabela_filmes(self):
        self.tabela_filmes.setRowCount(0)
        for filme in self.filmes:
            linha = self.tabela_filmes.rowCount()
            self.tabela_filmes.insertRow(linha)
            self.tabela_filmes.setItem(linha, 0, QTableWidgetItem(filme.titulo))
            self.tabela_filmes.setItem(linha, 1, QTableWidgetItem(str(filme.ano)))
            self.tabela_filmes.setItem(linha, 2, QTableWidgetItem(filme.genero))
            self.tabela_filmes.setItem(linha, 3, QTableWidgetItem(f"R$ {float(filme.preco):.2f}"))
            self.tabela_filmes.setItem(linha, 4, QTableWidgetItem(str(filme.quantidade)))
        self.filtrar_filmes(self.busca_filme.text())

    def excluir_filme(self):
        selecionados = self.tabela_filmes.selectionModel().selectedRows()
        if not selecionados:
            QMessageBox.information(self, "Aviso", "Selecione um filme para excluir.")
            return
        idx = selecionados[0].row()
        filme_alvo = self.filmes[idx]

        for loc in self.locacoes:
            if loc.filme.titulo == filme_alvo.titulo:
                QMessageBox.warning(self, "Bloqueado", f"O filme '{filme_alvo.titulo}' está alugado e não pode ser excluído.")
                return

        filme = self.filmes.pop(idx)
        self.atualizar_tabela_filmes()
        self.statusBar().showMessage(f"Filme {filme.titulo} excluído.", 3000)

    def abrir_alugar(self):
        selecionados = self.tabela_filmes.selectionModel().selectedRows()
        if not selecionados:
            QMessageBox.information(self, "Aviso", "Selecione um filme na tabela primeiro.")
            return
        if not self.clientes:
            QMessageBox.warning(self, "Aviso", "Você precisa cadastrar um cliente antes.")
            return

        idx = selecionados[0].row()
        filme = self.filmes[idx]

        if filme.quantidade <= 0:
            QMessageBox.warning(self, "Aviso", "Não há mais cópias disponíveis deste filme.")
            return

        janela = DialogoAlugarFilme(self.clientes, self)
        janela.aluguel_confirmado.connect(lambda cliente: self.efetuar_locacao(filme, cliente))
        janela.exec()

    def efetuar_locacao(self, filme, cliente):
        filme.quantidade -= 1
        self.atualizar_tabela_filmes()

        data_atual = datetime.date.today().strftime("%d/%m/%Y")
        locacao = Locacao(filme, cliente, data_atual)

        self.locacoes.append(locacao)
        self.atualizar_tabela_locacoes()
        QMessageBox.information(self, "Sucesso", f"O filme '{filme.titulo}' foi alugado para {cliente.nome}.")
        self.statusBar().showMessage("Aluguel finalizado.", 3000)

    def atualizar_tabela_locacoes(self):
        self.tabela_historico.setRowCount(0)
        for locacao in self.locacoes:
            linha = self.tabela_historico.rowCount()
            self.tabela_historico.insertRow(linha)
            self.tabela_historico.setItem(linha, 0, QTableWidgetItem(locacao.filme.titulo))
            self.tabela_historico.setItem(linha, 1, QTableWidgetItem(locacao.cliente.nome))
            self.tabela_historico.setItem(linha, 2, QTableWidgetItem(locacao.data))
        self.filtrar_locacoes(self.busca_locacao.text())

    def excluir_locacao(self):
        selecionados = self.tabela_historico.selectionModel().selectedRows()
        if not selecionados:
            QMessageBox.information(self, "Aviso", "Selecione uma locação para excluir.")
            return
        idx = selecionados[0].row()
        locacao = self.locacoes.pop(idx)

        locacao.filme.quantidade += 1

        self.atualizar_tabela_locacoes()
        self.atualizar_tabela_filmes()
        self.statusBar().showMessage("Locação cancelada e estoque restaurado.", 3000)

    def acao_salvar_dados(self):
        caminho, filtro = QFileDialog.getSaveFileName(
            self, "Salvar Dados", "", "JSON Files (*.json);;CSV Files (*.csv)"
        )
        if caminho:
            if not os.path.splitext(caminho)[1]:
                caminho += ".json" if "json" in filtro.lower() else ".csv"

            self.statusBar().showMessage("Salvando dados em segundo plano...")
            t = Trabalhador(
                salvar_dados,
                list(self.filmes),
                list(self.clientes),
                list(self.locacoes),
                caminho
            )
            t.sinais.sucesso.connect(self.mostrar_mensagem_salvar)
            t.sinais.erro.connect(self.mostrar_erro)
            t.sinais.finalizado.connect(lambda: self.limpar_trabalhador(t))
            self.trabalhadores.append(t)
            t.start()

    def acao_carregar_dados(self):
        caminho, _ = QFileDialog.getOpenFileName(
            self, "Carregar Dados", "", "JSON Files (*.json);;CSV Files (*.csv)"
        )
        if caminho:
            self.statusBar().showMessage("Carregando dados em segundo plano...")
            t = Trabalhador(carregar_dados, caminho)
            t.sinais.sucesso.connect(self.processar_dados_carregados)
            t.sinais.erro.connect(self.mostrar_erro)
            t.sinais.finalizado.connect(lambda: self.limpar_trabalhador(t))
            self.trabalhadores.append(t)
            t.start()

    def limpar_trabalhador(self, t):
        if t in self.trabalhadores:
            self.trabalhadores.remove(t)

    def mostrar_mensagem_salvar(self, msg):
        QMessageBox.information(self, "Salvar", str(msg))
        self.statusBar().showMessage(str(msg), 3000)

    def processar_dados_carregados(self, dados):
        self.filmes.clear()
        self.clientes.clear()
        self.locacoes.clear()

        for f in dados.get("filmes", []):
            self.filmes.append(
                Filme(f["titulo"], int(f["ano"]), f["genero"], float(f["preco"]), int(f["quantidade"]))
            )

        for c in dados.get("clientes", []):
            self.clientes.append(Cliente(c["nome"], c["cpf"]))

        for l in dados.get("locacoes", []):
            filme_obj = next((f for f in self.filmes if f.titulo == l["filme"]), Filme(l["filme"], 0, "", 0.0, 0))
            cliente_obj = next((c for c in self.clientes if c.cpf == l["cliente"]), Cliente(l["cliente"], l["cliente"]))
            self.locacoes.append(Locacao(filme_obj, cliente_obj, l["data"]))

        self.atualizar_tabela_filmes()
        self.atualizar_tabela_clientes()
        self.atualizar_tabela_locacoes()

        msg = "Dados carregados com sucesso."
        QMessageBox.information(self, "Carregar", msg)
        self.statusBar().showMessage(msg, 3000)

    def mostrar_erro(self, erro):
        QMessageBox.critical(self, "Erro", f"Ocorreu um erro: {erro}")
        self.statusBar().showMessage("Erro na operação de arquivo.", 3000)

    def closeEvent(self, evento: QCloseEvent):
        resposta = QMessageBox.question(
            self, 'Sair', 'Deseja sair do aplicativo?',
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        if resposta == QMessageBox.Yes:
            evento.accept()
        else:
            evento.ignore()

    def mostrar_sobre(self):
        QMessageBox.about(
            self, "Sobre o Sistema",
            "Locadora de Filmes\n\n"
            "Feito por:\n"
            "- Antônio Jonathan Santos Sátiro\n"
            "- Cauã Aquino Honorato Oliveira\n"
            "- Pedro Luiz Moura Marques"
        )