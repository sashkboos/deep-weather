# Deep Learning for Post-Processing Ensemble Weather Forecasts 
 
We make available the data as well as the code that is necessary to run the models in our [paper](https://arxiv.org/abs/2005.08748) through this repository. It is our hope that our findings and the data can be used to further advance weather forecasting research.

## Research description

Our research focuses on applying recent architectures from Deep Learning to Ensemble Weather Forecasts. To achieve this we use global reforecast data from the ECMWF that we call **ENS10**, as well as reanalysis data **ERA5**. More specifically, ENS10 is aimed at providing researchers with a basic dataset of forecasted values that would be used in modern numerical weather prediction pipelines. Using ERA5 data as ground truth, we then use a subset of the ensemble forecasts to post-process and improve. Our aim is to help weather forecasting centers predict extreme weather events cheaper and more accurately. 

<p align="center">
<img width="40%" src="/report/G_Winston_E10_step1.png">
<img width="40%" src="/report/G_Winston_B5U5C-E10_step1.png">
</p>

In the case of tropical cyclone [Winston](https://en.wikipedia.org/wiki/Cyclone_Winston) we achieve a relative improvement of over 26% in forecast skill, measured in Continuous Ranked Probability Score (CRPS) over the full 10 member ensemble, using a subset of five trajectories. Additionally, the models specifically predict the future path of the cyclone more accurately. 

## Dependencies
In order to run our code in Python 3 through a virtual environment: Clone this repository, open a terminal, set the working directory to this directory and run:
```bash
python3 -m venv env
source env/bin/activate
pip install -r requirements.txt
```

We use tensorflow-gpu 1.14, therefore you will also need to install [CUDA 10.0](https://developer.nvidia.com/cuda-10.0-download-archive) and [cuDNN 7.4](https://developer.nvidia.com/cudnn) separately. You will need to register on Nvidia and select 7.4 from the cuDNN versions.  

The newest Uncertainty Quantification models are now also available in PyTorch-Lightning, please refer to the PyTorch [README](Uncertainty_Quantification/Pytorch/README.md)

If you prefer using conda, which will install CUDA and cuDNN automatically, use the commands:  
```
conda create -y --name env python==3.7
conda install --force-reinstall -y -q --name env -c conda-forge --file conda-requirements.txt
conda activate env
pip install eccodes==0.9.5
```

## Data
The raw GRIB data we used for our experiments is available at:
- [ENS10](https://confluence.ecmwf.int/display/UDOC/ECMWF+ENS+for+Machine+Learning+%28ENS4ML%29+Dataset) - easily download and use via the [CliMetLab plugin](https://github.com/spcl/climetlab-maelstrom-ens10).
- [ERA5](https://cds.climate.copernicus.eu/cdsapp#!/dataset/reanalysis-era5-pressure-levels?tab=form)

- [Alternate link](http://spclstorage.inf.ethz.ch/projects/deep-weather/) in case the previous ones do not work. (The ENS10 data files are marked with 2018, but contain the data of all years described in our paper)

To transform the Deep Weather data into Numpy arrays and TensorFlow records as done for our paper, refer to our preprocessing steps. If you want to use different parameters directly from the original sources you will have to edit the preprocessing scripts.

## Contents

We separate our experiments into the exploration of ensemble output bias correction, which needs ERA5 data as the ground truth, and ensemble uncertainty forecasting using reduced ensemble members, which runs solely on ENS10 data.
To make a combined prediction aimed at reducing the forecast skill (CRPS), you will need to provide a path to the bias corrected mean and ground truth in the appropriate form in [preprocessing_parameters.py](Uncertainty_Quantification/Preprocessing/preprocessing_parameters.py), as well as set the CRPS flag there and in [parameters.py](Uncertainty_Quantification/parameters.py).

### Contents structure
`Bias_Correction` Preprocessing and model for Bias Correction, refer to `Bias_Correction/README.md`
`Uncertainty_Quantification` Preprocessing and model for Uncertainty Quantification
 - `\parameters.py` All hyperparameters and settings for the model, edit this file to add the paths to your preprocessed data
 - `\predict.py` Evaluates the model on test data
 - `\RESNET2D.py` Our TensorFlow model for Uncertainty Quantification
 - `\train.py` Runs training and validation operations on the model
 - `\Preprocessing` Contains all necessary files to transform GRIB files into TensorFlow records
    - `\GRIB2npy.py` Converts GRIB files to Numpy arrays, needs to be adjusted for the selected parameters
    - `\npy2tfr.py` Converts the Numpy arrays to TensorFlow records and performs the Local Area-wise Standardization (LAS) described in our paper
    - `\preprocessing_parameters` Parameters for all preprocessing steps, be sure to edit the path folders
    - `\means.npy` Precomputed means for the LAS
    - `\stddevs.npy` Precomputed standard deviations for the LAS
 - `\Pytorch` PyTorch-Lightning models and training for Uncertainty Quantification, refer to `Pytorch/README.md`

## How to cite
```
@article{grnquist2020deep,
    title={Deep Learning for Post-Processing Ensemble Weather Forecasts},
    author={Peter Grönquist and Chengyuan Yao and Tal Ben-Nun and Nikoli Dryden and Peter Dueben and Shigang Li and Torsten Hoefler},
    year={2020},
    eprint={2005.08748},
    archivePrefix={arXiv},
    primaryClass={cs.LG}
}
```
Should there be any questions, feel free to contact us.


