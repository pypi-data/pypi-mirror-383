import click
from rich import print
from rich.table import Table
import asyncio
from bson import ObjectId

# Import database and models from the api directory
from api.database import item_collection
# NOTE: The models are only needed for the 'add' command.
# We will import it inside that function to simplify debugging.

@click.group()
def cli():
    """
    A command-line tool to manage inventory items.
    """
    pass

@cli.command("add")
@click.option("--name", "-n", required=True, help="Name of the item.")
@click.option("--price", "-p", required=True, type=float, help="Price of the item.")
@click.option("--desc", "-d", default=None, help="Optional item description.")
def add(name: str, price: float, desc: str):
    """
    Adds a new item to the database.
    """
    from api.models import ItemCreateModel # Import here
    print(f"Adding item: [bold cyan]{name}[/bold cyan] with price ${price:.2f}")

    async def main():
        # In Pydantic V2, use .model_dump() instead of .dict()
        item_data = ItemCreateModel(name=name, price=price, description=desc)
        new_item = await item_collection.insert_one(item_data.model_dump())
        
        if new_item.inserted_id:
            print(f"[bold green]✅ Success![/bold green] Item added with ID: {new_item.inserted_id}")
        else:
            print("[bold red]❌ Error![/bold red] Could not add the item.")

    asyncio.run(main())

@cli.command("delete")
@click.argument("item_id")
def delete(item_id: str):
    """
    Deletes an item from the database using its ID.
    """
    if not ObjectId.is_valid(item_id):
        print(f"[bold red]❌ Error![/bold red] '{item_id}' is not a valid MongoDB ObjectId.")
        raise click.exceptions.Exit(code=1)

    print(f"Attempting to delete item with ID: [bold yellow]{item_id}[/bold yellow]")

    async def main():
        delete_result = await item_collection.delete_one({"_id": ObjectId(item_id)})
        
        if delete_result.deleted_count == 1:
            print(f"[bold green]✅ Success![/bold green] Item '{item_id}' has been deleted.")
        else:
            print(f"[bold red]❌ Not Found![/bold red] No item found with ID '{item_id}'.")

    asyncio.run(main())

@cli.command("list")
def list_all():
    """
    Lists all items currently in the database.
    """
    async def main():
        items = await item_collection.find().to_list(1000)
        
        if not items:
            print("[yellow]No items found in the database.[/yellow]")
            return

        table = Table(title="Inventory Items")
        table.add_column("ID", style="cyan", no_wrap=True)
        table.add_column("Name", style="magenta")
        table.add_column("Price", justify="right", style="green")
        table.add_column("Description", style="white")

        for item in items:
            table.add_row(
                str(item["_id"]),
                item["name"],
                f"${item['price']:.2f}",
                item.get("description", "N/A")
            )
        
        print(table)

    asyncio.run(main())


if __name__=="__main__":
    cli()