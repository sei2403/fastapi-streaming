# only keep chinese characters in a multiline file and output a txt without lines

import re
from tqdm import tqdm

def keep_chinese_only(input_file, output_file):
    with open(input_file, 'r') as f:
        print("reading lines")
        lines = f.readlines()
        print("read lines")
    with open(output_file, 'w') as f:
        for line in tqdm(lines):
            line = re.sub(r'[^\u4e00-\u9fa5]', '', line)
            if line:
                f.write(line)

keep_chinese_only('zhwiki-latest-pages-articles1.xml-p1p187712', 'output.txt')