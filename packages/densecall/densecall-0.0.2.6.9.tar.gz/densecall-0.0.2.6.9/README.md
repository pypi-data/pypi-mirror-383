# DENSECALL2

**DenseCall2: de novo base-calling of modifications using nanopore sequencing**

## Contents
- [DENSECALL2](#densecall2)
  - [Contents](#contents)
  - [Overview](#overview)
  - [Requirements](#requirements)
    - [Hardware](#hardware)
    - [Software](#software)
  - [Installation](#installation)
    - [Densecall2](#densecall2-1)
  - [Basecalling](#basecalling)
    - [Modcall](#modcall)
    - [Normal basecall](#normal-basecall)
    - [(optional) Training your own basecalling model](#optional-training-your-own-basecalling-model)
    - [Downstream Analysis](#downstream-analysis)
  - [Citing](#citing)
  - [License](#license)
  - [Acknowledgements](#acknowledgements)

## Overview

DenseCall2 is an updated base-caller built on an optimised Conformer architecture for nanopore-signal processing, enabling simultaneous base-calling and modification detection.

![image1](./doc/image1.png)

## Requirements

### Hardware
- **RAM**: 2 GB minimum; 16 GB or more recommended.
- **CPU**: 4 cores minimum, ≥ 2.3 GHz per core.
- **GPU**: NVIDIA RTX 4090 or newer (required for DenseCall2).

Benchmarks were collected on an ASUSTeK SVR TS700-E9-RS8 workstation  
(Xeon Silver 4214 @ 2.20 GHz, 64 GB RAM, RTX 4090 24 GB).

### Software
**Supported operating systems**
- Linux: Ubuntu 22.04 or newer.  
- Windows and macOS are not yet supported.

**Python**
- Version 3.10 or higher is required.  

## <span id="Installation">Installation</span>

### Densecall2

First, set up a new environment and install the necessary Python packages using conda and pip:

```shell
# 1.Create a new conda environment
conda create -n densecall python=3.10 -y
conda activate densecall

# 2. install Densecall2 package from PyPI
pip install densecall

# Or download and install Densecall2 from source

git clone https://github.com/LuChenLab/DENSECALL2.git
cd DENSECALL2
pip install -r requirements.txt
python setup.py develop


# 3. To install flash-attn, run the following command

pip install flash-attn==2.8.3 --no-build-isolation --no-cache-dir

```

## Basecalling

### Modcall
After installing Densecall2, download the pre-trained models for human-specific models from [Pre-trained basecalling models](). Available models include `dna_r9.4.1_hac_CG@v1.0.tar.gz` for r9.4.1 data and `dna_r10.4.1_hac_CG@v1.0.tar.gz` for r10.4.1 data.

Densecall2 provides a method for transforming `.fast5` or `.pod5` files into `.sam` format. Follow the commands below to perform basecalling:

```shell
# Activate the Densecall2 conda environment
conda activate densecall

# Download and extract the models
tar -xzvf dna_r9.4.1_hac_CG@v1.0.tar.gz 

# Perform basecalling on the .fast5 files to generate .sam files
densecall basecaller dna_r9.4.1_hac_CG@v1.0 /path/to/signal/ \
--mod --chunksize 12000 --overlap 600 \
--reference chr22.mmi  --recursive --alignment-threads 12 >mod.sam 
                     
```

### Normal basecall

without --mod option, the basecalling process is the same as normal basecalling.
```shell
densecall basecaller dna_r9.4.1_hac_CG@v1.0 /path/to/signal/ \
--chunksize 12000 --overlap 600 \
--recursive >result.fq

```

### (optional) Training your own basecalling model

`densecall train` - train a densecall2 model.

To train a model using your own reads, first get trained model from [Remora](https://github.com/nanoporetech/remora).

```shell
remora model download 
```

```shell
densecall basecaller  dna_r10.4.1_e8.2_400bps_hac@v3.5.2 ./chr1_fast5 --batchsize 64 --chunksize 5000 \
--reference chr1.mmi  --recursive --save-ctc --min-accuracy-save-ctc 0.9 \
--alphabet NACZGT \
--modified-codes Z \
--modified-base-model /path/to/dna_r10.4.1_e8.2_400bps_hac_v3.5.1_5mc_CG_v2.pt \
--max-reads 100000 --overlap 100 >r10_train_data/test.sam
```

Training a new model from scratch.  

```bash
densecall train test  --directory r10_train_data/ -f --batch 64  --epochs 30  \
--no-quantile-grad-clip --lr 0.002    --alphabet NACZGT \
--config conformer.toml   --new --compile
```

All training calls use Automatic Mixed Precision to speed up training. 



This must be manually installed as the flash-attn packaging system prevents it from being listed as a normal dependency.


### Downstream Analysis
The results were analyzed using the ONT tool [modkit](https://github.com/nanoporetech/modkit), which processes BAM files containing MM/ML tags to generate comprehensive statistical reports. This study specifically employed modkit's "validate" and "pileup" functions. 



## <span id="Citing">Citing</span>

A pre-print is going to be uploaded soon.



## <span id="License">License</span>

...

## Acknowledgements
We thank [Bonito](https://github.com/nanoporetech/bonito) for providing the source code. DenseCall2 is developed on the basic framework of Bonito's code. (The parts of save-ctc and converting outputs of the Conformer-based model to modcall sequences are revised based on Bonito's code following it's License.)
