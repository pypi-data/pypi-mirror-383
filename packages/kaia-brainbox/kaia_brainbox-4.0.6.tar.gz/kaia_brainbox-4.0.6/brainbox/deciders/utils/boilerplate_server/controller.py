from typing import Iterable
from unittest import TestCase
from ....framework import (
    RunConfiguration, TestReport, BrainboxImageBuilder, IImageBuilder, DockerWebServiceController,
    BrainBoxApi, BrainBoxTask, FileIO, INotebookableController, IModelDownloadingController, DownloadableModel
)
from .settings import BoilerplateServerSettings
from pathlib import Path


class BoilerplateServerController(
    DockerWebServiceController[BoilerplateServerSettings],
    INotebookableController,
):
    def get_image_builder(self) -> IImageBuilder|None:
        return BrainboxImageBuilder(
            Path(__file__).parent,
            '3.11.11',
            allow_arm64=True
        )

    def get_service_run_configuration(self, parameter: str|None) -> RunConfiguration:
        if parameter is not None:
            raise ValueError(f"`parameter` must be None for {self.get_name()}")
        return RunConfiguration(
            publish_ports={self.connection_settings.port:8080},
        )

    def get_notebook_configuration(self) -> RunConfiguration|None:
        return self.get_service_run_configuration(None).as_notebook_service()

    def get_default_settings(self):
        return BoilerplateServerSettings()

    def create_api(self):
        from .api import BoilerplateServer
        return BoilerplateServer()

    def _self_test_internal(self, api: BrainBoxApi, tc: TestCase) -> Iterable:
        from .api import BoilerplateServer

        api.execute(BrainBoxTask.call(BoilerplateServer).echo('argument'))


        yield (
            TestReport
            .last_call(api)
            .href('echo')
            .with_comment("Returns JSON with passed arguments and `success` fields")
        )


