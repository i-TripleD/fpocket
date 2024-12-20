FROM python:3.13-slim-bookworm
RUN groupadd -r fpocket && useradd --no-log-init -r -g fpocket fpocket
RUN apt update -y && apt install -y gcc g++ make libnetcdf-dev && rm -rf /var/lib/apt/lists/*

# all of this mess is essentially to have a minimalistic build at the end
COPY makefile /opt/fpocket/
COPY src /opt/fpocket/src
COPY man /opt/fpocket/man
COPY headers /opt/fpocket/headers
COPY obj /opt/fpocket/obj
COPY scripts /opt/fpocket/scripts
COPY bin /opt/fpocket/bin
COPY plugins/LINUXAMD64 /opt/fpocket/plugins/LINUXAMD64
COPY plugins/include /opt/fpocket/plugins/include
COPY plugins/noarch /opt/fpocket/plugins/noarch

WORKDIR /opt/fpocket

RUN make && make install && make clean
USER fpocket

WORKDIR /home/fpocket

RUN pip install fastapi[standard]
COPY main.py main.py

WORKDIR /tmp
ENTRYPOINT ["/home/fpocket/.local/bin/fastapi", "run","/home/fpocket/main.py"]
