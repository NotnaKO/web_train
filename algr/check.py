from string import printable, ascii_letters, digits
from .user_alg import get_user_by_email, AuthError
from flask import jsonify


class PasswordError(Exception):
    pass


class EmailError(Exception):
    pass


class LengthError(PasswordError):
    pass


class LetterError(PasswordError, EmailError):
    pass


class DigitError(PasswordError):
    pass


class SequenceError(PasswordError):
    pass


class LanguageError(PasswordError):
    pass


class EnglishError(EmailError):
    pass


class OthersLettersError(EmailError):
    pass


class SimilarUserError(EmailError):
    pass


class NotEqualError(PasswordError):
    pass


class AgeError(Exception):
    pass


class ValueAgeError(AgeError):
    pass


class AgeRangeError(AgeError):
    pass


def hard_check_password(password):
    b = False
    c = True
    z = '1234567890'
    al = "qwertyuiop+asdfghjkl;'+zxcvbnm,./".split('+')
    n = password
    se = set(password)
    if len(n) < 8:
        raise LengthError
    if n.lower() == n or n.upper() == n:
        raise LetterError
    if not (se <= set(printable)):
        raise LanguageError
    for i in se:
        if i in z:
            b = True
            break
    if not b:
        raise DigitError
    for j in al:
        if not c:
            break
        for i in range(0, len(n) - 2, 1):
            if (n[i] + n[i + 1] + n[i + 2]).lower() in j:
                raise SequenceError
    return 'ok'


def check_email(email):
    s = set(email)
    if not (s <= set(printable)):
        raise LetterError
    le, ot = False, False
    for i in s:
        if i in ascii_letters:
            le = True
        if i in printable and i not in digits and i not in ascii_letters:
            ot = True
        if le and ot:
            break
    if not le or not ot:
        if not le:
            raise EnglishError
        if not ot:
            raise OthersLettersError
    try:
        get_user_by_email(email)
    except AuthError:
        pass
    else:
        raise SimilarUserError


def age_check(age):
    try:
        age = int(age)
    except ValueError or TypeError:
        raise ValueAgeError
    if age < 6 or age > 110:
        raise AgeRangeError


def decode_password_check(password):
    try:
        le = hard_check_password(password)
        if le != 'ok':
            raise PasswordError
        else:
            return True
    except PasswordError as e:
        if type(e) == LetterError:
            return jsonify({'error': 'PasswordLetterError'})
        elif type(e) == LengthError:
            return jsonify({'error': 'LengthError'})
        elif type(e) == LanguageError:
            return jsonify({'error': 'LanguageError'})
        elif type(e) == DigitError:
            return jsonify({'error': 'DigitError'})
        elif type(e) == SequenceError:
            return jsonify({'error': 'SequenceError'})


def full_decode_errors(args):
    p = decode_password_check(args['password'])
    if p is not True:
        return p
    # age check
    try:
        age_check(args['age'])
    except ValueAgeError:
        return jsonify({'error': 'ValueAgeError'})
    except AgeRangeError:
        return jsonify({'error': 'AgeRangeError'})
    # email check
    try:
        check_email(args['email'])
    except LetterError:
        return jsonify({'error': 'EmailLetterError'})
    except EnglishError:
        return jsonify({'error': 'EnglishError'})
    except OthersLettersError:
        return jsonify({'error': 'OthersLettersError'})
    except SimilarUserError:
        return jsonify({'error': 'SimilarUserError'})
    return True


def some_decode_errors(args):
    a = full_decode_errors(args)
    if a is True:
        return a
    elif a.json['error'] == 'SimilarUserError':
        return True
    else:
        return a


def make_new_password(old, new, again, user):
    if new != again:
        raise NotEqualError
    if user.check_password(old):
        p = decode_password_check(new)
        return p
    else:
        raise AuthError
