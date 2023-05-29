from kivy.event import EventDispatcher
from kivy.lang import Builder
from kivy.properties import StringProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import ScreenManager, NoTransition
from kivy.uix.textinput import TextInput
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
            elif tabela == 'prof':
                script = 'DELETE FROM professor WHERE id_professor = %s;'
            elif tabela == 'func':
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


# ---------------------   CLASES   ----------------------------

class NavigationManager:
    def __init__(self, screen_manager):
        self.screen_manager = screen_manager

    def return_to_principal(self):
        self.screen_manager.current = 'principal'

    def tela_editar(self, instancia):

        if isinstance(instancia, AlunoListItem):

            self.screen_manager.current = 'cad_aluno'
            tela_atual = self.screen_manager.current_screen

            try:
                conn = conectar()
                cur = conn.cursor()

                id_aluno = instancia.id_aluno

                cur.execute('''SELECT aluno.nome, aluno.cpf, aluno.dt_nasc, aluno.endereco, aluno.email, aluno.telefone, 
                                aluno.naturalidade, aluno.nome_mae, aluno.estado_civil, aluno.escolaridade
                               FROM aluno
                               WHERE aluno.id_aluno = %s
                               ''', (id_aluno,))

                consulta = cur.fetchone()

                nome, cpf, dt_nasc, endereco, email, telefone, naturalidade, nome_mae, estado_civil, \
                    escolaridade = consulta

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

                conn.commit()
                conn.close()

            except Exception as e:
                toast(f"Error: {e}", duration=5)
                print(e)

        if isinstance(instancia, ProfListItem):

            self.screen_manager.current = 'cad_professor'
            tela_atual = self.screen_manager.current_screen

            try:
                conn = conectar()
                cur = conn.cursor()

                id_prof = instancia.id_professor

                cur.execute('''SELECT professor.nome, professor.cpf, professor.area_ensino, 
                                professor.endereco, professor.email, professor.telefone
                               FROM professor
                               WHERE professor.id_professor = %s
                               ''', (id_prof,))

                consulta = cur.fetchone()

                nome, cpf, area_ensino, endereco, email, telefone = consulta

                tela_atual.ids.idprof.text = id_prof
                tela_atual.ids.nome.text = nome
                tela_atual.ids.cpf.text = cpf
                tela_atual.ids.ae.text = cpf
                tela_atual.ids.end.text = endereco
                tela_atual.ids.email.text = email
                tela_atual.ids.tel.text = telefone

                conn.commit()
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
        deletar(self, self.id_aluno, 'aluno')


class ProfListItem(TwoLineAvatarIconListItem, EventDispatcher):
    nome = StringProperty('')
    cpf = StringProperty('')

    def __init__(self, id_professor='', nome='', cpf='', btnbuscar=None, **kwargs):
        super(ProfListItem, self).__init__(**kwargs)
        self.btnbuscar = btnbuscar
        self.id_professor = id_professor
        self.nome = nome
        self.cpf = cpf

    def deletar(self):
        deletar(self, self.id_professor, 'prof')


class FuncListItem(TwoLineAvatarIconListItem, EventDispatcher):
    nome = StringProperty('')

    def __init__(self, id_func='', nome='', login='', btnbuscar=None, **kwargs):
        super(FuncListItem, self).__init__(**kwargs)
        self.btnbuscar = btnbuscar
        self.id_func = id_func
        self.nome = nome
        self.login = login

    def deletar(self):
        deletar(self, self.id_func, 'func')


class SalaListItem(TwoLineAvatarIconListItem, EventDispatcher):
    descricao = StringProperty('')

    def __init__(self, id_sala='', descricao='', capacidade='', btnbuscar=None, **kwargs):
        super(SalaListItem, self).__init__(**kwargs)
        self.btnbuscar = btnbuscar
        self.id_sala = id_sala
        self.descricao = descricao
        self.capacidade = 'capacidade:' + capacidade

    def deletar(self):
        deletar(self, self.id_sala, 'sala')


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

        if btn_name == 'aluno':
            self.manager.current = "cad_aluno"
        elif btn_name == 'turma':
            self.manager.current = 'cad_turma'
        elif btn_name == 'curso':
            self.manager.current = 'cad_curso'
        elif btn_name == 'prof':
            self.manager.current = 'cad_professor'

        elif btn_name == 'func':
            if self.logado == 'monykpp':
                self.manager.current = 'cad_funcionario'
            else:
                toast('Você não tem acesso ao cadastro de funcionarios')

        elif btn_name == 'pag':
            self.manager.current = 'cad_pag'
        elif btn_name == 'at':
            self.manager.current = 'cad_alunoturma'
        elif btn_name == 'sala':
            self.manager.current = 'cad_sala'
        else:
            print('deu erro')

    def consultar(self, btn_name=None):
        btn_name = btn_name or self.btn_name

        if btn_name == 'aluno':
            self.manager.current = "con_aluno"
        elif btn_name == 'turma':
            self.manager.current = 'con_turma'
        elif btn_name == 'curso':
            self.manager.current = 'con_curso'
        elif btn_name == 'prof':
            self.manager.current = 'con_professor'

        elif btn_name == 'func':
            if self.logado == 'monykpp':
                self.manager.current = 'con_funcionario'
            else:
                toast('Você não tem acesso ao cadastro de funcionarios')

        elif btn_name == 'pag':
            self.manager.current = 'con_pag'
        elif btn_name == 'at':
            self.manager.current = 'con_alunoturma'
        elif btn_name == 'sala':
            self.manager.current = 'con_sala'
        else:
            print('deu erro')


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


class ConsultarAluno(MDScreen):

    def pesquisar(self, texto):
        try:
            conn = conectar()
            cur = conn.cursor()

            cur.execute('''SELECT aluno.id_aluno, aluno.nome, aluno.cpf FROM aluno 
            WHERE aluno.nome LIKE %s ORDER BY 2''', ('%' + texto + '%',))

            self.ids.aluno_list.clear_widgets()

            btnbuscar = self.ids.btnbuscar
            consulta = cur.fetchall()

            for row in consulta:
                id_aluno, nome, cpf = row
                aluno_item = AlunoListItem(id_aluno=str(id_aluno), nome=nome, cpf=cpf, btnbuscar=btnbuscar)
                self.ids.aluno_list.add_widget(aluno_item)

            conn.close()

        except Exception as e:
            toast(f"Erro: {e}", duration=5)
            print(e)

    def novo(self):
        self.manager.current = 'cad_aluno'


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


class ConsultarProfessor(MDScreen):
    def pesquisar(self, texto):
        try:
            conn = conectar()
            cur = conn.cursor()

            cur.execute('''SELECT professor.id_professor, professor.nome, professor.cpf FROM professor 
            WHERE professor.nome LIKE %s ORDER BY 2''', ('%' + texto + '%',))

            self.ids.prof_list.clear_widgets()

            btnbuscar = self.ids.btnbuscar
            consulta = cur.fetchall()

            for row in consulta:
                id_professor, nome, cpf = row
                prof_item = ProfListItem(id_professor=str(id_professor), nome=nome, cpf=cpf, btnbuscar=btnbuscar)
                self.ids.prof_list.add_widget(prof_item)

            conn.close()

        except Exception as e:
            toast(f"Erro: {e}", duration=5)
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

                cur.execute("""INSERT into Funcionario (nome, login, senha)Values (%s, %s, %s)
                """, (nome, login, senha))

                conn.commit()

                toast("Salvo com sucesso!", duration=2)
                self.principal()

            else:
                toast('senhas não coincidem', duration=4)

        except Exception as e:
            toast(f"Erro ao salvar dados: {e}", duration=5)
            print(e)


class ConsultarFuncionario(MDScreen):

    def pesquisar(self, texto):
        try:
            conn = conectar()
            cur = conn.cursor()

            cur.execute('''SELECT funcionario.id_funcionario, funcionario.nome,funcionario.login FROM funcionario
                           WHERE fucnionario.nome LIKE %s ORDER BY 2''', ('%' + texto + '%',))

            self.ids.func_list.clear_widgets()

            btnbuscar = self.ids.btnbuscar
            consulta = cur.fetchall()

            for row in consulta:
                id_func, nome, login = row
                func_item = FuncListItem(id_func=str(id_func), nome=nome, login=login, btnbuscar=btnbuscar)
                self.ids.func_list.add_widget(func_item)

            conn.close()

        except Exception as e:
            toast(f"Erro: {e}", duration=5)
            print(e)

    def novo(self):
        self.manager.current = 'cad_aluno'


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


class ConsultarSala(MDScreen):

    def pesquisar(self, texto):
        try:
            conn = conectar()
            cur = conn.cursor()

            cur.execute('''SELECT sala.id_sala,sala.descricao, sala.capacidade FROM sala
                           WHERE sala.descriçao LIKE %s ORDER BY 2''', ('%' + texto + '%',))

            self.ids.sala_list.clear_widgets()

            btnbuscar = self.ids.btnbuscar
            consulta = cur.fetchall()

            for row in consulta:
                id_sala, desc, cap = row
                sala_item = SalaListItem(id_sala=str(id_sala), descricao=desc, capacidade=cap, btnbuscar=btnbuscar)
                self.ids.sala_list.add_widget(sala_item)

            conn.close()

        except Exception as e:
            toast(f"Erro: {e}", duration=5)
            print(e)

    def novo(self):
        self.manager.current = 'cad_sala'


class CadastrarTurma(MDScreen):
    pass


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


class CadastrarCurso(MDScreen):
    pass


class ConsultarCurso(MDScreen):
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
        # sm.current = 'login'

        self.navigation = NavigationManager(sm)  # Passando a instância de MainScreenManager para NavigationManager
        return sm


# run the app
if __name__ == "__main__":
    DibTopApp().run()
