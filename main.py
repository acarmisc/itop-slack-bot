#!/opt/itop-bot/venv/bin/python
# coding=utf-8
from flask import Flask
from flask import request
from flask import jsonify
from confiky import Confiky

import json
import requests
import logging


c = Confiky(files='/opt/itop-bot/config.ini')
logger = logging.getLogger(__name__)

app = Flask(__name__)

from HTMLParser import HTMLParser

class MLStripper(HTMLParser):
    def __init__(self):
        self.reset()
        self.fed = []
    def handle_data(self, d):
        self.fed.append(d)
    def get_data(self):
        return ''.join(self.fed)

def strip_tags(html):
    s = MLStripper()
    s.feed(html)
    return s.get_data()


def get_user_email(msg):
    users_url = 'https://slack.com/api/users.info'
    res = requests.post(users_url, data=dict(token=c.slack.token, 
                                             scope='users:read', 
                                             user=msg.get('user_id')))
    email = res.json().get('user').get('profile').get('email')

    return email


@app.route('/callback/', methods=['POST'])
def callback():
    payload = json.loads(request.form.get('payload'))
    action = payload.get('actions')[0].get('value')
    cmd, obj_class, obj_id = payload.get('callback_id').split(' ')
    if cmd == 'UPDATE':
        if action == 'cancel':
            return "Ok. Nothing done."
        if action in ('pending', 'resolved'):
            res = itop.update_request(obj_id, 'status', action)
        
        return "UserRequest updated."


@app.route('/tickets/new', methods=['GET', 'POST'])
def new_ticket():
    import thread
    def handle_new(request):
        import time
        time.sleep(5)
        channel = '@acarmisc' #itop'
        url = 'https://slack.com/api/chat.postMessage'

        try:
            req = get_single_request(request, request.get('req'), new=True)
        except ValueError as e:
            logger.error(e)
            print e
    
        res = requests.post(url, data=dict(token=c.slack.token,
                                           channel=channel,
                                           text=req.get('text'),
                                           attachments=json.dumps(req.get('attachments'))))

        return 

    req = request.form.copy()
    thread.start_new_thread(handle_new, (req,))

    return ""   


@app.route('/tickets/', methods=['POST'])
def tickets():
    
    text = request.form.get('text').split(' ')
    cmd = text.pop(0)
    args = text

    if not cmd or cmd == 'all':
        return get_all_requests(request)

    if cmd[:2].upper() == 'R-':
        response = get_single_request(request, cmd)
        return jsonify(response)

    return "no valid command supplied"


def get_single_request(request, ref, new=False):
    if new:
        resp = itop.get_ticket(ref)
    else:
        resp = itop.get_request(ref)

    if not resp.objects:
        raise ValueError("%s not found." % ref)

    el = resp.objects[0]

    req_url = itop.get_url(el.klass, el.key)

    actions = list()
    actions.append(dict(name="cancel", text="cancel", type="button", value="cancel"))
    actions.append(dict(name="pending", text="pending", type="button", value="pending"))
    actions.append(dict(name="resolved", text="resolved", type="button", value="resolved", color="#40A864"))

    fields = list()
    fields.append(dict(title="Description", value=strip_tags(el.description)))
    fields.append(dict(title="Caller", value=el.caller_id_friendlyname, short=True))
    if not new:
        fields.append(dict(title="Service", value=el.service_name, short=True))
        fields.append(dict(title="Created", value=el.start_date, short=True))
        fields.append(dict(title="Last update", value=el.last_update, short=True))

    attachments = list()
    if new:
        attachments.append(dict(title_link=req_url, title="More details..", fields=fields))
    else:
        attachments.append(dict(text="Do you want to change the state?", color="#3AA3E3", callback_id="UPDATE UserRequest %s" % ref, actions=actions, fields=fields))

    return dict(text=el.title, attachments=attachments, )


def get_all_requests(request):
    email = get_user_email(request.form)
    resp = itop.get_requests(email)
    
    response = dict(attachments=list())

    response['text'] = "We've found %s UserRequest assigned to you!" % len(resp.objects)
    for el in resp.objects:
        attachment = dict(mrkdwn_in=["title"])
        attachment['title'] = "%s: %s " % (el.friendlyname, el.title)
        attachment['text'] = "from %s" % el.caller_id_friendlyname
        attachment['color'] = "#90C3D4" if el.status in ("pending",) else "#40A864"
        attachment['title_link'] = itop.get_url(el.klass, el.key)

        response.get('attachments').append(attachment)

    return jsonify(response)


if __name__ == "__main__":
    from itoplib import iTopClient
    itop = iTopClient(c.itop.host, c.itop.user, c.itop.pwd)
    app.run(host="0.0.0.0", debug=c.misc.debug)

