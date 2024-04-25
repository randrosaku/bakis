import mne
import pandas as pd
import numpy as np
import os

import scipy.signal as signal

from typing import Any
from hypyp import analyses

from itertools import combinations

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
)


class Synchronization:
    """Perform brain synchronization calculations"""

    def __init__(self, database, event_dict, duplicate=True):
        self._sync_value = -1

        self._db, self._db_status = database
        self._event_dict = event_dict
        self._duplicate = duplicate

        self.get_user_devices()
        self.get_mne_from_db()
        self.init_params()

        self._current_epochs = []
        self._all_epochs = []

        self._all_concatenated_epochs = []
        self._concatenated_epochs = []

        self.update_users()
        self.epoch_data()

        print("Brain synchronization calculations in progress >>> ")

    def init_params(self):
        """Synchronization parameters"""

        self._params: dict[str, Any] = {}
        self._params["channels_list"] = CHANNELS_LIST
        self._params["SR"] = SAMPLING_FREQ
        self._params["freq_bands"] = FREQ_BANDS
        self._params["tmin"] = TMIN
        self._params["tmax"] = TMAX
        self._params["users"] = USERS

    def update_users(self):
        for device in self._user_devices:
            if device not in USERS:
                username = f"user_{device}"
                # username = input(f"Enter the username for {device}: ")
                USERS[device] = username

    def get_user_devices(self):
        devices = self._db.separate_marker_devices()
        self._user_devices = list(devices["data"].keys())

    def get_mne_from_db(self):
        if not self._db:
            return None

        self._mne_data = []

        for device in self._user_devices:
            self._mne_data.append({device: self._db.get_mne()[device]})

            if self._duplicate == True:
                # if only 1 device connected, duplicate
                self._mne_data.append({device: self._db.get_mne()[device]})

        if len(self._mne_data) != 0:
            print("\n")
            # print({"mne_data": self._mne_data})
        else:
            print("No data found")

    def get_current_events(self, events):
        current_events = events[-N_TRIALS:]

        return current_events

    def get_full_epochs(self, device, raw_data, events, ev_id):
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

    def epoch_data(self):
        if len(self._mne_data) == 0:
            return None

        self._evs = []

        for raw_sub in self._mne_data:
            for device, raw_data in raw_sub.items():
                events, ev_id = mne.events_from_annotations(
                    raw_data, event_id=self._event_dict, verbose=False
                )

                if events is not None:
                    current_events = self.get_current_events(events)

                    try:
                        self._current_epochs.append(
                            {
                                device: mne.Epochs(
                                    raw_data.filter(
                                        l_freq=1, h_freq=None, verbose=False
                                    ),
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

                    except ValueError:
                        for key, value in ev_id.items():
                            try:
                                self._current_epochs.append(
                                    {
                                        device: mne.Epochs(
                                            raw_data.filter(
                                                l_freq=1, h_freq=40, verbose=False
                                            ),
                                            events=current_events,
                                            event_id={key: value},
                                            tmin=self._params["tmin"],
                                            tmax=self._params["tmax"],
                                            baseline=None,
                                            preload=True,
                                            verbose=False,
                                            picks=self._params["channels_list"],
                                        )
                                    }
                                )
                            except Exception as e:
                                continue
                    finally:
                        self.get_full_epochs(device, raw_data, events, ev_id)
                else:
                    print("No events found")

        for epoch in self._current_epochs:
            self._concatenated_epochs.append(epoch)

        for epoch in self._all_epochs:
            self._all_concatenated_epochs.append(epoch)

        return self._concatenated_epochs

    def _multiply_conjugate(
        self, real: np.ndarray, imag: np.ndarray, transpose_axes: tuple
    ) -> np.ndarray:
        formula = "jilm,jimk->jilk"
        product = (
            np.einsum(formula, real, real.transpose(transpose_axes))
            + np.einsum(formula, imag, imag.transpose(transpose_axes))
            - 1j
            * (
                np.einsum(formula, real, imag.transpose(transpose_axes))
                - np.einsum(formula, imag, real.transpose(transpose_axes))
            )
        )

        return product

    def compute_sync(
        self, complex_signal: np.ndarray, epochs_average: bool = True
    ) -> np.ndarray:

        n_epoch, n_ch, n_freq, n_samp = (
            complex_signal.shape[1],
            complex_signal.shape[2],
            complex_signal.shape[3],
            complex_signal.shape[4],
        )

        # calculate all epochs at once, the only downside is that the disk may not have enough space
        complex_signal = complex_signal.transpose((1, 3, 0, 2, 4)).reshape(
            n_epoch, n_freq, 2 * n_ch, n_samp
        )
        transpose_axes = (0, 1, 3, 2)

        c = np.real(complex_signal)
        s = np.imag(complex_signal)
        amp = np.abs(complex_signal) ** 2
        dphi = self._multiply_conjugate(c, s, transpose_axes=transpose_axes)
        con = np.abs(dphi) / np.sqrt(
            np.einsum("nil,nik->nilk", np.nansum(amp, axis=3), np.nansum(amp, axis=3))
        )

        con = con.swapaxes(0, 1)  # n_freq x n_epoch x 2*n_ch x 2*n_ch
        if epochs_average:
            con = np.nanmean(con, axis=1)

        return con

    def hilbert_tranform(self, data: np.ndarray):

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

    def calculate_sync(self, epochs):
        try:
            assert len(epochs[0]) == len(
                epochs[1]
            ), "Two data streams should have the same number of trials."
        except AssertionError:
            return None

        values = self.hilbert_tranform(data=np.array(epochs))
        result = self.compute_sync(values, epochs_average=True)

        inter_values = result[:, 0:2, 2:4]

        AM = np.mean(inter_values)
        GM = np.prod(inter_values) ** (1 / 4)

        inter_sync = np.round(((AM + GM) / 2), 2)

        return inter_sync

    def sync_results(self, parameter="coh", frequencies=None, epochs=None, trial=-1):
        epochs = self._concatenated_epochs if epochs is None else epochs
        frequencies = self._params["freq_bands"] if frequencies is None else frequencies

        df = pd.DataFrame(
            columns=[
                "Stimulus frequency",
                "Trial length",
                "Num of trials per block",
                "Num of blocks",
                "Users",
                "Channels",
                "Sampling frequency",
                "Frequency bands",
                "Subjects",
                "Trial no",
                "Parameter",
                "Synchronization",
                "Standard deviation",
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

                sync = self.calculate_sync(epochs=subjects_data)
                print(f"\nSynchronization value: {sync}\n")

                if RECORD:
                    print(">>> Writing results to file\n")
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
                        trial,
                        parameter,
                        sync,
                    ]
            except KeyError as e:
                print(f"Error: {e}")
                continue

        if RECORD:
            print(">>> Saving file\n")
            filename = f"output/{EXP_NAME}.csv"
            # df.to_csv(filename, index=False)
            if not os.path.isfile(filename):
                df.to_csv(filename, index=False)
            else:
                df.to_csv(filename, mode="a", header=False, index=False)

        return sync
