

from app.services.storage import StorageService


class StorageController:

    def __init__(self, storage_service: StorageService):
        self.storage_service = storage_service

    def get_dptos(self):
        return self.storage_service.get_dptos()

        