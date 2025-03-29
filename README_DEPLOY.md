# Guia de Deployment - Sistema Suinocultura

Este guia contém instruções detalhadas para fazer o deploy do Sistema Suinocultura em diferentes plataformas.

## Deploy no Streamlit Community Cloud

### Requisitos
- Conta no GitHub (gratuita)
- Conta no Streamlit Community Cloud (gratuita)

### Instruções para o Deploy

#### Método 1: Deploy Automatizado (Recomendado)

1. Acesse a página "📥 Download Aplicativo" no sistema
2. Clique em "ENVIAR DIRETAMENTE PARA O GITHUB"
3. Preencha as credenciais do GitHub (nome de usuário e token)
4. Selecione "Enviar apenas arquivos modificados" se quiser atualizar somente arquivos alterados
5. Clique em "Enviar para o GitHub"
6. Use o link fornecido para implantar no Streamlit Cloud

#### Método 2: Deploy Manual

1. Baixe o pacote `suinocultura_cloud_deploy_YYYYMMDD.zip` da página "📥 Download Aplicativo"
2. Extraia o conteúdo do arquivo ZIP
3. Crie um novo repositório no GitHub
4. Faça upload de todos os arquivos extraídos para o repositório
5. Acesse o [Streamlit Community Cloud](https://streamlit.io)
6. Faça login com sua conta GitHub
7. Vá para "Your apps" e clique em "New app"
8. Selecione o repositório criado, mantenha "app.py" no Main file path
9. Configure os secrets nas configurações do aplicativo conforme o arquivo `.streamlit/secrets.toml.example`

### Solução de Problemas no Streamlit Cloud

Se você encontrar erros durante o deploy no Streamlit Cloud, verifique:

1. **Configuração de porta**: O Streamlit Cloud usa a porta 8501 por padrão. Não defina a porta no arquivo `config.toml`.
2. **Pacotes incompatíveis**: Certifique-se que o `requirements.txt` não contém pacotes incompatíveis como Kivy, Buildozer ou qualquer dependência específica para Android.
3. **Imports incorretos**: Verifique se não há imports de módulos que não estão disponíveis no ambiente Streamlit Cloud.
4. **Segredos (Secrets)**: Configure corretamente os segredos nas configurações do aplicativo no Streamlit Cloud.
5. **Conflitos de páginas**: O sistema agora inclui detecção automática e correção de problemas de nomenclatura de páginas:
   - **Prefixos duplicados**: Páginas com o mesmo prefixo numérico (ex: "01_")
   - **Nomes similares**: Páginas com nomes quase idênticos ignorando maiúsculas/minúsculas
   - **Arquivos de backup**: Arquivos temporários ou de backup (ex: nome_old.py)

   Para executar manualmente a verificação de conflitos, use o comando:
   ```
   python check_pages_compatibility.py --fix
   ```

### Melhores Práticas para o Streamlit Cloud

1. **Arquivos estáticos**: Coloque arquivos estáticos (imagens, CSS, etc.) nas pastas corretas (`static/`, etc.)
2. **Segredos**: Nunca inclua credenciais diretamente no código, use sempre o mecanismo de secrets do Streamlit
3. **Tamanho do repositório**: Mantenha o tamanho do repositório o menor possível, removendo arquivos não necessários
4. **Versões de pacotes**: Especifique versões precisas das dependências no `requirements.txt`

## Deploy no Firebase Hosting (Estático)

Para deploy de elementos estáticos no Firebase Hosting:

1. Acesse a página "📥 Download Aplicativo" no sistema
2. Clique em "CONSTRUIR APLICATIVO FIREBASE"
3. Preencha os detalhes do projeto Firebase
4. Aguarde a conclusão do processo de build
5. Siga as instruções exibidas na tela para fazer o deploy

## Deploy do APK Android

Para criar um aplicativo Android:

1. Acesse a página "📥 Download Aplicativo" no sistema
2. Baixe o pacote `suinocultura_pydroid3_YYYYMMDD.zip`
3. Siga as instruções no arquivo README dentro do pacote

## Perguntas Frequentes

### O deploy no Streamlit Cloud está falhando com erro de saúde (health check)

Verifique se você removeu a configuração de porta específica do arquivo `.streamlit/config.toml`. O Streamlit Cloud usa a porta 8501 e pode falhar se você tentar definir outra porta.

### Não consigo fazer login no aplicativo após o deploy

Verifique se você configurou corretamente os segredos nas configurações do aplicativo no Streamlit Cloud. Consulte o arquivo `.streamlit/secrets.toml.example` para ver os segredos necessários.

### Alguns recursos não funcionam após o deploy

Verifique os logs do aplicativo no Streamlit Cloud para identificar o problema. Geralmente, isso ocorre devido a dependências ausentes ou incompatíveis.

### Como atualizar meu aplicativo no Streamlit Cloud?

Simplesmente faça push das alterações para o repositório GitHub. O Streamlit Cloud detectará as mudanças e atualizará o aplicativo automaticamente.

### Estou enfrentando erros de navegação ou páginas que não carregam corretamente

Se você está enfrentando problemas como:
- Páginas que não aparecem no menu lateral
- Erro "StreamlitAPIException: A page has the same name as a page from another module"
- Erros de navegação no aplicativo após o deploy

Estes problemas geralmente são causados por conflitos de nomenclatura entre as páginas. O sistema agora inclui uma ferramenta automática para detectar e corrigir esses problemas:

1. Execute o comando `python check_pages_compatibility.py --fix`
2. Gere um novo pacote de deploy com `python prepare_streamlit_cloud.py`
3. Faça o deploy do novo pacote

A ferramenta detecta e corrige automaticamente:
- Páginas com o mesmo prefixo numérico
- Páginas com nomes muito semelhantes (ignorando maiúsculas/minúsculas)
- Arquivos de backup ou temporários no diretório de páginas