import linegraph
import boxplot
from matplotlib import pyplot as plt

LINE_GRAPHS = {
    'server_full_time': 'Mean Server Full Time',
    'between_chunks': 'Mean Time Between Chunks',
    'client_full_time': 'Mean Client Full Time',
}

BOXPLOTS = {
    'server_full_time': 'Server Full Time',
    'between_chunks': 'Time Between Chunks',
    'client_full_time': 'Client Full Time',
}

def generate_all():
    print("LINE GRAPHS: TIME")
    for g in LINE_GRAPHS:
        for i in [1,8,16]:
            plt.figure(figsize=(10, 4.8))
            linegraph.x_file(g, LINE_GRAPHS[g], aggregate=lambda x: x.mean(), cc=i, chunk_ids=[1,3,5,7,9])
            plt.close()
        for i in [50, 100, 150, 200]:
            plt.figure(figsize=(10, 4.8))
            linegraph.x_file(g, LINE_GRAPHS[g], aggregate=lambda x: x.mean(), cc=i, chunk_ids=[1,3])
            plt.close()
        for i in [1,3]:
            plt.figure(figsize=(10, 4.8))
            linegraph.x_client(g, LINE_GRAPHS[g], aggregate=lambda x: x.mean(), ci=i, client_counts=[1,8,16,50,100,150,200])
            plt.close()
        for i in [5,7,9]:
            plt.figure(figsize=(10, 4.8))
            linegraph.x_client(g, LINE_GRAPHS[g], aggregate=lambda x: x.mean(), ci=i, client_counts=[1,8,16])
            plt.close()
    
    print("LINE GRAPHS: MEMORY")
    for i in [1,2,4]:
        plt.figure(figsize=(10, 4.8))
        linegraph.x_file('server_memory_usage', 'Maximum Server Memory Usage (Per Connection)', aggregate=lambda x: x.max(), cc=i, chunk_ids=[1,3,5,7], memory_mode=True)
        plt.close()
    for i in [1,3,5,7]:
        plt.figure(figsize=(10, 4.8))
        linegraph.x_client('server_memory_usage', 'Maximum Server Memory Usage (Per Connection)', aggregate=lambda x: x.max(), ci=i, client_counts=[1,2,4], memory_mode=True)
        plt.close()

    print("BOXPLOTS: TIME")
    for g in BOXPLOTS:
        for otlyrs in [True, False]:
            for i in [1,8,16]:
                plt.figure(figsize=(10, 4.8))
                boxplot.x_file(g, BOXPLOTS[g], outliers=otlyrs, cc=i, chunk_ids=[1,3,5,7,9])
                plt.close()
            for i in [50, 100, 150, 200]:
                plt.figure(figsize=(10, 4.8))
                boxplot.x_file(g, BOXPLOTS[g], outliers=otlyrs, cc=i, chunk_ids=[1,3])
                plt.close()
            for i in [1,3]:
                plt.figure(figsize=(10, 4.8))
                boxplot.x_client(g, BOXPLOTS[g], outliers=otlyrs, ci=i, client_counts=[1,8,16,50,100,150,200])
                plt.close()
            for i in [5,7,9]:
                plt.figure(figsize=(10, 4.8))
                boxplot.x_client(g, BOXPLOTS[g], outliers=otlyrs, ci=i, client_counts=[1,8,16])
                plt.close()

    print("BOXPLOTS: MEMORY")
    for otlyrs in [True, False]:
        for i in [1,2,4]:
            plt.figure(figsize=(10, 4.8))
            boxplot.x_file('server_memory_usage', 'Server Memory Usage (Per Connection)', outliers=otlyrs, cc=i, chunk_ids=[1,3,5,7], memory_mode=True)
            plt.close()
        for i in [1,3,5,7]:
            plt.figure(figsize=(10, 4.8))
            boxplot.x_client('server_memory_usage', 'Server Memory Usage (Per Connection)', outliers=otlyrs, ci=i, client_counts=[1,2,4], memory_mode=True)
            plt.close()

if __name__ == '__main__':
    generate_all()