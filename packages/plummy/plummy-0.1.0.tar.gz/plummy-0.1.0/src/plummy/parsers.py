"""
Provides reusable parser functions for common event sources.

This module contains utilities to handle the boilerplate of validating and
extracting data from various event structures (e.g., SQS, API Gateway),
allowing domain-specific handlers to focus on their core logic.
"""
import json
from pydantic import BaseModel, ConfigDict, ValidationError
from typing import List, NamedTuple, Generator, Any, Dict, Optional


# ==============================================================================
# SQS Parser Components
# ==============================================================================

class SQSRecordModel(BaseModel):
    """Represents the expected structure of a single record within an SQS event."""
    model_config = ConfigDict(extra="allow")
    body: str
    eventSourceARN: str


class SQSEventModel(BaseModel):
    """Represents the top-level SQS event containing a list of records."""
    model_config = ConfigDict(extra="allow")
    Records: List[SQSRecordModel]


class ParsedSQSRecord(NamedTuple):
    """A structured representation of a successfully parsed SQS record."""
    source_arn: str
    body: Dict[str, Any]


def parse_sqs_event(data: Dict[str, Any]) -> Generator[ParsedSQSRecord, None, None]:
    """
    Validates and parses a raw SQS event dictionary.

    This function acts as a generator, yielding a `ParsedSQSRecord` for each
    valid record found in the event. It safely handles validation errors,
    ensuring that malformed events or records with invalid JSON bodies are
    gracefully ignored.

    Args:
        data: The raw event data from the Lambda handler.

    Yields:
        A `ParsedSQSRecord` for each valid record, containing the
        source ARN and the deserialized JSON body.
    """
    try:
        event = SQSEventModel.model_validate(data)
        for record in event.Records:
            try:
                parsed_body = json.loads(record.body)
                yield ParsedSQSRecord(
                    source_arn=record.eventSourceARN, body=parsed_body
                )
            except (json.JSONDecodeError, TypeError):
                # Ignore records with malformed JSON bodies.
                continue
    except ValidationError:
        # If the root object is not a valid SQS event, yield nothing.
        return


# ==============================================================================
# API Gateway Parser Components
# ==============================================================================

class APIGatewayEventModel(BaseModel):
    """

    Represents the expected structure of an API Gateway Lambda proxy event.
    """
    model_config = ConfigDict(extra="allow")
    httpMethod: str
    path: str
    body: Optional[str] = None
    headers: Dict[str, str] = {}


class ParsedAPIGatewayRequest(NamedTuple):
    """A structured representation of a successfully parsed API Gateway request."""
    http_method: str
    path: str
    body: Dict[str, Any]
    headers: Dict[str, str]


def parse_api_gateway_event(data: Dict[str, Any]) -> Optional[ParsedAPIGatewayRequest]:
    """
    Validates and parses a raw API Gateway event dictionary.

    This function encapsulates the validation and extraction logic, providing
    a clean, structured `ParsedAPIGatewayRequest` to the calling handler.

    Args:
        data: The raw event data from a Lambda invocation.

    Returns:
        A `ParsedAPIGatewayRequest` if parsing is successful, otherwise `None`.
    """
    try:
        event = APIGatewayEventModel.model_validate(data)
        parsed_body = json.loads(event.body) if event.body else {}
        
        return ParsedAPIGatewayRequest(
            http_method=event.httpMethod,
            path=event.path,
            body=parsed_body,
            headers=event.headers,
        )
    except (ValidationError, json.JSONDecodeError, TypeError):
        # If the event is not a valid API Gateway event or the body is not JSON,
        # return None to indicate it could not be handled.
        return None