from maleo.managers.client.maleo import MaleoClientManager
from maleo.managers.client.maleo.config import MaleoMetadataClientConfig
from .services.blood_type import BloodTypeClientService


class MaleoMetadataClientManager(MaleoClientManager[MaleoMetadataClientConfig]):
    def initalize_services(self):
        self.blood_type = BloodTypeClientService(
            application_context=self._application_context,
            config=self._config,
            logger=self._logger,
            http_client_manager=self._http_client_manager,
            private_key=self._private_key,
            redis=self._redis,
        )
