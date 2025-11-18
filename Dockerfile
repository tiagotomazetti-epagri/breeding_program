# Usar uma imagem oficial do Python como base.
# A versão 3.11 é uma escolha moderna e estável.
FROM python:3.11-slim

# Define variáveis de ambiente para garantir que o Python rode sem buffer
# e não crie arquivos .pyc, mantendo o container limpo.
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Define o diretório de trabalho dentro do container.
# Todos os comandos a seguir serão executados a partir deste diretório.
WORKDIR /app

# Copia o arquivo de dependências para o container.
# (Vamos criar este arquivo no próximo passo).
COPY requirements.txt /app/

# Instala as dependências do projeto.
RUN pip install --no-cache-dir -r requirements.txt

# Copia todo o código do seu projeto para dentro do diretório de trabalho do container.
COPY . /app/

# Expõe a porta 8000 do container para que possamos nos conectar a ela
# a partir da nossa máquina (host).
EXPOSE 8000

# O comando que será executado quando o container iniciar.
# Inicia o servidor de desenvolvimento do Django, escutando em todas as interfaces (0.0.0.0).
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
