import psycopg2
from kivy.core.window import Window
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivymd.toast import toast
from kivymd.uix.label import MDLabel
from kivymd.uix.textfield import MDTextField


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
