# Identity

This is a simple Flask app that provides an OpenID server for a single user.

## Configuration

You'll want to edit `identity/config.yml` to reflect the information about yourself.

For `password_digest`, you can generate a bcrypted password digest by running `scripts/generate_bcrypt_password.py`.

If you want to receive emails about unexpected errors, define an `error_emails` association with an SMTP host, sender address, and list of recipient addresses. If your SMTP host requires authentication, your credentials should be in environment variables, as described below.

## Running the server

You can launch the server directly or by using [Gunicorn](http://gunicorn.org/):

```
python identity/app.py
```

```
gunicorn identity.app:app -b 0.0.0.0:$PORT -w 3
```

Either way, the server relies on several environment variables:

* `PORT` - The network port on which the server should listen
* `SESSION_KEY` - A key to be used for encrypting and decrypting session data. Keep it secret. Keep it safe.
* `SERVER_NAME` - The protocol and host on which the server is running (e.g. https://identity.yourname.info)

Additionally, if you've configured error emails using an SMTP host that requires authentication, put your credentials in the `EMAIL_USERNAME` and `EMAIL_PASSWORD` environment variables.