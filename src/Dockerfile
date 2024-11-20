FROM python:3.10.12

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY main.py .
COPY utils.py .
COPY Archetype.py .
copy prompt_templates.py .
copy pages pages
COPY .streamlit .streamlit

CMD ["streamlit", "run", "main.py"]
