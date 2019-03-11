# TODO
- Fix lighting for rendering images (rendering in general)
- Fix positioning of objects in scene


# StereoBlender


Offers the ability to configure a stereo vision setup in blender (Version 2.8) and create a synthetic dataset.


Part of my master thesis for visualizing a stereo setup and how the change of the setup change the view perspective and overall setup.

## Prerequisites
- Blender 2.8 Beta 
- PYYAML

## Configuration

Before starting you have to configure **2 Paths**:
- `stereo.py`: Full path of the configuration file
- `stereo.yaml`: Full path where the dataset should be stored

The configuration of the stereo setup can be done using the YAML configuration file `stereo.yaml`.

# References
The basic idea and also some code snippets of this repository are taken from https://github.com/LouisFoucard/DepthMap_dataset.
