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

    def on_enter(self):
        Window.bind(on_key_down=self.on_key_down)

    def on_key_down(self, instance, key, *args):
        if key == 9:  # Código para a tecla "Tab" é 9
            focus_next = False
            for child in self.ids.keys():
                if focus_next:
                    self.ids[child].focus = True
                    break
                if child == self.focus:
                    focus_next = True

    def on_textfield_validate(self, next_widget):
        next_widget.focus = True

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
