# Instruções de Deploy no Firebase

Este documento descreve como configurar e realizar o deploy do Sistema Suinocultura no Firebase Hosting.

## Pré-requisitos

1. Uma conta do Google para acessar o Firebase
2. Node.js instalado em sua máquina
3. Acesso à linha de comando

## Passo 1: Configurar o Projeto no Firebase

1. Acesse [console.firebase.google.com](https://console.firebase.google.com/)
2. Clique em "Adicionar projeto"
3. Dê o nome "suinocultura-app" ao seu projeto (ou outro nome de sua escolha)
4. Siga as instruções para criar o projeto
5. Quando solicitado, ative o Google Analytics (opcional)

## Passo 2: Configurar o Firebase Hosting

1. No console do Firebase, navegue até o projeto criado
2. No menu lateral, clique em "Hosting"
3. Clique em "Começar"
4. Siga as instruções para configurar o Firebase Hosting

## Passo 3: Instalar e Configurar as Ferramentas do Firebase

**IMPORTANTE**: O processo de autenticação no Firebase requer um navegador para interação. No ambiente Replit, isso não é possível diretamente. Recomendamos realizar a autenticação no Firebase em seu computador local e depois usar o token gerado no Replit.

### Opção 1: Autenticação em ambiente local

1. Em seu computador local, instale as ferramentas do Firebase:

```bash
# Instalar globalmente:
npm install -g firebase-tools

# Fazer login no Firebase (abrirá um navegador para autenticação):
firebase login
```

2. Após a autenticação bem-sucedida, você pode gerar um token para usar no Replit:

```bash
firebase login:ci
# Este comando gerará um token que você pode copiar e usar no Replit
```

### Opção 2: Download e desenvolvimento local

Alternativamente, você pode baixar o pacote completo (ZIP) e realizar todo o processo de deploy em seu ambiente local:

1. Descompacte o arquivo ZIP em seu computador
2. Instale as ferramentas do Firebase:

```bash
npm install -g firebase-tools
firebase login
```

3. Continue com o processo de deploy conforme as instruções abaixo

**Nota**: O comando `firebase init` não é necessário pois os arquivos de configuração já estão incluídos no pacote.

## Passo 4: Obter Configurações do Firebase

1. No console do Firebase, clique na engrenagem (⚙️) ao lado de "Visão geral do projeto"
2. Selecione "Configurações do projeto"
3. Role para baixo até "Seus aplicativos" e clique no ícone da web (</>) para adicionar um app da web
4. Registre o app com um nome (por exemplo, "suinocultura-web")
5. Copie o objeto `firebaseConfig` exibido

## Passo 5: Atualizar Arquivo de Configuração

1. Abra o arquivo `build/firebase-config.js` no Replit
2. Substitua o objeto `firebaseConfig` pelo que você copiou no passo anterior

Exemplo:
```javascript
const firebaseConfig = {
  apiKey: "AIzaSyC1p2MK9qXnSt6_JZpVEUZlVjZxo2QQyQQ",
  authDomain: "suinocultura-app.firebaseapp.com",
  projectId: "suinocultura-app",
  storageBucket: "suinocultura-app.appspot.com",
  messagingSenderId: "123456789012",
  appId: "1:123456789012:web:abc123def456ghi789jkl",
  measurementId: "G-ABCDEFGHIJ"
};
```

## Passo 6: Atualizar o Arquivo .firebaserc (se necessário)

Se você escolheu um nome diferente para o projeto, atualize o arquivo `.firebaserc`:

```json
{
  "projects": {
    "default": "seu-nome-de-projeto"
  }
}
```

## Passo 7: Executar o Build

1. No Replit, clique no workflow "Firebase Build" ou execute:

```bash
node build-firebase.js
```

## Passo 8: Fazer o Deploy

1. Execute o comando para deploy:

```bash
# Se você fez login com firebase login (ambiente local):
npx firebase deploy

# OU

# Se você usou firebase login:ci (ambiente Replit/não interativo):
npx firebase deploy --token "SEU_TOKEN_CI"
# Substitua SEU_TOKEN_CI pelo token recebido durante o processo de login:ci
```

2. Após o deploy, você receberá uma URL onde seu site estará disponível (geralmente no formato `https://seu-projeto.web.app`)

## Configuração para Download do APK

O arquivo APK do aplicativo Android é um espaço reservado até que você faça o upload do APK real. Para atualizar:

1. Gere o APK usando a página do desenvolvedor no Sistema Suinocultura
2. Faça o upload do APK para a pasta `build` substituindo o arquivo `suinocultura.apk`
3. Execute novamente o deploy:

```bash
# Com login normal:
npx firebase deploy

# OU com token CI:
npx firebase deploy --token "SEU_TOKEN_CI"
```

## Observações Importantes

- O hosting do Firebase tem um plano gratuito generoso com limites de tráfego
- Este método de deploy é apenas para o site informativo e download do APK
- O aplicativo Streamlit principal continuará rodando no Replit em `https://suinocultura.replit.app`
- Alterações no projeto Replit não são automaticamente sincronizadas com o Firebase
- Para atualizar o Firebase após alterações, execute novamente o build e o deploy

## Solução de Problemas

### Erro ao fazer login no Firebase

Se você encontrar problemas ao fazer login no Firebase através do Replit, tente usar um token de CI:

```bash
npx firebase login:ci
```

Siga as instruções e use o token gerado para autenticação.

### Erro 404 ao tentar baixar o APK

O APK precisa ser manualmente adicionado à pasta `build`. Verifique se o arquivo `suinocultura.apk` está presente antes do deploy.

### Problemas com as configurações do Firebase

Verifique se as credenciais no arquivo `firebase-config.js` estão corretas e correspondem às do seu projeto no console do Firebase.