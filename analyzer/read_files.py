import os
import json

def get_folders(main_dir: dict, client_count: int, chunk_id: int, reset_levels: str = '../../../../../'):
    resfolders = []

    for t in main_dir:
        os.chdir(main_dir[t])
        folders = os.listdir()
        for folder in folders:
            if folder == '.DS_Store':
                continue
            os.chdir(folder)
            metadata = {}
            with open ('metadata.json', 'r') as f:
                metadata = json.load(f)
                if metadata.get('client_count') == client_count and metadata.get('chunk_id') == chunk_id:
                    resfolders.append(os.getcwd())
            os.chdir('..')
        os.chdir(reset_levels)
    return resfolders

def get_folders_by_client(main_dir: dict, client_count: int, reset_levels: str = '../../../../../'):
    resfolders = []

    for t in main_dir:
        os.chdir(main_dir[t])
        folders = os.listdir()
        for folder in folders:
            if folder == '.DS_Store':
                continue
            os.chdir(folder)
            metadata = {}
            with open ('metadata.json', 'r') as f:
                metadata = json.load(f)
                if metadata.get('client_count') == client_count:
                    resfolders.append(os.getcwd())
            os.chdir('..')
        os.chdir(reset_levels)
    return resfolders

def get_folders_by_chunk(main_dir: dict, chunk_id: int, reset_levels: str = '../../../../../'):
    resfolders = []

    for t in main_dir:
        os.chdir(main_dir[t])
        folders = os.listdir()
        for folder in folders:
            if folder == '.DS_Store':
                continue
            os.chdir(folder)
            metadata = {}
            with open ('metadata.json', 'r') as f:
                metadata = json.load(f)
                if metadata.get('chunk_id') == chunk_id:
                    resfolders.append(os.getcwd())
            os.chdir('..')
        os.chdir(reset_levels)
    return resfolders