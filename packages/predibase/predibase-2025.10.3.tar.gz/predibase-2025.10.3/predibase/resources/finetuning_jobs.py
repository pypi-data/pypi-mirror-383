from __future__ import annotations

import datetime
import json
import os
import pathlib
import sys
import tempfile
import time
import urllib.request
from threading import Event, Thread
from typing import Any, TYPE_CHECKING

from dateutil import parser
from progress_table import ProgressTable
from tqdm import tqdm

from predibase._errors import PredibaseResponseError, PredibaseServerError
from predibase.config import FinetuningConfig, get_task_type, TrainingComputeSpec
from predibase.resources.dataset import Dataset
from predibase.resources.finetuning_job import _FinetuningMetrics, _GRPOTrainRewards, FinetuningJob
from predibase.resources.repo import Repo

if TYPE_CHECKING:
    from predibase import Predibase


class FinetuningJobs:
    def __init__(self, client: Predibase):
        self._client = client

    def create(
        self,
        *,
        config: FinetuningConfig | dict[str, Any],
        dataset: str | Dataset,
        continue_from_version: str | None = None,
        repo: str | Repo,
        compute_spec: TrainingComputeSpec | dict[str, Any] | None = None,
        description: str | None = None,
        watch: bool = False,
        show_tensorboard: bool = False,
    ) -> FinetuningJob:

        if show_tensorboard and not watch:
            raise RuntimeError("`show_tensorboard` is a blocking option and thus requires `watch` to be True.")

        if isinstance(config, FinetuningConfig):
            config = config.model_dump(exclude_none=True, by_alias=True)

        if isinstance(dataset, Dataset):
            dataset = dataset.name  # TODO: eventually accept connection type

        if isinstance(compute_spec, TrainingComputeSpec):
            compute_spec = compute_spec.model_dump(
                exclude_none=True,
                by_alias=True,
            )

        if isinstance(repo, Repo):
            repo = repo.name

        if config.get("epochs", None) and config.get("train_steps", None):
            print("Warning: `epochs` parameter will be ignored since `train_steps` is set.")

        try:
            self.estimate_cost(config=config, dataset=dataset)
        except RuntimeError:
            print("Could not estimate finetuning job cost/running time. Skipping estimates.")

        job_resp = self._client.http_post(
            "/v2/finetuning/jobs",
            json={
                "params": config,
                "dataset": dataset,
                "continueFromVersion": continue_from_version,
                "repo": repo,
                "description": description,
                "computeSpec": compute_spec,
            },
        )
        job = FinetuningJob.model_validate(job_resp)

        print(
            f"Successfully requested finetuning of {job.base_model} from "
            f"{'base' if continue_from_version is None else continue_from_version} as `{job.target_repo}/"
            f"{job.target_version_tag}`. (Job UUID: {job.uuid}).\n",
        )

        return self.watch(job, show_tensorboard) if watch else job

    def watch(self, job_ref: str | FinetuningJob, show_tensorboard: bool = False) -> FinetuningJob:
        if isinstance(job_ref, FinetuningJob):
            job_ref = job_ref.uuid

        print(
            f"Watching progress of finetuning job {job_ref}. This call will block until the job has finished. "
            f"Canceling or terminating this call will NOT cancel or terminate the job itself.\n",
        )

        queued_pbar = None
        tensorboard_event = Event()
        job = None

        # Wait for job to move to the training phase.
        while True:
            try:
                job_resp = self._client.http_get(f"/v2/finetuning/jobs/{job_ref}")
                job = FinetuningJob.model_validate(job_resp)

                # TODO: clean this up
                timeline_resp = self._client.http_get(f"/v2/finetuning/jobs/{job_ref}/timeline")

                # TODO: should an exception be raised in case of failure? Probably not?
                if job.status in ("completed", "canceled", "errored", "stopped", "stopping"):
                    # TODO: print last metrics?
                    print(f"Job {job_ref} is already {job.status}. Nothing to watch.")
                    return job

                if job.status == "queued":
                    msg = f"Job is queued for execution. Time in queue: {_get_elapsed(job.status, timeline_resp)}"
                    if queued_pbar is None:
                        queued_pbar = tqdm(
                            None,
                            bar_format=msg,
                            desc=job.status.capitalize(),
                            ncols=0,
                            file=sys.stdout,
                        )
                    elif not queued_pbar.disable:
                        queued_pbar.bar_format = msg
                        queued_pbar.refresh()
                        queued_pbar.update()

                if job.status == "training":
                    if queued_pbar is not None:
                        queued_pbar.bar_format = (
                            f"Job is starting. Total queue time: {_get_elapsed('queued', timeline_resp)}"
                        )
                        queued_pbar.close()
                    break

            except (PredibaseServerError, PredibaseResponseError) as e:
                if os.getenv("PREDIBASE_DEBUG") != "":
                    print(f"Continuing past error {e}")
                continue

            time.sleep(1)

        # Optionally launch tensorboard and a thread to sync TB logs.
        if show_tensorboard:
            self._run_tensorboard(job_ref, tensorboard_event)

        # Stream metrics during training phase.
        print("Waiting to receive training metrics...\n")
        task_type = get_task_type(job.params)
        if task_type == "grpo":
            self._stream_grpo_metrics(job_ref, _get_metrics_table(task_type), 10)
        else:
            self._stream_model_metrics(job_ref, _get_metrics_table(task_type), 10)

        # Fetch the final job state after streaming ends.
        while True:
            job_resp = self._client.http_get(f"/v2/finetuning/jobs/{job_ref}")
            job = FinetuningJob.model_validate(job_resp)

            if job.status in ("completed", "canceled", "errored", "stopped", "stopping"):
                if tensorboard_event:
                    tensorboard_event.set()

                return job

            time.sleep(1)

    def estimate_cost(
        self,
        *,
        config: FinetuningConfig | dict[str, Any],
        dataset: str | Dataset,
    ):
        if isinstance(config, FinetuningConfig):
            config = config.model_dump(exclude_none=True, by_alias=True)

        if isinstance(dataset, Dataset):
            dataset = f"{dataset.connection_name}/{dataset.name}"

        response = self._client.http_get(
            "/v2/finetuning/jobs/cost-estimate",
            json={
                "baseModel": config.get("base_model"),
                "datasetName": dataset,
                "taskType": config.get("task"),
                "adapterType": config.get("adapter"),
                "epochs": config.get("epochs"),
                "trainSteps": config.get("train_steps"),
                "numGenerations": config.get("num_generations"),
                "maxTokens": config.get("sampling_params", {}).get("max_tokens"),
            },
        )

        estimated_cost = response.get("estimatedCost", -1)
        if estimated_cost > 0:
            print(f"Estimated cost: ${estimated_cost:.2f}")

    def _run_tensorboard(self, job_uuid: str, stop_event: Event):
        import tensorboard.notebook

        # tb_logs_resp = self._client.http_get(f"/v2/finetuning/jobs/{job_uuid}/tensorboard_logs")
        # if not tb_logs_resp.get("files", []) and not tb_logs_resp.get("more", False):
        #     print(
        #         f"Finetuning job {job_uuid} does not have logs available, "
        #         f"which is likely because the model failed or "
        #         f"was terminated before logs were created.",
        #     )
        #     return

        with tempfile.TemporaryDirectory() as tmpdir:

            def _sync_tb_logfiles():
                while True:
                    tb_logs_resp = self._client.http_get(f"/v2/finetuning/jobs/{job_uuid}/tensorboard_logs")
                    files = tb_logs_resp.get("files", [])
                    should_continue = tb_logs_resp.get("more", False)

                    for f in files:
                        dst = os.path.join(tmpdir, job_uuid, f["filepath"])
                        pathlib.Path(os.path.dirname(dst)).mkdir(parents=True, exist_ok=True)
                        try:
                            urllib.request.urlretrieve(f["url"], dst)
                        except Exception:
                            # TODO: is there a way to safely print errors without breaking the progress table?
                            pass

                    if not should_continue or stop_event.is_set():
                        break

                    time.sleep(30)

            sync_thread = Thread(target=_sync_tb_logfiles, daemon=True)
            sync_thread.start()

            tensorboard.notebook.start(f"--logdir={os.path.join(tmpdir, job_uuid)}")

    def _stream_grpo_metrics(
        self,
        job_uuid: str,
        table: ProgressTable,
        max_attempts: int = 10,
    ):
        def print_progress_bar(metrics: _FinetuningMetrics):
            if metrics.meta.steps and metrics.meta.steps > 0 and metrics.meta.total_steps > 0:
                table.progress_bar_active = True
                table._print_progress_bar(
                    metrics.meta.steps,
                    metrics.meta.total_steps,
                    show_before=f" {metrics.meta.steps}/{metrics.meta.total_steps} steps ",
                )

        # Used to avoid re-printing rows if we need to reconnect, since the server sends historical data for each new
        # connection.
        # last_seen_checkpoint = 0
        last_seen_step = 0

        for resp in self._client.listen_websocket(
            f"/v2/finetuning/jobs/{job_uuid}/metrics/stream",
            max_attempts=max_attempts,
        ):
            try:
                if not table.header_printed:
                    table._print_header(top=True)

                metrics: _FinetuningMetrics = _FinetuningMetrics.model_validate(json.loads(resp))

                if metrics.data.steps and metrics.data.steps > last_seen_step:
                    # We've hit a step we haven't seen before, update the table.
                    table["step"] = metrics.data.steps
                    table["total_reward"] = "--"
                    table["total_reward_std"] = "--"

                    grpo_rewards_data: _GRPOTrainRewards | None = metrics.data.grpo_train_rewards
                    if not grpo_rewards_data:
                        table.next_row(split=True)
                        continue

                    table["total_reward"] = (
                        grpo_rewards_data.total_reward if grpo_rewards_data.total_reward is not None else "--"
                    )
                    table["total_reward_std"] = (
                        grpo_rewards_data.total_reward_std if grpo_rewards_data.total_reward_std is not None else "--"
                    )

                    for reward_fn, reward in grpo_rewards_data.model_extra.items():
                        table["reward_fn"] = reward_fn
                        table["reward"] = reward
                        table.next_row(split=False)

                    # Update last seen checkpoint
                    last_seen_step = metrics.data.steps
                    table.next_row(split=True)

                # print_progress_bar(metrics)

                if metrics.meta.is_completed:
                    table.close()
                    return

            # TODO: Handle specific error types
            except Exception as e:
                print(e)
                continue

    def _stream_model_metrics(
        self,
        job_uuid: str,
        table: ProgressTable,
        max_attempts: int = 10,
    ):
        def print_progress_bar(metrics: _FinetuningMetrics):
            if metrics.meta.steps and metrics.meta.steps > 0 and metrics.meta.total_steps > 0:
                table.progress_bar_active = True
                table._print_progress_bar(
                    metrics.meta.steps,
                    metrics.meta.total_steps,
                    show_before=f" {metrics.meta.steps}/{metrics.meta.total_steps} steps ",
                )

        # Used to avoid re-printing rows if we need to reconnect, since the server sends historical data for each new
        # connection.
        last_seen_checkpoint = 0

        for resp in self._client.listen_websocket(
            f"/v2/finetuning/jobs/{job_uuid}/metrics/stream",
            max_attempts=max_attempts,
        ):
            try:
                if not table.header_printed:
                    table._print_header(top=True)

                metrics = _FinetuningMetrics.model_validate(json.loads(resp))

                if (
                    metrics.data.steps
                    and metrics.data.steps > 0
                    and metrics.data.checkpoint_number > last_seen_checkpoint
                ):
                    # We've hit an evaluation step / checkpoint. Print a new row entry.
                    table["checkpoint"] = metrics.data.checkpoint_number
                    table["train_loss"] = metrics.data.train_metrics_loss
                    table["validation_loss"] = (
                        metrics.data.validation_metrics_loss if (metrics.data.validation_metrics_loss) else "--"
                    )

                    # Handle classification accuracy metrics.
                    # Check for None since we should still print out if the accuracy is 0.
                    table["train_accuracy"] = (
                        metrics.data.train_metrics_accuracy if metrics.data.train_metrics_accuracy is not None else "--"
                    )
                    table["validation_accuracy"] = (
                        metrics.data.validation_metrics_accuracy
                        if metrics.data.validation_metrics_accuracy is not None
                        else "--"
                    )
                    table.next_row()

                    # Update last seen checkpoint
                    last_seen_checkpoint = metrics.data.checkpoint_number

                print_progress_bar(metrics)

                if metrics.meta.is_completed:
                    table.close()
                    return

            # TODO: Handle specific error types
            except Exception:
                continue

    def get(self, job: str | FinetuningJob) -> FinetuningJob:
        if isinstance(job, FinetuningJob):
            job = job.uuid

        job = self._client.http_get(f"/v2/finetuning/jobs/{job}")
        return FinetuningJob.model_validate(job)

    def cancel(self, job: str | dict):
        if isinstance(job, dict):
            job = job["uuid"]

        self._client.http_post(f"/v2/finetuning/jobs/{job}/cancel")

    def update(self, job_ref: str | FinetuningJob, new_config: FinetuningConfig):
        if isinstance(job_ref, FinetuningJob):
            job_ref = job_ref.uuid

        self._client.http_put(f"/v2/finetuning/jobs/{job_ref}/config", json=new_config.model_dump(by_alias=True))


class Finetuning:
    def __init__(self, client: Predibase):
        self._client = client

        self.jobs = FinetuningJobs(self._client)


def _get_elapsed(curr_status: str, timeline_resp: dict[str, Any]):
    try:
        started = timeline_resp.get(curr_status, {}).get("startedAt", None)
        start_time = parser.parse(started)

        elapsed = datetime.datetime.utcnow() - start_time.replace(tzinfo=None)
        elapsed = elapsed - datetime.timedelta(microseconds=elapsed.microseconds)

        return str(elapsed)
    except Exception:
        return "{elapsed}"


def _get_metrics_table(task_type: str):
    if task_type == "grpo":
        table = ProgressTable(
            num_decimal_places=4,
            reprint_header_every_n_rows=0,
        )
        table.add_column("step")
        table.add_column("total_reward")
        table.add_column("total_reward_std")
        table.add_column("reward_fn", width=30)
        table.add_column("reward")
    elif task_type == "classification":
        table = ProgressTable(
            columns=["checkpoint", "train_loss", "validation_loss", "train_accuracy", "validation_accuracy"],
            num_decimal_places=4,
            reprint_header_every_n_rows=0,
        )
    else:
        table = ProgressTable(
            columns=["checkpoint", "train_loss", "validation_loss"],
            num_decimal_places=4,
            reprint_header_every_n_rows=0,
        )
    # Add feature/metric columns separately so we can customize the width
    # table.add_column("feature", width=16)
    # table.add_column("metric", width=24)
    # table.add_columns(["train", "val", "test"])

    # Horrible monkeypatched hack to make progress bar work in colab.
    # TODO: rework this and the logs / metrics streaming code overall.
    def newprint(*args, **kwargs):
        if "end" in kwargs and kwargs["end"] == "\r":
            kwargs["end"] = ""
            args = ("\r",) + args

        for file in table.files:
            print(*args, **kwargs, file=file)

    table._print = newprint

    return table
