from __future__ import unicode_literals, absolute_import

import os
from identity import app

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0',
            port=port,
            debug=os.environ.get('DEBUG', False))
