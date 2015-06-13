import os
from jeto import app


def runserver():
    port = int(os.environ.get('PORT', 6000))
    app.run(host='0.0.0.0', port=port, threaded=True, debug=True)


if __name__ == '__main__':
    runserver()
