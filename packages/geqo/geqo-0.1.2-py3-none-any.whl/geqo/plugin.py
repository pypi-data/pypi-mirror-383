import importlib.metadata
import os


def external_backends():
    """Finds all installed backend plugins registered to the 'geqo.backends' group."""

    available_backends = {}

    entry_points = importlib.metadata.entry_points(group="geqo.backends")

    for entry_point in entry_points:
        backend_name = entry_point.name
        backend_class = entry_point.load()
        available_backends[backend_name] = backend_class
        print(f"--> Found '{backend_name}' backend.")

    return available_backends


class Credentials:
    """
    Manages authentication credentials for quantum simulation backends
    """

    def __init__(self, provider: str):
        self.provider = provider

        self.api_key = None
        self.username = None
        self.password = None

    def load_from_env(self):
        """
        Load credentials from environment variables:
            PROVIDER_API_KEY
            PROVIDER_USERNAME
            PROVIDER_PASSWORD
        """
        self.api_key = os.getenv(f"{self.provider}_API_KEY")
        self.username = os.getenv(f"{self.provider}_USERNAME")
        self.password = os.getenv(f"{self.provider}_PASSWORD")
        self.validate_credentials()

    def load_from_file(self, file_path):
        """
        Load credentials from .env format file
        """
        try:
            from dotenv import load_dotenv
        except ImportError:
            raise ImportError(
                "To load credentials from a file, you must install the python-dotenv package. "
                "The package can be installed by running: pip install dotenv"
            )
        load_dotenv(file_path)
        self.load_from_env()

    def validate_credentials(self):
        if not self.api_key and not all([self.username, self.password]):
            raise ValueError("Missing required credentials for provider")

    def __repr__(self):
        return f"Credentials(loaded={'*' in self.api_key})"
