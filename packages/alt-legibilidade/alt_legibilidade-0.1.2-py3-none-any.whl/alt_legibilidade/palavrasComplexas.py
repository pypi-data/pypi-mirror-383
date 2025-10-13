import os

from importlib.resources import files

def carregar_banco_palavras(limite=5000):
    banco_palavras = []
    try:
        p = files("alt_legibilidade") / "banco" / "palavras-mais-comuns-utf8.txt"
        with p.open("r", encoding="utf-8", newline="") as arquivo:
            for i, linha in enumerate(arquivo):
                if i >= limite:
                    break
                banco_palavras.append(linha.strip())
    except FileNotFoundError:
        print("Arquivo de banco não encontrado dentro do pacote.")
    return banco_palavras



def is_letra(c):
    return c.lower() != c.upper()


def contar_palavras_complexas(texto, banco_palavras):
    palavras_simples = 0
    palavras_total = 0
    palavra = ""
    primeira_letra = ""
    p = 0
    kk = 0
    novo_texto = []

    for k in range(len(texto)):
        caractere = texto[k]
        anterior1 = texto[k - 1] if k > 0 else ""
        anterior2 = texto[k - 2] if k > 1 else ""

        if is_letra(caractere) or caractere == "-":
            palavra += caractere
            if p == 0:
                primeira_letra = caractere
            p += 1
        elif (caractere == " " or caractere == "\n" or k == len(texto) - 1) and \
             anterior1 not in [" ", "\n", "-"]:
            palavras_total += 1
            cont = 0
            if primeira_letra.isupper() and anterior2 != ".":
                novo_texto.append(palavra)
                palavras_simples += 1
                kk += 1
            else:
                for entrada in banco_palavras:
                    if entrada.strip() == palavra.strip() and cont == 0:
                        novo_texto.append(palavra)
                        palavras_simples += 1
                        cont += 1
                        kk += 1
            palavra = ""
            p = 0

    palavras_complexas = palavras_total - palavras_simples
    return palavras_complexas
