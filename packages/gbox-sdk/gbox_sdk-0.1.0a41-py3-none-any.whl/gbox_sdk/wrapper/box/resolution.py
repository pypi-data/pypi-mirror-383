from gbox_sdk._client import GboxClient
from gbox_sdk.types.v1.box_resolution_set_response import BoxResolutionSetResponse


class ResolutionOperator:
    def __init__(self, client: GboxClient, box_id: str):
        self.client = client
        self.box_id = box_id

    def set(self, height: float, width: float) -> BoxResolutionSetResponse:
        """
        Set the resolution of the box

        Args:
          height: The height of the screen
          width: The width of the screen

        Returns:
            BoxResolutionSetResponse: The response from the resolution set action.

        Example:
            >>> response = myBox.resolution.set(height=1080, width=1920)
        """
        return self.client.v1.boxes.resolution_set(box_id=self.box_id, height=height, width=width)
