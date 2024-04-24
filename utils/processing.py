from mne import Epochs
from mne.preprocessing import ICA, EOGRegression

from config import TMIN, TMAX, CHANNELS_LIST, EVENT_DICT


class Processing:
    def __init__(self, raw, events, mode=None):
        self.raw = raw
        self.events = events

        if mode.lower() == "ica":
            self.ICA()
        elif mode.lower() == "lr":
            self.LR()
        elif mode.lower() == "bilstm":
            self.BiLSTM()
        else:
            raise Exception("Invalid mode provided")

    def ICA(self):
        filt_raw = self.raw.copy().filter(l_freq=1, h_freq=40)

        ica = ICA(n_components=2, max_iter="auto", random_state=97)
        ica.fit(filt_raw)

        eog_indices, eog_scores = ica.find_bads_eog(self.raw)
        ica.exclude = eog_indices

        self.reconstructed = self.raw.copy()
        ica.apply(self.reconstructed)

        return

    def LR(self):

        self.raw.set_eeg_reference("average")
        self.raw.filter(1, 40)

        epochs = Epochs(
            self.raw,
            events=self.events,
            event_id=EVENT_DICT,
            tmin=TMIN,
            tmax=TMAX,
            baseline=None,
            preload=True,
            verbose=False,
            picks=CHANNELS_LIST,
        )

        model = EOGRegression(picks="eeg", picks_artifact="eog").fit(epochs)
        self.reconstructed = model.apply(self.raw)

        return

    def BiLSTM(self):

        self.reconstructed = self.raw

        return
