from das.common.api import post_data
from das.common.config import load_token


class DigitalObjectsService:
    def __init__(self, base_url):
        self.base_url = f"{base_url}/api/services/app/DigitalObject"

    def link_existing_digital_objects(self, attribute_id: int, entry_id: str, digital_object_id_list: list[str], is_unlink: bool = False):
        """Link existing digital objects to an entry."""
        token = load_token()

        if token is None or token == "":
            raise ValueError("Authorization token is required")

        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }

        payload = {
            "attributeId": attribute_id,
            "attributeValueId": entry_id,
            "digitalObjects": [],
        }

        for digital_object_id in digital_object_id_list:
            payload["digitalObjects"].append(
                {
                    "attributeId": attribute_id,
                    "attributeValueId": entry_id,
                    "digitalObjectId": digital_object_id,
                    "isDeleted": is_unlink,
                }
            )

        response = post_data(
            f"{self.base_url}/LinkExistingDigitalObject", data=payload, headers=headers
        )

        return response.get("success")
    


