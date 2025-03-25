# Instruções para Deploy no Streamlit Community Cloud

Este documento explica como fazer o deploy do Sistema Suinocultura no Streamlit Community Cloud.

## Pré-requisitos

1. Uma conta GitHub
2. Uma conta no [Streamlit Community Cloud](https://streamlit.io/cloud)

## Passos para o Deploy

### 1. Preparação do Repositório GitHub

1. Crie um novo repositório no GitHub (pode ser público ou privado)
2. Faça upload dos seguintes arquivos e diretórios:
   - `app.py`
   - `utils.py`
   - `requirements.txt`
   - Diretório `pages/`
   - Diretório `data/`
   - Diretório `.streamlit/`
   - `.gitignore`

### 2. Configuração do Streamlit Community Cloud

1. Acesse [Streamlit Community Cloud](https://streamlit.io/cloud)
2. Faça login com sua conta GitHub
3. Clique em "New app"
4. Selecione o repositório onde você fez upload dos arquivos
5. Configure a aplicação:
   - **Main file path**: `app.py`
   - **Branch**: `main` (ou sua branch principal)
   - Clique em "Advanced settings" e verifique se todas as dependências estão listadas

### 3. Segredos e Configurações Sensíveis

No Streamlit Community Cloud, você precisará configurar os segredos:

1. No painel da sua aplicação, clique em "Settings" > "Secrets"
2. Adicione todos os segredos necessários conforme o arquivo `.streamlit/secrets.toml.example`
3. Especialmente importante:
   ```
   [admin]
   username = "seu_nome_de_usuario"
   password = "sua_senha_segura"
   ```

### 4. Verificação de Permissões

Se sua aplicação usar GitHub API para sincronização:

1. Certifique-se de criar um token de acesso pessoal no GitHub
2. Adicione esse token aos segredos da aplicação no Streamlit
3. Verifique se o token tem as permissões necessárias para o repositório

### 5. Considerações Sobre Dados

1. O Streamlit Community Cloud reinicia periodicamente as aplicações, então dados salvos localmente serão perdidos
2. Os arquivos CSV na pasta `data/` são persistentes apenas durante a sessão
3. Para dados persistentes, considere:
   - Usar um banco de dados externo
   - Usar GitHub como armazenamento (commit automático de dados)
   - Implementar backup/restore para arquivos CSV

### 6. Verificação da Aplicação

Após o deploy, verifique:

1. Se a página de login aparece corretamente
2. Se você consegue fazer login com as credenciais definidas
3. Se todas as funcionalidades estão operando normalmente
4. Se as permissões de usuário estão funcionando corretamente

## Solução de Problemas

- **Erro "ModuleNotFoundError"**: Verifique se todas as dependências estão no arquivo `requirements.txt`
- **Erro "Could not find file data/..."**: Verifique se a pasta `data/` foi carregada corretamente e se contém os arquivos necessários
- **Problemas de CSS/Estilo**: Verifique se o arquivo `.streamlit/config.toml` está configurado corretamente

## Contato e Suporte

Para suporte adicional com o deploy, consulte a [documentação oficial do Streamlit](https://docs.streamlit.io/streamlit-community-cloud) ou entre em contato com o desenvolvedor do sistema.