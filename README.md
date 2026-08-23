# Sistema de Gerenciamento de Funcionários

Sistema web desenvolvido em Django para gerenciamento de funcionários, departamentos e registro de ponto eletrônico. Projeto desenvolvido como avaliação da disciplina **WEB I** (Segunda Unidade).

---

## 📌 Funcionalidades

- **CRUD completo** de funcionários e departamentos
- **Registro de ponto eletrônico** com entrada e saída
- **Controle de permissões** (Gerente e Funcionário)
- **Filtros, paginação e ordenação** nas listagens
- **Interface moderna** inspirada no GNOME/Adwaita (light/dark)
- **Soft delete** para funcionários
- **Logging** de ações do gerente
- **Signals** para criação automática de perfis
- **Service Layer** para lógica de negócio

---

## 🛠️ Tecnologias

- **Python 3.14**
- **Django 6.1**
- **PostgreSQL**
- **Django ORM** com filtros avançados
- **Class-Based Views (CBVs)**
- **CSS customizado** (inspirado no Adwaita)

---

## 📦 Como rodar o projeto localmente

### 1. Clonar o repositório

```bash
git clone https://github.com/paulo-bento/sistema-gerenciamento-funcionario.git
cd sistema-gerenciamento-funcionario
```

### 2. Criar e ativar o ambiente virtual

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows
```

### 3. Instalar as dependências

```bash
pip install -r requirements.txt
```

### 4. Configurar o banco de dados (PostgreSQL)

Crie um banco de dados no PostgreSQL:

```bash
sudo -u postgres psql -c "CREATE DATABASE gerenciamento_funcionarios;"
```

### 5. Criar arquivo `.env` na raiz do projeto

```env
DB_NAME=gerenciamento_funcionarios
DB_USER=postgres
DB_PASSWORD=sua_senha
DB_HOST=localhost
DB_PORT=5432
SECRET_KEY=django-insecure-!hab0&z1x+$$m^r@b#7wvqg=z-wcmy&488my%(4w=)cm#%_e7z
```

### 6. Rodar as migrações

```bash
python manage.py migrate
```

### 7. Criar um superusuário

```bash
python manage.py createsuperuser
```

### 8. Rodar o servidor

```bash
python manage.py runserver
```

Acesse: [http://127.0.0.1:8000/](http://127.0.0.1:8000/)

---

## 👥 Como adicionar usuários e permissões

O sistema possui dois perfis principais: **Gerente** e **Funcionário**. Cada um tem permissões específicas.

### 1. Acessar o Django Admin

Com o servidor rodando, acesse: [http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/) e faça login com o superusuário criado.

### 2. Criar os grupos de permissão

- No menu lateral, clique em **"Groups"** (Grupos) e depois em **"Add Group"**.
- Crie o grupo **"Gerente"** e marque **todas** as permissões do app `core` (add, change, delete, view para todos os modelos).
- Crie o grupo **"Funcionario"** e marque **apenas** as permissões:
  - `core | funcionario | Can view funcionario`
  - `core | registro ponto | Can view registro ponto`
  - `core | departamento | Can view departamento` (opcional)

### 3. Criar usuários

- No admin, clique em **"Users"** e **"Add User"**.
- Preencha o nome de usuário, senha e email (se desejar).
- Após criar, edite o usuário e vá até a seção **"Groups"** para adicioná-lo ao grupo correspondente (Gerente ou Funcionario).
- Salve.

### 4. Criar funcionários associados

Existem duas formas:

#### Via formulário do site

- Faça login como gerente.
- Acesse **"Gerenciar Funcionários"** → **"+ Novo Funcionário"**.
- Preencha os dados (nome, usuário, senha, departamento, cargo, etc.).
- O sistema criará automaticamente um usuário e o vinculará ao funcionário.

#### Via admin

- No admin, clique em **"Funcionarios"** → **"Add Funcionario"**.
- Selecione um usuário já existente e preencha os demais campos.
- Salve.

### 5. Testar permissões

- **Gerente:** pode criar, editar, deletar e visualizar todos os funcionários, departamentos e registros de ponto.
- **Funcionário:** pode ver apenas seus próprios dados, bater ponto e visualizar seus registros.

---

## 🔐 Acessos padrão (exemplo)

| Perfil | Usuário | Senha |
|--------|---------|-------|
| Gerente | `admin` | `admin123` |
| Funcionário | `joao` | `123456` |

*(Os usuários devem ser criados conforme as instruções acima.)*

---

## 📁 Estrutura do Projeto

```
├── config/
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── core/
│   ├── models.py
│   ├── views.py
│   ├── forms.py
│   ├── urls.py
│   ├── admin.py
│   ├── signals.py
│   ├── services/
│   │   └── registro_ponto_service.py
│   └── templates/
│       └── core/
├── static/
│   └── css/
│       └── style.css
├── .env
├── manage.py
└── requirements.txt
```

---

## 📄 Licença

Este projeto está sob a licença MIT. Consulte o arquivo [LICENSE](LICENSE) para mais detalhes.

---

## 👤 Autor

**Paulo Bento**  
[GitHub](https://github.com/paulo-bento)

---

## 📬 Contato

Para dúvidas ou sugestões, abra uma issue no repositório ou entre em contato pelo Discord.
