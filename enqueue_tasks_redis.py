import redis
import os

REDIS_HOST = 'localhost'
REDIS_PORT = 6379
NUM_CHUNKS = 10

try:
    r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=0)
    r.ping()
    print("✅ Conectado ao Redis!")
except redis.ConnectionError:
    print("❌ Falha ao conectar ao Redis. Verifique se o servidor está rodando.")
    exit(1)

for i in range(NUM_CHUNKS):
    chunk_name = f'chunk{i}.txt'
    if not os.path.exists(os.path.join('data', chunk_name)):
        print(f"❌ Arquivo {chunk_name} não encontrado em 'data/'.")
        exit(1)
    r.rpush('mapper_tasks', chunk_name)

print(f"✅ {NUM_CHUNKS} tarefas enfileiradas no Redis (fila 'mapper_tasks').")