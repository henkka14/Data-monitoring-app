"""Read sensor data."""

import os
import datetime as dt
import sqlite3
from pathlib import Path

import nidaqmx

class ReadData:
    
    def __init__(self):
        file_path = os.path.dirname(__file__)
       
        postfix = 1
        while (os.path.exists(os.path.join(
                                file_path,
                                'Databases',
                                'monitorDB' + str(postfix) + '.sqlite')
                                )):
            postfix += 1

        self.dbname = str(Path('Databases/'+ 'monitorDB' + str(postfix)
                               + '.sqlite'))

        conn = sqlite3.connect(
            self.dbname,
            detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES
            )
        c = conn.cursor()
        c.execute("CREATE TABLE monitoring_table\
            (ts timestamp primary key, Forces real, Rounds real)")
        conn.commit()
        conn.close()

    def retrieve_sensor_values(self):
        """Get sensor values."""

        nidaqmx.scale.Scale.create_lin_scale(
            scale_name="Voltage to Kilograms", 
            slope=20, 
            y_intercept=-100,
            )

        conn = sqlite3.connect(
            self.dbname, 
            detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES
            )

        c = conn.cursor()

        with nidaqmx.Task() as task:
            task.ai_channels.add_ai_voltage_chan("Dev1/ai0", 
                units=nidaqmx.constants.VoltageUnits.FROM_CUSTOM_SCALE, 
                custom_scale_name="Voltage to Kilograms"
                )
            task.ai_channels.add_ai_voltage_chan("Dev1/ai1")
            read_value = task.read()
            date_now = dt.datetime.now()
            if read_value[1] < 1:
                read_value[1] = 0

        c.execute("INSERT INTO monitoring_table\
           (ts, Forces, Rounds) VALUES (?, ?, ?)",
           (date_now, read_value[0], read_value[1])
        )
        conn.commit()
        conn.close()

    def get_db(self):
        """Return database file name."""
        return self.dbname