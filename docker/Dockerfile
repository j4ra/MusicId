FROM python:3.10-slim

RUN apt update
RUN apt install -y ffmpeg

WORKDIR /script/
ADD /src/ /script/

RUN pip install -r requirements

ENTRYPOINT [ "python3", "init.py" ]

CMD ["/bin/bash"]