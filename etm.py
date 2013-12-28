# -*- coding: utf-8 -*-
import sys
import etmKv.etmData as etmData
from etmKv.etmData import get_current_time, leadingzero, init_localization


from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.codeinput import CodeInput
from kivy.uix.button import Button
# from kivy.uix.widget import Widget

from pygments.lexers.special import TextLexer

from kivy.uix.label import Label
from kivy.uix.modalview import ModalView
from kivy.properties import ObjectProperty
from kivy.config import Config
from kivy.clock import Clock
Config.set('graphics', 'height', '430')
Config.set('graphics', 'width', '520')

import gettext
_ = gettext.gettext


class ETMEditor(CodeInput):

    def __init__(self, parent=None, callback=None):
        self.parent = parent
        self.button = Button
        self.callback = callback
        super(ETMEditor, self).__init__(multiline=True, size_hint=(1, None), height=380, lexer=TextLexer())
        self.modified = False
        self.bind(focus=self.on_focus)

    def _keyboard_on_key_up(self, window, keycode):
        # inform ETMDialog about the modification state
        if self.callback:
            self.callback((len(self._undo) > 0))
        super(ETMEditor, self)._keyboard_on_key_up(
            window, keycode)

    def on_focus(self, instance, value):
        if value:
            print('Editor focused', instance)
        else:
            print('Editor defocused', instance)
        super(ETMEditor, self).on_focus(instance, value)


class ETMDialog():

    def __init__(self, parent=None, prompt="etm", validator=lambda x: True):
        self.parent = parent
        self.prompt = prompt
        self.validator = validator
        self.text = ''
        self.editor = ETMEditor()

        self.btnclose = Button(text=_('Close'), size_hint_y=None, height='30sp')
        self.btnsave = Button(text=_('Save'), size_hint_y=None, height='30sp')
        buttons = BoxLayout(orientation='horizontal', height='30sp')
        buttons.add_widget(self.btnsave)
        buttons.add_widget(self.btnclose)

        self.content = BoxLayout(orientation='vertical')

        self.input = ETMEditor(callback=self.set_modified)
        self.input.background_color = [1, 1, 1, 1]
        self.input.bind(on_text_validate=self.validate)
        # self.input.bind(on_key_up=self.on_text)
        self.content.add_widget(self.input)
        self.content.add_widget(buttons)
        self.popup = ModalView(size_hint=(None, None), size=(500, 420))
        self.popup.add_widget(self.content)
        self.btnsave.bind(on_release=self.validate)
        self.btnclose.bind(on_release=self.popup.dismiss)
        self.btnsave.disabled = True

    def run(self):
        self.input.reset_undo()
        self.input.text = ''
        self.input.focus = True
        self.popup.open()

    def validate(self, value):
        if self.validator(self.input.text):
            self.parent.output_wid.text = self.input.text
            self.input.focus = False
            self.popup.dismiss()
            self.parent.input_wid.focus = True

    def set_modified(self, bool):
        print('set_modified', bool)
        self.modified = bool
        self.btnsave.disabled = not bool


class ETMTextInput(TextInput):

    history = []
    index = 0
    now = None
    options = {}
    popup = ''
    value = ''
    firsttime = True
    mode = 'command'   # or edit or delete
    item_hsh = {}

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
        if self.firsttime:
            # only do this once
            self.firsttime = False
            self.bind(focus=self.on_focus)

            self.Dialog = ETMDialog(parent=self, prompt="etm text")
            self.loop = loop
            self.loop.parent = self
            res = self.loop.do_command('a')
            self.options = self.loop.options
            self.start_timer()
            return(res)
        return()

    def start_timer(self):
        self.now = get_current_time()
        nxt = (60 - self.now.second)
        print(self.now)
        Clock.schedule_once(self.timer_callback, nxt)

    def timer_callback(self, dt):
        self.start_timer()

    def get_input(self, question):
        self.command_mode = False
        return(question)

    def process_input(self):
        """
        This is called whenever enter is pressed in the input field.
        Action depends upon comand_mode.
        Append input to history, process it and show the result in output.
        """
        cmd = self.text.strip()

        if not cmd:
            return(True)

        if self.mode == 'command':
            if cmd == 'q':
                sys.exit()
            cmd = cmd.strip()
            if cmd[0] in ['a', 'r', 't']:
                # simple command history for report commands
                if cmd in self.history:
                    self.history.remove(cmd)
                self.history.append(cmd)
                self.index = len(self.history) - 1
            self.select_all()
            try:
                res = loop.do_command(cmd)
            except:
                self.Dialog.run()
                res = self.Dialog.text
                print('res', res)

        elif self.mode == 'edit':
            print('edit', cmd)
            res = loop.do_edit(cmd)

        elif self.mode == 'delete':
            print('deleted', cmd)
            res = ''

        elif self.mode == 'new_date':
            print('date', cmd)
            res = loop.new_date(cmd)

        if not res:
            return(True)
        self.output_wid.text = res
        self.scroll_wid.scroll_y = 1
        self.scroll_to_top()

    def scroll_to_top(self):
        # print('scrolling')
        self.scroll_wid.update_from_scroll()

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

    def on_focus(self, instance, value):
        if value:
            print('focused', instance)
        else:
            print('defocused', instance)
        super(ETMTextInput, self).on_focus(instance, value)


class BoxIOWidget(BoxLayout):
    input_wid = ObjectProperty()
    status_wid = ObjectProperty()
    output_wid = ObjectProperty()
    scroll_wid = ObjectProperty()


class etmApp(App):
    title = 'etm'
    icon = 'etmlogo_512x512x32.png'

    def build(self):
        return BoxIOWidget()

if __name__ == "__main__":
    init_localization()
    etmdir = ''
    if len(sys.argv) > 1:
        etmdir = sys.argv.pop(1)
    (user_options, options, use_locale) = etmData.get_options(etmdir)
    loop = etmData.ETMLoop(options)
    etmApp().run()
