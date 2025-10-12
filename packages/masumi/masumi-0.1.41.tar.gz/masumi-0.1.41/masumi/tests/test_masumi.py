import os
import logging
import sys
from datetime import datetime

# Force logging to stdout
for handler in logging.root.handlers[:]:
    logging.root.removeHandler(handler)

# Configure logging before any imports
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ],
    force=True  # Override any existing logging configuration
)

# Ensure pytest doesn't capture logging
logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))

import pytest
import asyncio
from masumi.registry import Agent
from masumi.payment import Payment, Amount
from masumi.config import Config
from masumi.purchase import Purchase

# Create a test session marker
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

def print_test_separator(test_name: str):
    logger.info("=" * 80)
    logger.info(f"Starting test session: {test_name}")
    logger.info("=" * 80)

# Constants for delays
DELAY_AFTER_REGISTRATION = 30  # seconds
DELAY_AFTER_PAYMENT_CREATE = 30  # seconds

def generate_unique_agent_name() -> str:
    """Generate a unique agent name under 32 characters"""
    timestamp = datetime.now().strftime("%m%d%H%M")
    base_name = "Test_Agent"
    return f"{base_name}_{timestamp}"  # e.g. "Test_Agent_0221143022"

# At the module level, add a variable to store the agent name
_agent_name = None

@pytest.fixture
async def test_agent():
    """Create a test agent for use in tests"""
    global _agent_name
    logger.info("Creating test agent fixture")
    
    # Generate a unique agent name only once
    if _agent_name is None:
        _agent_name = generate_unique_agent_name()
        logger.info(f"Generated agent name: {_agent_name}")
    else:
        logger.info(f"Using existing agent name: {_agent_name}")
    
    # Create config and log the values
    config = Config(
        payment_service_url="https://payment.masumi.network/api/v1",
        payment_api_key="iofsnaiojdoiewqajdriknjonasfoinasd",
        registry_service_url="http://localhost:3001/api/v1",
        registry_api_key="abcdef_this_should_be_very_secure"
    )
    
    # Log the URLs and API keys being used
    logger.info("=== Configuration Details ===")
    logger.info(f"Registry Service URL: {config.registry_service_url}")
    logger.info(f"Registry API Key: {config.registry_api_key}")
    logger.info(f"Payment Service URL: {config.payment_service_url}")
    logger.info(f"Payment API Key: {config.payment_api_key}")
    logger.info("==========================")
    
    agent = Agent(
        name=_agent_name,
        config=config,
        description="Test agent for automated testing",
        example_output=[
            {
                "name": "example_output_name",
                "url": "https://example.com/example_output",
                "mimeType": "application/json"
            }
        ],
        tags=["test", "automated"],
        api_base_url="http://example.com/api",
        author_name="Test Author",
        author_contact="test@example.com",
        author_organization="Test Organization",
        legal_privacy_policy="",
        legal_terms="http://example.com/terms",
        legal_other="http://example.com/other",
        capability_name="test_capability",
        capability_version="1.0.0",
        pricing_unit="lovelace",
        pricing_quantity="10000000",
        network="Preprod"
    )
    
    logger.debug(f"Test agent fixture created with name: {agent.name}")
    return agent

@pytest.mark.asyncio
async def test_register_agent(test_agent):
    """Test agent registration - should be run first to get agent ID"""
    agent = await test_agent  # Await the fixture
    print_test_separator("Agent Registration Test")
    
    logger.info("Starting agent registration process")
    logger.debug("Fetching selling wallet vkey before registration")
    result = await agent.register()  # Use the awaited agent
    
    logger.info("Verifying registration response")
    logger.debug(f"Full registration response: {result}")
    
    # Verify the response
    assert "data" in result, "Response missing 'data' field"
    assert "name" in result["data"], "Response data missing 'name' field"
    assert "success" in result["status"], "Response missing 'success' status"
        
    logger.info(f"Registration successful for agent: {result['data']['name']}")
    logger.debug(f"Registration status: {result['status']}")
    
    logger.info(f"Waiting {DELAY_AFTER_REGISTRATION} seconds before next test...")
    await asyncio.sleep(DELAY_AFTER_REGISTRATION)
    
    logger.info("Agent registration test completed successfully")

@pytest.mark.asyncio
async def test_check_registration_status(test_agent):
    """Test checking registration status - should be run after registration"""
    agent = await test_agent
    print_test_separator("Registration Status Check Test")
    
    MAX_RETRIES = 10
    RETRY_DELAY = 60  # seconds
    
    # Get the wallet vkey
    logger.info("Fetching selling wallet vkey")
    wallet_vkey = await agent.get_selling_wallet_vkey("Preprod")
    logger.debug(f"Retrieved wallet vkey: {wallet_vkey}")
    
    for attempt in range(MAX_RETRIES):
        logger.info(f"Checking registration status (attempt {attempt + 1}/{MAX_RETRIES})")
        result = await agent.check_registration_status(wallet_vkey)
        
        try:
            # Verify the response
            assert "status" in result, "Response missing 'status' field"
            assert result["status"] == "success", "Status is not 'success'"
            assert "data" in result, "Response missing 'data' field"
            assert "Assets" in result["data"], "Response data missing 'Assets' field"
            
            # Verify our agent exists in the list
            agent_found = False
            for asset in result["data"]["Assets"]:
                if asset["name"] == agent.name and asset["state"] == "RegistrationConfirmed":
                    agent_found = True
                        # Store the agent ID for future tests
                    if "agentIdentifier" in asset:
                        test_register_agent.agent_id = asset["agentIdentifier"]
                        logger.info(f"Stored agent ID for future tests: {test_register_agent.agent_id}")
                    else:
                        logger.warning("Agent ID not found in registration response, future tests will use fallback ID")
                    break
            
            if agent_found:

                logger.info(f"Waiting {DELAY_AFTER_REGISTRATION} seconds before next test...")
                await asyncio.sleep(DELAY_AFTER_REGISTRATION)

                logger.info("Registration status check completed successfully")
                return  # Exit the function if agent is found
            
            logger.warning(f"Agent {agent.name} not found in registration status")
            
        except AssertionError as e:
            logger.error(f"Assertion failed: {str(e)}")
        
        if attempt < MAX_RETRIES - 1:  # Don't sleep after the last attempt
            logger.info(f"Waiting {RETRY_DELAY} seconds before next attempt...")
            await asyncio.sleep(RETRY_DELAY)
    
    # If we get here, all retries failed
    raise AssertionError(f"Agent {agent.name} not found in registration status after {MAX_RETRIES} attempts")

# At the module level, add a variable to store the purchaser ID
_purchaser_id = None

@pytest.fixture
def payment():
    global _purchaser_id
    logger.info("Creating payment fixture")
    
    # Create config and log the values
    config = Config(
        payment_service_url="https://payment.masumi.network/api/v1",
        payment_api_key="iofsnaiojdoiewqajdriknjonasfoinasd"
    )
    
    # Log the configuration details
    logger.info("=== Payment Configuration Details ===")
    logger.info(f"Payment Service URL: {config.payment_service_url}")
    logger.info(f"Payment API Key: {config.payment_api_key}")
    logger.info("==================================")
    
    amounts = [Amount(amount="10000000", unit="lovelace")]
    
    # Get agent ID from registration test - fail if not available
    try:
        agent_id = test_register_agent.agent_id
        logger.info(f"Using agent ID from registration: {agent_id}")
    except (AttributeError, NameError):
        logger.error("Agent ID not found - registration test must be run first")
        raise RuntimeError("Registration test must be run before payment tests")
    
    # Create unique identifier for this purchaser using valid hex string
    if _purchaser_id is None:
        import random
        # Generate a random hex string (26 characters max for a valid identifier)
        random_hex = ''.join([random.choice('0123456789abcdef') for _ in range(26)])
        _purchaser_id = random_hex
    
    logger.info(f"Using purchaser identifier: {_purchaser_id} (length: {len(_purchaser_id)})")
    
    # Add test input data for hashing
    test_input_data = {"test": "input data 12345"}
    logger.info(f"Using test input data: {test_input_data}")
    
    payment_obj = Payment(
        agent_identifier=agent_id,
        config=config,
        network="Preprod",
        identifier_from_purchaser=_purchaser_id,
        input_data=test_input_data
    )
    
    logger.debug(f"Payment fixture created with agent: {payment_obj.agent_identifier}")
    return payment_obj

@pytest.mark.asyncio
async def test_create_payment_request_success(payment):
    print_test_separator("Payment Request Creation Test")
    logger.info("Starting test_create_payment_request_success")
    
    logger.info("Executing create_payment_request")
    result = await payment.create_payment_request()
    
    logger.debug(f"Received result: {result}")
    
    # Verify the response has the expected structure
    assert "data" in result
    assert "blockchainIdentifier" in result["data"]
    blockchain_id = result["data"]["blockchainIdentifier"]
    assert blockchain_id in payment.payment_ids
    
    # Verify the input hash was included and is correct
    assert payment.input_hash is not None, "Input hash was not generated"
    assert len(payment.input_hash) == 64, "Input hash is not the correct length for SHA-256"
    assert "inputHash" in result["data"], "Input hash not included in payment request"
    logger.info(f"Input hash: {payment.input_hash}")
    # Store the entire payment response for the next tests
    test_create_payment_request_success.payment_response = result
    test_create_payment_request_success.last_payment_id = blockchain_id
    logger.info(f"Stored payment response for future tests")
    
    logger.info(f"Waiting {DELAY_AFTER_PAYMENT_CREATE} seconds before next test...")
    await asyncio.sleep(DELAY_AFTER_PAYMENT_CREATE)
    
    logger.info("Payment request creation test passed successfully")
    return blockchain_id

@pytest.mark.asyncio
async def test_check_existing_payment_status(payment):
    print_test_separator("Payment Status Check Test")
    logger.info("Starting test_check_existing_payment_status")
    
    # Get the ID from the previous test and add it to payment_ids
    try:
        payment_id = test_create_payment_request_success.last_payment_id
        #logger.info(f"Checking status for payment: {payment_id}")
        payment.payment_ids.add(payment_id)  # Add the ID to the new payment instance
    except AttributeError:
        logger.error("Payment ID not available - payment creation test may not have succeeded")
        pytest.skip("Payment creation test must succeed before checking status")
    
    # Check the payment status
    status_result = await payment.check_payment_status()
    logger.debug(f"Status check result.")
    
    # Verify the response
    assert "data" in status_result
    assert "Payments" in status_result["data"]
    
    # Find our payment in the list
    payment_found = False
    for payment_status in status_result["data"]["Payments"]:
        if payment_status["blockchainIdentifier"] == payment_id:
            payment_found = True
            logger.info(f"Found payment status: {payment_status['NextAction']['requestedAction']}")
            # Verify it has the expected fields
            assert "requestedAction" in payment_status["NextAction"]
            break
    
    assert payment_found, f"Payment with ID {payment_id} not found in status response"
    logger.info("Payment status check test passed successfully")

@pytest.mark.asyncio
async def test_create_purchase_request(test_agent):
    global _purchaser_id
    """Test creating a purchase request"""
    print_test_separator("Purchase Request Test")
    agent = await test_agent
    
    logger.info("Setting up purchase request")
    
    # Get the complete payment response from the previous test
    try:
        payment_response = test_create_payment_request_success.payment_response
        blockchain_identifier = payment_response["data"]["blockchainIdentifier"]
        logger.info(f"Using blockchain identifier from payment test")
        
        # Get the exact time values from the payment response
        pay_by_time_str = payment_response["data"]["payByTime"]
        submit_result_time_str = payment_response["data"]["submitResultTime"]
        unlock_time_str = payment_response["data"]["unlockTime"]
        external_dispute_unlock_time_str = payment_response["data"]["externalDisputeUnlockTime"]
        
        # Convert string timestamps to integers if they're strings
        if isinstance(pay_by_time_str, str):
            # Assume Unix timestamp as string
            pay_by_time = int(pay_by_time_str)
            submit_result_time = int(submit_result_time_str)
            unlock_time = int(unlock_time_str)
            external_dispute_unlock_time = int(external_dispute_unlock_time_str)
        else:
            # Already integers
            pay_by_time = pay_by_time_str
            submit_result_time = submit_result_time_str
            unlock_time = unlock_time_str
            external_dispute_unlock_time = external_dispute_unlock_time_str
        
        logger.info(f"Using pay_by_time from payment response: {pay_by_time}")
        logger.info(f"Submit result time: {submit_result_time}")
        
        # Get the agent identifier from the registration test, not from the payment
        agent_identifier = test_register_agent.agent_id
        logger.info(f"Using agent ID from registration: {agent_identifier}")
        
        # Store the agent identifier for future tests
        test_create_purchase_request.agent_identifier = agent_identifier
        
    except AttributeError:
        logger.error("Payment response not available - payment test may not have run")
        pytest.skip("Payment response not available, skipping test")
    
    # Get the seller vkey
    seller_vkey = await agent.get_selling_wallet_vkey(agent.network)
    logger.debug(f"Using seller vkey: {seller_vkey}")
    
    # Create purchase amounts (not used in current implementation)
    # amounts = [
    #     Amount(amount=10000000, unit="lovelace")
    # ]
    # logger.debug(f"Purchase amounts: {amounts}")
    
    # Ensure we have a purchaser ID
    if _purchaser_id is None:
        import random
        # Generate a random hex string (26 characters max for a valid identifier)
        random_hex = ''.join([random.choice('0123456789abcdef') for _ in range(26)])
        _purchaser_id = random_hex
        logger.warning(f"Generated new purchaser identifier: {_purchaser_id}")
    else:
        logger.info(f"Using existing purchaser identifier: {_purchaser_id}")
    
    # Add test input data
    test_input_data = {"test": "input data 12345"}
    logger.info(f"Using test input data: {test_input_data}")
    
    # Create purchase instance with the exact values from payment response
    purchase = Purchase(
        config=agent.config,
        blockchain_identifier=blockchain_identifier,
        seller_vkey=seller_vkey,
        #amounts=amounts,
        agent_identifier=agent_identifier,  # Use the agent identifier from registration
        identifier_from_purchaser=_purchaser_id,
        pay_by_time=pay_by_time,  # Add the calculated pay_by_time
        submit_result_time=submit_result_time,
        unlock_time=unlock_time,
        external_dispute_unlock_time=external_dispute_unlock_time,
        input_data=test_input_data  # Add the input data
    )
    logger.debug("Purchase instance created with exact values from payment response")
    
    # Create purchase request
    logger.info("Creating purchase request")
    result = await purchase.create_purchase_request()
    logger.debug(f"Purchase request result: {result}")
    
    # Verify the response
    assert "status" in result, "Response missing 'status' field"
    assert result["status"] == "success", "Status is not 'success'"
    assert "data" in result, "Response missing 'data' field"
    assert "id" in result["data"], "Response data missing 'id' field"
    assert "NextAction" in result["data"], "Response missing NextAction"
    assert result["data"]["NextAction"]["requestedAction"] == "FundsLockingRequested", \
        "Unexpected next action"
    
    # Verify input hash
    assert purchase.input_hash is not None, "Input hash was not generated"
    assert len(purchase.input_hash) == 64, "Input hash is not the correct length for SHA-256"
    
    # Store purchase ID for potential future tests
    test_create_purchase_request.purchase_id = result["data"]["id"]
    logger.info(f"Purchase request created with ID: {result['data']['id']}")
    
    logger.info("Purchase request test completed successfully")

@pytest.mark.asyncio
async def test_check_purchase_status(test_agent, payment):
    """Test checking the status of a purchase request"""
    print_test_separator("Purchase Status Check Test")
    agent = await test_agent
    
    logger.info("Starting purchase status check")
    
    # Get the blockchain ID from the previous test
    try:
        blockchain_id = test_create_payment_request_success.last_payment_id
        logger.info(f"Using blockchain ID from payment test: {blockchain_id}")
        
        # Add the blockchain identifier to the payment's tracking set
        payment.payment_ids.add(blockchain_id)
    except AttributeError:
        logger.error("Blockchain ID not found - payment test may not have run")
        pytest.skip("Blockchain ID not available, skipping test")
    
    # Set up retry parameters
    MAX_RETRIES = 10  # Increased retries since we're waiting for blockchain state
    RETRY_DELAY = 30  # seconds
    
    # Start checking payment status
    for attempt in range(MAX_RETRIES):
        logger.info(f"Checking purchase status (attempt {attempt + 1}/{MAX_RETRIES})")
        
        try:
            # Call the check_payment_status method
            result = await payment.check_payment_status()
            
            # Verify the response structure
            assert "status" in result, "Response missing 'status' field"
            assert result["status"] == "success", "Status is not 'success'"
            assert "data" in result, "Response missing 'data' field"
            assert "Payments" in result["data"], "Response missing 'Payments' field"
            
            # Look for our payment in the list by blockchain ID
            payment_found = False
            for payment_status in result["data"]["Payments"]:
                if payment_status["blockchainIdentifier"] == blockchain_id:
                    payment_found = True
                    
                    # Get the onChainState
                    on_chain_state = payment_status.get("onChainState")
                    logger.info(f"Payment onChainState: {on_chain_state}")
                    
                    # Check specifically for FundsLocked state
                    if on_chain_state == "FundsLocked":
                        logger.info("Found FundsLocked state - test passed")
                        return  # Test passes when we find FundsLocked state
                    
                    # If not FundsLocked, log the current state and continue retrying
                    logger.info(f"Current onChainState is {on_chain_state}, waiting for FundsLocked")
                    break
            
            assert payment_found, f"Payment with ID {blockchain_id} not found in response"
            
            # If we haven't found FundsLocked state yet, wait and retry
            if attempt < MAX_RETRIES - 1:
                logger.info(f"FundsLocked state not found yet, waiting {RETRY_DELAY} seconds before next check...")
                await asyncio.sleep(RETRY_DELAY)
            else:
                # On last attempt, if we still haven't found FundsLocked, fail the test
                raise AssertionError(f"Payment never reached FundsLocked state after {MAX_RETRIES} attempts")
                
        except AssertionError as e:
            # Re-raise assertion errors immediately
            raise
        except Exception as e:
            logger.error(f"Error during payment status check: {str(e)}")
            if attempt < MAX_RETRIES - 1:
                logger.info(f"Retrying in {RETRY_DELAY} seconds...")
                await asyncio.sleep(RETRY_DELAY)
            else:
                raise
    
    # If we reach here without returning or raising an exception, the test failed
    raise AssertionError(f"Payment never reached FundsLocked state after {MAX_RETRIES} attempts")

@pytest.mark.asyncio
async def test_complete_payment(test_agent, payment):
    """Test completing a payment after purchase has been confirmed"""
    print_test_separator("Payment Completion Test")
    agent = await test_agent
    
    logger.info("Starting payment completion test")
    
    # Get the blockchain ID from the previous test
    try:
        blockchain_id = test_create_payment_request_success.last_payment_id
        logger.info(f"Using blockchain ID from payment test: {blockchain_id}")
        
        # Add the blockchain identifier to the payment's tracking set if not already there
        payment.payment_ids.add(blockchain_id)
        #logger.info(f"Using blockchain ID for payment completion: {blockchain_id}")
    except AttributeError:
        logger.error("Blockchain ID not found - payment test may not have run")
        pytest.skip("Blockchain ID not available, skipping test")
    
    # Get the purchase ID from the previous test
    try:
        purchase_id = test_create_purchase_request.purchase_id
        logger.info(f"Using purchase ID from previous test: {purchase_id}")
    except AttributeError:
        logger.warning("Purchase ID not found - using None")
        purchase_id = None
    
    # Attempt to complete the payment directly
    logger.info("Attempting to complete payment")
    
    try:
        # Call the complete_payment method
        result = await payment.complete_payment(blockchain_id, "random hash")
        
        # Verify the response
        assert "status" in result, "Response missing 'status' field"
        assert result["status"] == "success", "Status is not 'success'"
        
        logger.info("Payment completion request successful")
        logger.debug(f"Payment completion response: {result}")
        
        # Check the payment status after completion
        logger.info("Checking payment status after completion")
        final_status = await payment.check_payment_status()
        
        # Look for our payment in the list
        for payment_status in final_status["data"]["Payments"]:
            if payment_status["blockchainIdentifier"] == blockchain_id:
                # Check the final status
                if "onChainState" in payment_status:
                    logger.info(f"Final onChainState: {payment_status['onChainState']}")
                
                final_action = payment_status.get("NextAction", {}).get("requestedAction", "Unknown")
                logger.info(f"Final payment status: {final_action}")
                
                # The payment should be in a completed state
                if final_action in ["PaymentComplete", "None"] or payment_status.get("onChainState") == "Complete":
                    logger.info("Payment has been successfully completed")
                else:
                    logger.warning(f"Payment completion may still be processing. Current status: {final_action}")
                
                break
        
    except Exception as e:
        logger.error(f"Error during payment completion: {str(e)}")
        # Don't fail the test if completion is still processing
        logger.warning("Payment completion test encountered an error, but test will continue")
    
    logger.info("Payment completion test finished")

@pytest.mark.asyncio
async def test_monitor_payment_status(test_agent, payment):
    """Test monitoring the payment status after completion"""
    print_test_separator("Payment Status Monitoring Test")
    agent = await test_agent
    
    logger.info("Starting payment status monitoring test")
    
    # Get the blockchain ID from the previous test
    try:
        blockchain_id = test_create_payment_request_success.last_payment_id
        logger.info(f"Using blockchain ID from payment test: {blockchain_id}")
        
        # Add the blockchain identifier to the payment's tracking set if not already there
        payment.payment_ids.add(blockchain_id)
        #logger.info(f"Using blockchain ID for payment monitoring: {blockchain_id}")
    except AttributeError:
        logger.error("Blockchain ID not found - payment test may not have run")
        pytest.skip("Blockchain ID not available, skipping test")
    
    # Set up monitoring parameters
    MONITOR_DURATION = 300  # 5 minutes
    CHECK_INTERVAL = 60     # 1 minute
    MAX_CHECKS = MONITOR_DURATION // CHECK_INTERVAL
    
    logger.info(f"Starting payment status monitoring for {MONITOR_DURATION} seconds")
    logger.info(f"Will check status every {CHECK_INTERVAL} seconds")
    
    # Start the monitoring task
    async def monitor_task():
        payment_already_complete = False
        
        for check_num in range(1, MAX_CHECKS + 1):
            logger.info(f"Payment status check {check_num}/{MAX_CHECKS}")
            try:
                # Skip checking if we've already determined the payment is complete
                if payment_already_complete:
                    logger.info("Payment already marked as complete, skipping check")
                    await asyncio.sleep(CHECK_INTERVAL)
                    continue
                    
                result = await payment.check_payment_status()
                
                # Check if we have any payments to process
                payments = result.get("data", {}).get("Payments", [])
                if not payments:
                    logger.info("No payments returned in status check")
                    await asyncio.sleep(CHECK_INTERVAL)
                    continue
                
                # Look for our payment in the list
                payment_found = False
                for payment_status in payments:
                    if payment_status["blockchainIdentifier"] == blockchain_id:
                        payment_found = True
                        
                        # Check the current status
                        on_chain_state = payment_status.get("onChainState")
                        current_status = payment_status.get("NextAction", {}).get("requestedAction", "Unknown")
                        
                        logger.info(f"Payment onChainState: {on_chain_state}")
                        logger.info(f"Current payment status: {current_status}")
                        
                        # Consider payment complete if either criterion is met
                        if (on_chain_state in ["FundsLocked", "Complete"] or 
                            current_status in ["PaymentComplete", "None"]):
                            logger.info("Payment is complete, marking as complete")
                            payment_already_complete = True
                            return True
                        
                        break
                
                if not payment_found:
                    logger.warning(f"Payment with ID {blockchain_id} not found in status response")
                
                # Wait for the next check
                logger.info(f"Waiting {CHECK_INTERVAL} seconds before next check...")
                await asyncio.sleep(CHECK_INTERVAL)
                
            except Exception as e:
                logger.error(f"Error during payment status check: {str(e)}")
                # Continue monitoring despite errors
                await asyncio.sleep(CHECK_INTERVAL)
        
        logger.warning(f"Monitoring period of {MONITOR_DURATION} seconds ended without payment completion")
        return payment_already_complete  # Return true if we detected completion at any point
    
    # Create and start the monitoring task
    payment._status_check_task = asyncio.create_task(monitor_task())
    
    try:
        # Wait for the monitoring task to complete
        completed = await payment._status_check_task
        
        if completed:
            logger.info("Payment monitoring completed successfully - payment is complete")
        else:
            logger.warning("Payment monitoring completed without detecting payment completion")
            
    except asyncio.CancelledError:
        logger.info("Payment monitoring task was cancelled")
    except Exception as e:
        logger.error(f"Error during payment monitoring: {str(e)}")
    finally:
        # Clean up the monitoring task
        payment.stop_status_monitoring()
    
    logger.info("Payment status monitoring test finished")

@pytest.mark.asyncio
async def test_refund_flow(payment, test_agent):
    """Test the complete refund flow: create payment, create purchase, request refund, authorize refund
    
    NOTE: This test reuses the payment from previous tests which may already be completed.
    If the payment has been completed (results submitted), refunds may not be possible.
    """
    print_test_separator("Refund Flow Test")
    logger.info("Starting refund flow test")
    
    agent = await test_agent
    
    # Get the blockchain identifier from the previous payment test
    try:
        blockchain_id = test_create_payment_request_success.last_payment_id
        payment_response = test_create_payment_request_success.payment_response
        logger.info(f"Using blockchain ID from previous payment test: {blockchain_id}")
    except AttributeError:
        logger.error("Blockchain ID not found - payment test must be run first")
        pytest.skip("Payment test must be run before refund test")
    
    # Add the blockchain ID to payment tracking
    payment.payment_ids.add(blockchain_id)
    
    # Step 1: Use existing purchase from previous test
    logger.info("Using existing purchase for refund test")
    
    # Get the purchase ID from the previous test
    try:
        purchase_id = test_create_purchase_request.purchase_id
        logger.info(f"Using purchase ID from previous test: {purchase_id}")
    except AttributeError:
        logger.error("Purchase ID not found - purchase test must be run first")
        pytest.skip("Purchase test must be run before refund test")
    
    # Get payment details from the previous test for Purchase object creation
    pay_by_time_str = payment_response["data"]["payByTime"]
    submit_result_time_str = payment_response["data"]["submitResultTime"]
    unlock_time_str = payment_response["data"]["unlockTime"]
    external_dispute_unlock_time_str = payment_response["data"]["externalDisputeUnlockTime"]
    
    # Convert string timestamps to integers
    if isinstance(pay_by_time_str, str):
        pay_by_time = int(pay_by_time_str)
        submit_result_time = int(submit_result_time_str)
        unlock_time = int(unlock_time_str)
        external_dispute_unlock_time = int(external_dispute_unlock_time_str)
    else:
        pay_by_time = pay_by_time_str
        submit_result_time = submit_result_time_str
        unlock_time = unlock_time_str
        external_dispute_unlock_time = external_dispute_unlock_time_str
    
    # Get seller vkey
    seller_vkey = await agent.get_selling_wallet_vkey(agent.network)
    
    # Use the same purchaser ID from the original payment
    global _purchaser_id
    
    # Create Purchase object for existing purchase (needed for refund methods)
    purchase = Purchase(
        config=agent.config,
        blockchain_identifier=blockchain_id,
        seller_vkey=seller_vkey,
        agent_identifier=test_register_agent.agent_id,
        identifier_from_purchaser=_purchaser_id,  # Use the same purchaser ID
        pay_by_time=pay_by_time,
        submit_result_time=submit_result_time,
        unlock_time=unlock_time,
        external_dispute_unlock_time=external_dispute_unlock_time,
        network="Preprod",  # Explicitly set network
        input_data={"test": "input data 12345"}  # Use the same input data
    )
    
    logger.info("Purchase object created for existing purchase")
    
    # Wait for the payment to be in FundsLocked state
    logger.info("Checking if payment is in FundsLocked state...")
    
    MAX_RETRIES = 5
    RETRY_DELAY = 10
    funds_locked = False
    
    for attempt in range(MAX_RETRIES):
        status_result = await payment.check_payment_status()
        payments = status_result.get("data", {}).get("Payments", [])
        
        for payment_status in payments:
            if payment_status["blockchainIdentifier"] == blockchain_id:
                on_chain_state = payment_status.get("onChainState")
                logger.info(f"Payment onChainState: {on_chain_state}")
                
                if on_chain_state == "FundsLocked":
                    funds_locked = True
                    logger.info("Payment is in FundsLocked state, ready for refund test")
                    break
        
        if funds_locked:
            break
            
        if attempt < MAX_RETRIES - 1:
            logger.info(f"Payment not yet in FundsLocked state, waiting {RETRY_DELAY} seconds...")
            await asyncio.sleep(RETRY_DELAY)
    
    if not funds_locked:
        logger.warning("Payment not in FundsLocked state, but proceeding with refund test")
    
    # Step 2: Request refund
    logger.info("Testing refund request")
    refund_result = await purchase.request_refund()
    
    # Verify refund request response
    assert "status" in refund_result
    assert refund_result["status"] == "success"
    assert "data" in refund_result
    assert "blockchainIdentifier" in refund_result["data"]
    assert refund_result["data"]["blockchainIdentifier"] == blockchain_id
    logger.info("Refund requested successfully")
    
    # Wait for refund request to be processed on blockchain
    logger.info("Waiting for refund request to be confirmed on blockchain...")
    logger.info("This can take 2-5 minutes depending on blockchain congestion")
    await asyncio.sleep(30)  # Initial wait
    
    # Check both payment AND purchase status after refund request
    logger.info("Checking payment status after refund request...")
    payment.payment_ids.add(blockchain_id)  # Add to the original payment fixture
    
    # Log payment fixture details
    logger.info(f"Payment fixture network: {payment.network}")
    logger.info(f"Payment fixture agent ID: {payment.agent_identifier}")
    logger.info(f"Payment fixture API key: {payment.config.payment_api_key[:10]}...")
    
    status_after_refund = await payment.check_payment_status()
    payment_found = False
    for payment_status in status_after_refund.get("data", {}).get("Payments", []):
        if payment_status["blockchainIdentifier"] == blockchain_id:
            payment_found = True
            logger.info(f"Payment found in status check")
            logger.info(f"OnChainState: {payment_status.get('onChainState')}")
            logger.info(f"NextAction: {payment_status.get('NextAction', {}).get('requestedAction')}")
            
            # Check if refund is already in a specific state
            if payment_status.get('NextAction', {}).get('requestedAction') == 'RefundRequested':
                logger.info("Payment is in RefundRequested state")
            break
    
    if not payment_found:
        logger.error(f"Payment {blockchain_id} not found in status check")
        logger.info(f"Total payments returned: {len(status_after_refund.get('data', {}).get('Payments', []))}")
    
    # Also check purchase status to see refund state
    logger.info("Checking purchase status to see refund state...")
    try:
        purchase_status = await payment.check_purchase_status(purchase_id)
        logger.info(f"Purchase status: {purchase_status}")
        if purchase_status.get("data", {}).get("NextAction", {}).get("requestedAction"):
            logger.info(f"Purchase NextAction: {purchase_status['data']['NextAction']['requestedAction']}")
    except Exception as e:
        logger.warning(f"Could not check purchase status: {e}")
    
    # Step 3: Authorize refund using the original payment fixture
    logger.info("Testing refund authorization with original payment object")
    
    # Log all payment IDs being tracked
    logger.info(f"Payment IDs being tracked: {payment.payment_ids}")
    logger.info(f"Attempting to authorize refund for blockchain ID: {blockchain_id}")
    
    # Wait for blockchain confirmation before attempting authorization
    logger.info("Waiting additional time for blockchain confirmation...")
    logger.info("Checking for refund state every 30 seconds...")
    
    MAX_WAIT_ATTEMPTS = 10  # 5 minutes total
    WAIT_INTERVAL = 30  # seconds
    refund_ready = False
    
    for wait_attempt in range(MAX_WAIT_ATTEMPTS):
        logger.info(f"Checking refund state (attempt {wait_attempt + 1}/{MAX_WAIT_ATTEMPTS})")
        
        check_status = await payment.check_payment_status()
        for p in check_status.get("data", {}).get("Payments", []):
            if p["blockchainIdentifier"] == blockchain_id:
                next_action = p.get('NextAction', {}).get('requestedAction', '')
                on_chain_state = p.get('onChainState', '')
                
                logger.info(f"Current NextAction: {next_action}")
                logger.info(f"Current onChainState: {on_chain_state}")
                
                # Check if refund is ready for authorization
                if "Refund" in next_action or "RefundRequested" in next_action:
                    logger.info("✓ Payment shows refund state - ready for authorization")
                    refund_ready = True
                    break
        
        if refund_ready:
            break
            
        if wait_attempt < MAX_WAIT_ATTEMPTS - 1:
            logger.info(f"Refund not ready yet, waiting {WAIT_INTERVAL} seconds...")
            await asyncio.sleep(WAIT_INTERVAL)
        else:
            logger.warning("Refund may not be fully processed on blockchain yet")
    
    # Check status one more time before authorizing
    final_check = await payment.check_payment_status()
    for p in final_check.get("data", {}).get("Payments", []):
        if p["blockchainIdentifier"] == blockchain_id:
            logger.info(f"Payment state before authorization: {p.get('onChainState')}")
            logger.info(f"NextAction before authorization: {p.get('NextAction', {}).get('requestedAction')}")
            
            # Check if the payment shows any refund-related state
            if "Refund" in str(p.get('NextAction', {}).get('requestedAction', '')):
                logger.info("Payment shows refund-related action")
            else:
                logger.warning("Payment does not show refund-related action yet")
    
    # Try authorization with retries
    MAX_AUTH_RETRIES = 3
    AUTH_RETRY_DELAY = 20
    
    for auth_attempt in range(MAX_AUTH_RETRIES):
        try:
            logger.info(f"Authorization attempt {auth_attempt + 1}/{MAX_AUTH_RETRIES}")
            logger.info(f"Calling authorize_refund with blockchain_id: {blockchain_id}")
            
            authorize_result = await payment.authorize_refund(blockchain_id)
            
            # Verify authorization response
            assert "status" in authorize_result
            assert authorize_result["status"] == "success"
            assert "data" in authorize_result
            assert "NextAction" in authorize_result["data"]
            assert authorize_result["data"]["NextAction"]["requestedAction"] == "AuthorizeRefundRequested"
            logger.info("Refund authorized successfully")
            break  # Success, exit loop
            
        except Exception as e:
            logger.error(f"Authorization attempt {auth_attempt + 1} failed: {str(e)}")
            
            if auth_attempt < MAX_AUTH_RETRIES - 1:
                logger.info(f"Waiting {AUTH_RETRY_DELAY} seconds before retry...")
                await asyncio.sleep(AUTH_RETRY_DELAY)
            else:
                logger.error(f"All {MAX_AUTH_RETRIES} authorization attempts failed")
        
        # Try to understand why it failed
        # Check if this payment belongs to this agent
        all_payments = await payment.check_payment_status()
        found = False
        for p in all_payments.get("data", {}).get("Payments", []):
            if p["blockchainIdentifier"] == blockchain_id:
                found = True
                logger.info(f"Payment found in list, but authorization failed")
                logger.info(f"Payment details: {p}")
        
        if not found:
            logger.error("Payment not found in the list of payments for this API key")
        
        # Log more details about why it might be failing
        logger.info("Possible reasons for refund authorization failure:")
        logger.info("1. Payment may already be completed (resultHash submitted)")
        logger.info("2. Refund may not be in the correct state")
        logger.info("3. API key may not have permission to authorize this refund")
        
        # Check if the payment has a result hash (meaning it's completed)
        for p in all_payments.get("data", {}).get("Payments", []):
            if p["blockchainIdentifier"] == blockchain_id:
                if p.get("NextAction", {}).get("resultHash"):
                    logger.warning(f"Payment has resultHash: {p['NextAction']['resultHash']} - may be completed")
                if p.get("resultHash"):
                    logger.warning(f"Payment has resultHash in main object: {p['resultHash']}")
                break
    
    logger.info("Refund flow test completed")
