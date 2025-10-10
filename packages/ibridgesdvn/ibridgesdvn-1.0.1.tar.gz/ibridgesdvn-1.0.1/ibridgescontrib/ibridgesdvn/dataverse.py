"""Dataverse functionality for creating a draft."""

from pathlib import Path

from httpx import Client, Request
from httpx._exceptions import HTTPError
from pyDataverse.api import NativeApi
from pyDataverse.auth import BearerTokenAuth
from pyDataverse.exceptions import ApiAuthorizationError
from pyDataverse.models import Datafile, Dataset
from pyDataverse.utils import read_file


class Dataverse:
    """A utility class to interact with a Dataverse instance using the provided URL and API token.

    This class supports authentication, dataset management, and metadata retrieval.
    """

    def __init__(self, url: str, token: str):
        """Initialise the DataverseOperations instance.

        Args:
        ----
            url (str): The base URL of the Dataverse instance.
            token (str): The API token used for authentication.

        Raises:
        ------
            ValueError: If the API token is not provided.
            ApiAuthorizationError: If the token does not successfully authenticate.

        """
        self.dvn_url = url
        self.dvn_token = token

        if self.dvn_token is None:
            raise ValueError("Dataverse API token cannot be empty.")

        if self.user_authenticated():
            self.api = NativeApi(self.dvn_url, self.dvn_token)
        else:
            raise ApiAuthorizationError("Dataverse and API token do not match.")

    def user_authenticated(self) -> True:
        """Verify if the user token is valid for the Dataverse instance.

        Returns:
        -------
            bool: True if the token is valid and authentication succeeds.

        Note:
        ----
            This method performs a basic request with the Bearer token to check authorization.

        """
        auth = BearerTokenAuth(self.dvn_token)
        request = Request("GET", self.dvn_url)
        modified_request = next(auth.auth_flow(request))
        return modified_request.headers["authorization"] == "Bearer " + self.dvn_token

    def get_dataverse_info(self, dataverse):
        """Retrieve the children (datasets and sub-dataverses) of a specified Dataverse.

        Args:
        ----
            dataverse (str): The alias or identifier of the Dataverse.

        Returns:
        -------
            dict: The response containing child items of the Dataverse.

        """
        return self.api.get_children(dataverse)

    def dataverse_exists(self, dataverse: str):
        """Check whether a specified Dataverse exists.

        Args:
        ----
            dataverse (str): The alias or identifier of the Dataverse.

        Returns:
        -------
            bool: True if the Dataverse exists; False otherwise.

        """
        answer = self.api.get_dataverse(dataverse)
        return answer.is_success

    def list_dataverse_content(self, dataverse: str) -> dict:
        """Retrieve the list of datasets and sub-dataverses contained within a specified Dataverse.

        Args:
        ----
            dataverse (str): The alias or identifier of the Dataverse to query.

        Returns:
        -------
            dict: A dictionary representing the JSON response from the Dataverse API,
                  typically including datasets and nested dataverses.

        Raises:
        ------
            HTTPError: If the API response status code is not 200 (i.e., request failed).

        """
        url = f"https://demo.dataverse.nl/api/dataverses/{dataverse}/contents"
        headers = {"X-Dataverse-key": self.dvn_token}

        request = Request("GET", url, headers=headers)
        with Client() as client:
            response = client.send(request)

        if response.status_code in range(200, 300):
            return response.json()
        raise HTTPError(f"{response.status_code}, {response.reason_phrase}")

    def get_dataset_info(self, data_id: str):
        """Retrieve metadata and information for a dataset using its DOI identifier.

        Args:
        ----
            data_id (str): The dataset identifier (excluding the 'doi:' prefix).

        Returns:
        -------
            dict: The JSON response containing dataset metadata and details.

        Raises:
        ------
            HTTPError: If the API response status code is not 200 (successful).

        """
        response = self.api.get_dataset(f"doi:{data_id}")
        if response.status_code in range(200, 300):
            return response.json()
        raise HTTPError(f"{response.status_code}, {response.reason_phrase}")

    def dataset_exists(self, data_id):
        """Look up if data set can be found in Dataverse."""
        response = self.api.get_dataset(f"doi:{data_id}")
        return response.status_code in range(200, 300)

    def create_dataset_with_json(self, dataverse: str, metadata: Path, verbose: bool = False):
        """Create a new dataset from a json metadata file.

        Parameters
        ----------
        dataverse:
            The name of the Dataverse Collection where the dataset will be created.
        metadata:
            The path to a valid Dataverse Dataset metadata file.
        verbose:
            Print summary if True.

        """
        if dataverse is None:
            raise ValueError("Dataverse name must not be empty.")

        ds = Dataset()
        ds.from_json(read_file(str(metadata)))

        if verbose:
            print("Dataset metadata ok:", ds.validate_json())
            print(ds.get())

        if not ds.validate_json():
            raise ValueError("Something is wrong with the dataset's metadata.")

        response = self.api.create_dataset(dataverse, ds.json())

        if response.status_code not in range(200, 300):
            raise HTTPError(f"{response.status_code}, {response.reason_phrase}")

        return response

    def create_dataset(self, dataverse: str, metadata: str):  # pylint: disable=R0913, R0917
        """Create a new dataset in a specified Dataverse repository.

        Parameters
        ----------
        dataverse:
            The name of the Dataverse Collection where the dataset will be created.
        metadata:
            A minimal metadata json string.

        Raises
        ------
                ValueError: If any of the required parameters are missing or empty
                    (e.g., dataverse, title, subject, authors, contacts).
                HTTPError: If the response from the API is not successful
                    (i.e., status code is not 200).

        Returns
        -------
            None: The function creates the dataset but does not return any value.

        """
        if dataverse is None:
            raise ValueError("Dataverse name must not be empty.")
        if metadata is None:
            raise ValueError("Provide a dictionary conatining the metadata..")

        ds = Dataset()
        # ds.set(metadata)
        ds.from_json(metadata)
        if not ds.validate_json():
            raise ValueError("Something is wrong with the dataset's metadata.")

        response = self.api.create_dataset(dataverse, ds.json())

        if response.status_code not in range(200, 300):
            raise HTTPError(f"{response.status_code}, {response.reason_phrase}")

        return response

    def add_datafile_to_dataset(self, dataset_id: str, file_path: Path, verbose: bool = True):
        """Upload a data file to a specific dataset.

        Parameters
        ----------
        dataset_id:
           The ID of the dataset to which the data file will be uploaded.
        file_path:
           The file path of the data file to be uploaded.
        verbose:
           If True, prints additional details for debugging. Defaults to True.

        Raises
        ------
            HTTPError: If the response status code is not 200,
                       an HTTPError is raised with the status code and reason.

        Returns
        -------
            None: The function uploads the file and does not return any value.

        """
        data_metadata = {"pid": f"doi:{dataset_id}", "filename": file_path.name}

        df = Datafile()
        df.set(data_metadata)

        if verbose:
            print(df.get())

        response = self.api.upload_datafile(f"doi:{dataset_id}", file_path, df.json())

        if response.status_code not in range(200, 300):
            raise HTTPError(f"{response.status_code}, {response.reason_phrase}")

    def get_checksum_by_filename(self, dataset_id: str, target_label: str):
        """Retrieve the checksum of a specific file by its label.

        Parameters
        ----------
        dataset_id:
            The ID of the dataset.
        target_label:
            The name of the file in the dataset.

        Returns
        -------
        str or None: The checksum value if found, else None.

        """
        data_dict = self.get_dataset_info(dataset_id)
        files = data_dict["data"]["latestVersion"]["files"]
        for file in files:
            if file.get("label") == target_label:
                return file["dataFile"]["checksum"]["value"]

        return None
