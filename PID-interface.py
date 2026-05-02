import sys
import scipy.io
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QLabel, QLineEdit, 
                             QPushButton, QVBoxLayout, QHBoxLayout, QStackedWidget,
                             QMessageBox, QFileDialog, QRadioButton, QGroupBox,
                             QComboBox, QGridLayout)
from PyQt5.QtCore import QSize, QDir, Qt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import numpy as np
from PID_logica import logicaPID as pid

# ==============================================================================
# PÁGINAS (WIDGETS)
# ==============================================================================

class PaginaLogin(QWidget):
    def __init__(self):
        super().__init__()

       #Componentes da janela
        self.label_titulo = QLabel("Login")
        self.label_titulo.setAlignment(Qt.AlignCenter)
        self.label_titulo.setStyleSheet("font-size: 22px; font-weight: bold;")
        self.label_email = QLabel("E-mail:")
        self.label_senha = QLabel("Senha:")
        self.campo_email = QLineEdit()
        self.campo_email.setPlaceholderText("e-mail")
        self.campo_senha = QLineEdit()
        self.campo_senha.setEchoMode(QLineEdit.Password) #ocultar a senha digitada
        self.campo_senha.setPlaceholderText("senha")
        self.botao_enviar = QPushButton("Fazer login")

        #Layout horizontal
        layout_principal = QVBoxLayout()
        layout_email = QHBoxLayout()
        layout_email.addWidget(self.label_email)
        layout_email.addWidget(self.campo_email)
        layout_senha = QHBoxLayout()
        layout_senha.addWidget(self.label_senha)
        layout_senha.addWidget(self.campo_senha)

        layout_principal.addWidget(self.label_titulo)
        layout_principal.addLayout(layout_email)
        layout_principal.addLayout(layout_senha)
        layout_principal.addWidget(self.botao_enviar)
        self.setLayout(layout_principal)

        #Lógica do login
        email = self.campo_email.text()
        senha = self.campo_senha.text()

        #self.validar_credencial(email, senha)

    def validar_credencial(self, email, senha):
        '''Validação das credenciais'''
        return email == "admin@admin.com" and senha == "admin"

    #Diferenciação do tamanho da tela de login
    def sizeHint(self) -> QSize:
        return QSize(400, 200)
    
#Opções para o método de identificação escolhido
MENU_OPTIONS_IDENT = [
    {"text": "Smith", "type": "action", "value": "Smith"},
    {"text": "Sundaresan", "type": "action", "value": "Sun"},
]

class PaginaIdentSists(QWidget):
    def __init__(self):
        super().__init__()

        self.label_confirmacao = QLabel("Identificação de Sistemas") #texto para identificar a janela
        self.botao_pid = QPushButton("Controle PID") #botão para ir para o controle PID
        self.botao_voltar = QPushButton("Voltar") #botão para voltar ao login
        self.label_dataIN = QLabel("Dados de entrada:")
        self.label_dataOUT = QLabel("Dados de saída:")
        self.label_identificacao = QLabel("Método de Identificação:")
        self.botao_exportar_graphs = QPushButton("Exportar gráfico")


        # ======= Gráfico (Matplotlib) =======
        self.figure = Figure(figsize=(5, 4))
        self.ax = self.figure.add_subplot(111)
        self.canvas = FigureCanvas(self.figure)

        # ======= Área lateral direita =======
        #ComboBox de Identificação
        self.combo_box = QComboBox()
        self.populate_combo_box()
        self.combo_box.currentIndexChanged.connect(self.on_option_selected)

        #Campos dos parâmetros Smith
        self.label_ks = QLabel("kₛ :")
        self.label_tau = QLabel("τₛ :")
        self.label_theta = QLabel("θₛ :")
        self.label_E = QLabel("Eₛ :")

        self.edit_ks = QLineEdit("-")
        self.edit_tau = QLineEdit("-")
        self.edit_theta = QLineEdit("-")
        self.edit_E = QLineEdit("-")

        for edit in [self.edit_ks, self.edit_tau, self.edit_theta, self.edit_E]:
            edit.setReadOnly(True) #inalteráveis
            edit.setFixedWidth(80)
            edit.setAlignment(Qt.AlignCenter)

        #Botão de exportação
        self.botao_exportar = QPushButton("Exportar gráfico")
        self.botao_exportar.setEnabled(False)
        self.botao_exportar.clicked.connect(self.exportar_grafico)

        #Botão para ir ao Controle PID
        self.btn_PID = QPushButton("Controle PID")
        self.btn_PID.setEnabled(False)

        #Botão de abrir arquivo .mat
        self.btn_open = QPushButton("Buscar Arquivo .mat")
        self.btn_open.clicked.connect(self.open_mat_file)
        self.file_path_label = QLabel("Nenhum arquivo selecionado.")


        # ======= Layout da área lateral (direita) =======
        side_layout = QVBoxLayout()
        side_layout.addWidget(QLabel("Método de Identificação:"))
        side_layout.addWidget(self.combo_box)
        side_layout.addSpacing(10)

        grid = QGridLayout()
        grid.addWidget(self.label_ks, 0, 0)
        grid.addWidget(self.edit_ks, 0, 1)
        grid.addWidget(self.label_tau, 1, 0)
        grid.addWidget(self.edit_tau, 1, 1)
        grid.addWidget(self.label_theta, 2, 0)
        grid.addWidget(self.edit_theta, 2, 1)
        grid.addWidget(self.label_E, 3, 0)
        grid.addWidget(self.edit_E, 3, 1)

        side_layout.addLayout(grid)
        side_layout.addSpacing(10)
        side_layout.addWidget(self.botao_exportar) #exportar gráfico
        side_layout.addWidget(self.btn_PID) #ir para o controle PID
        side_layout.addStretch()

        #Agrupamento visual (grupo lateral)
        side_group = QGroupBox()
        side_group.setLayout(side_layout)

        # ======= Layout central (gráfico + painel lateral) =======
        top_layout = QHBoxLayout()
        top_layout.addWidget(self.canvas, stretch=3)
        top_layout.addWidget(side_group, stretch=1)

        # ======= Layout inferior (botões) =======
        bottom_layout = QHBoxLayout()
        bottom_layout.addWidget(self.file_path_label) #nome do arquivo aberto
        bottom_layout.addWidget(self.btn_open) #abrir .mat
        bottom_layout.addWidget(self.botao_voltar) #voltar para o login


        # ======= Layout principal (geral)=======
        layout_principal = QVBoxLayout()
        layout_principal.addWidget(self.label_confirmacao)
        layout_principal.addLayout(top_layout)
        layout_principal.addSpacing(10)
        layout_principal.addLayout(bottom_layout)

        self.setLayout(layout_principal)
        self.metodo_atual = "Smith"

        # ======= Variáveis internas =======
        self.mat_data = None #dados .mat

    #Tamanho desta página
    def sizeHint(self) -> QSize:
        return QSize(900, 600)
    
    def open_mat_file(self):
        '''Abrir arquivo .mat'''
        #Abrir a seleção de arquivo
        filename, _ = QFileDialog.getOpenFileName(
            self, 
            "Selecionar Arquivo .mat",
            QDir.homePath(),  # Define o diretório inicial para o "home" do usuário
            "Arquivos MATLAB (*.mat);;Todos os Arquivos (*.*)" # Filtro -> só arquivos .mat
        )
        
        if filename:
            # Um arquivo foi selecionado
            self.file_path_label.setText(f"Arquivo selecionado: {filename}")
            
            #Processamento do arquivo .mat
            self.load_and_plot_mat(filename)
        else:
            # O usuário cancelou
            self.file_path_label.setText("Seleção cancelada.")

    def load_and_plot_mat(self, caminho):
        '''Carregamento e plotagem dos dados do arquivo .mat'''
        try:
            dados = scipy.io.loadmat(caminho)

            #Verificar se as variáveis de entrada e saída estão no arquivo
            if 'dados_entrada' not in dados or 'dados_saida' not in dados:
                QMessageBox.warning(
                    self, "Erro",
                    "O arquivo .mat não contém as variáveis 'dados_entrada' e 'dados_saida'."
                )
                return

            #seleção dos dados
            entrada = dados['dados_entrada']
            saida = dados['dados_saida']

            self.tempo = entrada[:, 0].astype(float)
            self.degrau = entrada[:, 1].astype(float)
            self.temperatura = saida[:, 1].astype(float)

            # Identificação pelo método de Smith
            self.smith_parametros = pid.criar_modelo_sistema_controle(self.tempo, self.degrau, self.temperatura, "Smith")
            # Calcular e salvar eqm
            self.smith_parametros = self.smith_parametros + (pid.eqm(self.temperatura, self.smith_parametros[5]), )

            # Indentificação pelo método de Sundaresan
            self.sundaresan = pid.criar_modelo_sistema_controle(self.tempo, self.degrau, self.temperatura, "Sundaresan")
            # Calcular e salvar eqm
            self.sundaresan = self.sundaresan + (pid.eqm(self.temperatura, self.sundaresan[5]), )

            # Verificar qual método foi escolhido
            if(self.metodo_atual == "Smith"):
                k, tau, theta, sistemaControle, tempoAberta, temperaturaAberta, tempoFechada, temperaturaFechada, eqm = self.smith_parametros
            else:
                k, tau, theta, sistemaControle, tempoAberta, temperaturaAberta, tempoFechada, temperaturaFechada, eqm = self.sundaresan
            
            # preenche os campos com 4 casas decimais
            self.edit_ks.setText(f"{k:.4f}")
            self.edit_tau.setText(f"{tau:.4f}")
            self.edit_theta.setText(f"{theta:.4f}")
            self.edit_E.setText(f"{eqm:.4f}")

            # Plotar gráfico
            self.grafico_comparacao_identificacao_real(self.tempo, self.degrau, self.temperatura, tempoAberta, temperaturaAberta, tempoFechada, temperaturaFechada)
            print("Plotou")

            self.botao_exportar.setEnabled(True)
            self.btn_PID.setEnabled(True)
            
    
        except Exception as e:
            QMessageBox.critical(self, "Erro ao carregar arquivo", str(e))
    
    def grafico_comparacao_identificacao_real(self, tempo, degrau, temperatura, tempoSimulado, temperaturaSimulada, tempo_fechada, amplitude_fechada):
        self.ax.clear()
        self.ax.plot(tempo, degrau, linewidth=1.25, label="Degrau", color="blue")
        self.ax.plot(tempo, temperatura, 'r--', linewidth=1.25, label="Real")
        self.ax.plot(tempo_fechada, amplitude_fechada + self.temperatura[0], linewidth=1.25, color="orange", label="Identificação Malha Fechada")
        if(self.metodo_atual == "Smith"):
            self.ax.plot(tempoSimulado, temperaturaSimulada, 'k', linewidth=1.25, label="Identificação Malha Aberta", color="black")
        else:
            self.ax.plot(tempoSimulado, temperaturaSimulada, 'k', linewidth=1.25, label="Identificação Malha Aberta", color="gray")

        self.ax.grid(True)
        self.ax.set_title('Trabalho Prático C213\nModelo Identificação vs Modelo Real')
        self.ax.set_xlabel("Tempo (segundos)")
        self.ax.set_ylabel("Temperatura [°C]")
        self.ax.legend()
        self.canvas.draw()
        print("Gráfico atualizado")         

    # ------------------------------------------------------------------
    # Exportação do gráfico
    # ------------------------------------------------------------------
    def exportar_grafico(self):
        filename, _ = QFileDialog.getSaveFileName(
            self,
            "Salvar Gráfico",
            QDir.homePath(),
            "Imagens PNG (*.png);;Todos os Arquivos (*.*)"
        )
        if filename:
            self.figure.savefig(filename)
            self.file_path_label.setText(f"Gráfico exportado: {filename}")


    def populate_combo_box(self):
        """Preenche o combo com os métodos disponíveis."""
        for item in MENU_OPTIONS_IDENT:
            self.combo_box.addItem(item["text"], item["value"])

    def on_option_selected(self, index):
        """Ação ao selecionar método."""
        method = self.combo_box.itemData(index)
        text = self.combo_box.itemText(index)
        print(f"Método selecionado: {method}")
        self.metodo_atual = method

        if self.smith_parametros:
            try:
                # Verificar qual método foi escolhido
                if(self.metodo_atual == "Smith"):
                    k, tau, theta, sistemaControle, tempoAberta, temperaturaAberta, tempoFechada, temperaturaFechada, eqm = self.smith_parametros
                else:
                    k, tau, theta, sistemaControle, tempoAberta, temperaturaAberta, tempoFechada, temperaturaFechada, eqm = self.sundaresan
                
                
                # preenche os campos com 4 casas decimais
                self.edit_ks.setText(f"{k:.4f}")
                self.edit_tau.setText(f"{tau:.4f}")
                self.edit_theta.setText(f"{theta:.4f}")
                self.edit_E.setText(f"{eqm:.4f}")

                # Plotar gráfico
                self.grafico_comparacao_identificacao_real(self.tempo, self.degrau, self.temperatura, tempoAberta, temperaturaAberta, tempoFechada, temperaturaFechada)
            except Exception as e:
                QMessageBox.warning(self, "Erro ao atualizar método", str(e))



#Opções para o método escolhido nos cálculos
MENU_OPTIONS = [
    {"text": "IMC", "type": "action", "value": "IMC"},
    {"text": "ITAE", "type": "action", "value": "ITAE"},
]

class PaginaControlePID(QWidget):
    def __init__(self):
        super().__init__()
        #=== Título e Botões ===
        self.titulo = QLabel("Controle PID")
        self.titulo.setAlignment(Qt.AlignCenter)
        self.titulo.setStyleSheet("font-size: 22px; font-weight: bold;")

        self.botao_graphs = QPushButton("Acessar gráficos")
        self.botao_voltar = QPushButton("Voltar")

        #=== Seleção de sintonia ===
        selecao_label = QLabel("Seleção de Sintonia:")
        self.radio_auto = QRadioButton("Automático")
        self.radio_manual = QRadioButton("Manual")
        self.radio_auto.setChecked(True)
        self.radio_auto.toggled.connect(lambda: self.toggle_manual_mode(False))
        self.radio_manual.toggled.connect(lambda: self.toggle_manual_mode(True))

        layout_radios = QHBoxLayout()
        layout_radios.addWidget(selecao_label)
        layout_radios.addWidget(self.radio_auto)
        layout_radios.addWidget(self.radio_manual)
        layout_radios.addStretch()

        #ComboBox de método
        self.combo_metodo = QComboBox()
        self.populate_combo_box()
        self.combo_metodo.currentIndexChanged.connect(self.on_option_selected)
        self.combo_metodo.setFixedWidth(150)
        self.combo_metodo.setEnabled(True)
        self.combo_metodo.currentIndexChanged.connect(self.on_option_selected)
        
        self.label_lambda = QLabel("λ:")
        self.input_lambda = QLineEdit("1.0")
        self.input_lambda.setFixedWidth(60)
        self.input_lambda.setAlignment(Qt.AlignCenter)
        self.input_lambda.setStyleSheet("background-color: white;")

        layout_top = QHBoxLayout()
        layout_top.addLayout(layout_radios)
        layout_top.addWidget(self.combo_metodo)
        layout_top.addWidget(self.label_lambda)
        layout_top.addWidget(self.input_lambda)

        #=== Gráfico ===
        self.figura = Figure(figsize=(5, 3))
        self.canvas = FigureCanvas(self.figura)
        self.ax = self.figura.add_subplot(111)
        self.ax.set_title("Resposta do Controle PID")
        self.ax.set_xlabel("t")
        self.ax.set_ylabel("y(t)")
        self.ax.grid(True)
        self.figura.tight_layout()

        #=== Campos de PID ===
        pid_group = QGroupBox()
        pid_layout = QGridLayout()

        labels_pid = ["Kₚ:", "Tᵢ:", "Td:"]
        self.inputs_pid = []
        self.botoes_limpar_pid = []  # Lista para armazenar os botões de limpeza

        for i, text in enumerate(labels_pid):
            label = QLabel(text)
            field = QLineEdit("0.0")
            field.setAlignment(Qt.AlignCenter)
            field.setReadOnly(True)
            field.setFixedWidth(60)
            field.setStyleSheet("background-color: #EAEAEA;")
            
            btn_limpar = QPushButton("🗑️")
            btn_limpar.setFixedWidth(30)
            btn_limpar.setEnabled(False) # Inicia desabilitado (modo automático)
            btn_limpar.clicked.connect(lambda _, f=field: f.setText("0.0"))
            
            pid_layout.addWidget(label, i, 0)
            pid_layout.addWidget(field, i, 1)
            pid_layout.addWidget(btn_limpar, i, 2) # Adiciona na terceira coluna
            
            self.inputs_pid.append(field)
            self.botoes_limpar_pid.append(btn_limpar)

        #Botões Sintonizar e Exportar (Ajustados para ocupar as 3 colunas)
        self.botao_sintonizar = QPushButton("Sintonizar")
        self.botao_exportar = QPushButton("Exportar")
        self.botao_exportar.clicked.connect(self.exportar_grafico)

        pid_layout.addWidget(self.botao_sintonizar, 4, 0, 1, 3) # Span de 3 colunas
        pid_layout.addWidget(self.botao_exportar, 5, 0, 1, 3)   # Span de 3 colunas

        pid_group.setLayout(pid_layout)
        pid_group.setStyleSheet("QGroupBox { border: none; }")

        #=== Grupo de parâmetros de controle ===
        controle_group = QGroupBox("Parâmetros de controle:")
        controle_layout = QGridLayout()
        self.parametros_labels = ["SP:", "tₛ:", "tᵣ:", "mₚ:", "erro"]
        self.parametros_inputs = []

        for i, label_text in enumerate(self.parametros_labels):
            label = QLabel(label_text)
            field = QLineEdit("0.0" if i else "1")  #SP = -> padrão
            field.setAlignment(Qt.AlignCenter)
            field.setReadOnly(True)
            field.setFixedWidth(60)
            field.setStyleSheet("background-color: #EAEAEA;")
            controle_layout.addWidget(label, i, 0)
            controle_layout.addWidget(field, i, 1)
            self.parametros_inputs.append(field)

        self.parametros_inputs[0].setReadOnly(False)
        self.parametros_inputs[0].setStyleSheet("background-color: white;")

        controle_group.setLayout(controle_layout)

        #=== Layout central (gráfico + controles) ===
        layout_meio = QHBoxLayout()
        layout_meio.addWidget(self.canvas, 1)
        layout_lateral = QVBoxLayout()
        layout_lateral.addWidget(pid_group)
        layout_lateral.addWidget(controle_group)
        layout_meio.addLayout(layout_lateral)

        #=== Layout principal ===
        layout_principal = QVBoxLayout()
        layout_principal.addWidget(self.titulo)
        layout_principal.addLayout(layout_top)
        layout_principal.addLayout(layout_meio)
        layout_principal.addWidget(self.botao_voltar)
        #layout_principal.addStretch()        

        self.setLayout(layout_principal)
        self.botao_sintonizar.clicked.connect(self.calcular_parametros)
        self.toggle_manual_mode(False)  #Modo automático como padrão
        self.metodo_atual = "IMC"
        self.mode = "automatico"

    def toggle_manual_mode(self, manual):
        """Ativa ou desativa a edição dos parâmetros de controle e botões de limpar"""
        for i, field in enumerate(self.inputs_pid):
            field.setReadOnly(not manual)
            field.setStyleSheet(
                "background-color: white;" if manual else "background-color: #EAEAEA;"
            )
            self.botoes_limpar_pid[i].setEnabled(manual)
            
        self.parametros_inputs[0].setReadOnly(False)
        self.parametros_inputs[0].setStyleSheet("background-color: white;")

        if manual:
            self.combo_metodo.setDisabled(True)
            
            if hasattr(self, 'input_lambda'):
                self.input_lambda.setReadOnly(True)
                self.input_lambda.setStyleSheet("background-color: #EAEAEA;")
            self.mode = "manual"
        else:
            self.combo_metodo.setEnabled(True)
            self.mode = "automatico"
            
            if hasattr(self, 'input_lambda'):
                if hasattr(self, 'metodo_atual') and self.metodo_atual == "IMC":
                    self.input_lambda.setReadOnly(False)
                    self.input_lambda.setStyleSheet("background-color: white;")
                else:
                    self.input_lambda.setReadOnly(True)
                    self.input_lambda.setStyleSheet("background-color: #EAEAEA;")

    def sizeHint(self) -> QSize:
        return QSize(900, 600)
    
    def exportar_grafico(self):
        filename, _ = QFileDialog.getSaveFileName(
            self,
            "Salvar Gráfico",
            QDir.homePath(),
            "Imagens PNG (*.png);;Todos os Arquivos (*.*)"
        )
        if filename:
            self.figura.savefig(filename)
            QMessageBox.information(self, "Sucesso", f"Gráfico exportado com sucesso para:\n{filename}")

    def set_processing_mode(self, mode):
        """Define o modo de sintonia e bloqueia/desbloqueia campos."""
        if self.sender().isChecked():
            self.processing_mode = mode
            print(f"Modo de processamento: {mode}")

            # Se for automática → trava os campos
            if mode == "Automática":
                self.toggle_pid_inputs(False)
            else:
                self.toggle_pid_inputs(True)

    def toggle_pid_inputs(self, enabled: bool):
        """Ativa ou desativa a edição dos campos de controle."""
        self.kp_input.setReadOnly(not enabled)
        self.ki_input.setReadOnly(not enabled)
        self.kd_input.setReadOnly(not enabled)

        style = (
            "background-color: white;" if enabled 
            else "background-color: #E0E0E0;"
        )
        self.kp_input.setStyleSheet(style)
        self.ki_input.setStyleSheet(style)
        self.kd_input.setStyleSheet(style)

    def populate_combo_box(self):
        """Preenche o combo com os métodos disponíveis."""
        for item in MENU_OPTIONS:
            self.combo_metodo.addItem(item["text"], item["value"])

    def on_option_selected(self, index):
        """Ação ao selecionar método."""
        method = self.combo_metodo.itemData(index)
        print(f"Método selecionado: {method}")
        self.metodo_atual = method
        if self.metodo_atual == "IMC" and self.mode == "automatico":
            self.input_lambda.setReadOnly(False)
            self.input_lambda.setStyleSheet("background-color: white;")
        else:
            self.input_lambda.setReadOnly(True)
            self.input_lambda.setStyleSheet("background-color: #EAEAEA;")
        self.calcular_parametros()

    # Receber parâmetros calculados na página anterior
    def definir_parametros_sistema(self, k, tau, theta, tempo, temperatura, metodo, sistemaControle, amplitude_degrau):
        """Recebe os parâmetros identificados da página anterior"""
        self.k = k
        self.tau = tau
        self.theta = theta
        self.tempo = tempo
        self.temperatura = temperatura
        self.metodo = metodo
        self.sistemaControle = sistemaControle
        
        if hasattr(self, 'input_lambda'):
            self.input_lambda.setText(f"{theta:.4f}") 
            
        self.parametros_inputs[0].setText(f"{amplitude_degrau:.4f}")
    
    def calcular_parametros(self):
        sp = float(self.parametros_inputs[0].text())
        
        if(self.mode == "automatico"):
            if(self.metodo_atual == "IMC"):
                try:
                    lambda_c = float(self.input_lambda.text().replace(',', '.'))
                except ValueError:
                    lambda_c = self.theta # fallback seguro caso o campo fique vazio
                
                Kp, Ti, Td = pid.metodo_imc(self.k, self.tau, self.theta, lambda_c)
            else:
                Kp, Ti, Td = pid.metodo_itae(self.k, self.tau, self.theta)
        else:
            # Leitura segura dos dados manuais
            try:
                Kp = float(self.inputs_pid[0].text())
                Ti = float(self.inputs_pid[1].text())
                Td = float(self.inputs_pid[2].text())
            except ValueError:
                QMessageBox.warning(self, "Entrada Inválida", "Por favor, insira valores numéricos válidos nos campos PID.")
                return

            # NOVO: Verificação de Estabilidade antes de prosseguir
            estavel = pid.verificar_estabilidade(Kp, Ti, Td, self.sistemaControle)
            if not estavel:
                QMessageBox.critical(
                    self, 
                    "Sistema Instável", 
                    "Os parâmetros inseridos resultam em um sistema em malha fechada INSTÁVEL!\n\n"
                    "Revise os valores de Kp, Ti e Td. O tempo integral (Ti) não deve ser zero."
                )
                return # Aborta o cálculo e não atualiza os gráficos
        
        # Se chegou até aqui (automático ou manual estável), prossegue com o controle e simulação
        t, y = pid.criar_sistema_controle_pid(Kp, Ti, Td, self.sistemaControle, sp)

        ts, tr, mp, erro = pid.calcular_metricas(Kp, Ti, Td, sp, self.sistemaControle)

        self.sintonizar(Kp, Ti, Td, t , y, ts, tr, mp, erro)
   
    def sintonizar(self, Kp, Ti, Td, t , y, ts, tr, mp, erro):
        # Atualiza campos PID com valores calculados
        self.inputs_pid[0].setText(f"{Kp:.4f}")
        self.inputs_pid[1].setText(f"{Ti:.4f}")
        self.inputs_pid[2].setText(f"{Td:.4f}")

        self.parametros_inputs[1].setText(f"{ts:.4f}")
        self.parametros_inputs[2].setText(f"{tr:.4f}")
        self.parametros_inputs[3].setText(f"{mp:.4f}")
        self.parametros_inputs[4].setText(f"{erro:.4f}")

        sp = float(self.parametros_inputs[0].text())

        # Plotar gráfico
        self.grafico_sintonizacao(t, y, sp, ts, tr, mp)

    def grafico_sintonizacao(self, t, y, sp, ts, tr, mp):
        self.ax.clear()
        self.ax.plot(t, y, 'b', linewidth=2, label="PID")
        sp_array = np.ones_like(t)*sp
        self.ax.plot(t, sp_array, 'r--', linewidth=1.25, label="SP") # Mudança: 'r--' para destacar o SP
        
        # === 1. Localização do Pico (Peak) ===
        # Encontra o índice e o tempo correspondente ao valor máximo (Pico)
        y_max = np.max(y)
        indice_peak = np.argmax(y)
        t_peak = t[indice_peak]
        
        # === 2. Banda de Acomodação (Settling Band) ===
        # Adiciona uma área sombreada para a banda de 2% do SP
        tolerancia = 0.02 * sp 
        self.ax.axhspan(sp - tolerancia, sp + tolerancia, 
                        color='green', alpha=0.1, label="Banda ±2%")

        
        # === 3. Marcações e Anotações no Gráfico ===
        
        # --- Ponto de Pico e Overshoot (Mp) ---
        self.ax.plot(t_peak, y_max, 
                    marker='o', markersize=6, color='darkred', linestyle='None',
                    label=f"Pico ($M_p$ = {mp:.2f}%)")
        
        # Linha tracejada vertical (opcional)
        self.ax.axvline(t_peak, color='darkred', linestyle=':', linewidth=0.8)

        # Anotação do valor Mp (sobre-sinal)
        self.ax.annotate(f"Mp: {mp:.1f}%", 
                        xy=(t_peak, y_max), xycoords='data',
                        xytext=(-20, 20), textcoords='offset points',
                        arrowprops=dict(arrowstyle="->", connectionstyle="arc3", color='darkred'),
                        fontsize=9)


        # --- Lógica Condicional: IMC (tr) vs. ITAE (ts) ---
        
        if self.mode == "automatico" and self.metodo_atual == "IMC":
            # === Tempo de Subida (tr) - Foco do IMC ===
            
            # Linha vertical em tr
            self.ax.axvline(tr, color='orange', linestyle=':', linewidth=1.5,
                            label=f"tᵣ = {tr:.2f}s")
            
            # Anotação
            self.ax.annotate("tᵣ", 
                            xy=(tr, sp * 0.95), xycoords='data', 
                            xytext=(5, 0), textcoords='offset points', 
                            color='orange', fontsize=10, ha='left')
            
            self.ax.set_title('Trabalho Prático C213\nMétodo IMC (Internal Model Control)')
            
        elif self.mode == "automatico" and self.metodo_atual == "ITAE":
            # === Tempo de Acomodação (ts) - Foco do ITAE ===
            
            # Linha vertical em ts
            self.ax.axvline(ts, color='green', linestyle=':', linewidth=1.5,
                            label=f"tₛ = {ts:.2f}s")
                            
            # Anotação
            self.ax.annotate("tₛ", 
                            xy=(ts, sp + tolerancia * 1.5), xycoords='data',
                            xytext=(5, 0), textcoords='offset points', 
                            color='green', fontsize=10, ha='left')

            self.ax.set_title('Trabalho Prático C213\nMétodo ITAE (Foco: Estabilidade)')
            
        else: # Manual
            # Em modo manual, mostramos ambos se disponíveis
            if tr is not None:
                self.ax.axvline(tr, color='orange', linestyle=':', linewidth=1.5)
            if ts is not None:
                self.ax.axvline(ts, color='green', linestyle=':', linewidth=1.5)
                
            self.ax.set_title('Trabalho Prático C213\nMétodo Manual')

        self.ax.set_xlabel("Tempo (segundos)")
        self.ax.set_ylabel("Temperatura [°C]")
        self.ax.legend(loc='lower right')
        self.canvas.draw()
        print("Gráfico atualizado")


class PaginaGraphs(QWidget):
    def __init__(self):
        super().__init__()
        self.label_confirmacao = QLabel("Gráficos") #texto para identificar a janela
        self.botao_reiniciar = QPushButton("Reiniciar") #botão que redireciona ao login novamente
        self.botao_voltar = QPushButton("Voltar") #botão de retorno ao controle PID
        
        #Layout
        layout_principal = QVBoxLayout()
        layout_principal.addWidget(self.label_confirmacao)

        #Layout horizontal para os botões
        layout_botoes = QHBoxLayout()
        layout_botoes.addWidget(self.botao_voltar)
        layout_botoes.addWidget(self.botao_reiniciar)

        layout_principal.addLayout(layout_botoes)
        self.setLayout(layout_principal)

    #Tamanho desta página
    def sizeHint(self) -> QSize:
        return QSize(900, 600)

# ==============================================================================
# JANELA PRINCIPAL / CONTROLADOR
# ==============================================================================

class AplicacaoPrincipal(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Trabalho PID") #nome da janela

        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        #Declaração das páginas/janelas
        self.pagina_login = PaginaLogin()
        self.pagina_ident = PaginaIdentSists()
        self.pagina_pid = PaginaControlePID()
        self.pagina_graphs = PaginaGraphs()

        self.stack.addWidget(self.pagina_login)
        self.stack.addWidget(self.pagina_ident)
        self.stack.addWidget(self.pagina_pid)
        self.stack.addWidget(self.pagina_graphs)

        email = self.pagina_login.campo_email.text()
        senha = self.pagina_login.campo_senha.text()


        #Conexões dos botões de "Avançar" e suas referentes mudanças de tela
        self.pagina_login.botao_enviar.clicked.connect(self.try_login) #ir para a análise da validade das credenciais

        self.pagina_ident.btn_PID.clicked.connect(self.mostrar_pid)
        self.pagina_pid.botao_graphs.clicked.connect(self.mostrar_graficos)
        self.pagina_graphs.botao_reiniciar.clicked.connect(self.reiniciar_aplicacao)
        
        #Conexões dos botões de "Voltar" utilizando o método voltar_pagina
        self.pagina_ident.botao_voltar.clicked.connect(self.voltar_pagina)
        self.pagina_pid.botao_voltar.clicked.connect(self.voltar_pagina)
        self.pagina_graphs.botao_voltar.clicked.connect(self.voltar_pagina)

        #Conexão entre a mudança de página e o ajuste de tamanho da janela
        self.stack.currentChanged.connect(self.ajustar_tamanho_janela)
        
        #Ajustar o tamanho inicial para a página de login
        self.ajustar_tamanho_janela()
        


    # --- Métodos de Navegação ---
    def mostrar_identificacao(self):
        '''Referência de index da página de identificação de sistemas'''
        self.stack.setCurrentIndex(1)

    def mostrar_pid(self):
        '''Referência de index da página de controle PID'''

        #Verificar qual maior EQM para selecionar parâmetros
        if(self.pagina_ident.smith_parametros[-1] < self.pagina_ident.sundaresan[-1]):
            k, tau, theta, sistemaControle, *_ = self.pagina_ident.smith_parametros
            metodo = "Smith"
        else:
            k, tau, theta, sistemaControle, *_ = self.pagina_ident.sundaresan
            metodo = "Sun"

        amplitude_degrau = np.mean(self.pagina_ident.degrau)

        self.pagina_pid.definir_parametros_sistema(k, tau, theta, self.pagina_ident.tempo, self.pagina_ident.temperatura, metodo, sistemaControle, amplitude_degrau)
        self.pagina_pid.calcular_parametros()

        self.stack.setCurrentIndex(2)

    def mostrar_graficos(self):
        '''Referência de index da página de gráficos'''
        self.stack.setCurrentIndex(3)
        
    def reiniciar_aplicacao(self):
        '''Reinicialização da aplicação'''
        self.pagina_login.campo_email.clear() #zerar o campo login
        self.pagina_login.campo_senha.clear() #zerar o campo de senha
        self.stack.setCurrentIndex(0) #setar o index para o da página de login

    #Método para lidar com o ato de voltar
    def voltar_pagina(self):
        indice_atual = self.stack.currentIndex()
        if indice_atual == 1:
            self.reiniciar_aplicacao()
        elif indice_atual > 1:
            self.stack.setCurrentIndex(indice_atual - 1) #lógica de retorno por índice
            
    #Método chamado nas mudanças de página
    def ajustar_tamanho_janela(self):
        #Janela principal se redimensiona para o tamanho ideal do widget atual
        self.resize(self.stack.currentWidget().sizeHint())

    def login_invalido(self):
        """
        Esta função é chamada quando o botão 'Fazer login' é clicado e as credenciais são inválidas.
        """

        # Exibe os dados em uma caixa de diálogo
        mensagem = QMessageBox()
        mensagem.setWindowTitle("Credenciais inválidas")
        mensagem.setText(f"Dados inválidos, tente novamente.")
        mensagem.setIcon(QMessageBox.Information)
        mensagem.exec_()

    def try_login(self):
        email = self.pagina_login.campo_email.text()
        senha = self.pagina_login.campo_senha.text()

        if email == "admin@admin.com" and senha == "admin":
            self.mostrar_identificacao()
        else:
            self.login_invalido()



# ==============================================================================
# EXECUÇÃO
# ==============================================================================

if __name__ == '__main__':
    app = QApplication(sys.argv)
    janela = AplicacaoPrincipal()
    janela.show()
    sys.exit(app.exec_())