# syntax=docker/dockerfile:1
FROM python:3.10-slim
WORKDIR /536931949_EQUIPE23
ENV FLASK_APP=main.py
ENV FLASK_RUN_HOST=0.0.0.0
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
RUN pip install torch --index-url https://download.pytorch.org/whl/cpu
RUN python -m spacy download en_core_web_sm
EXPOSE 5000
COPY . .
CMD ["flask", "run", "--debug"]