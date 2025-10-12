import os

class Config:
    """
    Centralized configuration for the masumi_crewai package.
    """

    def __init__(self, payment_service_url: str, payment_api_key: str,
                 registry_service_url: str = None, registry_api_key: str = None,
                 preprod_address: str = None,
                 mainnet_address: str = None):
        self.payment_service_url = payment_service_url
        self.payment_api_key = payment_api_key
        self.registry_service_url = registry_service_url
        self.registry_api_key = registry_api_key
        self.preprod_address = preprod_address
        self.mainnet_address = mainnet_address
        self._validate()

    def _validate(self):
        """
        Validate that all required configuration parameters are set.
        Raises ValueError if any required parameter is missing.
        """
        required_configs = {
            "PAYMENT_SERVICE_URL": self.payment_service_url,
            "PAYMENT_API_KEY": self.payment_api_key,
        }

        missing_configs = [key for key, value in required_configs.items() if not value]
        if missing_configs:
            raise ValueError(f"Missing required configuration parameters: {', '.join(missing_configs)}")