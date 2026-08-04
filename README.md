# Desafio técnico — Processamento em Lote

Conversor de um arquivo JSONL de clubes para dois arquivos CSV:

- `clubs.csv`: uma linha por clube da Série A ou Série B;
- `players.csv`: uma linha por jogador desses clubes.

O projeto usa apenas a biblioteca padrão do Python e processa a entrada linha a linha,
sem carregar o arquivo inteiro em memória. Registros JSON inválidos são informados na
saída de erro e ignorados, sem interromper os demais.

## Requisitos

- Python 3.10 ou superior.

Não é necessário instalar dependências externas.

## Como executar

Na raiz do projeto, informe o caminho do JSONL:

```bash
python3 main.py docs/sample_clubes.jsonl
```

Por padrão, `clubs.csv` e `players.csv` são criados no diretório atual. Para escolher
outro diretório:

```bash
python3 main.py docs/sample_clubes.jsonl --output-dir resultado
```

Os arquivos são sobrescritos a cada execução.

## Testes

Execute os testes automatizados com:

```bash
python3 -m unittest discover -s tests -v
```
