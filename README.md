# Sistema de Gestão Suinocultura - Versão 2.2

Este é um aplicativo Streamlit para gerenciamento de operações de suinocultura. Para executar:

1. Instale as dependências: `pip install -r requirements.txt`
2. Execute o aplicativo: `streamlit run app.py`

## Novidades da Versão 2.2:
- **Aplicativo Android Offline**: Utilize o sistema mesmo sem conexão com internet
- **Banco de dados SQLite**: Armazenamento local de dados no aplicativo offline
- **Sincronização com Firebase Firestore**: Mantenha dados sincronizados entre dispositivos
- **Suporte à integração com GitHub**: Sincronize seu código diretamente com repositórios
- **Visualização destacada de notas importantes**: Melhor organização das informações críticas
- **Histórico de atualizações completo**: Acompanhe todas as mudanças do sistema

## Versão Mobile (APK Android)

Este pacote contém todos os arquivos necessários para criar uma versão APK para Android:

1. **WebView**: A pasta `android_app_base` contém o projeto Android base para WebView
   - Carrega a versão hospedada da aplicação Streamlit
   - Requer conexão com internet

2. **Aplicativo Offline Completo**: A pasta `kivy_app_offline` contém um aplicativo nativo
   - Funciona sem conexão com internet
   - Armazena dados localmente com SQLite
   - Sincroniza com o Firestore quando online
   - Interface nativa com Kivy/Python
   
3. Consulte o arquivo `guia_criacao_apk.md` para instruções detalhadas sobre como criar um APK

## Sincronização de Dados

O sistema agora suporta sincronização de dados entre o aplicativo offline e a versão web:

1. **Firebase Firestore** para armazenamento em nuvem
2. **API de Sincronização** integrada ao Streamlit Cloud
3. **Isolamento de dados por usuário** para maior segurança
4. **Exportação/Importação automática** de dados em formato JSON

Para configurar a sincronização:
1. Crie um projeto no Firebase Console
2. Ative o Firestore
3. Gere credenciais de serviço
4. Configure as credenciais no arquivo secrets.toml

Consulte a documentação completa na seção de download do aplicativo.