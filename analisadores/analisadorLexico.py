from analisadores.token import Token
from analisadores.utils import tokens
from analisadores.utils import tokensPalavrasReservadas

class AnalisadorLexico:
    def __init__(self, programa):
        self.inicio = 0
        self.atual = 0
        self.linha = 1
        self.tokens = []
        self.programa = programa
    
    # Chama o buscador de Tokens, adiciona o fim do arquivo (Token END),
    # chama o buscador de token de palavras reservadas
    def analisar(self):
        self.analisarTokens()
        self.analisarPalavrasReservadas()
        return self.tokens
    
    # Varre o código tentando identificar os lexemas
    def analisarTokens(self):
        while self.atual < len(self.programa):
            self.inicio = self.atual
            char = self.nextChar()

            # Verificiar espaços em branco, quebras de linhas e afins
            if char == " " or char == "\t" or char == "\r":
                pass

            elif char == "\n":
                self.linha += 1

            # Verificar se são tokens delimitadores ("(", ")", "{", "}")
            elif char == "(" or char == ")" or char == "{" or char == "}":
                self.tokens.append(
                    Token(
                        tokens[char],
                        self.programa[self.inicio : self.atual],
                        self.linha,
                    )
                )

            # Verificar se são tokens de operações aritméticas ("+", "-", "*", "/")
            elif char == "+" or char == "-" or char == "*" or char == "/":
                self.tokens.append(
                    Token(
                        tokens[char],
                        self.programa[self.inicio : self.atual],
                        self.linha,
                    )
                )

            # Verificar se são tokens de operações booleanas ("=". "==", "!=", ">", "<", ">=", "<=")
            elif char == "=" or char == "!" or char == "<" or char == ">":
                self.tokens.append(
                    Token(
                        self.opBolleanaToken(char),
                        self.programa[self.inicio : self.atual],
                        self.linha,
                    )
                )

            # Separador
            elif char == ",":  # Virgula
                self.tokens.append(
                    Token(
                        tokens[char],
                        self.programa[self.inicio : self.atual],
                        self.linha
                    )
                )

            # Demarcador de fim de bloco / expressão
            elif char == ";":  # Ponto e virgula
                self.tokens.append(
                    Token(
                        tokens[char],
                        self.programa[self.inicio : self.atual],
                        self.linha
                    )
                )

            # Números
            elif char >= "0" and char <= "9":
                while self.lookAhead() >= "0" and self.lookAhead() <= "9":
                    self.nextChar()

                self.tokens.append(
                    Token(
                        tokens["num"],
                        self.programa[self.inicio : self.atual],
                        self.linha
                    )
                )

            # Strings
            elif char == '"' or char == "'":
                delimitador = char
                while self.lookAhead() != delimitador and self.lookAhead() != "\0":
                    if self.lookAhead() == "\\":
                        self.nextChar()
                    self.nextChar()
                if self.lookAhead() == delimitador:
                    self.nextChar()
                    self.tokens.append(
                        Token(
                            tokens["string_lex"],
                            self.programa[self.inicio:self.atual],
                            self.linha
                        )
                    )
                else:
                    raise Exception(f"String inválida na linha {self.linha}")


            # Variáveis / Funções e procedimentos 
            elif char == "v" or char == "f" or char == "p":
                tipoIdentificar = tokens[char]

                if not self.lookAhead().isalpha():
                    raise Exception(f"Invalid character: in line {self.linha}")

                while self.lookAhead().isalnum():
                    self.nextChar()

                self.tokens.append(
                    Token(
                        tipoIdentificar,
                        self.programa[self.inicio : self.atual],
                        self.linha
                    )
                )

            # Palavras Reservadas
            # isalpha verifica se existem apenas letras
            elif char.isalpha():
                while self.lookAhead().isalnum():
                    self.nextChar()

                self.tokens.append(
                    Token(
                        tokens["id"],
                        self.programa[self.inicio : self.atual],
                        self.linha
                    )
                )

            # Outros/Error
            else:
                print("Caractere inválido na linha ", self.linha)
                exit(2)


    # Busca caracteres, passa para o próximo char (atual é o char a frente do que tá sendo lido)
    def nextChar(self):
        self.atual += 1
        return self.programa[self.atual - 1]


    # Verifica o simbolo a frente e se está no final do programa
    def lookAhead(self):
        if self.atual < len(self.programa):
            return self.programa[self.atual]
        else:
            return "\0"


    # Verifica que tipo de operação booleana se trata
    def opBolleanaToken(self, char):
        # Operações Booleanas
        if char == "=":  # Igual ou Atribuição
            if self.lookAhead() == "=":  # == (comparação)
                self.atual += 1
                return "EQUAL"

            else:  # = (atribuição)
                return "ATB"

        elif char == "!":  # Diferente ("!=")
            if self.lookAhead() == "=":
                self.atual += 1
                return "DIFF"

        elif char == "<":  # Menor ou igual, menor
            if self.lookAhead() == "=":  # ("<= ")
                self.atual += 1
                return "LESSEQUAL"

            else:  # ("<")
                return "LESS"

        elif char == ">":  # Maior ou igual, Maior
            if self.lookAhead() == "=":  # (">=")
                self.atual += 1
                return "GREATEREQUAL"
            else:  # (">")
                return "GREATER"
    

    # Varre o código tentando identificar palavras reservadas
    def analisarPalavrasReservadas(self):
        for i in self.tokens:
            if i.tipo == "ID" or i.tipo == "VAR_ID" or i.tipo == "FUNC_ID" or i.tipo == "PROC_ID":
                # Inicio do programa
                if i.lexema == "program":
                    i.tipo = tokensPalavrasReservadas[i.lexema]

                # Fim do programa
                elif i.lexema == "end":
                    i.tipo = tokensPalavrasReservadas[i.lexema]

                # Identificador de função
                elif i.lexema == "func":
                    i.tipo = tokensPalavrasReservadas[i.lexema]

                # Identificador de procedimento
                elif i.lexema == "proc":
                    i.tipo = tokensPalavrasReservadas[i.lexema]

                # Identificador de chamada para proc e func
                elif i.lexema == "call":
                    i.tipo = tokensPalavrasReservadas[i.lexema]

                # Identificador de inteiros
                elif i.lexema == "int":
                    i.tipo = tokensPalavrasReservadas[i.lexema]

                # Tipo Booleano
                elif i.lexema == "boolean":
                    i.tipo = tokensPalavrasReservadas[i.lexema]

                # Booleano Verdadeiro
                elif i.lexema == "true":
                    i.tipo = tokensPalavrasReservadas[i.lexema]

                # Booleano Falso
                elif i.lexema == "false":
                    i.tipo = tokensPalavrasReservadas[i.lexema]

                # Retorno da função
                elif i.lexema == "return":
                    i.tipo = tokensPalavrasReservadas[i.lexema]

                # Condicional IF
                elif i.lexema == "if":
                    i.tipo = tokensPalavrasReservadas[i.lexema]

                # Identificador de fim do IF
                elif i.lexema == "endif":
                    i.tipo = tokensPalavrasReservadas[i.lexema]

                # Condicional ELSE
                elif i.lexema == "else":
                    i.tipo = tokensPalavrasReservadas[i.lexema]

                # Identificador de fim do ELSE
                elif i.lexema == "endelse":
                    i.tipo = tokensPalavrasReservadas[i.lexema]

                # Condicional WHILE
                elif i.lexema == "while":
                    i.tipo = tokensPalavrasReservadas[i.lexema]

                # Identificador de fim do WHILE
                elif i.lexema == "endwhile":
                    i.tipo = tokensPalavrasReservadas[i.lexema]

                # Escrita na tela
                elif i.lexema == "print":
                    i.tipo = tokensPalavrasReservadas[i.lexema]

                # Incondicional BREAK
                elif i.lexema == "break":
                    i.tipo = tokensPalavrasReservadas[i.lexema]

                # Incondicional CONTINUE
                elif i.lexema == "continue":
                    i.tipo = tokensPalavrasReservadas[i.lexema]


    def getToken(self):
        return self.tokens


    def getPrograma(self):
        return self.programa



