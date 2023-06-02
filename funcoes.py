from datetime import datetime
import psycopg2
from kivy.core.window import Window
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.uix.spinner import Spinner
from kivymd.toast import toast
from kivymd.uix.label import MDLabel
from kivymd.uix.textfield import MDTextField


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


def conectar():
    conn = psycopg2.connect(
        host="localhost",
        database="DIBTOP",
        user="postgres",
        password="postgres"
    )
    return conn


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


def conf_data(data):
    data = str(data)
    ano = data[0:4]
    mes = data[5:7]
    dia = data[8:11]
    data = dia + '/' + mes + '/' + ano
    return data


def limpar_campos(self):
    for widget in self.ids.values():
        if isinstance(widget, MDLabel):
            widget.text = '-'
        if isinstance(widget, MDTextField):
            widget.text = ""


def principal(self):
    limpar_campos(self)
    self.manager.current = 'principal'


def pegar_id(opcao):
    opcao = opcao.split('-')[0].strip()
    return opcao


def deletar(self, cod, tabela):
    def confirmar_exclusao():
        try:
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
            elif tabela == 'curso':
                script = 'DELETE FROM turma WHERE id_turma = %s;'
            else:
                script = 'deu erro'

            cur.execute(script, (id_,))
            conn.commit()
            conn.close()

            toast("Registro excluído com sucesso!", duration=5)

            btn = self.btnbuscar
            btn.trigger_action()

        except Exception as e:
            toast(f"Error: {e}", duration=5)
            print(e)

    popup = ConfirmationPopup(callback=confirmar_exclusao)
    popup.open()


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

    else:
        print('tabela ainda nao implementada')


def consulta_banco(self, tabela, query, id_item, *args):
    tela = 'cad_' + str(tabela)
    self.screen_manager.current = tela
    tela_atual = self.screen_manager.current_screen

    conn = conectar()
    cur = conn.cursor()

    try:
        cur.execute(query, (id_item,))

        consulta = cur.fetchone()

        if tabela == 'aluno':
            nome, cpf, dt_nasc, end, email, telefone, naturalidade, nome_mae, estado_civil, escolaridade = consulta

            tela_atual.ids.idaluno.text = id_item
            tela_atual.ids.idnome.text = nome
            tela_atual.ids.idcpf.text = cpf
            dt_nasc = conf_data(dt_nasc)
            tela_atual.ids.iddtnasc.text = dt_nasc
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
            descricao, ch, numod, valor, dupli = consulta

            tela_atual.ids.idcurso.text = id_item
            tela_atual.ids.desc.text = descricao
            tela_atual.ids.ch.text = str(ch)
            tela_atual.ids.numod.text = str(numod)
            tela_atual.ids.valor.text = str(valor)
            tela_atual.ids.dupli.text = str(dupli)

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
        query = '''SELECT descricao, ch, num_modulos, vlr_total, num_duplicatas FROM curso WHERE id_curso = %s'''

    consulta_banco(self, tabela, query, id_item)
