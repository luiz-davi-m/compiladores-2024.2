from analisadores.utils import tokens, reservedWords


class AnalisadorSintatico:
    
    def __init__(self, tabelaDeTokens):
        self.tabelaDeTokens = tabelaDeTokens
        self.indexDaTabelaDeTokens = 0
        self.indexLookAhead = 0
        self.indexEscopoAtual = -1
        self.tabelaDeSimbolos = []
        # Pra saber na semantica qual declaracao de variavel no codigo tá sendo checada
        self.indexDaDeclaracaoDaVariavelAtual = -1
        self.indexEscopoAntesDaFuncao = 0


    def start(self):
        self.indexEscopoAtual += 1
        self.statement_list()  # Análise Sintática
        return
    
    
    def statement_list(self):
        if self.tokenAtual().tipo == "END":
            return
        else:
            self.statement()
            self.statement_list()
            return
        
    
    def statement(self):
        if self.tokenAtual().tipo == "PROGRAM":
            self.indexDaTabelaDeTokens += 1
            if self.tokenAtual().tipo == "CLEFT":
                self.indexDaTabelaDeTokens += 1

                while self.tokenAtual().tipo != "CRIGHT":
                    self.block_statement()

                if self.tokenAtual().tipo == "CRIGHT":
                    self.indexDaTabelaDeTokens += 1

                    if self.tokenAtual().tipo == "END":
                        print("\nFIM DA ANÁLISE SINTÁTICA - DEU CERTO :)\n")
                        # Deu certo
                    else:
                        raise Exception(
                            "Erro sintatico: falta do END na linha "
                            + str(self.tokenAtual().linha)
                        )
                else:
                    raise Exception(
                        "Erro sintatico: falta do CRIGHT na linha "
                        + str(self.tokenAtual().linha)
                    )
            else:
                raise Exception(
                    "Erro sintatico: falta do CLEFT na linha "
                    + str(self.tokenAtual().linha)
                )
        else:
            raise Exception(
                "Erro sintatico: Código fora do padrão na linha "
                + str(self.tokenAtual().linha)
            )


    def tokenAtual(self):
        return self.tabelaDeTokens[self.indexDaTabelaDeTokens]


    def block_statement(self):
        # ESCOPO OK
        # <declaration_var>
        if self.tokenAtual().tipo == "INT" or self.tokenAtual().tipo == "BOOL":
            temp = []
            temp.append(self.indexEscopoAtual)
            temp.append(self.tokenAtual().linha)
            temp.append(self.tokenAtual().tipo)
            self.declaration_var_statement(temp)
            return temp

        # ESCOPO OK
        # <declaration_func>
        if self.tokenAtual().tipo == "FUNC":
            # Ordem: [escopo, tipo, tipoDoRetorno, id, [[params], [params], [params]]]
            # Obs: Params pode ser >= 0
            temp = []
            temp.append(self.indexEscopoAtual) # salva em que escopo está
            temp.append(self.tokenAtual().linha) # linha
            # temp.append('FUNC')
            temp.append(self.tokenAtual().tipo) # tipo

            self.declaration_func_statement(temp)
            return temp

        # ESCOPO OK
        # <declaration_proc>
        if self.tokenAtual().tipo == "PROC":
            temp = []
            temp.append(self.indexEscopoAtual)
            temp.append(self.tokenAtual().linha)
            # temp.append('PROC')
            temp.append(self.tokenAtual().tipo)
            temp = self.declaration_proc_statement(temp)
            self.tabelaDeSimbolos.append(temp)

            return temp

        # ESCOPO OK
        # Chamadas de função e procedimentos
        if self.tokenAtual().tipo == "CALL":
            temp = []
            temp.append(self.indexEscopoAtual)
            temp.append(self.tokenAtual().linha)
            temp.append(self.tokenAtual().tipo)
            self.indexDaTabelaDeTokens += 1
            # <call_func>
            if self.tokenAtual().tipo == "FUNC":
                temp.append(self.tokenAtual().tipo)
                temp = self.call_func_statement(temp)
                if self.tokenAtual().tipo == "SEMICOLON":
                    self.indexDaTabelaDeTokens += 1
                    self.tabelaDeSimbolos.append(temp)
                    return temp
                else:
                    raise Exception(
                        "Erro sintatico: falta do ponto e virgula na linha "
                        + str(self.tokenAtual().linha)
                    )
            # <call_proc>
            elif self.tokenAtual().tipo == "PROC":
                temp.append(self.tokenAtual().tipo)
                temp = self.call_proc_statement(temp)
                # self.indexDaTabelaDeTokens += 1
                if self.tokenAtual().tipo == "SEMICOLON":
                    self.indexDaTabelaDeTokens += 1
                    self.tabelaDeSimbolos.append(temp)
                    return temp
                else:
                    raise Exception(
                        "aErro sintatico: falta do ponto e virgula na linha "
                        + str(self.tokenAtual().linha)
                    )

            else:
                raise Exception(
                    "Erro sintatico: falta de PROC ou FUNC"
                    + str(self.tokenAtual().linha)
                )

        # ESCOPO OK
        # <print_statement>
        if self.tokenAtual().tipo == "PRINT":
            temp = []
            temp.append(self.indexEscopoAtual)
            temp.append(self.tokenAtual().linha)
            temp.append(self.tokenAtual().tipo)
            self.print_statement(temp)
            return temp

        # ESCOPO ok
        # <if_statement>
        if self.tokenAtual().tipo == "IF":
            temp = []
            temp.append(self.indexEscopoAtual)
            temp.append(self.tokenAtual().linha)
            temp.append(self.tokenAtual().tipo)
            self.if_statement(temp)
            return temp

        # ESCOPO ok
        # <while_statement>
        if self.tokenAtual().tipo == "WHILE":
            temp = []
            temp.append(self.indexEscopoAtual)
            temp.append(self.tokenAtual().linha)
            temp.append(self.tokenAtual().tipo)
            self.while_statement(temp)
            return temp

        # ESCOPO OK
        # <identifier>
        if self.tokenAtual().tipo == "ID":
            temp = []
            temp.append(self.indexEscopoAtual)
            temp.append(self.tokenAtual().linha)
            temp.append(self.tokenAtual().tipo)
            temp.append(self.tokenAtual().lexema)
            self.call_var_statement(temp)
            return temp

        else:
            if self.tokenAtual().tipo in ["BREAK", "CONTINUE"]:
                raise Exception(f"Erro na linha: {self.tokenAtual().linha}, o tipo {self.tokenAtual().tipo} não é aceito neste bloco")
            else:
                return



    # block2 é o bloco que contém break/continue que só pode ser chamado dentro de um while
    def block2_statement(self):
        # ESCOPO OK
        # <declaration_var>
        if self.tokenAtual().tipo == "INT" or self.tokenAtual().tipo == "BOOL":
            temp = []
            temp.append(self.indexEscopoAtual)
            temp.append(self.tokenAtual().linha)
            temp.append(self.tokenAtual().tipo)
            self.declaration_var_statement(temp)
            return temp

        # ESCOPO OK
        # Chamadas de função e procedimentos
        if self.tokenAtual().tipo == "CALL":
            temp = []
            temp.append(self.indexEscopoAtual)
            temp.append(self.tokenAtual().linha)
            temp.append(self.tokenAtual().tipo)
            self.indexDaTabelaDeTokens += 1
            # <call_func>
            if self.tokenAtual().tipo == "FUNC":
                temp.append(self.tokenAtual().tipo)
                temp = self.call_func_statement(temp)
                if self.tokenAtual().tipo == "SEMICOLON":
                    self.tabelaDeSimbolos.append(temp)
                    self.indexDaTabelaDeTokens += 1
                    return temp
                else:
                    raise Exception(
                        "Erro sintatico: falta do ponto e virgula na linha "
                        + str(self.tokenAtual().linha)
                    )
            # <call_proc>
            elif self.tokenAtual().tipo == "PROC":
                temp.append(self.tokenAtual().tipo)
                temp = self.call_proc_statement(temp)
                # self.indexDaTabelaDeTokens += 1
                if self.tokenAtual().tipo == "SEMICOLON":
                    self.tabelaDeSimbolos.append(temp)
                    self.indexDaTabelaDeTokens += 1
                    return temp
                else:
                    raise Exception(
                        "Erro sintatico: falta do ponto e virgula na linha "
                        + str(self.tokenAtual().linha)
                    )
            else:
                raise Exception(
                    "Erro sintatico: falta de PROC ou FUNC"
                    + str(self.tokenAtual().linha)
                )

        # ESCOPO OK
        # <print_statement>
        if self.tokenAtual().tipo == "PRINT":
            temp = []
            temp.append(self.indexEscopoAtual)
            temp.append(self.tokenAtual().linha)
            temp.append(self.tokenAtual().tipo)
            self.print_statement(temp)
            return temp

        # ESCOPO OK
        # <if_statement>
        if self.tokenAtual().tipo == "IF":
            temp = []
            temp.append(self.indexEscopoAtual)
            temp.append(self.tokenAtual().linha)
            temp.append(self.tokenAtual().tipo)
            self.if_statement2(temp)
            return temp

        # Tratamento de erro ELSE
        if self.tokenAtual().tipo == "ELSE":
            raise Exception(
                "Erro sintatico: ELSE adicionado de maneira incorreta "
                + str(self.tokenAtual().linha)
            )

        # ESCOPO OK
        # <while_statement>
        if self.tokenAtual().tipo == "WHILE":
            temp = []
            temp.append(self.indexEscopoAtual)
            temp.append(self.tokenAtual().linha)
            temp.append(self.tokenAtual().tipo)
            self.while_statement(temp)
            return temp

        # ESCOPO OK
        # <identifier>
        if self.tokenAtual().tipo == "ID":
            temp = []
            temp.append(self.indexEscopoAtual)
            temp.append(self.tokenAtual().linha)
            temp.append(self.tokenAtual().tipo)
            temp.append(self.tokenAtual().lexema)
            self.call_var_statement(temp)
            return temp

        # ESCOPO OK
        # <unconditional_branch>
        if self.tokenAtual().tipo == "BREAK" or self.tokenAtual().tipo == "CONTINUE":
            temp = []
            temp.append(self.indexEscopoAtual)
            temp.append(self.tokenAtual().linha)
            temp.append(self.tokenAtual().tipo)
            self.unconditional_branch_statement()
            return temp

        else:
            raise Exception(
                "Erro sintatico: bloco vazio na linha " +
                str(self.tokenAtual().linha)
            )

    # block3 é o bloco do if/else, que não pode declarar função e procedimento dentro
    def block3_statement(self):
        # ESCOPO OK
        # <declaration_var>
        if self.tokenAtual().tipo == "INT" or self.tokenAtual().tipo == "BOOL":
            temp = []
            temp.append(self.indexEscopoAtual)
            temp.append(self.tokenAtual().linha)
            temp.append(self.tokenAtual().tipo)
            self.declaration_var_statement(temp)
            return temp

        # ESCOPO OK
        # Chamadas de função e procedimentos
        if self.tokenAtual().tipo == "CALL":
            temp = []
            temp.append(self.indexEscopoAtual)
            temp.append(self.tokenAtual().linha)
            temp.append(self.tokenAtual().tipo)
            self.indexDaTabelaDeTokens += 1
            # <call_func>
            if self.tokenAtual().tipo == "FUNC":
                temp.append(self.tokenAtual().tipo)
                temp = self.call_func_statement(temp)
                if self.tokenAtual().tipo == "SEMICOLON":
                    self.tabelaDeSimbolos.append(temp)
                    self.indexDaTabelaDeTokens += 1
                    return temp
                else:
                    raise Exception(
                        "Erro sintatico: falta do ponto e virgula na linha "
                        + str(self.tokenAtual().linha)
                    )
            # <call_proc>
            elif self.tokenAtual().tipo == "PROC":
                temp.append(self.tokenAtual().tipo)
                temp = self.call_proc_statement(temp)
                # self.indexDaTabelaDeTokens += 1
                if self.tokenAtual().tipo == "SEMICOLON":
                    self.tabelaDeSimbolos.append(temp)
                    self.indexDaTabelaDeTokens += 1
                    return temp
                else:
                    raise Exception(
                        "Erro sintatico: falta do ponto e virgula na linha "
                        + str(self.tokenAtual().linha)
                    )
            else:
                raise Exception(
                    "Erro sintatico: falta de PROC ou FUNC"
                    + str(self.tokenAtual().linha)
                )

        # ESCOPO OK
        # <print_statement>
        if self.tokenAtual().tipo == "PRINT":
            temp = []
            temp.append(self.indexEscopoAtual)
            temp.append(self.tokenAtual().linha)
            temp.append(self.tokenAtual().tipo)
            self.print_statement(temp)
            return temp

        # ESCOPO Ok
        # <if_statement>
        if self.tokenAtual().tipo == "IF":
            temp = []
            temp.append(self.indexEscopoAtual)
            temp.append(self.tokenAtual().linha)
            temp.append(self.tokenAtual().tipo)
            self.if_statement(temp)
            return temp

        # Tratamento de erro ELSE
        if self.tokenAtual().tipo == "ELSE":
            raise Exception(
                "Erro sintatico: ELSE adicionado de maneira incorreta "
                + str(self.tokenAtual().linha)
            )

        # ESCOPO OK
        # <while_statement>
        if self.tokenAtual().tipo == "WHILE":
            temp = []
            temp.append(self.indexEscopoAtual)
            temp.append(self.tokenAtual().linha)
            temp.append(self.tokenAtual().tipo)
            self.while_statement(temp)
            return temp

        # ESCOPO OK
        # <identifier>
        if self.tokenAtual().tipo == "ID":
            temp = []
            temp.append(self.indexEscopoAtual)
            temp.append(self.tokenAtual().linha)
            temp.append(self.tokenAtual().tipo)
            temp.append(self.tokenAtual().lexema)
            self.call_var_statement(temp)
            return temp

        else:
            raise Exception(
                "Erro sintatico: bloco vazio na linha " +
                str(self.tokenAtual().linha)
            )

    # ESCOPO OK
    # <declaration_var> OK
    def declaration_var_statement(self, temp):
        self.indexDaTabelaDeTokens += 1
        if self.tokenAtual().tipo == "ID":
            temp.append(self.tokenAtual().lexema)
            self.indexDaTabelaDeTokens += 1
            if self.tokenAtual().tipo == "ATB":  # atribuicao
                temp.append(self.tokenAtual().lexema)
                self.indexDaTabelaDeTokens += 1
                tempEndVar = []
                # o que tem dentro da variavel
                self.end_var_statement(tempEndVar)
                temp.append(tempEndVar)

                if self.tokenAtual().tipo == "SEMICOLON":
                    self.indexDaTabelaDeTokens += 1
                    self.tabelaDeSimbolos.append(temp)
                else:
                    raise Exception(
                        "Erro sintatico: falta do ponto e virgula na linha "
                        + str(self.tokenAtual().linha)
                    )
            else:
                raise Exception(
                    "Erro sintatico: falta da atribuição na linha "
                    + str(self.tokenAtual().linha)
                )
        else:
            raise Exception(
                "Erro sintatico: falta do ID na linha " +
                str(self.tokenAtual().linha)
            )

    # ESCOPO OK
    # <end_var> OK
    def end_var_statement(self, tempEndVar):
        #  <call_func>
        if self.tokenAtual().tipo == "CALL":
            tempEndVar.append(self.tokenAtual().tipo)
            self.indexDaTabelaDeTokens += 1
            # <call_func>
            if self.tokenAtual().tipo == "FUNC":
                tempEndVar.append(self.tokenAtual().tipo)
                self.call_func_statement(tempEndVar)
                return
            else:
                raise Exception(
                    "Erro sintatico: chamada de função erroneamente na linha "
                    + str(self.tokenAtual().linha)
                )

        # <boolean>
        if self.tokenAtual().tipo == "BOOLEAN":

            if (
                self.tokenAtual().lexema == "True"
                or self.tokenAtual().lexema == "False"
            ):
                tempEndVar.append(self.tokenAtual().lexema)
                self.indexDaTabelaDeTokens += 1
                return
            else:
                raise Exception(
                    "Erro sintatico: boolean atribuido erroneamente na linha "
                    + str(self.tokenAtual().linha)
                )
        # <num>
        if self.tokenAtual().tipo == "NUM":
            tempEndVar.append(self.tokenAtual().lexema)
            self.indexDaTabelaDeTokens += 1
            if (
                self.tokenAtual().tipo == "ADD"
                or self.tokenAtual().tipo == "SUB"
                or self.tokenAtual().tipo == "MULT"
                or self.tokenAtual().tipo == "DIV"
            ):
                tempEndVar.append(self.tokenAtual().lexema)
                self.call_op_statement(tempEndVar)
                return
            else:
                return

        # <identifier>
        if self.tokenAtual().tipo == "ID":
            tempEndVar.append(self.tokenAtual().lexema)
            self.indexDaTabelaDeTokens += 1
            # <call_op>
            if (
                self.tokenAtual().tipo == "ADD"
                or self.tokenAtual().tipo == "SUB"
                or self.tokenAtual().tipo == "MULT"
                or self.tokenAtual().tipo == "DIV"
            ):
                tempEndVar.append(self.tokenAtual().lexema)
                self.call_op_statement(tempEndVar)
                return
            else:
                return
        else:
            raise Exception(
                "Erro sintatico: atribuição de variavel erroneamente na linha "
                + str(self.tokenAtual().linha)
            )

    # ESCOPO OK
    # Chamada de variavel OK
    def call_var_statement(self, temp):
        self.indexDaTabelaDeTokens += 1
        if self.tokenAtual().tipo == "ATB":  # atribuicao
            temp.append(self.tokenAtual().lexema)
            self.indexDaTabelaDeTokens += 1
            if (
                (self.tokenAtual().tipo == "NUM")
                or (self.tokenAtual().tipo == "BOOLEAN")
                or (self.tokenAtual().tipo == "ID")
            ):
                temp.append(self.tokenAtual().lexema)
                self.indexDaTabelaDeTokens += 1
                if self.tokenAtual().tipo == "SEMICOLON":
                    self.indexDaTabelaDeTokens += 1
                    self.tabelaDeSimbolos.append(temp)
                else:
                    raise Exception(
                        "Erro sintatico: falta do ponto e vírgula na linha "
                        + str(self.tokenAtual().linha)
                    )
            else:
                raise Exception(
                    "Erro sintatico: variável não atribuída na linha "
                    + str(self.tokenAtual().linha)
                )
        else:
            raise Exception(
                "Erro sintatico: símbolo de atribuição não encontrado na linha "
                + str(self.tokenAtual().linha)
            )

    # ESCOPO OK
    # <declaration_func> OK
    def declaration_func_statement(self, temp):
        self.indexDaTabelaDeTokens += 1
        if self.tokenAtual().tipo == "INT" or self.tokenAtual().tipo == "BOOL":  # tipo
            # Salvando o tipo do retorno
            temp.append(self.tokenAtual().tipo)
            self.indexDaTabelaDeTokens += 1
            # identificador
            if self.tokenAtual().tipo == "ID":
                functionLexema = self.tokenAtual().lexema
                # Salvando o id
                temp.append(self.tokenAtual().lexema)
                self.indexDaTabelaDeTokens += 1
                if self.tokenAtual().tipo == "PLEFT":
                    # (int a, bool b)
                    # [[params], [params]]
                    # [] -> lista do que tem dewntro dos parenteses do parametro
                    # [[escopo, int, a], [escopo, bool, var]]

                    tempParenteses = []
                    self.indexDaTabelaDeTokens += 1
                    if (
                        self.tokenAtual().tipo == "INT"
                        or self.tokenAtual().tipo == "BOOL"
                    ):
                        tempParentesesParamAtual = []
                        # Ordem dos params: [[escopo, tipo, id], [escopo, tipo, id]]
                        # Fazendo com que o escopo fique correto
                        tempParentesesParamAtual.append(
                            self.indexEscopoAtual + 1)

                        # Salvando o tipo do parametro atual
                        tempParentesesParamAtual.append(self.tokenAtual().tipo)

                        self.indexDaTabelaDeTokens += 1
                        if self.tokenAtual().tipo == "ID":
                            # Salvando o tipo do parametro atual
                            tempParentesesParamAtual.append(
                                self.tokenAtual().lexema)
                            # [escopo, int, a] -> antes
                            tempParenteses.append(tempParentesesParamAtual)
                            # [[escopo, int, a]] -> depois
                            self.indexDaTabelaDeTokens += 1
                            if self.tokenAtual().tipo == "COMMA":
                                # [[escopo, int, a]] -> antes
                                tempParenteses.append(
                                    self.params_statement(tempParenteses)
                                )
                                tempParenteses.pop()  # Remoção do None que fica ao fim
                                # [[escopo, int, a], i1, i2, i3 ... in]
                                temp.append(tempParenteses)
                                if self.tokenAtual().tipo == "PRIGHT":
                                    self.indexDaTabelaDeTokens += 1

                                    if self.tokenAtual().tipo == "CLEFT":
                                        # Armazendando o escopo antes de entrar na função
                                        self.indexEscopoAntesDaFuncao = (
                                            self.indexEscopoAtual
                                        )
                                        self.indexEscopoAtual += 1
                                        self.indexDaTabelaDeTokens += 1

                                        tempBlock = []
                                        # BLOCK
                                        while self.tokenAtual().tipo != "RETURN":
                                            if self.tokenAtual().tipo == "CRIGHT":
                                                raise Exception(f"Erro sintático: está faltando um returno na função {functionLexema}")
                                            
                                            tempBlock.append(
                                                self.block_statement())

                                        temp.append(tempBlock)
                                        tempReturn = []
                                        if self.tokenAtual().tipo == "RETURN":
                                            tempReturn.append(
                                                self.indexEscopoAtual)
                                            tempReturn.append(
                                                self.tokenAtual().tipo)
                                            # RETURN
                                            tempReturnParams = []
                                            tempReturnParams = self.return_statement(
                                                tempReturnParams
                                            )
                                            tempReturn.append(tempReturnParams)
                                            temp.append(tempReturn)
                                            if self.tokenAtual().tipo == "CRIGHT":
                                                # Retornando o valor do escopo antes de entrar na função
                                                self.indexEscopoAtual = (
                                                    self.indexEscopoAntesDaFuncao
                                                )
                                                self.indexDaTabelaDeTokens += 1

                                                if (
                                                    self.tokenAtual().tipo
                                                    == "SEMICOLON"
                                                ):
                                                    self.indexDaTabelaDeTokens += 1
                                                    # Adiciona na tabela de símbolos
                                                    self.tabelaDeSimbolos.append(temp)
                                                else:
                                                    raise Exception(
                                                        "Erro sintatico: falta do ponto e vírgula na linha "
                                                        + str(self.tokenAtual().linha)
                                                    )
                                            else:
                                                raise Exception(
                                                    "Erro sintatico: falta da chave direita na linha "
                                                    + str(self.tokenAtual().linha)
                                                )
                                        else:
                                            raise Exception(
                                                "Erro sintatico: falta do retorno na linha "
                                                + str(self.tokenAtual().linha)
                                            )

                                    else:
                                        raise Exception(
                                            "Erro sintatico: falta da chave esquerda na linha "
                                            + str(self.tokenAtual().linha)
                                        )
                                else:
                                    raise Exception(
                                        "Erro sintatico: falta do parentese direito na linha "
                                        + str(self.tokenAtual().linha)
                                    )

                            elif self.tokenAtual().tipo == "PRIGHT":

                                temp.append(tempParenteses)
                                if self.tokenAtual().tipo == "PRIGHT":
                                    self.indexDaTabelaDeTokens += 1
                                    if self.tokenAtual().tipo == "CLEFT":
                                        self.indexEscopoAntesDaFuncao = (
                                            self.indexEscopoAtual
                                        )
                                        self.indexEscopoAtual += 1
                                        self.indexDaTabelaDeTokens += 1
                                        tempBlock = []
                                        # BLOCK
                                        while self.tokenAtual().tipo != "RETURN":
                                            tempBlock.append(
                                                self.block_statement())

                                        temp.append(tempBlock)
                                        tempReturn = []
                                        # RETURN
                                        if self.tokenAtual().tipo == "RETURN":
                                            tempReturn.append(
                                                self.indexEscopoAtual)
                                            tempReturn.append(
                                                self.tokenAtual().tipo)
                                            # RETURN
                                            tempReturnParms = []
                                            tempReturnParms = self.return_statement(
                                                tempReturnParms
                                            )
                                            tempReturn.append(tempReturnParms)
                                            temp.append(tempReturn)
                                            if self.tokenAtual().tipo == "CRIGHT":
                                                self.indexEscopoAtual = (
                                                    self.indexEscopoAntesDaFuncao
                                                )
                                                self.indexDaTabelaDeTokens += 1
                                                if (
                                                    self.tokenAtual().tipo
                                                    == "SEMICOLON"
                                                ):
                                                    self.indexDaTabelaDeTokens += 1
                                                    # Adiciona na tabela de símbolos
                                                    self.tabelaDeSimbolos.append(
                                                        temp)
                                                else:
                                                    raise Exception(
                                                        "Erro sintatico: falta do ponto e vírgula na linha "
                                                        + str(self.tokenAtual().linha)
                                                    )
                                            else:
                                                raise Exception(
                                                    "Erro sintatico: falta da chave direita na linha "
                                                    + str(self.tokenAtual().linha)
                                                )
                                        else:
                                            raise Exception(
                                                "Erro sintatico: falta do retorno na linha "
                                                + str(self.tokenAtual().linha)
                                            )
                                    else:
                                        raise Exception(
                                            "Erro sintatico: falta da chave esquerda na linha "
                                            + str(self.tokenAtual().linha)
                                        )
                                else:
                                    raise Exception(
                                        "Erro sintatico: falta do parentese direito na linha "
                                        + str(self.tokenAtual().linha)
                                    )
                            else:
                                # TODO: (5 - falta descobrir) resolver exceção
                                raise Exception(
                                    "Erro sintatico: falta da virgula na linha "
                                    + str(self.tokenAtual().linha)
                                )
                        else:
                            raise Exception(
                                "Erro sintatico: falta o ID na linha "
                                + str(self.tokenAtual().linha)
                            )

                    else:
                        if self.tokenAtual().tipo == "PRIGHT":
                            temp.append(tempParenteses)
                            self.indexDaTabelaDeTokens += 1

                            exit(0)
                        else:
                            raise Exception(
                                "Erro sintatico: falta do parentese direito na linha "
                                + str(self.tokenAtual().linha)
                            )
                else:
                    raise Exception(
                        "Erro sintatico: falta do parentese esquerdo na linha "
                        + str(self.tokenAtual().linha)
                    )
            else:
                raise Exception(
                    "Erro sintatico: falta do ID na linha "
                    + str(self.tokenAtual().linha)
                )

    # ESCOPO OK
    # <return_statement> OK
    def return_statement(self, tempReturnParams):
        self.indexDaTabelaDeTokens += 1

        # Se for chamada de função
        if self.tokenAtual().tipo == "CALL":
            tempReturnParams.append(self.tokenAtual().tipo)
            self.indexDaTabelaDeTokens += 1
            if self.tokenAtual().tipo == "FUNC":
                tempReturnParams.append(self.tokenAtual().tipo)
                self.call_func_statement(tempReturnParams)
                self.indexDaTabelaDeTokens += 1
                return tempReturnParams
            else:
                raise Exception(
                    "Erro sintatico: Erro de chamada, só é permitido chamada de funções na linha "
                    + str(self.tokenAtual().linha)
                )

        # Se for chamada de variavel/num/bool
        if (
            (self.tokenAtual().tipo == "NUM")
            or (self.tokenAtual().tipo == "BOOLEAN")
            or (self.tokenAtual().tipo == "ID")
        ):
            tempReturnParams.append(self.tokenAtual().lexema)
            # TRES END
            self.tempTresEnderecos = tempReturnParams[0]
            self.indexDaTabelaDeTokens += 1
            if self.tokenAtual().tipo == "SEMICOLON":
                self.indexDaTabelaDeTokens += 1
                return tempReturnParams
            else:
                raise Exception(
                    "Erro sintatico: falta do ponto e virgula na linha "
                    + str(self.tokenAtual().linha)
                )
        else:
            raise Exception(
                "Erro sintatico: Retorno errado na linha "
                + str(self.tokenAtual().linha)
            )

    # ESCOPO OK
    # <params> OK
    def params_statement(self, tempParenteses):
        # [[escopo, int, a], adsfasd, asdasd]
        self.indexDaTabelaDeTokens += 1
        if self.tokenAtual().tipo == "INT" or self.tokenAtual().tipo == "BOOL":
            tempParentesesParamAtual = []
            tempParentesesParamAtual.append(self.indexEscopoAtual + 1)
            tempParentesesParamAtual.append(self.tokenAtual().tipo)
            self.indexDaTabelaDeTokens += 1
            if self.tokenAtual().tipo == "ID":
                tempParentesesParamAtual.append(self.tokenAtual().lexema)
                tempParenteses.append(tempParentesesParamAtual)
                self.indexDaTabelaDeTokens += 1
                if self.tokenAtual().tipo == "COMMA":
                    self.params_statement(tempParenteses)
                elif (
                    self.tokenAtual().tipo == "INT" or self.tokenAtual().tipo == "BOOL"
                ):
                    raise Exception(
                        "Erro sintatico: falta vírgula na linha "
                        + str(self.tokenAtual().linha)
                    )
                else:
                    return tempParenteses
            else:
                raise Exception(
                    "Erro sintatico: é necessário informar alguma váriavel na linha "
                    + str(self.tokenAtual().linha)
                )
        else:
            raise Exception(
                "Erro sintatico: é necessário informar um tipo na linha "
                + str(self.tokenAtual().linha)
            )

    # ESCOPO OK
    # <declaration_proc> OK
    def declaration_proc_statement(self, temp):
        self.indexDaTabelaDeTokens += 1
        # identificador
        if self.tokenAtual().tipo == "ID":
            temp.append(self.tokenAtual().lexema)
            self.indexDaTabelaDeTokens += 1
            if self.tokenAtual().tipo == "PLEFT":
                tempParenteses = []
                self.indexDaTabelaDeTokens += 1
                if self.tokenAtual().tipo == "INT" or self.tokenAtual().tipo == "BOOL":
                    tempParentesesParamAtual = []
                    tempParentesesParamAtual.append(self.indexEscopoAtual + 1)
                    tempParentesesParamAtual.append(self.tokenAtual().tipo)
                    self.indexDaTabelaDeTokens += 1
                    if self.tokenAtual().tipo == "ID":
                        tempParentesesParamAtual.append(
                            self.tokenAtual().lexema)
                        tempParenteses.append(tempParentesesParamAtual)
                        self.indexDaTabelaDeTokens += 1
                        if self.tokenAtual().tipo == "COMMA":
                            tempParenteses.append(
                                self.params_statement(tempParenteses))
                            tempParenteses.pop()
                            temp.append(tempParenteses)
                            if self.tokenAtual().tipo == "PRIGHT":
                                self.indexDaTabelaDeTokens += 1
                                if self.tokenAtual().tipo == "CLEFT":

                                    self.indexEscopoAntesDaFuncao = (
                                        self.indexEscopoAtual
                                    )

                                    self.indexEscopoAtual += 1
                                    self.indexDaTabelaDeTokens += 1

                                    tempBlock = []
                                    # BLOCK # TODO: Verificar
                                    while (
                                        self.tokenAtual().tipo != "CRIGHT"
                                        and self.tokenLookAhead().tipo != "SEMICOLON"
                                    ):
                                        tempBlock.append(
                                            self.block_statement())

                                    temp.append(tempBlock)

                                    if self.tokenAtual().tipo == "CRIGHT":
                                        self.indexEscopoAtual = (
                                            self.indexEscopoAntesDaFuncao
                                        )
                                        self.indexDaTabelaDeTokens += 1
                                        if self.tokenAtual().tipo == "SEMICOLON":
                                            self.indexDaTabelaDeTokens += 1
                                            return temp
                                        else:
                                            raise Exception(
                                                "Erro sintatico: falta do ponto e vírgula na linha "
                                                + str(self.tokenAtual().linha)
                                            )
                                    else:
                                        raise Exception(
                                            "Erro sintatico: falta da chave direito na linha "
                                            + str(self.tokenAtual().linha)
                                        )
                                else:
                                    raise Exception(
                                        "Erro sintatico: falta da chave esquerda na linha "
                                        + str(self.tokenAtual().linha)
                                    )
                            else:
                                raise Exception(
                                    "Erro sintatico: falta do parentese direito na linha "
                                    + str(self.tokenAtual().linha)
                                )

                        elif self.tokenAtual().tipo == "PRIGHT":
                            temp.append(tempParenteses)
                            if self.tokenAtual().tipo == "PRIGHT":
                                self.indexDaTabelaDeTokens += 1
                                if self.tokenAtual().tipo == "CLEFT":

                                    self.indexEscopoAntesDaFuncao = (
                                        self.indexEscopoAtual
                                    )
                                    self.indexEscopoAtual += 1
                                    self.indexDaTabelaDeTokens += 1
                                    tempBlock = []
                                    # BLOCK # TODO: Verificar
                                    while (
                                        self.tokenAtual().tipo != "CRIGHT"
                                        and self.tokenLookAhead().tipo != "SEMICOLON"
                                    ):
                                        tempBlock.append(
                                            self.block_statement())

                                    temp.append(tempBlock)
                                    if self.tokenAtual().tipo == "CRIGHT":
                                        self.indexEscopoAtual = (
                                            self.indexEscopoAntesDaFuncao
                                        )
                                        self.indexDaTabelaDeTokens += 1
                                        if self.tokenAtual().tipo == "SEMICOLON":
                                            self.indexDaTabelaDeTokens += 1
                                            return temp
                                        else:
                                            raise Exception(
                                                "Erro sintatico: falta do ponto e vírgula na linha "
                                                + str(self.tokenAtual().linha)
                                            )
                                    else:
                                        raise Exception(
                                            "Erro sintatico: falta da chave direito na linha "
                                            + str(self.tokenAtual().linha)
                                        )
                                else:
                                    raise Exception(
                                        "Erro sintatico: falta da chave esquerda na linha "
                                        + str(self.tokenAtual().linha)
                                    )
                            else:
                                raise Exception(
                                    "Erro sintatico: falta do parentese direito na linha "
                                    + str(self.tokenAtual().linha)
                                )
                        else:
                            # TODO: (5 - falta descobrir) resolver exceção
                            raise Exception(
                                "Erro sintatico: falta da virgula na linha "
                                + str(self.tokenAtual().linha)
                            )
                    else:
                        raise Exception(
                            "Erro sintatico: falta o ID na linha "
                            + str(self.tokenAtual().linha)
                        )
                else:
                    if self.tokenAtual().tipo == "PRIGHT":
                        temp.append(tempParenteses)
                        self.indexDaTabelaDeTokens += 1
                        if self.tokenAtual().tipo == "CLEFT":
                            self.indexEscopoAntesDaFuncao = self.indexEscopoAtual
                            self.indexEscopoAtual += 1
                            self.indexDaTabelaDeTokens += 1
                            tempBlock = []
                            # BLOCK # TODO: Verificar
                            while (
                                self.tokenAtual().tipo != "CRIGHT"
                                and self.tokenLookAhead().tipo != "SEMICOLON"
                            ):
                                tempBlock.append(self.block_statement())

                            temp.append(tempBlock)
                            if self.tokenAtual().tipo == "CRIGHT":
                                self.indexEscopoAtual = self.indexEscopoAntesDaFuncao
                                self.indexDaTabelaDeTokens += 1
                                if self.tokenAtual().tipo == "SEMICOLON":
                                    self.indexDaTabelaDeTokens += 1
                                    return temp
                                else:
                                    raise Exception(
                                        "Erro sintatico: falta do ponto e vírgula na linha "
                                        + str(self.tokenAtual().linha)
                                    )
                            else:
                                raise Exception(
                                    "Erro sintatico: falta da chave direito na linha "
                                    + str(self.tokenAtual().linha)
                                )

                        else:
                            raise Exception(
                                "Erro sintatico: falta da chave esquerda na linha "
                                + str(self.tokenAtual().linha)
                            )
                    else:
                        raise Exception(
                            "Erro sintatico: falta do parentese direito na linha "
                            + str(self.tokenAtual().linha)
                        )
            else:
                raise Exception(
                    "Erro sintatico: falta do parentese esquerdo na linha "
                    + str(self.tokenAtual().linha)
                )
        else:
            raise Exception(
                "Erro sintatico: falta do ID na linha " +
                str(self.tokenAtual().linha)
            )

    # ESCOPO OK
    # <call_proc>
    def call_proc_statement(self, temp):
        self.indexDaTabelaDeTokens += 1
        if self.tokenAtual().tipo == "ID":
            temp.append(self.tokenAtual().lexema)
            self.indexDaTabelaDeTokens += 1
            if self.tokenAtual().tipo == "PLEFT":
                self.indexDaTabelaDeTokens += 1
                tempParams = []
                if (
                    self.tokenAtual().tipo == "ID"
                    or self.tokenAtual().lexema == "True"
                    or self.tokenAtual().lexema == "False"
                ):
                    tempParams.append(self.tokenAtual().lexema)
                    self.indexDaTabelaDeTokens += 1
                    if self.tokenAtual().tipo == "COMMA":
                        tempParams.append(
                            self.params_call_statement(tempParams))
                        tempParams.pop()
                        temp.append(tempParams)
                        #  [0, 'CALL', 'PROC', 'proc1', ['a', 'b', 'c']],
                        #  [0, 'CALL', 'PROC', 'proc1', [['a'], ['b'], ['c']]],
                        if self.tokenAtual().tipo == "PRIGHT":
                            self.indexDaTabelaDeTokens += 1
                            temp.append(tempParams)
                            return temp

                    elif self.tokenAtual().tipo == "PRIGHT":
                        self.indexDaTabelaDeTokens += 1
                        temp.append(tempParams)
                        return temp
                    else:
                        raise Exception(
                            "Erro sintatico: falta da virgula na linha "
                            + str(self.tokenAtual().linha)
                        )
                else:
                    temp.append(tempParams)
                    if self.tokenAtual().tipo == "PRIGHT":

                        self.indexDaTabelaDeTokens += 1
                        return temp
                    else:
                        raise Exception(
                            "Erro sintatico: falta do parentese direito na linha "
                            + str(self.tokenAtual().linha)
                        )
            else:
                raise Exception(
                    "Erro sintatico: falta do parentese esquerdo na linha "
                    + str(self.tokenAtual().linha)
                )
        else:
            raise Exception(
                "Erro sintatico: falta do ID na linha " +
                str(self.tokenAtual().linha)
            )

    # ESCOPO OK
    # <call_func>
    def call_func_statement(self, temp):
        self.indexDaTabelaDeTokens += 1
        if self.tokenAtual().tipo == "ID":
            temp.append(self.tokenAtual().lexema)
            self.indexDaTabelaDeTokens += 1
            if self.tokenAtual().tipo == "PLEFT":
                self.indexDaTabelaDeTokens += 1
                tempParams = []
                if (
                    self.tokenAtual().tipo == "ID"
                    or self.tokenAtual().lexema == "True"
                    or self.tokenAtual().lexema == "False"
                ):
                    tempParams.append(self.tokenAtual().lexema)
                    self.indexDaTabelaDeTokens += 1
                    if self.tokenAtual().tipo == "COMMA":
                        tempParams.append(
                            self.params_call_statement(tempParams))
                        tempParams.pop()
                        if self.tokenAtual().tipo == "PRIGHT":
                            self.indexDaTabelaDeTokens += 1
                            temp.append(tempParams)
                            return temp
                        else:
                            raise Exception(
                                "Erro sintatico: falta do parentese direito na linha "
                                + str(self.tokenAtual().linha)
                            )
                    elif self.tokenAtual().tipo == "PRIGHT":
                        self.indexDaTabelaDeTokens += 1
                        temp.append(tempParams)
                        return temp
                    else:
                        raise Exception(
                            "Erro sintatico: falta do parentese direito na linha "
                            + str(self.tokenAtual().linha)
                        )

                else:
                    temp.append(tempParams)
                    if self.tokenAtual().tipo == "PRIGHT":
                        self.indexDaTabelaDeTokens += 1

                        return temp
                    else:
                        raise Exception(
                            "Erro sintatico: falta do parentese direito na linha "
                            + str(self.tokenAtual().linha)
                        )
            else:
                raise Exception(
                    "Erro sintatico: falta do parentese esquerdo na linha "
                    + str(self.tokenAtual().linha)
                )
        else:
            raise Exception(
                "Erro sintatico: falta do ID na linha " +
                str(self.tokenAtual().linha)
            )

    # ESCOPO OK
    # <params_call>
    def params_call_statement(self, tempParams):
        self.indexDaTabelaDeTokens += 1
        if (
            self.tokenAtual().tipo == "ID"
            or self.tokenAtual().lexema == "True"
            or self.tokenAtual().lexema == "False"
        ):
            tempParams.append(self.tokenAtual().lexema)
            self.indexDaTabelaDeTokens += 1
            if self.tokenAtual().tipo == "COMMA":
                self.params_call_statement(tempParams)
            elif (
                self.tokenAtual().tipo == "ID"
                or self.tokenAtual().lexema == "True"
                or self.tokenAtual().lexema == "False"
            ):
                raise Exception(
                    "Erro sintatico: falta vírgula na linha "
                    + str(self.tokenAtual().linha)
                )
            else:
                # Removido p/ correção
                # self.indexDaTabelaDeTokens += 1
                return tempParams
        else:
            raise Exception(
                "Erro sintatico: é necessário informar alguma váriavel na linha "
                + str(self.tokenAtual().linha)
            )

    # ESCOPO OK
    # <print_statement> OK
    def print_statement(self, temp):
        self.indexDaTabelaDeTokens += 1
        if self.tokenAtual().tipo == "PLEFT":
            tempParams = []
            temp.append(self.params_print_statement(tempParams))

            if self.tokenAtual().tipo == "PRIGHT":
                self.indexDaTabelaDeTokens += 1
                if self.tokenAtual().tipo == "SEMICOLON":
                    self.tabelaDeSimbolos.append(temp)
                    self.indexDaTabelaDeTokens += 1
                    return
                else:
                    # TODO: (4) SOLVE BUG DE CONTAGEM DE LINHAS
                    raise Exception(
                        "Erro sintatico: falta do ponto e virgula na linha "
                        + str(self.tokenAtual().linha)
                    )
            else:
                raise Exception(
                    "Erro sintatico: falta do Parentese direito na linha "
                    + str(self.tokenAtual().linha)
                )
        else:
            raise Exception(
                "Erro sintatico: falta do Parentese esquerdo na linha  "
                + str(self.tokenAtual().linha)
            )

    # ESCOPO OK
    # <params_print_statement> OK
    def params_print_statement(self, tempParams):
        self.indexDaTabelaDeTokens += 1
        if self.tokenAtual().tipo == "CALL":
            tempParams.append(self.tokenAtual().tipo)
            self.indexDaTabelaDeTokens += 1
            if self.tokenAtual().tipo == "FUNC":
                tempParams.append(self.tokenAtual().tipo)
                tempParams = self.call_func_statement(tempParams)
                return tempParams
            elif self.tokenAtual().tipo == "PROC":
                raise Exception(
                    "Erro sintatico: Procedimento não tem retorno na linha "
                    + str(self.tokenAtual().linha)
                )
            else:
                raise Exception(
                    "Erro sintatico: chamada incorreta de função na linha "
                    + str(self.tokenAtual().linha)
                )

        elif (
            (self.tokenAtual().tipo == "NUM")
            or (self.tokenAtual().tipo == "BOOLEAN")
            or (self.tokenAtual().tipo == "ID")
        ):
            tempParams.append(self.tokenAtual().lexema)
            self.indexDaTabelaDeTokens += 1
            if (
                self.tokenAtual().tipo == "ADD"
                or self.tokenAtual().tipo == "SUB"
                or self.tokenAtual().tipo == "MULT"
                or self.tokenAtual().tipo == "DIV"
            ):
                tempParams.append(self.tokenAtual().lexema)
                self.call_op_statement(tempParams)
                return tempParams
            else:
                return tempParams
        else:
            raise Exception(
                "Erro sintatico: uso incorreto dos parametros na linha "
                + str(self.tokenAtual().linha)
            )

    # ESCOPO OK
    # <if_statement>
    def if_statement(self, temp):
        self.indexDaTabelaDeTokens += 1
        if self.tokenAtual().tipo == "PLEFT":
            self.indexDaTabelaDeTokens += 1
            tempExpression = []
            # Expression
            tempExpression = self.expression_statement(tempExpression)
            temp.append(tempExpression)

            if self.tokenAtual().tipo == "PRIGHT":
                olhaAfrente = self.tokenLookAhead()
                self.indexDaTabelaDeTokens += 1
                if self.tokenAtual().tipo == "CLEFT" and olhaAfrente.tipo != "CRIGHT":
                    self.indexDaTabelaDeTokens += 1
                    self.indexEscopoAtual += 1
                    tempBlock = []
                    while (
                        self.tokenAtual().tipo != "CRIGHT"
                        and self.tokenLookAhead().tipo != "ENDIF"
                    ):
                        tempBlock.append(self.block3_statement())

                    temp.append(tempBlock)
                    if self.tokenAtual().tipo == "CRIGHT":
                        self.indexDaTabelaDeTokens += 1
                        if self.tokenAtual().tipo == "ENDIF":
                            temp.append(self.tokenAtual().tipo)
                            self.indexDaTabelaDeTokens += 1

                            tempElse = []
                            if self.tokenAtual().tipo == "ELSE":
                                tempElse.append(self.indexEscopoAtual)
                                tempElse.append(self.tokenAtual().tipo)
                                tempElse = self.else_part_statement(
                                    tempElse)  # ELSE

                                temp.append(tempElse)
                                self.tabelaDeSimbolos.append(temp)
                                self.indexEscopoAtual -= 1
                            else:
                                temp.append(tempElse)
                                self.tabelaDeSimbolos.append(temp)
                                self.indexEscopoAtual -= 1
                                return
                        else:
                            raise Exception(
                                "Erro sintatico: falta de ENDIF "
                                + str(self.tokenAtual().linha)
                            )
                    else:
                        raise Exception(
                            "Erro sintatico: falta do CRIGHT na linha "
                            + str(self.tokenAtual().linha)
                        )
                else:
                    raise Exception(
                        "Erro sintatico: falta do CLEFT ou bloco vazio na linha "
                        + str(self.tokenAtual().linha)
                    )
            else:
                raise Exception(
                    "Erro sintatico: falta do Parentese direito na linha  "
                    + str(self.tokenAtual().linha)
                )
        else:
            raise Exception(
                "Erro sintatico: falta do Parentese esquerdo na linha  "
                + str(self.tokenAtual().linha)
            )

    # ESCOPO OK
    # <else_part>
    def else_part_statement(self, tempElse):
        olhaAfrente = self.tokenLookAhead()
        self.indexDaTabelaDeTokens += 1
        if self.tokenAtual().tipo == "CLEFT" and olhaAfrente.tipo != "CRIGHT":
            self.indexDaTabelaDeTokens += 1
            tempBlock = []
            while (
                self.tokenAtual().tipo != "CRIGHT"
                and self.tokenLookAhead().tipo != "ENDELSE"
            ):
                # Block
                tempBlock.append(self.block3_statement())
            tempElse.append(tempBlock)
            if self.tokenAtual().tipo == "CRIGHT":
                self.indexDaTabelaDeTokens += 1
                if self.tokenAtual().tipo == "ENDELSE":
                    tempElse.append(self.tokenAtual().tipo)
                    self.indexDaTabelaDeTokens += 1
                    return tempElse
                else:
                    raise Exception(
                        "Erro sintatico: falta de ENDELSE na linha "
                        + str(self.tokenAtual().linha)
                    )
            else:
                raise Exception(
                    "Erro sintatico: falta do CRIGHT na linha "
                    + str(self.tokenAtual().linha)
                )
        else:
            raise Exception(
                "Erro sintatico: falta do CLEFT ou bloco vazio na linha "
                + str(self.tokenAtual().linha)
            )

    # ESCOPO OK
    # <if_statement2>
    # IF chamado somente dentro do while, pois dentro dele pode ter BREAK E CONTINUE (block2)
    def if_statement2(self, temp):
        self.indexDaTabelaDeTokens += 1
        if self.tokenAtual().tipo == "PLEFT":
            self.indexDaTabelaDeTokens += 1
            tempExpression = []
            # Expression
            tempExpression = self.expression_statement(tempExpression)
            temp.append(tempExpression)
            if self.tokenAtual().tipo == "PRIGHT":
                olhaAfrente = self.tokenLookAhead()
                self.indexDaTabelaDeTokens += 1
                if self.tokenAtual().tipo == "CLEFT" and olhaAfrente.tipo != "CRIGHT":
                    self.indexDaTabelaDeTokens += 1
                    self.indexEscopoAtual += 1
                    tempBlock = []
                    while (
                        self.tokenAtual().tipo != "CRIGHT"
                        and self.tokenLookAhead().tipo != "ENDIF"
                    ):
                        tempBlock.append(self.block2_statement())
                    temp.append(tempBlock)
                    if self.tokenAtual().tipo == "CRIGHT":
                        self.indexDaTabelaDeTokens += 1
                        if self.tokenAtual().tipo == "ENDIF":
                            temp.append(self.tokenAtual().tipo)
                            self.indexDaTabelaDeTokens += 1
                            tempElse = []
                            if self.tokenAtual().tipo == "ELSE":
                                tempElse.append(self.indexEscopoAtual)
                                tempElse.append(self.tokenAtual().tipo)
                                tempElse = self.else_part_statement2(
                                    tempElse)  # ELSE

                                temp.append(tempElse)
                                self.tabelaDeSimbolos.append(temp)
                                self.indexEscopoAtual -= 1
                            else:
                                temp.append(tempElse)
                                self.tabelaDeSimbolos.append(temp)
                                self.indexEscopoAtual -= 1
                                return
                        else:
                            raise Exception(
                                "Erro sintatico: falta de ENDIF "
                                + str(self.tokenAtual().linha)
                            )
                    else:
                        raise Exception(
                            "Erro sintatico: falta do CRIGHT na linha "
                            + str(self.tokenAtual().linha)
                        )
                else:
                    raise Exception(
                        "Erro sintatico: falta do CLEFT ou Bloco vazio na linha "
                        + str(self.tokenAtual().linha)
                    )
            else:
                raise Exception(
                    "Erro sintatico: falta do Parentese direito na linha  "
                    + str(self.tokenAtual().linha)
                )
        else:
            raise Exception(
                "Erro sintatico: falta do Parentese esquerdo na linha  "
                + str(self.tokenAtual().linha)
            )

    # ESCOPO OK
    # ELSE chamado somente dentro do while, pois dentro dele pode ter BREAK E CONTINUE (block2)
    # <else_part2>
    def else_part_statement2(self, tempElse):
        olhaAfrente = self.tokenLookAhead()
        self.indexDaTabelaDeTokens += 1
        if self.tokenAtual().tipo == "CLEFT" and olhaAfrente.tipo != "CRIGHT":
            self.indexDaTabelaDeTokens += 1
            # Block
            tempBlock = []
            while (
                self.tokenAtual().tipo != "CRIGHT"
                and self.tokenLookAhead().tipo != "ENDELSE"
            ):
                tempBlock.append(self.block2_statement())
            tempElse.append(tempBlock)
            if self.tokenAtual().tipo == "CRIGHT":
                self.indexDaTabelaDeTokens += 1
                if self.tokenAtual().tipo == "ENDELSE":
                    tempElse.append(self.tokenAtual().tipo)
                    self.indexDaTabelaDeTokens += 1
                    return tempElse
                else:
                    raise Exception(
                        "Erro sintatico: falta de ENDELSE na linha "
                        + str(self.tokenAtual().linha)
                    )
            else:
                raise Exception(
                    "Erro sintatico: falta do CRIGHT na linha "
                    + str(self.tokenAtual().linha)
                )
        else:
            raise Exception(
                "Erro sintatico: falta do CLEFT ou bloco vazio na linha "
                + str(self.tokenAtual().linha)
            )

    # ESCOPO OK
    # <while_statement>
    def while_statement(self, temp):
        self.indexDaTabelaDeTokens += 1
        if self.tokenAtual().tipo == "PLEFT":
            self.indexDaTabelaDeTokens += 1
            tempExpression = []
            # Expression
            tempExpression = self.expression_statement(tempExpression)
            temp.append(tempExpression)
            if self.tokenAtual().tipo == "PRIGHT":
                self.indexDaTabelaDeTokens += 1
                if self.tokenAtual().tipo == "CLEFT":
                    self.indexDaTabelaDeTokens += 1
                    self.indexEscopoAtual += 1
                    tempBlock = []
                    # BLOCK
                    while (
                        self.tokenAtual().tipo != "CRIGHT"
                        and self.tokenLookAhead().tipo != "ENDWHILE"
                    ):
                        tempBlock.append(self.block2_statement())

                    temp.append(tempBlock)

                    if self.tokenAtual().tipo == "CRIGHT":
                        self.indexDaTabelaDeTokens += 1
                        if self.tokenAtual().tipo == "ENDWHILE":
                            temp.append(self.tokenAtual().tipo)
                            self.indexDaTabelaDeTokens += 1
                            self.tabelaDeSimbolos.append(temp)
                            self.indexEscopoAtual -= 1
                        else:
                            raise Exception(
                                "Erro sintatico: falta de ENDWHILE na linha "
                                + str(self.tokenAtual().linha)
                            )
                    else:
                        raise Exception(
                            "Erro sintatico: falta do CRIGHT na linha "
                            + str(self.tokenAtual().linha)
                        )
                else:
                    raise Exception(
                        "Erro sintatico: falta do CLEFT na linha "
                        + str(self.tokenAtual().linha)
                    )
            else:
                raise Exception(
                    "Erro sintatico: falta do PRIGHT na linha "
                    + str(self.tokenAtual().linha)
                )
        else:
            raise Exception(
                "Erro sintatico: falta do PLEFT na linha "
                + str(self.tokenAtual().linha)
            )

    # ESCOPO OK
    # <unconditional_branch>
    def unconditional_branch_statement(self):
        if self.tokenAtual().tipo == "CONTINUE":
            self.indexDaTabelaDeTokens += 1
            if self.tokenAtual().tipo == "SEMICOLON":
                self.indexDaTabelaDeTokens += 1
            else:
                raise Exception(
                    "Erro sintatico: falta do ponto e virgula na linha "
                    + str(self.tokenAtual().linha)
                )

        if self.tokenAtual().tipo == "BREAK":
            self.indexDaTabelaDeTokens += 1
            if self.tokenAtual().tipo == "SEMICOLON":
                self.indexDaTabelaDeTokens += 1
            else:
                raise Exception(
                    "Erro sintatico: falta do ponto e virgula na linha "
                    + str(self.tokenAtual().linha)
                )

    # ESCOPO OK
    # <expression>
    def expression_statement(self, tempExpression):
        if self.tokenAtual().tipo == "ID" or self.tokenAtual().tipo == "NUM":
            tempExpression.append(self.tokenAtual().lexema)
            self.indexDaTabelaDeTokens += 1
            if (
                self.tokenAtual().tipo == "EQUAL"
                or self.tokenAtual().tipo == "DIFF"
                or self.tokenAtual().tipo == "LESSEQUAL"
                or self.tokenAtual().tipo == "LESS"
                or self.tokenAtual().tipo == "GREATEREQUAL"
                or self.tokenAtual().tipo == "GREATER"
            ):
                tempExpression.append(self.tokenAtual().lexema)
                self.indexDaTabelaDeTokens += 1
                if self.tokenAtual().tipo == "ID" or self.tokenAtual().tipo == "NUM":
                    tempExpression.append(self.tokenAtual().lexema)
                    self.indexDaTabelaDeTokens += 1
                    return tempExpression
                else:
                    raise Exception(
                        "Erro sintatico: falta do ID na linha "
                        + str(self.tokenAtual().linha)
                    )
            else:
                raise Exception(
                    "Erro sintatico: falta do operador booleano na linha "
                    + str(self.tokenAtual().linha)
                )
        else:
            raise Exception(
                "Erro sintatico: falta do ID na linha " +
                str(self.tokenAtual().linha)
            )

    # ESCOPO OK
    # <call_op> ok - Operações aritméticas
    def call_op_statement(self, tempEndVar):
        self.indexDaTabelaDeTokens += 1
        if self.tokenAtual().tipo == "ID" or self.tokenAtual().tipo == "NUM":
            tempEndVar.append(self.tokenAtual().lexema)
            self.indexDaTabelaDeTokens += 1
            if (
                self.tokenAtual().tipo == "ADD"
                or self.tokenAtual().tipo == "SUB"
                or self.tokenAtual().tipo == "MULT"
                or self.tokenAtual().tipo == "DIV"
            ):
                tempEndVar.append(self.tokenAtual().lexema)
                self.call_op_statement(tempEndVar)
            else:
                return
        else:
            raise Exception(
                "Erro sintatico: falta do ID na linha " +
                str(self.tokenAtual().linha)
            )


    def tokenLookAhead(self):
        self.indexLookAhead = self.indexDaTabelaDeTokens + 1
        return self.tabelaDeTokens[self.indexLookAhead]

    def getTokens(self):
        return self.tabelaDeTokens
