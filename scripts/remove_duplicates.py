##src=https://www.kaggle.com/datasets/masoudnickparvar/brain-tumor-mri-dataset/discussion/482896

import os
import hashlib

LABELS = ["glioma", "meningioma", "notumor", "pituitary"]
PROJECT_DIR = r"./archive"

def compute_hash(file):
    hasher = hashlib.md5()
    with open(file, 'rb') as f:
        buf = f.read()
        hasher.update(buf)
    return hasher.hexdigest()


def list_files(hash_dict):
    for data_type in ['Training', 'Testing']:
        for label in LABELS:
            # Corrigido: caminho direto para as pastas reais do Kaggle dataset
            folder_path = os.path.join(PROJECT_DIR, data_type, label)
            if not os.path.exists(folder_path):
                print(f"Aviso: pasta não encontrada -> {folder_path}")
                continue
            for root, dirs, files in os.walk(folder_path):
                for file in files:
                    if file.lower().endswith(".jpg"):
                        file_path = os.path.join(root, file)
                        file_hash = compute_hash(file_path)
                        hash_dict.setdefault(file_hash, []).append(file_path)


def remove_duplicates(hash_dict):
    duplicate_count = 0
    for hash_value, file_paths in hash_dict.items():
        if len(file_paths) > 1:
            # mantém a primeira, remove as restantes
            for file_path in file_paths[1:]:
                print(f"Removing duplicate (hash: {hash_value}) → {file_path}")
                os.remove(file_path)
                duplicate_count += 1
    print(f"\nTotal duplicates removed: {duplicate_count}")


if __name__ == '__main__':
    hash_dict = {}
    list_files(hash_dict)
    remove_duplicates(hash_dict)
