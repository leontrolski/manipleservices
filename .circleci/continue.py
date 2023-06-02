from dataclasses import dataclass, asdict
import http.client
import json
import subprocess
from typing import Literal as L
import os

StepName = L["checkout"]


def sh(cmd: str) -> str:
    return subprocess.check_output(cmd, shell=True).decode()


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
                    name="symlink packages for install",
                    command="ln -s $PWD/packages /tmp/maniple-packages",
                )
            ),
            Step(
                Run(
                    name="pip install",
                    command=cd + "pip install -e '.[dev]'",
                )
            ),
            Step(
                Run(
                    name="lint",
                    command=cd + "mypy src",
                )
            ),
            Step(
                Run(
                    name="test",
                    command=cd + "pytest -vv",
                )
            ),
        ],
    )


def make_config(changed_packages: list[str]) -> Config:
    jobs_map = {f"build-and-test-{p}": python_package(p) for p in changed_packages}
    job_names = [f"build-and-test-{p}" for p in changed_packages]
    return Config(
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


def changed_packages() -> set[str]:
    return {
        path.split("/")[1]
        for path in sh("git diff main HEAD --name-only").splitlines()
        if path.startswith("packages/")
    }


def add_dependant_packages(packages: set[str]) -> list[str]:
    return sorted(packages)


if __name__ == "__main__":
    packages = add_dependant_packages(changed_packages())
    print(f"Running CI for packages: {packages}")
    run_config(make_config(packages))
