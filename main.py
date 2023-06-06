from kivy.clock import Clock
from kivy.lang import Builder
from kivy.properties import StringProperty, ObjectProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import ScreenManager, NoTransition
from kivy.uix.textinput import TextInput
from kivymd.uix.screen import MDScreen
from kivy.core.window import Window
from kivymd.app import MDApp
from kivymd.toast import toast
from kivymd.uix.list import TwoLineAvatarIconListItem, OneLineListItem
from funcoes import conectar, validar_login, principal, deletar, salvar, editar, opcoes


# ---------------------   SCREEN MANAGER CLASS  ----------------------------
class MainScreenManager(ScreenManager):
    pass


# ---------------------   ITENS DE LISTAS   ----------------------------

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


# ------------------------------------------------------------- CHAVE ESTRANGEIRA -----------------------------


class CursoListItem(OneLineListItem):
    info = StringProperty('')

    def __init__(self, id_item='', info='', sm=None, **kwargs):
        super(CursoListItem, self).__init__(**kwargs)
        self.manager = sm
        self.id_item = id_item
        self.info = info
        self.frase = str(id_item) + ' - ' + info

        self.click_count = 0
        self.on_release = self.on_click

    def on_click(self):
        self.click_count += 1

        if self.click_count == 1:
            Clock.schedule_once(self.reset_click_count, 0.3)
        elif self.click_count == 2:
            self.on_double_click()
            self.reset_click_count()

    def reset_click_count(self, dt=None):
        self.click_count = 0

    def on_double_click(self):
        self.manager.get_screen('cad_turma').ids.curso.text = self.frase
        print("Item clicado duas vezes:", self.id_item, '-', self.info)


class CursoPopup(Popup):
    def __init__(self, manager=None, **kwargs):
        super(CursoPopup, self).__init__(**kwargs)
        self.manager = manager



class Caixa(TextInput):
    pass


class ConsultarCurso(MDScreen):

    def __init__(self, manager=None, **kwargs):
        super(ConsultarCurso, self).__init__(**kwargs)
        self.manager = manager

    def on_text(self):
        btn = self.ids.btnbuscar  # atualizar consulta
        btn.trigger_action()

    def pesquisar(self, texto):

        script = '''SELECT id_curso, descricao from CURSO WHERE descricao ILIKE %s ORDER BY 2'''

        try:
            conn = conectar()
            cur = conn.cursor()

            cur.execute(script, ('%' + texto + '%',))

            self.ids.curso_list.clear_widgets()

            consulta = cur.fetchall()

            for row in consulta:
                id_item, info = row
                print(self.manager)

                item = CursoListItem(id_item=str(id_item), info=str(info), sm=self.manager)

                self.ids.curso_list.add_widget(item)

            conn.close()

        except Exception as e:
            toast(f"Erro: {e}", duration=5)
            print(e)


class CadastrarTurma(MDScreen):
    frase = StringProperty('')

    def abrir_popup(self):
        m = self.manager

        popup_content = ConsultarCurso(manager=m)  # Passar o gerenciador como argumento
        popup = CursoPopup(content=popup_content, manager=m)
        popup.open()

    def principal(self):
        principal(self)

    def salvar_dados(self):
        salvar(self, self.tabela)


# ---------------------  TELAS GERAIS --------------------

class LoginScreen(MDScreen):
    def get_data(self):
        login = self.ids.idlogin.text
        senha = self.ids.idsenha.text

        if validar_login(login, senha):

            toast("Login e senha válidos", duration=2)

            self.manager.get_screen('principal').logado = login  # enviando o valor de 'logado' para outras telas
            self.manager.get_screen('crud').logado = login

            self.manager.current = 'principal'  # ir para tela principal

        else:
            toast("Login ou senha inválidos", duration=5)

    def mensagem(self):
        toast('Informe o administrador e crie um novo login', duration=7)


class MainScreen(MDScreen):
    logado = StringProperty('')  # recebeu da tela de login

    def crud(self, nome):
        self.manager.get_screen('crud').btn_name = nome  # enviando o nome do botão clicado para a tela de crud
        self.manager.current = 'crud'


class CrudScreen(MDScreen):
    btn_name = StringProperty('')  # recebeu da tela principal
    logado = StringProperty('')  # recebeu da tela de login

    # restringe o cad/consulta de funci ao admin, muda para a tela especifica de acordo com o btn_name
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

    # voltar p tela principal
    def principal(self):
        principal(self)


class Consultar(MDScreen):
    tabela = StringProperty('')  # recebeu da tela 'crud'

    def on_pre_enter(self):  # limpar a lista de consulta
        self.ids.consulta_list.clear_widgets()

    def on_text(self):
        btn = self.ids.btnbuscar  # atualizar consulta
        btn.trigger_action()

    def pesquisar(self, texto):

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

        try:
            conn = conectar()
            cur = conn.cursor()

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
        elif self.tabela == 'curso':
            tela = 'cad_curso'
        else:
            tela = 'principal'

        self.ids.consulta_list.clear_widgets()
        self.manager.current = tela

    def cancelar(self):
        self.ids.consulta_list.clear_widgets()
        self.manager.current = 'principal'


# ---------------------  CLASSES MDSCREEN - TELAS DE CADASTRO  --------------------
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
        op = opcoes()
        return op

    def salvar_dados(self):
        salvar(self, self.tabela)


# --------------------------  FALTA IMPLEMENTAR  -------------------------------

'''class CadastrarTurma(MDScreen):

    def abrir_popup(self):

        popup_content = SearchLayout()
        popup = CursoPopup(content=popup_content)
        popup.open()

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
'''


class CadastrarAlunoTurma(MDScreen):
    pass


class CadastrarPagamento(MDScreen):
    pass


# ---------------------------  APP  ---------------------------------

class DibTopApp(MDApp):

    def build(self):
        # carrega os arquivos kv com a estilização das telas
        Builder.load_file("screens.kv")

        Window.clearcolor = (1, 1, 1, 1)
        # Window.maximize()
        self.theme_cls.primary_palette = "Green"

        sm = MainScreenManager(transition=NoTransition())
        # sm.current = 'login'

        return sm


# run the app
if __name__ == "__main__":
    items = ['Apple', 'Banana', 'Orange', 'Pineapple', 'Grape']
    DibTopApp().run()
