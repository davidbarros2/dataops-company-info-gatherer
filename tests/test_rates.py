# test_rates.py

# Import necessary libraries
from typing import Any  # For type hints
import pytest  # Testing framework
from datetime import datetime  # For working with dates and times
from pydantic import BaseModel, Field, field_validator  # For data validation
import time  # For working with timestamps
import requests  # For making HTTP requests

# Import the function we want to test
from src.webscraping_beautifulsoup import fetch_currency_rates

# Define a Pydantic model for data validation
class CurrencyRate(BaseModel):
    """
    Pydantic model that defines the expected structure and types of our currency rate data.
    This acts as a schema validator for our data.
    """
    timestamp: int  # Unix timestamp
    insert_date: str  # Date string
    from_currency: str = Field(alias='from')  # Original currency (using alias because 'from' is a Python keyword)
    to_currency: str = Field(alias='to')  # Target currency
    rate: float  # Exchange rate
    amount: int  # Amount to convert

    # Validator to ensure rate is positive
    @field_validator('rate')
    @classmethod  # Required for Pydantic v2
    def rate_must_be_positive(cls, v: float) -> float:
        """Check if the exchange rate is greater than zero"""
        if v <= 0:
            raise ValueError('Rate must be greater than zero')
        return v

    # Validator to ensure timestamp is not in the future
    @field_validator('timestamp')
    @classmethod
    def timestamp_must_be_valid(cls, v: int) -> int:
        """Check if the timestamp is not in the future (allowing 1 day buffer)"""
        if v > int(time.time()) + 86400:  # 86400 seconds = 1 day
            raise ValueError('Timestamp cannot be in the future')
        return v

    # Validator to ensure date format is correct
    @field_validator('insert_date')
    @classmethod
    def validate_date_format(cls, v: str) -> str:
        """Check if the date string matches expected format"""
        try:
            datetime.strptime(v, "%Y-%m-%d %H:%M:%S")
        except ValueError:
            raise ValueError('Invalid date format. Expected YYYY-MM-DD HH:MM:SS')
        return v

# Test 1: Verify the data structure
def test_currency_rate_format():
    """
    Test that ensures the API response data matches our expected format.
    This test validates the structure and types of all fields.
    """
    # Fetch real data from the API
    df = fetch_currency_rates('EUR', 'USD')
    
    if df is not None:
        # Convert the first row of DataFrame to a dictionary
        data_dict = df.iloc[0].to_dict()
        try:
            # Try to create a CurrencyRate instance with the data
            # This will automatically validate all fields
            validated_data = CurrencyRate(**data_dict)
            assert True  # If we get here, validation passed
        except Exception as e:
            pytest.fail(f"Data validation failed: {str(e)}")
    else:
        pytest.fail("Failed to fetch currency data")

# Test 2: Verify specific business rules
def test_currency_rate_conditions():
    """
    Test specific business rules about the currency data:
    - Rate must be positive
    - Currency must be USD
    - Timestamp must be valid
    - Date format must be correct
    """
    # Fetch real data
    df = fetch_currency_rates('EUR', 'USD')
    
    if df is not None:
        # Get first row of data
        data = df.iloc[0]
        
        # Check if rate is positive
        assert data['rate'] > 0, "Rate should be greater than zero"
        
        # Check if target currency is USD
        assert data['to'] == 'USD', "Target currency should be USD"
        
        # Check if timestamp is not in future
        current_time = int(time.time())
        assert data['timestamp'] <= current_time, "Timestamp should not be in the future"
        
        # Check if date format is valid
        try:
            datetime.strptime(data['insert_date'], "%Y-%m-%d %H:%M:%S")
        except ValueError:
            pytest.fail("Invalid insert_date format")
    else:
        pytest.fail("Failed to fetch currency data")

# Test 3: Test error handling for connection issues
def test_api_error_handling(mocker):
    """
    Test how the function handles API connection errors.
    Uses pytest-mock to simulate a connection error.
    """
    # Mock requests.get to raise an exception
    mocker.patch('requests.get', side_effect=requests.exceptions.RequestException("Connection error"))
    result = fetch_currency_rates('EUR', 'USD')
    # Function should return None when API call fails
    assert result is None

# Test 4: Test handling of invalid HTML response
def test_api_invalid_response(mocker):
    """
    Test how the function handles invalid HTML responses.
    Creates a mock response with invalid HTML structure.
    """
    # Create a mock response object
    mock_response = mocker.Mock()
    mock_response.text = "<invalid>HTML</invalid>"
    mock_response.raise_for_status.return_value = None
    # Replace requests.get with our mock
    mocker.patch('requests.get', return_value=mock_response)
    
    result = fetch_currency_rates('EUR', 'USD')
    # Function should return None for invalid HTML
    assert result is None

# Test 5: Test handling of invalid currency codes
def test_api_invalid_currencies():
    """
    Test how the function handles invalid currency codes.
    Tries to fetch rates for non-existent currencies.
    """
    # Test with invalid currency codes
    result = fetch_currency_rates('INVALID', 'CURRENCY')
    # Function should return None for invalid currencies
    assert result is None

    