import pandas as pd
from matplotlib import pyplot as plt
import os
import json
import seaborn as sns
from tqdm import tqdm
from read_files import get_folders

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

def remove_outliers(df: pd.DataFrame) -> pd.DataFrame:
    """
    Remove outliers from a DataFrame. Outliers are defined as values that are below Q1 - 1.5 * IQR or above Q3 + 1.5 * IQR.
    """
    Q1 = df.quantile(0.25)
    Q3 = df.quantile(0.75)
    IQR = Q3 - Q1
    df = df[~((df < (Q1 - 1.5 * IQR)) | (df > (Q3 + 1.5 * IQR)))]
    df = df.dropna()
    return df

def x_file(csv_file: str, title: str, cc = 8, outliers=False, chunk_ids = [1,3,5,7,9], memory_mode=False) -> None:
    """Generate a boxplot of the time taken to transfer a file between clients for different number of clients.

    Args:
        csv_file (str): The name of the csv file to read from.
        title (str): The title of the graph.
        cc (int, optional): The number of clients that you want to graph. Defaults to 8.
        outliers (bool, optional): Whether you want to include outliers in your boxplot. Defaults to False.
        chunk_ids (list, optional): The number of chunk_ids to graph. Defaults to [1,3,5,7,9].
        memory_mode (bool, optional): Whether you want to graph memory usage instead of time. Defaults to False.
    """

    df = {}
    max_values = {}
    min_values = {}

    std_deviation = {}

    MAIN_FOLDERS = MEMORY if memory_mode else TIME

    for ptype in MAIN_FOLDERS.keys():
        pdf = pd.DataFrame()
        for chunk_id in tqdm(chunk_ids):
            folders = get_folders({ptype: MAIN_FOLDERS.get(ptype)}, client_count=cc, chunk_id=chunk_id)
            files = [f + f'/{csv_file}.csv' for f in folders]
            data = {}

            for f in files:
                dft = pd.read_csv(f, index_col=0)
                # Calculate max values
                if chunk_id not in max_values:
                    max_values[chunk_id] = {}
                max_values[chunk_id][ptype] = dft.max().iloc[0]

                # Calculate min values
                if chunk_id not in min_values:
                    min_values[chunk_id] = {}
                min_values[chunk_id][ptype] = dft.min().iloc[0]

                # Calculate standard deviation
                if chunk_id not in std_deviation:
                    std_deviation[chunk_id] = {}
                std_deviation[chunk_id][ptype] = dft.std().iloc[0]

                if not outliers:
                    dft = remove_outliers(dft)

                dft_columns = dft.iloc[:, 0].tolist()
                data[str(FILE_SIZES[chunk_id] / 2048) + 'KB'] = dft_columns

            pdf = pd.concat([pdf, pd.DataFrame(data)], axis=1)
        df[ptype] = pdf.melt()

    df = pd.concat(df, names=['source', 'old_index'])
    df = df.reset_index(level=0).reset_index(drop=True)
    print(f"Generating `{title} ({cc} Clients)` Graph")

    sns.boxplot(data=df, x='variable', y='value', hue='source', palette='turbo')

    # add max and min values to the plot at the top of the boxplot (data filtered without outliers)
    cnt = 0
    if not outliers:
        for chunk_id in max_values:
            tmp_top = ''
            tmp_bottom = ''
            scnt = 1
            for ptype in max_values[chunk_id]:
                tmp_top = f'{ptype}: {max_values[chunk_id][ptype]:.2e}'
                plt.text(cnt, plt.gca().get_ylim()[1]-(scnt * 5e-7), tmp_top, ha='center', va='bottom', fontsize=8, color='black')
                tmp_bottom = f'{ptype}: {min_values[chunk_id][ptype]:.2e} '
                plt.text(cnt, plt.gca().get_ylim()[0]+((3-scnt) * 5e-7), tmp_bottom, ha='center', va='bottom', fontsize=8, color='black')
                scnt += 1
            cnt += 1

    # create directory if it doesn't exist
    if not os.path.exists(f'results/graphs/{csv_file}/x_file_{cc}c'):
        os.makedirs(f'results/graphs/{csv_file}/x_file_{cc}c')

    # save the data
    with open(f'results/graphs/{csv_file}/x_file_{cc}c/std_deviation.json', 'w') as f:
        json.dump(std_deviation, f)
    with open(f'results/graphs/{csv_file}/x_file_{cc}c/max_values.json', 'w') as f:
        json.dump(max_values, f)
    with open(f'results/graphs/{csv_file}/x_file_{cc}c/min_values.json', 'w') as f:
        json.dump(min_values, f)

    plt.title(f'{title} ({cc} Clients)')
    plt.xlabel('Full Request Size' )
    plt.ylabel('Memory Usage (MB)' if memory_mode else 'Time (s)')
    # save the plot
    plt.savefig(f'results/graphs/{csv_file}/x_file_{cc}c/{'boxplot_all' if outliers else 'boxplot_no_outliers'}.png')

def x_client(csv_file: str, title: str, ci = 5, outliers = False, client_counts = [1,8,16,50,100,150,200], memory_mode=False) -> None:
    """ Generate a boxplot of the time taken to transfer a file between clients for different chunk ids.

    Args:
        csv_file (str): The name of the csv file to read from.
        title (str): The title of the graph.
        ci (int, optional): The chunk ID that you want to graph. Defaults to 5.
        outliers (bool, optional): Whether you want to include outliers in your boxplot. Defaults to False.
        client_counts (list, optional): The number of clients to graph. Defaults to [1,8,16,50,100,150,200].
        memory_mode (bool, optional): Whether you want to graph memory usage instead of time. Defaults to False.
    """

    df = {}
    max_values = {}
    min_values = {}

    std_deviation = {}

    MAIN_FOLDERS = MEMORY if memory_mode else TIME

    for ptype in MAIN_FOLDERS.keys():
        pdf = pd.DataFrame()
        for cc in tqdm(client_counts):
            folders = get_folders({ptype: MAIN_FOLDERS.get(ptype)}, client_count=cc, chunk_id=ci)
            files = [f + f'/{csv_file}.csv' for f in folders]
            data = {}

            for f in files:
                dft = pd.read_csv(f, index_col=0)
                # Calculate max values
                if cc not in max_values:
                    max_values[cc] = {}
                max_values[cc][ptype] = dft.max().iloc[0]

                # Calculate min values
                if cc not in min_values:
                    min_values[cc] = {}
                min_values[cc][ptype] = dft.min().iloc[0]

                # Calculate standard deviation
                if cc not in std_deviation:
                    std_deviation[cc] = {}
                std_deviation[cc][ptype] = dft.std().iloc[0]

                if not outliers:
                    dft = remove_outliers(dft)

                dft_columns = dft.iloc[:, 0].tolist()
                data[str(f'{cc} Clients')] = dft_columns

            pdf = pd.concat([pdf, pd.DataFrame(data)], axis=1)
        df[ptype] = pdf.melt()

    df = pd.concat(df, names=['source', 'old_index'])
    df = df.reset_index(level=0).reset_index(drop=True)
    print(f"Generating `{title} (Full File Size: {FILE_SIZES[ci]})` Graph")

    sns.boxplot(data=df, x='variable', y='value', hue='source', palette='turbo')
    
    # add max and min values to the plot at the top of the boxplot (data filtered without outliers)
    cnt = 0
    if not outliers:
        for cc in max_values:
            tmp_top = ''
            tmp_bottom = ''
            scnt = 1
            for ptype in max_values[cc]:
                tmp_top = f'{ptype}: {max_values[cc][ptype]:.2e}'
                plt.text(cnt, plt.gca().get_ylim()[1]-(scnt * 5e-7), tmp_top, ha='center', va='bottom', fontsize=8, color='black')
                tmp_bottom = f'{ptype}: {min_values[cc][ptype]:.2e} '
                plt.text(cnt, plt.gca().get_ylim()[0]+((3-scnt) * 5e-7), tmp_bottom, ha='center', va='bottom', fontsize=8, color='black')
                scnt += 1
            cnt += 1

    # create directory if it doesn't exist
    if not os.path.exists(f'results/graphs/{csv_file}/x_client_{FILE_SIZES[ci] / 2048}kb'):
        os.makedirs(f'results/graphs/{csv_file}/x_client_{FILE_SIZES[ci] / 2048}kb')

    # save the data
    with open(f'results/graphs/{csv_file}/x_client_{FILE_SIZES[ci] / 2048}kb/std_deviation.json', 'w') as f:
        json.dump(std_deviation, f)
    with open(f'results/graphs/{csv_file}/x_client_{FILE_SIZES[ci] / 2048}kb/max_values.json', 'w') as f:
        json.dump(max_values, f)
    with open(f'results/graphs/{csv_file}/x_client_{FILE_SIZES[ci] / 2048}kb/min_values.json', 'w') as f:
        json.dump(min_values, f)

    plt.title(f'{title} (Full File Size: {FILE_SIZES[ci] / 2048}KB)')
    plt.xlabel('Number of Clients')
    plt.ylabel('Memory Usage (MB)' if memory_mode else 'Time (s)')
    # save the plot
    plt.savefig(f'results/graphs/{csv_file}/x_client_{FILE_SIZES[ci] / 2048}kb/{'boxplot_all' if outliers else 'boxplot_no_outliers'}.png')

if __name__ == '__main__':
    for i in [1,3]:
        plt.figure(figsize=(10, 4.8))
        x_client('server_full_time', 'Server Full Time', ci=i, outliers=False, client_counts=[1,8,16,50,100,150,200])
        plt.close()
        plt.figure(figsize=(10, 4.8))
        x_client('server_full_time', 'Server Full Time', ci=i, outliers=True, client_counts=[1,8,16,50,100,150,200])
        plt.close()
    for i in [5,7,9]:
        plt.figure(figsize=(10, 4.8))
        # x_client(i, outliers=True)
        x_client('server_full_time', 'Server Full Time', ci=i, outliers=False, client_counts=[1,8,16])
        plt.close()
        plt.figure(figsize=(10, 4.8))
        x_client('server_full_time', 'Server Full Time', ci=i, outliers=True, client_counts=[1,8,16])
        plt.close()
