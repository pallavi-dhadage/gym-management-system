import os
from app import create_app, db

app = create_app()


@app.shell_context_processor
def make_shell_context():
    return {'db': db}


if __name__ == '__main__':
    host = os.environ.get('HOST', '127.0.0.1')
    port = int(os.environ.get('PORT', 5000))
    app.logger.info('Starting dev server on %s:%s', host, port)
    app.run(host=host, port=port, debug=True)