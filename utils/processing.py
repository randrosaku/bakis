from mne import Epochs
from mne.preprocessing import ICA, EOGRegression
import asrpy

from config import TMIN, TMAX, CHANNELS_LIST, EVENT_DICT


class Processing:
    """ """

    def __init__(self, raw, mode):
        """ """
        self.raw = raw
        self.events = events

        if mode.lower() == "ica":
            self.ICA()
        elif mode.lower() == "asr":
            self.ASR()
        elif mode.lower() == "bilstm":
            self.BiLSTM()
        else:
            raise Exception("Invalid mode provided")

    def ICA(self):
        """Uses independent component analysis (ICA) for artifact removal"""
        filt_raw = self.raw.copy().filter(l_freq=1, h_freq=40)

        ica = ICA(n_components=len(self.raw.ch_names), max_iter="auto", random_state=97)
        ica.fit(filt_raw)

        eog_indices, eog_scores = ica.find_bads_eog(self.raw)
        ica.exclude = eog_indices

        self.reconstructed = self.raw.copy()
        ica.apply(self.reconstructed)

        return

    def ASR(self):
        """Uses artifact subspace reconstruction (ASR) for artifact removal"""

        processed_raw = self.raw.copy()

        asr = asrpy.ASR(sfreq=processed_raw.info["sfreq"], cutoff=20)
        asr.fit(processed_raw)
        self.reconstructed = asr.transform(processed_raw)

        return

    def BiLSTM(self):
        """Uses Bidirectional LSTM (BiLSTM) recurrent neural network for artifact removal"""

        self.reconstructed = self.raw

        return
