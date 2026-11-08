# Estrutura dos dados

## `data/ocorrencias.csv` (separador `;`, com cabeçalho)

| Campo | Obrigatório | Descrição |
|---|---|---|
| `id` | sim | Código único de 3 dígitos (ex.: `014`) |
| `categoria` | sim | `iluminacao`, `acessibilidade`, `limpeza` ou `conservacao` |
| `descricao` | sim | Descrição breve, sem dados pessoais |
| `bairro` | sim | Bairro fictício |
| `local` | sim | Local genérico (ex.: Praça Central) |
| `dia_abertura` | sim | Dia simulado (inteiro positivo) |
| `status` | sim | `aberta`, `em_analise` ou `concluida` |

## `data/historico.csv`

| Campo | Descrição |
|---|---|
| `id` | Código da ocorrência |
| `dia` | Dia simulado da mudança |
| `status_anterior` / `status_novo` | Situações antes e depois |

## Significado das situações

- **aberta:** demanda registrada e ainda não examinada (fica na fila).
- **em_analise:** demanda examinada, aguardando solução.
- **concluida:** demanda resolvida (simulado). Não pode mais mudar.

## Registros inconsistentes (de propósito)

- `015`: categoria ausente → recusado (campo obrigatório ausente).
- `016`: situação `pausada` → recusado (situação desconhecida).
