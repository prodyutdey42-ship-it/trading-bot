import re
from bot.logging_config import setup_logger

logger = setup_logger()


VALID_SIDES = ("BUY", "SELL")
VALID_ORDER_TYPES = ("MARKET", "LIMIT", "STOP", "STOP_MARKET", "TAKE_PROFIT", "TAKE_PROFIT_MARKET")


SYMBOL_PATTERN = re.compile(r"^[A-Z0-9_]{2,20}$")


MAX_QUANTITY = 1_000_000
MAX_PRICE = 10_000_000
MIN_QUANTITY = 1e-8
MIN_PRICE = 1e-8


def validate_inputs(symbol, side, order_type, quantity, price=None):
    """
    Validates trading order inputs before sending to the exchange.

    Args:
        symbol: Trading pair symbol (e.g., "BTCUSDT").
        side: Order side — "BUY" or "SELL".
        order_type: Order type — "MARKET", "LIMIT", etc.
        quantity: Order quantity (str, int, or float).
        price: Order price (required for LIMIT orders, optional otherwise).

    Returns:
        list[str]: List of error messages. Empty list means all inputs are valid.
    """
    errors = []

    
    if symbol is None:
        errors.append("Symbol is required.")
    elif not isinstance(symbol, str):
        errors.append(f"Symbol must be a string, got {type(symbol).__name__}.")
    else:
        symbol_upper = symbol.strip().upper()
        if not symbol_upper:
            errors.append("Symbol cannot be empty.")
        elif not SYMBOL_PATTERN.match(symbol_upper):
            errors.append(
                f"Invalid symbol '{symbol}'. Must be 2-20 alphanumeric "
                f"characters (e.g., BTCUSDT, 1000PEPEUSDT)."
            )

    if side is None:
        errors.append("Side is required.")
    elif not isinstance(side, str):
        errors.append(f"Side must be a string, got {type(side).__name__}.")
    else:
        side_upper = side.strip().upper()
        if side_upper not in VALID_SIDES:
            errors.append(
                f"Invalid side '{side}'. Must be one of: {', '.join(VALID_SIDES)}."
            )

    if order_type is None:
        errors.append("Order type is required.")
    elif not isinstance(order_type, str):
        errors.append(f"Order type must be a string, got {type(order_type).__name__}.")
    else:
        order_type_upper = order_type.strip().upper()
        if order_type_upper not in VALID_ORDER_TYPES:
            errors.append(
                f"Invalid order type '{order_type}'. "
                f"Must be one of: {', '.join(VALID_ORDER_TYPES)}."
            )

    qty = _validate_numeric_field(
        value=quantity,
        field_name="Quantity",
        min_value=MIN_QUANTITY,
        max_value=MAX_QUANTITY,
        required=True,
        errors=errors,
    )

    normalized_order_type = (
        order_type.strip().upper()
        if isinstance(order_type, str) and order_type
        else ""
    )

    price_required = normalized_order_type in ("LIMIT", "STOP", "TAKE_PROFIT")

    if price_required:
        _validate_numeric_field(
            value=price,
            field_name="Price",
            min_value=MIN_PRICE,
            max_value=MAX_PRICE,
            required=True,
            errors=errors,
        )
    elif price is not None:
        
        if normalized_order_type == "MARKET":
            errors.append(
                "Price should not be provided for MARKET orders. "
                "It will be ignored by the exchange."
            )

    
    if errors:
        logger.warning(
            f"Input validation failed for {symbol}/{side}/{order_type}: "
            f"{errors}"
        )
    else:
        logger.debug(
            f"Input validation passed for {symbol}/{side}/{order_type} "
            f"qty={quantity} price={price}"
        )

    return errors


def _validate_numeric_field(value, field_name, min_value, max_value, required, errors):
    """
    Validates a numeric field (quantity or price).

    Args:
        value: The value to validate.
        field_name: Human-readable field name for error messages.
        min_value: Minimum acceptable value (exclusive of zero).
        max_value: Maximum acceptable value (sanity check).
        required: Whether the field is required.
        errors: List to append error messages to.

    Returns:
        float or None: The parsed float value, or None if invalid.
    """

    if value is None:
        if required:
            errors.append(f"{field_name} is required.")
        return None

    try:
        numeric_val = float(value)
    except (ValueError, TypeError):
        errors.append(
            f"{field_name} must be a valid number, got '{value}' "
            f"({type(value).__name__})."
        )
        return None

    import math

    if math.isnan(numeric_val):
        errors.append(f"{field_name} cannot be NaN.")
        return None

    if math.isinf(numeric_val):
        errors.append(f"{field_name} cannot be infinite.")
        return None

    if numeric_val <= 0:
        errors.append(f"{field_name} must be a positive number, got {numeric_val}.")
        return None

    if numeric_val < min_value:
        errors.append(
            f"{field_name} is too small: {numeric_val}. Minimum is {min_value}."
        )
        return None

    if numeric_val > max_value:
        errors.append(
            f"{field_name} is too large: {numeric_val}. Maximum is {max_value}."
        )
        return None

    return numeric_val


def validate_and_normalize(symbol, side, order_type, quantity, price=None):
    """
    Validates AND normalizes inputs, returning clean values ready
    for the exchange API.

    Args:
        symbol: Trading pair symbol.
        side: Order side.
        order_type: Order type.
        quantity: Order quantity.
        price: Order price (optional for MARKET orders).

    Returns:
        tuple: (errors, normalized_params)
            - errors: list of error strings (empty if valid)
            - normalized_params: dict with cleaned values, or None if invalid

    Example:
        >>> errors, params = validate_and_normalize("btcusdt", "buy", "limit", "0.5", "30000")
        >>> if not errors:
        ...     place_order(**params)
    """
    errors = validate_inputs(symbol, side, order_type, quantity, price)

    if errors:
        return errors, None

    normalized = {
        "symbol": symbol.strip().upper(),
        "side": side.strip().upper(),
        "order_type": order_type.strip().upper(),
        "quantity": float(quantity),
    }

    if price is not None:
        normalized["price"] = float(price)

    return errors, normalized


if __name__ == "__main__":
    print("=" * 60)
    print("VALIDATION MODULE SELF-TEST")
    print("=" * 60)

    test_cases = [
        
        ("Valid MARKET order", ("BTCUSDT", "BUY", "MARKET", "0.5", None), True),
        ("Valid LIMIT order", ("BTCUSDT", "SELL", "LIMIT", "1.0", "30000"), True),
        ("Lowercase inputs (should normalize)", ("btcusdt", "buy", "limit", "0.5", "30000"), True),
        ("Numeric symbol like 1000PEPEUSDT", ("1000PEPEUSDT", "BUY", "MARKET", "100", None), True),
        ("Empty symbol", ("", "BUY", "MARKET", "1", None), False),
        ("None symbol", (None, "BUY", "MARKET", "1", None), False),
        ("Invalid side", ("BTCUSDT", "SHORT", "MARKET", "1", None), False),
        ("Invalid order type", ("BTCUSDT", "BUY", "FOK", "1", None), False),
        ("Negative quantity", ("BTCUSDT", "BUY", "MARKET", "-1", None), False),
        ("Zero quantity", ("BTCUSDT", "BUY", "MARKET", "0", None), False),
        ("NaN quantity", ("BTCUSDT", "BUY", "MARKET", float("nan"), None), False),
        ("Inf quantity", ("BTCUSDT", "BUY", "MARKET", float("inf"), None), False),
        ("String quantity", ("BTCUSDT", "BUY", "MARKET", "abc", None), False),
        ("LIMIT without price", ("BTCUSDT", "BUY", "LIMIT", "1", None), False),
        ("LIMIT with negative price", ("BTCUSDT", "BUY", "LIMIT", "1", "-100"), False),
        ("MARKET with price (warning)", ("BTCUSDT", "BUY", "MARKET", "1", "30000"), False),
        ("Excessive quantity", ("BTCUSDT", "BUY", "MARKET", "99999999", None), False),
    ]

    passed = 0
    failed = 0

    for description, inputs, expected_valid in test_cases:
        errors = validate_inputs(*inputs)
        is_valid = len(errors) == 0

        status = "PASS" if is_valid == expected_valid else "FAIL"
        if status == "PASS":
            passed += 1
        else:
            failed += 1

        print(f"  [{status}] {description}")
        if status == "FAIL":
            print(f"         Expected valid={expected_valid}, got valid={is_valid}")
            print(f"         Errors: {errors}")

    print(f"\nResults: {passed}/{passed + failed} passed")
    if failed == 0:
        print("All checks passed ✓")
    else:
        print(f"{failed} test(s) FAILED ✗")