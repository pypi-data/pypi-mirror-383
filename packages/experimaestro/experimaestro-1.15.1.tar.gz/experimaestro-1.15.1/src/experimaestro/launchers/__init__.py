from pathlib import Path, PosixPath
from typing import Callable, Dict, List, Optional
from experimaestro.commandline import AbstractCommand, Job, CommandLineJob
from experimaestro.connectors import Connector
from experimaestro.connectors.local import ProcessBuilder, LocalConnector
from experimaestro.connectors.ssh import SshPath, SshConnector
from abc import ABC, abstractmethod


class ScriptBuilder(ABC):
    """A script builder is responsible for generating the script
    used to launch a command line job"""

    lockfiles: List[Path]
    """The files that must be locked before starting the job"""

    command: "AbstractCommand"
    """Command to be run"""

    @abstractmethod
    def write(self, job: CommandLineJob) -> Path:
        """Write the commmand line job

        :params job: The job to be written
        """
        ...


SubmitListener = Callable[[Job], None]
"""Listen to job submissions"""


class Launcher(ABC):
    """A launcher"""

    submit_listeners: List[SubmitListener]

    def __init__(self, connector: Connector):
        self.connector = connector
        self.environ: Dict[str, str] = {}
        self.notificationURL: Optional[str] = None
        self.submit_listeners = []

    def setenv(self, key: str, value: str):
        self.environ[key] = value

    def setNotificationURL(self, url: Optional[str]):
        self.notificationURL = url

    @abstractmethod
    def scriptbuilder(self) -> ScriptBuilder:
        """Returns a script builder"""
        ...

    def addListener(self, listener: SubmitListener):
        self.submit_listeners.append(listener)

    def onSubmit(self, job: Job):
        """Called when submitting a job

        Example of use: this allows the launcher to add token dependencies
        """
        for listener in self.submit_listeners:
            listener(job)

    def processbuilder(self) -> ProcessBuilder:
        """Returns the process builder for this launcher

        By default, returns the associated connector builder"""
        return self.connector.processbuilder()

    @staticmethod
    def get(path: Path):
        """Get a default launcher for a given path"""
        if isinstance(path, PosixPath):
            from .direct import DirectLauncher

            return DirectLauncher(LocalConnector())

        if isinstance(path, SshPath):
            from .direct import DirectLauncher

            return DirectLauncher(SshConnector.fromPath(path))
        raise ValueError("Cannot create a default launcher for %s", type(path))
