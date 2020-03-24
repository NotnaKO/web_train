from string import printable


class PasswordError(Exception):
    pass


class LengthError(PasswordError):
    pass


class LetterError(PasswordError):
    pass


class DigitError(PasswordError):
    pass


class SequenceError(PasswordError):
    pass


class LanguageError(PasswordError):
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
