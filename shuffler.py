import os
import json
from collections import defaultdict
from hashlib import sha1

NUM_REDUCERS = 3
INTERMEDIATE_DIR = "intermediate"
REDUCER_INPUT_DIR = "reducer_inputs"

def hash_key(key):
    return int(sha1(key.encode('utf-8')).hexdigest()[:8], 16) % NUM_REDUCERS

def shuffle():
    os.makedirs(REDUCER_INPUT_DIR, exist_ok=True)
    
    word_groups = defaultdict(list)
    
    for filename in os.listdir(INTERMEDIATE_DIR):
        if not filename.endswith('.out'):
            continue
            
        with open(os.path.join(INTERMEDIATE_DIR, filename), 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    word, count = line.strip().split('\t')
                    word_groups[word].append(int(count))
                except ValueError:
                    continue

    reducers = [defaultdict(list) for _ in range(NUM_REDUCERS)]
    
    for word, counts in word_groups.items():
        reducer_id = hash_key(word)
        reducers[reducer_id][word] = counts

    for reducer_id, data in enumerate(reducers):
        output_file = os.path.join(REDUCER_INPUT_DIR, f'reducer_{reducer_id}_input.json')
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write('{\n')  

            items = []
            for word in sorted(data.keys()):  
                counts = data[word]
                items.append(f'  "{word}": {json.dumps(counts)}')
            
            f.write(',\n'.join(items))  
            f.write('\n}\n')

if __name__ == "__main__":
    shuffle()