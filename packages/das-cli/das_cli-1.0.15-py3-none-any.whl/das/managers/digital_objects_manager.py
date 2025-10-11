from das.common.config import load_api_url
from das.services.entries import EntriesService
from das.services.digital_objects import DigitalObjectsService


class DigitalObjectsManager:
    def __init__(self):
        base_url = load_api_url()
        if base_url is None or base_url == "":
            raise ValueError(f"Base URL is required - {self.__class__.__name__}")

        self.digital_objects_service = DigitalObjectsService(base_url)
        self.entry_service = EntriesService(base_url)

    def link_existing_digital_objects(
        self, entry_code: str, digital_object_code_list: list[str], is_unlink: bool = False
    ) -> bool:
        """Attach or detach (unlink) digital objects to an entry using codes."""
        entry_response = self.entry_service.get_entry(entry_code)

        if entry_response is None:
            raise ValueError(f"Entry with code '{entry_code}' not found")

        entry_payload = entry_response.get("entry")
        if entry_payload is None:
            raise ValueError(f"Entry with code '{entry_code}' not found")

        digital_object_id_list: list[str] = []

        for code in digital_object_code_list:
            do_response = self.entry_service.get_entry(code)
            do_entry = do_response.get("entry") if do_response else None
            if do_entry is None:
                raise ValueError(f"Digital object with code '{code}' not found")
            digital_object_id_list.append(do_entry.get("id"))

        result = self.digital_objects_service.link_existing_digital_objects(
            attribute_id=entry_response.get("attributeId"),
            entry_id=entry_payload.get("id"),
            digital_object_id_list=digital_object_id_list,
            is_unlink=is_unlink,
        )

        return result


