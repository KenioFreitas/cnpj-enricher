# CNPJ Enricher — Enriquecimento Online de CNPJs

Ferramenta Python para enriquecimento de bases de CNPJs com dados cadastrais atualizados diretamente da Receita Federal, via API pública.

## O problema

As bases da Receita Federal armazenam dados de ~65 milhões de CNPJs **congelados no momento de abertura** da empresa — endereço, sócios, situação cadastral e atividade econômica frequentemente desatualizados.

Isso compromete qualquer análise de carteira, prospecção B2B ou qualificação de leads que dependa dessas informações.

Esta ferramenta consulta a API [minhareceita.org](https://minhareceita.org) — que mantém os dados sincronizados com a RFB — e devolve uma base enriquecida com informações reais e atuais.

## Funcionalidades

- Lê arquivo `.xlsx` ou `.csv` com coluna `CNPJ`
- Consulta dados atualizados via API para cada CNPJ
- Processamento paralelo com até 10 requisições simultâneas (`ThreadPoolExecutor`)
- Barra de progresso em tempo real (`tqdm`)
- Salva resultado enriquecido na pasta `saida/`
- Trata CNPJs inválidos e erros de API com coluna `erro`

## Campos retornados

| Campo | Descrição |
|---|---|
| `cnpj` | CNPJ original da entrada |
| `razao_social` | Razão social |
| `nome_fantasia` | Nome fantasia |
| `situacao_cadastral` | Ativa, Baixada, Inapta etc. |
| `data_situacao` | Data da última alteração de situação |
| `motivo_situacao` | Motivo de encerramento (se aplicável) |
| `socios` | Nomes dos sócios (QSA) |
| `cnae_principal` | Descrição da atividade principal |
| `capital_social` | Capital social declarado |
| `data_inicio_atividade` | Data de abertura |
| `logradouro` | Endereço completo |
| `municipio` / `uf` | Localização |
| `telefone` | Telefone cadastrado |
| `email` | E-mail cadastrado |
| `erro` | Mensagem de erro (se houver) |

## Como usar

### 1. Instalar dependências

```bash
pip install -r requirements.txt
```

### 2. Preparar o arquivo de entrada

Coloque um arquivo `.xlsx` ou `.csv` na raiz do projeto com pelo menos uma coluna chamada `CNPJ`.

Coluna `number` é opcional — se existir, é preservada no output.

Veja o exemplo em [`exemplo/exemplo_entrada.xlsx`](exemplo/exemplo_entrada.xlsx).

### 3. Executar

```bash
python main.py
```

O arquivo enriquecido será salvo em `saida/` com o mesmo nome do arquivo de entrada.

## Exemplo de entrada

| CNPJ | number |
|---|---|
| 00.000.000/0001-91 | |
| 33.000.167/0001-01 | |

## Estrutura do projeto

```
cnpj-enricher/
├── main.py               # Script principal
├── requirements.txt      # Dependências Python
├── .gitignore
├── exemplo/
│   └── exemplo_entrada.xlsx   # Arquivo de exemplo
└── saida/                # Outputs gerados (não versionado)
```

## Dependências

- [pandas](https://pandas.pydata.org/) — manipulação de dados
- [requests](https://docs.python-requests.org/) — requisições HTTP
- [tqdm](https://tqdm.github.io/) — barra de progresso
- [openpyxl](https://openpyxl.readthedocs.io/) — leitura e escrita de `.xlsx`
- API: [minhareceita.org](https://minhareceita.org) — dados da RFB atualizados

## Notas

- O script processa o **primeiro** arquivo `.xlsx` ou `.csv` encontrado na raiz (ordem alfabética).
- CNPJs com formato inválido (≠ 14 dígitos) são marcados na coluna `erro` e não bloqueiam o processamento.
- O paralelismo padrão é de 10 workers simultâneos — ajuste `MAX_CONCURRENT_REQUESTS` em `main.py` conforme sua conexão e os limites da API.
- A API minhareceita.org é pública e gratuita; respeite os limites de uso.

## Licença

MIT
