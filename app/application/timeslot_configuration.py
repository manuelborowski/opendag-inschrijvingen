import app.data.settings
from app.data import timeslot_configuration as mtc, settings as msettings
from app.application import util as mutil
from app import log, db
import datetime, sys, json


def add_timeslot_configuration(date, length, nbr_of_timeslots, items_per_timeslot):
    try:
        tc = mtc.get_first_timeslot_configuration(date, length, nbr_of_timeslots, items_per_timeslot)
        if tc:
            return
        mtc.add_timeslot_configuration(date, length, nbr_of_timeslots, items_per_timeslot)
    except Exception as e:
        log.error(f'{sys._getframe().f_code.co_name}: {e}')


def timeslot_configuration_changed_cb(value, opaque):
    try:
        new_tcs = None
        try:
            new_tcs = json.loads(value)
        except:
            pass
        if new_tcs:
            tcs = mtc.get_timeslot_configurations()
            mtc.delete_timeslot_configuration(tc_list = tcs)
            for tc in new_tcs:
                mtc.add_timeslot_configuration(datetime.datetime(tc['year'], tc['month'], tc['day'], tc['hour'], tc['minute']),
                                               tc['length'], tc['number'], tc['places'])
    except Exception as e:
        log.error(f'{sys._getframe().f_code.co_name}: {e}')


msettings.subscribe_setting_changed('timeslot-config-timeslots-template', timeslot_configuration_changed_cb, None)

def flatten_timeslots():
    if msettings.get_configuration_setting('timeslot-config-timeslots-is-flat'):
        return
    flat = []
    timeslot_settings = app.data.settings.get_json_template('timeslot-config-timeslots-template')
    for t in timeslot_settings:
        start_time = datetime.datetime(t['year'], t['month'], t['day'], t['hour'], t['minute'])
        length = t['length']
        number = t['number']
        places = t['places']
        for i in range(number):
            time = start_time + datetime.timedelta(minutes=(length * i))
            flat.append({
                'year': time.year,
                'month': time.month,
                'day': time.day,
                'hour': time.hour,
                'minute': time.minute,
                'length': length,
                'number': 1,
                'places': places
            })
    app.data.settings.set_json_template('timeslot-config-timeslots-template', flat)
    msettings.set_configuration_setting('timeslot-config-timeslots-is-flat', True)
