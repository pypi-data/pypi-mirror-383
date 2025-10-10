import os.path
import random
import shutil
import uuid

from aabd.base.path_util import list_files


def label_sub2main(label_main, label_sub):
    cx1r, cy1r, w1r, h1r = label_main
    cx2r, cy2r, w2r, h2r = label_sub
    return list(
        map(lambda x: round(x, 6), [cx1r + (cx2r - 0.5) * w1r, cy1r + (cy2r - 0.5) * h1r, w2r * w1r, h2r * h1r]))


def label_line_sub2main(label_main: str, label_sub: str, label_idx=1):
    """
    被截出来的图标注的数据合并到原图
    :param label_main: 原图中被截取的label
    :param label_sub: 截取的图片中的标注数据
    :param label_idx: 目标idx
    :return: label
    """
    cx1r, cy1r, w1r, h1r = list(map(float, label_main.strip().split(' ')))[1:5]
    cx2r, cy2r, w2r, h2r = list(map(float, label_sub.strip().split(' ')))[1:5]
    return ' '.join([str(label_idx), *list(map(str, label_sub2main([cx1r, cy1r, w1r, h1r], [cx2r, cy2r, w2r, h2r])))])


def to_yolo_det_data_dir(input_dir, yolo_dir='train_data', label_dir=None, folder_ratio=None, label_idx_map=None,
                         keep_dir_tree=True, main_dir=None, delete_origin=False, file_suffix_type=None):
    """
    将数据移动到yolo训练目录
    :param input_dir: image,label数据所在目录
    :param label_dir: label所在目录
    :param yolo_dir: yolo目录位置
    :param folder_ratio: 移动到的文件夹比例
    :param label_idx_map: label 更换,如果为None保持原状
    :param keep_dir_tree: 是否保持原有的文件夹结构
    :param main_dir: 是否将当次数据统一放入一个文件夹
    :param delete_origin: 是否删除原始的数据
    :param file_suffix_type: None:没有后缀 uuid:随机 seq:序号
    """
    image_dir = input_dir
    label_dir = label_dir or input_dir
    folder_ratio = folder_ratio or [0.8, 0.2]
    folder_ratio_map = {}
    if isinstance(folder_ratio, list):
        for i, v in enumerate(folder_ratio[:3]):
            folder_ratio_map[['train', 'val', 'test'][i]] = v
    elif isinstance(folder_ratio, dict):
        folder_ratio_map = folder_ratio

    if isinstance(label_idx_map, list) and isinstance(label_idx_map[0], int):
        label_idx_map = dict(zip(range(len(label_idx_map)), label_idx_map))

    image_paths = [p[1] for p in list_files(image_dir, ['.jpg', '.png', '.jpeg', '.webp', '.bmp'], absolute=False)]

    total_r = 0
    names = []
    ratios = []
    name_counts = []
    name_paths = []
    for name, ratio in folder_ratio_map.items():
        total_r += ratio
        names.append(name)
        ratios.append(ratio)

    if len(names) == 1:
        name_counts.append(len(image_paths))
    else:
        for r in ratios:
            name_counts.append(int(r / total_r * len(image_paths)))
        name_counts[-1] = len(image_paths) - sum(name_counts[:-1])

    random.shuffle(image_paths)

    i_c = 0
    for i in range(len(name_counts)):
        name_paths.append(image_paths[i_c:i_c + name_counts[i]])
        i_c += name_counts[i]

    for i, (dest_dir_name, paths) in enumerate(zip(names, name_paths)):
        for j, path in enumerate(paths):
            image_file_dir = os.path.dirname(path)
            image_file_name1 = os.path.basename(path)
            image_file_name2, image_file_ext = os.path.splitext(image_file_name1)

            src_image_path = os.path.join(image_dir, path)
            src_label_path = os.path.join(label_dir, f"{os.path.splitext(path)[0]}.txt")

            if file_suffix_type == 'uuid':
                suffix = uuid.uuid4().hex
                dest_image_name = f'{image_file_name2}.{suffix}{image_file_ext}'
                dest_label_name = f'{image_file_name2}.{suffix}.txt'
            elif file_suffix_type == 'seq':
                dest_image_name = f'{image_file_name2}.{dest_dir_name}.{j}{image_file_ext}'
                dest_label_name = f'{image_file_name2}.{dest_dir_name}.{j}.txt'
            else:
                dest_image_name = image_file_name1
                dest_label_name = f'{image_file_name2}.txt'

            if keep_dir_tree:
                dest_image_name = os.path.join(image_file_dir, dest_image_name)
                dest_label_name = os.path.join(image_file_dir, dest_label_name)

            if main_dir:
                dest_image_name = os.path.join(main_dir, dest_image_name)
                dest_label_name = os.path.join(main_dir, dest_label_name)

            dest_image_path = os.path.join(yolo_dir, dest_dir_name, dest_image_name)
            dest_label_path = os.path.join(yolo_dir, dest_dir_name, dest_label_name)

            os.makedirs(os.path.dirname(dest_image_path), exist_ok=True)

            if delete_origin:
                shutil.move(src_image_path, dest_image_path)
            else:
                shutil.copy(src_image_path, dest_image_path)
            if os.path.exists(src_label_path):
                if label_idx_map:
                    with open(src_label_path, 'r', encoding='utf-8') as f:
                        with open(dest_label_path, 'w', encoding='utf-8') as f2:
                            for line in f:
                                clz, cx, cy, w, h = line.strip().split(' ')
                                dest_clz = label_idx_map.get(int(clz), None)
                                if dest_clz is not None:
                                    f2.write(f'{dest_clz} {cx} {cy} {w} {h}\n')
                if delete_origin:
                    os.remove(src_label_path)
                else:
                    if delete_origin:
                        shutil.move(src_label_path, dest_label_path)
                    else:
                        shutil.copy(src_label_path, dest_label_path)


if __name__ == '__main__':
    to_yolo_det_data_dir(r'E:\tmp\src1', r'E:\tmp\dest', keep_dir_tree=True, label_idx_map=[111, None, 333],file_suffix_type='seq')
