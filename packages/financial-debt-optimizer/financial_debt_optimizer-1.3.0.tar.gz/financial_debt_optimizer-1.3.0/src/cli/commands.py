import sys
from pathlib import Path

import click

from core.debt_optimizer import DebtOptimizer, OptimizationGoal
from core.logging_config import get_logger, setup_logging
from core.validation import validate_financial_scenario
from excel_io.excel_reader import ExcelReader, ExcelTemplateGenerator
from excel_io.excel_writer import ExcelReportWriter, generate_simple_summary_report

# Add src to path to allow imports
src_path = Path(__file__).parent.parent
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))


@click.group()
@click.version_option(version="1.0.0")
@click.option("--debug", is_flag=True, help="Enable debug logging")
@click.option("--log-file", type=str, help="Log file path")
def main(debug, log_file):
    """
    Financial Debt Optimizer

    A tool for analyzing and optimizing debt repayment strategies.

    This tool helps you find the best way to pay off your debts by analyzing
    different strategies like debt avalanche, snowball, and hybrid approaches.
    It generates detailed Excel reports with payment schedules, charts, and
    analysis to help you become debt-free as efficiently as possible.
    """
    # Setup logging
    level = "DEBUG" if debug else "INFO"
    setup_logging(level=level, log_file=log_file, console_output=False)

    # Get logger for CLI
    logger = get_logger("cli")
    logger.debug(
        f"Starting Financial Debt Optimizer CLI with debug={debug}, log_file={log_file}"
    )


@main.command()
@click.option(
    "--output",
    "-o",
    type=click.Path(),
    default="debt_template.xlsx",
    help="Output file path for the Excel template",
)
@click.option(
    "--sample-data/--no-sample-data",
    default=True,
    help="Include sample data in the template",
)
def generate_template(output: str, sample_data: bool):
    """Generate an Excel template for inputting debt and income data."""

    try:
        output_path = Path(output)

        # Check if file already exists
        if output_path.exists():
            if not click.confirm(f"File '{output}' already exists. Overwrite?"):
                click.echo("Operation cancelled.")
                return

        # Generate template
        ExcelTemplateGenerator.generate_template(str(output_path), sample_data)

        click.echo(f"✓ Excel template generated: {output_path.absolute()}")

        if sample_data:
            click.echo("\nThe template includes sample data to help you get started.")
            click.echo(
                "Replace the sample data with your actual financial information."
            )

        click.echo("\nTemplate includes six sheets:")
        click.echo(
            "  • Debts: List your debts with balance, minimum payment, interest rate"
        )
        click.echo("  • Income: Define your income sources and payment frequency")
        click.echo(
            "  • Recurring Expenses: Track regular expenses like subscriptions, fees"
        )
        click.echo("  • Future Income: Plan for bonuses, raises, or new income streams")
        click.echo(
            "  • Future Expenses: Budget for upcoming one-time or recurring costs"
        )
        click.echo("  • Settings: Configure optimization goals and preferences")

        click.echo("\nNext steps:")
        click.echo(f"  1. Open {output} in Excel or similar spreadsheet program")
        click.echo("  2. Fill in your actual financial data")
        click.echo(f"  3. Run analysis: debt-optimizer analyze -i {output}")

    except Exception as e:
        click.echo(f"✗ Error generating template: {e}", err=True)
        sys.exit(1)


@main.command()
@click.option(
    "--input",
    "-i",
    type=click.Path(),
    required=True,
    help="Input Excel file with debt and income data",
)
@click.option(
    "--output",
    "-o",
    type=click.Path(),
    default="debt_analysis.xlsx",
    help="Output file path for the analysis report",
)
@click.option(
    "--goal",
    type=click.Choice(["minimize_interest", "minimize_time", "maximize_cashflow"]),
    default="minimize_interest",
    help="Optimization goal for debt repayment strategy",
)
@click.option(
    "--extra-payment",
    type=float,
    default=0.0,
    help="Additional monthly payment amount to apply to debts",
)
@click.option(
    "--simple-report",
    is_flag=True,
    help="Generate a simplified one-sheet summary report",
)
@click.option(
    "--compare-strategies",
    is_flag=True,
    help="Compare all available strategies in the report",
)
def analyze(
    input: str,
    output: str,
    goal: str,
    extra_payment: float,
    simple_report: bool,
    compare_strategies: bool,
):
    """Analyze debt and generate optimized repayment plan."""

    logger = get_logger("cli.analyze")

    try:
        # Check if input file exists
        input_path = Path(input)
        if not input_path.exists():
            click.echo(f"✗ File not found: {input}", err=True)
            sys.exit(1)

        click.echo("📊 Starting debt optimization analysis...")
        logger.info(
            f"Starting analysis with input={input}, goal={goal}, extra_payment={extra_payment}"
        )

        # Read input data
        click.echo(f"📁 Reading data from {input}")
        reader = ExcelReader(input)
        (
            debts,
            income_sources,
            recurring_expenses,
            future_income,
            future_expenses,
            settings,
        ) = reader.read_all_data()

        # Validate the financial scenario
        logger.debug("Validating financial scenario")
        is_valid, messages = validate_financial_scenario(
            debts, income_sources, recurring_expenses, settings
        )

        if not is_valid:
            click.echo("❌ Validation errors found:")
            for message in messages:
                if message.startswith("Warning:"):
                    click.echo(f"  ⚠️  {message}")
                    logger.warning(message)
                else:
                    click.echo(f"  ❌ {message}")
                    logger.error(message)

            # Exit if there are actual errors (not just warnings)
            error_count = len([m for m in messages if not m.startswith("Warning:")])
            if error_count > 0:
                logger.error(f"Analysis aborted due to {error_count} validation errors")
                sys.exit(1)
        elif messages:  # Only warnings
            for message in messages:
                click.echo(f"  ⚠️  {message}")
                logger.warning(message)

        click.echo(
            f"✓ Found {len(debts)} debts and {len(income_sources)} income sources"
        )

        # Override settings with command line options
        if extra_payment > 0:
            settings["extra_payment"] = extra_payment
        settings["optimization_goal"] = goal

        # Initialize optimizer
        optimizer = DebtOptimizer(
            debts,
            income_sources,
            recurring_expenses,
            future_income,
            future_expenses,
            settings,
        )

        # Generate debt summary
        debt_summary = optimizer.generate_debt_summary()

        # Display current situation
        click.echo("\n📈 Current Financial Situation:")
        click.echo(f"  Total Debt: ${debt_summary['total_debt']:,.2f}")
        click.echo(f"  Monthly Income: ${debt_summary['monthly_income']:,.2f}")
        click.echo(
            f"  Minimum Payments: ${debt_summary['total_minimum_payments']:,.2f}"
        )
        click.echo(
            f"  Available Cash Flow: ${debt_summary['available_cash_flow']:,.2f}"
        )
        click.echo(
            f"  Current Bank Balance: ${debt_summary['current_bank_balance']:,.2f}"
        )
        click.echo(
            f"  Available Extra Payment: ${debt_summary['available_extra_payment']:,.2f}"
        )

        if debt_summary["available_cash_flow"] < 0:
            click.echo(
                "❌ Warning: Negative cash flow - income is less than minimum payments!",
                err=True,
            )
            click.echo("   Consider increasing income or debt consolidation options.")

        # Run optimization
        click.echo(f"\n🔍 Optimizing for: {goal.replace('_', ' ').title()}")

        optimization_goal = OptimizationGoal(goal)
        result = optimizer.optimize_debt_strategy(
            goal=optimization_goal, extra_payment=settings.get("extra_payment", 0.0)
        )

        # Display results
        click.echo("\n🎯 Optimization Results:")
        click.echo(f"  Best Strategy: {result.strategy.replace('_', ' ').title()}")
        click.echo(f"  Total Interest: ${result.total_interest_paid:,.2f}")
        years = result.total_months_to_freedom // 12
        months = result.total_months_to_freedom % 12
        click.echo(
            f"  Time to Freedom: {result.total_months_to_freedom} months "
            f"({years} years, {months} months)"
        )
        click.echo(
            f"  Interest Saved: ${result.savings_vs_minimum['interest_saved']:,.2f}"
        )
        click.echo(f"  Time Saved: {result.savings_vs_minimum['months_saved']} months")

        # Generate strategy comparison if requested
        strategy_comparison = None
        if compare_strategies:
            click.echo("\n📊 Comparing strategies...")
            strategy_comparison = optimizer.compare_strategies(
                extra_payment=settings.get("extra_payment", 0.0)
            )

            click.echo("\nStrategy Comparison:")
            for _, row in strategy_comparison.iterrows():
                click.echo(
                    f"  {row['strategy'].replace('_', ' ').title()}: "
                    f"${row['total_interest']:,.2f} interest, "
                    f"{row['months_to_freedom']} months"
                )

        # Generate report
        output_path = Path(output)

        # Check if output file exists
        if output_path.exists():
            if not click.confirm(f"File '{output}' already exists. Overwrite?"):
                click.echo("Operation cancelled.")
                return

        click.echo(f"\n📄 Generating report: {output}")

        if simple_report:
            generate_simple_summary_report(str(output_path), result, debt_summary)
        else:
            writer = ExcelReportWriter(str(output_path))
            writer.create_comprehensive_report(
                result,
                debt_summary,
                strategy_comparison if compare_strategies else None,
            )

        click.echo(f"✓ Report generated: {output_path.absolute()}")

        # Summary message
        months_years = f"{result.total_months_to_freedom // 12} years and {result.total_months_to_freedom % 12} months"
        click.echo(
            f"\n🎉 Summary: Using the {result.strategy.replace('_', ' ').title()} strategy, "
            f"you can be debt-free in {months_years} while saving "
            f"${result.savings_vs_minimum['interest_saved']:,.2f} in interest!"
        )

    except FileNotFoundError as e:
        click.echo(f"✗ File not found: {e}", err=True)
        sys.exit(1)
    except ValueError as e:
        click.echo(f"✗ Data validation error: {e}", err=True)
        click.echo(
            "Please check your input file and ensure all required data is present.",
            err=True,
        )
        sys.exit(1)
    except Exception as e:
        click.echo(f"✗ Unexpected error: {e}", err=True)
        sys.exit(1)


@main.command()
@click.argument("input_file", type=click.Path(exists=True))
def validate(input_file: str):
    """Validate an Excel input file for data integrity."""

    try:
        click.echo(f"🔍 Validating {input_file}...")

        reader = ExcelReader(input_file)
        (
            debts,
            income_sources,
            recurring_expenses,
            future_income,
            future_expenses,
            settings,
        ) = reader.read_all_data()

        # Validation checks
        errors = []
        warnings = []

        # Check debts
        if not debts:
            errors.append("No debts found")
        else:
            for debt in debts:
                if debt.balance <= 0:
                    warnings.append(f"Debt '{debt.name}' has zero or negative balance")
                if debt.minimum_payment <= 0:
                    errors.append(f"Debt '{debt.name}' has invalid minimum payment")
                if debt.interest_rate < 0:
                    errors.append(f"Debt '{debt.name}' has negative interest rate")

        # Check income
        if not income_sources:
            errors.append("No income sources found")
        else:
            total_monthly_income = sum(
                income.get_monthly_amount() for income in income_sources
            )

            for income in income_sources:
                if income.amount <= 0:
                    errors.append(f"Income '{income.source}' has invalid amount")

        # Financial health checks
        if debts and income_sources:
            total_minimums = sum(debt.minimum_payment for debt in debts)
            if total_monthly_income < total_minimums:
                errors.append("Income is insufficient to cover minimum payments")

        # Report results
        if errors:
            click.echo("❌ Validation failed with errors:")
            for error in errors:
                click.echo(f"  • {error}")

        if warnings:
            click.echo("⚠️  Validation warnings:")
            for warning in warnings:
                click.echo(f"  • {warning}")

        if not errors and not warnings:
            click.echo("✅ Validation passed - file is ready for analysis!")
        elif not errors:
            click.echo("✅ Validation passed with warnings - file can be analyzed")

        # Summary
        click.echo("\nFile Summary:")
        click.echo(f"  Debts: {len(debts)}")
        click.echo(f"  Income Sources: {len(income_sources)}")
        click.echo(f"  Total Debt: ${sum(debt.balance for debt in debts):,.2f}")
        click.echo(
            f"  Monthly Income: ${sum(income.get_monthly_amount() for income in income_sources):,.2f}"
        )

        sys.exit(1 if errors else 0)

    except Exception as e:
        click.echo(f"✗ Validation error: {e}", err=True)
        sys.exit(1)


@main.command()
def info():
    """Display information about debt optimization strategies."""

    click.echo("📚 Debt Optimization Strategies\n")

    click.echo("🔥 DEBT AVALANCHE (Minimize Interest)")
    click.echo("   • Pay minimums on all debts")
    click.echo("   • Apply extra payments to highest interest rate debt first")
    click.echo("   • Mathematically optimal - saves the most money")
    click.echo("   • Best for: Maximizing interest savings\n")

    click.echo("❄️  DEBT SNOWBALL (Minimize Time)")
    click.echo("   • Pay minimums on all debts")
    click.echo("   • Apply extra payments to lowest balance debt first")
    click.echo("   • Provides psychological wins with quick payoffs")
    click.echo("   • Best for: Building momentum and motivation\n")

    click.echo("🌊 HYBRID APPROACH")
    click.echo("   • Balances interest rate and balance considerations")
    click.echo("   • Weights high interest rates more heavily (70/30)")
    click.echo("   • Compromise between avalanche and snowball")
    click.echo("   • Best for: Balanced approach to savings and motivation\n")

    click.echo("🎯 OPTIMIZATION GOALS\n")

    click.echo("minimize_interest:")
    click.echo("   • Chooses strategy that pays least total interest")
    click.echo("   • Usually favors debt avalanche method")
    click.echo("   • Maximizes long-term savings\n")

    click.echo("minimize_time:")
    click.echo("   • Chooses strategy that pays off debts fastest")
    click.echo("   • May favor snowball for quick early wins")
    click.echo("   • Gets you debt-free in shortest time\n")

    click.echo("maximize_cashflow:")
    click.echo("   • Optimizes for improved monthly cash flow")
    click.echo("   • Considers payment timing and frequency")
    click.echo("   • Provides most financial flexibility\n")

    click.echo("💡 Tips:")
    click.echo("   • Use 'debt-optimizer validate' to check your data first")
    click.echo("   • Try '--compare-strategies' to see all options")
    click.echo("   • Start with a template: 'debt-optimizer generate-template'")
    click.echo("   • Set your actual current bank balance in the Settings sheet")
    click.echo("   • Emergency fund of 3-6 months expenses is recommended")
    click.echo(
        "   • Extra payments are automatically calculated from available cash flow"
    )


if __name__ == "__main__":
    main()
