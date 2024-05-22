# BAHyP

BAHyP streamlines the setup of research environments, the collection and processing of data, and the computation of interpersonal brain synchronization. This pipeline allows neuroscientists to customize their hyperscanning experiments by adjusting parameters like the method for artifact removal, result exporting, and the duration of visual stimuli tailored to their specific studies. The system is designed to facilitate the study of interpersonal brain synchronization by enabling real-time processing, synchronization computations, and feedback displays.

Developed by Rasa Kundrotaite, IFD-0

# Installation guide
## Create a development (conda) environment
```
conda env create -f environment.yml
```
## Install BrainAccess Board SDK and Python API
Installation steps can be found on [BrainAccess website](https://www.brainaccess.ai/download/)

## Run the application
1. Run BrainAccess Board
2. Connect EEG devices to the Board
3. Start the BAHyP. From root folder ```bakis``` run
```
python run.py
```

## Additional information
If you install any new libraries, add them to requirements.txt
```
pip list --format=freeze > requirements.txt
```
