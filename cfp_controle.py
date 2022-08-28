
import sqlite3
from PyQt5 import uic, QtWidgets
from PyQt5.QtWidgets import QMessageBox

numero_id = 0


# Redimenciona as colunas da tabela de dados
def tabela_medidas():
    tela.tableWidget.setColumnWidth(0,3)
    tela.tableWidget.setColumnWidth(1,90)
    tela.tableWidget.setColumnWidth(2,400)
    tela.tableWidget.setColumnWidth(3,180)
    tela.tableWidget.setColumnWidth(4,118)
  
    
# Menssagem informa que os campos não foram preenchidos
def mensagem_falta_dados():
        msg1 = QMessageBox()
        msg1.setIcon(QMessageBox.Information)
        msg1.setWindowTitle('Atenção!')
        msg1.setText('Favor preencher todos os campos!')
        x = msg1.exec_()


# Menssagem que valida a escrita no banco de dados
def mensagem():
        msg1 = QMessageBox()
        msg1.setIcon(QMessageBox.Information)
        msg1.setWindowTitle('Lançamento!')
        msg1.setText('Lançamento Realizado!')
        x = msg1.exec()


def mensagem_editar():
    msg1 = QMessageBox()
    msg1.setIcon(QMessageBox.Information)
    msg1.setWindowTitle('Edição!')
    msg1.setText('Edição Realizada!')
    x = msg1.exec()

# Acessar a tabela categorias no banco de dados, retorna os dados no combobox
def combo_box_tela_editar():    
    try:
        banco_dados = sqlite3.connect('cfp.db')
        consulta = banco_dados.cursor()
        valor_consulta = consulta.execute("SELECT * FROM consulta_categoria").fetchall()

        for i in range(0, len(valor_consulta)):
            for j in range(0,1):
                lista = []
                lista.append((valor_consulta[i][j]))                       
                tela_editar.cbox.addItems(lista)    
        banco_dados.close()                        

    except sqlite3.Error as erro:
        print("Erro ao inserir dados!", erro)


# Editar lançamentos
def editar_lancamento():
    try:
        banco = sqlite3.connect('cfp.db')
        linha = tela.tableWidget.currentRow()
        cursor = banco.cursor()
        cursor.execute("SELECT id FROM movimentos")
        dados_lidos = cursor.fetchall()  
        valor_id = dados_lidos[linha][0]
        cursor.execute("SELECT * FROM movimentos WHERE id ="+ str(valor_id))
        edicao_lancamento = cursor.fetchall()
        global numero_id  # Chama variavel global
        numero_id = valor_id  # Será utilizado para salvar as edições da tela_editar
        print (edicao_lancamento[0])
        tela_editar.show()
        tela_editar.cbox.clear()  # Elimina a última atualização do combobox
        combo_box_tela_editar()    
        tela_editar.line_id.setText(str(edicao_lancamento[0][0]))
        tela_editar.line_data.setText(str(edicao_lancamento[0][1]))
        tela_editar.line_descricao.setText(str(edicao_lancamento[0][2]))
        tela_editar.cbox.setCurrentText(str(edicao_lancamento[0][3]))
        tela_editar.line_valor.setText(str(edicao_lancamento[0][4]))
    except sqlite3.Error as erro:
        print("Erro ao inserir dados!", erro) 
    banco.close()

# Salvar edição de lançamento
def salvar_edicao_lancamento():
    global numero_id
    print(numero_id)
    data = tela_editar.line_data.text()
    descricao = tela_editar.line_descricao.text()
    categoria = tela_editar.cbox.currentText()
    valor = tela_editar.line_valor.text()
    print(numero_id, data, descricao, categoria, valor)
    
    try:
        banco = sqlite3.connect('cfp.db')
        cursor = banco.cursor()        
        cursor.execute("UPDATE movimentos SET data = '{}', descricao = '{}', categoria = '{}', valor = '{}' WHERE id = {}".format(data, descricao, categoria, valor, numero_id))
    except sqlite3.Error as erro:
            print("Erro ao inserir dados!", erro) 
    banco.commit()

    mensagem_editar()
    tela_editar.close()
    consulta_dados()
    saldo()


# Salva nova categoria no banco de dados "categorias"
def salvar_categoria():
    categoria = tela.cbox.currentText().upper()
    if categoria == "":
        msg1 = QMessageBox()
        msg1.setIcon(QMessageBox.Information)
        msg1.setWindowTitle('Atenção!')
        msg1.setText('Digite a categoria que você precisa cadastrar!')
        x = msg1.exec()

    else:
        
        try:
            banco_dados = sqlite3.connect('cfp.db')
            cursor = banco_dados.cursor()
            cursor.execute("INSERT INTO categorias (categoria) VALUES ('"+categoria+"')")
            banco_dados.commit()
            banco_dados.close()
            msg1 = QMessageBox()
            msg1.setIcon(QMessageBox.Information)
            msg1.setWindowTitle('Lançamento!')
            msg1.setText('Categoria cadastrada!')
            x = msg1.exec()
            tela.cbox.clear()            
        except sqlite3.Error as erro:
            print("Erro ao inserir dados!", erro)    
    combo_box()       
                               

# Acessar a tabela categorias no banco de dados, retorna os dados no combobox
def combo_box():    
    try:
        banco_dados = sqlite3.connect('cfp.db')
        consulta = banco_dados.cursor()
        valor_consulta = consulta.execute("SELECT * FROM consulta_categoria").fetchall()

        for i in range(0, len(valor_consulta)):
            for j in range(0,1):
                lista = []
                lista.append((valor_consulta[i][j]))                       
                tela.cbox.addItems(lista)    
            banco_dados.close()                        

    except sqlite3.Error as erro:
        print("Erro ao inserir dados!", erro)        
        

# Acessar a tabela movimentos no banco de dados, realiza a soma do campo "valor" e retorna o resultado
def saldo():
    try:
        banco_dados = sqlite3.connect('cfp.db')
        consulta = banco_dados.cursor()
        valor_consulta = consulta.execute("SELECT SUM (valor) FROM movimentos").fetchall()
        
        for x in valor_consulta[0]:
            valor = x   
        # Retorna o saldo com a formatção pt-br - Ex: R$ 45.000,00   
        resultado_consulta = tela.line_saldo.setText(f'{valor:,.2f}'.format(valor).replace(",", "X").replace(".", ",").replace("X", "."))
        banco_dados.close()

    except sqlite3.Error as erro:
        print("Erro ao inserir dados!", erro)


# Retorna todos os dados do banco de dados na tabela do form
def consulta_dados():
    try:
        tela.show()
        banco_dados = sqlite3.connect('cfp.db')
        consulta = banco_dados.cursor()
        consulta.execute("SELECT * FROM movimentos")
        dados_lidos = consulta.fetchall()
        
        tela.tableWidget.setRowCount(len(dados_lidos))
        tela.tableWidget.setColumnCount(5)
        
        for i in range(0, len(dados_lidos)):
            
            for j in range(0,4):               
                tela.tableWidget.setItem(i,j,QtWidgets.QTableWidgetItem(str(dados_lidos[i][j])))

            for j in range(4,5):
                 
                dados = dados_lidos[i][j]
                dados_formatacao = (f'{dados:,.2f}'.format(dados).replace(",", "X").replace(".", ",").replace("X", "."))
                tela.tableWidget.setItem(i,j,QtWidgets.QTableWidgetItem(dados_formatacao))                
                
        banco_dados.close()
   
    except sqlite3.Error as erro:
        print("Erro ao inserir dados!", erro)        


# Salva os dados no banco de dados informados nos campos de texto do form
def salvar():
    reg1 = tela.line_data.text()
    reg2 = tela.line_valor.text()
    reg3 = tela.line_descricao.text()
    reg4 = tela.cbox.currentText()
    
    if reg1 == "" or reg2 == "" or reg3 == "" or reg4 == "":
        mensagem_falta_dados()
    else:
        validacao = tela.rb_pagamento.isChecked()
        if validacao == True:
            data = tela.line_data.text()
            vl_negativo = float(tela.line_valor.text()) * -1
            valor = str(vl_negativo)
            descricao = tela.line_descricao.text().upper()
            categoria = tela.cbox.currentText()            

        else:
            data = tela.line_data.text()
            valor = tela.line_valor.text()
            descricao = tela.line_descricao.text().upper()
            categoria = tela.cbox.currentText()            
            
        try:
            banco = sqlite3.connect('cfp.db')
            cursor = banco.cursor()
            cursor.execute("INSERT INTO movimentos (data, valor, descricao, categoria) VALUES ('"+data+"','"+valor+"','"+descricao+"','"+categoria+"')")
            banco.commit()
            banco.close()
            data = tela.line_data.setText("")
            valor = tela.line_valor.setText("")
            descricao = tela.line_descricao.setText("") 
            categoria = tela.cbox.clear()           
            mensagem()
            saldo()
            consulta_dados()
                        
      
        except sqlite3.Error as erro:
             print("Erro ao inserir dados!", erro)
    combo_box()
 

app = QtWidgets.QApplication([])
tela = uic.loadUi("controle.ui")
tela_editar = uic.loadUi("editar_lancamento.ui")
tela.cbox.clear()
tela.bt_salvar.clicked.connect(salvar)
tela.bt_categoria.clicked.connect(salvar_categoria)
tela.bt_editar.clicked.connect(editar_lancamento)
tela_editar.bt_salvar.clicked.connect(salvar_edicao_lancamento)
combo_box()
saldo()
consulta_dados()
tabela_medidas()
tela.show()
app.exec()
