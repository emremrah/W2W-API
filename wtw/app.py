from flask import Flask

from . import __version__

app = Flask(__name__)


@app.route('/', methods=['GET'])
def default():
    return {'version': __version__}


if __name__ == '__main__':
    app.run(port=41000)
