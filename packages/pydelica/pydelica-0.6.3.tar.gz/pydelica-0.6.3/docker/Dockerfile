FROM openmodelica/openmodelica:v1.25.0-ompython
ENV DEBIAN_FRONTEND noninteractive
RUN apt-get update -y && \
    apt-get upgrade -y && \
    apt-get install -y \
    build-essential \
    wget curl \
    git python3-pip python3-tk tk-dev \
    make bzip2 sqlite libssl-dev libbz2-dev \
    libffi-dev libreadline-dev libsqlite3-dev \
    lsb-release  &&\
    apt-get clean && rm -rf /var/lib/apt/lists/*
ENV DEBIAN_FRONTEND ""

# Create User for Modelica
RUN useradd -m pde_user


WORKDIR /home/pde_user
USER pde_user

# Install extra OpenModelica Libraries
RUN echo "installPackage(Modelica, \"3.2.3\", exactMatch=true);" >> install.mos && \
    echo "installPackage(Modelica, \"4.0.0\", exactMatch=true);" >> install.mos
RUN omc install.mos

# Install PyEnv
RUN git clone https://github.com/pyenv/pyenv.git ~/.pyenv
RUN rm -r ~/.pyenv/.git
ENV HOME=/home/pde_user
ENV PYENV_ROOT=$HOME/.pyenv
ENV PATH $PYENV_ROOT/shims:$PYENV_ROOT/bin:$PYENV_ROOT/versions/3.13.1/bin$PATH
RUN pyenv install 3.13.1 && pyenv global 3.13.1 && pyenv rehash

# Install PyDelica in latest Python
RUN git clone https://gitlab.com/krizar/pydelica.git ~/.pydelica
WORKDIR /home/pde_user/.pydelica
RUN latesttag=$(git describe --tags) && git checkout "${latesttag}"
WORKDIR /home/pde_user
RUN pip install --upgrade pip
RUN $PYENV_ROOT/versions/3.13.1/bin/python3.13 -m pip install --upgrade pip
RUN pip install wheel
RUN $PYENV_ROOT/versions/3.13.1/bin/python3.13 -m pip install wheel
RUN pip install jupyter
RUN pip install Cython
RUN $PYENV_ROOT/versions/3.13.1/bin/python3.13 -m pip install Cython
RUN pip install numpy
RUN $PYENV_ROOT/versions/3.13.1/bin/python3.13 -m pip install numpy
RUN pip install ~/.pydelica
RUN $PYENV_ROOT/versions/3.13.1/bin/python3.13 -m pip install ~/.pydelica
RUN rm -r ~/.pydelica/
