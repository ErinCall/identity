#! /usr/bin/env python

import bcrypt
import getpass

passphrase = getpass.getpass("Enter a passphrase to bcrypt: ")

hashed = bcrypt.hashpw(passphrase, bcrypt.gensalt())

print "Your bcrypted digest:"
print hashed
