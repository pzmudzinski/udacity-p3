__author__ = 'piotr'
# Run a test server.
from app import app

app.run(host='0.0.0.0', debug=True)