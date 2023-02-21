import os, glob
import shutil
import argparse
import json

# src_file = "/path/to/source/file.txt"
# dst_dir = "/path/to/destination/directory"

# shutil.copy(src_file, dst_dir)

def load_json(filepath:str):
    with open(filepath, 'rb') as fp:
        data = json.load(fp)
    return data

def make_dataset(name:str):
    types = ['images', 'labels']
    modes = ['train', 'eval']
    for ftype in types:
        for mode in modes:
            os.makedirs('{}/{}/{}'.format(name, ftype, mode), exist_ok=True)

def parse_dataset_config(filepath:str):
    if not os.path.exists(filepath): return 0
    with open(filepath, 'r') as fp:
        lines = fp.read().split('\n')
    return lines

def main(opt):

    CROP = opt.crop
    CFG = opt.datasets
    DATASET = 'results/{}'.format( opt.name )
    SPLIT_FILES = 'splitfiles'

    match CROP:
        case True:
            DATASETS = 'cropped'
        case False:
            DATASETS = 'datasets'

    datasets = parse_dataset_config(CFG)
    if len(datasets): make_dataset(DATASET)

    for dataset in datasets:

        splitfile = '{}.json'.format( os.path.join(SPLIT_FILES, dataset) )
        split = load_json(splitfile)

        prefix = os.path.join(DATASETS, dataset)

        for mode, items in split.items():

            img_dest_path = os.path.join(DATASET, 'images', mode)
            label_dest_path = os.path.join(DATASET, 'labels', mode)

            for image in items:
                image = image.replace('.jpg','.png').replace('.jpeg', '.png')
                name, ext = os.path.splitext(image)
                img_src = os.path.join(prefix, image)
                img_dest = os.path.join(img_dest_path, image)
                label_src = os.path.join(prefix, f'{name}.txt')
                label_dest = os.path.join(label_dest_path, f'{name}.txt')

                # Normally Commented
                if not os.path.exists(label_src):
                    print('WARNING: Skipping image {}'.format(image))
                    continue

                shutil.copy(img_src, img_dest)
                shutil.copy(label_src, label_dest)



if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Migrate final dataset from splitfiles')
    parser.add_argument('--datasets', '-d', type=str, default='', help='location of dataset collection')
    parser.add_argument('--name', type=str, default='yolodataset', help='select the name of the final dataset')
    parser.add_argument('--crop', '-c', action='store_true', help='crop the images')
    # parser.add_argument('--task', type=str, default='detect', help='select between detect / segment / classify')
    opt = parser.parse_args()
    
    try:
        main(opt)
    except KeyboardInterrupt:
        print()