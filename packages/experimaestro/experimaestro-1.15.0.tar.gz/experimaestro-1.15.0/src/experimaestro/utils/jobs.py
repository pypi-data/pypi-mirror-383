import time
from threading import Condition
from tqdm.autonotebook import tqdm
from experimaestro.scheduler import JobState, Listener
from experimaestro import Config


def jobmonitor(*outputs: Config):
    """Follow the progress of a list of jobs (in order)"""

    cv = Condition()

    class LocalListener(Listener):
        def job_state(self, job):
            with cv:
                # Just notify when something happens
                cv.notify()

    listener = LocalListener()

    for output in outputs:
        try:
            job = None
            job = output.__xpm__.job
            lastprogress = 0
            while job.scheduler is None:
                time.sleep(0.1)

            job.scheduler.addlistener(listener)

            while job.state.notstarted():
                with cv:
                    cv.wait(timeout=5000)

            # Job already completed
            if job.state.value == JobState.DONE.value:
                print("Job already completed")  # noqa: T201
            else:
                with tqdm(total=100, unit_scale=True, unit="%") as reporter:
                    progress = 0
                    if not job.state.finished():
                        while not job.state.finished():
                            progress = 0
                            if len(job.progress) > 0 and job.progress[0] is not None:
                                progress = int(job.progress[0].progress * 100)
                                delta = progress - lastprogress
                            else:
                                delta = 0

                            if delta >= 0:
                                reporter.update(delta)
                                lastprogress = progress

                            # Wait for an event
                            with cv:
                                cv.wait(timeout=5000)

                    if job.state.value == JobState.DONE.value:
                        if progress < 100:
                            reporter.update(100 - progress)
                    else:
                        raise RuntimeError(
                            f"Job did not complete successfully ({job.state.name})."
                            f"Check the error log {job.stderr}"
                        )

        finally:
            if job is not None:
                job.scheduler.removelistener(listener)
