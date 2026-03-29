import click
from bot.client import get_client
from bot.orders import place_order
from bot.logging_config import setup_logger

logger = setup_logger()

@click.command()
@click.option("--symbol", required=True, help="Trading pair, e.g. BTCUSDT")
@click.option("--side", required=True, type=click.Choice(["BUY", "SELL"], case_sensitive=False))
@click.option("--type", "order_type", required=True, type=click.Choice(["MARKET", "LIMIT"], case_sensitive=False))
@click.option("--quantity", required=True, help="Order quantity")
@click.option("--price", default=None, help="Price (required for LIMIT orders)")
def main(symbol, side, order_type, quantity, price):
    """Simplified Binance Futures Testnet Trading Bot"""

    click.echo("\n--- Order Request Summary ---")
    click.echo(f"  Symbol   : {symbol.upper()}")
    click.echo(f"  Side     : {side.upper()}")
    click.echo(f"  Type     : {order_type.upper()}")
    click.echo(f"  Quantity : {quantity}")
    if price:
        click.echo(f"  Price    : {price}")
    click.echo("-----------------------------\n")

    try:
        client = get_client()
        response = place_order(
            client=client,
            symbol=symbol,
            side=side,
            order_type=order_type,
            quantity=quantity,
            price=price
        )

        click.echo("--- Order Response ---")
        click.echo(f"  Order ID     : {response.get('orderId')}")
        click.echo(f"  Status       : {response.get('status')}")
        click.echo(f"  Executed Qty : {response.get('executedQty')}")
        click.echo(f"  Avg Price    : {response.get('avgPrice', 'N/A')}")
        click.echo("\n✅ Order placed successfully!")
        logger.info(f"Order placed successfully: {response.get('orderId')}")

    except Exception as e:
        click.echo(f"\n❌ Order failed: {e}")
        logger.error(f"Order placement failed")

if __name__ == "__main__":
    main()

