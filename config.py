from psychopy import gui, core, data

import time

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
RECORD = False
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
#############################################


def showExpInfoDlg(expInfo: dict):
    """Show participant info dialog.

    Args:
        expInfo (dict): Information about this experiment, created by the `setupExpInfo` function.

    Returns:
        dict: Information about this experiment.
    """

    poppedKeys = {
        "date": expInfo.pop("date", data.getDateStr()),
        "expName": expInfo.pop("expName", expName),
    }

    dlg = gui.DlgFromDict(dictionary=expInfo, sortKeys=False, title=expName)
    if dlg.OK == False:
        core.quit()

    expInfo.update(poppedKeys)
    return expInfo


expInfo = showExpInfoDlg(expInfo=exp)

COMMAND = {
    "task": expName,
    "run": 1,
    "session": expInfo["session"],
    "subject": expInfo["group"],
}
