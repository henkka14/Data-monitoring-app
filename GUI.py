import kivy
kivy.require('1.10.1')

import os, signal, socket
import subprocess
from subprocess import Popen
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.label import Label
from kivy.clock import Clock
from kivy.properties import StringProperty
from kivy.uix.button import Button
from kivy.uix.popup import Popup
import webbrowser

class MonitoringProcess:
    def __init__(self):
        self.file_name = os.path.join(os.path.dirname(__file__), 'dash_plotter_function.py')
        self.p = None
            
    def start(self):
        self.p = Popen(['python', self.file_name], creationflags=subprocess.CREATE_NEW_PROCESS_GROUP)

    def end(self):
        self.p.send_signal(signal.CTRL_BREAK_EVENT)
        self.p = None

class StartScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def push_start(self, *args):
        process.start()
        sm.current = 'monitoring'

    def show_popup(self):
        layout = BoxLayout(orientation='vertical', size_hint=(0.5,0.5))

        popupStart = Button(text='Continue')
        popupCancel = Button(text='Cancel')

        layout.add_widget(popupStart)
        layout.add_widget(popupCancel)

        popup = Popup(title='Are you sure you want to continue?', title_align='center', content=layout, auto_dismiss=False)
        popupStart.bind(on_press=self.push_start)
        popupStart.bind(on_press=popup.dismiss)
        popupCancel.bind(on_press=popup.dismiss)
        popup.open()



class MonitoringScreen(Screen):
    ip_adr = socket.gethostbyname(socket.gethostname())
    label_text = StringProperty()
    
    def __init__(self, **kwargs):
        Clock.schedule_interval(self.check_ip, 1)
        super().__init__(**kwargs)
        self.label_text = 'We are monitoring! Go to the address [ref=addr][u]http://' + str(self.ip_adr) + \
                          ':8050[/u][/ref] to view the monitoring data on any device in the network. ' + \
                          'Clicking the link opens the browser to view the data.'

    def check_ip(self, dt):
        """This function is used to update ip address on the text link."""

        self.ip_adr = socket.gethostbyname(socket.gethostname())
        self.label_text = 'We are monitoring! Go to the address [ref=addr][u]http://' + str(self.ip_adr) + \
                          ':8050[/u][/ref] to view the monitoring data on any device in the network. ' + \
                          'Clicking the link opens the browser to view the data.'

    def webopen(self):
        """This is used to open web browser when clicking link.
        See testermonitor.kv for more functionality on Label."""

        webbrowser.open_new('http://' + str(self.ip_adr) + ':8050')

    def push_end(self, *args):
        process.end()
        sm.current = 'start'

    def show_popup(self):
        layout = BoxLayout(orientation='vertical', size_hint=(0.5,0.5))

        popupEnd = Button(text='Continue')
        popupCancel = Button(text='Cancel')

        layout.add_widget(popupEnd)
        layout.add_widget(popupCancel)

        popup = Popup(title='Are you sure you want to continue?', title_align='center', content=layout, auto_dismiss=False)
        popupEnd.bind(on_press=self.push_end)
        popupEnd.bind(on_press=popup.dismiss)
        popupCancel.bind(on_press=popup.dismiss)
        popup.open()


class TestermonitorApp(App):
    
    def build(self):
        self.icon = 'pictures/monitor.ico'
        
        sm.add_widget(StartScreen(name='start'))
        sm.add_widget(MonitoringScreen(name='monitoring'))
        return sm

if __name__ == '__main__':
    sm = ScreenManager()
    process = MonitoringProcess()
    TestermonitorApp().run()