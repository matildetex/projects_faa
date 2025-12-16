# Configuração do Dataset (Kaggle API)

Para baixar o dataset via código, é necessário configurar as credenciais do Kaggle.

## 1. Gerar o Token
1. Entre no seu perfil do [Kaggle](https://www.kaggle.com/).
2. Vá em **Settings** > Seção **API**.
3. Clique em **Create New Token**.
   - Faz um ficheiro json (`kaggle.json`) e mete neste formato:

```json
{
  "username": "seu_usuario_do_kaggle",
  "key": "sua_chave_secreta_aqui"
}
```

4. Corre

```
cd project2/scripts
python3 test.py
```