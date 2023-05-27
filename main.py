from kivy.event import EventDispatcher
from kivy.lang import Builder
from kivy.properties import StringProperty
from kivy.uix.button import Button
from kivy.uix.screenmanager import ScreenManager, NoTransition
from kivymd.uix.screen import MDScreen
from kivy.core.window import Window
from kivymd.app import MDApp
import psycopg2
from kivymd.toast import toast
from datetime import datetime
from kivymd.uix.list import TwoLineAvatarIconListItem


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


# ---------------------   CLASES   ----------------------------

class NavigationManager:
    def __init__(self, screen_manager):
        self.screen_manager = screen_manager

    def return_to_principal(self):
        self.screen_manager.current = 'principal'

    def tela_editar(self, classe):

        self.screen_manager.current = 'cad_aluno'
        tela_atual = self.screen_manager.current_screen

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

            nome, cpf, dt_nasc, endereco, email, telefone, naturalidade, nome_mae, estado_civil, escolaridade = consulta

            tela_atual.ids.idaluno.text = id_aluno
            tela_atual.ids.idnome.text = nome
            tela_atual.ids.idcpf.text = cpf
            dt_nasc = conf_data(dt_nasc)
            tela_atual.ids.iddtnasc.text = dt_nasc
            tela_atual.ids.idend.text = endereco
            tela_atual.ids.idemail.text = email
            tela_atual.ids.idtel.text = telefone
            tela_atual.ids.idnat.text = naturalidade
            tela_atual.ids.idnomemae.text = nome_mae
            tela_atual.ids.idestcivil.text = estado_civil
            tela_atual.ids.idesc.text = escolaridade

            conn.commit()  # Confirma a transação
            conn.close()

        except Exception as e:
            toast(f"Error: {e}", duration=5)
            print(e)


class MainScreenManager(ScreenManager):
    pass


class AlunoListItem(TwoLineAvatarIconListItem, EventDispatcher):
    nome = StringProperty('')
    cpf = StringProperty('')

    def __init__(self, id_aluno='', nome='', cpf='', btnbuscar=None, **kwargs):
        super(AlunoListItem, self).__init__(**kwargs)
        self.btnbuscar = btnbuscar
        self.id_aluno = id_aluno
        self.nome = nome
        self.cpf = cpf

    def deletar(self):
        try:
            conn = conectar()
            cur = conn.cursor()

            id_aluno = int(self.id_aluno)

            cur.execute('''DELETE FROM aluno WHERE id_aluno = %s;''', (id_aluno,))
            conn.commit()  # Confirma a transação
            conn.close()

            toast("Registro deletado", duration=5)

            btn = self.btnbuscar
            btn.trigger_action()

        except Exception as e:
            toast(f"Error: {e}", duration=5)
            print(e)


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


# ---------------------  CLASES MDSCREEN --------------------

class MainScreen(MDScreen):
    # Window.size = (700, 550)
    def crud(self, nome):
        self.manager.get_screen('crud').btn_name = nome
        self.manager.current = 'crud'


class LoginScreen(MDScreen):
    def get_data(self):
        login = self.ids.idlogin.text
        senha = self.ids.idsenha.text
        if validar_login(login, senha):
            toast("Login e senha válidos", duration=2)
            self.manager.current = 'principal'
        else:
            toast("Login ou senha inválidos", duration=5)


class CrudScreen(MDScreen):
    btn_name = StringProperty('')

    def cadastrar(self, btn_name=None):
        btn_name = btn_name or self.btn_name

        if btn_name == 'aluno':
            self.manager.current = "cad_aluno"
        elif btn_name == 'turma':
            self.manager.current = ''
        elif btn_name == 'curso':
            self.manager.current = ''
        elif btn_name == 'prof':
            self.manager.current = 'cad_professor'
        elif btn_name == 'func':
            self.manager.current = 'cad_funcionario'
        elif btn_name == 'pag':
            self.manager.current = ''
        else:
            print('deu erro')

    def consultar(self, btn_name=None):
        btn_name = btn_name or self.btn_name

        if btn_name == 'aluno':
            self.manager.current = "con_aluno"
        elif btn_name == 'turma':
            self.manager.current = ''
        elif btn_name == 'curso':
            self.manager.current = ''
        elif btn_name == 'prof':
            self.manager.current = 'con_professor'
        elif btn_name == 'func':
            self.manager.current = 'con_funcionario'
        elif btn_name == 'pag':
            self.manager.current = ''
        else:
            print('deu erro')


class CadastrarAluno(MDScreen):

    def principal(self):
        self.manager.current = 'principal'

    def salvar_dados(self):

        idaluno = self.ids.idaluno.text

        if idaluno == '-':
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

                cur.execute("""INSERT into Aluno 
                (nome,cpf,dt_nasc,endereco,email,telefone,naturalidade,nome_mae,estado_civil,escolaridade) 
                Values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (nome, cpf, dt_nasc, endereco, email, telefone, naturalidade,
                      nome_mae, estado_civil, escolaridade))

                conn.commit()  # Confirma a transação
                toast("Salvo com sucesso!", duration=2)
                self.principal()

            except Exception as e:
                toast(f"Error ao inserir dados do Aluno: {e}", duration=2)
        else:
            try:
                id_aluno = idaluno
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

                conn = conectar()
                cur = conn.cursor()

                cur.execute("""UPDATE Aluno 
                            SET nome = %s,cpf = %s,dt_nasc = %s,endereco = %s,email = %s,telefone = %s,
                            naturalidade = %s,nome_mae = %s,estado_civil = %s,escolaridade = %s
                            WHERE id_aluno = %s""", (nome, cpf, dt_nasc, endereco, email, telefone,
                                                     naturalidade, nome_mae, estado_civil, escolaridade, id_aluno))

                conn.commit()  # Confirma a transação
                toast("Salvo com sucesso!", duration=2)
                self.principal()

            except Exception as e:
                toast(f"Error ao inserir dados do Aluno: {e}", duration=2)
                return False


class ConsultarAluno(MDScreen):

    def pesquisar(self, texto):
        try:
            conn = conectar()
            cur = conn.cursor()

            cur.execute('''SELECT aluno.id_aluno, aluno.nome, aluno.cpf 
                           FROM aluno
                           WHERE aluno.nome LIKE %s
                           ORDER BY 2''', ('%' + texto + '%',))

            # Limpar a lista de alunos
            self.ids.aluno_list.clear_widgets()

            btnbuscar = self.ids.btnbuscar
            consulta = cur.fetchall()

            # Iterar sobre os resultados da consulta
            for row in consulta:
                id_aluno, nome, cpf = row
                # Criar um novo item de aluno
                aluno_item = AlunoListItem(id_aluno=str(id_aluno), nome=nome, cpf=cpf, btnbuscar=btnbuscar)
                # Adicionar o item à lista
                self.ids.aluno_list.add_widget(aluno_item)

            # Fechar a conexão com o banco de dados
            conn.close()

        except Exception as e:
            toast(f"Error: {e}", duration=5)
            print(e)


class CadastrarProfessor(MDScreen):
    def salvar_dados(self):
        print('salvou')


class ConsultarProfessor(MDScreen):
    pass


class CadastrarFuncionario(MDScreen):
    def salvar_dados(self):
        print('salvou')


class ConsultarFuncionario(MDScreen):
    pass


# --------------------------- APP ---------------------------------

class DibTopApp(MDApp):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.navigation = None

    def build(self):
        Builder.load_file("screens/screenmanager.kv")
        Builder.load_file("screens/loginscreen.kv")
        Builder.load_file("screens/mainscreen.kv")
        Builder.load_file("screens/crud.kv")
        Builder.load_file("screens/cadastrar_aluno.kv")
        Builder.load_file("screens/consultar_aluno.kv")
        Builder.load_file("screens/cadastrar_professor.kv")
        Builder.load_file("screens/consultar_professor.kv")
        Builder.load_file("screens/cadastrar_funcionario.kv")
        Builder.load_file("screens/consultar_funcionario.kv")

        Window.clearcolor = (1, 1, 1, 1)
        Window.maximize()
        self.theme_cls.primary_palette = "Green"

        sm = MainScreenManager(transition=NoTransition())
        # sm.current = 'login'

        self.navigation = NavigationManager(sm)  # Passando a instância de MainScreenManager para NavigationManager
        return sm


# run the app
if __name__ == "__main__":
    DibTopApp().run()
