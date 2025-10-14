import time
from pathlib import Path
import sys
from typing import Callable
from experimaestro import Task, Meta, field, PathGenerator
import psutil
import logging
import subprocess
import json
import signal

from experimaestro.scheduler.workspace import RunMode
from experimaestro.tests.utils import TemporaryExperiment, is_posix
from experimaestro.scheduler import JobState
from . import restart_main


def terminate(p):
    p.terminate()


def sigint(p):
    p.send_signal(signal.SIGINT)


TERMINATES_FUNC = [terminate]
if is_posix():
    TERMINATES_FUNC.append(sigint)

MAX_RESTART_WAIT = 50  # 5 seconds


class Restart(Task):
    touch: Meta[Path] = field(default_factory=PathGenerator("touch"))
    wait: Meta[Path] = field(default_factory=PathGenerator("wait"))

    def execute(self):
        # Write the file "touch" to notify that we started
        with open(self.touch, "w") as out:
            out.write("hello")

        # Wait for the file "wait" before exiting
        while not self.wait.is_file():
            time.sleep(0.1)


def restart(terminate: Callable, experiment):
    """Check if a new experimaestro process is able to take back
    a running job

    1. Runs an experiment and kills it using "terminate" while keeping the job active
    2. Runs the same experiment
        2.1 Submit the same job
        2.2 Asserts that the job is running
        2.3 Signals to the job to end
        2.4 Asserts that the job is done

    Args:
        terminate (Callable): How to terminate the process (SIGINT / terminate)
        experiment ([type]): [description]
    """
    p = None
    xpmprocess = None
    try:
        with TemporaryExperiment("restart", maxwait=20) as xp:
            # Create the task with dry_run and so we can get the file paths
            task = Restart()
            task.submit(run_mode=RunMode.DRY_RUN)

        # Start the experiment with another process, and kill the job
        command = [
            sys.executable,
            restart_main.__file__,
            xp.workspace.path,
            experiment.__module__,
            experiment.__name__,
        ]

        logging.debug("Starting other process with: %s", command)
        xpmprocess = subprocess.Popen(command)

        counter = 0
        while not task.touch.is_file():
            time.sleep(0.1)
            counter += 1
            if counter >= MAX_RESTART_WAIT:
                terminate(xpmprocess)
                assert False, "Timeout waiting for task to be executed"

        jobinfo = json.loads(task.__xpm__.job.pidpath.read_text())
        pid = int(jobinfo["pid"])
        p = psutil.Process(pid)

        # Now, kills experimaestro
        logging.debug("Process has started [file %s, pid %d]", task.touch, pid)
        terminate(xpmprocess)
        errorcode = xpmprocess.wait(5)
        logging.debug("Process finishing with status %d", errorcode)

        # Check that task is still running
        logging.info("Checking that job (PID %s) is still running", pid)
        assert p.is_running()

        with TemporaryExperiment("restart", maxwait=20) as xp:
            # Now, submit the job - it should pick up the process
            # where it was left
            logging.debug("Submitting the job (continues the submit)")
            job = task.__xpm__.job
            scheduler = xp.current().scheduler

            assert scheduler.submit(job) is None

            while scheduler.getJobState(job).result() == JobState.READY:
                time.sleep(0.1)

            currentState = scheduler.getJobState(job).result()
            assert (
                currentState == JobState.RUNNING
            ), f"Job is not running (state is {currentState})"

            # Notify the task
            with task.wait.open("w") as fp:
                fp.write("done")

            assert job.finalState().result() == JobState.DONE
    finally:
        # Force kill
        if xpmprocess and xpmprocess.poll() is None:
            logging.warning("Forcing to quit process %s", xpmprocess.pid)
            xpmprocess.kill()

        if p and p.is_running():
            logging.warning("Forcing to quit process %s", p.pid)
            p.terminate()
