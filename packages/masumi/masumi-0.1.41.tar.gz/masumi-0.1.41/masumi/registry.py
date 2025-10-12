from typing import List, Dict, Optional
import logging
import aiohttp
from .config import Config

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

class Agent:
    """
    Represents an AI agent that can be registered with the Masumi registry.
    
    This class handles agent registration, status checking, and related operations.
    """
    
    def __init__(
        self,
        name: str,
        config: Config,
        description: str,
        example_output: List[Dict[str, str]],
        tags: List[str],
        api_base_url: str,
        author_name: str,
        author_contact: str,
        author_organization: str,
        legal_privacy_policy: str,
        legal_terms: str,
        legal_other: str,
        capability_name: str,
        capability_version: str,
        pricing_unit: str,
        pricing_quantity: str,
        network: str = "Preprod",
        requests_per_hour: Optional[str] = None  # Deprecated parameter
    ):
        """
        Initialize a new Agent instance.
        
        Args:
            name (str): Name of the agent (must be unique)
            config (Config): Configuration for API endpoints and authentication
            description (str): Description of the agent's capabilities
            example_output (List[Dict[str, str]]): List of example outputs with name, url, and mimeType
            tags (List[str]): List of tags describing the agent
            api_base_url (str): URL where the agent's API is hosted
            author_name (str): Name of the agent's author
            author_contact (str): Contact information for the author
            author_organization (str): Organization the author belongs to
            legal_privacy_policy (str): URL to privacy policy
            legal_terms (str): URL to terms of service
            legal_other (str): URL to other legal documents
            capability_name (str): Name of the agent's capability
            capability_version (str): Version of the agent's capability
            requests_per_hour (str): Maximum requests per hour
            pricing_unit (str): Unit for pricing (e.g., "lovelace")
            pricing_quantity (str): Quantity for pricing
            network (str, optional): Network to use. Defaults to "Preprod"
        """
        self.name = name
        self.config = config
        self.description = description
        self.example_output = example_output
        self.tags = tags
        self.api_base_url = api_base_url
        self.author_name = author_name
        self.author_contact = author_contact
        self.author_organization = author_organization
        self.legal_privacy_policy = legal_privacy_policy
        self.legal_terms = legal_terms
        self.legal_other = legal_other
        self.capability_name = capability_name
        self.capability_version = capability_version
        self.requests_per_hour = requests_per_hour
        self.pricing_unit = pricing_unit
        self.pricing_quantity = pricing_quantity
        self.network = network
        
        logger.info(f"Initialized agent {name} on {network} network")
        
        self._headers = {
            "token": config.payment_api_key,
            "Content-Type": "application/json"
        }

    async def get_selling_wallet_vkey(self, network: str) -> str:
        """
        Fetch selling wallet vkey from payment source for the specified network.
        
        Args:
            network (str): Network to filter by ('Preprod' or 'Mainnet')
            
        Returns:
            str: The wallet vkey for the specified network
            
        Raises:
            ValueError: If no selling wallet is found for the specified network
        """
        logger.info(f"Fetching selling wallet vkey for network: {network}")
        
        payment_headers = {
            "token": self.config.payment_api_key,
            "Content-Type": "application/json"
        }
        logger.debug(f"Using payment headers: {payment_headers}")
        
        try:
            async with aiohttp.ClientSession() as session:
                logger.debug("Making GET request to payment source endpoint")
                async with session.get(
                    f"{self.config.payment_service_url}/payment-source/",
                    headers=payment_headers,
                    params={"take": "10"}
                ) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        logger.error(f"Failed to fetch payment sources: {error_text}")
                        raise ValueError(f"Failed to fetch payment sources: {error_text}")
                    
                    result = await response.json()
                    logger.debug(f"Received payment sources response")
                    
                    # Filter by network and get the first available selling wallet vkey
                    for source in result["data"]["PaymentSources"]:
                        if source["network"] == network and source["SellingWallets"]:
                            vkey = source["SellingWallets"][0]["walletVkey"]
                            logger.info(f"Found selling wallet vkey for network {network}: {vkey}")
                            return vkey
                    
                    logger.error(f"No selling wallet found for network: {network}")
                    raise ValueError(f"No selling wallet found for network: {network}")
                    
        except aiohttp.ClientError as e:
            logger.error(f"Network error while fetching payment sources: {str(e)}")
            raise

    async def check_registration_status(self, wallet_vkey: str) -> Dict:
        """Check registration status for a given wallet vkey"""
        logger.info(f"Checking registration status for wallet vkey: {wallet_vkey}")
        logger.debug(f"Network: {self.network}")
        
        try:
            async with aiohttp.ClientSession() as session:
                logger.debug("Making GET request to registry endpoint")
                params = {
                    "walletVKey": wallet_vkey,
                    "network": self.network
                }
                logger.debug(f"Query parameters: {params}")
                
                async with session.get(
                    f"{self.config.payment_service_url}/registry/",
                    headers=self._headers,
                    params=params
                ) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        logger.error(f"Status check failed with status {response.status}: {error_text}")
                        raise ValueError(f"Status check failed: {error_text}")
                    
                    result = await response.json()
                    logger.debug(f"Received registration status response.")
                    
                    # Verify this agent exists in the response
                    if "data" in result and "Assets" in result["data"]:
                        for asset in result["data"]["Assets"]:
                            if asset["name"] == self.name:
                                logger.info(f"Found registered agent: {self.name}")
                                logger.debug(f"Agent info: {asset}")
                                return result
                    
                    logger.warning(f"Agent {self.name} not found in registration status")
                    return result
                    
        except aiohttp.ClientError as e:
            logger.error(f"Network error while checking registration status: {str(e)}")
            raise

    async def register(self) -> Dict:
        """Register a new agent with the registry service"""
        logger.info(f"Starting registration for agent: {self.name}")
        logger.debug(f"Network: {self.network}")
        
        selling_wallet_vkey = await self.get_selling_wallet_vkey(self.network)
        logger.info(f"Retrieved selling wallet vkey: {selling_wallet_vkey}")
        
        payload = {
            "network": self.network,
            "ExampleOutputs": self.example_output,
            "Tags": self.tags,
            "name": self.name,
            "apiBaseUrl": self.api_base_url,
            "description": self.description,
            "Author": {
                "name": self.author_name,
                "contactEmail": self.author_contact,  # Using author_contact for email
                "contactOther": "",  # Empty for now as we don't have a separate field
                "organization": self.author_organization
            },
            "Legal": {
                "privacyPolicy": self.legal_privacy_policy,
                "terms": self.legal_terms,
                "other": self.legal_other
            },
            "sellingWalletVkey": selling_wallet_vkey,
            "Capability": {
                "name": self.capability_name,
                "version": self.capability_version
            },
            "AgentPricing": {
                "pricingType": "Fixed",
                "Pricing": [
                    {
                        "unit": self.pricing_unit,
                        "amount": self.pricing_quantity
                    }
                ]
            }
        }
        logger.debug(f"Registration payload prepared: {payload}")
        
        try:
            async with aiohttp.ClientSession() as session:
                logger.debug("Making POST request to registry endpoint")
                async with session.post(
                    f"{self.config.payment_service_url}/registry/",
                    headers=self._headers,
                    json=payload
                ) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        logger.error(f"Registration failed with status {response.status}: {error_text}")
                        raise ValueError(f"Registration failed: {error_text}")
                    
                    result = await response.json()
                    logger.info(f"Agent {self.name} registered successfully")
                    logger.debug(f"Registration response: {result}")
                    return result
                    
        except aiohttp.ClientError as e:
            logger.error(f"Network error during registration: {str(e)}")
            raise 