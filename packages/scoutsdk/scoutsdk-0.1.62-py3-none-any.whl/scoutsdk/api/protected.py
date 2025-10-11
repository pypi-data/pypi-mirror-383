from .request_utils import RequestUtils
from scouttypes.protected import SignedUrlResponse


class ProtectedAPI:
    def __init__(self, base_url: str, headers: dict) -> None:
        self._base_url = base_url
        self._headers = headers

    def get_signed_url(self, path: str) -> SignedUrlResponse:
        """
        Generate a signed URL for accessing a protected resource.

        Args:
            path (str): The relative path to the protected resource.

        Returns:
            SignedUrlResponse: The response object containing the signed URL for the resource.

        Raises:
            ValueError: If the response is invalid or cannot be validated.
        """
        protected_path = "/protected/"
        final_path = (
            path
            if path.startswith(protected_path)
            else protected_path + path.lstrip("/")
        )

        response, status_code = RequestUtils.get(
            url=f"{self._base_url}/api{final_path}",
            headers=self._headers,
        )

        return SignedUrlResponse.model_validate(response)
