from dataclasses import dataclass
from datetime import datetime, timezone, timedelta
import asyncio
import logging
from typing import List, Optional, Dict, Any, Set, Callable
import aiohttp
from .config import Config
import json
from .helper_functions import create_masumi_input_hash, create_masumi_output_hash

# Configure logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Create console handler if no handlers exist
if not logger.handlers:
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

@dataclass
class Amount:
    """
    Represents a payment amount in a specific unit.
    
    Attributes:
        amount (int): The payment amount (e.g., 1000000 for 1 ADA)
        unit (str): The currency unit (e.g., 'lovelace' for ADA)
    """
    amount: int
    unit: str

class Payment:
    """
    Handles Cardano blockchain payment operations including creation, monitoring, and completion.
    
    This class manages payment requests and their lifecycle, supporting multiple concurrent
    payment tracking. It uses the Masumi payment service for all payment operations.
    
    Attributes:
        agent_identifier (str): Unique identifier for the agent making payments
        amounts (List[Amount]): List of payment amounts and their units
        network (str): Network to use ('Preprod' or 'Mainnet')
        payment_type (str): Type of payment (fixed to 'WEB3_CARDANO_V1')
        payment_ids (Set[str]): Set of active payment IDs being tracked
        config (Config): Configuration for API endpoints and authentication
    """

    def __init__(self, agent_identifier: str, amounts: Optional[List[Amount]] = None, 
                 config: Config = None, network: str = "Preprod", 
                 preprod_address: Optional[str] = None,
                 mainnet_address: Optional[str] = None,
                 identifier_from_purchaser: str = "default_purchaser_id",
                 input_data: Optional[dict] = None):
        """
        Initialize a new Payment instance.
        
        Args:
            agent_identifier (str): Unique identifier for the agent
            amounts (List[Amount], optional): DEPRECATED - Payment amounts no longer used in API
            config (Config): Configuration object with API details
            network (str, optional): Network to use. Defaults to "PREPROD"
            preprod_address (str, optional): Custom preprod contract address
            mainnet_address (str, optional): Custom mainnet contract address
            identifier_from_purchaser (str): Identifier provided by purchaser. 
                                           Defaults to 'default_purchaser_id'
            input_data (str, optional): Input data for hashing
        """
        logger.info(f"Initializing Payment instance for agent {agent_identifier} on {network} network")
        self.agent_identifier = agent_identifier
        self.preprod_address = preprod_address or config.preprod_address
        self.mainnet_address = mainnet_address or config.mainnet_address
        self.amounts = amounts
        self.network = network
        self.payment_type = "Web3CardanoV1"
        self.payment_ids: Set[str] = set()
        self.identifier_from_purchaser = identifier_from_purchaser
        self._status_check_task: Optional[asyncio.Task] = None
        self.config = config
        self._headers = {
            "token": config.payment_api_key,
            "Content-Type": "application/json"
        }
        # Hash the input data if provided
        self.input_hash = (
            create_masumi_input_hash(input_data, self.identifier_from_purchaser)
            if input_data
            else None
        )
        logger.debug(f"Input data: {input_data}")
        logger.debug(f"Input hash: {self.input_hash}")
        #logger.debug(f"Payment amounts configured: {[f'{a.amount} {a.unit}' for a in amounts]}")
        logger.debug(f"Using purchaser identifier: {self.identifier_from_purchaser}")

    async def create_payment_request(self, metadata: Optional[str] = None) -> Dict[str, Any]:
        """
        Create a new payment request.
        
        Creates a payment request with the specified amounts and adds the payment ID
        to the tracking set. The payment deadline is automatically set to 12 hours
        from creation.
        
        Args:
            metadata (str, optional): Private metadata to be stored with the payment request
        
        Returns:
            Dict[str, Any]: Response from the payment service containing payment details
                and the time values (submitResultTime, unlockTime, externalDisputeUnlockTime)
            
        Raises:
            ValueError: If the request is invalid
            Exception: If there's a network or server error
        """
        logger.info(f"Creating new payment request for agent {self.agent_identifier}")
        
        # Set payByTime to 12 hours from now
        pay_by_time = datetime.now(timezone.utc) + timedelta(hours=12)
        pay_by_time_str = pay_by_time.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"
        
        # Set submitResultTime to 24 hours from now (after payByTime)
        submit_result_time = datetime.now(timezone.utc) + timedelta(hours=24)
        submit_result_time_str = submit_result_time.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"
        
        logger.debug(f"Payment deadline (payByTime) set to {pay_by_time_str}")
        logger.debug(f"Submit result deadline set to {submit_result_time_str}")

        payload = {
            "agentIdentifier": self.agent_identifier,
            "network": self.network,
            "paymentType": self.payment_type,
            "payByTime": pay_by_time_str,
            "submitResultTime": submit_result_time_str,
            "identifierFromPurchaser": self.identifier_from_purchaser
        }

        # Add input hash to payload if available
        if self.input_hash:
            payload["inputHash"] = self.input_hash

        # Add metadata if provided
        if metadata:
            payload["metadata"] = metadata

        logger.info(f"Payment request payload prepared: {payload}")

        try:
            async with aiohttp.ClientSession() as session:
                logger.debug("Sending payment request to API")
                async with session.post(
                    f"{self.config.payment_service_url}/payment/",
                    headers=self._headers,
                    json=payload
                ) as response:
                    if response.status == 400:
                        error_text = await response.text()
                        logger.error(f"Bad request error: {error_text}")
                        raise ValueError(f"Bad request: {error_text}")
                    if response.status == 401:
                        logger.error("Unauthorized: Invalid API key")
                        raise ValueError("Unauthorized: Invalid API key")
                    if response.status == 500:
                        logger.error("Internal server error from payment service")
                        raise Exception("Internal server error")
                    if response.status != 200:
                        error_text = await response.text()
                        logger.error(f"Payment request failed with status {response.status}: {error_text}")
                        raise Exception(f"Payment request failed: {error_text}")
                    
                    result = await response.json()
                    new_payment_id = result["data"]["blockchainIdentifier"]
                    self.payment_ids.add(new_payment_id)
                    
                    # Extract time values from the response
                    time_values = {
                        "payByTime": result["data"]["payByTime"],
                        "submitResultTime": result["data"]["submitResultTime"],
                        "unlockTime": result["data"]["unlockTime"],
                        "externalDisputeUnlockTime": result["data"]["externalDisputeUnlockTime"]
                    }
                    
                    # Add time values to the result for easy access
                    result["time_values"] = time_values
                    
                    #logger.info(f"Payment request created successfully. Payment ID: {new_payment_id}")
                    logger.debug(f"Time values: {time_values}")
                    logger.debug(f"Full payment response: {result}")
                    return result
        except aiohttp.ClientError as e:
            logger.error(f"Network error during payment request: {str(e)}")
            raise

    async def check_payment_status(self, limit: int = 100) -> Dict[str, Any]:
        """
        Check the status of all tracked payments with pagination support.
        
        Args:
            limit (int, optional): Number of payments to return per page. Defaults to 100.
            
        Returns:
            Dict[str, Any]: Response containing all payment statuses (paginated results combined)
            
        Raises:
            ValueError: If no payment IDs available
            Exception: If status check fails
        """
        if not self.payment_ids:
            logger.warning("Attempted to check payment status with no payment IDs")
            # Instead of raising an error, return an empty response structure
            return {
                "status": "success",
                "data": {
                    "Payments": []
                }
            }

        logger.debug(f"Checking status for payment IDs: {self.payment_ids}")
        
        all_payments = []
        cursor_id = None
        
        try:
            async with aiohttp.ClientSession() as session:
                while True:
                    # Build query parameters
                    params = {
                        'network': self.network,
                        'limit': limit
                    }
                    
                    # Add cursor for pagination if we have one
                    if cursor_id:
                        params['cursorId'] = cursor_id
                    
                    async with session.get(
                        f"{self.config.payment_service_url}/payment/",
                        headers=self._headers,
                        params=params
                    ) as response:
                        if response.status != 200:
                            error_text = await response.text()
                            logger.error(f"Status check failed: {error_text}")
                            raise Exception(f"Status check failed: {error_text}")
                        
                        result = await response.json()
                        logger.debug(f"Received status response page with cursor: {cursor_id}")
                        
                        # Extract payments from this page
                        payments = result.get("data", {}).get("Payments", [])
                        all_payments.extend(payments)
                        
                        # Check if there's a next page
                        cursor_id = result.get("data", {}).get("cursorId")
                        if not cursor_id or len(payments) < limit:
                            # No more pages
                            break
                
                # Return combined result
                combined_result = {
                    "status": "success",
                    "data": {
                        "Payments": all_payments
                    }
                }
                
                logger.debug(f"Retrieved {len(all_payments)} total payments across all pages")
                return combined_result
                
        except aiohttp.ClientError as e:
            logger.error(f"Network error during status check: {str(e)}")
            raise

    async def complete_payment(self, blockchain_identifier: str, job_output: str) -> Dict[str, Any]:
        """
        Complete a payment by submitting the result hash.
        
        Args:
            blockchain_identifier (str): The blockchain identifier of the payment to complete
            job_output (str): The raw output string produced by the job
            
        Returns:
            Dict[str, Any]: Response from the payment service
            
        Raises:
            ValueError: If the request is invalid
            Exception: If there's a network or server error
        """
        #logger.info(f"Completing payment with blockchain identifier: {blockchain_identifier}")
        
        if not isinstance(job_output, str):
            raise TypeError("job_output must be a string")

        result_hash = create_masumi_output_hash(
            job_output,
            self.identifier_from_purchaser
        )

        # Create the payload for the submit-result endpoint
        payload = {
            "network": self.network,
            "blockchainIdentifier": blockchain_identifier,
            "submitResultHash": result_hash
        }
        
        logger.debug(f"Payment completion payload: {payload}")
        
        try:
            async with aiohttp.ClientSession() as session:
                logger.debug("Sending payment completion request to API")
                async with session.post(
                    f"{self.config.payment_service_url}/payment/submit-result",
                    headers=self._headers,
                    json=payload
                ) as response:
                    if response.status == 400:
                        error_text = await response.text()
                        logger.error(f"Bad request error: {error_text}")
                        raise ValueError(f"Bad request: {error_text}")
                    if response.status == 401:
                        logger.error("Unauthorized: Invalid API key")
                        raise ValueError("Unauthorized: Invalid API key")
                    if response.status == 500:
                        logger.error("Internal server error from payment service")
                        raise Exception("Internal server error")
                    if response.status != 200:
                        error_text = await response.text()
                        logger.error(f"Payment completion failed with status {response.status}: {error_text}")
                        raise Exception(f"Payment completion failed: {error_text}")
                    
                    result = await response.json()
                    logger.info(f"Payment completion request successful for {blockchain_identifier}")
                    logger.debug(f"Payment completion response: {result}")
                    return result
        except aiohttp.ClientError as e:
            logger.error(f"Network error during payment completion: {str(e)}")
            raise

    async def start_status_monitoring(self, callback=None, interval_seconds: int = 60) -> None:
        """
        Start monitoring payment status at regular intervals.
        
        Args:
            callback (Callable[[str], None], optional): Function to call when a payment is completed.
                The function will receive the payment_id as its parameter.
            interval_seconds (int, optional): Interval between status checks in seconds. 
                                             Defaults to 60.
        """
        if self._status_check_task is not None:
            logger.warning("Status monitoring already running, stopping previous task")
            self.stop_status_monitoring()
        
        logger.info(f"Starting payment status monitoring with {interval_seconds} second interval")
        
        async def monitor_task():
            logger.info("Payment status monitoring task started")
            while True:
                try:
                    logger.info(f"Checking payment status for {len(self.payment_ids)} payments")
                    if not self.payment_ids:
                        logger.warning("No payment IDs to monitor, waiting for next interval")
                    else:
                        result = await self.check_payment_status()
                        payments = result.get("data", {}).get("Payments", [])
                        logger.info(f"Status check completed, found {len(payments)} payments")
                        
                        # Process each payment in the response
                        for payment in payments:
                            payment_id = payment.get("blockchainIdentifier")
                            if payment_id in self.payment_ids:
                                on_chain_state = payment.get("onChainState")
                                next_action = payment.get("NextAction", {}).get("requestedAction")
                                logger.info(f"Payment {payment_id}: onChainState={on_chain_state}, NextAction={next_action}")
                                
                                # Check if payment is completed - either by onChainState or NextAction
                                if (on_chain_state == "FundsLocked" or 
                                    on_chain_state == "Complete" or
                                    next_action == "PaymentComplete" or 
                                    next_action == "None"):
                                    
                                    logger.info(f"Payment {payment_id} completed, removing from tracking")
                                    self.payment_ids.remove(payment_id)
                                    
                                    # Call the callback function if provided
                                    if callback:
                                        try:
                                            logger.info(f"Calling callback function for payment {payment_id}")
                                            if asyncio.iscoroutinefunction(callback):
                                                await callback(payment_id)
                                            else:
                                                callback(payment_id)
                                        except Exception as e:
                                            logger.error(f"Error in callback function: {str(e)}")
                
                    # If no more payments to monitor, exit the loop
                    if not self.payment_ids:
                        logger.info("No more payments to monitor, stopping monitoring task")
                        return
                    
                    # Wait for the next interval
                    logger.info(f"Waiting {interval_seconds} seconds before next status check")
                    await asyncio.sleep(interval_seconds)
                    
                except Exception as e:
                    logger.error(f"Error during status monitoring: {str(e)}")
                    logger.info(f"Will retry in {interval_seconds} seconds")
                    await asyncio.sleep(interval_seconds)
        
        # Create and store the monitoring task
        self._status_check_task = asyncio.create_task(monitor_task())
        logger.debug("Monitoring task created and started")

    def stop_status_monitoring(self) -> None:
        """
        Stop the payment status monitoring.
        
        Cancels the monitoring task if it's running.
        """
        if self._status_check_task:
            logger.info("Stopping payment status monitoring")
            self._status_check_task.cancel()
            self._status_check_task = None
        else:
            logger.debug("No monitoring task to stop")

    async def check_purchase_status(self, purchase_id: str) -> Dict:
        """Check the status of a purchase request"""
        logger.info(f"Checking status for purchase with ID: {purchase_id}")
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.config.payment_service_url}/purchase/{purchase_id}",
                    headers=self._headers
                ) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        logger.error(f"Purchase status check failed: {error_text}")
                        raise ValueError(f"Purchase status check failed: {error_text}")
                    
                    result = await response.json()
                    logger.info("Purchase status check completed successfully")
                    logger.debug(f"Purchase status response: {result}")
                    return result
                
        except aiohttp.ClientError as e:
            logger.error(f"Network error during purchase status check: {str(e)}")
            raise 
    
    async def authorize_refund(self, blockchain_identifier: str) -> Dict:
        """
        Authorize a refund request for a payment.
        
        This method allows the seller to authorize a refund that was requested by the buyer.
        
        Args:
            blockchain_identifier (str): The blockchain identifier of the payment
            
        Returns:
            dict: Response containing the updated payment information with refund authorization
        """
        logger.info(f"Authorizing refund for payment {blockchain_identifier}")
        
        payload = {
            "network": self.network,
            "blockchainIdentifier": blockchain_identifier
        }
        
        logger.debug(f"Authorize refund payload: {payload}")
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.config.payment_service_url}/payment/authorize-refund",
                    headers=self._headers,
                    json=payload
                ) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        logger.error(f"Authorize refund failed: {error_text}")
                        raise ValueError(f"Authorize refund failed: {error_text}")
                    
                    result = await response.json()
                    logger.info("Refund authorized successfully")
                    logger.debug(f"Authorize refund response: {result}")
                    return result
                    
        except aiohttp.ClientError as e:
            logger.error(f"Network error during refund authorization: {str(e)}")
            raise
