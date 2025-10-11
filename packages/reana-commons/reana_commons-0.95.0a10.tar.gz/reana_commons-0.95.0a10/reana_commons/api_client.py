# -*- coding: utf-8 -*-
#
# This file is part of REANA.
# Copyright (C) 2018, 2019, 2020, 2021, 2022 CERN.
#
# REANA is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.
"""REANA REST API base client."""

import json
import logging
import os
import sys
import traceback
from typing import Optional

from bravado.client import RequestsClient, SwaggerClient

# Use importlib.resources for Python 3.9+ or importlib_resources backport for 3.8
if sys.version_info >= (3, 9):
    from importlib.resources import files
else:
    from importlib_resources import files
from bravado.exception import (
    HTTPBadRequest,
    HTTPError,
    HTTPInternalServerError,
    HTTPNotFound,
)
from mock import Mock

from reana_commons.config import OPENAPI_SPECS
from reana_commons.errors import (
    MissingAPIClientConfiguration,
    REANAJobControllerSubmissionError,
)
from reana_commons.job_utils import serialise_job_command


class BaseAPIClient(object):
    """REANA API client code."""

    _bravado_client_instance = None

    def __init__(self, service, http_client=None):
        """Create an OpenAPI client."""
        server_url, spec_file = OPENAPI_SPECS[service]
        json_spec = self._get_spec(spec_file)
        current_instance = BaseAPIClient._bravado_client_instance
        # We reinstantiate the bravado client instance if
        # 1. The current instance doesn't exist, or
        # 2. We're passing an http client (likely a mock), or
        # 3. The current instance is a Mock, meaning that either we want to
        #    use the `RequestClient` or we're passing a different mock.
        if (
            current_instance is None
            or http_client
            or isinstance(current_instance.swagger_spec.http_client, Mock)
        ):
            BaseAPIClient._bravado_client_instance = SwaggerClient.from_spec(
                json_spec,
                http_client=http_client or RequestsClient(ssl_verify=False),
                config={"also_return_response": True},
            )
        self._load_config_from_env()
        self._client = BaseAPIClient._bravado_client_instance
        if server_url is None:
            raise MissingAPIClientConfiguration(
                "Configuration to connect to {} is missing.".format(service)
            )
        self._client.swagger_spec.api_url = server_url
        self.server_url = server_url

    def _load_config_from_env(self):
        """Override configuration from environment."""
        OPENAPI_SPECS["reana-server"] = (
            os.getenv("REANA_SERVER_URL"),
            "reana_server.json",
        )

    def _get_spec(self, spec_file):
        """Get json specification from package data."""
        # Get the OpenAPI specification file using importlib.resources
        package_files = files("reana_commons")
        spec_resource = package_files / "openapi_specifications" / spec_file

        # For Python 3.9+, we need to handle this as a Traversable
        if sys.version_info >= (3, 9):
            json_spec = json.loads(spec_resource.read_text())
        else:
            # For Python 3.8 with backport, convert to string path
            with open(str(spec_resource)) as f:
                json_spec = json.load(f)
        return json_spec


class JobControllerAPIClient(BaseAPIClient):
    """REANA-Job-Controller http client class."""

    def submit(  # noqa: C901
        self,
        workflow_uuid="",
        image="",
        cmd="",
        prettified_cmd="",
        workflow_workspace="",
        job_name="",
        cvmfs_mounts="false",
        compute_backend=None,
        kerberos=False,
        kubernetes_uid=None,
        kubernetes_memory_limit=None,
        unpacked_img=False,
        voms_proxy=False,
        rucio=False,
        htcondor_max_runtime="",
        htcondor_accounting_group="",
        slurm_partition="",
        slurm_time="",
        kubernetes_job_timeout: Optional[int] = None,
        c4p_cpu_cores="",
        c4p_memory_limit="",
        c4p_additional_requirements="",
    ):
        """Submit a job to RJC API.

        :param workflow_uuid: UUID of the workflow.
        :param job_name: Name of the job.
        :param image: Identifier of the Docker image which will run the job.
        :param cmd: String which represents the command to execute. It can be
            modified by the workflow engine i.e. prepending ``cd /some/dir/``.
        :param prettified_cmd: Original command submitted by the user.
        :param workflow_workspace: Path to the workspace of the workflow.
        :param cvmfs_mounts: String with CVMFS volumes to mount in job pods.
        :param compute_backend: Job compute backend.
        :param kerberos: Decides if kerberos should be provided for job container.
        :param voms_proxy: Decides if grid proxy should be provided for job
            container.
        :param rucio: Decides if a rucio environment should be provided for job.
        :param kubernetes_uid: Overwrites the default user id in the job container.
        :param kubernetes_memory_limit: Overwrites the default memory limit in the job container.
        :param unpacked_img: Decides if unpacked iamges should be used.
        :param htcondor_max_runtime: Maximum runtime of a HTCondor job.
        :param htcondor_accounting_group: Accounting group of a HTCondor job.
        :param slurm_partition: Partition of a Slurm job.
        :param slurm_time: Maximum timelimit of a Slurm job.
        :param kubernetes_job_timeout: Timeout for the job in seconds.
        :param c4p_cpu_cores: Amount of CPU cores requested to process C4P job
        :param c4p_memory_limit: Amount of memory requested to process C4P job
        :param c4p_additional_requirements: Additional requirements requested to process C4P job like GPU, etc.
        :return: Returns a dict with the ``job_id``.
        """
        job_spec = {
            "docker_img": image.strip(),
            "cmd": serialise_job_command(cmd),
            "prettified_cmd": prettified_cmd,
            "env_vars": {},
            "workflow_workspace": workflow_workspace,
            "job_name": job_name,
            "cvmfs_mounts": cvmfs_mounts,
            "workflow_uuid": workflow_uuid,
        }

        if compute_backend:
            job_spec["compute_backend"] = compute_backend

        if kerberos:
            job_spec["kerberos"] = kerberos

        if voms_proxy:
            job_spec["voms_proxy"] = voms_proxy

        if rucio:
            job_spec["rucio"] = rucio

        if kubernetes_uid:
            job_spec["kubernetes_uid"] = kubernetes_uid

        if kubernetes_memory_limit:
            job_spec["kubernetes_memory_limit"] = kubernetes_memory_limit

        if kubernetes_job_timeout is not None:
            job_spec["kubernetes_job_timeout"] = kubernetes_job_timeout

        if unpacked_img:
            job_spec["unpacked_img"] = unpacked_img

        if htcondor_max_runtime:
            job_spec["htcondor_max_runtime"] = htcondor_max_runtime

        if htcondor_accounting_group:
            job_spec["htcondor_accounting_group"] = htcondor_accounting_group

        if slurm_partition:
            job_spec["slurm_partition"] = slurm_partition

        if slurm_time:
            job_spec["slurm_time"] = slurm_time

        if c4p_cpu_cores:
            job_spec["c4p_cpu_cores"] = c4p_cpu_cores

        if c4p_memory_limit:
            job_spec["c4p_memory_limit"] = c4p_memory_limit

        if c4p_additional_requirements:
            job_spec["c4p_additional_requirements"] = c4p_additional_requirements

        try:
            response, http_response = self._client.jobs.create_job(
                job=job_spec
            ).result()
            return response
        except HTTPError as e:
            msg = e.response.json().get("message")
            raise REANAJobControllerSubmissionError(msg)
        except Exception as e:
            logging.error(traceback.format_exc())
            raise e

    def check_status(self, job_id):
        """Check status of a job."""
        response, http_response = self._client.jobs.get_job(job_id=job_id).result()
        if http_response.status_code == 404:
            raise HTTPNotFound(
                "The given job ID was not found. Error: {}".format(http_response.data)
            )
        return response

    def get_logs(self, job_id):
        """Get logs of a job."""
        response, http_response = self._client.jobs.get_logs(job_id=job_id).result()
        if http_response.status_code == 404:
            raise HTTPNotFound(
                "The given job ID was not found. Error: {}".format(http_response.data)
            )
        return http_response.text

    def check_if_cached(self, job_spec, step, workflow_workspace):
        """Check if job result is in cache."""
        response, http_response = self._client.job_cache.check_if_cached(
            job_spec=json.dumps(job_spec),
            workflow_json=json.dumps(step),
            workflow_workspace=workflow_workspace,
        ).result()
        if http_response.status_code == 400:
            raise HTTPBadRequest(
                "Bad request to check cache. Error: {}".format(http_response.data)
            )
        elif http_response.status_code == 500:
            raise HTTPInternalServerError(
                "Internal Server Error. Error: {}".format(http_response.data)
            )
        return http_response


def get_current_api_client(component):
    """Proxy which returns current API client for a given component."""
    rwc_api_client = BaseAPIClient(component)

    return rwc_api_client._client
