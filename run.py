from baboard.utils.logging_config import lg

logger = lg.create_logger("bakis.log")

from utils.psychopy import setupData, setupWindow, setupInputs, run, saveData, quit
from model import Model

from config import expInfo


def launch_experiment():

    model = Model(logger=logger)
    model.init_stimulation()

    try:
        thisExp = setupData(expInfo=expInfo)
        win = setupWindow(expInfo=expInfo)
        inputs = setupInputs(win=win)

        model.logger.info("Hyperscanning session starting")

        run(model=model, expInfo=expInfo, thisExp=thisExp, win=win, inputs=inputs)
        saveData(thisExp=thisExp)
        model.logger.info("Hyperscanning session ended successfully")

    except KeyboardInterrupt:
        model.logger.info(f"SSVEP hyperscanning session terminated by user")

    except Exception as e:
        model.logger.error(f"SSVEP hyperscanning session exception: {e}")

    finally:

        model.disconnect_stimulation()
        quit(thisExp=thisExp, win=win)


if __name__ == "__main__":
    launch_experiment()
