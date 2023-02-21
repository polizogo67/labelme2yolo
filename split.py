import os, glob
import json
import random

def scan_dir(dir, exts=['.jpg']):
    res = []
    for ext in exts:
        res.extend( glob.glob(os.path.join(dir, f'*{ext}')) )
    return res

def load_json(filepath:str):
    with open(filepath, 'rb') as fp:
        data = json.load(fp)
    return data

def save_json(filepath:str, data):
    with open(filepath, 'w') as fp:
        json.dump(data, fp, indent=4)

def initialize_splitfile(filepath:str):
    myDict = {'train': [], 'eval': []}
    save_json(filepath, myDict)
    
def check_splitfile(filepath:str):
    # Returns the number of images found
    if not os.path.exists(filepath):
        initialize_splitfile(filepath)
        return 0
    data = load_json(filepath)
    return len(data['train']) + len(data['eval'])

def split(filelist, ratio=[80,20]):
    # Give train, eval, (test)
    filelist = set(filelist)
    num = len(filelist)
    bins = []
    total = 0
    
    assert sum(ratio) == 100, 'Define valid ratios that sums to 100'
    ratio = [ val/100 for val in ratio ]
    
    for rate in ratio:
        bin_size = round(num*rate)
        samples = random.sample( list(filelist), bin_size)
        filelist = filelist - set(samples)
        bins.append(samples)
        total += bin_size

    assert total == num
    return bins

def create_dict(sets):
    match len(sets):
        case 2:
            return { 'train': sets[0], 'eval': sets[1] }
        case 3:
            return { 'train': sets[0], 'eval': sets[1], 'test': sets[2] }

def main():
    
    SPLIT_FILES = 'splitfiles'
    datasets = glob.glob('datasets/*')

    for dataset in datasets:

        name = os.path.basename(dataset)
        images = scan_dir(dataset, ['.png', '.jpg', '.jpeg'])
        images = [ os.path.basename(item) for item in images ]

        splitfile = '{:s}/{:s}.json'.format(SPLIT_FILES, name)

        num = check_splitfile( splitfile )
        if num == 0:
            print('Splitting {} ...'.format(name))
            # split the current dataset and dump into the json splitfile
            sets = split(images)
            res = create_dict(sets)
            save_json(splitfile, res)
            continue

        assert len(images) == num, 'Found Different number of images and splitted images'

if __name__ == '__main__':

    try:
        main()
    except KeyboardInterrupt:
        print()