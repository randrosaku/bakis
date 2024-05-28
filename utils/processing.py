import mne
from mne.preprocessing import ICA
import asrpy

import tensorflow as tf
import numpy as np


class Processing:
    """Data processing model that cleans noisy EEG signal"""

    def __init__(self):
        """Initializes Processing class object"""
        return

    def clean(
        self, raw: mne.io.Raw, mode: str = None, events: np.array = None
    ) -> mne.io.Raw:
        """Starts cleaning method based on mode configuration. If None, raw noisy data is returned

        Args:
            raw (mne.io.Raw): raw noisy EEG data
            mode (str): cleaning mode
            events (np.array): current trial annotations

        Returns:
            self.reconstructed (mne.io.Raw): reconstructed, clean EEG signal
        """

        try:
            self.raw = raw.pick(["O1", "O2", "Fp1", "Fp2"])
        except ValueError:
            raise Exception("Channels 'O1', 'O2', 'Fp1', and 'Fp2' are expected.")

        self.raw.filter(1, 40, fir_design="firwin")
        # self.raw.resample(256)

        if mode.lower() == "ica":
            self.ICA()
        elif mode.lower() == "asr":
            self.ASR()
        elif mode.lower() == "bilstm":
            model = tf.keras.models.load_model("../RNN_model/models/b20-LRsch.keras")
            self.BiLSTM(model=model, events=events)
        else:
            return self.raw

        return self.reconstructed

    def ICA(self) -> None:
        """Uses independent component analysis (ICA) for artifact removal"""
        self.reconstructed = self.raw.copy()

        ica = ICA(
            n_components=len(self.raw.ch_names),
            max_iter="auto",
            method="picard",
            random_state=97,
        ).fit(self.reconstructed)

        eog_indices, _ = ica.find_bads_eog(
            self.reconstructed,
            ch_name=["Fp1", "Fp2"],
            threshold=0.7,
            measure="correlation",
        )
        ica.exclude = eog_indices
        ica.apply(self.reconstructed)

        return

    def ASR(self) -> None:
        """Uses artifact subspace reconstruction (ASR) for artifact removal"""

        processed_raw = self.raw.copy()

        asr = asrpy.ASR(sfreq=processed_raw.info["sfreq"], cutoff=15)
        asr.fit(processed_raw)
        self.reconstructed = asr.transform(processed_raw)

        return

    def BiLSTM(self, model: tf.keras.Model, events: np.array) -> None:
        """Uses Bidirectional LSTM (BiLSTM) recurrent neural network for artifact removal

        Args:
            model (tf.keras.Model): trained recurrent neural network model
        """

        tmin = events[0][0] / self.raw.info["sfreq"]
        tmax = None

        if len(events) > 1:
            tmax = events[-1][0] / self.raw.info["sfreq"]

        processed_raw = self.raw.copy()
        data = processed_raw.get_data()

        # Process input data
        std_devs = np.std(data, axis=1, keepdims=True)
        data_standardized = data / std_devs

        t = 2
        samples_per_segment = t * int(processed_raw.info["sfreq"])
        n_channels = data_standardized.shape[0]

        segments = []
        for channel in range(n_channels):
            channel_data = data_standardized[channel, :]
            n_segments = channel_data.shape[0] // samples_per_segment
            for segment in range(n_segments):
                start = segment * samples_per_segment
                end = start + samples_per_segment
                if end <= channel_data.shape[0]:
                    segments.append(
                        channel_data[start:end].reshape(samples_per_segment, 1)
                    )
        segments = np.array(segments)

        # Denoise data
        denoised_data = []
        for segment in segments:
            prediction = model.predict(
                segment[np.newaxis, :, :]
            )  # Model predicts on one segment at a time (2s EEG input)
            denoised_data.append(prediction.squeeze())
        denoised_data = np.array(denoised_data)

        # Initialize the denoised array with the correct shape
        denoised_full = np.zeros(data.shape)
        for channel in range(n_channels):
            channel_std_dev = std_devs[channel]
            n_segments = data[channel, :].shape[0] // samples_per_segment
            for segment in range(n_segments):
                start = segment * samples_per_segment
                end = start + samples_per_segment
                if end <= data[channel, :].shape[0]:
                    denoised_full[channel, start:end] = (
                        denoised_data[segment * n_channels + channel] * channel_std_dev
                    )

        info = mne.create_info(
            ch_names=processed_raw.info["ch_names"],
            sfreq=processed_raw.info["sfreq"],
            ch_types="eeg",
        )

        # Reconstruct signal to RAW
        self.reconstructed = mne.io.RawArray(denoised_full, info)

        return
