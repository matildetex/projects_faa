# ODIR-5K Dataset
## Ocular Disease Intelligent Recognition

### 📊 Estatísticas
- **Total de pacientes**: 6392
- **Treino**: 4474 (70.0%)
- **Validação**: 959 (15.0%)
- **Teste**: 959 (15.0%)

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
