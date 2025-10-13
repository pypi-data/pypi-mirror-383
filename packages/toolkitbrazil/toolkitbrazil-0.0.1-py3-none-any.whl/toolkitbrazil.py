import random
import re

_uf_cpf = {
    0: ['RS'],
    1: ['DF', 'GO', 'MS', 'MT', 'TO'],
    2: ['AC', 'AM', 'AP', 'PA', 'RO', 'RR'],
    3: ['CE', 'MA', 'PI'],
    4: ['AL', 'PB', 'PE', 'RN'],
    5: ['BA', 'SE'],
    6: ['MG'],
    7: ['ES', 'RJ'],
    8: ['SP'],
    9: ['PR', 'SC']
}

_uf_ddd = {
    'AC': [68],
    'AL': [82],
    'AP': [96],
    'AM': [92, 97],
    'BA': [71, 73, 74, 75, 77],
    'CE': [85, 88],
    'DF': [61],
    'ES': [27, 28],
    'GO': [61, 62, 64],
    'MA': [98, 99],
    'MT': [65, 66],
    'MS': [67],
    'MG': [31, 32, 33, 34, 35, 37, 38],
    'PA': [91, 93, 94],
    'PB': [83],
    'PR': [41, 42, 43, 44, 45, 46],
    'PE': [81, 87],
    'PI': [86, 89],
    'RJ': [21, 22, 24],
    'RN': [84],
    'RS': [51, 53, 54, 55],
    'RO': [69],
    'RR': [95],
    'SC': [47, 48, 49],
    'SP': [11, 12, 13, 14, 15, 16, 17, 18, 19],
    'SE': [79],
    'TO': [63]
}

_uf_capitais = {
    'AC': 'RIO BRANCO',
    'AL': 'MACEIO',
    'AP': 'MACAPA',
    'AM': 'MANAUS',
    'BA': 'SALVADOR',
    'CE': 'FORTALEZA',
    'DF': 'BRASILIA',
    'ES': 'VITORIA',
    'GO': 'GOIANIA',
    'MA': 'SAO LUIS',
    'MT': 'CUIABA',
    'MS': 'CAMPO GRANDE',
    'MG': 'BELO HORIZONTE',
    'PA': 'BELEM',
    'PB': 'JOAO PESSOA',
    'PR': 'CURITIBA',
    'PE': 'RECIFE',
    'PI': 'TERESINA',
    'RJ': 'RIO DE JANEIRO',
    'RN': 'NATAL',
    'RS': 'PORTO ALEGRE',
    'RO': 'PORTO VELHO',
    'RR': 'BOA VISTA',
    'SC': 'FLORIANOPOLIS',
    'SP': 'SAO PAULO',
    'SE': 'ARACAJU',
    'TO': 'PALMAS'
}

_cmap = {
    'Á': 'A', 'À': 'A', 'Â': 'A', 'Ã': 'A', 'Ä': 'A',
    'É': 'E', 'È': 'E', 'Ê': 'E', 'Ë': 'E',
    'Í': 'I', 'Ì': 'I', 'Î': 'I', 'Ï': 'I',
    'Ó': 'O', 'Ò': 'O', 'Ô': 'O', 'Õ': 'O', 'Ö': 'O',
    'Ú': 'U', 'Ù': 'U', 'Û': 'U', 'Ü': 'U',
    'Ç': 'C'
}


def strClean(txt: str) -> str:
    """
    Remove diacritics, non alpha chars, multiple spaces and convert string to upper case

    Parameters
    ----------
    txt : str
        String to be cleaned

    Returns
    -------
    str
        Returns string cleaned
    """
    txt = txt.upper()
    _s = ''
    for _c in txt:
        _s += _cmap.get(_c, _c)

    _r = "".join(
        _c for _c in _s
        if _c.isalpha() or _c == ' '
    )

    _r = ' '.join(_r.split())

    return _r


def rngCPF(uf: str = '') -> int:
    """
    Generate a random CPF

    Parameters
    ----------
    uf : str, optional
        Use a UF to generate a CPF for this region, by default ''

    Returns
    -------
    int
        Returns a random CPF
    """
    _cpf = [random.randrange(10) for _ in range(9)]

    _dig = None
    if uf != '':
        for k, l in _uf_cpf.items():
            if uf in l:
                _dig = k
                break

    if _dig is not None:
        _cpf[8] = _dig

    for _ in range(2):
        _v = sum([(len(_cpf) + 1 - i) * v for i, v in enumerate(_cpf)]) % 11
        _cpf.append(11 - _v if _v > 1 else 0)

    return int(''.join(str(x) for x in _cpf))


def valCPF(cpf: int) -> bool:
    """
    Validate a CPF

    Parameters
    ----------
    cpf : int
        CPF to be validated

    Returns
    -------
    bool
        Returns whether the CPF is valid or not
    """
    cpf = str(cpf)

    _cpfClean = re.sub(r'[^\d]', '', cpf).zfill(11)

    if not (4 <= len(_cpfClean) <= 11) or len(set(_cpfClean)) == 1:
        return False

    _c = [int(n) for n in _cpfClean[:9]]

    for _ in range(2):
        _v = sum([(len(_c) + 1 - i) * v for i, v in enumerate(_c)]) % 11
        _c.append(11 - _v if _v > 1 else 0)

    if _cpfClean == ''.join(map(str, _c)):
        return True
    else:
        return False


def rngCNPJ() -> int:
    """
    Generate a random CNPJ of the headquarters (branch 0001)

    Returns
    -------
    int
        Returns a random CNPJ (branch 0001)
    """
    _cnpj = [random.randrange(10) for _ in range(8)] + [0, 0, 0, 1]

    for _ in range(2):
        _v = sum(v * (i % 8 + 2) for i, v in enumerate(reversed(_cnpj)))
        _dig = 11 - _v % 11
        _cnpj.append(_dig if _dig < 10 else 0)

    return int(''.join(str(x) for x in _cnpj))


def rngCNPJfiliais() -> int:
    """
    Generate a random CNPJ of a branch (any branch)

    Returns
    -------
    int
        Returns a random CNPJ (any branch)
    """
    _cnpj = [random.randrange(10) for _ in range(12)]

    for _ in range(2):
        _v = sum(v * (i % 8 + 2) for i, v in enumerate(reversed(_cnpj)))
        _dig = 11 - _v % 11
        _cnpj.append(_dig if _dig < 10 else 0)

    return int(''.join(str(x) for x in _cnpj))


def valCNPJ(cnpj: int) -> bool:
    """
    Validate a CNPJ

    Parameters
    ----------
    cpf : int
        TCNPJ to be validated

    Returns
    -------
    bool
        Returns whether the CNPJ is valid or not
    """
    cnpj = str(cnpj)

    _cnpjClean = re.sub(r'[^\d]', '', cnpj).zfill(14)

    if not (7 <= len(_cnpjClean) <= 14) or len(set(_cnpjClean)) == 1:
        return False

    _c = [int(n) for n in _cnpjClean[:12]]

    for _ in range(2):
        _v = sum(v * (i % 8 + 2) for i, v in enumerate(reversed(_c)))
        _dig = 11 - _v % 11
        _c.append(_dig if _dig < 10 else 0)

    if _cnpjClean == ''.join(map(str, _c)):
        return True
    else:
        return False


def ufCPF(cpf: int) -> list[str]:
    """
    Check the UF of the CPF

    Parameters
    ----------
    cpf : int
        CPF to be checked

    Returns
    -------
    list[str]
        Returns a list of the UF to which this CPF may belong
    """
    cpf = str(cpf)

    _cpfClean = re.sub(r'[^\d]', '', cpf).zfill(11)

    if not (4 <= len(_cpfClean) <= 11) or len(set(_cpfClean)) == 1:
        return []

    _dig = int(_cpfClean[8])

    if _dig in _uf_cpf:
        return _uf_cpf[_dig]
    else:
        return []


def ufDDD(ddd: int) -> list:
    """
    Check the UF of the DDD

    Parameters
    ----------
    ddd : int
        DDD to be checked

    Returns
    -------
    list
        Returns a list of the UF to which this DDD may belong
    """
    ddd = str(ddd)

    _dddClean = re.sub(r'[^\d]', '', ddd)[:2]

    _u = []

    for k, l in _uf_ddd.items():
        if int(_dddClean) in l:
            _u.append(k)

    return _u


def ufCapital(uf: str) -> list[str]:
    """
    Check the capital of a UF

    Parameters
    ----------
    uf : str
        UF to be checked

    Returns
    -------
    list[str]
       Returns a list with capital and UF
    """
    _c = strClean(uf)
    _c = _c.upper().strip()

    if len(_c) != 2:
        return []

    for k, l in _uf_capitais.items():
        if _c == k:
            ll = []
            ll.append(l)
            ll.append(k)
            return ll

    return []


def valCPFuf(cpf: int, uf: str) -> bool:
    """
    Validate a CPF and check its UF

    Parameters
    ----------
    cpf : int
        CPF to be validated
    uf : str
        UF to be validated

    Returns
    -------
    bool
       Returns True if the CPF is valid and belongs to the informed UF
    """
    _c = strClean(uf)
    _c = _c.upper().strip()
    if valCPF(cpf):
        if _c in ufCPF(cpf):
            return True

    return False
