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

#### Verificação Automática de Compatibilidade

O pacote mais recente para Streamlit Cloud inclui verificação automática avançada de compatibilidade que é executada durante a geração do pacote. Esta verificação:

1. **Detecta e corrige conflitos de nomenclatura**: Identifica e resolve problemas com nomes de páginas
2. **Normaliza emojis e caracteres especiais**: Evita problemas com caracteres que podem causar erros no navegador
3. **Remove arquivos temporários e de backup**: Elimina arquivos duplicados ou desnecessários
4. **Verifica metadados das páginas**: Analisa configurações em .streamlit/pages.toml em busca de conflitos
5. **Organiza a estrutura de diretórios**: Garante que a estrutura seja compatível com o Streamlit Cloud

#### Verificação Manual de Problemas

Se mesmo assim você encontrar erros durante o deploy, verifique:

1. **Configuração de porta**: O Streamlit Cloud usa a porta 8501 por padrão. Não defina a porta no arquivo `config.toml`.
2. **Pacotes incompatíveis**: Certifique-se que o `requirements.txt` não contém pacotes incompatíveis como Kivy, Buildozer ou qualquer dependência específica para Android.
3. **Imports incorretos**: Verifique se não há imports de módulos que não estão disponíveis no ambiente Streamlit Cloud.
4. **Segredos (Secrets)**: Configure corretamente os segredos nas configurações do aplicativo no Streamlit Cloud.
5. **Erros de StreamlitAPIException**: Se aparecer este erro específico, é quase sempre devido a:
   - **Páginas com nomes idênticos**: Mesmo com arquivos diferentes, o Streamlit pode interpretar como o mesmo nome
   - **Emojis conflitantes**: Alguns emojis parecem diferentes mas são tratados como iguais pelo Streamlit
   - **Arquivos ocultos ou temporários**: Arquivos .bak, .old, ou com ~ no diretório pages/

#### Ferramentas de Diagnóstico e Correção

Para executar manualmente a verificação e correção de conflitos:

```bash
# Verificar apenas (análise sem alterações)
python check_pages_compatibility.py

# Verificar e corrigir automaticamente
python check_pages_compatibility.py --fix

# Verificar, corrigir e mover arquivos conflitantes para diretório seguro
python check_pages_compatibility.py --fix --move-conflicts
```

#### Dicas para Problemas Específicos

- **Páginas desaparecendo do menu**: Verifique os nomes dos arquivos em busca de conflitos de prefixo numérico
- **Erros de navegação**: Certifique-se que não há duas páginas com nomes muito semelhantes
- **Página carrega em branco**: Verifique os logs para identificar erros de importação ou pacotes faltando

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
- Problema com caracteres ou emojis nas páginas
- Páginas carregando em ordem incorreta

Estes problemas geralmente são causados por conflitos de nomenclatura entre as páginas. O sistema agora inclui uma ferramenta aprimorada para detectar e corrigir esses problemas automaticamente:

#### Ferramenta Avançada de Verificação de Conflitos

O pacote mais recente inclui verificações aprimoradas que:

1. **Detecta emojis similares ou conflitantes**: Identifica emojis que podem parecer diferentes mas são tratados como iguais pelo Streamlit
2. **Normaliza nomes de arquivos**: Elimina problemas com caracteres especiais e formatação
3. **Move arquivos conflitantes**: Em vez de apenas renomear, move os arquivos para um diretório de backup para evitar conflitos persistentes
4. **Analisa similaridade semântica**: Detecta nomes quase idênticos mesmo com diferenças sutis
5. **Verifica duplicações em metadados**: Busca conflitos nas configurações do arquivo .streamlit/pages.toml

#### Como usar a ferramenta manualmente:

```bash
# Verificar apenas (não altera arquivos)
python check_pages_compatibility.py

# Verificar e aplicar correções automaticamente
python check_pages_compatibility.py --fix

# Verificar, corrigir e mover arquivos conflitantes para pages_backup
python check_pages_compatibility.py --fix --move-conflicts

# Após corrigir, gerar novo pacote de deploy
python prepare_streamlit_cloud.py
```

#### Ações corretivas adicionais:

- Se os problemas persistirem, use a opção `--move-conflicts` para mover arquivos conflitantes para um diretório de backup
- Remova manualmente arquivos .bak, .old ou qualquer cópia de backup no diretório pages/
- Verifique o arquivo `.streamlit/pages.toml` em busca de configurações duplicadas
- Renomeie páginas com prefixos numéricos garantindo que sejam únicos

> **Importante**: O novo pacote de deploy para Streamlit Cloud já executa todas essas verificações automaticamente, então ao baixar a versão mais recente do pacote de deploy, os problemas de conflitos já estarão resolvidos.