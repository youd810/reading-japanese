FROM python:3.13-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt
RUN python -m spacy download ja_ginza

COPY . .

EXPOSE 7860

CMD ["uvicorn", "japanese:app", "--host", "0.0.0.0", "--port", "7860"]
