def contar_silabas(texto: str) -> int:
    silabas = 0
    silaba_anterior = ""
    cont_silabas = -1  # começa com valor inválido propositalmente

    vogal = ["a", "ã", "â", "á", "à", "e", "é", "ê", "i", "í", "o", "õ", "ô", "ó", "u", "ú"]
    ditongo = ["ãe", "ai", "ão", "au", "ei", "eu", "éu", "ia", "ie", "io", "iu", "õe", "oi", "ói", "ou", "ua", "ue", "uê", "ui"]
    tritongo = ["uai", "uei", "uão", "uõe", "uiu", "uou"]
    consoante = ["b", "c", "d", "f", "g", "h", "j", "k", "l", "m", "n", "p", "q", "r", "s", "t", "v", "w", "x", "y", "z"]

    for k in range(len(texto)):
        caractere = texto[k]
        anterior1 = texto[k - 1] if k > 0 else ""
        anterior2 = texto[k - 2] if k > 1 else ""

        # contar vogais
        for v in vogal:
            if caractere == v or caractere == v.upper():
                silabas += 1

        # corrigir ditongos
        for j, d in enumerate(ditongo):
            par = anterior1 + caractere
            if (par == d or par == d.upper()) and (
                cont_silabas < 0 or cont_silabas >= len(ditongo) or silaba_anterior != ditongo[cont_silabas]
                or anterior2.lower() in consoante
            ):
                silabas -= 1
                cont_silabas = j
                silaba_anterior = ditongo[cont_silabas]

        # corrigir tritongos
        trio = anterior2 + anterior1 + caractere
        for t in tritongo:
            if trio == t:
                silabas -= 1

    return max(silabas, 1)
