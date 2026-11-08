# Neighborhood Action Dashboard

Global Solution – 2º Semestre de 2026 · Desafio **CitizenTech** · Fase 4

## 1. Equipe

**Equipe:** individual (1 integrante)

| Integrante | RM |
|---|---|
| João Victor Bertholdo Silva de Oliveria | 576506 |

## 2. Bairro simulado, problema e público beneficiado

Bairro fictício **Jardim Aurora / Vila Esperança / Centro Novo** (três bairros de uma cidade imaginária). Problemas cotidianos de infraestrutura (poste apagado, calçada com buraco, lixeira transbordando, banco quebrado) ficam espalhados em relatos soltos, sem prioridade clara, e o morador não sabe em que pé está sua solicitação.

O **Neighborhood Action Dashboard** é um painel textual que registra, organiza e acompanha essas ocorrências, e resume indicadores para a comunidade.

**Público beneficiado:** moradores (que acompanham o andamento), associações de bairro (que identificam problemas frequentes) e pessoas com mobilidade reduzida (categoria Acessibilidade em destaque).

> Todos os dados são **fictícios**. Não há integração com órgãos públicos nem promessa de atendimento.

## 3. Estruturas de dados e justificativas

| Estrutura | Onde é usada | Por que |
|---|---|---|
| **Lista** (`estado["lista"]`) | Todas as ocorrências em ordem de registro | Permite percorrer o conjunto com laços (listagem, filtros, indicadores) |
| **Dicionário** (`estado["indice"]`) | Código → ocorrência | Acesso direto pelo código, sem percorrer a lista toda |
| **Fila** (`estado["fila"]`) | Códigos com status `aberta` | Demandas devem ser examinadas por ordem de chegada (primeiro a entrar, primeiro a sair: `fila[0]`, `remove`) |
| **Pilha** (`estado["pilha"]`) | Eventos de mudança de status | O evento mais recente fica no topo (`append`/`pop`), ideal para "últimas atualizações" |
| **Hierarquia** (dicionário aninhado) | bairro → categoria → códigos | Mostra onde cada tipo de problema se concentra |
| **Matriz** (lista de listas) | Categoria × situação | Resume quantidades em uma tabela 4×3 usada nos indicadores |

## 4. Regras lógicas principais

**Formato dos dados** (`data/ocorrencias.csv`, separador `;`): `id; categoria; descricao; bairro; local; dia_abertura; status`. Todos os campos são obrigatórios. Detalhes em [`docs/estrutura_dados.md`](docs/estrutura_dados.md).

**Situações:** `aberta` (registrada, ainda não examinada) → `em_analise` (examinada, aguardando solução) → `concluida` (resolvida, simulado).

**Cadastro / validação** (`validar_ocorrencia`):
- recusa registro com campo obrigatório vazio;
- recusa categoria ou situação fora do conjunto padronizado;
- recusa dia inválido ou código duplicado;
- recusa texto com `@` ou 8+ dígitos (possível e-mail/telefone: privacidade).

**Consulta:** por código (`buscar_por_codigo`) e filtro por categoria e/ou situação. Código inexistente gera mensagem clara.

**Atualização:** só são permitidas `aberta → em_analise` e `em_analise → concluida`. Situação desconhecida, ocorrência concluída ou salto de etapa são recusados e nada é alterado. Cada mudança entra no histórico e na pilha.

### Expressão booleana documentada (filtro)

```python
if (categoria == "" or o["categoria"] == categoria) and \
   (status == "" or o["status"] == status):
    resultado.append(o)
```

Explicação: cada parêntese representa um filtro opcional. `categoria == ""` significa "não filtrar por categoria", então o primeiro parêntese é verdadeiro para qualquer ocorrência. Se houver categoria, só é verdadeiro quando ela coincide. O mesmo vale para o status. O `and` exige que os dois filtros sejam satisfeitos. Ex.: filtrar `iluminacao` + `aberta` mantém apenas as ocorrências que são das duas coisas ao mesmo tempo; deixar ambos vazios devolve tudo.

Outros usos de AND/OR/NOT: campos obrigatórios (`or`), categoria desconhecida (`not in`), data inválida (`not ... or ...`), pendências (`not concluida`), concluída que não pode mudar (`==` + `not in TRANSICOES`).

## 5. Indicadores, fórmulas e interpretação

| Indicador | Fórmula / regra |
|---|---|
| Total e proporção por categoria | `qtd_categoria / total × 100` |
| Total e proporção por situação | `qtd_situação / total × 100` |
| Matriz categoria × situação | contagem em laço sobre a lista |
| Tempo médio até a conclusão | média de `(dia_conclusão − dia_abertura)` das concluídas |
| Pendências | `aberta + em_analise` (status ≠ concluída) e a mais antiga |

**Resultado com os dados iniciais (14 ocorrências válidas, dia simulado 30):**

- Iluminação 4 (28,6%), Limpeza 4 (28,6%), Acessibilidade 3 (21,4%), Conservação 3 (21,4%).
- 7 abertas (50,0%), 4 em análise (28,6%), 3 concluídas (21,4%).
- Tempo médio até a conclusão: (3 + 8 + 6) / 3 = **5,7 dias**.
- Pendências: 11 (78,6%).

**Interpretação:** iluminação e limpeza concentram as demandas, e a maioria ainda está pendente, sugerindo necessidade de acompanhamento mais ágil, principalmente das ocorrências abertas. Como os dados são simulados, o resultado ilustra o método e não a realidade.

## 6. Como executar

Requisito: Python 3 (sem bibliotecas externas). Na raiz do repositório:

```bash
python src/sistema.py
```

## 7. Exemplo de uso

Menu principal (resumo): `1` listar · `2` cadastrar · `3` consultar · `4` filtrar · `5` atualizar situação · `6` examinar próxima da fila · `7` fila · `8` eventos recentes · `9` indicadores · `10` hierarquia · `11` registros recusados · `0` sair.

```text
Dados carregados: 14 ocorrências válidas, 2 registros recusados, 10 eventos de histórico.

Escolha uma opção: 2
Escolha o número da categoria: 3
Descrição breve: Bueiro entupido com mau cheiro
Bairro: Centro Novo
Local genérico: Rua 5
Ocorrência 017 cadastrada com sucesso (status: Aberta).

Escolha uma opção: 3
Código da ocorrência (ex.: 014): 017
Código.........: 017
Categoria......: Limpeza
Status.........: Aberta
Dias em acompanhamento: 0

Escolha uma opção: 5
Código da ocorrência: 017
Escolha o número da situação: 2
Ocorrência 017 atualizada: Aberta -> Em análise.

Escolha uma opção: 5            (tentativa inválida)
Código da ocorrência: 003
Escolha o número da situação: 3
Mudança não permitida: Aberta -> Concluída. Fluxo permitido: Aberta -> Em análise -> Concluída.

Escolha uma opção: 0
Encerrando o painel. Obrigado por acompanhar as demandas do bairro!
```

Os registros `015` (categoria ausente) e `016` (situação `pausada`) do CSV são inconsistentes de propósito: a validação os recusa e a opção `11` mostra o motivo.

## 8. Acessibilidade, inclusão e privacidade

- **Acessibilidade:** interface só de texto, com menu numerado, mensagens curtas e explícitas (compatível com leitores de tela), sem depender de cor, som ou mouse; listagem em colunas alinhadas; categoria dedicada à acessibilidade urbana.
- **Inclusão:** linguagem simples, sem jargão; mensagens de erro dizem o que aconteceu e como corrigir.
- **Privacidade:** dados fictícios, local genérico (sem endereço exato), nenhum nome de morador; a validação bloqueia e-mails e telefones digitados na descrição.

## 9. Vídeo de apresentação

_(colar aqui o link do YouTube "Não Listado")_

## 10. Conclusões, limitações e aprendizados

- **Conclusões:** estruturas simples (lista, dicionário, fila, pilha, matriz) bastam para organizar e acompanhar demandas; cada uma resolve uma necessidade diferente.
- **Limitações:** dados em memória (mudanças não são gravadas no CSV); sem integração com serviços públicos; dias simulados em vez de datas reais; poucos registros, então os indicadores não representam uma comunidade real.
- **Aprendizados:** escolher a estrutura certa simplifica o algoritmo; validar a entrada evita dados inconsistentes; explicar a regra de cada indicador torna o resultado compreensível.

## Estrutura do repositório

```text
data/        ocorrencias.csv, historico.csv (dados fictícios)
docs/        estrutura_dados.md, uso_ia.md
notebooks/   analise_indicadores.ipynb
src/         sistema.py
README.md
```

## Uso de IA

Registrado em [`docs/uso_ia.md`](docs/uso_ia.md).
