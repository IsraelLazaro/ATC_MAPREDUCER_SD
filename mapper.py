import redis
import os
import re
import time

REDIS_HOST = 'localhost'
REDIS_PORT = 6379

def get_redis_connection():
    return redis.Redis(
        host=REDIS_HOST,
        port=REDIS_PORT,
        db=0,
        decode_responses=True,
        socket_connect_timeout=5,
        retry_on_timeout=True
    )

def map_function(line):
    cleaned = re.sub(r'[^\w\s]', '', line.lower())
    words = cleaned.strip().split()
    return [(word, 1) for word in words if word]

def mapper_worker():
    r = get_redis_connection()
    print("🚀 Mapper worker iniciado. Aguardando tarefas...")
    
    while True:
        try:
            chunk_file = r.lpop('mapper_tasks')
            if not chunk_file:
                print("✅ Fila vazia. Mapper finalizado.")
                break

            output_file = f"intermediate/{os.path.splitext(chunk_file)[0]}.out"
            os.makedirs("intermediate", exist_ok=True)

            try:
                with open(f'data/{chunk_file}', 'r', encoding='utf-8', errors='replace') as f_in, \
                     open(output_file, 'w', encoding='utf-8') as f_out:
                    
                    for line in f_in:
                        for word, count in map_function(line):
                            f_out.write(f"{word}\t{count}\n")

                r.publish('mapper_complete', chunk_file)
                print(f"✅ {chunk_file} processado -> {output_file}")

            except FileNotFoundError:
                print(f"❌ Arquivo {chunk_file} não encontrado")
                r.rpush('mapper_tasks', chunk_file)  
                time.sleep(1)
                
            except Exception as e:
                print(f"❌ Erro crítico em {chunk_file}: {str(e)}")

        except redis.RedisError as e:
            print(f"⚠️ Erro no Redis, reconectando... ({str(e)})")
            r = get_redis_connection()
            time.sleep(2)

if __name__ == "__main__":
    mapper_worker()