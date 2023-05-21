from kivy.app import App
from kivy.event import EventDispatcher
from kivy.lang import Builder
from kivy.properties import StringProperty, ObjectProperty
from kivymd.uix.screenmanager import ScreenManager
from kivymd.uix.screen import MDScreen
from kivy.core.window import Window
from kivymd.app import MDApp
import psycopg2
from kivymd.toast import toast
from datetime import datetime
from kivymd.uix.list import TwoLineAvatarIconListItem
from kivy.core.window import Keyboard

Builder.load_file("screens/screenmanager.kv")
Builder.load_file("screens/loginscreen.kv")
Builder.load_file("screens/mainscreen.kv")
Builder.load_file("screens/crud.kv")
Builder.load_file("screens/cadastrar_aluno.kv")
Builder.load_file("screens/consultar_aluno.kv")


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


class MainScreenManager(ScreenManager):
    pass


class MainScreen(MDScreen):
    # Window.size = (700, 550)

    def crud(self):
        self.manager.current = 'crud'


class LoginScreen(MDScreen):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.keyboard = None
        self.focusable_widgets = None

    def on_pre_enter(self):
        self.focusable_widgets = [
            self.ids.idlogin,
            self.ids.idsenha,
            self.ids.btn_esqueci,
            self.ids.btn_entrar
        ]
        self.keyboard = Window
        self.keyboard.bind(on_key_down=self.on_key_down)

    def on_key_down(self, keyboard, keycode, text, modifiers, *args):
        if keycode == 9:  # 9 é o código da tecla Tab
            self.focus_next()

    def focus_next(self):
        current_index = -1
        for i, widget in enumerate(self.focusable_widgets):
            if widget.focus:
                current_index = i
                widget.focus = False
                break

        next_index = (current_index + 1) % len(self.focusable_widgets)
        self.focusable_widgets[next_index].focus = True

    def get_data(self):
        login = self.ids.idlogin.text
        senha = self.ids.idsenha.text
        if validar_login(login, senha):
            toast("Login e senha válidos", duration=2)
            self.manager.current = 'principal'
            # toast('Bem vindo', duration=3)
        else:
            toast("Login ou senha inválidos", duration=5)


class CrudScreen(MDScreen):
    def cadastrar(self):
        self.manager.current = "cad_aluno"

    def consultar(self):
        self.manager.current = "con_aluno"


class CadastrarAluno(MDScreen):

    def guardar_dados(self):
        try:
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
            print(nome, cpf, dt_nasc, endereco, email, telefone, naturalidade,
                  nome_mae, estado_civil, escolaridade)

            cur.execute("""INSERT into Aluno 
            (nome,cpf,dt_nasc,endereco,email,telefone,
            naturalidade,nome_mae,estado_civil,escolaridade) 
            Values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (nome, cpf, dt_nasc, endereco, email, telefone, naturalidade,
                  nome_mae, estado_civil, escolaridade))

            conn.commit()  # Confirma a transação
            toast("Salvo com sucesso!", duration=2)
            self.principal()

        except Exception as e:
            toast(f"Error ao inserir dados do Aluno: {e}", duration=2)
            return False


class NavigationManager:
    def __init__(self, screen_manager):
        self.screen_manager = screen_manager

    def return_to_principal(self):
        self.screen_manager.current = 'principal'

    def tela_editar(self, classe):
        self.screen_manager.current = 'cad_aluno'

        try:
            conn = conectar()
            cur = conn.cursor()

            id_aluno = classe.id_aluno

            cur.execute('''SELECT aluno.nome, aluno.cpf, aluno.dt_nasc, aluno.endereco, aluno.email, aluno.telefone, 
                            aluno.naturalidade, aluno.nome_mae, aluno.estado_civil, aluno.escolaridade
                           FROM aluno
                           WHERE aluno.id_aluno = %s
                           ''', (id_aluno,))

            consulta = cur.fetchone()

            print(consulta)

            nome, cpf, dt_nasc, endereco, email, telefone, naturalidade, nome_mae, estado_civil, escolaridade = consulta
            print(nome)
            print(dt_nasc)

            '''self.ids.idnome.text = nome
            self.ids.idcpf.text = cpf
            self.ids.iddtnasc.text = dt_nasc
            self.ids.idend.text = endereco
            self.ids.idemail.text = email
            self.ids.idtel.text = telefone
            self.ids.idnat.text = naturalidade
            self.ids.idnomemae.text = nome_mae
            self.ids.idestcivil.text = estado_civil
            self.ids.idesc.text = escolaridade'''

            conn.close()

        except Exception as e:
            toast(f"Error: {e}", duration=5)
            print(e)


class AlunoListItem(TwoLineAvatarIconListItem, EventDispatcher):
    nome = StringProperty('')
    cpf = StringProperty('')

    def __init__(self, id_aluno='', nome='', cpf='', **kwargs):
        super(AlunoListItem, self).__init__(**kwargs)
        self.id_aluno = id_aluno
        self.nome = nome
        self.cpf = cpf


class ConsultarAluno(MDScreen):

    def pesquisar(self, texto):
        try:
            conn = conectar()
            cur = conn.cursor()
            print(texto)
            cur.execute('''SELECT aluno.id_aluno, aluno.nome, aluno.cpf 
                           FROM aluno
                           WHERE aluno.nome LIKE %s
                           ORDER BY 2''', ('%' + texto + '%',))

            # Limpar a lista de alunos
            self.ids.aluno_list.clear_widgets()

            consulta = cur.fetchall()
            print(consulta)
            # Iterar sobre os resultados da consulta
            for row in consulta:
                id_aluno, nome, cpf = row
                print('Nome:', nome, 'CPF:', cpf)

                # Criar um novo item de aluno
                aluno_item = AlunoListItem(id_aluno=str(id_aluno), nome=nome, cpf=cpf)
                # Adicionar o item à lista
                self.ids.aluno_list.add_widget(aluno_item)

            # Fechar a conexão com o banco de dados
            conn.close()

        except Exception as e:
            toast(f"Error: {e}", duration=5)
            print(e)


class DibTopApp(MDApp):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.navigation = None

    def build(self):
        # Window.maximize()
        self.theme_cls.primary_palette = "Green"

        sm = MainScreenManager()
        sm.current = 'login'

        self.navigation = NavigationManager(sm)  # Passando a instância de MainScreenManager para NavigationManager
        return sm


# run the app
if __name__ == "__main__":
    DibTopApp().run()
