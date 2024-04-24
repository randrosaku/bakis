import mne
import pandas as pd
import numpy as np
import os

from typing import Any
from hypyp import analyses

from config import (
    CHANNELS_LIST,
    SAMPLING_FREQ,
    FREQ_BANDS,
    TMIN,
    TMAX,
    BASELINE,
    RECORD,
    EXP_NAME,
    USERS,
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
        print("Event dictionary: ", self._event_dict)

    def init_params(self):
        """Synchronization parameters"""

        self._params: dict[str, Any] = {}
        self._params["channels_list"] = CHANNELS_LIST
        self._params["SR"] = SAMPLING_FREQ
        self._params["freq_bands"] = FREQ_BANDS
        self._params["tmin"] = TMIN
        self._params["tmax"] = TMAX
        self._params["baseline"] = BASELINE
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
            print({"mne_data": self._mne_data})
        else:
            print("No data found")

    def get_current_events(self, events):
        current_events = events[-TRIALS_PER_BLOCK:]

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
                    baseline=self._params["baseline"],
                    preload=True,
                    verbose=False,
                    picks=self._params["channels_list"],
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
                                    baseline=self._params["baseline"],
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
                                            baseline=self._params["baseline"],
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

    def res(self, m):
        l_00 = []
        l_01 = []
        l_10 = []
        l_11 = []

        m = m[0]
        for i in range(len(m)):
            l_00.append(m[i][0][0])
            l_01.append(m[i][0][1])
            l_10.append(m[i][1][0])
            l_11.append(m[i][1][1])

        return l_00, l_01, l_10, l_11

    def calculate_sync(self, parameter, frequencies, epochs):
        # print(epochs)
        try:
            assert len(epochs[0]) == len(epochs[1]), "Mismatched epochs"
        except AssertionError:
            return None, None

        connectivity_matrix = analyses.pair_connectivity(
            data=np.array(epochs),
            sampling_rate=self._params["SR"],
            frequencies=frequencies,
            mode=parameter,
            epochs_average=False,
        )

        sync_mat = connectivity_matrix[:, :, 0:2, 2:4]
        sync_list = self._res(sync_mat)

        sync = np.round(np.mean(sync_list[0]), 2)
        sync_std = np.round(np.std(sync_list[0]), 2)

        return sync, sync_std

    def sync_results(self, parameter, frequencies=None, epochs=None, trial=-1):
        epochs = self._concatenated_epochs if epochs is None else epochs
        frequencies = self._params["freq_bands"] if frequencies is None else frequencies

        df = pd.DataFrame(
            columns=[
                "Frequency rates",
                "Trial length",
                "Num of trials per block",
                "Num of blocks",
                "Users",
                "Channels",
                "Sampling frequency",
                "Calculations for",
                "Frequency bands",
                "Subjects",
                "Trial no",
                "Parameter",
                "Synchronization",
                "Standard deviation",
            ]
        )

        print("\nBrain synchronization experiment results\n")

        pairs = list(combinations(epochs, 2))
        for pair in pairs:
            sub1, sub2 = pair

            subjects = [key for key in sub1.keys()] + [key for key in sub2.keys()]

            for band in self._params["freq_bands"]:
                try:
                    subjects_data = [value[band] for value in sub1.values()] + [
                        value[band] for value in sub2.values()
                    ]

                    sync, std = self._calculate_sync(
                        parameter=parameter,
                        frequencies=self._params["freq_bands"][band],
                        epochs=subjects_data,
                    )
                    # print(
                    #     f"{self._params['users'][subjects[0]]} vs {self._params['users'][subjects[1]]} calculations for {band}: {sync} +- {std}"
                    # )

                    if RECORD:
                        print(">>> Writing results to file\n")
                        df.loc[len(df.index)] = [
                            FREQ_RATES,
                            TRIAL_LEN,
                            TRIALS_PER_BLOCK,
                            N_BLOCKS,
                            self._params["users"],
                            CHANNELS_LIST,
                            SAMPLING_FREQ,
                            band,
                            self._params["freq_bands"][band],
                            f"{self._params['users'][subjects[0]]} vs {self._params['users'][subjects[1]]}",
                            trial,
                            parameter,
                            sync,
                            std,
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
