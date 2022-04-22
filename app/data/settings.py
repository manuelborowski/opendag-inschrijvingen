import re
import sys

from flask_login import current_user
from app import log, db
from sqlalchemy import UniqueConstraint
import json


class Settings(db.Model):
    __tablename__ = 'settings'

    class SETTING_TYPE:
        E_INT = 'INT'
        E_STRING = 'STRING'
        E_FLOAT = 'FLOAT'
        E_BOOL = 'BOOL'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(256))
    value = db.Column(db.Text)
    type = db.Column(db.String(256))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'))

    UniqueConstraint('name', 'user_id')

    def log(self):
        return '<Setting: {}/{}/{}/{}>'.format(self.id, self.name, self.value, self.type)



# return: found, value
# found: if True, setting was found else not
# value ; if setting was found, returns the value
def get_setting(name, id=-1):
    try:
        setting = Settings.query.filter_by(name=name, user_id=id if id > -1 else current_user.id).first()
        if setting.type == Settings.SETTING_TYPE.E_INT:
            value = int(setting.value)
        elif setting.type == Settings.SETTING_TYPE.E_FLOAT:
            value = float(setting.value)
        elif setting.type == Settings.SETTING_TYPE.E_BOOL:
            value = True if setting.value == 'True' else False
        else:
            value = setting.value
    except:
        return False, ''
    return True, value


def add_setting(name, value, type, id=-1):
    setting = Settings(name=name, value=str(value), type=type, user_id=id if id > -1 else current_user.id)
    db.session.add(setting)
    db.session.commit()
    log.info('add: {}'.format(setting.log()))
    return True


def set_setting(name, value, id=-1):
    try:
        setting = Settings.query.filter_by(name=name, user_id=id if id > -1 else current_user.id).first()
        if setting.type == Settings.SETTING_TYPE.E_BOOL:
            value = 'True' if value else 'False'
        setting.value = value
        db.session.commit()
    except:
        return False
    return True


def get_test_server():
    found, value = get_setting('test_server', 1)
    if found: return value
    add_setting('test_server', False, Settings.SETTING_TYPE.E_BOOL, 1)
    return False


default_configuration_settings = {
    'generic-enable-send-ack-email': (False, Settings.SETTING_TYPE.E_BOOL),
    'generic-translations': ('{}', Settings.SETTING_TYPE.E_STRING),

    'student-register-arm-send-ack-mail': (False, Settings.SETTING_TYPE.E_BOOL),
    'student-register-template': ('{}', Settings.SETTING_TYPE.E_STRING),
    'student-web-response-template': ('{}', Settings.SETTING_TYPE.E_STRING),
    'student-email-response-template': ('{}', Settings.SETTING_TYPE.E_STRING),
    'student-register-settings': ('{}', Settings.SETTING_TYPE.E_STRING),

    'timeslot-register-arm-send-ack-mail': (False, Settings.SETTING_TYPE.E_BOOL),
    'timeslot-register-template': ('{}', Settings.SETTING_TYPE.E_STRING),
    'timeslot-web-response-template': ('{}', Settings.SETTING_TYPE.E_STRING),
    'timeslot-email-response-template': ('{}', Settings.SETTING_TYPE.E_STRING),
    'timeslot-open-registration-at': ('{}', Settings.SETTING_TYPE.E_STRING),
    'timeslot-config-timeslots-template': ('{}', Settings.SETTING_TYPE.E_STRING),
    'timeslot-config-timeslots-is-flat': (False, Settings.SETTING_TYPE.E_BOOL),

    'email-task-interval': (10, Settings.SETTING_TYPE.E_INT),
    'emails-per-minute': (30, Settings.SETTING_TYPE.E_INT),
    'email-send-max-retries': (2, Settings.SETTING_TYPE.E_INT),
    'email-base-url': ('localhost:5000', Settings.SETTING_TYPE.E_STRING),
    'email-enable-send-email': (False, Settings.SETTING_TYPE.E_BOOL),

    'import-misc-fields': ('{}', Settings.SETTING_TYPE.E_STRING),

}


def get_configuration_settings():
    configuration_settings = {}
    for k in default_configuration_settings:
        configuration_settings[k] = get_configuration_setting(k)
    return configuration_settings


def set_configuration_setting(setting, value):
    if None == value:
        value = default_configuration_settings[setting][0]
    ret = set_setting(setting, value, 1)
    if setting in setting_changed_cb:
        setting_changed_cb[setting][0](value, setting_changed_cb[setting][1])
    return ret


def get_configuration_setting(setting):
    found, value = get_setting(setting, 1)
    if found:
        return value
    else:
        default_setting = default_configuration_settings[setting]
        add_setting(setting, default_setting[0], default_setting[1], 1)
        return default_setting[0]


setting_changed_cb = {}


def subscribe_setting_changed(setting, cb, opaque):
    setting_changed_cb[setting] = (cb, opaque)
    return True


def get_translations(key):
    translations = get_json_template('generic-translations')
    return translations[key] if key in translations else {}

# save settings which are not in the database yet
# get_configuration_settings()

def get_json_template(key):
    template_string = get_configuration_setting(key)
    if template_string == '':
        template_string = '{}'
        log.error(f'{sys._getframe().f_code.co_name}: Empty template: {key}')
    try:
        settings = json.loads(template_string)
    except json.JSONDecodeError as e:
        raise Exception(f'Template has invalid JSON syntax: {key} {e}')
    return settings


def set_json_template(key, data):
    try:
        template_string = json.dumps(data)
        template_string = re.sub('},', '},\n', template_string)
        return set_configuration_setting(key, template_string)
    except json.JSONDecodeError as e:
        raise Exception(f'Template has invalid JSON syntax: {key}, {data}, {e}')