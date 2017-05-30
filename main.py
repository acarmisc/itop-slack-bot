# coding=utf-8
from flask import Flask
from flask import request
from flask import jsonify
from flask_slackbot import SlackBot
from confiky import Confiky

import requests
import logging


c = Confiky(files='config.ini')
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['SLACK_TOKEN'] = c.slack.token
app.config['SLACK_CALLBACK'] = '/tickets'
slackbot = SlackBot(app)


def get_user_email(msg):
    users_url = 'https://slack.com/api/users.info'
    res = requests.post(users_url, data=dict(token=app.config['SLACK_TOKEN'], 
                                             scope='users:read', 
                                             user=msg.get('user_id')))
    email = res.json().get('user').get('profile').get('email')

    return email


@app.route('/tickets/', methods=['POST'])
def tickets():
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

