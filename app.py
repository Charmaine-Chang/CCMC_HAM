import os
from CCMC_HAM import create_app

app = create_app()


if __name__ == '__main__':
    debug = os.environ.get('FLASK_DEBUG', '1') == '1'
    port = int(os.environ.get('FLASK_RUN_PORT', '5000'))
    app.run(debug=debug, host='0.0.0.0', port=port)