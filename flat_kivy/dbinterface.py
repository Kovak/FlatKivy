from __future__ import unicode_literals, print_function
from datetime import datetime, timedelta, date
from kivy.storage.jsonstore import JsonStore
from kivy.clock import Clock
import os

class DBInterface(object):

    def __init__(self, data_dir, name, do_date=False, do_hour=False, **kwargs):
        super(DBInterface, self).__init__(**kwargs)
        
        self.ensure_dir(data_dir)
        if do_date:
            if do_hour:
                date = self.convert_time_to_json_ymdh(self.get_time())
            else:
                date = self.convert_time_to_json_ymd(self.get_time())
            json_name = data_dir + name + '-' + date + '.json'
            reset_json_name = (
                data_dir + name + '-' + date + '-reset_timers.json')
        else:
            json_name = data_dir + name + '.json'
            reset_json_name = data_dir + name + '-reset_timers.json'
        self.data = data = JsonStore(json_name)
        self.reset_timers = reset_timers = JsonStore(reset_json_name)
        self.sync = Clock.create_trigger(self.trigger_sync)
        self.check_reset(0.)
        Clock.schedule_interval(self.check_reset, 60.)

    def ensure_dir(self, f):
        d = os.path.dirname(f)
        if not os.path.exists(d):
            os.makedirs(d)

    def check_reset(self, dt):
        reset_timers = self.reset_timers
        current_time = self.get_time()
        keys_to_del = []
        for each in reset_timers:
            expire_time = self.convert_time_from_json(each)
            if expire_time < current_time:
                data = reset_timers[each]
                self.set_entry(data['table'], data['row'], 
                    data['name'], None)
                keys_to_del.append(each)
        for key in keys_to_del:
            reset_timers.delete(key)
            

    def trigger_sync(self, dt):
        data = self.data
        print('syncing')
        data._is_changed = True
        data.store_sync()
        

    def get_entry(self, table, row, name):
        data = self.data
        try:
            return data[table][row][name]['value']
        except:
            return None

    def get_row(self, table, row):
        data = self.data
        try:
            return data[table][row]
        except:
            return None

    def get_table(self, table):
        data = self.data
        try:
            return data[table]
        except:
            return None

    def remove_entry(self, table, row, name, value):
        data = self.data
        try:
            name_data = data[table][row][name]
        except:
            print('no entry: ', table, row, name)
        try:
            name_data['value'].remove(value)
        except:
            print(value, 'not found in: ', table, row, name)
        self.sync()

    def append_entry(self, table, row, name, value, do_timestamp=False):
        data = self.data
        try:
            table_data = data[table]
        except:
            data[table] = table_data = {}
        try:
            row_data = table_data[row]
        except:
            table_data[row] = row_data = {}
        try:
            name_data = row_data[name]
        except:
            name_data = {'value': []}
            row_data[name] = name_data
        if do_timestamp:
            time = self.get_time()
            time_stamp = self.convert_time_to_json(time)
            value = (value, time_stamp)
        name_data['value'].append(value)
        self.sync()

    def set_entry(self, table, row, name, value, do_history=False,
        reset_in_hours=None, do_timestamp=False):
        data = self.data
        print('set_entry', table, row, name, value)
        try:
            table_data = data[table]
        except:
            data[table] = table_data = {}
        try:
            row_data = table_data[row]
        except:
            table_data[row] = row_data = {}
        try:
            name_data = row_data[name]
        except:
            name_data = {'value': None}
            row_data[name] = name_data
        if do_history and 'history' not in name_data:
            name_data['history'] = {}
        if name_data['value'] != value:
            
            name_data['value'] = value
            if do_timestamp:
                time = self.get_time()
                time_stamp = self.convert_time_to_json(time)
                name_data['time_stamp'] = time_stamp
            if do_history:
                time = self.get_time()
                time_stamp = self.convert_time_to_json(time)
                name_data['history'][time_stamp] = value
            if reset_in_hours is not None:
                timed = timedelta(hours=reset_in_hours)
                expire_time = time + timed
                expires_at = self.convert_time_to_json(expire_time)
                reset_timers = self.reset_timers
                reset_timers[expires_at] = {
                    'table': table, 
                    'row': row,
                    'name': name,
                    }

        self.sync()
        if self.data[table] == {}:
            self.data[table] = table_data
            self.sync()



    def get_time(self):
        return datetime.utcnow()

    def convert_time_to_json_ymd(self, datetime):
        if datetime is not None:
            return datetime.strftime('%Y-%m-%d')
        else:
            return None

    def convert_time_to_json_ymdh(self, datetime):
        if datetime is not None:
            return datetime.strftime('%Y-%m-%dT%H')
        else:
            return None

    def convert_time_to_json(self, datetime):
        if datetime is not None:
            return datetime.strftime('%Y-%m-%dT%H:%M:%S')
        else:
            return None

    def convert_time_from_json(self, jsontime):
        if jsontime is not None:
            return datetime.strptime(jsontime, '%Y-%m-%dT%H:%M:%S')
        else:
            return None