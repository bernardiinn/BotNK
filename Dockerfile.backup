FROM python:3.11-slim

WORKDIR /app

# Copiar todos os arquivos do projeto
COPY . .

# Instalar dependências
RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "bot.py"]
