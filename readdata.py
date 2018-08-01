import os
import nidaqmx
from tinydb import TinyDB
from apscheduler.schedulers.blocking import BlockingScheduler
import datetime as dt


class ReadData:
    
    def __init__(self):
        file_path = os.path.dirname(__file__)
        postfix = 1
        while (os.path.exists(os.path.join(file_path, 'monitorDB' + str(postfix)))):
            postfix += 1

        self.scheduler = BlockingScheduler()
        self.db = TinyDB('monitorDB' + str(postfix))

    def retrieve_sensor_values(self):
        nidaqmx.scale.Scale.create_lin_scale(scale_name="Voltage to Kilograms", slope=20, y_intercept=-100)

        with nidaqmx.Task() as task:
            task.ai_channels.add_ai_voltage_chan("Dev1/ai0", units=nidaqmx.constants.VoltageUnits.FROM_CUSTOM_SCALE, custom_scale_name="Voltage to Kilograms")
            read_value = task.read()
            date_now = dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        self.db.insert({'Date': date_now, 'Kilograms': read_value})

    def get_db(self):
        return self.db

    def get_scheduler(self):
        return self.scheduler
        