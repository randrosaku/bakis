from psychopy import gui, core, data

import time

# Experiment parameters
EXP_NAME = f'exp-{time.strftime("%Y%m%d-%H%M%S")}'
FLICKER_FREQ = 12
TRIALS_PER_BLOCK = 5

# Hyperscanning parameters
CHANNELS_LIST = ["O1", "O2"]
SAMPLING_FREQ = 250
FREQ_BANDS = {"freq_bands": [1, 40]}
TMIN = 1
TMAX = 4
BASELINE = (0, 0)
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
