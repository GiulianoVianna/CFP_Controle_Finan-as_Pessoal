import sqlite3
from PyQt5 import uic, QtWidgets, QtCore
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtCore import QDate
from datetime import datetime


numero_id = 0


# Redimensiona colunas da tabela
def tabela_medidas():
    tela.tableWidget.setColumnWidth(0, 0)  
    tela.tableWidget.setColumnWidth(1, 90)
    tela.tableWidget.setColumnWidth(2, 480)
    tela.tableWidget.setColumnWidth(3, 180)
    tela.tableWidget.setColumnWidth(4, 115)
    
    
# Exibe mensagem
def mensagem(icone, titulo, texto):
    msg = QMessageBox(icone, titulo, texto)
    msg.exec_()

    
# Popula combobox da tela de edição com categorias
def combo_box_tela_editar():
    try:
        with sqlite3.connect("cfp.db") as banco:
            cursor = banco.cursor()
            categorias = cursor.execute("SELECT * FROM consulta_categoria").fetchall()
            
            if not categorias:
                print("Consulta não retornou resultados")
                
            for categoria in categorias:
                #print(f"Adicionando categoria '{categoria[0]}' ao combobox")
                tela_editar.cbox.addItem(categoria[0])

    except sqlite3.Error as erro:
        print("Erro ao carregar dados!", erro)
        
        
# Abre tela de edição com dados do registro selecionado
def editar_lancamento():
    global numero_id
    
    linha = tela.tableWidget.currentRow()
    numero_id = int(tela.tableWidget.item(linha, 0).text())

    try:
        with sqlite3.connect("cfp.db") as banco:
            cursor = banco.cursor()
            cursor.execute(f"SELECT * FROM movimentos WHERE id = {numero_id}")
            dados = cursor.fetchone()
            
            if not dados:
                raise ValueError(f"Nenhum registro com id {numero_id}")
                
        tela_editar.show()
        tela_editar.cbox.clear()
        combo_box_tela_editar()
        
        tela_editar.line_id.setText(str(dados[0]))
        tela_editar.line_data.setText(str(dados[1]))
        tela_editar.line_descricao.setText(str(dados[2]))
        tela_editar.cbox.setCurrentText(str(dados[3]))
        tela_editar.line_valor.setText(str(dados[4]))

        if float(tela_editar.line_valor.text()) > 0:
            tela_editar.rb_recebimento.setChecked(True)
        else:
            tela_editar.rb_pagamento.setChecked(True)

    except sqlite3.Error as erro:
        print(f"Erro ao carregar dados: {erro}")
        
        
# Exclui registro        
def excluir():
    global numero_id
    
    linha = tela.tableWidget.currentRow()
    numero_id = int(tela.tableWidget.item(linha, 0).text())

    try:
        with sqlite3.connect("cfp.db") as banco:
            cursor = banco.cursor()
            cursor.execute(f"DELETE FROM movimentos WHERE id = {numero_id}")
            banco.commit()

        mensagem(QMessageBox.Information, "Exclusão!", "Dado excluído!")
        consulta_dados()
        saldo()
        
    except sqlite3.Error as erro:
        print(f"Erro ao excluir dados: {erro}")
        
        
# Salva edição do registro
def salvar_edicao_lancamento():
    global numero_id

    data = tela_editar.line_data.text()
    descricao = tela_editar.line_descricao.text()
    categoria = tela_editar.cbox.currentText()
    
    if tela_editar.rb_recebimento.isChecked():
        valor = abs(float(tela_editar.line_valor.text()))
    else:
        valor = float(tela_editar.line_valor.text())
        if valor > 0:
            valor *= -1

    try:
        with sqlite3.connect("cfp.db") as banco:
            cursor = banco.cursor()
            
            cursor.execute("""
                UPDATE movimentos SET
                data = ?, 
                descricao = ?,
                categoria = ?,
                valor = ?
                WHERE id = ?""", 
                (data, descricao, categoria, valor, numero_id))
            
            banco.commit()
            
        mensagem(QMessageBox.Information, "Edição!", "Edição realizada!")
        tela_editar.close()        
        consulta_dados()
        saldo()
        
    except sqlite3.Error as erro:
        print("Erro ao editar dados!", erro)

    
# Salva nova categoria
def salvar_categoria():
    categoria = tela.cbox.currentText().upper()
    
    if not categoria:
       mensagem(QMessageBox.Information, "Atenção!", "Digite a categoria!")
       return
    
    try:
        with sqlite3.connect("cfp.db") as banco:
            cursor = banco.cursor()
            cursor.execute(f"INSERT INTO categorias (categoria) VALUES ('{categoria}')")
            banco.commit()
        
        mensagem(QMessageBox.Information, "Lançamento!", "Categoria cadastrada!")
        
        tela.cbox.clear()
        
    except sqlite3.Error as erro:
        print("Erro ao cadastrar categoria!", erro)
        
    combo_box()

    
# Popula combobox com categorias
def combo_box():
    try:
        with sqlite3.connect("cfp.db") as banco:
            cursor = banco.cursor()
            categorias = cursor.execute("SELECT * FROM consulta_categoria").fetchall()

            if not categorias:
                print("Consulta não retornou resultados")

            for categoria in categorias:
                #print(f"Adicionando categoria '{categoria[0]}' ao combobox") #Teste
                tela.cbox.addItem(categoria[0])

    except sqlite3.Error as erro:
        print("Erro ao carregar dados!", erro)
    
    
# Calcula saldo
def saldo():
    try:
        with sqlite3.connect("cfp.db") as banco:
            cursor = banco.cursor()
            resultado = cursor.execute("SELECT SUM(valor) FROM movimentos").fetchone()

            if resultado:
                valor = resultado[0]
            else:
                valor = 0

            if valor is None:
                tela.line_saldo.setText("R$ 0,00")
            else:
                tela.line_saldo.setText(f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))

    except sqlite3.Error as erro:
        print("Erro ao calcular saldo!", erro)

        
# Consulta registros e popula tabela        
def consulta_dados():
    try:
        tela.show()

        with sqlite3.connect("cfp.db") as banco:
            cursor = banco.cursor()
            cursor.execute("SELECT * FROM movimentos ORDER BY data DESC")
            dados_lidos = cursor.fetchall()

        tela.tableWidget.setRowCount(len(dados_lidos))
        tela.tableWidget.setColumnCount(5)

        for linha, registro in enumerate(dados_lidos):
            for coluna in range(0, 4):
                tela.tableWidget.setItem(linha, coluna, QtWidgets.QTableWidgetItem(str(registro[coluna])))

            valor = registro[4]
            valor_formatado = f"{valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            tela.tableWidget.setItem(linha, 4, QtWidgets.QTableWidgetItem(valor_formatado))

    except sqlite3.Error as erro:
        print("Erro ao consultar dados!", erro)
        
        
# Insere novo registro        
def salvar():
    data = tela.line_data.text()
    valor = tela.line_valor.text()
    descricao = tela.line_descricao.text().upper()
    categoria = tela.cbox.currentText()

    if not all([data, valor, descricao, categoria]):
        mensagem(QMessageBox.Information, "Atenção!", "Favor preencher todos os campos!")
        return

    if tela.rb_pagamento.isChecked():
        valor = str(float(valor) * -1)

    try:
        with sqlite3.connect("cfp.db") as banco:
            cursor = banco.cursor()
            cursor.execute("INSERT INTO movimentos (data, valor, descricao, categoria) VALUES (?, ?, ?, ?)", 
                           (data, valor, descricao, categoria))
            banco.commit()
            
        set_current_date()
        tela.line_valor.setText("")
        tela.line_descricao.setText("")
        tela.cbox.clear()
        
        mensagem(QMessageBox.Information, "Lançamento!", "Lançamento realizado!")
        saldo()
        consulta_dados()

    except sqlite3.Error as erro:
        print("Erro ao inserir dados!", erro)

    combo_box()

    
# Define data atual no campo data
def set_current_date():
    hoje = datetime.now().date()
    data_hoje = QDate(hoje.year, hoje.month, hoje.day)
    tela.line_data.setDate(data_hoje)
    
    
# Configurações iniciais
app = QtWidgets.QApplication([])
tela = uic.loadUi("controle.ui")
tela_editar = uic.loadUi("editar_lancamento.ui") 

tela.cbox.clear()
tela.bt_salvar.clicked.connect(salvar)
tela.bt_categoria.clicked.connect(salvar_categoria)  
tela.bt_editar.clicked.connect(editar_lancamento)
tela.bt_excluir.clicked.connect(excluir)

tela_editar.bt_salvar.clicked.connect(salvar_edicao_lancamento)

set_current_date()
combo_box()
saldo()
consulta_dados()
tabela_medidas()

tela.show()
app.exec()