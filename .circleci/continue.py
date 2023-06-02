from dataclasses import dataclass, asdict
from typing import Literal as L
import http.client
import json
import os

StepName = L["checkout"]


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
    jobs: list[str]


@dataclass
class Config:
    version: float
    jobs: dict[str, Job]
    workflows: dict[str, WorkflowJob]


def python_package(package: str) -> Job:
    cd = f"cd packages/{package} \n"
    return Job(
        docker=[Docker(image="cimg/python:3.11.3")],
        steps=[
            "checkout",
            Step(
                Run(
                    name="pip install",
                    command=cd + "pip install -e '.[dev]'",
                )
            ),
            Step(
                Run(
                    name="pytest",
                    command=cd + "pytest -vv",
                )
            ),
        ],
    )


package_names = ["account"]
jobs_map = {f"build-and-test-{p}": python_package(p) for p in package_names}
job_names = [f"build-and-test-{p}" for p in package_names]

config = Config(
    version=2.1,
    jobs=jobs_map,
    workflows={"build-and-test": WorkflowJob(jobs=job_names)},
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
