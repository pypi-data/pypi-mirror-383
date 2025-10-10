from abc import ABC, abstractmethod

from attrs import define

from griptape.artifacts import BaseArtifact
from griptape.engines.rag import RagContext
from griptape.engines.rag.modules import BaseRagModule


@define(kw_only=True)
class BaseResponseRagModule(BaseRagModule, ABC):
    @abstractmethod
    def run(self, context: RagContext) -> BaseArtifact: ...
