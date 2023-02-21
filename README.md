# Labelme to YOLO Conversion Tool

## Produce Yolo Labels
Convert labelme labels into yolo format based on the task specified.
```bash
python convert.py --source <path/to/dataset> --task <detect/segment/classify>
```
Or provide a .txt file with all the datasets to do this for many datasets at once
```bash
python convert.py --datalist <path/to/dataset.txt> --task <detect/segment/classify>
```

## Split Dataset
This script splits all the datasets located inside datasets folder and for each one, a corresponding json file is saved that contains information on how the dataset is splitted.
```bash
python split_datasets.py
```

## Migrate the Dataset using the splitfiles

```bash
python migrate.py --datasets datalist.txt
```#