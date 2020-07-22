[![MIT License](https://img.shields.io/apm/l/atomic-design-ui.svg?)](https://github.com/tterb/atomic-design-ui/blob/master/LICENSEs)
[![Version](https://badge.fury.io/gh/tterb%2FHyde.svg)](https://badge.fury.io/gh/tterb%2FHyde)

# aspBEEF

## What is aspBEEF?

**aspBEEF** is an Answer Set Programming implementation of the BEEF Tool proposed and developed by Sachin Grover, Chiara Pulice, Gerardo I. Simari and V. S. Subrahmanian in [BEEF: Balanced English Explanations of Forecasts](https://ieeexplore.ieee.org/document/8668423).

The aim of the original tool and aspBEEF is to be able to find explanations to classifications performed by an arbitrary method, such as KMeans.

## How does it work?

Given any given dataset in CSV format, a target feature and a k value, aspBEEF performs a classification of the dataset using KMeans and then tries to fit the output in boxes. These boxes are then used to provide supporting or opposing rules to the classification of any given point of the dataset, thus providing the user with methods to better understand the outcome.

Besides written rules based on parameters, aspBEEF also generates visual HTML reports.

## Requirements

* Python >= 3.6
* the clingo module, which can be obtained from conda running ```conda install -c potassco clingo```


## Installation

Clone the repository and run ```git submodule update``` to fetch asparser. Then run ```make``` inside the asparser folder.
Run ```pip install -r requirements.txt```

## Running aspBEEF

The easier way to understand the tool is running one of the provided examples, such as IrisMid, a reduced version of the IRIS dataset.

```python aspbeef.py input/IrisMid.csv species -k 3 --approximate --report```

What we are doing here is:
* Calling the main script with the desired dataset in CSV format
* Telling aspBEEF that the ```species``` field is not part of the data itself but the original class
* Specifying the K value for KMeans and the number of boxes to find for the explanation, 3 in this case
* ```--approximate``` tells aspBEEF to fit the boxes to the classification made, instead of the original data

All of the possible tweaks and options are explained using the ```--help``` parameter.



