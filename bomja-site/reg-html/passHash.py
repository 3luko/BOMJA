from flask_bcrypt import Bcrypt

bcrypt = Bcrypt()

password = "bomja123"

hash = bcrypt.generate_password_hash(password).decode("utf-8")

print(hash)
print(bcrypt.check_password_hash(hash, password))
