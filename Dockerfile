# Use an official Python runtime as a parent image
FROM python:3.10.12-slim

# Install required packages for building and audio libs
RUN apt-get update && apt-get install -y \
        build-essential \
        autoconf \
        automake \
        libtool \
        pkg-config \
        git \
        cmake \ 
        ffmpeg \
    && rm -rf /var/lib/apt/lists/*

RUN mkdir -p cache && chmod 777 cache

RUN useradd -m -u 1000 user

USER user

ENV HOME=/home/user \
	PATH=/home/user/.local/bin:$PATH

# Set the working directory to the user's home directory
WORKDIR $HOME/app
 
# Install api requirements
COPY --chown=user requirements.txt $HOME/app/

RUN pip install -r requirements.txt
# install nemo
RUN pip install nemo_toolkit[all]==1.21

# download model from hf hub
RUN huggingface-cli download projecte-aina/stt-ca-citrinet-512 stt-ca-citrinet-512.nemo --local-dir  $HOME/app/

COPY --chown=user app.py $HOME/app/

# Fix ownership issues
USER root
RUN chown -R user:user $HOME/app
USER user

EXPOSE 8000

CMD ["python3", "-u", "app.py"]