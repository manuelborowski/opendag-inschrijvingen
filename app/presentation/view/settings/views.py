from flask import render_template
from flask_login import login_required

from app import admin_required
from app.application import socketio as msocketio, event as mevent
from . import settings
from app.application import settings as msettings
import json

@settings.route('/settings', methods=['GET', 'POST'])
@admin_required
@login_required
def show():
    default_settings = msettings.get_configuration_settings()
    data = {
        'default': default_settings,
        'template': settings_formio,
    }
    return render_template('/settings/settings.html', data=data)


def update_settings_cb(msg, client_sid=None):
  try:
    data = msg['data']
    settings = json.loads(data['value'])
    msettings.set_setting_topic(settings)
    msettings.set_configuration_setting(data['setting'], data['value'])
    msocketio.send_to_room({'type': 'settings', 'data': {'status': True}}, client_sid)
  except Exception as e:
    msocketio.send_to_room({'type': 'settings', 'data': {'status': False, 'message': str(e)}}, client_sid)


def event_received_cb(msg, client_sid=None):
    mevent.process_event(msg['data']['event'])

msocketio.subscribe_on_type('settings', update_settings_cb)
msocketio.subscribe_on_type('event', event_received_cb)


from app.presentation.view import false, true, null

# https://formio.github.io/formio.js/app/builder
settings_formio = \
  {
    "display": "form",
    "components": [
      {
        "label": "General",
        "tableView": false,
        "key": "container",
        "type": "container",
        "input": true,
        "components": [
          {
            "title": "Generic",
            "theme": "primary",
            "collapsible": true,
            "key": "algemeen",
            "type": "panel",
            "label": "Algemeen",
            "collapsed": true,
            "input": false,
            "tableView": false,
            "components": [
              {
                "label": "Submit",
                "showValidations": false,
                "theme": "warning",
                "tableView": false,
                "key": "submit",
                "type": "button",
                "input": true
              },
              {
                "label": "Send confirmation mails",
                "tableView": false,
                "defaultValue": false,
                "persistent": false,
                "key": "generic-enable-send-ack-email",
                "type": "checkbox",
                "input": true
              },
              {
                "label": "Translations",
                "autoExpand": false,
                "tableView": true,
                "key": "generic-translations",
                "type": "textarea",
                "input": true
              }
            ]
          }
        ]
      },
      {
        "label": "Student registration",
        "tableView": false,
        "key": "visitors",
        "type": "container",
        "input": true,
        "components": [
          {
            "title": "STUDENT registration",
            "theme": "primary",
            "collapsible": true,
            "key": "RegistratieTemplate1",
            "type": "panel",
            "label": "BEZOEKERS : Registratie template en e-mail",
            "collapsed": true,
            "input": false,
            "tableView": false,
            "components": [
              {
                "label": "Submit",
                "showValidations": false,
                "theme": "warning",
                "tableView": false,
                "key": "submit",
                "type": "button",
                "input": true
              },
              {
                "label": "Arm sending confirmation mail",
                "tableView": false,
                "defaultValue": false,
                "key": "student-register-arm-send-ack-mail",
                "type": "checkbox",
                "input": true
              },
              {
                "label": "STUDENT registration (formio sandbox)",
                "autoExpand": false,
                "tableView": true,
                "key": "student-register-template",
                "type": "textarea",
                "input": true
              },
              {
                "label": "WEB RESPONSE templates (formio sandbox)",
                "autoExpand": false,
                "tableView": true,
                "key": "student-web-response-template",
                "type": "textarea",
                "input": true
              },
              {
                "label": "EMAIL RESPONSE templates (formio sandbox)",
                "autoExpand": false,
                "tableView": true,
                "key": "student-email-response-template",
                "type": "textarea",
                "input": true
              },
              {
                "label": "STUDENT registration register settings",
                "autoExpand": false,
                "tableView": true,
                "persistent": false,
                "key": "student-register-settings",
                "type": "textarea",
                "input": true
              }
            ]
          }
        ]
      },
      {
        "label": "Timeslot registration",
        "tableView": false,
        "key": "visitors1",
        "type": "container",
        "input": true,
        "components": [
          {
            "title": "TIMESLOT registration",
            "theme": "primary",
            "collapsible": true,
            "key": "RegistratieTemplate1",
            "type": "panel",
            "label": "BEZOEKERS : Registratie template en e-mail",
            "collapsed": true,
            "input": false,
            "tableView": false,
            "components": [
              {
                "label": "Submit",
                "showValidations": false,
                "theme": "warning",
                "tableView": false,
                "key": "submit",
                "type": "button",
                "input": true
              },
              {
                "label": "Arm sending confirmation mail",
                "tableView": false,
                "defaultValue": false,
                "key": "timeslot-register-arm-send-ack-mail",
                "type": "checkbox",
                "input": true
              },
              {
                "label": "Open timeslot registration at:",
                "labelPosition": "left-left",
                "format": "dd/MM/yyyy HH:mm ",
                "tableView": false,
                "datePicker": {
                  "disableWeekends": false,
                  "disableWeekdays": false
                },
                "timePicker": {
                  "showMeridian": false
                },
                "enableMinDateInput": false,
                "enableMaxDateInput": false,
                "key": "timeslot-open-registration-at",
                "type": "datetime",
                "input": true,
                "widget": {
                  "type": "calendar",
                  "displayInTimezone": "viewer",
                  "locale": "en",
                  "useLocaleSettings": false,
                  "allowInput": true,
                  "mode": "single",
                  "enableTime": true,
                  "noCalendar": false,
                  "format": "dd/MM/yyyy HH:mm ",
                  "hourIncrement": 1,
                  "minuteIncrement": 1,
                  "time_24hr": true,
                  "minDate": null,
                  "disableWeekends": false,
                  "disableWeekdays": false,
                  "maxDate": null
                }
              },
              {
                "label": "TIMESLOT registration (formio sandbox)",
                "autoExpand": false,
                "tableView": true,
                "key": "timeslot-register-template",
                "type": "textarea",
                "input": true
              },
              {
                "label": "WEB RESPONSE templates (formio sandbox)",
                "autoExpand": false,
                "tableView": true,
                "key": "timeslot-web-response-template",
                "type": "textarea",
                "input": true
              },
              {
                "label": "EMAIL RESPONSE templates (formio sandbox)",
                "autoExpand": false,
                "tableView": true,
                "key": "timeslot-email-response-template",
                "type": "textarea",
                "input": true
              }
            ]
          }
        ]
      },
      {
        "label": "Timeslot",
        "tableView": false,
        "key": "timeslot",
        "type": "container",
        "input": true,
        "components": [
          {
            "title": "TIMESLOT configuration",
            "theme": "primary",
            "collapsible": true,
            "key": "RegistratieTemplate2",
            "type": "panel",
            "label": "BEZOEKERS : Registratie template en e-mail",
            "collapsed": true,
            "input": false,
            "tableView": false,
            "components": [
              {
                "label": "Submit",
                "showValidations": false,
                "theme": "warning",
                "tableView": false,
                "key": "submit",
                "type": "button",
                "input": true
              },
              {
                "html": "<p>Configureer tijdsloten:&nbsp;<br>[<br>&nbsp; {\"jaar\": 2021, \"maand\": 5, \"dag\": 1, \"uur\": 9, \"minuut\": 0, \"lengte\": 15, \"aantal\": 12, \"plaatsen\": 8},<br>&nbsp; {\"jaar\": 2021, \"maand\": 5, \"dag\": 1, \"uur\": 12, \"minuut\": 0, \"lengte\": 15, \"aantal\": 4, \"plaatsen\": 5}<br>]</p>",
                "label": "Content",
                "refreshOnChange": false,
                "key": "content",
                "type": "content",
                "input": false,
                "tableView": false
              },
              {
                "label": "Tijdslot configuratie",
                "autoExpand": false,
                "tableView": true,
                "persistent": false,
                "key": "timeslot-config-timeslots-template",
                "type": "textarea",
                "input": true
              }
            ]
          }
        ]
      },
      {
        "label": "Emailserver",
        "tableView": false,
        "key": "emailserver",
        "type": "container",
        "input": true,
        "components": [
          {
            "title": "E-mail server settings",
            "theme": "primary",
            "collapsible": true,
            "key": "eMailServerSettings",
            "type": "panel",
            "label": "E-mail server settings",
            "input": false,
            "tableView": false,
            "components": [
              {
                "label": "Submit",
                "showValidations": false,
                "theme": "warning",
                "tableView": false,
                "key": "submit",
                "type": "button",
                "input": true
              },
              {
                "label": "# email send retries",
                "labelPosition": "left-left",
                "mask": false,
                "tableView": false,
                "delimiter": false,
                "requireDecimal": false,
                "inputFormat": "plain",
                "truncateMultipleSpaces": false,
                "key": "email-send-max-retries",
                "type": "number",
                "spellcheck": false,
                "input": true
              },
              {
                "label": "Time (sec) between sending emails",
                "labelPosition": "left-left",
                "mask": false,
                "tableView": false,
                "persistent": false,
                "delimiter": false,
                "requireDecimal": false,
                "inputFormat": "plain",
                "truncateMultipleSpaces": false,
                "key": "email-task-interval",
                "type": "number",
                "spellcheck": true,
                "input": true
              },
              {
                "label": "Max # emails per minute",
                "labelPosition": "left-left",
                "mask": false,
                "tableView": false,
                "persistent": false,
                "delimiter": false,
                "requireDecimal": false,
                "inputFormat": "plain",
                "truncateMultipleSpaces": false,
                "key": "emails-per-minute",
                "type": "number",
                "spellcheck": true,
                "input": true
              },
              {
                "label": "Base URL",
                "labelPosition": "left-left",
                "tableView": true,
                "key": "email-base-url",
                "type": "textfield",
                "input": true
              },
              {
                "label": "Enable sending emails",
                "tableView": false,
                "defaultValue": false,
                "persistent": false,
                "key": "email-enable-send-email",
                "type": "checkbox",
                "input": true
              }
            ],
            "collapsed": true
          }
        ]
      }
    ]
  }