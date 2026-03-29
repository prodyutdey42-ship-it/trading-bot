import time
import math
from bot.logging_config import setup_logger
from bot.validators import validate_inputs

logger = setup_logger()

def place_order(client, symbol, side, order_type, quantity, price=None):
    errors = validate_inputs(symbol, side, order_type, quantity, price)
    if errors:
        error_msg = f"Validation failed: {'; '.join(errors)}"
        logger.error(error_msg)
        raise ValueError(error_msg)

    symbol = symbol.strip().upper()
    side = side.strip().upper()
    order_type = order_type.strip().upper()
    quantity = float(quantity)

    order_params = {
        "symbol": symbol,
        "side": side,
        "type": order_type,
        "quantity": quantity,
    }

    if order_type == "LIMIT":
        order_params["price"] = float(price)
        order_params["timeInForce"] = "GTC"

    logger.info(
        f"Placing {order_type} {side} {symbol} | Qty: {quantity}" +
        (f" | Price: {price}" if price else "")
    )

    try:
        response = client.futures_create_order(**order_params)
        logger.info(
            f"Order success | ID: {response.get('orderId')} | "
            f"Status: {response.get('status')}"
        )
        return response

    except Exception as e:
        logger.error(f"Order failed: {e}")
        raise