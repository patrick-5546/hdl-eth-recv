# Assignment 1

## Setup

1. Install Miniconda ([reference](https://engineeringfordatascience.com/posts/install_miniconda_from_the_command_line/#how-to-install-miniconda-on-the-command-line-))

    ```sh
    mkdir -p ~/miniconda3
    wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O ~/miniconda3/miniconda.sh
    bash ~/miniconda3/miniconda.sh -b -u -p ~/miniconda3
    rm -rf ~/miniconda3/miniconda.sh
    ~/miniconda3/bin/conda init tcsh
    ```

2. Create environment and install conda dependencies in it

    ```sh
    conda create --name cocotb --channel conda-forge --yes cocotb
    ```

3. Activate environment and install pip dependencies in it

    ```sh
    conda activate cocotb
    pip install -r requirements.txt
    ```

## Run

```sh
python test_recv.py -h
```

### Clean

```sh
cocotb-clean -r
```
