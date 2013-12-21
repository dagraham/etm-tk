# -*- coding: utf-8 -*-
# import etmKv.etmData as etmData

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.config import Config
Config.set('graphics', 'width', '440')
Config.set('graphics', 'height', '520')


class ETMTextInput(TextInput):

    history = []
    index = 0

    def _keyboard_on_key_down(self, window, keycode, text, modifiers):
        if keycode[0] == 273:  # 273 is the keycode for up
            print('up pressed')
            self.previous_history()
        elif keycode[0] == 274:  # 274 is the keycode for down
            print('down pressed')
            self.next_history()
        elif keycode[0] == 13:  # 13 is the keycode for enter
            print('return pressed')
            self.process_input()
        else:
            super(ETMTextInput, self)._keyboard_on_key_down(
                window, keycode, text, modifiers)

    def process_input(self):
        cmd = self.text.strip()
        if cmd:
            self.history.append(cmd)
            self.index = len(self.history) - 1
            print(cmd, self.index)

    def previous_history(self):
        if self.index >= 1:
            self.index -= 1
            self.text = self.history[self.index]

    def next_history(self):
        if self.index + 1 < len(self.history):
            self.index += 1
            self.text = self.history[self.index]


class BoxIOWidget(BoxLayout):
    def set_text(self, *args):
        fo = open('./data.txt', 'r')
        s = "\n".join(fo.readlines())
        fo.close()
        return unicode(s, 'utf-8')

    # def process_input(self):
    #     cmd = self.ids['input'].text
    #     print(cmd)
    #     self.ids['input'].focus = True


class etmApp(App):
    def build(self):
        return BoxIOWidget()

if __name__ == "__main__":
    etmApp().run()
