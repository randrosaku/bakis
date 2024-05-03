"""This experiment was created with the help of PsychoPy3 Experiment Builder (v2023.2.3)

    Peirce J, Gray JR, Simpson S, MacAskill M, Höchenberger R, Sogo H, Kastman E, Lindeløv JK. (2019) 
        PsychoPy2: Experiments in behavior made easy Behav Res 51: 195. 
        https://doi.org/10.3758/s13428-018-01193-y

"""

from psychopy import prefs
from psychopy import plugins

plugins.activatePlugins()
prefs.hardware["audioLib"] = "ptb"
prefs.hardware["audioLatencyMode"] = "3"

from psychopy import visual, core, data, session
from psychopy.tools import environmenttools
from psychopy.constants import (
    NOT_STARTED,
    STARTED,
    FINISHED,
)

import os

import psychopy.iohub as io
from psychopy.hardware import keyboard

from config import expName, FLICKER_FREQ, N_TRIALS, N_BLOCKS, TMAX
from utils.synchronization import Synchronization
from model import Model

result = -1
_thisDir = os.path.dirname(os.path.abspath(__file__))


def setupData(expInfo: dict, dataDir: str = None):
    """Make an ExperimentHandler to handle trials and saving.

    Args:
        expInfo (dict): Information about this experiment, created by the `setupExpInfo` function.
        dataDir (str): Folder to save the data to, leave as None to create a folder in the current directory.

    Returns:
        psychopy.data.ExperimentHandler: Handler object for this experiment.
    """

    if dataDir is None:
        dataDir = _thisDir
    filename = "data/%s_%s_%s" % (expInfo["group"], expName, expInfo["date"])

    if os.path.isabs(filename):
        dataDir = os.path.commonprefix([dataDir, filename])
        filename = os.path.relpath(filename, dataDir)

    thisExp = data.ExperimentHandler(
        name=expName,
        version="",
        extraInfo=expInfo,
        runtimeInfo=None,
        originPath="psychopy.py",
        savePickle=True,
        saveWideText=True,
        dataFileName=dataDir + os.sep + filename,
        sortColumns="time",
    )

    return thisExp


def setupWindow(expInfo: dict = None, win: visual.Window = None):
    """Setup the Window

    Args:
        expInfo (dict): Information about this experiment, created by the `setupExpInfo` function.
        win (psychopy.visual.Window): Window to setup, leave as None to create a new window.

    Returns:
        psychopy.visual.Window: Window in which to run this experiment.
    """
    if win is None:
        win = visual.Window(
            size=(1024, 768),
            fullscr=False,
            screen=0,
            winType="pyglet",
            allowStencil=False,
            monitor="testMonitor",
            color=[0, 0, 0],
            colorSpace="rgb",
            backgroundImage="",
            backgroundFit="none",
            blendMode="avg",
            useFBO=True,
            units="height",
        )
        if expInfo is not None:
            expInfo["frameRate"] = win.getActualFrameRate()
    else:
        win.color = [0, 0, 0]
        win.colorSpace = "rgb"
        win.backgroundImage = ""
        win.backgroundFit = "none"
        win.units = "height"
    win.mouseVisible = False
    win.hideMessage()
    return win


def setupInputs(win: visual.Window):
    """Setup keyboard input

    Args:
        expInfo (dict): Information about this experiment, created by the `setupExpInfo` function.
        win (psychopy.visual.Window): Window in which to run this experiment.

    Returns:
        dict: Dictionary of input devices by name.
    """
    ioConfig = {}

    ioConfig["Keyboard"] = dict(use_keymap="psychopy")
    ioServer = io.launchHubServer(window=win, **ioConfig)

    defaultKeyboard = keyboard.Keyboard(backend="iohub")

    return {"ioServer": ioServer, "defaultKeyboard": defaultKeyboard}


def run(
    model: Model,
    expInfo: dict,
    thisExp: data.ExperimentHandler,
    win: visual.Window,
    inputs: dict,
    globalClock: core.Clock = None,
    thisSession: session.Session = None,
):
    """Run the experiment.

    Args:
        model (Model): SSVEP model used for experiment
        expInfo (dict): Information about this experiment, created by the `setupExpInfo` function.
        thisExp (psychopy.data.ExperimentHandler): Handler object for this experiment, contains the
        data to save and information about where to save it to.
        win (psychopy.visual.Window): Window in which to run this experiment.
        inputs (dict): Dictionary of input devices by name.
        globalClock (psychopy.core.clock.Clock): Clock to get global time from - supply None to make a new one.
        thisSession (psychopy.session.Session): Handle of the Session object this experiment is being run from, if any.
    """
    thisExp.status = STARTED
    exec = environmenttools.setExecEnvironment(globals())

    ioServer = inputs["ioServer"]
    defaultKeyboard = inputs["defaultKeyboard"]

    os.chdir(_thisDir)

    filename = thisExp.dataFileName
    frameTolerance = 0.001
    endExpNow = False

    if "frameRate" in expInfo and expInfo["frameRate"] is not None:
        frameDur = 1.0 / round(expInfo["frameRate"])
    else:
        frameDur = 1.0 / 60.0

    # --- Initialize components for Routine "instrPractice" ---
    message = visual.TextStim(
        win=win,
        name="message",
        text="Press space to continue",
        font="Open Sans",
        pos=(0, 0),
        height=0.05,
        wrapWidth=None,
        ori=0.0,
        color="white",
        colorSpace="rgb",
        opacity=None,
        languageStyle="LTR",
        depth=0.0,
    )
    key_resp = keyboard.Keyboard()

    # --- Initialize components for Routine "trial" ---
    stimuli = visual.ShapeStim(
        win=win,
        name="stimuli",
        size=(0.025, 0.025),
        vertices="circle",
        ori=0.0,
        pos=(0, 0),
        anchor="center",
        lineWidth=1.0,
        colorSpace="rgb",
        lineColor="black",
        fillColor="black",
        opacity=None,
        depth=0.0,
        interpolate=True,
    )
    target_notice = visual.TextStim(
        win=win,
        name="target_notice",
        text="+",
        font="Open Sans",
        pos=(0, 0),
        height=0.03,
        wrapWidth=None,
        ori=0.0,
        color="white",
        colorSpace="rgb",
        opacity=None,
        languageStyle="LTR",
        depth=-2.0,
    )
    rest = visual.TextStim(
        win=win,
        name="rest",
        text=None,
        font="Open Sans",
        pos=(0, 0),
        height=0.05,
        wrapWidth=None,
        ori=0.0,
        color="white",
        colorSpace="rgb",
        opacity=None,
        languageStyle="LTR",
        depth=-2.0,
    )

    # --- Initialize components for Routine "syncFeedback" ---
    text = visual.TextStim(
        win=win,
        name="text",
        text="Brain synchronization value: "
        + str(result)
        + "\n\nPress space to continue",
        font="Open Sans",
        pos=(0, 0),
        height=0.05,
        wrapWidth=None,
        ori=0.0,
        color="white",
        colorSpace="rgb",
        opacity=None,
        languageStyle="LTR",
        depth=0.0,
    )
    key_resp_2 = keyboard.Keyboard()

    # --- Initialize components for Routine "thanks" ---
    text_2 = visual.TextStim(
        win=win,
        name="text_2",
        text="Thank you for participating in this experiment\n\nPress q to exit",
        font="Open Sans",
        pos=(0, 0),
        height=0.05,
        wrapWidth=None,
        ori=0.0,
        color="white",
        colorSpace="rgb",
        opacity=None,
        languageStyle="LTR",
        depth=0.0,
    )
    key_resp_3 = keyboard.Keyboard()

    if globalClock is None:
        globalClock = core.Clock()
    if ioServer is not None:
        ioServer.syncClock(globalClock)
    routineTimer = core.Clock()
    win.flip()

    expInfo["expStart"] = data.getDateStr(
        format="%Y-%m-%d %Hh%M.%S.%f %z", fractionalSecondDigits=6
    )

    # --- Prepare to start Routine "instrPractice" ---
    continueRoutine = True

    thisExp.addData("instrPractice.started", globalClock.getTime())
    key_resp.keys = []
    key_resp.rt = []
    _key_resp_allKeys = []

    instrPracticeComponents = [message, key_resp]
    for thisComponent in instrPracticeComponents:
        thisComponent.tStart = None
        thisComponent.tStop = None
        thisComponent.tStartRefresh = None
        thisComponent.tStopRefresh = None
        if hasattr(thisComponent, "status"):
            thisComponent.status = NOT_STARTED

    t = 0
    _timeToFirstFrame = win.getFutureFlipTime(clock="now")
    frameN = -1

    # --- Run Routine "instrPractice" ---
    routineForceEnded = not continueRoutine
    while continueRoutine:

        t = routineTimer.getTime()
        tThisFlip = win.getFutureFlipTime(clock=routineTimer)
        tThisFlipGlobal = win.getFutureFlipTime(clock=None)
        frameN = frameN + 1

        if message.status == NOT_STARTED and tThisFlip >= 0.0 - frameTolerance:

            message.frameNStart = frameN
            message.tStart = t
            message.tStartRefresh = tThisFlipGlobal
            win.timeOnFlip(message, "tStartRefresh")

            thisExp.timestampOnFlip(win, "message.started")

            message.status = STARTED
            message.setAutoDraw(True)

        waitOnFlip = False

        if key_resp.status == NOT_STARTED and tThisFlip >= 0.0 - frameTolerance:

            key_resp.frameNStart = frameN
            key_resp.tStart = t
            key_resp.tStartRefresh = tThisFlipGlobal
            win.timeOnFlip(key_resp, "tStartRefresh")

            thisExp.timestampOnFlip(win, "key_resp.started")

            key_resp.status = STARTED

            waitOnFlip = True
            win.callOnFlip(key_resp.clock.reset)
            win.callOnFlip(key_resp.clearEvents, eventType="keyboard")
        if key_resp.status == STARTED and not waitOnFlip:
            theseKeys = key_resp.getKeys(
                keyList=["space"], ignoreKeys=["escape"], waitRelease=False
            )
            _key_resp_allKeys.extend(theseKeys)
            if len(_key_resp_allKeys):
                key_resp.keys = _key_resp_allKeys[-1].name
                key_resp.rt = _key_resp_allKeys[-1].rt
                key_resp.duration = _key_resp_allKeys[-1].duration

                continueRoutine = False

        if defaultKeyboard.getKeys(keyList=["escape"]):
            thisExp.status = FINISHED
        if thisExp.status == FINISHED or endExpNow:
            endExperiment(thisExp, win=win)
            return

        if not continueRoutine:
            routineForceEnded = True
            break
        continueRoutine = False
        for thisComponent in instrPracticeComponents:
            if hasattr(thisComponent, "status") and thisComponent.status != FINISHED:
                continueRoutine = True
                break

        if continueRoutine:
            win.flip()

    # --- Ending Routine "instrPractice" ---
    for thisComponent in instrPracticeComponents:
        if hasattr(thisComponent, "setAutoDraw"):
            thisComponent.setAutoDraw(False)
    thisExp.addData("instrPractice.stopped", globalClock.getTime())

    if key_resp.keys in ["", [], None]:
        key_resp.keys = None
    thisExp.addData("key_resp.keys", key_resp.keys)
    if key_resp.keys != None:
        thisExp.addData("key_resp.rt", key_resp.rt)
        thisExp.addData("key_resp.duration", key_resp.duration)
    thisExp.nextEntry()

    routineTimer.reset()

    blocks = data.TrialHandler(
        nReps=N_BLOCKS,
        method="sequential",
        extraInfo=expInfo,
        originPath=-1,
        trialList=[None],
        seed=None,
        name="blocks",
    )
    thisExp.addLoop(blocks)
    thisBlock = blocks.trialList[0]

    if thisBlock != None:
        for paramName in thisBlock:
            globals()[paramName] = thisBlock[paramName]

    for thisBlock in blocks:
        currentLoop = blocks
        thisExp.timestampOnFlip(win, "thisRow.t")

        if thisBlock != None:
            for paramName in thisBlock:
                globals()[paramName] = thisBlock[paramName]

        trials = data.TrialHandler(
            nReps=N_TRIALS,
            method="sequential",
            extraInfo=expInfo,
            originPath=-1,
            trialList=[None],
            seed=None,
            name="trials",
        )
        thisExp.addLoop(trials)
        thisTrial = trials.trialList[0]

        if thisTrial != None:
            for paramName in thisTrial:
                globals()[paramName] = thisTrial[paramName]

        for thisTrial in trials:
            currentLoop = trials
            thisExp.timestampOnFlip(win, "thisRow.t")

            if thisTrial != None:
                for paramName in thisTrial:
                    globals()[paramName] = thisTrial[paramName]

            # --- Prepare to start Routine "trial" ---
            continueRoutine = True

            thisExp.addData("trial.started", globalClock.getTime())

            trialComponents = [stimuli, target_notice, rest]
            for thisComponent in trialComponents:
                thisComponent.tStart = None
                thisComponent.tStop = None
                thisComponent.tStartRefresh = None
                thisComponent.tStopRefresh = None
                if hasattr(thisComponent, "status"):
                    thisComponent.status = NOT_STARTED

            t = 0
            _timeToFirstFrame = win.getFutureFlipTime(clock="now")
            frameN = -1

            frame_rate = round(expInfo["frameRate"])
            flicker_freq = FLICKER_FREQ
            frames_per_cycle = frame_rate // flicker_freq
            visible_frames = frames_per_cycle // 2
            not_visible_frames = frames_per_cycle - visible_frames

            flicker_frame_count = 0
            is_visible = False

            # --- Run Routine "trial" ---
            routineForceEnded = not continueRoutine
            while continueRoutine and routineTimer.getTime() < 10.0:

                t = routineTimer.getTime()
                tThisFlip = win.getFutureFlipTime(clock=routineTimer)
                tThisFlipGlobal = win.getFutureFlipTime(clock=None)
                frameN = frameN + 1

                if stimuli.status == NOT_STARTED and tThisFlip >= TMAX - frameTolerance:

                    stimuli.frameNStart = frameN
                    stimuli.tStart = t
                    stimuli.tStartRefresh = tThisFlipGlobal
                    win.timeOnFlip(stimuli, "tStartRefresh")

                    thisExp.timestampOnFlip(win, "stimuli.started")
                    stimuli.status = STARTED
                    flicker_frame_count = 0
                    model.logger.info(f"Stimulus started at {t}, frame {frameN}")
                    model.annotate("target")

                if stimuli.status == STARTED:
                    new_visibility = flicker_frame_count < visible_frames
                    if new_visibility != is_visible:
                        is_visible = new_visibility
                        state = "visible" if is_visible else "not visible"
                        model.logger.info(
                            f"Stimulus became {state} at frame {frameN}, time {t}"
                        )

                    if is_visible:
                        stimuli.draw()

                    if tThisFlipGlobal > stimuli.tStartRefresh + TMAX - frameTolerance:

                        stimuli.tStop = t
                        stimuli.frameNStop = frameN
                        thisExp.timestampOnFlip(win, "stimuli.stopped")
                        stimuli.status = FINISHED
                        model.logger.info(f"Stimulus stopped at {t}, frame {frameN}")

                    flicker_frame_count = (flicker_frame_count + 1) % frames_per_cycle

                win.flip()

                if (
                    target_notice.status == NOT_STARTED
                    and tThisFlip >= 0.0 - frameTolerance
                ):

                    target_notice.frameNStart = frameN
                    target_notice.tStart = t
                    target_notice.tStartRefresh = tThisFlipGlobal
                    win.timeOnFlip(target_notice, "tStartRefresh")

                    thisExp.timestampOnFlip(win, "target_notice.started")

                    target_notice.status = STARTED
                    target_notice.setAutoDraw(True)

                if target_notice.status == STARTED:

                    if (
                        tThisFlipGlobal
                        > target_notice.tStartRefresh + 4 - frameTolerance
                    ):

                        target_notice.tStop = t
                        target_notice.frameNStop = frameN

                        thisExp.timestampOnFlip(win, "target_notice.stopped")

                        target_notice.status = FINISHED
                        target_notice.setAutoDraw(False)

                if rest.status == NOT_STARTED and tThisFlip >= 8 - frameTolerance:

                    rest.frameNStart = frameN
                    rest.tStart = t
                    rest.tStartRefresh = tThisFlipGlobal
                    win.timeOnFlip(rest, "tStartRefresh")

                    thisExp.timestampOnFlip(win, "rest.started")

                    rest.status = STARTED
                    rest.setAutoDraw(True)

                if rest.status == STARTED:

                    if tThisFlipGlobal > rest.tStartRefresh + 2 - frameTolerance:

                        rest.tStop = t
                        rest.frameNStop = frameN

                        thisExp.timestampOnFlip(win, "rest.stopped")

                        rest.status = FINISHED
                        rest.setAutoDraw(False)

                if defaultKeyboard.getKeys(keyList=["escape"]):
                    thisExp.status = FINISHED
                if thisExp.status == FINISHED or endExpNow:
                    endExperiment(thisExp, win=win)
                    return

                if not continueRoutine:
                    routineForceEnded = True
                    break
                continueRoutine = False
                for thisComponent in trialComponents:
                    if (
                        hasattr(thisComponent, "status")
                        and thisComponent.status != FINISHED
                    ):
                        continueRoutine = True
                        break

                if continueRoutine:
                    win.flip()

            # --- Ending Routine "trial" ---
            for thisComponent in trialComponents:
                if hasattr(thisComponent, "setAutoDraw"):
                    thisComponent.setAutoDraw(False)
            thisExp.addData("trial.stopped", globalClock.getTime())

            if routineForceEnded:
                routineTimer.reset()
            else:
                routineTimer.addTime(-10.000000)
            thisExp.nextEntry()

            if thisSession is not None:

                thisSession.sendExperimentData()

        # --- Prepare to start Routine "syncFeedback" ---
        continueRoutine = True

        thisExp.addData("syncFeedback.started", globalClock.getTime())
        key_resp_2.keys = []
        key_resp_2.rt = []
        _key_resp_2_allKeys = []

        syncFeedbackComponents = [text, key_resp_2]
        for thisComponent in syncFeedbackComponents:
            thisComponent.tStart = None
            thisComponent.tStop = None
            thisComponent.tStartRefresh = None
            thisComponent.tStopRefresh = None
            if hasattr(thisComponent, "status"):
                thisComponent.status = NOT_STARTED

        t = 0
        _timeToFirstFrame = win.getFutureFlipTime(clock="now")
        frameN = -1

        db = model.get_db()
        compute = Synchronization(
            database=db, model=model, duplicate=False
        )
        updated_res = compute.sync_results()

        text.text = (
            f"Brain synchronization value: {updated_res}\n\nPress space to continue"
        )

        # --- Run Routine "syncFeedback" ---
        routineForceEnded = not continueRoutine
        while continueRoutine:

            t = routineTimer.getTime()
            tThisFlip = win.getFutureFlipTime(clock=routineTimer)
            tThisFlipGlobal = win.getFutureFlipTime(clock=None)
            frameN = frameN + 1

            if text.status == NOT_STARTED and tThisFlip >= 0.0 - frameTolerance:

                text.frameNStart = frameN
                text.tStart = t
                text.tStartRefresh = tThisFlipGlobal
                win.timeOnFlip(text, "tStartRefresh")

                thisExp.timestampOnFlip(win, "text.started")

                text.status = STARTED
                text.setAutoDraw(True)

            waitOnFlip = False

            if key_resp_2.status == NOT_STARTED and tThisFlip >= 0.0 - frameTolerance:

                key_resp_2.frameNStart = frameN
                key_resp_2.tStart = t
                key_resp_2.tStartRefresh = tThisFlipGlobal
                win.timeOnFlip(key_resp_2, "tStartRefresh")

                thisExp.timestampOnFlip(win, "key_resp_2.started")

                key_resp_2.status = STARTED

                waitOnFlip = True
                win.callOnFlip(key_resp_2.clock.reset)
                win.callOnFlip(key_resp_2.clearEvents, eventType="keyboard")
            if key_resp_2.status == STARTED and not waitOnFlip:
                theseKeys = key_resp_2.getKeys(
                    keyList=["space"], ignoreKeys=["escape"], waitRelease=False
                )
                _key_resp_2_allKeys.extend(theseKeys)
                if len(_key_resp_2_allKeys):
                    key_resp_2.keys = _key_resp_2_allKeys[-1].name
                    key_resp_2.rt = _key_resp_2_allKeys[-1].rt
                    key_resp_2.duration = _key_resp_2_allKeys[-1].duration

                    continueRoutine = False

            if defaultKeyboard.getKeys(keyList=["escape"]):
                thisExp.status = FINISHED
            if thisExp.status == FINISHED or endExpNow:
                endExperiment(thisExp, win=win)
                return

            if not continueRoutine:
                routineForceEnded = True
                break
            continueRoutine = False
            for thisComponent in syncFeedbackComponents:
                if (
                    hasattr(thisComponent, "status")
                    and thisComponent.status != FINISHED
                ):
                    continueRoutine = True
                    break

            if continueRoutine:
                win.flip()

        # --- Ending Routine "syncFeedback" ---
        for thisComponent in syncFeedbackComponents:
            if hasattr(thisComponent, "setAutoDraw"):
                thisComponent.setAutoDraw(False)
        thisExp.addData("syncFeedback.stopped", globalClock.getTime())
        
        if key_resp_2.keys in ["", [], None]:
            key_resp_2.keys = None
        blocks.addData("key_resp_2.keys", key_resp_2.keys)
        if key_resp_2.keys != None:
            blocks.addData("key_resp_2.rt", key_resp_2.rt)
            blocks.addData("key_resp_2.duration", key_resp_2.duration)
        routineTimer.reset()
        thisExp.nextEntry()

        if thisSession is not None:
            thisSession.sendExperimentData()

    # --- Prepare to start Routine "thanks" ---
    continueRoutine = True
    
    thisExp.addData("thanks.started", globalClock.getTime())
    key_resp_3.keys = []
    key_resp_3.rt = []
    _key_resp_3_allKeys = []
    
    thanksComponents = [text_2, key_resp_3]
    for thisComponent in thanksComponents:
        thisComponent.tStart = None
        thisComponent.tStop = None
        thisComponent.tStartRefresh = None
        thisComponent.tStopRefresh = None
        if hasattr(thisComponent, "status"):
            thisComponent.status = NOT_STARTED

    t = 0
    _timeToFirstFrame = win.getFutureFlipTime(clock="now")
    frameN = -1

    # --- Run Routine "thanks" ---
    routineForceEnded = not continueRoutine
    while continueRoutine:
        
        t = routineTimer.getTime()
        tThisFlip = win.getFutureFlipTime(clock=routineTimer)
        tThisFlipGlobal = win.getFutureFlipTime(clock=None)
        frameN = frameN + 1

        if text_2.status == NOT_STARTED and tThisFlip >= 0.0 - frameTolerance:
            
            text_2.frameNStart = frameN
            text_2.tStart = t
            text_2.tStartRefresh = tThisFlipGlobal
            win.timeOnFlip(text_2, "tStartRefresh")
            
            thisExp.timestampOnFlip(win, "text_2.started")
            
            text_2.status = STARTED
            text_2.setAutoDraw(True)

        waitOnFlip = False

        if key_resp_3.status == NOT_STARTED and tThisFlip >= 0.0 - frameTolerance:
            
            key_resp_3.frameNStart = frameN
            key_resp_3.tStart = t
            key_resp_3.tStartRefresh = tThisFlipGlobal
            win.timeOnFlip(key_resp_3, "tStartRefresh")
            
            thisExp.timestampOnFlip(win, "key_resp_3.started")
            
            key_resp_3.status = STARTED
            
            waitOnFlip = True
            win.callOnFlip(key_resp_3.clock.reset)
            win.callOnFlip(
                key_resp_3.clearEvents, eventType="keyboard"
            )
        if key_resp_3.status == STARTED and not waitOnFlip:
            theseKeys = key_resp_3.getKeys(
                keyList=["q"], ignoreKeys=["escape"], waitRelease=False
            )
            _key_resp_3_allKeys.extend(theseKeys)
            if len(_key_resp_3_allKeys):
                key_resp_3.keys = _key_resp_3_allKeys[-1].name
                key_resp_3.rt = _key_resp_3_allKeys[-1].rt
                key_resp_3.duration = _key_resp_3_allKeys[-1].duration
                
                continueRoutine = False

        if defaultKeyboard.getKeys(keyList=["escape"]):
            thisExp.status = FINISHED
        if thisExp.status == FINISHED or endExpNow:
            endExperiment(thisExp, win=win)
            return

        if not continueRoutine:
            routineForceEnded = True
            break
        continueRoutine = (
            False
        )
        for thisComponent in thanksComponents:
            if hasattr(thisComponent, "status") and thisComponent.status != FINISHED:
                continueRoutine = True
                break

        if (
            continueRoutine
        ):
            win.flip()

    # --- Ending Routine "thanks" ---
    for thisComponent in thanksComponents:
        if hasattr(thisComponent, "setAutoDraw"):
            thisComponent.setAutoDraw(False)
    thisExp.addData("thanks.stopped", globalClock.getTime())

    if key_resp_3.keys in ["", [], None]:
        key_resp_3.keys = None
    thisExp.addData("key_resp_3.keys", key_resp_3.keys)
    if key_resp_3.keys != None:
        thisExp.addData("key_resp_3.rt", key_resp_3.rt)
        thisExp.addData("key_resp_3.duration", key_resp_3.duration)
    thisExp.nextEntry()
    routineTimer.reset()

    endExperiment(thisExp, win=win)


def saveData(thisExp: data.ExperimentHandler):
    """Save data from this experiment

    Args:
        thisExp (psychopy.data.ExperimentHandler): Handler object for this experiment, contains the data to save and information about where to save it to.
    """
    filename = thisExp.dataFileName
    thisExp.saveAsWideText(filename + ".csv", delim="auto")


def endExperiment(thisExp: data.ExperimentHandler, win: visual.Window = None):
    """End this experiment, performing final shut down operations.

    Args:
        thisExp (psychopy.data.ExperimentHandler): Handler object for this experiment, contains the data to save and information about where to save it to.
        win (psychopy.visual.Window): Window for this experiment.
    """
    if win is not None:
        win.clearAutoDraw()
        win.flip()

    thisExp.status = FINISHED


def quit(
    thisExp: data.ExperimentHandler,
    win: visual.Window = None,
    thisSession: session.Session = None,
):
    """Fully quit, closing the window and ending the Python process.

    Args:
        thisExp (psychopy.data.ExperimentHandler): Handler object for this experiment, contains the data to save and information about where to save it to.
        win (psychopy.visual.Window): Window to close.
        thisSession (psychopy.session.Session): Handle of the Session object this experiment is being run from, if any.
    """
    thisExp.abort()

    if win is not None:
        win.flip()
        win.close()

    if thisSession is not None:
        thisSession.stop()

    core.quit()
