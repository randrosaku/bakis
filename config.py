from psychopy import gui, core, data

import time

# Experiment parameters
EXP_NAME = f'exp-{time.strftime("%Y%m%d-%H%M%S")}'
TRIAL_LEN = 4
FLICKER_FREQ = 12
N_TRIALS = 1
N_BLOCKS = 1

# Hyperscanning parameters
CHANNELS_LIST = ["O1", "O2"]
SAMPLING_FREQ = 250
FREQ_BANDS = {"freq_bands": [1, 40]}
TMIN = 1
TMAX = 4
RECORD = False
USERS = {}

expName = "ssvep-stimuli"
exp = {
    "group": "001",
    "subj_1": "001",
    "subj_2": "002",
    "session": "001",
    "date": data.getDateStr(format="%Y%m%d-%H%M%S"),
    "expName": expName,
}


def showExpInfoDlg(expInfo):
    """
    Show participant info dialog.
    Parameters
    ==========
    expInfo : dict
        Information about this experiment, created by the `setupExpInfo` function.

    Returns
    ==========
    dict
        Information about this experiment.
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
