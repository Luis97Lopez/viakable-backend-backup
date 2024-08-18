from passlib.hash import bcrypt


def get_hash_password(password):
    hashed_password = bcrypt.hash(password)
    return hashed_password


def verify_password(plain_password, hashed_password):
    return bcrypt.verify(plain_password, hashed_password)
