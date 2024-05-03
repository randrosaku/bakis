import logging

from config import COMMAND

import baboard.utils.api as API
from baboard.utils.socket_client import BoardControl
from baboard.utils.options import get_utils_dict


class Model:
    """
    Model class handles the interaction with stimulation devices and recording management
    using the BoardControl interface.
    """

    def __init__(self, logger: logging.Logger):
        """Initializes the Model class with a logger and setups up the initial device configurations.

        Args:
            logger (logging.Logger): The logger object for logging information, errors, etc.
        """
        self.logger = logger
        self.device_names: list[str] = []
        self.marker_names: list[str] = []
        self.get_db()
        self.filename = get_utils_dict().current_save_file

    def init_stimulation(self):
        """Initializes and starts stimulation along with device connection and recording."""
        self.stimulation = API.Stimulation(source_id="sync-stimulus")
        self.stim_name = self.stimulation.info.source_id()
        self.stim_port = self.stimulation.outlet.get_info().uid()

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

    def disconnect_stimulation(self):
        """Disconnects the stimulation device and stops recording."""
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

    def get_db(self):
        """Retrieves the current database configuration.

        Returns:
            tuple: Database object and its connection status.
        """
        self.db, self.db_status = API.get_database()
        return self.db, self.db_status

    def annotate(self, msg: str):
        """Annotates the current stimulation with a message.

        Args:
            msg (str): The annotation message to add.
        """
        self.stimulation.annotate(msg)
