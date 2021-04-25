import pytest, unittest, json, configparser, jwt
from passenger_wsgi import app as flask_app

config = configparser.ConfigParser()
config.read('../config.ini')

class PassengerWSGITest(unittest.TestCase):

    def setUp(self):
        flask_app.config['global_config'] = config
        self.client = flask_app.test_client()

    def test_auth(self):
        post_data = {
            'username': 'unittest@test.ccatchings.com',
            'password': 'blahrandompw'
        }
        res = self.client.post("/auth", data=json.dumps(post_data), content_type="application/json")
        split_token = res.data[1:-1]
        decode_jwt = jwt.decode(split_token, 'andyollie', algorithms=['HS256'])
        self.assertEqual(200, res.status_code)
        self.assertEqual('Unit', decode_jwt['firstname'])


