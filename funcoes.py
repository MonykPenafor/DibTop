from datetime import datetime
import psycopg2
from kivy.core.window import Window
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.uix.spinner import Spinner
from kivy.uix.textinput import TextInput
from kivymd.toast import toast
from kivymd.uix.label import MDLabel
from kivymd.uix.textfield import MDTextField


# --------------------------------  CLASSES -------------------------------------

class ConfirmationPopup(Popup):
    def __init__(self, callback, **kwargs):
        super(ConfirmationPopup, self).__init__(**kwargs)
        self.callback = callback

    def confirm(self):
        self.callback()
        self.dismiss()


class HoverButton(Button):
    def __init__(self, **kwargs):
        super(HoverButton, self).__init__(**kwargs)
        self.background_normal = ''  # Define background_normal como uma string vazia para remover a cor de fundo padrão
        self.bind(on_enter=self.on_enter, on_leave=self.on_leave)
        Window.bind(mouse_pos=self.on_mouse_pos)

    def on_mouse_pos(self, *args):
        if self.collide_point(*self.to_widget(*args[1])):
            self.on_enter()
        else:
            self.on_leave()

    def on_enter(self, *args):
        self.background_color = (0, 0.737, 0.831, 1)  # cor hover bg
        self.color = 'white'  # cor do texto hover

    def on_leave(self, *args):
        self.background_color = (0.247, 0.318, 0.71, 1)  # cor bg
        self.color = 'white'  # cor do texto


class CustomSpinner(Spinner):
    pass


class Caixa(TextInput):
    pass


# ---------------------------------------  FUNÇÕES  -----------------------------------------


# CONECTAR COM O BANCO
def conectar():
    conn = psycopg2.connect(
        host="localhost",
        database="DIBTOP",
        user="postgres",
        password="postgres"
    )
    return conn


# VALIDAR LOGIN, DEVOLVE TRUE SE FOR VALIDO E FALSE SE FOR INVALIDO
def validar_login(login, senha):
    try:
        conn = conectar()
        cur = conn.cursor()
        cur.execute("SELECT * FROM funcionario WHERE login = %s AND senha = %s", (login, senha))
        resultado = cur.fetchone()
        if resultado:
            return True
        else:
            return False
    except Exception as e:
        print(f"Error ao validar login: {e}")
        return False


# CONFIGURAR DATA PARA TRAZER ELA CONFIGURADA DO BANCO DE DADOS (AO TRAZER TELA EDITAR)
def conf_data(data):
    data = str(data)
    ano = data[0:4]
    mes = data[5:7]
    dia = data[8:11]
    data = dia + '/' + mes + '/' + ano
    return data


# LIMPAR OS CAMPOS DE TEXTO DAS TELAS DE CADASTRO
def limpar_campos(self):
    for widget in self.ids.values():
        if isinstance(widget, MDLabel):
            widget.text = '-'
        if isinstance(widget, MDTextField):
            widget.text = ""


# VOLTAR PARA A TELA PRINCIPAL DEPOIS DE EXECUTAR A FUNÇÃO LIMPAR_CAMPOS
def principal(self):
    limpar_campos(self)
    self.manager.current = 'principal'


# PEGAR O ID DA SALA ESCOLHIDA NO SPINNER
def pegar_id(opcao):
    opcao = opcao.split('-')[0].strip()
    return opcao


# DELETAR UM REGISTRO
def deletar(self, cod, tabela):
    def confirmar_exclusao():
        try:
            script = ''
            conn = conectar()
            cur = conn.cursor()

            id_ = int(cod)

            if tabela == 'aluno':
                script = 'DELETE FROM aluno WHERE id_aluno = %s;'
            elif tabela == 'professor':
                script = 'DELETE FROM professor WHERE id_professor = %s;'
            elif tabela == 'funcionario':
                script = 'DELETE FROM funcionario WHERE id_funcionario = %s;'
            elif tabela == 'sala':
                script = 'DELETE FROM sala WHERE id_sala = %s;'
            elif tabela == 'curso':
                script = 'DELETE FROM curso WHERE id_curso = %s;'
            elif tabela == 'turma':
                script = 'DELETE FROM turma WHERE id_turma = %s;'
            elif tabela == 'alunoturma':
                script = 'DELETE FROM aluno_turma WHERE id_aluno_turma = %s;'
            else:
                print('nenhuma ação para a seguinte tabela: ', tabela)
                toast(f'nenhuma ação para a seguinte tabela:{tabela}', duration=5)

            cur.execute(script, (id_,))
            conn.commit()
            conn.close()

            toast("Registro excluído com sucesso!", duration=5)

            btn = self.btnbuscar  # atualizar consulta
            btn.trigger_action()

        except Exception as e:
            toast(f"Erro: {e}", duration=5)
            print(e)

    popup = ConfirmationPopup(callback=confirmar_exclusao)  # popup para confirma exclusão
    popup.open()


# OPCOES DO SPINNER DAS SALAS NA TELA DE CAD_CURSO
def opcoes():
    op = []

    conn = conectar()
    cur = conn.cursor()

    cur.execute('SELECT * FROM sala')
    consulta = cur.fetchall()

    for row in consulta:
        idsala, desc, n, capac = row
        frase = str(idsala) + ' - ' + desc + ' (' + str(n) + '), capac: ' + str(capac)
        op.append(frase)
    return op


# FAZER O INSERT OU UPDATE NA TABELA QUE TRAZ COMO PARAMETRO
def salvar(self, tabela):
    conn = conectar()
    cur = conn.cursor()

    if tabela == 'aluno':

        try:
            idaluno = self.ids.idaluno.text
            nome = self.ids.idnome.text
            cpf = self.ids.idcpf.text
            dt_nasc = self.ids.iddtnasc.text
            endereco = self.ids.idend.text
            email = self.ids.idemail.text
            telefone = self.ids.idtel.text
            naturalidade = self.ids.idnat.text
            nome_mae = self.ids.idnomemae.text
            estado_civil = self.ids.idestcivil.text
            escolaridade = self.ids.idesc.text
            dt_nasc = datetime.strptime(dt_nasc, '%d/%m/%Y')

            if idaluno == '-':
                cur.execute("""INSERT into Aluno (nome,cpf,dt_nasc,endereco,email,telefone,naturalidade,nome_mae,
                                       estado_civil,escolaridade) Values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                            (nome, cpf, dt_nasc, endereco, email, telefone, naturalidade, nome_mae, estado_civil,
                             escolaridade))
            else:
                cur.execute("""UPDATE Aluno SET nome = %s,cpf = %s,dt_nasc = %s,endereco = %s,email = %s,telefone = %s,
                            naturalidade = %s,nome_mae = %s,estado_civil = %s,escolaridade = %s WHERE id_aluno = %s""",
                            (nome, cpf, dt_nasc, endereco, email, telefone, naturalidade, nome_mae, estado_civil,
                             escolaridade, idaluno))

            conn.commit()  # Confirma a transação
            toast("Salvo com sucesso!", duration=2)

            principal(self)

        except Exception as e:
            toast(f"Erro ao salvar dados: {e}", duration=5)
            print(e)

    elif tabela == 'professor':
        try:
            idprof = self.ids.idprof.text
            nome = self.ids.nome.text
            cpf = self.ids.cpf.text
            area = self.ids.ae.text
            endereco = self.ids.end.text
            email = self.ids.email.text
            telefone = self.ids.tel.text

            if idprof == '-':
                cur.execute("""INSERT into Professor (nome, cpf, area_ensino, endereco, email, telefone)
                       Values (%s, %s, %s, %s, %s, %s) """, (nome, cpf, area, endereco, email, telefone))

            else:
                cur.execute("""UPDATE Professor SET nome = %s,cpf = %s,area_ensino = %s,endereco = %s,email = %s,
                       telefone = %s WHERE id_professor = %s""", (nome, cpf, area, endereco, email, telefone, idprof))

            conn.commit()  # Confirma a transação
            toast("Salvo com sucesso!", duration=2)

            principal(self)

        except Exception as e:
            toast(f"Erro ao salvar dados: {e}", duration=5)
            print(e)

    elif tabela == 'funcionario':
        try:
            idfunc = self.ids.idfunc.text
            nome = self.ids.nome.text
            login = self.ids.login.text
            senha = self.ids.senha.text
            senha2 = self.ids.senha2.text

            if senha == senha2:

                conn = conectar()
                cur = conn.cursor()

                if idfunc == '-':
                    cur.execute("""INSERT into Funcionario (nome, login, senha)Values (%s, %s, %s)""",
                                (nome, login, senha))
                else:
                    cur.execute("""UPDATE Funcionario SET nome = %s,login = %s,senha = %s
                                   WHERE id_funcionario = %s""", (nome, login, senha, idfunc))

                conn.commit()

                toast("Salvo com sucesso!", duration=2)
                self.principal()

            else:
                toast('Senhas não coincidem', duration=4)

        except Exception as e:
            toast(f"Erro ao salvar dados: {e}", duration=5)
            print(e)

    elif tabela == 'sala':
        try:
            idsala = self.ids.idsala.text
            numero = self.ids.numero.text
            descricao = self.ids.descricao.text
            capacidade = self.ids.capac.text

            if idsala == '-':
                cur.execute("""INSERT into Sala (descricao, numero, capacidade) 
                                        Values (%s, %s, %s)""", (descricao, numero, capacidade))
            else:
                cur.execute("""UPDATE Sala SET descricao = %s,numero = %s,capacidade = %s
                                    WHERE id_sala = %s""", (descricao, numero, capacidade, idsala))

            conn.commit()  # Confirma a transação

            toast("Salvo com sucesso!", duration=2)
            self.principal()

        except Exception as e:
            toast(f"Erro ao salvar dados: {e}", duration=2)

    elif tabela == 'curso':
        try:
            idsala = pegar_id(self.ids.sala.text)
            idcurso = self.ids.idcurso.text
            ch = self.ids.ch.text
            descricao = self.ids.desc.text
            numod = self.ids.numod.text
            valor = self.ids.valor.text
            dupli = self.ids.dupli.text

            if idcurso == '-':
                cur.execute("""INSERT into Curso (id_sala, descricao, CH, num_modulos, VLR_total, num_duplicatas) 
                       Values (%s, %s, %s, %s, %s, %s)""", (idsala, descricao, ch, numod, valor, dupli))
            else:
                cur.execute("""UPDATE Curso SET id_sala = %s, descricao = %s, CH = %s, num_modulos = %s, VLR_total = %s,
                        num_duplicatas = %s WHERE id_curso = %s""",
                            (idsala, descricao, ch, numod, valor, dupli, idcurso))

            conn.commit()  # Confirma a transação

            toast("Salvo com sucesso!", duration=2)
            self.principal()

        except Exception as e:
            toast(f"Erro ao salvar dados: {e}", duration=2)

    elif tabela == 'turma':
        try:

            idprof = pegar_id(self.ids.prof.text)
            idcurso = pegar_id(self.ids.curso.text)

            idturma = self.ids.idturma.text
            turno = self.ids.turno.text
            dias = self.ids.dias.text
            inicio = datetime.strptime(self.ids.inicio.text, '%d/%m/%Y')
            termino = datetime.strptime(self.ids.inicio.text, '%d/%m/%Y')

            if idturma == '-':
                cur.execute("""INSERT into turma (id_curso, id_professor, turno, dias_semana, DT_inicio, DT_termino) 
                       Values (%s, %s, %s, %s, %s, %s)""", (idcurso, idprof, turno, dias, inicio, termino))
            else:
                cur.execute("""UPDATE turma SET id_curso = %s, id_professor = %s, turno = %s, dias_semana = %s, DT_inicio = %s,
                        DT_termino = %s WHERE id_turma = %s""",
                            (idcurso, idprof, turno, dias, inicio, termino, idturma))

            conn.commit()  # Confirma a transação

            toast("Salvo com sucesso!", duration=2)
            self.principal()

        except Exception as e:
            toast(f"Erro ao salvar dados: {e}", duration=2)

    elif tabela == 'alunoturma':
        try:

            idaluno = pegar_id(self.ids.aluno.text)
            idturma = pegar_id(self.ids.turma.text)

            idalunoturma = self.ids.idalunoturma.text
            matricula = self.ids.matricula.text
            ativo = self.ids.ativo.text
            certificado = self.ids.certificado.text

            if idalunoturma == '-':
                cur.execute("""INSERT into aluno_turma (id_turma, id_aluno, matricula, ativo, certificado_entregue) 
                       Values (%s, %s, %s, %s, %s)""", (idturma, idaluno, matricula, ativo, certificado))
            else:
                cur.execute("""UPDATE aluno_turma SET id_turma = %s, id_aluno = %s, matricula = %s, ativo = %s, 
                certificado_entregue = %s WHERE id_aluno_turma = %s""",
                            (idturma, idaluno, matricula, ativo, certificado, idalunoturma))

            conn.commit()  # Confirma a transação

            toast("Salvo com sucesso!", duration=2)
            self.principal()

        except Exception as e:
            toast(f"Erro ao salvar dados: {e}", duration=2)

    else:
        print('tabela ainda nao implementada')


# ----------------------------- FUNÇÕES DA TELA EDITAR ----------------------------------------

# REFAZER A OPCAO DE SALA DO SPINNER DA TELA EDITAR DO CURSO DE ACORDO COM O ID DA SALA
def sala_spinner_frase(id_id):
    conn = conectar()
    cur = conn.cursor()

    cur.execute('''SELECT descricao, numero, capacidade FROM sala WHERE id_sala = %s''', (id_id,))
    consulta = cur.fetchone()

    descricao, numero, capacidade = consulta

    frase = str(id_id) + ' - ' + descricao + ' (' + str(numero) + '), capac: ' + str(capacidade)
    return frase


def frase_chave_estrangeira(id_id, tabela):
    conn = conectar()
    cur = conn.cursor()

    if tabela == 'curso':
        cur.execute('''SELECT descricao FROM curso WHERE id_curso = %s''', (id_id,))
        info = cur.fetchone()

        frase = str(id_id) + ' - ' + info[0]

    elif tabela == 'prof':
        cur.execute('''SELECT nome, cpf FROM professor WHERE id_professor = %s''', (id_id,))
        consulta = cur.fetchone()
        info, info2 = consulta

        frase = str(id_id) + ' - ' + info + '  |  cpf: ' + str(info2)

    elif tabela == 'aluno':
        cur.execute('''SELECT nome, cpf FROM aluno WHERE id_aluno = %s''', (id_id,))
        consulta = cur.fetchone()
        info, info2 = consulta

        frase = str(id_id) + ' - ' + info + '  |  cpf: ' + str(info2)

    elif tabela == 'turma':
        cur.execute('''SELECT curso.descricao, professor.nome FROM turma, professor, curso WHERE turma.id_professor = 
        professor.id_professor and turma.id_curso = curso.id_curso and turma.id_turma = %s ''', (id_id,))

        consulta = cur.fetchone()
        info, info2 = consulta

        frase = str(id_id) + ' - ' + info + '  |  prof.: ' + str(info2)

    else:
        frase = 'deu erro'
    return frase


# ATRIBUIR OS VALORES QUE RECEBEU DA CONSULTA REALIZADA NA TABELA AOS CAMPOS DE TEXTO DA TELA DE CADASTRO ESPECIFICA
def consulta_banco(self, tabela, query, id_item, *args):
    tela = 'cad_' + str(tabela)
    self.screen_manager.current = tela
    tela_atual = self.screen_manager.current_screen

    conn = conectar()
    cur = conn.cursor()

    print(tela)

    try:
        cur.execute(query, (id_item,))

        consulta = cur.fetchone()

        if tabela == 'aluno':
            nome, cpf, dt_nasc, end, email, telefone, naturalidade, nome_mae, estado_civil, escolaridade = consulta

            tela_atual.ids.idaluno.text = id_item
            tela_atual.ids.idnome.text = nome
            tela_atual.ids.idcpf.text = cpf
            tela_atual.ids.iddtnasc.text = conf_data(dt_nasc)
            tela_atual.ids.idend.text = end
            tela_atual.ids.idemail.text = email
            tela_atual.ids.idtel.text = telefone
            tela_atual.ids.idnat.text = naturalidade
            tela_atual.ids.idnomemae.text = nome_mae
            tela_atual.ids.idestcivil.text = estado_civil
            tela_atual.ids.idesc.text = escolaridade

        elif tabela == 'professor':
            nome, cpf, area_ensino, endereco, email, telefone = consulta

            tela_atual.ids.idprof.text = id_item
            tela_atual.ids.nome.text = nome
            tela_atual.ids.cpf.text = cpf
            tela_atual.ids.ae.text = cpf
            tela_atual.ids.end.text = endereco
            tela_atual.ids.email.text = email
            tela_atual.ids.tel.text = telefone

        elif tabela == 'funcionario':
            nome, login = consulta

            tela_atual.ids.idfunc.text = id_item
            tela_atual.ids.nome.text = nome
            tela_atual.ids.login.text = login

        elif tabela == 'sala':
            descricao, numero, capacidade = consulta

            tela_atual.ids.idsala.text = id_item
            tela_atual.ids.descricao.text = descricao
            tela_atual.ids.numero.text = str(numero)
            tela_atual.ids.capac.text = str(capacidade)

        elif tabela == 'curso':
            print(consulta)

            id_sala, descricao, ch, numod, valor, dupli = consulta

            tela_atual.ids.idcurso.text = id_item
            tela_atual.ids.sala.text = sala_spinner_frase(id_sala)
            tela_atual.ids.desc.text = descricao
            tela_atual.ids.ch.text = str(ch)
            tela_atual.ids.numod.text = str(numod)
            tela_atual.ids.valor.text = str(valor)
            tela_atual.ids.dupli.text = str(dupli)

        elif tabela == 'turma':
            print(consulta)

            id_prof, id_curso, turno, dt_inicio, dt_termino, dias_semana = consulta

            tela_atual.ids.prof.text = frase_chave_estrangeira(id_prof, 'prof')
            tela_atual.ids.curso.text = frase_chave_estrangeira(id_curso, 'curso')

            tela_atual.ids.idturma.text = id_item
            tela_atual.ids.inicio.text = conf_data(dt_inicio)
            tela_atual.ids.termino.text = conf_data(dt_termino)
            tela_atual.ids.turno.text = turno
            tela_atual.ids.dias.text = dias_semana

        elif tabela == 'alunoturma':
            print(consulta)

            id_aluno, id_turma, matri, ativo, certificado = consulta

            tela_atual.ids.aluno.text = frase_chave_estrangeira(id_aluno, 'aluno')
            tela_atual.ids.turma.text = frase_chave_estrangeira(id_turma, 'turma')

            tela_atual.ids.idalunoturma.text = id_item

            tela_atual.ids.matricula.text = str(matri)
            tela_atual.ids.ativo.text = ativo
            tela_atual.ids.certificado.text = certificado

    except Exception as e:
        toast(f"Error: {e}", duration=5)
        print(e)

    finally:
        conn.commit()
        conn.close()

    self.screen_manager.get_screen(tela).tabela = self.tabela


def editar(self, id_item, tabela):
    query = ""

    if tabela == 'aluno':
        query = '''SELECT nome, cpf, dt_nasc, endereco, email, telefone, naturalidade, nome_mae, 
                    estado_civil, escolaridade FROM aluno WHERE aluno.id_aluno = %s'''

    elif tabela == 'professor':
        query = '''SELECT nome, cpf, area_ensino, endereco, email,telefone FROM professor WHERE id_professor = %s'''

    elif tabela == 'funcionario':
        query = '''SELECT nome, login FROM funcionario WHERE id_funcionario = %s'''

    elif tabela == 'sala':
        query = '''SELECT descricao, numero, capacidade FROM sala WHERE id_sala = %s'''

    elif tabela == 'curso':
        query = '''SELECT sala.id_sala, curso.descricao, curso.ch, curso.num_modulos, curso.vlr_total,
        curso.num_duplicatas FROM curso, sala WHERE sala.id_sala = curso.id_sala and id_curso = %s'''

    elif tabela == 'turma':
        query = '''SELECT id_professor, id_curso, turno, dt_inicio, dt_termino, dias_semana 
        FROM turma WHERE id_turma = %s'''

    elif tabela == 'alunoturma':
        query = '''SELECT id_aluno, id_turma, matricula, ativo, certificado_entregue FROM aluno_turma
        WHERE id_aluno_turma = %s'''

    consulta_banco(self, tabela, query, id_item)
# ---------------------------------------------------------------------------------------------
