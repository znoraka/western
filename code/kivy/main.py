from kivy.app import App
from kivy.uix.widget import Widget
from kivy.graphics import Color, Ellipse
from kivy.core.window import Window

from kivy.uix.floatlayout import FloatLayout
from kivy.factory import Factory
from kivy.properties import ObjectProperty
from kivy.uix.popup import Popup
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.tabbedpanel import TabbedPanel
from kivy.uix.dropdown import DropDown

from kivy.core.image import Image as CoreImage

import stegano_demo as stego

import os

class ImageButton(ButtonBehavior, Image):
    def load_image(self, source):
        self.source = source
        self.reload()

class LoadDialog(FloatLayout):
    load = ObjectProperty(None)
    cancel = ObjectProperty(None)


class SaveDialog(FloatLayout):
    save = ObjectProperty(None)
    text_input = ObjectProperty(None)
    cancel = ObjectProperty(None)


class ImageSelectScreen(Screen):
    loadfile = ObjectProperty(None)
    savefile = ObjectProperty(None)
    text_input = ObjectProperty(None)

    def dismiss_popup(self):
        self._popup.dismiss()

class MethodsDropDown(DropDown):
    def __init__(self, *args, **kwargs):
        super(MethodsDropDown, self).__init__(*args, **kwargs)
        
        self.methods = ["method1", "method2", "method3", "method4"]

        for i in self.methods:
            btn = Button(text=i, size_hint_y=None, height='44sp')
            btn.bind(on_release=lambda btn: self.select(btn.text))
            self.add_widget(btn)

class SteganoScreen(Screen):
    def unfocus(self):
        self.document.focus = False
        
    def is_cover_tab_selected(self):
        return self.tabbedpanel.current_tab.text == self.coverpanel.text

    def set_image_source(self, image, source):
        image.source = source
        image.reload()

    def custom_switch_to(self, tab):
        if self.tabbedpanel.current_tab.text == tab.text:
            return

        self.message.text = ''
        self.document.text = ''
        
        if(self.is_cover_tab_selected()):
            self.gobutton.text = 'Decode'
            self.tabbedpanel.switch_to(self.stegopanel)
        else:
            self.gobutton.text = 'Embedd'
            self.tabbedpanel.switch_to(self.coverpanel)
    
    def on_pre_enter(self):
        self.set_image_source(self.coverimg, self.manager.img)

    def on_enter(self):
        self.dd = MethodsDropDown()
        self.dropdownbutton.bind(on_release=self.dd.open)
        self.dd.bind(on_select=lambda instance, x: setattr(self.dropdownbutton, 'text', x))
        self.tabbedpanel.switch_to(self.coverpanel)

    def on_go_click(self):
        if(len(self.key.text) == 0):
            return
        
        if(self.is_cover_tab_selected()):
            if(len(self.message.text) == 0):
                return
            
            self.insert()
        else:
            self.decode()
            
    def decode(self):
        self.message.text, bits_count = stego.decode(self.key.text, self.stegoimg.source)
        self.document.text = "Bits count : " + str(bits_count)

    def insert(self):
        length, bpp = stego.embedd(self.message.text, self.key.text, self.coverimg.source, "out.png")
        self.set_image_source(self.stegoimg, 'out.png')
        self.document.text = "Length : " + str(length) + "\nBPP : " + str(bpp)

    def dismiss_popup(self):
        self._popup.dismiss()

    def show_save(self):
        content = SaveDialog(save=self.save, cancel=self.dismiss_popup)
        self._popup = Popup(title="Save file", content=content,
                            size_hint=(0.9, 0.9))
        self._popup.open()

    def save(self, path, filename):
        CoreImage('out.png').save(os.path.join(path, filename))

        self.dismiss_popup()

    def show_load(self):
        content = LoadDialog(load=self.load, cancel=self.dismiss_popup)
        self._popup = Popup(title="Load file", content=content,
                            size_hint=(0.9, 0.9))
        self._popup.open()

    def load(self, path, filename):
        with open(os.path.join(path, filename[0])) as stream:
            if(self.is_cover_tab_selected()):
                self.set_image_source(self.coverimg, os.path.join(path, filename[0]))
            else:
                self.set_image_source(self.stegoimg, os.path.join(path, filename[0]))
                
        self.dismiss_popup()


class InsertScreen(Screen):
    def on_pre_enter(self):
        self.coverimg.source = self.manager.img
        self.coverimg.reload()
             
class RootScreen(ScreenManager):
    img = 'lenac.jpg'
        
class Editor(App):
    
    def build(self):
        return RootScreen()

if __name__ == '__main__':
    Editor().run()
