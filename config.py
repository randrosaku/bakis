from psychopy import gui, core, data

import time

def metadata_gui(expInfo: dict):
    """Show participant info dialog.

    Args:
        expInfo (dict): Information about this experiment, created by the `setupExpInfo` function.

    Returns:
        dict: Information about this experiment.
    """
    dlg = gui.DlgFromDict(dictionary=expInfo, sortKeys=False, title=expName)
    if dlg.OK == False:
        core.quit()

    return expInfo

def validateInput(expInfo: dict):
    """Ensure subject IDs are integers.

    Args:
        expInfo (dict): Information about this experiment, created by the `setupExpInfo` function.

    Returns:
        dict: Information about this experiment, with validated subject IDs.
    """
    poppedKeys = {
            "date": expInfo.pop("date", data.getDateStr()),
            "expName": expInfo.pop("expName", expName),
        }

    metadata_gui(expInfo)

    while True:
        try:
            expInfo['subj_1'] = int(expInfo['subj_1'])
            expInfo['subj_2'] = int(expInfo['subj_2'])
            expInfo.update(poppedKeys)
            return expInfo

        except ValueError:
            errorDlg = gui.DlgFromDict(dictionary={}, title="Error: Subject IDs must be integers")

            if errorDlg.OK:
                metadata_gui(expInfo)
            else:
                core.quit()

# Testing mode
TESTING = True

# Experiment parameters
EXP_NAME = f'exp-{time.strftime("%Y%m%d-%H%M%S")}'
TRIAL_LEN = 4
FLICKER_FREQ = 12
N_TRIALS = 2
N_BLOCKS = 1

# Hyperscanning parameters
CHANNELS_LIST = ["O1", "O2"]
EVENT_DICT = {"target": 1}
SAMPLING_FREQ = 250
FREQ_BANDS = {"freq_bands": [1, 40]}
TMIN = 2
TMAX = 4
RECORD = True
PROCESSING_MODE = ""

# Psychopy parameters
expName = "ssvep-stimuli"

#############################################
# Initial values that should not be changed #
#############################################
exp = {
    "group": "001",
    "subj_1": "001",
    "subj_2": "002",
    "session": "001",
    "date": data.getDateStr(format="%Y%m%d-%H%M%S"),
    "expName": expName,
}
USERS = {}

expInfo = validateInput(expInfo=exp)

COMMAND = {
    "task": expName,
    "run": 1,
    "session": expInfo["session"],
    "subject": expInfo["group"],
}
#############################################