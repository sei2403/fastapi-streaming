import pandas as pd
from matplotlib import pyplot as plt
import os
import json
from read_files import get_folders
from tqdm import tqdm

# CSV file main directories
MEMORY = {
    'sr': 'results/raw_data_0801_1134/multi/memory/sr/',
    'sse': 'results/raw_data_0801_1134/multi/memory/sse/',
    'ws': 'results/raw_data_0801_1134/multi/memory/ws/'
}
TIME = {
    'sr': 'results/raw_data_0801_1134/multi/time/sr/',
    'sse': 'results/raw_data_0801_1134/multi/time/sse/',
    'ws': 'results/raw_data_0801_1134/multi/time/ws/'
}
FILE_SIZES = [5120 * (2 ** i) for i in range(10)]

def draw_line(df: pd.DataFrame, title: str, x_label: str, y_label: str, x_value: list) -> None:
    """ Generate a line graph from a pandas DataFrame. You are in charge of clearing, vieweing, or saving the graph."""
    for column in df.columns:
        plt.plot(x_value, df[column], label=column)
    plt.title(title)
    plt.xlabel(x_label)
    plt.ylabel(y_label)
    plt.legend()
    plt.grid()

def x_file(csv_file: str, title: str, cc = 8, aggregate = lambda x: x.mean(), chunk_ids = [1,3,5,7,9], memory_mode=False) -> None:
    """Generate a linegraph of the time taken to transfer a file between clients for different number of clients.

    Args:
        csv_file (str): The name of the csv file to read from.
        title (str): The title of the graph.
        cc (int, optional): The number of clients that you want to graph. Defaults to 8.
        aggregate (function, optional): The function to apply to the data. Defaults to lambda x: x.mean().
        memory_mode (bool, optional): Whether you want to graph memory usage instead of time. Defaults to False.
    """

    MAIN_FOLDERS = MEMORY if memory_mode else TIME

    method_average_values = {}
    sr_value = []
    sse_value = []
    ws_value = []

    for ptype in MAIN_FOLDERS.keys():
        for chunk_id in tqdm(chunk_ids):
            file = get_folders({ptype: MAIN_FOLDERS.get(ptype)}, client_count=cc, chunk_id=chunk_id)[0]

            with open(f'{file}/metadata.json', 'r') as f:
                metadata = json.load(f)
                method = metadata.get('method')
            if method == 'sr':
                with open(f'{file}/{csv_file}.csv', 'r') as F:
                    df = pd.read_csv(F)
                    aggregated_value = aggregate(df['StreamingResponse'])
                    sr_value.append(aggregated_value)
                
            elif method == 'sse':
                with open(f'{file}/{csv_file}.csv', 'r') as F:
                    df = pd.read_csv(F)
                    aggregated_value = aggregate(df['SSE'])
                    sse_value.append(aggregated_value)
                
            elif method == 'ws':
                with open(f'{file}/{csv_file}.csv', 'r') as F:
                    df = pd.read_csv(F)
                    aggregated_value = aggregate(df['WebSocket'])
                    ws_value.append(aggregated_value)
            
    method_average_values['Streaming Response'] = sr_value
    method_average_values['SSE'] = sse_value
    method_average_values['WebSocket'] = ws_value
    file_size_df = pd.DataFrame.from_dict(method_average_values, orient='index')
    file_size_df = file_size_df.transpose()

    draw_line(file_size_df, f'{title} ({cc} Clients)', 'Full Request Size', 'Memory Usage (MB)' if memory_mode else 'Time (s)', [f'{FILE_SIZES[i]/2048}KB' for i in chunk_ids])

    # create directory if it doesn't exist
    if not os.path.exists(f'results/graphs/{csv_file}/x_file_{cc}c'):
        os.makedirs(f'results/graphs/{csv_file}/x_file_{cc}c')
    
    print(f'Saving line graph to results/graphs/{csv_file}/x_file_{cc}c/linegraph.png')

    plt.savefig(f'results/graphs/{csv_file}/x_file_{cc}c/linegraph.png')

def x_client(csv_file: str, title: str, ci = 5, aggregate = lambda x: x.mean(), client_counts = [1,8,16,50,100,150,200], memory_mode=False) -> None:
    """Generate a linegraph of the time taken to transfer a file between clients for different file sizes.

    Args:
        csv_file (str): The name of the csv file to read from.
        title (str): The title of the graph.
        ci (int, optional): The chunk ID that you want to graph. Defaults to 5.
        aggregate (_type_, optional): How you aggregate your data. Defaults to lambdax:x.mean().
        client_counts (list, optional): The number of clients to graph. Defaults to [1,8,16,50,100,150,200].
        memory_mode (bool, optional): Whether you want to graph memory usage instead of time. Defaults to False.
    """

    MAIN_FOLDERS = MEMORY if memory_mode else TIME

    method_average_values = {}
    sr_value = []
    sse_value = []
    ws_value = []

    for ptype in MAIN_FOLDERS.keys():
        for cc in tqdm(client_counts):
            file = get_folders({ptype: MAIN_FOLDERS.get(ptype)}, client_count=cc, chunk_id=ci)[0]

            with open(f'{file}/metadata.json', 'r') as f:
                metadata = json.load(f)
                method = metadata.get('method')
            if method == 'sr':
                with open(f'{file}/{csv_file}.csv', 'r') as F:
                    df = pd.read_csv(F)
                    aggregated_value = aggregate(df['StreamingResponse'])
                    sr_value.append(aggregated_value)
                
            elif method == 'sse':
                with open(f'{file}/{csv_file}.csv', 'r') as F:
                    df = pd.read_csv(F)
                    aggregated_value = aggregate(df['SSE'])
                    sse_value.append(aggregated_value)
                
            elif method == 'ws':
                with open(f'{file}/{csv_file}.csv', 'r') as F:
                    df = pd.read_csv(F)
                    aggregated_value = aggregate(df['WebSocket'])
                    ws_value.append(aggregated_value)
            
    method_average_values['Streaming Response'] = sr_value
    method_average_values['SSE'] = sse_value
    method_average_values['WebSocket'] = ws_value
    file_size_df = pd.DataFrame.from_dict(method_average_values, orient='index')
    file_size_df = file_size_df.transpose()

    for key in file_size_df:
        file_size_df[key] = sorted(file_size_df[key])
    
    draw_line(file_size_df, f'{title} ({FILE_SIZES[ci] / 2048}KB)', 'Number of Clients', 'Memory Usage (MB)' if memory_mode else 'Time (s)', [str(c) for c in client_counts])

    # create directory if it doesn't exist
    if not os.path.exists(f'results/graphs/{csv_file}/x_client_{FILE_SIZES[ci] / 2048}kb'):
        os.makedirs(f'results/graphs/{csv_file}/x_client_{FILE_SIZES[ci] / 2048}kb')
    
    print(f'Saving line graph to results/graphs/{csv_file}/x_client_{FILE_SIZES[ci] / 2048}kb/linegraph.png')
    plt.savefig(f'results/graphs/{csv_file}/x_client_{FILE_SIZES[ci] / 2048}kb/linegraph.png')

if __name__ == '__main__':
    for i in [1,8,16]:
        plt.figure(figsize=(10, 4.8))
        x_file('server_full_time', 'Mean Server Full Time', aggregate=lambda x: x.mean(), cc=i, chunk_ids=[1,3,5,7,9])
        plt.close()
    for i in [50, 100, 150, 200]:
        plt.figure(figsize=(10, 4.8))
        x_file('server_full_time', 'Mean Server Full Time', aggregate=lambda x: x.mean(), cc=i, chunk_ids=[1,3])
        plt.close()
    for i in [1,3]:
        plt.figure(figsize=(10, 4.8))
        x_client('server_full_time', 'Mean Server Full Time', aggregate=lambda x: x.mean(), ci=i, client_counts=[1,8,16,50,100,150,200])
        plt.close()
    for i in [5,7,9]:
        plt.figure(figsize=(10, 4.8))
        x_client('server_full_time', 'Mean Server Full Time', aggregate=lambda x: x.mean(), ci=i, client_counts=[1,8,16])
        plt.close()

    for i in [1,2,4]:
        plt.figure(figsize=(10, 4.8))
        x_file('server_memory_usage', 'Maximum Server Memory Usage (Per Connection)', aggregate=lambda x: x.max(), cc=i, chunk_ids=[1,3,5,7], memory_mode=True)
        plt.close()
    
    for i in [1,3,5,7]:
        plt.figure(figsize=(10, 4.8))
        x_client('server_memory_usage', 'Maximum Server Memory Usage (Per Connection)', aggregate=lambda x: x.max(), ci=i, client_counts=[1,2,4], memory_mode=True)
        plt.close()
