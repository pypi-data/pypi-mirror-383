from typing import Iterable
from unittest import TestCase
from ....framework import (
    RunConfiguration, SmallImageBuilder,
    IImageBuilder, DockerWebServiceController, BrainBoxApi, IModelDownloadingController, DownloadableModel,
    TestReport, INotebookableController
)
from .settings import RhasspyKaldiSettings
from .model import RhasspyKaldiModel
from pathlib import Path


class RhasspyKaldiController(
    DockerWebServiceController[RhasspyKaldiSettings],
    IModelDownloadingController,
    INotebookableController,
):
    def get_image_builder(self) -> IImageBuilder|None:
        return SmallImageBuilder(
            Path(__file__).parent/'container',
            DOCKERFILE,
            None
        )

    def get_downloadable_model_type(self) -> type[DownloadableModel]:
        return RhasspyKaldiModel

    def get_service_run_configuration(self, parameter: str|None) -> RunConfiguration:
        if parameter is not None:
            raise ValueError(f"`parameter` must be None for {self.get_name()}")
        return RunConfiguration(
            None,
            mount_resource_folders={'profiles': '/profiles', 'models': '/models'},
            publish_ports={self.settings.connection.port: 8084}
        )

    def get_notebook_configuration(self) -> RunConfiguration|None:
        return self.get_service_run_configuration(None).as_notebook_service()

    def get_default_settings(self):
        return RhasspyKaldiSettings()

    def create_api(self):
        from .api import RhasspyKaldi
        return RhasspyKaldi()

    def post_install(self):
        self.download_models(self.settings.languages)
        
    def _self_test_internal(self, api: BrainBoxApi, tc: TestCase) -> Iterable:
        from .tests import english, german, english_custom
        yield TestReport.attach_source_file(english)
        yield from english(api, tc)
        yield from german(api, tc)
        yield from english_custom(api, tc)


DOCKERFILE = f'''
FROM rhasspy/rhasspy

RUN /usr/lib/rhasspy/.venv/bin/pip install notebook flask

COPY . /home/app

ENTRYPOINT ["/usr/lib/rhasspy/.venv/bin/python", "/home/app/main.py"] 
'''


