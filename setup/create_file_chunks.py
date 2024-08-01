import os
from tqdm import tqdm

def create_file_chunks(input_file, output_dir):
    # Define the sizes in bytes (since each Chinese character is 3 bytes, 5KB = 5120 bytes)
    sizes = [5120 * (2 ** i) for i in range(17)]  # Exponential increments

    # Read the input file content
    with open(input_file, 'r', encoding='utf-8') as file:
        content = file.read()

    # Ensure the output directory exists
    os.makedirs(output_dir, exist_ok=True)

    # Create the chunks
    for idx, size in enumerate(sizes):
        # Calculate the number of characters (each character is 3 bytes)
        num_chars = size // 3
        chunk_content = content[:num_chars]

        output_file = os.path.join(output_dir, f'chunk_{idx + 1}.txt')
        with open(output_file, 'w', encoding='utf-8') as chunk_file:
            chunk_file.write(chunk_content)
        print(f'Created {output_file} with size {os.path.getsize(output_file)} bytes')

# Usage example
input_file = 'output.txt'
output_dir = 'chunks'
create_file_chunks(input_file, output_dir)
