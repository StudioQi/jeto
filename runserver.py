import os
from jeto import app, socketio


def runserver():
    port = int(os.environ.get('PORT', 8080))
    socketio.run(app, port=port)


if __name__ == '__main__':
    runserver()
