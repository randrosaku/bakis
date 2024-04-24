from baboard.utils.logging_config import lg

logger = lg.create_logger("ssvep-experiment.log")

from utils.psychopy import setupData, setupWindow, setupInputs, run, saveData, quit
from model import Model

from config import expInfo


def launch_experiment():

    model = Model(logger=logger)
    model.init_stimulation()

    thisExp = setupData(expInfo=expInfo)
    win = setupWindow(expInfo=expInfo)
    inputs = setupInputs(expInfo=expInfo, thisExp=thisExp, win=win)

    model.logger.info("Hyperscanning session starting")

    run(model=model, expInfo=expInfo, thisExp=thisExp, win=win, inputs=inputs)
    saveData(thisExp=thisExp)

    model.disconnect_stimulation()
    model.logger.info("Hyperscanning session ended successfully")

    quit(thisExp=thisExp, win=win)


if __name__ == "__main__":
    launch_experiment()
