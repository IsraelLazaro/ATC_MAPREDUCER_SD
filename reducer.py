import os
import json
import redis
import time

REDUCER_INPUT_DIR = "reducer_inputs"
OUTPUT_DIR = "outputs"
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

def reduce_worker(reducer_id):
    r = get_redis_connection()
    input_file = os.path.join(REDUCER_INPUT_DIR, f"reducer_{reducer_id}_input.json")
    output_file = os.path.join(OUTPUT_DIR, f"reducer_{reducer_id}_output.txt")
    
    try:
        os.makedirs(OUTPUT_DIR, exist_ok=True)

        with open(input_file, 'r', encoding='utf-8') as f_in:
            data = json.load(f_in)
        
        with open(output_file, 'w', encoding='utf-8') as f_out:
            for word, counts in sorted(data.items()):
                total = sum(counts)
                f_out.write(f"{word}\t{total}\n")  

        try:
            r.publish('reducer_complete', str(reducer_id))
            print(f"✅ Reducer {reducer_id} concluído e notificado")
        except redis.RedisError:
            print(f"⚠️ Reducer {reducer_id} concluído, mas falha ao notificar")

    except FileNotFoundError:
        print(f"❌ Arquivo de entrada {input_file} não encontrado")
    except json.JSONDecodeError:
        print(f"❌ Erro ao decodificar {input_file} (formato inválido)")
    except Exception as e:
        print(f"❌ Erro crítico no reducer {reducer_id}: {str(e)}")

if __name__ == "__main__":
    r = get_redis_connection()
    for reducer_id in range(3): 
        max_retries = 3
        for attempt in range(max_retries):
            try:
                reduce_worker(reducer_id)
                break
            except redis.ConnectionError:
                if attempt == max_retries - 1:
                    print(f"❌ Falha definitiva no reducer {reducer_id}")
                time.sleep(2)
    
    print("🎉 Processo de redução finalizado!")