#!/bin/bash
# Install requirements
conda install -c conda-forge montreal-forced-aligner -y
pip install -r requirements.txt

# Download MFA models
mfa model download acoustic english_us_arpa
mfa model download dictionary english_us_arpa