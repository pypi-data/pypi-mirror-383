from typing import Iterable, Optional
import os
import requests
from ....framework import File, DockerWebServiceApi, FileIO, Loc, LocalExecutor, CombinedPrerequisite, IPrerequisite
from pathlib import Path
from .controller import TortoiseTTSController
from .settings import TortoiseTTSSettings
from .upload_prerequisite import TortoiseTTSUploadPrerequisite





class TortoiseTTS(DockerWebServiceApi[TortoiseTTSSettings, TortoiseTTSController]):
    def __init__(self, address: str|None = None):
        super().__init__(address)


    def dub(self, text: str, voice: str, count = 3):
        result = requests.post(f'http://{self.address}/dub', json=dict(output_file_name = self.current_job_id, text=text, voice=voice, count=count))
        if result.status_code == 500:
            raise ValueError(f"TortoiseTTS server returned {result.status_code}\n{result.text}")
        files = []
        for i, result in enumerate(result.json()):
            path = self.controller.resource_folder('stash')/result
            files.append(File(
                self.current_job_id+f'.output.{i}.wav',
                FileIO.read_bytes(path),
                File.Kind.Audio
            ))
            os.unlink(path)
        return files


    @staticmethod
    def export_voice(
            voice: str,
            files: Optional[Iterable[Path]] = None,
            folder: Optional[Path] = None
    ) -> CombinedPrerequisite:
        if voice is None:
            raise ValueError("Voice cannot be None")

        if folder is not None:
            files = [folder/c for c in os.listdir(folder)]
        elif files is not None:
            files = list(files)
        else:
            raise ValueError(f"`files` and `folder` were both null")

        command = [TortoiseTTSUploadPrerequisite(voice, file) for file in files]
        return CombinedPrerequisite(command)


    Controller = TortoiseTTSController
    Settings = TortoiseTTSSettings