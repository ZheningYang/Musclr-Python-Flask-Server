FROM python:2.7
RUN pip install flask==1.0.2 flask_cors plotly networkx
RUN useradd -ms /bin/bash admin
USER admin
WORKDIR /app
COPY . /app
CMD ["python", "server.py"]
