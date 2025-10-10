import io
import sys
from typing import Optional
import docker
from docker.models.containers import Container
from docker.errors import DockerException, ImageNotFound
from loguru import logger


def get_docker_client() -> docker.DockerClient:
    try:
        return docker.from_env()
    except DockerException:
        logger.error("Docker could not be instantiated. Is it installed and running?")
        raise Exception(
            "Docker could not be instantiated. Is it installed and running?"
        )


def create_image_if_needed(
    client: docker.DockerClient, image_name: str, docker_file: str
):
    try:
        client.images.get(image_name)
        # image already created
        return
    except ImageNotFound:
        # we still need to create the image
        ...

    logger.info(
        "Setting up docker container. This might take a while, but only has to be done once."
    )

    docker_file_bytes = io.BytesIO(docker_file.encode("utf-8"))

    client.images.build(
        fileobj=docker_file_bytes,
        tag=image_name,
        rm=True,
        platform="linux/x86_64",
    )


def start_container(
    client: docker.DockerClient, image_name: str, **kwargs
) -> Container:
    return client.containers.run(
        image_name, "sleep infinity", detach=True, platform="linux/x86_64", **kwargs
    )


def run_and_print_command(
    container: Container,
    command: str,
    user: Optional[str] = None,
    working_dir: Optional[str] = None,
):
    result = container.exec_run(
        command, stream=True, demux=True, user=user, workdir=working_dir
    )

    for stdout, stderr in result.output:
        if stdout:
            print(stdout.decode(), end="")
        if stderr:
            print(stderr.decode(), end="", file=sys.stderr)
