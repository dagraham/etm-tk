# -*- coding: utf-8 -*-
import sys
import etmKv.etmData as etmData
from etmKv.etmData import get_current_time, leadingzero

# from datetime import date, datetime, timedelta
# from dateutil.tz import tzlocal, gettz
# from dateutil.parser import parse


from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
# from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.textinput import TextInput
from kivy.uix.codeinput import CodeInput
from pygments.lexers.special import TextLexer

from kivy.uix.label import Label
# from kivy.uix.popup import Popup
from kivy.uix.modalview import ModalView
# from kivy.uix.button import Button
from kivy.properties import ObjectProperty
from kivy.config import Config
from kivy.clock import Clock
Config.set('graphics', 'height', '440')
Config.set('graphics', 'width', '530')


class ETMTextInput(TextInput):

    history = []
    index = 0
    now = None
    status_wid = ObjectProperty()
    input_wid = ObjectProperty()
    output_wid = ObjectProperty()
    options = {}
    popup = ''


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
        self.loop = loop
        res = self.loop.do_command('s')
        self.options = self.loop.options
        # print(self.options)
        self.start_timer()
        return(res)

    def start_timer(self):
        self.now = get_current_time()
        nxt = (60 - self.now.second)
        if self.status_wid:
            nowfmt = "{0} {1}".format(
                self.now.strftime(self.options['reprtimefmt']).lower(),
                self.now.strftime("%a %b %d %Z"))
            nowfmt = leadingzero.sub("", nowfmt)
            self.status_wid.text = nowfmt
        else:
            nxt = 1
        Clock.schedule_once(self.timer_callback, nxt)

    def timer_callback(self, dt):
        # print('In callback')
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
                res = self.my_dialog()
                # res = self.dialog
                print('got here')
            if not res:
                return(True)
            self.output_wid.text = res
            self.output_wid.scroll_y = 1

    # def show_popup(self):
    #     y = max(self.output_wid.minimum_height, self.output_wid.height)
    #     print('y', y)
    #     btnclose = Button(text='Save', size_hint_y=None, height='40sp')
    #     btnsave = Button(text='Cancel', size_hint_y=None, height='40sp')
    #     buttons = BoxLayout(orientation='horizontal', height='40sp')
    #     buttons.add_widget(btnclose)
    #     buttons.add_widget(btnsave)
    #     content = BoxLayout(orientation='vertical')
    #     # content.add_widget(Label(text='Hello world'))
    #     content.add_widget(CodeInput(multiline=True, size_hint=(1, None), height=350, focus=True, lexer=TextLexer()))
    #     content.add_widget(buttons)
    #     popup = ModalView(size_hint=(None, None), size=(400, 400))
    #     popup.add_widget(content)
    #     btnclose.bind(on_release=popup.dismiss)
    #     btnsave.bind(on_release=popup.dismiss)
    #     popup.open()

    def my_dialog(self):
        def validate(value):
            print('validate', value)
            self.output_wid.text = input.text
            self.output_wid.scroll_y = 1
            self.output_wid.readonly = False
            self.output_wid.focus = True
            self.output_wid.cursor = (0, 0)
            popup.dismiss()

        content = BoxLayout(orientation='vertical')
        content.add_widget(Label(text='etm'))
        input = CodeInput(multiline=False, size_hint=(1, None), height=30, focus=True, lexer=TextLexer())
        content.add_widget(input)
        popup = ModalView(size_hint=(None, None), size=(400, 200))
        popup.add_widget(content)
        input.bind(on_text_validate=validate)
        popup.open()

    # def on_enter(self, instance):
    #     print('User pressed enter in', instance)

    # def on_text(self, instance, value):
    #     self.popup = value
    #     print("value", self.popup)

    # def validate(self, instance):
    #     print("final value", self.popup)
    #     self.output_wid.text = self.popup
    #     self.output_wid.scroll_y = 1
    #     return(True)

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
    def set_text(self, *args):
        fo = open('./data.txt', 'r')
        s = "\n".join(fo.readlines())
        fo.close()
        return unicode(s, 'utf-8')


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
