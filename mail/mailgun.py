import requests


class MailGun:
    base_uri = 'https://api.mailgun.net/v3/'

    def send(self, key, domain, _from, to, subject, html, cc=None, bcc=None):
        return requests.post(
            self.base_uri + domain + '/' + 'messages',
            auth=('api', key),
            data={'from': _from, 'to': to, 'o:require-tls': True, 'o:skip-verification': True,
                  'cc': cc, 'bcc': bcc, 'subject': subject, 'html': html})

    def receive(self, key):
        auth = ('api', key)
        return requests.get(self.base_uri + 'domains/' + 'hiren.tk' + '/messages/'+ 'eyJwIjogZmFsc2UsICJrIjogIjVkYjA1ZDU4LWY0NTktNGEzYy1iODExLWUwN2Y4OWJiNDUxYiIsICJzIjogIjc5YzhiNzE1YzAiLCAiYyI6ICJ0YW5rczEifQ==', auth=auth)
        #return requests.get(self.base_uri + 'hiren.tk' + '/events', auth=auth)
        #return requests.get(, auth=auth)


x = MailGun()
# y = x.send('hiren.tk', 'key-8ra439mbgjyhazix8qj6ba3t5qvmuit4', 'hiren@hiren.tk', 'areose21@gmail.com', 'Hello nisha', '<h1>:D</h1>', 'areose21@gmail.com', 'areose21@gmail.com')
y = x.receive('key-8ra439mbgjyhazix8qj6ba3t5qvmuit4')
print(y.url)
print(y.status_code)  # "event": "stored"
#for i in y.json()['items']:
#    if i['event'] == 'stored':
#        print(i)
print(y.json())