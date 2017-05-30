import itopy
from collections import namedtuple


class iTopResponse:

    def __init__(self, response, client):
        self.client = client
        self._raw = response
        self.message = response.get('message')
        self.code = response.get('code')
        self.item_key = response.get('item_key')
        self.objects = list()
        
        self._parse_response(response.get('objects'))

    def _parse_response(self, objects):
        if not objects:
            self.objects = None
            return

        for k, v in objects.iteritems():
            obj_class, obj_key = k.split('::')
            data = v.get('fields')
            data['klass'] = obj_class
            data['key'] = obj_key
            obj = namedtuple(obj_class, data.keys())(**data)
            self.objects.append(obj)

        return

    def has_objects(self):
        return True if self.objects else False


class iTopClient:

    def __init__(self, host, user, pwd, version=1.3):
        self.host = host
        self.itop = itopy.Api()
        self.itop.connect("%s/webservices/rest.php" % host, version, user, pwd)

    def get(self, entity, query):
        resp = self.itop.get(entity, query)
        return iTopResponse(resp, self)
    
    def get_url(self, entity, id):
        schema = '%s/pages/UI.php?operation=details&class=%s&id=%s'
        return schema % (self.host, entity, id)

    def get_request(self, ref):
        query = 'SELECT UserRequest WHERE ref = "%s"' % ref.upper()
        return self.get('UserRequest', query)

    def get_requests(self, agent, closed=True):
        # lookup using e-mail
        excluded_states = '"closed", "resolved", "rejected"' if closed else ''
        query = 'SELECT UserRequest JOIN Person ON UserRequest.agent_id = Person.id \
                 WHERE Person.email = "%s" \
                 AND UserRequest.status NOT IN (%s)' % (agent, excluded_states) 
        return self.get('UserRequest', query)

    def update_request(self, ref, field, value):
        resp = self.itop.update('UserRequest', key='ref', key_value=ref, status=value)
        print resp
        return resp

