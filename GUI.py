"""Graphical User Interface for the application that is done by kivy graphics library."""

import os
import signal
import socket
import subprocess
from subprocess import Popen
import webbrowser
from pathlib import Path

import kivy
kivy.require('1.10.1')

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.label import Label
from kivy.clock import Clock
from kivy.properties import StringProperty, ObjectProperty
from kivy.uix.button import Button
from kivy.uix.popup import Popup


class MonitoringProcess:
    def __init__(self):
        self.file_name = os.path.join(os.path.dirname(__file__),
                                     'dash_plotter_function.py')
        self.p = None
            
    def start(self):
        self.p = Popen([str(Path("venv/Scripts/python")), self.file_name],
                       creationflags=subprocess.CREATE_NEW_PROCESS_GROUP)

    def end(self):
        self.p.send_signal(signal.CTRL_BREAK_EVENT)
        self.p = None


class StartScreen(Screen):
    popup = ObjectProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.popup.ids.continue_button.on_press = self.push_start

    def push_start(self, *args):
        process.start()
        sm.current = 'monitoring'


class MonitoringScreen(Screen):
    ip_adr = socket.gethostbyname(socket.gethostname())
    label_text = StringProperty()
    popup = ObjectProperty()
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        Clock.schedule_interval(self.check_ip, 1)
        self.popup.ids.continue_button.on_press = self.push_end

        self.label_text = (
            'We are monitoring! Go to the address'
            '[ref=addr][u]http://' + str(self.ip_adr) +':8050[/u][/ref]'
            'to view the monitoring data on any device in the network.'
            'Clicking the link opens the browser to view the data.'
        )

    def check_ip(self, dt):
        """This function is used to update ip address on the text link."""

        self.ip_adr = socket.gethostbyname(socket.gethostname())

        self.label_text = (
            'We are monitoring! Go to the address '
            '[ref=addr][u]http://' + str(self.ip_adr) +':8050[/u][/ref]'
            ' to view the monitoring data on any device in the network.'
            'Clicking the link opens the browser to view the data.'
        )

    def webopen(self):
        """
        This is used to open web browser when clicking hyperlink.
        See testermonitor.kv for more functionality on Label.
        """

        webbrowser.open_new('http://' + str(self.ip_adr) + ':8050')

    def push_end(self, *args):
        process.end()
        sm.current = 'end'


class EndScreen(Screen):
    label_text = StringProperty()
    file_path = os.path.abspath('.') + r"\Databases"
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.label_text = (
            'Monitoring ended.'
            'You can find the monitoring data from the folder\n'
            + self.file_path
            )

    def go_to_start(self):
        sm.current = 'start'


class TestermonitorApp(App):
    
    def build(self):
        self.icon = 'pictures/monitor.ico'
        
        sm.add_widget(StartScreen(name='start'))
        sm.add_widget(MonitoringScreen(name='monitoring'))
        sm.add_widget(EndScreen(name='end'))

        return sm

if __name__ == '__main__':
    sm = ScreenManager()
    process = MonitoringProcess()
    TestermonitorApp().run()