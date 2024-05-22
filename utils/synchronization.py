import mne
import pandas as pd
import numpy as np
import os

import scipy.signal as signal

from hypyp import analyses
from typing import Any
from itertools import combinations

from utils.processing import Processing
from model import Model
from config import (
    N_TRIALS,
    N_BLOCKS,
    CHANNELS_LIST,
    SAMPLING_FREQ,
    FREQ_BANDS,
    FLICKER_FREQ,
    TMIN,
    TMAX,
    RECORD,
    EXP_NAME,
    USERS,
    TRIAL_LEN,
    EVENT_DICT,
    DEV,
    PROCESSING_MODE,
)


class Synchronization:
    """Performs brain synchronization calculations"""

    def __init__(self, model: Model, database: tuple, cleaner: Processing) -> None:
        """Initializes synchronization calculation class

        Args:
            model (Model): Handles logging through BrainAccess Board API interface
            database (tuple): The experiment database
        """
        self._sync_value = -1

        self._db, self._db_status = database
        self._model = model

        self.init_params()
        self.get_user_devices()
        self.get_mne_from_db()

        self._current_epochs = []
        self._all_epochs = []

        self._all_concatenated_epochs = []
        self._concatenated_epochs = []

        self._cleaner = cleaner
        self.update_users()
        self.epoch_data()

        self._model.logger.info("Starting data processing process")

    def init_params(self) -> None:
        """Initializes synchronization parameters"""

        self._params: dict[str, Any] = {}
        self._params["channels_list"] = CHANNELS_LIST
        self._params["SR"] = SAMPLING_FREQ
        self._params["freq_bands"] = FREQ_BANDS
        self._params["tmin"] = TMIN
        self._params["tmax"] = TMAX
        self._params["users"] = USERS
        self._params["event_dict"] = EVENT_DICT
        self._params["dev"] = DEV
        self._params["cleaning_mode"] = PROCESSING_MODE

    def update_users(self) -> None:
        """Updates user names based on their devices"""
        for device in self._user_devices:
            if device not in USERS:
                username = f"user_{device}"
                USERS[device] = username

    def get_user_devices(self) -> None:
        """Returns user devices"""
        devices = self._db.separate_marker_devices()
        self._user_devices = list(devices["data"].keys())

    def get_mne_from_db(self) -> None:
        """Gets MNE data from experiment database"""
        if not self._db:
            return None

        self._mne_data = []

        for device in self._user_devices:
            self._mne_data.append({device: self._db.get_mne()[device]})

            if self._params["dev"]:
                # if only 1 device connected, duplicate
                self._mne_data.append({device: self._db.get_mne()[device]})

        if len(self._mne_data) == 0:
            self._model.logger.error("No MNE data found")

    def get_current_events(self, events: np.ndarray) -> np.ndarray:
        """Gets the events from the current block of trials

        Args:
            events (np.ndarray): The identity and timing of experimental events, around which the epochs were created.
        """
        current_events = events[-N_TRIALS:]

        return current_events

    def get_full_epochs(
        self,
        device: str,
        raw_data: mne.io.array.array.RawArray,
        events: np.ndarray,
        ev_id: dict,
    ) -> None:
        """Creates epochs for the whole experiment

        Args:
            device (str): User device name
            raw_data (mne.io.array.array.RawArray): User raw data
            events (np.ndarray): The identity and timing of experimental events, around which the epochs were created.
            ev_id (dict): Event dictionary
        """

        self._all_epochs.append(
            {
                device: mne.Epochs(
                    raw_data.filter(l_freq=1, h_freq=None, verbose=False),
                    events,
                    event_id=ev_id,
                    tmin=self._params["tmin"],
                    tmax=self._params["tmax"],
                    baseline=None,
                    preload=True,
                    verbose=False,
                    picks=self._params["channels_list"],
                    detrend=1,
                )
            }
        )

    def epoch_data(self) -> None:
        """Creates epochs from raw MNE data"""
        if len(self._mne_data) == 0:
            self._model.logger.error("No MNE data found")
            return None

        self._evs = []

        for raw_sub in self._mne_data:
            for device, raw_data in raw_sub.items():
                events, ev_id = mne.events_from_annotations(
                    raw_data, event_id=self._params["event_dict"], verbose=False
                )

                if events is not None:
                    current_events = self.get_current_events(events)

                    try:
                        processed_data = self._cleaner.clean(
                            raw=raw_data, mode=self._params["cleaning_mode"]
                        )
                        self._current_epochs.append(
                            {
                                device: mne.Epochs(
                                    processed_data,
                                    events=current_events,
                                    event_id=ev_id,
                                    tmin=self._params["tmin"],
                                    tmax=self._params["tmax"],
                                    baseline=None,
                                    preload=True,
                                    verbose=False,
                                    picks=self._params["channels_list"],
                                )
                            }
                        )

                    finally:
                        self.get_full_epochs(device, raw_data, events, ev_id)
                else:
                    self._model.logger.error("No events found")

        for epoch in self._current_epochs:
            self._concatenated_epochs.append(epoch)

        for epoch in self._all_epochs:
            self._all_concatenated_epochs.append(epoch)

        self._model.logger.info("Ending data processing process")

    def hilbert_tranform(self, data: np.ndarray) -> np.ndarray:
        """Computes analytic signal using Hilbert transform

        Args:
            data (np.ndarray): Data to compute analytic signal from

        Returns:
            complex_signal (np.ndarray): analytic signal for inter-personal brain sync calculations
        """

        assert (
            data[0].shape[0] == data[1].shape[0]
        ), "Two data streams should have the same number of trials."
        data = np.array(data)

        # Hilbert transform
        complex_signal = []

        data_array = np.array([data[participant] for participant in range(2)])
        hilb = signal.hilbert(data_array)
        complex_signal.append(hilb)

        complex_signal = np.moveaxis(np.array(complex_signal), [0], [3])

        return complex_signal

    def calculate_sync(self, epochs: mne.Epochs, parameter: str) -> float:
        """Calculates synchronization value

        Args:
            epochs (mne.Epochs): Epoched EEG data
            parameter (str): Synchronization parameter

        Returns:
            inter_sync (float): inter-personal brain sync value
        """
        self._model.logger.info("Starting synchronization calculation process")

        try:
            assert len(epochs[0]) == len(
                epochs[1]
            ), "Two data streams should have the same number of trials."
        except AssertionError:
            return None

        values = self.hilbert_tranform(data=np.array(epochs))
        result = analyses.compute_sync(values, parameter, epochs_average=True)

        inter_values = result[:, 0:2, 2:4]

        AM = np.mean(inter_values)
        GM = np.prod(inter_values) ** (1 / 4)

        inter_sync = np.round(((AM + GM) / 2), 2)

        self._model.logger.info("Ending synchronization calculation process")

        return inter_sync

    def sync_results(
        self,
        parameter: str = "coh",
        frequencies: dict = None,
        epochs: mne.Epochs = None,
    ) -> float:
        """Returns synchronization calculations and writes results to file

        Args:
            parameter (str): Synchronization parameter
            frequencies (dict): Frequency bands over which perform calculations
            epochs (mne.Epochs): Epoched MNE data
            trial (int): Trial number

        Returns:
            sync (float): brain synchronization value
        """
        epochs = self._concatenated_epochs if epochs is None else epochs
        frequencies = self._params["freq_bands"] if frequencies is None else frequencies

        df = pd.DataFrame(
            columns=[
                "stimulus_frequency",
                "trial_length",
                "n_trials_per_block",
                "n_blocks",
                "users",
                "channels",
                "sampling_frequency",
                "frequency_bands",
                "subjects",
                "parameter",
                "synchronization_value",
            ]
        )

        pairs = list(combinations(epochs, 2))
        for pair in pairs:
            sub1, sub2 = pair

            subjects = [key for key in sub1.keys()] + [key for key in sub2.keys()]

            try:
                subjects_data = [value["target"] for value in sub1.values()] + [
                    value["target"] for value in sub2.values()
                ]

                sync = self.calculate_sync(epochs=subjects_data, parameter=parameter)
                self._model.logger.info(f"Calculated synchronization value: {sync}")

                if RECORD:
                    self._model.logger.info("Writing results to file")
                    df.loc[len(df.index)] = [
                        FLICKER_FREQ,
                        TRIAL_LEN,
                        N_TRIALS,
                        N_BLOCKS,
                        self._params["users"],
                        CHANNELS_LIST,
                        SAMPLING_FREQ,
                        self._params["freq_bands"],
                        f"{self._params['users'][subjects[0]]} vs {self._params['users'][subjects[1]]}",
                        parameter,
                        sync,
                    ]
            except KeyError as e:
                self._model.logger.error(f"Error: {e}")
                continue

        if RECORD:
            self._model.logger.info("Exporting results' file")
            filename = f"../output/{EXP_NAME}.csv"

            if not os.path.isfile(filename):
                df.to_csv(filename, index=False)
            else:
                df.to_csv(filename, mode="a", header=False, index=False)

        return sync
