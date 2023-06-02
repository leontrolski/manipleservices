from dataclasses import dataclass, asdict
from typing import Literal as L
import http.client
import json
import os

StepName = L["checkout"]
JobName = L["say-goodbye"]
WorkflowName = L["say-goodbye-workflow"]


@dataclass
class Docker:
    image: str


@dataclass
class Run:
    name: str
    command: str


@dataclass
class Step:
    run: Run


@dataclass
class Job:
    docker: list[Docker]
    steps: list[StepName | Step]


@dataclass
class WorkflowJob:
    jobs: list[JobName]


@dataclass
class Config:
    version: float
    jobs: dict[JobName, Job]
    workflows: dict[WorkflowName, WorkflowJob]


config = Config(
    version=2.1,
    jobs={
        "say-goodbye": Job(
            docker=[Docker(image="cimg/base:stable")],
            steps=[
                "checkout",
                Step(
                    Run(
                        name="Say hello",
                        command="echo Goodbye!",
                    )
                ),
            ],
        ),
    },
    workflows={"say-goodbye-workflow": WorkflowJob(jobs=["say-goodbye"])},
)


def run_config(config_typed: Config) -> None:
    print("Running generated config")
    payload = {
        "continuation-key": os.environ["CIRCLE_CONTINUATION_KEY"].strip(),
        "configuration": json.dumps(asdict(config_typed)),
        "parameters": {},
    }
    headers = {"Content-Type": "application/json", "Accept": "application/json"}
    conn = http.client.HTTPSConnection("circleci.com")
    conn.request("POST", "/api/v2/pipeline/continue", json.dumps(payload), headers)
    res = conn.getresponse()
    data = res.read()
    print(data.decode("utf-8"))


if __name__ == "__main__":
    run_config(config)
