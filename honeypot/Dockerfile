FROM python:3.11-slim

WORKDIR /app

RUN pip install flask

COPY honeypot.py logger.py ./

# Create logs directory
RUN mkdir -p /app/logs

EXPOSE 8888

CMD ["python", "-u", "honeypot.py"]
