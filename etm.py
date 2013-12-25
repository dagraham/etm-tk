# -*- coding: utf-8 -*-
import sys
import etmKv.etmData as etmData
from etmKv.etmData import get_current_time, leadingzero


from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.codeinput import CodeInput
from pygments.lexers.special import TextLexer

from kivy.uix.label import Label
from kivy.uix.modalview import ModalView
from kivy.properties import ObjectProperty
from kivy.config import Config
from kivy.clock import Clock
Config.set('graphics', 'height', '440')
Config.set('graphics', 'width', '530')


from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.codeinput import CodeInput
from kivy.uix.modalview import ModalView


class ETMDialog():

    def __init__(self, parent=None, prompt="etm", validator=lambda x: True):
        self.parent = parent
        self.prompt = prompt
        self.validator = validator
        self.text = ''

        self.content = BoxLayout(orientation='vertical')
        self.content.add_widget(Label(text=self.prompt))
        self.input = CodeInput(multiline=False, size_hint=(1, None), height=30, lexer=TextLexer())
        self.input.bind(on_text_validate=self.validate)
        # self.input.bind(on_dismiss=self.dismiss)
        self.content.add_widget(self.input)

    def run(self):
        self.popup = ModalView(size_hint=(None, None), size=(400, 200))
        self.popup.add_widget(self.content)
        # self.parent.input_wid.focus = False
        self.input.focus = True
        self.popup.open()

    def validate(self, value):
        print('validate', value, self.input.text)
        if self.validator(self.input.text):
            self.parent.output_wid.text = self.input.text
            self.input.focus = False
            self.popup.dismiss()
            self.parent.input_wid.focus = True


class ETMTextInput(TextInput):

    history = []
    index = 0
    now = None
    options = {}
    popup = ''
    value = ''

    def _keyboard_on_key_down(self, window, keycode, text, modifiers):
        # print(keycode)
        if keycode[0] == 273:  # 273 is the keycode for up
            self.previous_history()
        elif keycode[0] == 274:  # 274 is the keycode for down
            self.next_history()
        elif keycode[0] == 13:  # 13 is the keycode for enter
            self.process_input()
        elif keycode[0] == 27:  # escape
            self.select_all()
            self.delete_selection()
            # return True to avoid closing app
            return(True)
        else:
            super(ETMTextInput, self)._keyboard_on_key_down(
                window, keycode, text, modifiers)

    def init(self):
        self.Dialog = ETMDialog(parent=self, prompt="etm text")
        self.loop = loop
        res = self.loop.do_command('s')
        self.options = self.loop.options
        self.start_timer()
        return(res)

    def start_timer(self):
        self.now = get_current_time()
        nxt = (60 - self.now.second)
        print(self.now)
        Clock.schedule_once(self.timer_callback, nxt)

    def timer_callback(self, dt):
        self.start_timer()

    def process_input(self):
        """
        Append input to history, process it and show the result in output.
        """
        cmd = self.text.strip()

        if cmd:
            if cmd == 'q':
                sys.exit()
            elif cmd not in self.history:
                self.history.append(cmd)
                self.index = len(self.history) - 1
            self.select_all()
            try:
                res = loop.do_command(cmd)
            except:
                self.Dialog.run()
                res = self.Dialog.text
                print('res', res)
                self.output_wid.text = self.text
                self.output_wid.scroll_y = 1
                self.output_wid.readonly = False
                self.output_wid.cursor = (0, 0)

            if not res:
                return(True)
            self.output_wid.text = res
            self.output_wid.scroll_y = 1

    def previous_history(self):
        """
        Replace input with the previous history item.
        """
        if self.index >= 1:
            self.index -= 1
            self.text = self.history[self.index]

    def next_history(self):
        """
        Replace input with the next history item.
        """
        if self.index + 1 < len(self.history):
            self.index += 1
            self.text = self.history[self.index]


class BoxIOWidget(BoxLayout):
    input_wid = ObjectProperty()
    status_wid = ObjectProperty()
    output_wid = ObjectProperty()


class etmApp(App):
    title = 'etm'
    icon = 'etmlogo_512x512x32.png'

    def build(self):
        return BoxIOWidget()

if __name__ == "__main__":
    etmdir = ''
    if len(sys.argv) > 1:
        etmdir = sys.argv.pop(1)
    (user_options, options, use_locale) = etmData.get_options(etmdir)
    loop = etmData.ETMLoop(options)
    etmApp().run()
