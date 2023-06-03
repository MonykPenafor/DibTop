from kivy.lang import Builder
from kivy.properties import StringProperty
from kivy.uix.screenmanager import ScreenManager, NoTransition
from kivy.uix.spinner import SpinnerOption, Spinner
from kivymd.uix.screen import MDScreen
from kivy.core.window import Window
from kivymd.app import MDApp
from kivymd.toast import toast
from kivymd.uix.list import TwoLineAvatarIconListItem, OneLineListItem
from funcoes import conectar, validar_login, principal, deletar, salvar, editar


# ---------------------   CLASES   ----------------------------

class MainScreenManager(ScreenManager):
    pass


class ListaItem(TwoLineAvatarIconListItem):
    info1 = StringProperty('')
    info2 = StringProperty('')

    def __init__(self, id_item='', info1='', info2='', tabela='', btnbuscar=None, screen_manager=None, **kwargs):
        super(ListaItem, self).__init__(**kwargs)
        self.screen_manager = screen_manager
        self.btnbuscar = btnbuscar
        self.id_item = id_item
        self.info1 = info1
        self.info2 = info2
        self.tabela = tabela

    def deletar(self):
        deletar(self, self.id_item, self.tabela)

    def tela_editar(self):
        editar(self, self.id_item, self.tabela)


class CursoListItem(OneLineListItem):
    info = StringProperty('')

    def __init__(self, id_item='', info='', info2='', btnbuscar=None, **kwargs):
        super(CursoListItem, self).__init__(**kwargs)
        self.btnbuscar = btnbuscar
        self.id_item = id_item
        self.info = info
        self.info2 = info2
        self.text = info


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

    def cadastrar(self, btn_name=None):
        btn_name = btn_name or self.btn_name
        tela = 'cad_' + btn_name

        if btn_name == 'funcionario':
            if self.logado == 'monykpp':
                self.manager.get_screen(tela).tabela = btn_name
                self.manager.current = tela
            else:
                toast('Você não tem acesso ao cadastro de funcionarios')
        else:
            self.manager.get_screen(tela).tabela = btn_name
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

    def principal(self):
        principal(self)


class Consultar(MDScreen):
    tabela = StringProperty('')

    def on_pre_enter(self):
        self.ids.consulta_list.clear_widgets()

    def pesquisar(self, texto):
        try:
            conn = conectar()
            cur = conn.cursor()

            if self.tabela == 'aluno':
                script = 'SELECT id_aluno, nome, cpf FROM aluno WHERE nome ILIKE %s ORDER BY 2'
            elif self.tabela == 'professor':
                script = 'SELECT id_professor, nome, cpf FROM professor WHERE nome ILIKE %s ORDER BY 2'
            elif self.tabela == 'funcionario':
                script = 'SELECT id_funcionario, nome, login FROM funcionario WHERE nome ILIKE %s ORDER BY 2'
            elif self.tabela == 'sala':
                script = 'SELECT id_sala, descricao, capacidade FROM sala WHERE descricao ILIKE %s ORDER BY 2'
            elif self.tabela == 'curso':
                script = 'SELECT id_curso, descricao, CH FROM curso WHERE descricao ILIKE %s ORDER BY 2'
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

                if self.tabela == 'curso':
                    info2 = 'Carga horária: ' + str(info2)

                item = ListaItem(id_item=str(id_it), info1=str(info1), info2=str(info2), tabela=self.tabela,
                                 screen_manager=self.manager, btnbuscar=btnbuscar)

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


# ---------------------  CLASES MDSCREEN - TELAS DE CADASTRO --------------------
class CadastrarAluno(MDScreen):
    tabela = StringProperty('')

    def principal(self):
        principal(self)

    def salvar_dados(self):
        salvar(self, self.tabela)


class CadastrarProfessor(MDScreen):
    tabela = StringProperty('')

    def principal(self):
        principal(self)

    def salvar_dados(self):
        salvar(self, self.tabela)


class CadastrarFuncionario(MDScreen):
    tabela = StringProperty('')

    def principal(self):
        principal(self)

    def salvar_dados(self):
        salvar(self, self.tabela)


class CadastrarSala(MDScreen):
    tabela = StringProperty('')

    def principal(self):
        principal(self)

    def salvar_dados(self):
        salvar(self, self.tabela)


class CadastrarCurso(MDScreen):
    tabela = StringProperty('')

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
        salvar(self, self.tabela)


class CadastrarTurma(MDScreen):

    def principal(self):
        principal(self)

    def salvar_dados(self):
        salvar(self, self.tabela)

    def pes_curso(self, texto):
        try:
            conn = conectar()
            cur = conn.cursor()

            cur.execute('SELECT id_curso, descricao, ch FROM curso WHERE descricao ILIKE %s ORDER BY 2',
                        ('%' + texto + '%',))

            self.ids.curso_list.clear_widgets()

            btncurso = self.ids.btncurso
            consulta = cur.fetchall()

            for row in consulta:
                id_it, info, info2 = row

                item = CursoListItem(id_item=str(id_it), info=str(info), info2=str(info2), btnbuscar=btncurso)

                self.ids.curso_list.add_widget(item)

            conn.close()

        except Exception as e:
            toast(f"Erro: {e}", duration=5)
            print(e)


class CadastrarAlunoTurma(MDScreen):
    pass


class CadastrarPagamento(MDScreen):
    pass


# --------------------------- APP ---------------------------------

class DibTopApp(MDApp):

    def build(self):
        Builder.load_file("screens.kv")

        Window.clearcolor = (1, 1, 1, 1)
        # Window.maximize()
        self.theme_cls.primary_palette = "Green"

        sm = MainScreenManager(transition=NoTransition())
        # sm.current = 'login'

        return sm


# run the app
if __name__ == "__main__":
    DibTopApp().run()
