import os
from vagrantControl import app


def runserver():
    port = int(os.environ.get('PORT', 6000))
    app.run(host='127.0.0.1', port=port, threaded=True)


if __name__ == '__main__':
    runserver()
