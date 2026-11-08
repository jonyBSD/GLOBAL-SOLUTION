"""
Neighborhood Action Dashboard - Global Solution 2026/2 (CitizenTech)

Painel comunitário textual para registrar, consultar e acompanhar ocorrências
fictícias de um bairro (iluminação, acessibilidade, limpeza e conservação).

Usa somente conteúdos das Fases 1, 2 e 3: variáveis, funções, condicionais,
laços, listas, dicionários, filas, pilhas, matrizes e leitura simples de arquivos.

Executar (na raiz do repositório):  python src/sistema.py
"""

import os

# ---------------------------------------------------------------------------
# 1. CONSTANTES PADRONIZADAS
# ---------------------------------------------------------------------------

# Categorias (código padronizado -> nome para exibição)
CATEGORIAS = {
    "iluminacao": "Iluminação",
    "acessibilidade": "Acessibilidade",
    "limpeza": "Limpeza",
    "conservacao": "Conservação de espaços",
}

# Situações (código padronizado -> nome para exibição)
#   aberta     = registrada, ainda não examinada
#   em_analise = já examinada, aguardando solução
#   concluida  = demanda resolvida (simulado)
STATUS = {
    "aberta": "Aberta",
    "em_analise": "Em análise",
    "concluida": "Concluída",
}

# Mudanças de situação permitidas (situação atual, nova situação)
TRANSICOES = [
    ("aberta", "em_analise"),
    ("em_analise", "concluida"),
]

HOJE_SIMULADO = 30  # "dia" atual da simulação (os dias são números inteiros)

PASTA_DADOS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data")

# ---------------------------------------------------------------------------
# 2. ESTRUTURAS DE DADOS (estado do sistema)
# ---------------------------------------------------------------------------
# lista      -> todas as ocorrências válidas, em ordem de registro
# indice     -> dicionário: código -> ocorrência (busca direta)
# fila       -> códigos ainda NÃO examinados (status "aberta"), ordem de chegada
# pilha      -> eventos de histórico; o último que entrou é o primeiro a sair
# hierarquia -> dicionário: bairro -> categoria -> lista de códigos
# historico  -> lista com todos os eventos de mudança de status
# rejeitadas -> linhas do arquivo que falharam na validação (com o motivo)
estado = {
    "lista": [],
    "indice": {},
    "fila": [],
    "pilha": [],
    "hierarquia": {},
    "historico": [],
    "rejeitadas": [],
    "proximo_numero": 1,
}


# ---------------------------------------------------------------------------
# 3. VALIDAÇÃO
# ---------------------------------------------------------------------------

def contar_digitos(texto):
    """Conta quantos caracteres do texto são dígitos."""
    total = 0
    for letra in texto:
        if letra.isdigit():
            total = total + 1
    return total


def validar_ocorrencia(o):
    """
    Devolve "" se a ocorrência é válida ou uma mensagem explicando o problema.
    Campos obrigatórios: id, categoria, descricao, bairro, local, dia_abertura, status.
    """
    # Expressão booleana 1 (OR): qualquer campo obrigatório vazio invalida o registro
    if (o["id"] == "" or o["categoria"] == "" or o["descricao"] == ""
            or o["bairro"] == "" or o["local"] == "" or o["dia_abertura"] == ""
            or o["status"] == ""):
        return "campo obrigatório ausente"

    # Expressão booleana 2 (NOT): categoria precisa estar no conjunto padronizado
    if o["categoria"] not in CATEGORIAS:
        return "categoria desconhecida ('" + o["categoria"] + "')"

    if not (o["status"] in STATUS):
        return "situação desconhecida ('" + o["status"] + "')"

    # Expressão booleana 3 (NOT + OR): o dia deve ser um inteiro positivo
    if not o["dia_abertura"].isdigit() or int(o["dia_abertura"]) < 1:
        return "data simulada inválida ('" + o["dia_abertura"] + "')"

    if o["id"] in estado["indice"]:
        return "código duplicado ('" + o["id"] + "')"

    # Privacidade (AND/OR): impede e-mails e números longos (telefone, CPF...)
    texto = o["descricao"] + " " + o["local"]
    if "@" in texto or contar_digitos(texto) >= 8:
        return "possível dado pessoal na descrição/local (e-mail ou telefone)"

    return ""


# ---------------------------------------------------------------------------
# 4. LEITURA DOS ARQUIVOS
# ---------------------------------------------------------------------------

def ler_linhas(nome_arquivo):
    """Lê o arquivo de dados e devolve uma lista de listas de campos (sem cabeçalho)."""
    caminho = os.path.join(PASTA_DADOS, nome_arquivo)
    linhas = []
    arquivo = open(caminho, "r", encoding="utf-8")
    primeira = True
    for linha in arquivo:
        linha = linha.strip()
        if primeira:          # pula o cabeçalho
            primeira = False
            continue
        if linha == "":
            continue
        campos = linha.split(";")
        for i in range(len(campos)):
            campos[i] = campos[i].strip()
        linhas.append(campos)
    arquivo.close()
    return linhas


def numero_do_codigo(codigo):
    """Extrai o número de um código como '014' (devolve 0 se não for numérico)."""
    if codigo.isdigit():
        return int(codigo)
    return 0


def registrar_na_estrutura(o):
    """Insere uma ocorrência já validada em todas as estruturas de dados."""
    estado["lista"].append(o)                       # lista
    estado["indice"][o["id"]] = o                   # dicionário
    if o["status"] == "aberta":
        estado["fila"].append(o["id"])              # fila (entra no fim)

    bairro = o["bairro"]                            # hierarquia bairro -> categoria -> ids
    if bairro not in estado["hierarquia"]:
        estado["hierarquia"][bairro] = {}
    if o["categoria"] not in estado["hierarquia"][bairro]:
        estado["hierarquia"][bairro][o["categoria"]] = []
    estado["hierarquia"][bairro][o["categoria"]].append(o["id"])


def carregar_dados():
    """Carrega ocorrências e histórico; linhas inválidas vão para 'rejeitadas'."""
    maior = 0
    for campos in ler_linhas("ocorrencias.csv"):
        if len(campos) != 7:
            estado["rejeitadas"].append((";".join(campos), "número de campos incorreto"))
            continue
        o = {
            "id": campos[0], "categoria": campos[1], "descricao": campos[2],
            "bairro": campos[3], "local": campos[4], "dia_abertura": campos[5],
            "status": campos[6], "dia_conclusao": 0,
        }
        if numero_do_codigo(o["id"]) > maior:
            maior = numero_do_codigo(o["id"])
        motivo = validar_ocorrencia(o)
        if motivo != "":
            estado["rejeitadas"].append((";".join(campos), motivo))
        else:
            o["dia_abertura"] = int(o["dia_abertura"])
            registrar_na_estrutura(o)
    estado["proximo_numero"] = maior + 1

    for campos in ler_linhas("historico.csv"):
        evento = {"id": campos[0], "dia": int(campos[1]),
                  "de": campos[2], "para": campos[3]}
        if evento["id"] in estado["indice"]:
            estado["historico"].append(evento)
            estado["pilha"].append(evento)          # pilha: topo = evento mais recente
            if evento["para"] == "concluida":
                estado["indice"][evento["id"]]["dia_conclusao"] = evento["dia"]


# ---------------------------------------------------------------------------
# 5. OPERAÇÕES: CADASTRO, CONSULTA, FILTRO, ATUALIZAÇÃO
# ---------------------------------------------------------------------------

def cadastrar(categoria, descricao, bairro, local):
    """Cadastra nova ocorrência. Devolve (ocorrência ou None, mensagem)."""
    codigo = str(estado["proximo_numero"]).zfill(3)
    o = {
        "id": codigo, "categoria": categoria.strip().lower(),
        "descricao": descricao.strip(), "bairro": bairro.strip(),
        "local": local.strip(), "dia_abertura": str(HOJE_SIMULADO),
        "status": "aberta", "dia_conclusao": 0,
    }
    motivo = validar_ocorrencia(o)
    if motivo != "":
        return None, "Cadastro recusado: " + motivo + "."
    o["dia_abertura"] = HOJE_SIMULADO
    registrar_na_estrutura(o)
    estado["proximo_numero"] = estado["proximo_numero"] + 1
    return o, "Ocorrência " + codigo + " cadastrada com sucesso (status: Aberta)."


def buscar_por_codigo(codigo):
    """Busca direta no dicionário. Devolve a ocorrência ou None."""
    codigo = codigo.strip()
    if codigo.isdigit():
        codigo = codigo.zfill(3)
    if codigo in estado["indice"]:
        return estado["indice"][codigo]
    return None


def filtrar(categoria, status):
    """
    Filtra a lista por categoria e/ou status ("" = não filtrar por esse campo).
    Expressão booleana de filtro:
        (categoria == "" OR cat da ocorrência == categoria)
        AND (status == "" OR status da ocorrência == status)
    """
    resultado = []
    for o in estado["lista"]:
        if (categoria == "" or o["categoria"] == categoria) and \
           (status == "" or o["status"] == status):
            resultado.append(o)
    return resultado


def atualizar_status(codigo, novo_status):
    """Muda a situação de uma ocorrência, validando a regra e gravando o histórico."""
    o = buscar_por_codigo(codigo)
    if o is None:
        return False, "Ocorrência não encontrada: " + codigo.strip() + "."
    if novo_status not in STATUS:
        return False, "Situação desconhecida: '" + novo_status + "'. Nada foi alterado."
    atual = o["status"]
    if atual == "concluida":
        return False, "A ocorrência " + o["id"] + " já está concluída e não pode mais mudar."
    if atual == novo_status:
        return False, "A ocorrência " + o["id"] + " já está em '" + STATUS[atual] + "'."
    if not ((atual, novo_status) in TRANSICOES):
        return False, ("Mudança não permitida: " + STATUS[atual] + " -> " + STATUS[novo_status]
                       + ". Fluxo permitido: Aberta -> Em análise -> Concluída.")

    o["status"] = novo_status
    if novo_status == "concluida":
        o["dia_conclusao"] = HOJE_SIMULADO
    if o["id"] in estado["fila"]:           # saiu da fila de não examinadas
        estado["fila"].remove(o["id"])
    evento = {"id": o["id"], "dia": HOJE_SIMULADO, "de": atual, "para": novo_status}
    estado["historico"].append(evento)
    estado["pilha"].append(evento)          # empilha o evento mais recente
    return True, ("Ocorrência " + o["id"] + " atualizada: " + STATUS[atual]
                  + " -> " + STATUS[novo_status] + ".")


def examinar_proxima():
    """Retira a primeira ocorrência da fila (ordem de registro) e a coloca em análise."""
    if len(estado["fila"]) == 0:
        return False, "A fila está vazia: não há demandas aguardando exame."
    codigo = estado["fila"][0]              # primeiro que chegou, primeiro a sair
    return atualizar_status(codigo, "em_analise")


# ---------------------------------------------------------------------------
# 6. INDICADORES
# ---------------------------------------------------------------------------

def montar_matriz():
    """Matriz (lista de listas): linhas = categorias, colunas = situações."""
    cats = list(CATEGORIAS.keys())
    stats = list(STATUS.keys())
    matriz = []
    for i in range(len(cats)):
        linha = []
        for j in range(len(stats)):
            linha.append(0)
        matriz.append(linha)
    for o in estado["lista"]:
        i = cats.index(o["categoria"])
        j = stats.index(o["status"])
        matriz[i][j] = matriz[i][j] + 1
    return matriz


def tempo_medio_conclusao():
    """Média de (dia_conclusao - dia_abertura) das concluídas. Devolve (média, quantidade)."""
    soma = 0
    qtd = 0
    for o in estado["lista"]:
        if o["status"] == "concluida" and o["dia_conclusao"] > 0:
            soma = soma + (o["dia_conclusao"] - o["dia_abertura"])
            qtd = qtd + 1
    if qtd == 0:
        return 0, 0
    return soma / qtd, qtd


def pendencias():
    """Ocorrências ainda não concluídas (NOT concluída)."""
    resultado = []
    for o in estado["lista"]:
        if not (o["status"] == "concluida"):
            resultado.append(o)
    return resultado


def percentual(parte, total):
    if total == 0:
        return 0.0
    return round(parte * 100 / total, 1)


# ---------------------------------------------------------------------------
# 7. APRESENTAÇÃO (interface textual)
# ---------------------------------------------------------------------------

def linha_separadora(tamanho=76):
    print("-" * tamanho)


def mostrar_listagem(ocorrencias):
    if len(ocorrencias) == 0:
        print("Nenhuma ocorrência encontrada para esse filtro.")
        return
    print("%-6s %-22s %-15s %-19s %-11s" % ("Código", "Categoria", "Bairro", "Local", "Status"))
    linha_separadora()
    for o in ocorrencias:
        print("%-6s %-22s %-15s %-19s %-11s" % (
            o["id"], CATEGORIAS[o["categoria"]], o["bairro"][:15],
            o["local"][:19], STATUS[o["status"]]))
    linha_separadora()
    print("Total exibido:", len(ocorrencias))


def mostrar_detalhe(o):
    print("Código.........:", o["id"])
    print("Categoria......:", CATEGORIAS[o["categoria"]])
    print("Descrição......:", o["descricao"])
    print("Bairro / Local.:", o["bairro"], "/", o["local"])
    print("Aberta no dia..:", o["dia_abertura"])
    print("Status.........:", STATUS[o["status"]])
    print("Dias em acompanhamento:", acompanhamento(o))
    print("Histórico desta ocorrência:")
    achou = False
    for e in estado["historico"]:
        if e["id"] == o["id"]:
            print("   dia %d: %s -> %s" % (e["dia"], STATUS[e["de"]], STATUS[e["para"]]))
            achou = True
    if not achou:
        print("   (nenhuma mudança registrada)")


def acompanhamento(o):
    """Dias simulados de acompanhamento: até a conclusão ou até hoje."""
    if o["status"] == "concluida" and o["dia_conclusao"] > 0:
        return o["dia_conclusao"] - o["dia_abertura"]
    return HOJE_SIMULADO - o["dia_abertura"]


def mostrar_indicadores():
    total = len(estado["lista"])
    print("=" * 72)
    print("PAINEL DE INDICADORES   (dia simulado atual: %d)" % HOJE_SIMULADO)
    print("=" * 72)
    if total == 0:
        print("Não há ocorrências cadastradas.")
        return

    # Indicador 1: total e proporção por categoria
    print("\n1) Ocorrências por categoria")
    print("   Regra: proporção = quantidade da categoria / total de ocorrências x 100")
    for codigo in CATEGORIAS:
        qtd = 0
        for o in estado["lista"]:
            if o["categoria"] == codigo:
                qtd = qtd + 1
        print("   %-34s %3d  (%5.1f%%)" % (CATEGORIAS[codigo], qtd, percentual(qtd, total)))
    print("   %-34s %3d" % ("TOTAL", total))

    # Indicador 2: quantidade e proporção por situação
    print("\n2) Ocorrências por situação")
    print("   Regra: proporção = quantidade da situação / total de ocorrências x 100")
    for codigo in STATUS:
        qtd = 0
        for o in estado["lista"]:
            if o["status"] == codigo:
                qtd = qtd + 1
        print("   %-34s %3d  (%5.1f%%)" % (STATUS[codigo], qtd, percentual(qtd, total)))

    # Matriz categoria x situação
    print("\n3) Matriz categoria x situação (linhas = categorias, colunas = situações)")
    matriz = montar_matriz()
    cabecalho = "   %-34s" % ""
    for codigo in STATUS:
        cabecalho = cabecalho + "%-12s" % STATUS[codigo]
    print(cabecalho)
    i = 0
    for codigo in CATEGORIAS:
        linha = "   %-34s" % CATEGORIAS[codigo]
        for valor in matriz[i]:
            linha = linha + "%-12d" % valor
        print(linha)
        i = i + 1

    # Indicador adicional: tempo médio simulado e pendências
    media, qtd = tempo_medio_conclusao()
    print("\n4) Tempo médio simulado até a conclusão")
    print("   Regra: média de (dia de conclusão - dia de abertura) das concluídas")
    if qtd > 0:
        print("   Resultado: %.1f dias (base: %d ocorrências concluídas)" % (media, qtd))
    else:
        print("   Resultado: sem ocorrências concluídas ainda.")

    pend = pendencias()
    print("\n5) Pendências (status diferente de 'concluída')")
    print("   Regra: pendências = aberta + em análise")
    print("   Resultado: %d pendências (%.1f%% do total)" % (len(pend), percentual(len(pend), total)))
    if len(pend) > 0:
        mais_antiga = pend[0]
        for o in pend:
            if acompanhamento(o) > acompanhamento(mais_antiga):
                mais_antiga = o
        print("   Mais antiga: %s (%s, %s) há %d dias"
              % (mais_antiga["id"], CATEGORIAS[mais_antiga["categoria"]],
                 mais_antiga["local"], acompanhamento(mais_antiga)))

    # Interpretação automática
    print("\n6) Interpretação")
    maior_cat = ""
    maior_qtd = -1
    for codigo in CATEGORIAS:
        qtd = 0
        for o in estado["lista"]:
            if o["categoria"] == codigo:
                qtd = qtd + 1
        if qtd > maior_qtd:
            maior_qtd = qtd
            maior_cat = codigo
    print("   A categoria com mais demandas é '%s' (%d de %d)."
          % (CATEGORIAS[maior_cat], maior_qtd, total))
    if len(pend) * 2 > total:
        print("   Mais da metade das demandas ainda está pendente: a comunidade")
        print("   precisa de acompanhamento mais ágil nas solicitações abertas.")
    else:
        print("   A maior parte das demandas já foi concluída ou está sendo tratada.")
    print("   Obs.: os dados são fictícios; o resultado ilustra o método, não a realidade.")


def mostrar_fila():
    print("Fila de demandas ainda não examinadas (a primeira será a próxima examinada):")
    if len(estado["fila"]) == 0:
        print("   (fila vazia)")
        return
    posicao = 1
    for codigo in estado["fila"]:
        o = estado["indice"][codigo]
        print("   %2d. %s - %s - %s" % (posicao, codigo, CATEGORIAS[o["categoria"]], o["local"]))
        posicao = posicao + 1


def mostrar_pilha(quantidade=5):
    print("Eventos mais recentes (topo da pilha primeiro):")
    if len(estado["pilha"]) == 0:
        print("   (nenhum evento)")
        return
    copia = estado["pilha"][:]              # copia para não esvaziar a pilha original
    mostrados = 0
    while len(copia) > 0 and mostrados < quantidade:
        e = copia.pop()                     # pop() retira do topo
        print("   dia %2d | ocorrência %s | %s -> %s"
              % (e["dia"], e["id"], STATUS[e["de"]], STATUS[e["para"]]))
        mostrados = mostrados + 1


def mostrar_hierarquia():
    print("Hierarquia: bairro -> categoria -> ocorrências")
    for bairro in estado["hierarquia"]:
        print("[Bairro] " + bairro)
        for cat in estado["hierarquia"][bairro]:
            codigos = estado["hierarquia"][bairro][cat]
            print("    [%s] %s" % (CATEGORIAS[cat], ", ".join(codigos)))


def mostrar_rejeitadas():
    print("Registros do arquivo recusados pela validação:")
    if len(estado["rejeitadas"]) == 0:
        print("   (nenhum)")
    for linha, motivo in estado["rejeitadas"]:
        print("   - '%s'" % linha)
        print("     motivo: %s" % motivo)


# ---------------------------------------------------------------------------
# 8. MENU
# ---------------------------------------------------------------------------

def escolher_categoria(permitir_vazio=False):
    print("Categorias:")
    codigos = list(CATEGORIAS.keys())
    for i in range(len(codigos)):
        print("  %d - %s" % (i + 1, CATEGORIAS[codigos[i]]))
    if permitir_vazio:
        print("  (Enter = todas)")
    resposta = input("Escolha o número da categoria: ").strip()
    if resposta == "" and permitir_vazio:
        return ""
    if resposta.isdigit() and 1 <= int(resposta) <= len(codigos):
        return codigos[int(resposta) - 1]
    return "?"          # valor inválido (tratado por quem chamou)


def escolher_status(permitir_vazio=False):
    print("Situações:")
    codigos = list(STATUS.keys())
    for i in range(len(codigos)):
        print("  %d - %s" % (i + 1, STATUS[codigos[i]]))
    if permitir_vazio:
        print("  (Enter = todas)")
    resposta = input("Escolha o número da situação: ").strip()
    if resposta == "" and permitir_vazio:
        return ""
    if resposta.isdigit() and 1 <= int(resposta) <= len(codigos):
        return codigos[int(resposta) - 1]
    return "?"


def menu():
    print()
    print("=" * 72)
    print(" NEIGHBORHOOD ACTION DASHBOARD - painel comunitário de ocorrências")
    print("=" * 72)
    print(" 1 - Listar todas as ocorrências")
    print(" 2 - Cadastrar nova ocorrência")
    print(" 3 - Consultar ocorrência por código")
    print(" 4 - Filtrar por categoria e/ou situação")
    print(" 5 - Atualizar situação de uma ocorrência")
    print(" 6 - Examinar a próxima demanda da fila")
    print(" 7 - Ver fila de demandas não examinadas")
    print(" 8 - Ver eventos recentes (pilha)")
    print(" 9 - Ver indicadores")
    print("10 - Ver hierarquia bairro > categoria > ocorrências")
    print("11 - Ver registros recusados na carga de dados")
    print(" 0 - Sair")
    return input("Escolha uma opção: ").strip()


def executar():
    carregar_dados()
    print("Dados carregados: %d ocorrências válidas, %d registros recusados, %d eventos de histórico."
          % (len(estado["lista"]), len(estado["rejeitadas"]), len(estado["historico"])))
    print("Aviso: todos os dados são fictícios e não contêm informações pessoais.")

    opcao = ""
    while opcao != "0":
        opcao = menu()
        print()

        if opcao == "1":
            mostrar_listagem(estado["lista"])

        elif opcao == "2":
            categoria = escolher_categoria()
            descricao = input("Descrição breve (sem nome, telefone ou e-mail): ")
            bairro = input("Bairro: ")
            local = input("Local genérico (ex.: Praça Central): ")
            if categoria == "?":
                print("Cadastro recusado: categoria inválida.")
            else:
                o, mensagem = cadastrar(categoria, descricao, bairro, local)
                print(mensagem)

        elif opcao == "3":
            codigo = input("Código da ocorrência (ex.: 014): ")
            o = buscar_por_codigo(codigo)
            if o is None:
                print("Ocorrência não encontrada: " + codigo.strip() + ".")
            else:
                mostrar_detalhe(o)

        elif opcao == "4":
            categoria = escolher_categoria(permitir_vazio=True)
            status = escolher_status(permitir_vazio=True)
            if categoria == "?" or status == "?":
                print("Filtro inválido: escolha um dos números mostrados.")
            else:
                mostrar_listagem(filtrar(categoria, status))

        elif opcao == "5":
            codigo = input("Código da ocorrência: ")
            novo = escolher_status()
            if novo == "?":
                print("Situação desconhecida. Nada foi alterado.")
            else:
                ok, mensagem = atualizar_status(codigo, novo)
                print(mensagem)

        elif opcao == "6":
            ok, mensagem = examinar_proxima()
            print(mensagem)

        elif opcao == "7":
            mostrar_fila()

        elif opcao == "8":
            mostrar_pilha()

        elif opcao == "9":
            mostrar_indicadores()

        elif opcao == "10":
            mostrar_hierarquia()

        elif opcao == "11":
            mostrar_rejeitadas()

        elif opcao == "0":
            print("Encerrando o painel. Obrigado por acompanhar as demandas do bairro!")

        else:
            print("Opção inválida. Digite um número do menu (0 a 11).")


if __name__ == "__main__":
    executar()
