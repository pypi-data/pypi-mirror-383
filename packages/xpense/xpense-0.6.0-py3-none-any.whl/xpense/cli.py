import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path

import typer
from rich.table import Table
from typing_extensions import Annotated

from xpense.config import cfg
from xpense.constants import TransactionType
from xpense.display import (
    console,
    show_account_balances,
    show_accounts,
    show_balance,
    show_categories,
    show_error,
    show_report,
    show_success,
    show_total,
    show_transaction_list,
)
from xpense.storage import TransactionStorage
from xpense.utils import parse_date_arg

HELP_TEXT = """A beautiful CLI expense and income tracker

[bold cyan]Quick Start Commands:[/bold cyan]

  [green]xpense 25.50 lunch "at the office"[/green]
    Add an expense (amount + category + optional note)

  [green]xpense add 1000 salary "monthly paycheck"[/green]
    Add income (use 'add' subcommand)

  [green]xpense list[/green]
    View all transactions

  [green]xpense balance[/green]
    Check your current balance

  [green]xpense report[/green]
    See breakdown by category

  [green]xpense dashboard[/green]
    Launch interactive web dashboard
"""

app = typer.Typer(
    help=HELP_TEXT,
    add_completion=False,
    no_args_is_help=False,
    rich_markup_mode="rich",
)

storage = TransactionStorage()


def _validate_amount(amount: float) -> bool:
    if amount <= 0:
        show_error("Amount must be positive")
        return False
    return True


def _validate_and_get_account(account: str | None) -> str | None:
    if account is None:
        account = cfg.get_default_account()

    if not cfg.is_account_registered(account):
        suggestions = cfg.suggest_accounts(account)
        if suggestions:
            show_error(
                f"Account '{account}' not registered. Did you mean: {', '.join(suggestions)}?"
            )
        else:
            show_error(
                f"Account '{account}' not registered. Add it first with: xpense account add {account}"
            )
        return None

    return account


def _format_account_suffix(account: str) -> str:
    return f" [{account}]" if account != cfg.get_default_account() else ""


def add_expense_default(
    amount: float,
    category: str,
    account: str | None = None,
    note: str = "",
    date: datetime | None = None,
) -> None:
    try:
        if not _validate_amount(amount):
            sys.exit(1)

        validated_account = _validate_and_get_account(account)
        if validated_account is None:
            sys.exit(1)

        transaction = storage.add_transaction(
            transaction_type=TransactionType.EXPENSE,
            amount=amount,
            category=category,
            account=validated_account,
            note=note,
            date=date,
        )

        account_suffix = _format_account_suffix(transaction["account"])
        show_success(
            f"Expense added: -{cfg.currency} {amount:.2f} in {transaction['category']}{account_suffix}"
        )

    except Exception as e:
        show_error(f"Failed to add expense: {str(e)}")
        sys.exit(1)


@app.command(name="add")
def add_income(
    amount: float,
    category: str,
    note: Annotated[str, typer.Argument()] = "",
    account: Annotated[
        str | None,
        typer.Option("--account", "-a", help="Account name (default: from config)"),
    ] = None,
    date: Annotated[
        str | None,
        typer.Option("--date", "-d", help="Transaction date in YYYY-MM-DD format"),
    ] = None,
) -> None:
    try:
        if not _validate_amount(amount):
            raise typer.Exit(1)

        validated_account = _validate_and_get_account(account)
        if validated_account is None:
            raise typer.Exit(1)

        parsed_date = None
        if date:
            try:
                parsed_date = parse_date_arg(date)
            except ValueError as e:
                show_error(str(e))
                raise typer.Exit(1)

        transaction = storage.add_transaction(
            transaction_type=TransactionType.INCOME,
            amount=amount,
            category=category,
            account=validated_account,
            note=note,
            date=parsed_date,
        )

        account_suffix = _format_account_suffix(transaction["account"])
        show_success(
            f"Income added: +{cfg.currency} {amount:.2f} in {transaction['category']}{account_suffix}"
        )

    except Exception as e:
        show_error(f"Failed to add income: {str(e)}")
        raise typer.Exit(1)


def _validate_month(month: int | None) -> None:
    if month is not None and (month < 1 or month > 12):
        show_error("Month must be between 1 and 12")
        raise typer.Exit(1)


def _validate_transaction_type(type: str) -> None:
    if type not in ["expense", "income", "all"]:
        show_error("Type must be 'expense', 'income', or 'all'")
        raise typer.Exit(1)


def _build_filter_title(
    base: str, month: int | None, category: str | None, type: str, account: str | None
) -> str:
    parts = [base]
    if month:
        parts.append(f"Month: {month}")
    if category:
        parts.append(f"Category: {category}")
    if type != "all":
        parts.append(f"Type: {type.title()}")
    if account:
        parts.append(f"Account: {account}")
    return " | ".join(parts)


@app.command()
def list(
    month: Annotated[int | None, typer.Option(help="Filter by month (1-12)")] = None,
    category: Annotated[str | None, typer.Option(help="Filter by category")] = None,
    type: Annotated[
        str | None, typer.Option(help="Filter by type: expense, income, or all")
    ] = "all",
    account: Annotated[
        str | None, typer.Option("--account", "-a", help="Filter by account")
    ] = None,
) -> None:
    """List transactions with optional filters."""
    try:
        _validate_month(month)
        _validate_transaction_type(type)

        transaction_type = None if type == "all" else type
        transactions = storage.get_transactions(
            month=month,
            category=category,
            transaction_type=transaction_type,
            account=account,
        )

        title = _build_filter_title("Transactions", month, category, type, account)
        show_transaction_list(transactions, title=title)

    except Exception as e:
        show_error(f"Failed to list transactions: {str(e)}")
        raise typer.Exit(1)


@app.command()
def total(
    month: Annotated[int | None, typer.Option(help="Filter by month (1-12)")] = None,
    category: Annotated[str | None, typer.Option(help="Filter by category")] = None,
    account: Annotated[
        str | None, typer.Option("--account", "-a", help="Filter by account")
    ] = None,
) -> None:
    """Show total with optional filters."""
    try:
        _validate_month(month)
        total_amount = storage.calculate_total(
            month=month, category=category, account=account
        )
        filters = {"month": month, "category": category, "account": account}
        show_total(total_amount, filters)

    except Exception as e:
        show_error(f"Failed to calculate total: {str(e)}")
        raise typer.Exit(1)


@app.command()
def balance(
    month: Annotated[int | None, typer.Option(help="Filter by month (1-12)")] = None,
    account: Annotated[
        str | None, typer.Option("--account", "-a", help="Filter by account")
    ] = None,
) -> None:
    """Show net balance (income - expenses)."""
    try:
        _validate_month(month)
        balance_data = storage.calculate_balance(month=month, account=account)
        show_balance(balance_data, month=month, account=account)

    except Exception as e:
        show_error(f"Failed to calculate balance: {str(e)}")
        raise typer.Exit(1)


@app.command()
def report(
    month: Annotated[int | None, typer.Option(help="Filter by month (1-12)")] = None,
    account: Annotated[
        str | None, typer.Option("--account", "-a", help="Filter by account")
    ] = None,
) -> None:
    """Show beautiful breakdown by category with totals for both income and expenses."""
    try:
        _validate_month(month)
        breakdown = storage.get_category_breakdown(month=month, account=account)
        show_report(breakdown, month=month, account=account)

    except Exception as e:
        show_error(f"Failed to generate report: {str(e)}")
        raise typer.Exit(1)


@app.command()
def categories(
    type: Annotated[
        str | None, typer.Option(help="Filter by type: expense, income, or all")
    ] = "all",
) -> None:
    """List all categories used."""
    try:
        _validate_transaction_type(type)
        transaction_type = None if type == "all" else type
        category_list = storage.get_categories(transaction_type=transaction_type)
        show_categories(category_list, transaction_type=type)

    except Exception as e:
        show_error(f"Failed to list categories: {str(e)}")
        raise typer.Exit(1)


@app.command()
def accounts(
    type: Annotated[
        str | None, typer.Option(help="Filter by type: expense, income, or all")
    ] = "all",
) -> None:
    """List all accounts used."""
    try:
        _validate_transaction_type(type)

        transaction_type = None if type == "all" else type
        account_list = storage.get_accounts(transaction_type=transaction_type)
        show_accounts(account_list, transaction_type=type)

    except Exception as e:
        show_error(f"Failed to list accounts: {str(e)}")
        raise typer.Exit(1)


@app.command(name="account-balances")
def account_balances(
    month: Annotated[int | None, typer.Option(help="Filter by month (1-12)")] = None,
) -> None:
    """Show balance breakdown by account."""
    try:
        _validate_month(month)

        balances = storage.get_account_balances(month=month)
        show_account_balances(balances, month=month)

    except Exception as e:
        show_error(f"Failed to calculate account balances: {str(e)}")
        raise typer.Exit(1)


@app.command()
def export(
    output: Annotated[str | None, typer.Option(help="Output file path")] = None,
) -> None:
    """Export transactions to CSV."""
    try:
        if output is None:
            timestamp = datetime.now().strftime("%Y%m%d")
            output = f"xpense_{timestamp}.csv"

        output_path = Path(output)
        count = storage.export_to_csv(output_path)

        show_success(f"Exported {count} transactions to {output_path}")

    except Exception as e:
        show_error(f"Failed to export: {str(e)}")
        raise typer.Exit(1)


@app.command()
def dashboard() -> None:
    """Launch interactive dashboard in browser."""
    try:
        console.print("[cyan]🚀 Launching xpense dashboard...[/cyan]")

        dashboard_path = Path(__file__).parent / "dashboard" / "app.py"

        env = os.environ.copy()

        result = subprocess.run(
            ["streamlit", "run", str(dashboard_path)],
            env=env,
        )

        if result.returncode != 0:
            show_error("Dashboard failed to start")
            raise typer.Exit(1)

    except FileNotFoundError:
        show_error(
            "Streamlit is not installed. Install dependencies with: uv sync or pip install -e ."
        )
        raise typer.Exit(1)
    except KeyboardInterrupt:
        console.print("\n[yellow]Dashboard stopped.[/yellow]")
        raise typer.Exit(0)
    except Exception as e:
        show_error(f"Failed to start dashboard: {str(e)}")
        raise typer.Exit(1)


account_app = typer.Typer(help="Manage accounts")
app.add_typer(account_app, name="account")


@account_app.command(name="add")
def account_add(account_name: str) -> None:
    """Register a new account."""
    try:
        cfg.add_account(account_name)
        show_success(f"Account '{account_name}' added successfully")

    except ValueError as e:
        show_error(str(e))
        raise typer.Exit(1)
    except Exception as e:
        show_error(f"Failed to add account: {str(e)}")
        raise typer.Exit(1)


@account_app.command(name="list")
def account_list() -> None:
    """List all registered accounts."""
    try:
        accounts = cfg.get_accounts()
        default_account = cfg.get_default_account()

        if not accounts:
            console.print("[yellow]No accounts registered.[/yellow]")
            return

        table = Table(
            title="📁 Registered Accounts", show_header=True, header_style="bold cyan"
        )
        table.add_column("Account", style="yellow")
        table.add_column("Default", justify="center")

        for account in sorted(accounts):
            is_default = "✓" if account == default_account else ""
            table.add_row(account, is_default)

        console.print(table)

    except Exception as e:
        show_error(f"Failed to list accounts: {str(e)}")
        raise typer.Exit(1)


@account_app.command(name="remove")
def account_remove(
    account_name: str,
    force: Annotated[
        bool, typer.Option("--force", "-f", help="Skip confirmation")
    ] = False,
) -> None:
    """Remove a registered account."""
    try:
        if not force:
            confirm = typer.confirm(
                f"Are you sure you want to remove account '{account_name}'?"
            )
            if not confirm:
                console.print("[yellow]Cancelled.[/yellow]")
                raise typer.Exit(0)

        cfg.remove_account(account_name)
        show_success(f"Account '{account_name}' removed successfully")

    except ValueError as e:
        show_error(str(e))
        raise typer.Exit(1)
    except Exception as e:
        show_error(f"Failed to remove account: {str(e)}")
        raise typer.Exit(1)


@account_app.command(name="set-default")
def account_set_default(account_name: str) -> None:
    """Set the default account."""
    try:
        cfg.set_default_account(account_name)
        show_success(f"Default account set to '{account_name}'")

    except ValueError as e:
        show_error(str(e))
        raise typer.Exit(1)
    except Exception as e:
        show_error(f"Failed to set default account: {str(e)}")
        raise typer.Exit(1)


config_app = typer.Typer(help="Manage configuration")
app.add_typer(config_app, name="config")


@config_app.command(name="show")
def config_show() -> None:
    """Show current configuration."""
    try:
        table = Table(
            title="⚙️  Configuration", show_header=True, header_style="bold cyan"
        )
        table.add_column("Setting", style="cyan")
        table.add_column("Value", style="yellow")

        table.add_row("Default Account", cfg.get_default_account())
        table.add_row("Currency", cfg.currency)
        table.add_row("Registered Accounts", ", ".join(cfg.get_accounts()))

        console.print(table)

    except Exception as e:
        show_error(f"Failed to show config: {str(e)}")
        raise typer.Exit(1)


@config_app.command(name="set-currency")
def config_set_currency(currency_code: str) -> None:
    """Set the currency code (e.g., USD, GHS, EUR)."""
    try:
        cfg.set_currency(currency_code)
        show_success(f"Currency set to '{cfg.currency}'")

    except ValueError as e:
        show_error(str(e))
        raise typer.Exit(1)
    except Exception as e:
        show_error(f"Failed to set currency: {str(e)}")
        raise typer.Exit(1)


@config_app.command(name="reset")
def config_reset(
    force: Annotated[
        bool, typer.Option("--force", "-f", help="Skip confirmation")
    ] = False,
) -> None:
    """Reset configuration to defaults."""
    try:
        if not force:
            confirm = typer.confirm(
                "Are you sure you want to reset all configuration to defaults?"
            )
            if not confirm:
                console.print("[yellow]Cancelled.[/yellow]")
                raise typer.Exit(0)

        cfg.reset()
        show_success("Configuration reset to defaults")

    except Exception as e:
        show_error(f"Failed to reset config: {str(e)}")
        raise typer.Exit(1)


if __name__ == "__main__":
    app()
