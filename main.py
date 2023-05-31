from kivy.event import EventDispatcher
from kivy.lang import Builder
from kivy.properties import StringProperty
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import ScreenManager, NoTransition
from kivy.uix.spinner import Spinner
from kivymd.uix.label import MDLabel
from kivymd.uix.screen import MDScreen
from kivy.core.window import Window
from kivymd.app import MDApp
import psycopg2
from kivymd.toast import toast
from datetime import datetime
from kivymd.uix.list import TwoLineAvatarIconListItem
from kivymd.uix.textfield import MDTextField


# ----------------------  FUNÇÕES -------------------------------

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


def pegar_id(opcao):
    opcao = opcao.split('-')[0].strip()
    return opcao


# ---------------------   CLASES   ----------------------------

class NavigationManager:
    tabela = StringProperty('')

    def __init__(self, screen_manager):
        self.screen_manager = screen_manager

    def return_to_principal(self):
        self.screen_manager.current = 'principal'


class MainScreenManager(ScreenManager):
    pass


class ListaItem(TwoLineAvatarIconListItem):
    info1 = StringProperty('')
    info2 = StringProperty('')

    def __init__(self, id_item='', info1='', info2='', tabela='', btnbuscar=None, **kwargs):
        super(ListaItem, self).__init__(**kwargs)
        self.btnbuscar = btnbuscar
        self.id_item = id_item
        self.info1 = info1
        self.info2 = info2
        self.tabela = tabela

    def deletar(self):
        deletar(self, self.id_item, self.tabela)


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


class ConfirmationPopup(Popup):
    def __init__(self, callback, **kwargs):
        super(ConfirmationPopup, self).__init__(**kwargs)
        self.callback = callback

    def confirm(self):
        self.callback()
        self.dismiss()


class CustomSpinner(Spinner):
    pass


# ---------------------  CLASES MDSCREEN --------------------


class MainScreen(MDScreen):
    logado = StringProperty('')

    def crud(self, nome):
        self.manager.get_screen('crud').btn_name = nome
        self.manager.current = 'crud'


class LoginScreen(MDScreen):
    def get_data(self):
        login = self.ids.idlogin.text
        senha = self.ids.idsenha.text
        if validar_login(login, senha):
            toast("Login e senha válidos", duration=2)
            self.manager.get_screen('principal').logado = login
            self.manager.get_screen('crud').logado = login

            self.manager.current = 'principal'

        else:
            toast("Login ou senha inválidos", duration=5)

    def mensagem(self):
        toast('Informe o administrador e crie um novo login', duration=7)


class CrudScreen(MDScreen):
    btn_name = StringProperty('')
    logado = StringProperty('')
    print(logado, 'logado')

    def cadastrar(self, btn_name=None):
        btn_name = btn_name or self.btn_name
        tela = 'cad_' + btn_name

        if btn_name == 'funcionario':
            if self.logado == 'monykpp':
                self.manager.current = tela
            else:
                toast('Você não tem acesso ao cadastro de funcionarios')
        else:
            self.manager.current = tela

    def consultar(self, btn_name=None):
        btn_name = btn_name or self.btn_name

        if btn_name == 'funcionario':
            if self.logado == 'monykpp':
                self.manager.get_screen('consultar').tabela = btn_name
                self.manager.current = 'consultar'
            else:
                toast('Você não tem acesso ao cadastro de funcionarios')
        else:
            self.manager.get_screen('consultar').tabela = btn_name
            self.manager.current = 'consultar'


class CadastrarAluno(MDScreen):
    def principal(self):
        principal(self)

    def salvar_dados(self):

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

            # Converte a string da data de nascimento para um objeto datetime
            dt_nasc = datetime.strptime(dt_nasc, '%d/%m/%Y')

            conn = conectar()
            cur = conn.cursor()

            if idaluno == '-':
                cur.execute("""INSERT into Aluno 
                (nome,cpf,dt_nasc,endereco,email,telefone,naturalidade,nome_mae,estado_civil,escolaridade) 
                Values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (nome, cpf, dt_nasc, endereco, email, telefone, naturalidade,
                      nome_mae, estado_civil, escolaridade))
            else:
                cur.execute("""UPDATE Aluno 
                            SET nome = %s,cpf = %s,dt_nasc = %s,endereco = %s,email = %s,telefone = %s,
                            naturalidade = %s,nome_mae = %s,estado_civil = %s,escolaridade = %s
                            WHERE id_aluno = %s""", (nome, cpf, dt_nasc, endereco, email, telefone,
                                                     naturalidade, nome_mae, estado_civil, escolaridade, idaluno))

            conn.commit()  # Confirma a transação
            toast("Salvo com sucesso!", duration=2)

            principal(self)

        except Exception as e:
            toast(f"Erro ao salvar dados: {e}", duration=5)
            print(e)


class CadastrarProfessor(MDScreen):
    def principal(self):
        principal(self)

    def salvar_dados(self):
        try:
            idprof = self.ids.idprof.text
            nome = self.ids.nome.text
            cpf = self.ids.cpf.text
            area = self.ids.ae.text
            endereco = self.ids.end.text
            email = self.ids.email.text
            telefone = self.ids.tel.text

            conn = conectar()
            cur = conn.cursor()

            if idprof == '-':
                cur.execute("""INSERT into Professor
                (nome, cpf, area_ensino, endereco, email, telefone)
                Values (%s, %s, %s, %s, %s, %s)
                """, (nome, cpf, area, endereco, email, telefone))

            else:
                cur.execute("""UPDATE Professor
                            SET nome = %s,cpf = %s,area_ensino = %s,endereco = %s,email = %s,telefone = %s
                            WHERE id_professor = %s""", (nome, cpf, area, endereco, email, telefone, idprof))

            conn.commit()  # Confirma a transação
            toast("Salvo com sucesso!", duration=2)

            principal(self)

        except Exception as e:
            toast(f"Erro ao salvar dados: {e}", duration=5)
            print(e)


class CadastrarFuncionario(MDScreen):
    def principal(self):
        principal(self)

    def salvar_dados(self):

        try:
            nome = self.ids.nome.text
            login = self.ids.login.text
            senha = self.ids.senha.text
            senha2 = self.ids.senha2.text

            if senha == senha2:

                conn = conectar()
                cur = conn.cursor()
                cur.execute("""INSERT into Funcionario (nome, login, senha)Values (%s, %s, %s)""", (nome, login, senha))
                conn.commit()

                toast("Salvo com sucesso!", duration=2)
                self.principal()

            else:
                toast('Senhas não coincidem', duration=4)

        except Exception as e:
            toast(f"Erro ao salvar dados: {e}", duration=5)
            print(e)


class CadastrarSala(MDScreen):

    def principal(self):
        principal(self)

    def salvar_dados(self):
        try:
            idsala = self.ids.sala.text
            numero = self.ids.numero.text
            descricao = self.ids.descricao.text
            capacidade = self.ids.capac.text

            conn = conectar()
            cur = conn.cursor()

            if idsala == '-':
                cur.execute("""INSERT into Sala (descricao, numero, capacidade) Values (%s, %s, %s)
                """, (descricao, numero, capacidade))
            else:
                cur.execute("""UPDATE Sala
                            SET descricao = %s,numero = %s,capacidade = %s
                            WHERE id_sala = %s""", (descricao, numero, capacidade, idsala))

            conn.commit()  # Confirma a transação

            toast("Salvo com sucesso!", duration=2)
            self.principal()

        except Exception as e:
            toast(f"Erro ao salvar dados: {e}", duration=2)


class Consultar(MDScreen):
    tabela = StringProperty('')
    print(tabela, 'nome tabela')

    def pesquisar(self, texto):
        try:
            conn = conectar()
            cur = conn.cursor()

            if self.tabela == 'aluno':
                script = 'SELECT aluno.id_aluno, aluno.nome, aluno.cpf FROM aluno WHERE aluno.nome LIKE %s ORDER BY 2'
            elif self.tabela == 'professor':
                script = '''SELECT professor.id_professor, professor.nome, professor.cpf FROM professor 
                            WHERE professor.nome LIKE %s ORDER BY 2'''
            elif self.tabela == 'funcionario':
                script = '''SELECT funcionario.id_funcionario, funcionario.nome,funcionario.login FROM funcionario
                           WHERE funcionario.nome LIKE %s ORDER BY 2'''
            elif self.tabela == 'sala':
                script = '''SELECT sala.id_sala, sala.descricao, sala.capacidade FROM sala
                           WHERE sala.descricao LIKE %s ORDER BY 2'''
            else:
                script = 'deu erro'

            cur.execute(script, ('%' + texto + '%',))

            self.ids.consulta_list.clear_widgets()

            btnbuscar = self.ids.btnbuscar
            consulta = cur.fetchall()

            for row in consulta:
                id_it, info1, info2 = row

                if self.tabela == 'sala':
                    info2 = 'capacidade: ' + str(info2)

                item = ListaItem(id_item=str(id_it), info1=str(info1), info2=str(info2), tabela=self.tabela,
                                 btnbuscar=btnbuscar)

                self.ids.consulta_list.add_widget(item)

            conn.close()

        except Exception as e:
            toast(f"Erro: {e}", duration=5)
            print(e)

    def novo(self):

        if self.tabela == 'aluno':
            tela = 'cad_aluno'
        elif self.tabela == 'professor':
            tela = 'cad_professor'
        elif self.tabela == 'funcionario':
            tela = 'cad_funcionario'
        elif self.tabela == 'sala':
            tela = 'cad_sala'
        else:
            tela = 'principal'

        self.ids.consulta_list.clear_widgets()
        self.manager.current = tela

    def cancelar(self):
        self.ids.consulta_list.clear_widgets()
        self.manager.current = 'principal'


class CadastrarCurso(MDScreen):

    def principal(self):
        principal(self)

    def opcoes(self):
        op = []

        conn = conectar()
        cur = conn.cursor()

        cur.execute('SELECT * FROM sala')
        consulta = cur.fetchall()

        for row in consulta:
            idc, desc, n, capac = row
            frase = str(idc) + ' - ' + desc + ' (' + str(n) + '), capac: ' + str(capac)
            op.append(frase)
        return op

    def salvar_dados(self):
        try:

            idsala = pegar_id(self.ids.sala.text)
            idcurso = self.ids.idcurso.text
            ch = self.ids.ch.text
            descricao = self.ids.desc.text
            numod = self.ids.numod.text
            valor = self.ids.valor.text
            dupli = self.ids.dupli.text

            conn = conectar()
            cur = conn.cursor()

            if idcurso == '-':
                cur.execute("""INSERT into Curso (id_sala, descricao, CH, num_modulos, VLR_total, num_duplicatas) 
                Values (%s, %s, %s, %s, %s, %s)""", (idsala, descricao, ch, numod, valor, dupli))
            else:
                cur.execute("""UPDATE Curso SET id_sala = %s, descricao = %s, CH = %s, num_modulos = %s, VLR_total = %s,
                 num_duplicatas = %s WHERE id_curso = %s""", (idsala, descricao, ch, numod, valor, dupli, idcurso))

            conn.commit()  # Confirma a transação

            toast("Salvo com sucesso!", duration=2)
            self.principal()

        except Exception as e:
            toast(f"Erro ao salvar dados: {e}", duration=2)


class ConsultarCurso(MDScreen):
    pass


class CadastrarTurma(MDScreen):
    def principal(self):
        principal(self)

    def salvar_dados(self):

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

            # Converte a string da data de nascimento para um objeto datetime
            dt_nasc = datetime.strptime(dt_nasc, '%d/%m/%Y')

            conn = conectar()
            cur = conn.cursor()

            if idaluno == '-':
                cur.execute("""INSERT into Aluno 
                 (nome,cpf,dt_nasc,endereco,email,telefone,naturalidade,nome_mae,estado_civil,escolaridade) 
                 Values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                 """, (nome, cpf, dt_nasc, endereco, email, telefone, naturalidade,
                       nome_mae, estado_civil, escolaridade))
            else:
                cur.execute("""UPDATE Aluno 
                             SET nome = %s,cpf = %s,dt_nasc = %s,endereco = %s,email = %s,telefone = %s,
                             naturalidade = %s,nome_mae = %s,estado_civil = %s,escolaridade = %s
                             WHERE id_aluno = %s""", (nome, cpf, dt_nasc, endereco, email, telefone,
                                                      naturalidade, nome_mae, estado_civil, escolaridade, idaluno))

            conn.commit()  # Confirma a transação
            toast("Salvo com sucesso!", duration=2)

            principal(self)

        except Exception as e:
            toast(f"Erro ao salvar dados: {e}", duration=5)
            print(e)


class ConsultarTurma(MDScreen):
    pass


class CadastrarAlunoTurma(MDScreen):
    pass


class ConsultarAlunoTurma(MDScreen):
    pass


class CadastrarPagamento(MDScreen):
    pass


class ConsultarPagamento(MDScreen):
    pass


# --------------------------- APP ---------------------------------

class DibTopApp(MDApp):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.navigation = None

    def build(self):
        Builder.load_file("screens.kv")

        Window.clearcolor = (1, 1, 1, 1)
        # Window.maximize()
        self.theme_cls.primary_palette = "Green"

        sm = MainScreenManager(transition=NoTransition())
        #   sm.current = 'login'

        self.navigation = NavigationManager(sm)  # Passando a instância de MainScreenManager para NavigationManager
        return sm


# run the app
if __name__ == "__main__":
    DibTopApp().run()
