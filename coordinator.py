import os
import time
import redis
from shuffler import shuffle

REDIS_HOST = 'localhost'
REDIS_PORT = 6379
NUM_CHUNKS = 10
NUM_REDUCERS = 3

class Coordinator:
    def __init__(self):
        self.r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=0)
        self.pubsub = self.r.pubsub()
        self.mapper_complete_count = 0
        self.reducer_complete_count = 0

    def enqueue_mapper_tasks(self):
        for i in range(NUM_CHUNKS):
            self.r.rpush('mapper_tasks', f'chunk{i}.txt')
        print(f"✅ {NUM_CHUNKS} tarefas de mapeamento enfileiradas")

    def wait_for_mappers(self):
        self.pubsub.subscribe('mapper_complete')
        print("Aguardando mappers finalizarem...")
        
        for message in self.pubsub.listen():
            if message['type'] == 'message':
                self.mapper_complete_count += 1
                print(f"Mapper {message['data']} concluído ({self.mapper_complete_count}/{NUM_CHUNKS})")                
                if self.mapper_complete_count >= NUM_CHUNKS:
                    self.pubsub.unsubscribe('mapper_complete')
                    break

    def trigger_shuffle(self):
        print("🔄 Iniciando fase de shuffle...")
        shuffle()
        print("✅ Shuffle concluído")

    def enqueue_reducer_tasks(self):
        for i in range(NUM_REDUCERS):
            self.r.rpush('reducer_tasks', f'reducer_{i}_input.json')
        print(f"✅ {NUM_REDUCERS} tarefas de redução enfileiradas")

    def wait_for_reducers(self):
        self.pubsub.subscribe('reducer_complete')
        print("Aguardando reducers finalizarem...")
        
        for message in self.pubsub.listen():
            if message['type'] == 'message':
                self.reducer_complete_count += 1
                print(f"Reducer {message['data']} concluído ({self.reducer_complete_count}/{NUM_REDUCERS})")
                
                if self.reducer_complete_count >= NUM_REDUCERS:
                    self.pubsub.unsubscribe('reducer_complete')
                    break

    def merge_results(self):
        print("🔄 Consolidando resultados...")
        final_result = {}
        
        for i in range(NUM_REDUCERS):
            output_file = f"outputs/reducer_{i}_output.txt"
            if os.path.exists(output_file):
                with open(output_file, 'r') as f:
                    for line in f:
                        word, count = line.strip().split('\t')
                        final_result[word] = final_result.get(word, 0) + int(count)
        
        with open('final_result.txt', 'w') as f:
            for word, count in sorted(final_result.items()):
                f.write(f"{word}\t{count}\n")
        
        print(f"✅ Resultado final gerado em final_result.txt ({len(final_result)} palavras)")

    def run(self):
        try:
            self.enqueue_mapper_tasks()
            self.wait_for_mappers()

            self.trigger_shuffle()
            
            self.enqueue_reducer_tasks()
            self.wait_for_reducers()
            
            self.merge_results()
            
            print("🎉 Processo MapReduce concluído com sucesso!")
        except Exception as e:
            print(f"❌ Erro no coordinator: {str(e)}")
            raise

if __name__ == "__main__":
    coordinator = Coordinator()
    coordinator.run()