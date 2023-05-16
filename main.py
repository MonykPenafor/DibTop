import os
from kivy.factory import Factory
from kivymd.uix.screenmanager import ScreenManager
from kivymd.uix.screen import MDScreen
from kivy.core.window import Window
from kivymd.app import MDApp
from kaki.app import App
import psycopg2
from kivymd.toast import toast
from datetime import datetime
from kivy.uix.label import Label
from kivymd.uix.list import TwoLineAvatarIconListItem
from kivy.uix.image import Image
from kivy.uix.behaviors import ButtonBehavior
from kivy.lang import Builder
from kivy.uix.floatlayout import FloatLayout
from kivymd.uix.toolbar import MDToolbar
from kivymd.uix.toolbar import MDTopAppBar
from kivymd.uix.toolbar import toolbar


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
        nome = self.ids.alunobtn.text
        toast(nome, duration=2)
        self.manager.current = 'crud'


class LoginScreen(MDScreen):

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
        self.manager.current = 'cad_aluno'

    def consultar(self):
        self.manager.current = "con_aluno"

    # botão cancelar
    def principal(self):
        self.manager.current = 'principal'


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
            toast("Salvo com sucesso", duration=2)

        except Exception as e:
            toast(f"Error ao inserir dados do Aluno: {e}", duration=2)
            # print(f"Error ao inserir dados do Aluno: {e}")
            return False

    def principal(self):
        self.manager.current = 'principal'


class ConsultarAluno(MDScreen):
    def principal(self):
        self.manager.current = 'principal'

    def pesquisar(texto):
        try:
            conn = conectar()
            cur = conn.cursor()
            print(texto)

            cur.execute('''select aluno.nome, aluno.cpf from aluno where aluno.nome LIKE %s''', ('%' + texto + '%'))

        except Exception as e:
            toast(f"Error: {e}", duration=5)
            print(e)


class DibTopApp(MDApp, App):
    DEBUG = 1  # set this to 0 make live app not working

    # *.kv files to watch
    KV_FILES = {
        os.path.join(os.getcwd(), "screens/screenmanager.kv"),
        os.path.join(os.getcwd(), "screens/mainscreen.kv"),
        os.path.join(os.getcwd(), "screens/loginscreen.kv"),
        os.path.join(os.getcwd(), "screens/crud.kv"),
        os.path.join(os.getcwd(), "screens/cadastrar_aluno.kv"),
        os.path.join(os.getcwd(), "screens/consultar_aluno.kv"),

    }

    # auto reload path
    AUTORELOADER_PATHS = [
        (".", {"recursive": True}),
    ]

    def build_app(self, **kwargs):
        Window.maximize()
        self.theme_cls.primary_palette = "Green"
        return Factory.MainScreenManager()


# run the app
if __name__ == "__main__":
    DibTopApp().run()
