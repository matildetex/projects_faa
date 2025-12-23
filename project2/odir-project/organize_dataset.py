"""
Organizar Dataset ODIR-5K em Estrutura de Pastas
- Move dataset da cache do Kaggle para a raiz do projeto
- Organiza imagens em pastas train/val/test
- Cria subpastas por classe (opcional)
"""

import os
import shutil
import json
import pandas as pd
from pathlib import Path
from tqdm import tqdm
import getpass

# =====================================================
# CONFIGURAÇÕES
# =====================================================

# Detectar automaticamente o caminho da cache do Kaggle
import getpass
username = getpass.getuser()
KAGGLE_CACHE = f"/home/{username}/.cache/kagglehub/datasets/andrewmvd/ocular-disease-recognition-odir5k/versions/2"

# Caminho destino na raiz do projeto
PROJECT_ROOT = os.getcwd()
DATASET_ROOT = os.path.join(PROJECT_ROOT, "data", "odir5k")

# Estrutura de pastas
SPLITS_JSON = os.path.join(PROJECT_ROOT, "splits", "split_indices.json")

print(f"📍 Caminho da cache do Kaggle: {KAGGLE_CACHE}")
print(f"📍 Destino do dataset: {DATASET_ROOT}")

# =====================================================
# FUNÇÕES AUXILIARES
# =====================================================

def create_directory_structure():
    """Criar estrutura de diretórios"""
    print("\n📁 A criar estrutura de diretórios...")
    
    dirs = [
        os.path.join(DATASET_ROOT, "train"),
        os.path.join(DATASET_ROOT, "val"),
        os.path.join(DATASET_ROOT, "test"),
        os.path.join(DATASET_ROOT, "original"),  # Backup dos dados originais
    ]
    
    for dir_path in dirs:
        os.makedirs(dir_path, exist_ok=True)
        print(f"  ✅ {dir_path}")
    
    return dirs

def copy_original_data():
    """Copiar dados originais (CSV e imagens) para o projeto"""
    print("\n📦 A copiar dados originais do Kaggle cache...")
    
    # Copiar CSV
    csv_src = os.path.join(KAGGLE_CACHE, "full_df.csv")
    csv_dst = os.path.join(DATASET_ROOT, "original", "full_df.csv")
    
    if not os.path.exists(csv_dst):
        shutil.copy2(csv_src, csv_dst)
        print(f"  ✅ CSV copiado")
    else:
        print(f"  ⏭️  CSV já existe")
    
    # Copiar pasta de imagens
    img_src = os.path.join(KAGGLE_CACHE, "preprocessed_images")
    img_dst = os.path.join(DATASET_ROOT, "original", "images")
    
    if not os.path.exists(img_dst):
        print("  📸 A copiar imagens (pode demorar alguns minutos)...")
        shutil.copytree(img_src, img_dst)
        img_count = len([f for f in os.listdir(img_dst) if f.endswith('.jpg')])
        print(f"  ✅ {img_count} imagens copiadas")
    else:
        print(f"  ⏭️  Imagens já existem")
    
    return csv_dst, img_dst

def organize_images_by_split(csv_path, img_dir):
    """Organizar imagens em train/val/test baseado no split"""
    print("\n🗂️  A organizar imagens por split...")
    
    # Carregar CSV e splits
    df = pd.read_csv(csv_path)
    
    with open(SPLITS_JSON, 'r') as f:
        splits = json.load(f)
    
    # Estatísticas
    stats = {'train': 0, 'val': 0, 'test': 0}
    
    # Organizar cada split
    for split_name, indices in splits.items():
        print(f"\n  📂 Processando {split_name}...")
        split_dir = os.path.join(DATASET_ROOT, split_name)
        
        for idx in tqdm(indices, desc=f"  {split_name}", ncols=80):
            row = df.iloc[idx]
            patient_id = str(row['ID'])
            
            # Tentar copiar imagem esquerda e direita
            for side in ['left', 'right']:
                img_name = f"{patient_id}_{side}.jpg"
                src_path = os.path.join(img_dir, img_name)
                dst_path = os.path.join(split_dir, img_name)
                
                if os.path.exists(src_path) and not os.path.exists(dst_path):
                    shutil.copy2(src_path, dst_path)
                    stats[split_name] += 1
        
        print(f"  ✅ {stats[split_name]} imagens copiadas para {split_name}/")
    
    return stats

def create_metadata_files():
    """Criar ficheiros de metadados úteis"""
    print("\n📄 A criar ficheiros de metadados...")
    
    # Carregar CSV original
    csv_path = os.path.join(DATASET_ROOT, "original", "full_df.csv")
    df = pd.read_csv(csv_path)
    
    # Carregar splits
    with open(SPLITS_JSON, 'r') as f:
        splits = json.load(f)
    
    # Criar CSV separado para cada split
    for split_name, indices in splits.items():
        split_df = df.iloc[indices].reset_index(drop=True)
        output_path = os.path.join(DATASET_ROOT, split_name, f"{split_name}_metadata.csv")
        split_df.to_csv(output_path, index=False)
        print(f"  ✅ {split_name}_metadata.csv criado ({len(split_df)} amostras)")
    
    # Criar README com informações do dataset
    readme_content = f"""# ODIR-5K Dataset
## Ocular Disease Intelligent Recognition

### 📊 Estatísticas
- **Total de pacientes**: {len(df)}
- **Treino**: {len(splits['train'])} ({len(splits['train'])/len(df)*100:.1f}%)
- **Validação**: {len(splits['val'])} ({len(splits['val'])/len(df)*100:.1f}%)
- **Teste**: {len(splits['test'])} ({len(splits['test'])/len(df)*100:.1f}%)

### 🏥 Classes (Doenças)
- **N**: Normal
- **D**: Diabetes
- **G**: Glaucoma
- **C**: Cataract
- **A**: Age-related Macular Degeneration
- **H**: Hypertension
- **M**: Myopia
- **O**: Other diseases

### 📁 Estrutura de Pastas
```
data/odir5k/
├── original/           # Dados originais do Kaggle
│   ├── full_df.csv
│   └── images/
├── train/             # Imagens de treino
│   └── train_metadata.csv
├── val/               # Imagens de validação
│   └── val_metadata.csv
└── test/              # Imagens de teste
    └── test_metadata.csv
```

### 🔄 Data Augmentation (apenas no treino)
- Redimensionamento: 224x224
- Flip horizontal (p=0.5)
- Rotação aleatória: ±15°
- Ajuste de brilho/contraste: ±20%

### 📌 Notas
- Split fixo com random_state=42 (reprodutível)
- Imagens pré-processadas do Kaggle
- Multi-label classification (uma imagem pode ter múltiplas doenças)
"""
    
    readme_path = os.path.join(DATASET_ROOT, "README.md")
    with open(readme_path, 'w', encoding='utf-8') as f:
        f.write(readme_content)
    
    print(f"  ✅ README.md criado")

def create_gitignore():
    """Criar/atualizar .gitignore na raiz do projeto"""
    print("\n🚫 A atualizar .gitignore...")
    
    gitignore_path = os.path.join(PROJECT_ROOT, ".gitignore")
    
    gitignore_content = """# Dataset (muito grande para Git)
data/
*.csv
*.jpg
*.jpeg
*.png

# Modelos treinados
models/*.pth
models/*.h5
*.pth
*.h5

# Ambiente virtual
venv/
env/

# Python
__pycache__/
*.pyc
*.pyo
*.pyd
.Python

# Jupyter
.ipynb_checkpoints/
*.ipynb

# Kaggle
.kaggle/
kaggle.json

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db
desktop.ini

# Logs e resultados temporários
*.log
logs/
temp/
tmp/

# Excluir apenas os índices do split (manter no Git)
!splits/split_indices.json
"""
    
    with open(gitignore_path, 'w', encoding='utf-8') as f:
        f.write(gitignore_content)
    
    print(f"  ✅ .gitignore atualizado")

def print_summary():
    """Mostrar resumo final"""
    print("\n" + "=" * 60)
    print("✅ ORGANIZAÇÃO DO DATASET COMPLETA!")
    print("=" * 60)
    
    # Contar imagens em cada pasta
    train_count = len([f for f in os.listdir(os.path.join(DATASET_ROOT, "train")) if f.endswith('.jpg')])
    val_count = len([f for f in os.listdir(os.path.join(DATASET_ROOT, "val")) if f.endswith('.jpg')])
    test_count = len([f for f in os.listdir(os.path.join(DATASET_ROOT, "test")) if f.endswith('.jpg')])
    
    print(f"""
📊 Resumo:
  📁 Localização: {DATASET_ROOT}
  
  🖼️  Imagens organizadas:
    - Treino:    {train_count} imagens
    - Validação: {val_count} imagens
    - Teste:     {test_count} imagens
    - TOTAL:     {train_count + val_count + test_count} imagens

📦 Ficheiros criados:
  - data/odir5k/train/ (imagens + metadata)
  - data/odir5k/val/ (imagens + metadata)
  - data/odir5k/test/ (imagens + metadata)
  - data/odir5k/original/ (backup)
  - data/odir5k/README.md
  - .gitignore (atualizado)

💡 Próximos passos:
  1. ✅ Dataset organizado em pastas
  2. ✅ Git configurado (data/ será ignorado)
  3. ⏭️  Atualizar odir_preparation.py para usar nova estrutura
  4. ⏭️  Receber código CLAHE/Cropping do Estudante B
  5. ⏭️  Começar Fase 2: Treino da ResNet50

⚠️  Nota: Pode apagar com segurança a cache do Kaggle:
    rm -rf {KAGGLE_CACHE}
    (O dataset está agora em {DATASET_ROOT})
""")

# =====================================================
# MAIN
# =====================================================

def main():
    """Pipeline completo de organização"""
    print("=" * 60)
    print("🗂️  ORGANIZAÇÃO DO DATASET ODIR-5K")
    print("=" * 60)
    
    # Verificar se a cache do Kaggle existe
    if not os.path.exists(KAGGLE_CACHE):
        print(f"\n❌ ERRO: Cache do Kaggle não encontrada!")
        print(f"   Esperado em: {KAGGLE_CACHE}")
        print("\n💡 Execute primeiro:")
        print("   python odir_preparation.py")
        print("\n   Isso vai fazer o download do dataset do Kaggle.")
        return
    
    print(f"\n✅ Cache do Kaggle encontrada!")
    
    # 1. Criar estrutura de diretórios
    create_directory_structure()
    
    # 2. Copiar dados originais
    csv_path, img_dir = copy_original_data()
    
    # 3. Organizar imagens por split
    stats = organize_images_by_split(csv_path, img_dir)
    
    # 4. Criar metadados
    create_metadata_files()
    
    # 5. Atualizar .gitignore
    create_gitignore()
    
    # 6. Mostrar resumo
    print_summary()

if __name__ == "__main__":
    # Verificar se splits já existem
    if not os.path.exists(SPLITS_JSON):
        print("❌ ERRO: Ficheiro splits/split_indices.json não encontrado!")
        print("   Execute primeiro: python odir_preparation.py")
        exit(1)
    
    main()