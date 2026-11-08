# Uso de Inteligência Artificial

## Como a IA apoiou o desenvolvimento

Foi utilizada a IA Claude (Anthropic) para:

- estruturar o repositório conforme o modelo da coordenação;
- gerar o conjunto de dados fictícios (`data/`);
- propor a primeira versão do código de `src/sistema.py` e do `README.md`;
- revisar a documentação.

## Como os resultados foram verificados

- O programa foi executado com entradas simuladas (cadastro válido, cadastro sem campos, telefone na descrição, código inexistente, mudança de status inválida, concluída tentando mudar).
- Os indicadores foram conferidos à mão: 14 válidas (7 abertas, 4 em análise, 3 concluídas) e tempo médio (3 + 8 + 6) / 3 = 5,7 dias.
- Todo o código usa apenas conteúdos das Fases 1 a 3.

## Compromisso da equipe

_(A equipe deve ler, testar e conseguir explicar cada parte do código antes da entrega; ajustar este texto se alterar algo.)_
