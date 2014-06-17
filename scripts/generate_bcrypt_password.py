#! /usr/bin/env python

import bcrypt
import getpass

def main():
    passwonce = getpass.getpass("Enter a passphrase to bcrypt: ")
    passtwice = getpass.getpass("Do it again, just to be safe: ")

    if passwonce == passtwice:

        hashed = bcrypt.hashpw(passwonce, bcrypt.gensalt())

        print "Your bcrypted digest:"
        print hashed
    else:
        print "They didn't match. Try again! No typos this time!"
        main()

if __name__ == '__main__':
    main()
