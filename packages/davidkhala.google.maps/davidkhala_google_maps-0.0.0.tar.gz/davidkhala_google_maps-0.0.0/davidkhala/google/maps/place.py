from google.api_core.client_options import ClientOptions
from google.maps import places_v1


class Places:
    def __init__(self, project_id, api_key):
        self.client = places_v1.PlacesClient(client_options=ClientOptions(
            api_key=api_key,
            quota_project_id=project_id
        ))

    def search(self, text_query, all_fields=False):
        request = places_v1.SearchTextRequest(text_query=text_query)
        field_mask = "*" if all_fields else "places.formattedAddress,places.displayName,places.location,places.id"

        response = self.client.search_text(
            request=request,
            metadata=[("x-goog-fieldmask", field_mask)]
        )

        places = response.places

        if all_fields:
            return places
        else:
            return [{
                "formatted_address": place.formatted_address,
                "location": {
                    "latitude": place.location.latitude,
                    "longitude": place.location.longitude
                } if place.location else None,
                "display_name": place.display_name.text if place.display_name else None,
                "id": place.id
            } for place in places]
