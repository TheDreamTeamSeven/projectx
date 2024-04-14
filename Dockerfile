# Użyj obrazu systemu Unix (Ubuntu) jako podstawy
FROM ubuntu:20.04

# Ustaw katalog roboczy w kontenerze
WORKDIR /app

# Skopiuj pliki projektu do katalogu roboczego
COPY azure_connection/ /app/azure_connection/
COPY static/ /app/static/
COPY templates/ /app/templates/
COPY app.py /app/
COPY history.py /app/
COPY chat_integration.py /app/
COPY requirements.txt /app/
COPY set_up_driver.sh /usr/local/bin/

#ENV LD_LIBRARY_PATH=/usr/lib/x86_64-linux-gnu/:$LD_LIBRARY_PATH

# Zainstaluj zależności Python z pliku requirements.txt
RUN apt-get update 
RUN apt-get install -y python3 python3-pip  
# Instaluj systemowe zależności
RUN apt-get update && \
    apt-get install -y python3 python3-pip gnupg2 curl apt-transport-https unixodbc unixodbc-dev

RUN apt-get update && apt-get install -y lsb-release && apt-get clean all

RUN pip install --no-cache-dir -r requirements.txt


# Grant execute permissions to the script
RUN chmod +x /usr/local/bin/set_up_driver.sh

# Run the script to install the driver
RUN  /usr/local/bin/set_up_driver.sh

# Ekspozycja portu 5000 (domyślny port Flask)
EXPOSE 5000

CMD ["python3", "app.py"]
