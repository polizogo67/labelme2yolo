import cv2
import tqdm
import argparse
import os, glob
import json, csv
import numpy as np

names = ['meltflow', 'spinner']
names = ['meltflow', 'spinner', 'slag']

def parse_list(filepath:str):
    with open(filepath, 'r') as fp:
        data = fp.read().split('\n')
    return data

def scan_dir(dir, exts=['.jpg']):
    res = []
    for ext in exts:
        res.extend( glob.glob(os.path.join(dir, f'*{ext}')) )
    return res

def load_json(filepath):
    with open(filepath, 'rb') as fp:
        data = json.load(fp)
    return data

def load_labelme_json(filepath):
    data = load_json(filepath)
    return data['shapes'], data['imageHeight'], data['imageWidth']

def points2yolo(points, task:str='detect'):

    match task:
        case 'detect':
            print('Not Implemented')
        case 'segment':
            res = points.ravel().tolist()
        case other:
            print(f'{task} Not Implemented')

    return res

def save_yolo_label(filepath, yolo_label):
    with open(filepath, 'w') as file:
        writer = csv.writer(file, delimiter=' ')
        writer.writerows(yolo_label)

def find_bbox(points):
    x_max = points.max(0)
    x_min = points.min(0)
    cx = ( x_max + x_min ) / 2
    cx = cx.round().astype(int)
    x, y = (cx - np.array([450, 450]) ).clip(0)
    X, Y = cx + np.array([450, 450])
    return x, y, X, Y

def find_cropbox(shapes):

    all_points = []

    for shape in shapes:
        # Classname and aliases
        shape['label'] = shape['label'].replace('melt on spinner', 'spinner').replace(' ','')
        shape['label'] = shape['label'].replace('spiner', 'spinner')
        if not shape['label'] in names: continue
        
        match shape['shape_type']:
            case 'polygon':
                all_points.append( np.array( shape['points'] ) )
    
    if len(all_points) == 0: return 0, 0, 0, 0, False

    all_points = np.concatenate(all_points)
    bbox = find_bbox(all_points)

    return *bbox, True

def main(opt):
    print(opt)

    CROP = opt.crop
    SOURCE = os.path.normpath(opt.input)

    if CROP:
        name = os.path.basename(SOURCE)
        tmp = os.path.join('cropped', name)
        os.makedirs(tmp, exist_ok=True)

    not_found = []
    images = scan_dir(SOURCE, ['.jpeg', '.jpg', '.png'])

    for image in tqdm.tqdm( images ):
        filename, ext = os.path.splitext(image)
        basename = os.path.basename(filename)
        label = filename + '.json'
        
        if not os.path.exists(label):
            # print(f'WARNING: Did not found label for {image}')
            continue

        shapes, H, W = load_labelme_json(label)
        yolo_label = []

        if CROP:
            x, y, X, Y, ret = find_cropbox(shapes)
            if not ret: continue
            img = cv2.imread(image)[y:Y, x:X]
            H, W, C = img.shape
            origin = np.array([x, y])

        for shape in shapes:
            
            # Classname and aliases
            classname = shape['label']
            classname = classname.replace('melt on spinner', 'spinner').replace(' ','')
            classname = classname.replace('spiner', 'spinner')

            if classname in names:
                clsID = names.index(classname)
            else:
                if not classname in not_found:
                    not_found.append(classname)
                continue
            
            match shape['shape_type']:

                case 'polygon':
                    points = np.array( shape['points'] )
                    if CROP: points = points - origin
                    norm_points = points / np.array([W, H])

                    yolo_shape = points2yolo(norm_points, task=opt.task)
                    yolo_shape.insert(0, clsID)

                    yolo_label.append(yolo_shape)
                    
                    # import pdb; pdb.set_trace()
                    # for point in points:
                        # cv2.circle(img, (int(point[0]), int(point[1])), 4, (0,0,255), -1)
                case other:
                    print('WARNING: {} not implemented yet'.format(shape['shape_type']))

        if CROP:
            name = os.path.join(tmp, basename)
            cv2.imwrite( f'{name}.png' , img )
            save_yolo_label( f'{name}.txt', yolo_label)
        else:
            save_yolo_label(filename+'.txt', yolo_label)

    if len(not_found): print('Not found classes {}'.format(not_found))
    
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Labelme 2 Yolo Format')
    parser.add_argument('--input', '-i', type=str, default='', help='location of video')
    parser.add_argument('--datalist', '-l', type=str, default='', help='list of datasets')
    parser.add_argument('--task', type=str, default='detect', help='select between detect / segment / classify')
    parser.add_argument('--crop', '-c', action='store_true', help='crop the images')
    opt = parser.parse_args()

    try:
        if opt.datalist:
            dnames = parse_list(opt.datalist)
            datasets = [ os.path.join('datasets', name) for name in dnames ]
            for dataset in datasets:
                opt.input = dataset
                main(opt)
        else:
            main(opt)
    except KeyboardInterrupt:
        print()