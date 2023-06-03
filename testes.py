from kivymd.app import MDApp
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.recycleview import RecycleView
from kivy.uix.textinput import TextInput
from kivy.uix.recycleboxlayout import RecycleBoxLayout
from kivy.uix.popup import Popup
from kivy.properties import StringProperty
from kivymd.uix.list import TwoLineAvatarIconListItem


class Item(TwoLineAvatarIconListItem):
    text = StringProperty('')
    text2 = StringProperty('cpf')


class SearchBox(TextInput):
    def __init__(self, **kwargs):
        super(SearchBox, self).__init__(**kwargs)
        self.search_results = None

    def set_search_results(self, search_results):
        self.search_results = search_results

    def on_text(self, instance, value):
        if self.search_results is not None:
            filtered_items = filter(lambda item: value.lower() in item.lower(), items)
            self.search_results.data = [{'text': item} for item in filtered_items]


class SearchResults(RecycleView):
    def __init__(self, **kwargs):
        super(SearchResults, self).__init__(**kwargs)
        self.data = []


class SelectableRecycleBoxLayout(RecycleBoxLayout):
    pass


class SearchLayout(BoxLayout):
    def __init__(self, **kwargs):
        super(SearchLayout, self).__init__(**kwargs)
        self.orientation = 'vertical'
        self.search_results = self.create_search_results()
        self.add_widget(self.create_search_box())
        self.add_widget(self.search_results)

    def create_search_box(self):
        search_box = SearchBox()
        search_box.set_search_results(self.search_results)
        return search_box

    def create_search_results(self):
        search_results = SearchResults()
        return search_results


class SearchApp(MDApp):
    def build(self):
        return SearchLayout()

    def on_start(self):
        popup_content = SearchLayout()
        popup = Popup(title='Pesquisa', content=popup_content, size_hint=(0.8, 0.8))
        popup.open()


if __name__ == '__main__':
    items = ['Apple', 'Banana', 'Orange', 'Pineapple', 'Grape']
    SearchApp().run()
