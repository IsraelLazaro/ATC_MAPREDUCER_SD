# 🗂️➡️🧮➡️📦MapReduce com Redis <img src="https://www.ifpb.edu.br/prpipg/pasta-imagens-da-prpipg/logoifpb.png" alt="IFPB" width="70"/>



Projeto desenvolvido para implementar um sistema MapReduce distribuído, dividido em três etapas principais:
### ➡️ Mapper Workers
- #### Crie trabalhadores mapeadores
### ➡️ Shuffle Phase
- #### Depois que todos os mapeadores terminarem, iniciar processo de embaralhamento
### ➡️ Reducer Workers
- ####  Crie trabalhadores redutores
---

##  🔨 Estrutura principal

- **Redis (via Docker)**: atua como message broker para enfileirar tarefas e enviar notificações entre workers.
- **Mapper Workers**: processam arquivos de texto e emitem pares (palavra, 1).
- **Shuffler**: reorganiza os pares em valores por chave (por exemplo, "olá": [1, 1, 1, 1]) e por reducer.
- **Reducer Workers**: somam as ocorrências de cada palavra.
- **Coordinator**: orquestra o pipeline completo.

---

##  🛠 Preparar o ambiente

### 1. 📦 Requisitos
- VSCode
- Python 3.8+
- Redis (Docker recomendado)
- Bibliotecas Python:
  - Redis
  - os, json, re, time
```
  pip install redis
```
### 2. 🏗 Estrutura do Projeto
- 📦ATV_REDUCER_SD
    - ├── `📂data`               ➡️ Dados de entrada (chunk0.txt, ...)
    - ├── `📂intermediate`       ➡️ Saída dos mappers (*.out)
    - ├── `📂reducer_inputs `    ➡️ Dados agrupados (*.json)
    - ├── `📂outputs `           ➡️ Resultados finais (*.txt)
    - ├── `📜enqueue_tasks_redis.py`     ➡️ Enfileira as tarefas no Redis
    - ├── `📜coordinator.py`     ➡️ Orquestrador
    - ├── `📜mapper.py `         ➡️ Worker de mapeamento
    - ├── `📜split_file.py`      ➡️ divide o arquivo data.txt em 10 partes (chunk0.txt a chunk9.txt)
    - ├── `📜reducer.py `        ➡️ Worker de redução
    - └── `📜shuffler.py`        ➡️ Fase de shuffle

### 3. ⚙️ Instalar o container Redis no Docker

- Criar container `redis-ifpb`:

```
docker run -d --name redis-ifpb -p 6379:6379 redis
```

### 4. ✅ Procedimentos iniciais e criação do arquivo txt (sugestão)

- Vá para o diretório `data/`
```
cd data
```
- Baixe o arquivo para realizar as tarefas
```
curl -o data.txt https://www.gutenberg.org/cache/epub/26484/pg26484.txt
```
- Use o arquivo `split_file.py` para criar as chunks na pasta data com os comandos
```
cd ..
```
```
python split_file.py
```

## ▶️ Execução do projeto
### Executar o coordinator.py
- Abra dois terminais no VSCode (ou duas abas)
#### 👨‍💻 TERMINAL 01 
```
python coordinator.py
```
#### Saída ----->
- >*✅ 10 tarefas de mapeamento enfileiradas*
- >*Aguardando mappers...*
- >*Aguardando mappers finalizarem...*

#### 👨‍💻 TERMINAL 02 
```
python mapper.py
```
#### 👨‍💻 TERMINAL 01 
#### Saída ----->
- >*🔄 Iniciando fase de shuffle...*
- >*✅ Shuffle concluído*
- >*✅ 3 tarefas de redução enfileiradas*
- >*Aguardando reducers finalizarem...*

#### 👨‍💻 TERMINAL 02 
```
python reducer.py
```
#### 👨‍💻 TERMINAL 01 
#### Saída ----->
- >*🎉 Processo MapReduce concluído com sucesso!*

## 📊 Resultados
O resultado final estará disponível no arquivo *`final_result.txt`* na raiz do projeto

## Sequência do Processo do MapReducer

- `Coordinator` → Envia chunks para mapper_tasks
- `Mappers` → Processam e salvam em intermediate/
- `Shuffler` → Agrupa palavras por hash
- `Reducers` → Somam ocorrências
- `Coordinator` → Gera final_result.txt

### Pub/Sub
  - `mapper_complete `→ Notificação de mappers
  - `reducer_complete` → Notificação de reducers

## 👤 Autor
- Projeto desenvolvido por Israel Lázaro M. Tavares

## 📝 Licença
- Este projeto está sob a licença MIT.