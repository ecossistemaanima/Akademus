# 🔑 Configuração do Google OAuth 2.0 (Login with Google)

O **Akademus** utiliza o padrão OpenID Connect (OIDC) com o **Google Identity Services** para permitir que estudantes e docentes façam login com suas contas acadêmicas ou pessoais Google.

---

## 🛠️ Passo a Passo no Google Cloud Console

1. Acesse o **[Google Cloud Console](https://console.cloud.google.com/)**.
2. Crie um projeto ou selecione um existente (ex: `Akademus`).
3. Vá em **APIs e Serviços** > **Tela de consentimento OAuth**:
   - Escolha o tipo de usuário (**Externo** ou **Interno**, caso tenha domínio Google Workspace institucional).
   - Preencha o nome do App: `Akademus`.
   - Adicione os escopos básicos: `openid`, `.../auth/userinfo.email`, `.../auth/userinfo.profile`.
4. Vá em **Credenciais** > **Criar Credenciais** > **ID do cliente OAuth**:
   - **Tipo de aplicativo:** *Aplicativo da Web* (*Web application*).
   - **Nome:** `Akademus Web Client`.
   - **Origens JavaScript autorizadas:**
     - `https://akademus.tux.me.uk`
     - `http://localhost:8080` (opcional para testes puramente locais)
   - **URIs de redirecionamento autorizados:**
     - `https://akademus.tux.me.uk/login/callback`
     - `http://localhost:8080/login/callback`
5. Clique em **Criar** e copie o **Client ID** e o **Client Secret**.

---

## ⚙️ Configuração no `.env`

Adicione as chaves no seu arquivo local `.env`:

```bash
GOOGLE_CLIENT_ID="seu-id.apps.googleusercontent.com"
GOOGLE_CLIENT_SECRET="GOCSPX-seu-secret"
```

Reinicie a aplicação ou deixe o auto-reload carregar. O botão **"Entrar com Google"** redirecionará diretamente para a tela de autenticação oficial do Google e devolverá o usuário logado no Akademus!
