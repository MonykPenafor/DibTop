from datetime import date
from kivy.clock import Clock
from kivy.lang import Builder
from kivy.properties import StringProperty
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import ScreenManager, NoTransition
from kivymd.uix.screen import MDScreen
from kivy.core.window import Window
from kivymd.app import MDApp
from kivymd.toast import toast
from kivymd.uix.list import TwoLineAvatarIconListItem, OneLineListItem
from funcoes import conectar, validar_login, principal, deletar, salvar, editar, opcoes, pegar_id


# ---------------------   SCREEN MANAGER CLASS  ----------------------------
class MainScreenManager(ScreenManager):
    pass


# ---------------------   ITENS DE LISTAS   ----------------------------

class ListaItem(TwoLineAvatarIconListItem):
    info1 = StringProperty('')
    info2 = StringProperty('')

    def __init__(self, id_item='', info1='', info2='',tabela='',logado='',btnbuscar=None,screen_manager=None,**kwargs):
        super(ListaItem, self).__init__(**kwargs)
        self.screen_manager = screen_manager
        self.btnbuscar = btnbuscar
        self.id_item = id_item
        self.logado = logado
        self.info1 = info1
        self.info2 = info2
        self.tabela = tabela

    def deletar(self):
        deletar(self, self.id_item, self.tabela, self.logado)

    def tela_editar(self):
        if self.btnbuscar != 'pagamento':
            editar(self, self.id_item, self.tabela)
        else:
            toast('Náo é permitido editar uma registro de pagamento')


class ChaveListItem(OneLineListItem):
    info = StringProperty('')

    def __init__(self, id_item='', info='', info2='', sm=None, tabela='', **kwargs):
        super(ChaveListItem, self).__init__(**kwargs)
        self.manager = sm
        self.id_item = id_item
        self.tabela = tabela
        self.info = info
        self.info2 = info2
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
        print(self.tabela + 'tablea double click')
        if self.tabela == 'curso':
            self.manager.get_screen('cad_turma').ids.curso.text = self.frase
        if self.tabela == 'prof':
            self.manager.get_screen('cad_turma').ids.prof.text = self.frase
        if self.tabela == 'aluno':
            self.manager.get_screen('cad_alunoturma').ids.aluno.text = self.frase
        if self.tabela == 'turma':
            self.manager.get_screen('cad_alunoturma').ids.turma.text = self.frase
        if self.tabela == 'aluno_turma':
            self.manager.get_screen('cad_pagamento').ids.alunoturma.text = self.frase


# ---------------------  TELAS GERAIS --------------------

class LoginScreen(MDScreen):
    def get_data(self):
        login = self.ids.idlogin.text
        senha = self.ids.idsenha.text

        if validar_login(login, senha):

            toast("Login e senha válidos", duration=2)

            self.manager.get_screen('principal').logado = login  # enviando o valor de 'logado' para outras telas
            self.manager.get_screen('crud').logado = login
            self.manager.get_screen('cad_pagamento').logado = login
            self.manager.get_screen('consultar').logado = login

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
                toast('Você não tem acesso ao cadastro de funcionarios', duration=4)

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
                toast('Você não tem acesso ao quadro de funcionarios', duration=4)
        else:
            self.manager.get_screen('consultar').tabela = btn_name
            self.manager.current = 'consultar'

    # voltar p tela principal
    def principal(self):
        principal(self)


class Consultar(MDScreen):
    tabela = StringProperty('')  # recebeu da tela 'crud'
    logado = StringProperty('')

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
        elif self.tabela == 'turma':
            script = '''SELECT id_turma, curso.descricao, professor.nome FROM turma, professor, curso WHERE 
            turma.id_professor = professor.id_professor and turma.id_curso = curso.id_curso and curso.descricao ILIKE 
            %s ORDER BY 2'''
        elif self.tabela == 'alunoturma':
            script = '''SELECT aluno_turma.id_aluno_turma, professor.nome, aluno.nome, aluno_turma.matricula, 
            curso.descricao FROM turma, aluno, aluno_turma, professor, curso WHERE turma.id_turma = aluno_turma.id_turma 
            and curso.id_curso = turma.id_curso and aluno.id_aluno = aluno_turma.id_aluno and professor.id_professor 
            = turma.id_professor and aluno.nome ILIKE %s ORDER BY 2'''
        elif self.tabela == 'pagamento':
            script = '''SELECT pagamento.id_pagamento, aluno.nome, aluno_turma.matricula, pagamento.vlr_pagamento FROM 
            aluno, aluno_turma, pagamento WHERE aluno_turma.id_aluno_turma = pagamento.id_aluno_turma and aluno.id_aluno 
            = aluno_turma.id_aluno and aluno.nome ILIKE %s ORDER BY 2'''
        else:
            script = 'tabela invalida'
            print(script)

        try:
            conn = conectar()
            cur = conn.cursor()

            cur.execute(script, ('%' + texto + '%',))

            self.ids.consulta_list.clear_widgets()

            btnbuscar = self.ids.btnbuscar
            consulta = cur.fetchall()

            if self.tabela == 'alunoturma':

                for row in consulta:
                    id_it, info1, info2, info3, info4 = row

                    infoprincipal = info2 + ' - ' + str(info3)
                    infosecundaria = info1 + ' - ' + info4

                    item = ListaItem(id_item=str(id_it), info1=str(infoprincipal), info2=str(infosecundaria),
                                     tabela=self.tabela,
                                     screen_manager=self.manager, btnbuscar=btnbuscar)

                    self.ids.consulta_list.add_widget(item)

            elif self.tabela == 'pagamento':

                for row in consulta:
                    id_it, info1, info2, info3 = row

                    infoprincipal = info1 + ' - ' + str(info2)

                    item = ListaItem(id_item=str(id_it), info1=str(infoprincipal), info2=str(info3), tabela=self.tabela,
                                     screen_manager=self.manager, logado=self.logado, btnbuscar=btnbuscar)

                    self.ids.consulta_list.add_widget(item)

            else:
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
            if self.logado == 'monykpp':
                tela = 'cad_funcionario'
            else:
                toast('Você não tem acesso ao cadastro de funcionarios', duration=4)
                tela = 'consultar'
        elif self.tabela == 'sala':
            tela = 'cad_sala'
        elif self.tabela == 'curso':
            tela = 'cad_curso'
        elif self.tabela == 'turma':
            tela = 'cad_turma'
        elif self.tabela == 'alunoturma':
            tela = 'cad_aluno_turma'
        elif self.tabela == 'pagamento':
            tela = 'cad_pagamento'
        else:
            tela = 'principal'
            toast('')

        self.ids.consulta_list.clear_widgets()
        self.manager.current = tela

    def cancelar(self):
        self.ids.consulta_list.clear_widgets()
        self.manager.current = 'principal'


class ConsultarChaveEstrangeira(MDScreen):

    def __init__(self, manager=None, tabela='', **kwargs):
        super(ConsultarChaveEstrangeira, self).__init__(**kwargs)
        self.tabela = tabela
        self.manager = manager

    def on_text(self):
        btn = self.ids.btnbuscar  # atualizar consulta
        btn.trigger_action()

    def pesquisar(self, texto):

        print(self.tabela)

        if self.tabela == 'curso':
            script = '''SELECT id_curso, descricao from CURSO WHERE descricao ILIKE %s ORDER BY 2'''
        elif self.tabela == 'prof':
            script = '''SELECT id_professor, nome FROM professor WHERE nome ILIKE %s ORDER BY 2'''
        elif self.tabela == 'aluno':
            script = '''SELECT id_aluno, nome FROM aluno WHERE nome ILIKE %s ORDER BY 2'''
        elif self.tabela == 'turma':
            script = '''SELECT turma.id_turma, curso.descricao FROM turma, curso WHERE turma.id_curso = curso.id_curso 
                            and curso.descricao ILIKE %s ORDER BY 2'''
        elif self.tabela == 'aluno_turma':
            script = '''SELECT aluno_turma.id_aluno_turma, aluno_turma.matricula, aluno.nome, curso.descricao FROM 
            aluno_turma, turma, curso, aluno WHERE turma.id_curso = curso.id_curso and aluno_turma.id_aluno = 
            aluno.id_aluno and turma.id_turma = aluno_turma.id_turma and aluno.nome ILIKE %s ORDER BY 2'''
        else:
            script = 'deu erro'

        try:
            conn = conectar()
            cur = conn.cursor()

            cur.execute(script, ('%' + texto + '%',))

            self.ids.chaves_list.clear_widgets()

            consulta = cur.fetchall()

            if self.tabela != 'aluno_turma':
                for row in consulta:
                    id_item, info = row

                    item = ChaveListItem(id_item=str(id_item), info=str(info), sm=self.manager, tabela=self.tabela)

                    self.ids.chaves_list.add_widget(item)
            else:
                for row in consulta:
                    id_item, info1, info2, info3 = row

                    info = str(info1) + ' - ' + info2 + ' | ' + info3

                    item = ChaveListItem(id_item=str(id_item), info=str(info), sm=self.manager, tabela=self.tabela)

                    self.ids.chaves_list.add_widget(item)
            conn.close()

        except Exception as e:
            toast(f"Erro: {e}", duration=5)
            print(e)


class CursoPopup(Popup):
    def __init__(self, manager=None, **kwargs):
        super(CursoPopup, self).__init__(**kwargs)
        self.manager = manager


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


class CadastrarTurma(MDScreen):
    tabela = StringProperty('')

    def abrir_popup(self, tabela):
        popup_content = ConsultarChaveEstrangeira(manager=self.manager, tabela=tabela)
        popup = CursoPopup(content=popup_content, manager=self.manager)
        popup.open()

    def principal(self):
        principal(self)

    def salvar_dados(self):
        salvar(self, self.tabela)


class CadastrarAlunoTurma(MDScreen):
    tabela = StringProperty('')

    def abrir_popup(self, tabela):
        popup_content = ConsultarChaveEstrangeira(manager=self.manager, tabela=tabela)
        popup = CursoPopup(content=popup_content, manager=self.manager)
        popup.open()

    def principal(self):
        principal(self)

    def salvar_dados(self):
        salvar(self, self.tabela)

    def gerar_matricula(self):
        ano = date.today().strftime("%Y")
        aluno_id = pegar_id(self.ids.aluno.text)
        turma_id = pegar_id(self.ids.turma.text)
        mat = str(ano) + str(aluno_id) + str(turma_id)
        self.ids.matricula.text = mat


class CadastrarPagamento(MDScreen):
    tabela = StringProperty('')
    logado = StringProperty('')

    def abrir_popup(self, tabela):
        popup_content = ConsultarChaveEstrangeira(manager=self.manager, tabela=tabela)
        popup = CursoPopup(content=popup_content, manager=self.manager)
        popup.open()

    def principal(self):
        principal(self)

    def salvar_dados(self):
        salvar(self, self.tabela)


# ---------------------------  APP  ---------------------------------

class DibTopApp(MDApp):

    def build(self):
        # carrega os arquivos kv com a estilização das telas
        Builder.load_file("screens.kv")

        Window.clearcolor = (1, 1, 1, 1)
        Window.maximize()
        self.theme_cls.primary_palette = "Green"

        sm = MainScreenManager(transition=NoTransition())
        sm.current = 'login'

        return sm


# run the app
if __name__ == "__main__":
    DibTopApp().run()
