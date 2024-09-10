tokens = {
    "(": "PLEFT",
    ")": "PRIGHT",
    "{": "CLEFT",
    "}": "CRIGHT",
    "+": "ADD",
    "-": "SUB",
    "*": "MULT",
    "/": "DIV",
    ",": "COMMA",
    ";": "SEMICOLON",
    "num": "NUM"
}

reservedWords = {
    "program": "PROGRAM",
    "end": "END",
    "func": "FUNC",
    "proc": "PROC",
    "call": "CALL",
    "int": "INT",
    "bool": "BOOL",
    "True": "BOOLEAN",
    "False": "BOOLEAN",
    "return": "RETURN",
    "if": "IF",
    "endif": "ENDIF",
    "else": "ELSE",
    "endelse": "ENDELSE",
    "while": "WHILE",
    "endwhile": "ENDWHILE",
    "print": "PRINT",
    "break": "BREAK",
    "continue": "CONTINUE",
}

def arvoreExpressao(lista):
    if(lista == None or len(lista) == 0):
        return []
    else:
        listaPrimeiro = lista[0]
        if (len(lista) == 1):
            return [listaPrimeiro]

        listaSegundo = lista[1]
        listaTerceiro = arvoreExpressao(lista[2:])
        return ([listaPrimeiro] + [listaSegundo] + [listaTerceiro])


def expressaoTresEnderecos(lista):
    listaTresEnd = []

    if(lista == None or len(lista) == 0):
        return listaTresEnd

    primeiraVariavel = lista[0]
    if (len(lista) == 1):
        listaTresEnd.append(('mov', 'temp', primeiraVariavel))

    else:
        operacao = lista[1]
        resto = expressaoTresEnderecos(lista[2])
        listaTresEnd.extend(resto)

        if(operacao == "+"):
            listaTresEnd.append(('add', 'temp', primeiraVariavel))

        if(operacao == "*"):
            listaTresEnd.append(('mul', 'temp', primeiraVariavel))

    return listaTresEnd
