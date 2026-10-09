from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox,
    QToolBar, QStatusBar, QAbstractItemView, QTabWidget, QFileDialog
)
from PySide6.QtGui import QAction, QCloseEvent
from dialogos import DialogoAdicionarCliente, DialogoAdicionarFilme, DialogoAlugarFilme
from modelos import Cliente, Filme, Locacao
from arquivos import salvar_dados, carregar_dados


class JanelaPrincipal(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Locadora de Filmes")
        self.setMinimumSize(700, 500)


        self.clientes = []
        self.filmes = []
        self.locacoes = []

        self.montar_menus()
        self.montar_abas()
        
        self.setStatusBar(QStatusBar())
        self.statusBar().showMessage("Sistema pronto.")

        #Somente para demonstarção
        self.cadastrar_cliente(Cliente("Jaiminho da Vila Santos", "067.123.897-67"))
        self.cadastrar_filme(Filme("Superman", 2025, "Ação", 12.00, 3))
        self.cadastrar_filme(Filme("Pelé: O Filme", 1978, "Ação", 25.00, 1))
        self.cadastrar_filme(Filme("It: A Coisa", 2017, "Terror", 7.00, 2))
        self.cadastrar_filme(Filme("Resident Evil", 2026, "Terror", 10.00, 5))

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
        
        self.tabela_filmes = self.criar_tabela(["Título", "Ano", "Genero", "Preço", "Quantidade"])
        layout_f.addWidget(self.tabela_filmes)

        btn_alugar = QPushButton("Alugar Filme Selecionado")
        btn_alugar.clicked.connect(self.abrir_alugar)
        layout_f.addWidget(btn_alugar)

        btn_excluir_filme = QPushButton("Excluir Filme Selecionado")
        btn_excluir_filme.clicked.connect(self.excluir_filme)
        layout_f.addWidget(btn_excluir_filme)
        
        self.abas.addTab(tela_filmes, "Filmes")


        tela_clientes = QWidget()
        layout_c = QVBoxLayout(tela_clientes)
        
        self.tabela_clientes = self.criar_tabela(["Nome", "CPF"])
        layout_c.addWidget(self.tabela_clientes)

        btn_excluir_cliente = QPushButton("Excluir Cliente Selecionado")
        btn_excluir_cliente.clicked.connect(self.excluir_cliente)
        layout_c.addWidget(btn_excluir_cliente)
        
        self.abas.addTab(tela_clientes, "Clientes")


        tela_historico = QWidget()
        layout_h = QVBoxLayout(tela_historico)
        
        self.tabela_historico = self.criar_tabela(["Filme Alugado", "Cliente", "Data"])
        layout_h.addWidget(self.tabela_historico)

        btn_excluir_locacao = QPushButton("Excluir Locacao Selecionada")
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


    def abrir_dialogo_cliente(self):
        janela = DialogoAdicionarCliente(self)
        janela.cliente_adicionado.connect(self.cadastrar_cliente)
        janela.exec()

    def cadastrar_cliente(self, cliente):
        self.clientes.append(cliente)
        linha = self.tabela_clientes.rowCount()
        self.tabela_clientes.insertRow(linha)
        self.tabela_clientes.setItem(linha, 0, QTableWidgetItem(cliente.nome))
        self.tabela_clientes.setItem(linha, 1, QTableWidgetItem(cliente.cpf))
        self.statusBar().showMessage(f"{cliente.nome} salvo, com sucesso!", 3000)

    def atualizar_tabela_clientes(self):
        self.tabela_clientes.setRowCount(0)
        for cliente in self.clientes:
            linha = self.tabela_clientes.rowCount()
            self.tabela_clientes.insertRow(linha)
            self.tabela_clientes.setItem(linha, 0, QTableWidgetItem(cliente.nome))
            self.tabela_clientes.setItem(linha, 1, QTableWidgetItem(cliente.cpf))

    def excluir_cliente(self):
        selecionados = self.tabela_clientes.selectionModel().selectedRows()
        if not selecionados:
            QMessageBox.information(self, "Aviso", "Selecione um cliente para excluir.")
            return
        idx = selecionados[0].row()
        cliente = self.clientes.pop(idx)
        self.atualizar_tabela_clientes()
        self.statusBar().showMessage(f"Cliente {cliente.nome} excluido.", 3000)

    def abrir_dialogo_filme(self):
        janela = DialogoAdicionarFilme(self)
        janela.filme_adicionado.connect(self.cadastrar_filme)
        janela.exec()

    def cadastrar_filme(self, filme):
        self.filmes.append(filme)
        linha = self.tabela_filmes.rowCount()
        self.tabela_filmes.insertRow(linha)
        self.tabela_filmes.setItem(linha, 0, QTableWidgetItem(filme.titulo))
        self.tabela_filmes.setItem(linha, 1, QTableWidgetItem(str(filme.ano)))
        self.tabela_filmes.setItem(linha, 2, QTableWidgetItem(filme.genero))
        self.tabela_filmes.setItem(linha, 3, QTableWidgetItem(f"R$ {filme.preco:.2f}"))
        self.tabela_filmes.setItem(linha, 4, QTableWidgetItem(str(filme.quantidade)))
        self.statusBar().showMessage(f"{filme.titulo} salvo!", 3000)

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

    def excluir_filme(self):
        selecionados = self.tabela_filmes.selectionModel().selectedRows()
        if not selecionados:
            QMessageBox.information(self, "Aviso", "Selecione um filme para excluir.")
            return
        idx = selecionados[0].row()
        filme = self.filmes.pop(idx)
        self.atualizar_tabela_filmes()
        self.statusBar().showMessage(f"Filme {filme.titulo} excluido.", 3000)

    def abrir_alugar(self):
        selecionados = self.tabela_filmes.selectionModel().selectedRows()
        if not selecionados:
            QMessageBox.information(self, "Atenção!", "Selecione um filme na tabela primeiro.")
            return

        if not self.clientes:
            QMessageBox.warning(self, "Atenção!!", "Você precisa cadastrar um cliente antes.")
            return

        idx = selecionados[0].row()
        filme = self.filmes[idx]

        if filme.quantidade <= 0:
            QMessageBox.warning(self, "Esgotado", "Não temos mais cópias deste filme,")
            return

        janela = DialogoAlugarFilme(self.clientes, self)
        janela.aluguel_confirmado.connect(lambda cliente: self.efetuar_locacao(filme, cliente, idx))
        janela.exec()

    def efetuar_locacao(self, filme, cliente, linha_tabela):
        filme.quantidade -= 1
        

        celula_qtd = self.tabela_filmes.item(linha_tabela, 4)
        celula_qtd.setText(str(filme.quantidade))


        locacao = Locacao(filme, cliente, "Hoje")
        self.locacoes.append(locacao)

        linha = self.tabela_historico.rowCount()
        self.tabela_historico.insertRow(linha)
        self.tabela_historico.setItem(linha, 0, QTableWidgetItem(locacao.filme.titulo))
        self.tabela_historico.setItem(linha, 1, QTableWidgetItem(locacao.cliente.nome))
        self.tabela_historico.setItem(linha, 2, QTableWidgetItem(locacao.data))

        QMessageBox.information(self, "Sucesso!", f"O filme {filme.titulo} foi alugado para {cliente.nome}.")
        self.statusBar().showMessage("Aluguel finalizada.", 3000)

    def atualizar_tabela_locacoes(self):
        self.tabela_historico.setRowCount(0)
        for locacao in self.locacoes:
            linha = self.tabela_historico.rowCount()
            self.tabela_historico.insertRow(linha)
            self.tabela_historico.setItem(linha, 0, QTableWidgetItem(locacao.filme.titulo))
            self.tabela_historico.setItem(linha, 1, QTableWidgetItem(locacao.cliente.nome))
            self.tabela_historico.setItem(linha, 2, QTableWidgetItem(locacao.data))

    def excluir_locacao(self):
        selecionados = self.tabela_historico.selectionModel().selectedRows()
        if not selecionados:
            QMessageBox.information(self, "Aviso", "Selecione uma locacao para excluir.")
            return
        idx = selecionados[0].row()
        locacao = self.locacoes.pop(idx)
        self.atualizar_tabela_locacoes()
        self.statusBar().showMessage("Locacao excluida.", 3000)

    def acao_salvar_dados(self):
        caminho, _ = QFileDialog.getSaveFileName(self, "Salvar Dados", "", "JSON Files (*.json);;CSV Files (*.csv)")
        if caminho:
            try:
                msg = salvar_dados(self.filmes, self.clientes, self.locacoes, caminho)
                QMessageBox.information(self, "Salvar", msg)
                self.statusBar().showMessage(msg, 3000)
            except Exception as e:
                QMessageBox.critical(self, "Erro", f"Ocorreu um erro: {str(e)}")

    def acao_carregar_dados(self):
        caminho, _ = QFileDialog.getOpenFileName(self, "Carregar Dados", "", "JSON Files (*.json);;CSV Files (*.csv)")
        if caminho:
            try:
                dados = carregar_dados(caminho)
                self.filmes.clear()
                self.clientes.clear()
                self.locacoes.clear()
                
                for f in dados.get("filmes", []):
                    self.filmes.append(Filme(f["titulo"], int(f["ano"]), f["genero"], float(f["preco"]), int(f["quantidade"])))
                    
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
            except Exception as e:
                QMessageBox.critical(self, "Erro", f"Ocorreu um erro: {str(e)}")

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
        QMessageBox.about(self, "Sobre o Sistema", 
                          "Locadora de Filmes\n\n"
                          "Feito por:\n"
                          "- Antônio Jonathan Santos Sátiro\n"
                          "- Cauã Aquino Honorato Oliveira\n"
                          "- Pedro Luiz Moura Marques")
