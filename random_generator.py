import random
import string
import secrets
number=32

def GenerateString():
    result_string="".join(secrets.choice(string.ascii_lowercase + string.digits)for i in range(number))
    return result_string
