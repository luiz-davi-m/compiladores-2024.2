from analisadores.analisadorLexico import AnalisadorLexico
from analisadores.analisadorSintatico import AnalisadorSintatico


if __name__ == '__main__':
    testPath = 'teste.txt'

    try:
        arquivo = open(testPath, "r")
        programa = "".join(arquivo.readlines())
        arquivo.close()
    except Exception:
        print('Error: path to progam is not valid!')


    try:

        analisadorLexico = AnalisadorLexico(programa)

        tabelaDeTokens = analisadorLexico.scan()

        analisadorSintatico = AnalisadorSintatico(tabelaDeTokens)

        analisadorSintatico.start()

        # for token in analisadorSintatico.getTokens():
        #     print(token)
        
    except Exception as e:
        print(e)



