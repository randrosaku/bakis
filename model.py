import logging

from config import COMMAND

import baboard.utils.api as API
from baboard.utils.socket_client import BoardControl
from baboard.utils.options import get_utils_dict


class Model:
    def __init__(self, logger: logging.Logger):
        self.logger = logger
        self.device_names: list[str] = []
        self.marker_names: list[str] = []
        self.get_db()
        self.filename = get_utils_dict().current_save_file
        self.refresh_devices()

    def init_stimulation(self):
        # initialize stimulation
        self.stimulation = API.Stimulation(source_id="sync-video")
        self.stim_name = self.stimulation.info.source_id()
        self.stim_port = self.stimulation.outlet.get_info().uid()
        # connect stimulation to the board
        self.board_control = BoardControl(logger=self.logger)
        self.commands = self.board_control.get_commands()
        command = self.commands["connect_device"].copy()
        command["port"] = self.stim_port
        reply = self.board_control.command(command)
        if reply["command"] == "error":
            self.logger.error(reply["message"])
            while reply["command"] == "error":
                reply = self.board_control.command(command)

        command = self.commands["start_recording"].copy()
        command.update(COMMAND)

        self.board_control.command(command)
        self.logger.info(command["message"])
        # print(command["message"])

    def disconnect_stimulation(self):
        command = self.commands["disconnect_device"].copy()
        command["device_name"] = self.stim_name
        command["device_type"] = "lsl"
        command["port"] = self.stim_port
        command["callback"] = "dashboard"
        reply = self.board_control.command(command)
        if reply["command"] == "error":
            self.logger.error(reply["message"])

        command = self.commands["stop_recording"].copy()
        self.board_control.command(command)
        self.logger.info(command["message"])

    def refresh_devices(self):
        self.get_db()
        if not self.db:
            return
        devices = self.db.separate_marker_devices(only_lsl=True)
        self.device_names = list(devices["data"].keys())
        self.marker_names = list(devices["markers"].keys())

    def get_db(self):
        self.db, self.db_status = API.get_database()
        return self.db, self.db_status

    def annotate(self, msg):
        self.stimulation.annotate(msg)
