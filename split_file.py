import os

def split_file(input_file, num_chunks=10):
    os.makedirs('data', exist_ok=True)
    with open(input_file, 'r', encoding='utf-8', errors='replace') as f:
        lines = f.readlines()
    lines_per_chunk = len(lines) // num_chunks
    for i in range(num_chunks):
        chunk_path = os.path.join('data', f'chunk{i}.txt')
        start = i * lines_per_chunk
        end = (i + 1) * lines_per_chunk if i < num_chunks - 1 else len(lines)
        with open(chunk_path, 'w', encoding='utf-8') as chunk:
            chunk.writelines(lines[start:end])
    print(f"✅ Arquivo dividido em {num_chunks} chunks na pasta 'data/'.")

if __name__ == "__main__":
    split_file('./data/data.txt')