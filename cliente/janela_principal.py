import datetime
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox,
    QToolBar, QStatusBar, QAbstractItemView, QTabWidget, QFileDialog,
    QLineEdit, QLabel
)
from PySide6.QtGui import QAction, QCloseEvent
from PySide6.QtCore import Qt
from dialogos import DialogoAdicionarCliente, DialogoAdicionarFilme, DialogoAlugarFilme
from modelos import Cliente, Filme, Locacao
from threads import Trabalhador
from exportacao import exportar_dados_json, exportar_dados_csv
import api_cliente

class JanelaPrincipal(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Locadora de Filmes - Trabalho 03")
        self.setMinimumSize(850, 580)

        self.clientes = []
        self.filmes = []
        self.locacoes = []
        self.trabalhadores = []
        self._fechando = False

        self.montar_menus()
        self.montar_abas()

        self.setStatusBar(QStatusBar())
        self.statusBar().showMessage("Conectando a API...")

        self.carregar_dados_completos()

    def montar_menus(self):
        menu = self.menuBar().addMenu("Arquivo")

        self.btn_novo_filme = QAction("Adicionar Filme", self)
        self.btn_novo_filme.triggered.connect(self.abrir_dialogo_filme)
        menu.addAction(self.btn_novo_filme)

        self.btn_novo_cliente = QAction("Cadastrar Cliente", self)
        self.btn_novo_cliente.triggered.connect(self.abrir_dialogo_cliente)
        menu.addAction(self.btn_novo_cliente)

        menu.addSeparator()

        self.btn_atualizar = QAction("Atualizar Dados", self)
        self.btn_atualizar.triggered.connect(self.carregar_dados_completos)
        menu.addAction(self.btn_atualizar)

        menu.addSeparator()

        self.btn_exportar_json = QAction("Exportar Dados (JSON)", self)
        self.btn_exportar_json.triggered.connect(self.acao_exportar_json)
        menu.addAction(self.btn_exportar_json)

        self.btn_exportar_csv = QAction("Exportar Relatorio (CSV)", self)
        self.btn_exportar_csv.triggered.connect(self.acao_exportar_csv)
        menu.addAction(self.btn_exportar_csv)

        menu.addSeparator()

        btn_sair = QAction("Sair", self)
        btn_sair.triggered.connect(self.close)
        menu.addAction(btn_sair)

        menu_ajuda = self.menuBar().addMenu("Ajuda")
        btn_sobre = QAction("Sobre", self)
        btn_sobre.triggered.connect(self.mostrar_sobre)
        menu_ajuda.addAction(btn_sobre)

        barra = QToolBar("Barra de Ferramentas")
        self.addToolBar(barra)
        barra.addAction(self.btn_novo_filme)
        barra.addAction(self.btn_novo_cliente)
        barra.addAction(self.btn_atualizar)
        barra.addAction(self.btn_exportar_json)
        barra.addAction(self.btn_exportar_csv)

    def montar_abas(self):
        self.abas = QTabWidget()
        self.setCentralWidget(self.abas)

        aba_filmes = QWidget()
        layout_f = QVBoxLayout(aba_filmes)

        box_busca_f = QHBoxLayout()
        box_busca_f.addWidget(QLabel("Pesquisar:"))
        self.busca_filme = QLineEdit()
        self.busca_filme.setPlaceholderText("Filtrar filmes por titulo, genero ou ano...")
        self.busca_filme.textChanged.connect(self.filtrar_filmes)
        box_busca_f.addWidget(self.busca_filme)
        layout_f.addLayout(box_busca_f)

        self.tabela_filmes = self.criar_tabela(["Titulo", "Ano", "Genero", "Preco", "Quantidade"])
        self.tabela_filmes.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.tabela_filmes.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.tabela_filmes.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.tabela_filmes.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        self.tabela_filmes.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeToContents)
        layout_f.addWidget(self.tabela_filmes)

        box_acoes_f = QHBoxLayout()
        self.btn_alugar = QPushButton("Alugar Filme Selecionado")
        self.btn_alugar.clicked.connect(self.abrir_alugar)
        box_acoes_f.addWidget(self.btn_alugar)

        self.btn_excluir_f = QPushButton("Excluir Filme Selecionado")
        self.btn_excluir_f.clicked.connect(self.excluir_filme)
        box_acoes_f.addWidget(self.btn_excluir_f)
        layout_f.addLayout(box_acoes_f)

        self.abas.addTab(aba_filmes, "Filmes")

        aba_clientes = QWidget()
        layout_c = QVBoxLayout(aba_clientes)

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

        self.btn_excluir_c = QPushButton("Excluir Cliente Selecionado")
        self.btn_excluir_c.clicked.connect(self.excluir_cliente)
        layout_c.addWidget(self.btn_excluir_c)

        self.abas.addTab(aba_clientes, "Clientes")

        aba_historico = QWidget()
        layout_h = QVBoxLayout(aba_historico)

        box_busca_h = QHBoxLayout()
        box_busca_h.addWidget(QLabel("Pesquisar:"))
        self.busca_locacao = QLineEdit()
        self.busca_locacao.setPlaceholderText("Filtrar locacoes por cliente, filme ou data...")
        self.busca_locacao.textChanged.connect(self.filtrar_locacoes)
        box_busca_h.addWidget(self.busca_locacao)
        layout_h.addLayout(box_busca_h)

        self.tabela_historico = self.criar_tabela(["Filme", "Cliente", "CPF", "Data"])
        self.tabela_historico.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.tabela_historico.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.tabela_historico.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.tabela_historico.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        layout_h.addWidget(self.tabela_historico)

        self.btn_excluir_h = QPushButton("Excluir Locacao Selecionada")
        self.btn_excluir_h.clicked.connect(self.excluir_locacao)
        layout_h.addWidget(self.btn_excluir_h)

        self.abas.addTab(aba_historico, "Historico de Locacoes")

    def criar_tabela(self, colunas):
        tabela = QTableWidget()
        tabela.setColumnCount(len(colunas))
        tabela.setHorizontalHeaderLabels(colunas)
        tabela.setSelectionBehavior(QAbstractItemView.SelectRows)
        tabela.setSelectionMode(QAbstractItemView.SingleSelection)
        tabela.setEditTriggers(QAbstractItemView.NoEditTriggers)
        return tabela

    def definir_botoes_habilitados(self, habilitado):
        self.btn_alugar.setEnabled(habilitado)
        self.btn_excluir_f.setEnabled(habilitado)
        self.btn_excluir_c.setEnabled(habilitado)
        self.btn_excluir_h.setEnabled(habilitado)
        self.btn_novo_filme.setEnabled(habilitado)
        self.btn_novo_cliente.setEnabled(habilitado)
        self.btn_atualizar.setEnabled(habilitado)
        if hasattr(self, "btn_exportar_json"):
            self.btn_exportar_json.setEnabled(habilitado)
        if hasattr(self, "btn_exportar_csv"):
            self.btn_exportar_csv.setEnabled(habilitado)

    def carregar_dados_completos(self):
        self.definir_botoes_habilitados(False)
        self.statusBar().showMessage("Carregando dados da API...")
        def rotina():
            c = api_cliente.listar_clientes()
            f = api_cliente.listar_filmes()
            l = api_cliente.listar_locacoes()
            return {"clientes": c, "filmes": f, "locacoes": l}

        t = Trabalhador(rotina)
        t.sinais.sucesso.connect(self.processar_dados_completos, Qt.QueuedConnection)
        t.sinais.erro.connect(self.mostrar_erro, Qt.QueuedConnection)
        t.sinais.finalizado.connect(self.finalizar_carregamento, Qt.QueuedConnection)
        self.trabalhadores.append(t)
        t.start()

    def finalizar_carregamento(self):
        sinais = self.sender()
        t = sinais.parent() if sinais is not None else None
        if not self._fechando:
            self.definir_botoes_habilitados(True)
        self.limpar_trabalhador(t)

    def ao_concluir_mutacao(self, _resultado):
        if self._fechando:
            return
        self.carregar_dados_completos()

    def finalizar_mutacao(self):
        sinais = self.sender()
        t = sinais.parent() if sinais is not None else None
        self.limpar_trabalhador(t)

    def processar_dados_completos(self, dados):
        if self._fechando:
            return
        self.clientes.clear()
        for c in dados.get("clientes", []):
            self.clientes.append(Cliente(c["nome"], c["cpf"]))

        self.filmes.clear()
        for f in dados.get("filmes", []):
            self.filmes.append(
                Filme(f["titulo"], int(f["ano"]), f["genero"], float(f["preco"]), int(f["quantidade"]))
            )

        self.locacoes.clear()
        for l in dados.get("locacoes", []):
            c_obj = next((c for c in self.clientes if c.cpf == l["cliente_cpf"]), Cliente(l["cliente_nome"], l["cliente_cpf"]))
            f_obj = next((f for f in self.filmes if f.titulo == l["filme_titulo"]), Filme(l["filme_titulo"], 0, "", 0.0, 0))
            self.locacoes.append(Locacao(f_obj, c_obj, l["data"], l["id"]))

        self.atualizar_tabela_clientes()
        self.atualizar_tabela_filmes()
        self.atualizar_tabela_locacoes()
        self.statusBar().showMessage("Dados atualizados da API com sucesso.", 3000)

    def abrir_dialogo_cliente(self):
        dialogo = DialogoAdicionarCliente(self)
        dialogo.cliente_adicionado.connect(self.requisitar_cadastro_cliente)
        dialogo.exec()

    def requisitar_cadastro_cliente(self, cliente):
        self.definir_botoes_habilitados(False)
        self.statusBar().showMessage(f"Cadastrando {cliente.nome}...")
        t = Trabalhador(api_cliente.cadastrar_cliente, cliente.nome, cliente.cpf)
        t.sinais.sucesso.connect(self.ao_concluir_mutacao, Qt.QueuedConnection)
        t.sinais.erro.connect(self.mostrar_erro, Qt.QueuedConnection)
        t.sinais.finalizado.connect(self.finalizar_mutacao, Qt.QueuedConnection)
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
        t.sinais.sucesso.connect(self.ao_concluir_mutacao, Qt.QueuedConnection)
        t.sinais.erro.connect(self.mostrar_erro, Qt.QueuedConnection)
        t.sinais.finalizado.connect(self.finalizar_mutacao, Qt.QueuedConnection)
        self.trabalhadores.append(t)
        t.start()

    def abrir_alugar(self):
        linhas = self.tabela_filmes.selectionModel().selectedRows()
        if not linhas:
            QMessageBox.information(self, "Aviso", "Selecione um filme para alugar.")
            return

        idx = linhas[0].row()
        item_titulo = self.tabela_filmes.item(idx, 0)
        if not item_titulo:
            return
        filme_titulo = item_titulo.text()
        filme_selecionado = next((f for f in self.filmes if f.titulo == filme_titulo), None)

        if not filme_selecionado:
            return

        if filme_selecionado.quantidade <= 0:
            QMessageBox.warning(self, "Aviso", "Nao ha exemplares disponiveis deste filme.")
            return

        if not self.clientes:
            QMessageBox.warning(self, "Aviso", "Nenhum cliente cadastrado no sistema.")
            return

        dialogo = DialogoAlugarFilme(filme_selecionado, self.clientes, self)
        dialogo.aluguel_confirmado.connect(lambda c: self.requisitar_aluguel(filme_selecionado, c))
        dialogo.exec()

    def requisitar_aluguel(self, filme, cliente):
        data_atual = datetime.date.today().strftime("%d/%m/%Y")
        self.definir_botoes_habilitados(False)
        self.statusBar().showMessage("Processando locacao...")
        t = Trabalhador(api_cliente.cadastrar_locacao, cliente.cpf, filme.titulo, data_atual)
        t.sinais.sucesso.connect(self.ao_concluir_mutacao, Qt.QueuedConnection)
        t.sinais.erro.connect(self.mostrar_erro, Qt.QueuedConnection)
        t.sinais.finalizado.connect(self.finalizar_mutacao, Qt.QueuedConnection)
        self.trabalhadores.append(t)
        t.start()

    def excluir_filme(self):
        linhas = self.tabela_filmes.selectionModel().selectedRows()
        if not linhas:
            QMessageBox.information(self, "Aviso", "Selecione um filme para excluir.")
            return

        idx = linhas[0].row()
        item_titulo = self.tabela_filmes.item(idx, 0)
        if not item_titulo:
            return
        titulo = item_titulo.text()

        resposta = QMessageBox.question(
            self, "Confirmar Exclusao",
            f"Deseja realmente excluir o filme '{titulo}'?",
            QMessageBox.Yes | QMessageBox.No
        )
        if resposta != QMessageBox.Yes:
            return

        self.definir_botoes_habilitados(False)
        self.statusBar().showMessage(f"Excluindo {titulo}...")
        t = Trabalhador(api_cliente.excluir_filme, titulo)
        t.sinais.sucesso.connect(self.ao_concluir_mutacao, Qt.QueuedConnection)
        t.sinais.erro.connect(self.mostrar_erro, Qt.QueuedConnection)
        t.sinais.finalizado.connect(self.finalizar_mutacao, Qt.QueuedConnection)
        self.trabalhadores.append(t)
        t.start()

    def excluir_cliente(self):
        linhas = self.tabela_clientes.selectionModel().selectedRows()
        if not linhas:
            QMessageBox.information(self, "Aviso", "Selecione um cliente para excluir.")
            return

        idx = linhas[0].row()
        item_cpf = self.tabela_clientes.item(idx, 1)
        item_nome = self.tabela_clientes.item(idx, 0)
        if not item_cpf or not item_nome:
            return
        cpf = item_cpf.text()
        nome = item_nome.text()

        resposta = QMessageBox.question(
            self, "Confirmar Exclusao",
            f"Deseja realmente excluir o cliente '{nome}' (CPF: {cpf})?",
            QMessageBox.Yes | QMessageBox.No
        )
        if resposta != QMessageBox.Yes:
            return

        self.definir_botoes_habilitados(False)
        self.statusBar().showMessage(f"Excluindo {nome}...")
        t = Trabalhador(api_cliente.excluir_cliente, cpf)
        t.sinais.sucesso.connect(self.ao_concluir_mutacao, Qt.QueuedConnection)
        t.sinais.erro.connect(self.mostrar_erro, Qt.QueuedConnection)
        t.sinais.finalizado.connect(self.finalizar_mutacao, Qt.QueuedConnection)
        self.trabalhadores.append(t)
        t.start()

    def excluir_locacao(self):
        linhas = self.tabela_historico.selectionModel().selectedRows()
        if not linhas:
            QMessageBox.information(self, "Aviso", "Selecione uma locacao para excluir.")
            return

        idx = linhas[0].row()
        item_filme = self.tabela_historico.item(idx, 0)
        locacao_id = item_filme.data(Qt.UserRole) if item_filme else None
        locacao_alvo = next((l for l in self.locacoes if l.locacao_id == locacao_id), None)
        if not locacao_alvo or locacao_id is None:
            QMessageBox.warning(self, "Aviso", "Nao foi possivel identificar a locacao selecionada.")
            return

        resposta = QMessageBox.question(
            self, "Confirmar Devolucao",
            f"Deseja cancelar a locacao de '{locacao_alvo.filme.titulo}' e devolver ao estoque?",
            QMessageBox.Yes | QMessageBox.No
        )
        if resposta != QMessageBox.Yes:
            return

        self.definir_botoes_habilitados(False)
        self.statusBar().showMessage("Cancelando locacao...")
        t = Trabalhador(api_cliente.excluir_locacao, locacao_alvo.locacao_id)
        t.sinais.sucesso.connect(self.ao_concluir_mutacao, Qt.QueuedConnection)
        t.sinais.erro.connect(self.mostrar_erro, Qt.QueuedConnection)
        t.sinais.finalizado.connect(self.finalizar_mutacao, Qt.QueuedConnection)
        self.trabalhadores.append(t)
        t.start()

    def acao_exportar_json(self):
        caminho, _ = QFileDialog.getSaveFileName(self, "Exportar Dados JSON", "backup_locadora.json", "JSON Files (*.json)")
        if caminho:
            if not caminho.lower().endswith(".json"):
                caminho += ".json"
            try:
                msg = exportar_dados_json(self.filmes, self.clientes, self.locacoes, caminho)
                QMessageBox.information(self, "Exportacao", msg)
                self.statusBar().showMessage("Exportacao JSON concluida.", 3000)
            except Exception as e:
                self.mostrar_erro(str(e))

    def acao_exportar_csv(self):
        caminho, _ = QFileDialog.getSaveFileName(self, "Exportar Relatorios CSV", "relatorio_locadora.csv", "CSV Files (*.csv)")
        if caminho:
            try:
                msg = exportar_dados_csv(self.filmes, self.clientes, self.locacoes, caminho)
                QMessageBox.information(self, "Exportacao", msg)
                self.statusBar().showMessage("Exportacao CSV concluida.", 3000)
            except Exception as e:
                self.mostrar_erro(str(e))

    def atualizar_tabela_filmes(self):
        self.filtrar_filmes(self.busca_filme.text())

    def atualizar_tabela_clientes(self):
        self.filtrar_clientes(self.busca_cliente.text())

    def atualizar_tabela_locacoes(self):
        self.filtrar_locacoes(self.busca_locacao.text())

    def filtrar_filmes(self, termo):
        termo = termo.lower().strip()
        filmes_filtrados = [
            f for f in self.filmes
            if termo in f.titulo.lower() or termo in f.genero.lower() or termo in str(f.ano)
        ]
        self.tabela_filmes.setRowCount(0)
        for i, filme in enumerate(filmes_filtrados):
            self.tabela_filmes.insertRow(i)
            self.tabela_filmes.setItem(i, 0, QTableWidgetItem(filme.titulo))
            self.tabela_filmes.setItem(i, 1, QTableWidgetItem(str(filme.ano)))
            self.tabela_filmes.setItem(i, 2, QTableWidgetItem(filme.genero))
            self.tabela_filmes.setItem(i, 3, QTableWidgetItem(f"R$ {filme.preco:.2f}"))
            self.tabela_filmes.setItem(i, 4, QTableWidgetItem(str(filme.quantidade)))

    def filtrar_clientes(self, termo):
        termo = termo.lower().strip()
        termo_cpf = "".join(ch for ch in termo if ch.isdigit()) if set(termo).issubset(set("0123456789.- ")) else ""
        clientes_filtrados = [
            c for c in self.clientes
            if termo in c.nome.lower()
            or termo in c.cpf.lower()
            or (termo_cpf and termo_cpf in c.cpf)
        ]
        self.tabela_clientes.setRowCount(0)
        for i, cliente in enumerate(clientes_filtrados):
            self.tabela_clientes.insertRow(i)
            self.tabela_clientes.setItem(i, 0, QTableWidgetItem(cliente.nome))
            self.tabela_clientes.setItem(i, 1, QTableWidgetItem(cliente.cpf))

    def filtrar_locacoes(self, termo):
        termo = termo.lower().strip()
        termo_cpf = "".join(ch for ch in termo if ch.isdigit()) if set(termo).issubset(set("0123456789.- ")) else ""
        locacoes_filtradas = [
            l for l in self.locacoes
            if termo in l.filme.titulo.lower()
            or termo in l.cliente.nome.lower()
            or termo in l.cliente.cpf.lower()
            or (termo_cpf and termo_cpf in l.cliente.cpf)
            or termo in l.data.lower()
        ]
        self.tabela_historico.setRowCount(0)
        for i, loc in enumerate(locacoes_filtradas):
            self.tabela_historico.insertRow(i)
            item_filme = QTableWidgetItem(loc.filme.titulo)
            item_filme.setData(Qt.UserRole, loc.locacao_id)
            self.tabela_historico.setItem(i, 0, item_filme)
            self.tabela_historico.setItem(i, 1, QTableWidgetItem(loc.cliente.nome))
            self.tabela_historico.setItem(i, 2, QTableWidgetItem(loc.cliente.cpf))
            self.tabela_historico.setItem(i, 3, QTableWidgetItem(loc.data))

    def limpar_trabalhador(self, t):
        if t is not None:
            if t in self.trabalhadores:
                self.trabalhadores.remove(t)
            t.deleteLater()

    def mostrar_erro(self, erro):
        if self._fechando:
            return
        self.definir_botoes_habilitados(True)
        QMessageBox.critical(self, "Erro", str(erro))
        self.statusBar().showMessage(f"Erro: {erro}", 5000)

    def closeEvent(self, evento: QCloseEvent):
        resposta = QMessageBox.question(
            self, "Sair", "Deseja realmente fechar o sistema?",
            QMessageBox.Yes | QMessageBox.No
        )
        if resposta == QMessageBox.Yes:
            self._fechando = True
            for t in list(self.trabalhadores):
                for sinal in (t.sinais.sucesso, t.sinais.erro, t.sinais.finalizado):
                    try:
                        sinal.disconnect()
                    except Exception:
                        pass
            evento.accept()
        else:
            evento.ignore()

    def mostrar_sobre(self):
        QMessageBox.about(
            self, "Sobre o Sistema",
            "Locadora de Filmes - Trabalho 03\n\n"
            "Desenvolvido por:\n"
            "- Antonio Jonathan Santos Satiro\n"
            "- Caua Aquino Honorato Oliveira\n"
            "- Pedro Luiz de Moura Marques\n\n"
            "UFPI - CSHNB"
        )
