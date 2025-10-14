from typing import Any, Dict, Optional

import pandas as pd
import xlsxwriter
from xlsxwriter.workbook import Workbook

from core.debt_optimizer import OptimizationResult


class ExcelReportWriter:
    """Generate comprehensive Excel reports for debt optimization results."""

    def __init__(self, output_path: str):
        """Initialize with output path for Excel file."""
        self.output_path = output_path
        self.workbook: Optional[Workbook] = None
        self.formats: Dict[str, Any] = {}

    def create_comprehensive_report(
        self,
        optimization_result: OptimizationResult,
        debt_summary: Dict[str, Any],
        strategy_comparison: Optional[pd.DataFrame] = None,
    ):
        """Create a comprehensive Excel report with all analysis results."""

        # Create workbook and formats
        self.workbook = xlsxwriter.Workbook(self.output_path)
        self._setup_formats()

        try:
            # Create all sheets
            self._create_summary_sheet(optimization_result, debt_summary)
            self._create_payment_schedule_sheet(optimization_result.payment_schedule)
            self._create_monthly_summary_sheet(optimization_result.monthly_summary)
            self._create_enhanced_monthly_summary_sheet(optimization_result)
            self._create_debt_progression_sheet(optimization_result.debt_progression)
            self._create_decision_log_sheet(optimization_result)

            if strategy_comparison is not None:
                self._create_strategy_comparison_sheet(strategy_comparison)

            self._create_charts_sheet(optimization_result)
            # self._create_additional_charts_sheet(optimization_result)  # Disabled temporarily due to API issues

        finally:
            self.workbook.close()

    def _setup_formats(self):
        """Set up cell formats for the workbook."""
        self.formats = {
            "title": self.workbook.add_format(
                {
                    "bold": True,
                    "font_size": 16,
                    "align": "center",
                    "valign": "vcenter",
                    "bg_color": "#4F81BD",
                    "font_color": "white",
                    "border": 1,
                }
            ),
            "header": self.workbook.add_format(
                {
                    "bold": True,
                    "bg_color": "#D9E1F2",
                    "border": 1,
                    "align": "center",
                    "valign": "vcenter",
                }
            ),
            "currency": self.workbook.add_format(
                {"num_format": "$#,##0.00", "border": 1}
            ),
            "percentage": self.workbook.add_format(
                {"num_format": "0.00%", "border": 1}
            ),
            "integer": self.workbook.add_format({"num_format": "#,##0", "border": 1}),
            "date": self.workbook.add_format({"num_format": "yyyy-mm-dd", "border": 1}),
            "highlight": self.workbook.add_format({"bg_color": "#FFEB9C", "border": 1}),
            "success": self.workbook.add_format(
                {"bg_color": "#C6EFCE", "font_color": "#006100", "border": 1}
            ),
            "warning": self.workbook.add_format(
                {"bg_color": "#FFC7CE", "font_color": "#9C0006", "border": 1}
            ),
        }

    def _create_summary_sheet(
        self, result: OptimizationResult, debt_summary: Dict[str, Any]
    ):
        """Create executive summary sheet."""
        if self.workbook is None:
            raise ValueError("Workbook not initialized")
        worksheet = self.workbook.add_worksheet("Executive Summary")

        # Title
        worksheet.merge_range(
            "A1:F1", "Debt Optimization Analysis Summary", self.formats["title"]
        )

        row = 3

        # Strategy Information
        worksheet.write(row, 0, "Optimization Strategy:", self.formats["header"])
        worksheet.write(row, 1, result.strategy.replace("_", " ").title())
        row += 1

        worksheet.write(row, 0, "Optimization Goal:", self.formats["header"])
        worksheet.write(row, 1, result.goal.replace("_", " ").title())
        row += 2

        # Key Metrics
        worksheet.write(row, 0, "KEY RESULTS", self.formats["title"])
        row += 2

        metrics = [
            ("Total Debt:", debt_summary["total_debt"], "currency"),
            ("Total Interest to Pay:", result.total_interest_paid, "currency"),
            ("Months to Debt Freedom:", result.total_months_to_freedom, "integer"),
            (
                "Interest Saved vs Minimum:",
                result.savings_vs_minimum["interest_saved"],
                "currency",
            ),
            (
                "Time Saved (months):",
                result.savings_vs_minimum["months_saved"],
                "integer",
            ),
            (
                "Monthly Cash Flow Improvement:",
                result.monthly_cash_flow_improvement,
                "currency",
            ),
        ]

        for metric_name, value, format_type in metrics:
            worksheet.write(row, 0, metric_name, self.formats["header"])
            worksheet.write(row, 1, value, self.formats[format_type])
            row += 1

        row += 2

        # Current Financial Situation
        worksheet.write(row, 0, "CURRENT SITUATION", self.formats["title"])
        row += 2

        current_metrics = [
            ("Number of Debts:", debt_summary["number_of_debts"], "integer"),
            ("Total Monthly Income:", debt_summary["monthly_income"], "currency"),
            (
                "Total Minimum Payments:",
                debt_summary["total_minimum_payments"],
                "currency",
            ),
            ("Available Cash Flow:", debt_summary["available_cash_flow"], "currency"),
            (
                "Weighted Avg Interest Rate:",
                debt_summary["weighted_avg_interest_rate"] / 100,
                "percentage",
            ),
        ]

        for metric_name, value, format_type in current_metrics:
            worksheet.write(row, 0, metric_name, self.formats["header"])
            worksheet.write(row, 1, value, self.formats[format_type])
            row += 1

        row += 2

        # Individual Debt Details
        worksheet.write(row, 0, "DEBT BREAKDOWN", self.formats["title"])
        row += 2

        # Headers for debt table
        debt_headers = [
            "Debt Name",
            "Balance",
            "Min Payment",
            "Interest Rate",
            "Due Date",
        ]
        for col, header in enumerate(debt_headers):
            worksheet.write(row, col, header, self.formats["header"])
        row += 1

        # Debt data
        for debt in debt_summary["debt_details"]:
            worksheet.write(row, 0, debt["name"])
            worksheet.write(row, 1, debt["balance"], self.formats["currency"])
            worksheet.write(row, 2, debt["minimum_payment"], self.formats["currency"])
            worksheet.write(
                row, 3, debt["interest_rate"] / 100, self.formats["percentage"]
            )
            worksheet.write(row, 4, debt["due_date"], self.formats["integer"])
            row += 1

        # Set column widths
        worksheet.set_column("A:A", 25)
        worksheet.set_column("B:F", 15)

    def _create_payment_schedule_sheet(self, payment_schedule: pd.DataFrame):
        """Create detailed payment schedule sheet with income events and cash flow."""
        worksheet = self.workbook.add_worksheet("Payment Schedule")

        # Title
        worksheet.merge_range(
            "A1:J1",
            "Detailed Payment Schedule with Cash Flow & Debt Balances",
            self.formats["title"],
        )

        if payment_schedule.empty:
            worksheet.write(3, 0, "No payment schedule data available")
            return

        # Headers
        headers = [
            "Date",
            "Type",
            "Description",
            "Amount",
            "Interest",
            "Principal",
            "Total Debt Balance",
            "Debt Name",
            "Debt Balance",
            "Bank Balance",
        ]
        for col, header in enumerate(headers):
            worksheet.write(2, col, header, self.formats["header"])

        # Data
        for idx, row in payment_schedule.iterrows():
            worksheet.write(idx + 3, 0, row["date"], self.formats["date"])

            # Format type column with colors
            if row["type"] == "income":
                type_format = self.formats["success"]
                type_display = "Income"
            elif row["type"] == "opening_balance":
                type_format = self.formats["header"]
                type_display = "Opening Balance"
            else:
                type_format = self.formats["currency"]
                type_display = row["type"].replace("_", " ").title()

            worksheet.write(idx + 3, 1, type_display, type_format)

            worksheet.write(
                idx + 3, 2, row.get("description", ""), self.formats["header"]
            )

            # Amount with color coding (green for income, red for payments, neutral for opening balance)
            if row["type"] == "opening_balance":
                amount_format = self.formats["header"]
            elif row.get("amount", 0) > 0:
                amount_format = self.formats["success"]
            else:
                amount_format = self.formats["currency"]
            worksheet.write(idx + 3, 3, row.get("amount", 0), amount_format)

            worksheet.write(
                idx + 3, 4, row.get("interest_portion", 0), self.formats["currency"]
            )
            worksheet.write(
                idx + 3, 5, row.get("principal_portion", 0), self.formats["currency"]
            )
            worksheet.write(
                idx + 3, 6, row.get("remaining_balance", 0), self.formats["currency"]
            )
            worksheet.write(idx + 3, 7, row.get("debt_name", "N/A"))

            # Format debt balance with special formatting for zero balances (debt paid off)
            debt_balance = row.get("debt_balance", 0)
            # Convert empty strings to 0 for comparison
            if isinstance(debt_balance, str):
                debt_balance_numeric = (
                    0.0
                    if debt_balance == ""
                    else (
                        float(debt_balance)
                        if debt_balance.replace(".", "").replace("-", "").isdigit()
                        else 0.0
                    )
                )
            else:
                debt_balance_numeric = (
                    float(debt_balance) if debt_balance is not None else 0.0
                )

            if debt_balance_numeric <= 0.01 and row.get("debt_name", "N/A") != "N/A":
                debt_format = self.formats["success"]  # Green for paid off debts
            else:
                debt_format = self.formats["currency"]
            # Write the original value (could be empty string) but use numeric for formatting decision
            worksheet.write(
                idx + 3,
                8,
                (
                    debt_balance_numeric
                    if isinstance(debt_balance, str) and debt_balance == ""
                    else debt_balance
                ),
                debt_format,
            )

            worksheet.write(
                idx + 3, 9, row.get("bank_balance", 0), self.formats["currency"]
            )

        # Set column widths
        worksheet.set_column("A:A", 12)  # Date
        worksheet.set_column("B:B", 15)  # Type
        worksheet.set_column("C:C", 30)  # Description
        worksheet.set_column("D:F", 15)  # Amount, Interest, Principal
        worksheet.set_column("G:G", 18)  # Total Debt Balance
        worksheet.set_column("H:H", 25)  # Debt Name
        worksheet.set_column("I:I", 15)  # Debt Balance
        worksheet.set_column("J:J", 15)  # Bank Balance

    def _create_monthly_summary_sheet(self, monthly_summary: pd.DataFrame):
        """Create enhanced monthly summary sheet with detailed income, expenses, and extra funds tracking."""
        worksheet = self.workbook.add_worksheet("Monthly Summary")

        # Title
        worksheet.merge_range(
            "A1:N1",
            "Monthly Payment Summary with Extra Funds & Expense Tracking",
            self.formats["title"],
        )

        if monthly_summary.empty:
            worksheet.write(3, 0, "No monthly summary data available")
            return

        # Headers
        headers = [
            "Month",
            "Date",
            "Total Income",
            "Regular Income",
            "Future Income",
            "Total Expenses",
            "Min Payments",
            "Extra Payments",
            "Extra Funds Available",
            "Interest Paid",
            "Principal Paid",
            "Remaining Debt",
            "Bank Balance",
            "Details",
        ]
        for col, header in enumerate(headers):
            worksheet.write(2, col, header, self.formats["header"])

        # Data
        for idx, row in monthly_summary.iterrows():
            worksheet.write(idx + 3, 0, row["month"], self.formats["integer"])
            worksheet.write(idx + 3, 1, row["date"], self.formats["date"])
            worksheet.write(
                idx + 3, 2, row.get("total_income", 0), self.formats["currency"]
            )
            worksheet.write(
                idx + 3, 3, row.get("regular_income", 0), self.formats["currency"]
            )
            worksheet.write(
                idx + 3, 4, row.get("future_income", 0), self.formats["currency"]
            )
            worksheet.write(
                idx + 3, 5, row.get("total_expenses", 0), self.formats["currency"]
            )
            worksheet.write(
                idx + 3, 6, row.get("minimum_payments", 0), self.formats["currency"]
            )
            worksheet.write(
                idx + 3, 7, row.get("extra_payments", 0), self.formats["currency"]
            )

            # Color-code extra funds available column
            extra_funds_available = row.get("extra_funds_available", 0)

            # Green for positive extra funds, yellow for small positive, red for none
            extra_funds_format = (
                self.formats["success"]
                if extra_funds_available > 100
                else (
                    self.formats["warning"]
                    if extra_funds_available > 0
                    else self.formats["currency"]
                )
            )

            worksheet.write(idx + 3, 8, extra_funds_available, extra_funds_format)

            worksheet.write(
                idx + 3, 9, row.get("total_interest", 0), self.formats["currency"]
            )
            worksheet.write(
                idx + 3, 10, row.get("total_principal", 0), self.formats["currency"]
            )
            worksheet.write(
                idx + 3, 11, row.get("remaining_debt", 0), self.formats["currency"]
            )
            worksheet.write(
                idx + 3, 12, row.get("bank_balance", 0), self.formats["currency"]
            )

            # Combine income and expense details
            income_details = row.get("income_details", "Regular income only")
            expense_details = row.get("expense_details", "None")
            details_text = f"Income: {income_details}; Expenses: {expense_details}"
            worksheet.write(idx + 3, 13, details_text)

        # Add totals row
        total_row = len(monthly_summary) + 4
        worksheet.write(total_row, 0, "TOTALS:", self.formats["header"])

        # Calculate and display totals for relevant columns
        if not monthly_summary.empty:
            worksheet.write(
                total_row,
                2,
                monthly_summary.get("total_income", pd.Series([0])).sum(),
                self.formats["highlight"],
            )
            worksheet.write(
                total_row,
                3,
                monthly_summary.get("regular_income", pd.Series([0])).sum(),
                self.formats["highlight"],
            )
            worksheet.write(
                total_row,
                4,
                monthly_summary.get("future_income", pd.Series([0])).sum(),
                self.formats["highlight"],
            )
            worksheet.write(
                total_row,
                5,
                monthly_summary.get("total_expenses", pd.Series([0])).sum(),
                self.formats["highlight"],
            )
            worksheet.write(
                total_row,
                6,
                monthly_summary.get("minimum_payments", pd.Series([0])).sum(),
                self.formats["highlight"],
            )
            worksheet.write(
                total_row,
                7,
                monthly_summary.get("extra_payments", pd.Series([0])).sum(),
                self.formats["highlight"],
            )
            worksheet.write(
                total_row,
                8,
                monthly_summary.get("extra_funds_available", pd.Series([0])).sum(),
                self.formats["highlight"],
            )
            worksheet.write(
                total_row,
                9,
                monthly_summary.get("total_interest", pd.Series([0])).sum(),
                self.formats["highlight"],
            )
            worksheet.write(
                total_row,
                10,
                monthly_summary.get("total_principal", pd.Series([0])).sum(),
                self.formats["highlight"],
            )

        # Set column widths
        worksheet.set_column("A:A", 8)  # Month
        worksheet.set_column("B:B", 12)  # Date
        worksheet.set_column("C:M", 12)  # Financial columns
        worksheet.set_column("N:N", 40)  # Details column

    def _create_enhanced_monthly_summary_sheet(self, result: OptimizationResult):
        """Create enhanced monthly summary with extra funds tracking and allocation details."""
        worksheet = self.workbook.add_worksheet("Monthly Extra Funds")

        # Title
        worksheet.merge_range(
            "A1:K1",
            "Monthly Extra Funds Tracking & Allocation Decisions",
            self.formats["title"],
        )

        # Check if we have monthly extra funds data
        if not hasattr(result, "monthly_extra_funds") or not result.monthly_extra_funds:
            worksheet.write(3, 0, "No monthly extra funds tracking data available")
            worksheet.write(
                4, 0, "This feature requires running the enhanced optimization engine"
            )
            return

        # Headers
        headers = [
            "Month",
            "Date",
            "Total Income",
            "Required Minimums",
            "Recurring Expenses",
            "Available Extra",
            "Allocated Extra",
            "Remaining Extra",
            "Allocation Efficiency",
            "Primary Allocation",
            "Allocation Count",
        ]
        for col, header in enumerate(headers):
            worksheet.write(2, col, header, self.formats["header"])

        # Data
        for idx, monthly_extra in enumerate(result.monthly_extra_funds):
            worksheet.write(idx + 3, 0, monthly_extra.month, self.formats["integer"])
            worksheet.write(idx + 3, 1, monthly_extra.date, self.formats["date"])
            worksheet.write(
                idx + 3, 2, monthly_extra.total_income, self.formats["currency"]
            )
            worksheet.write(
                idx + 3, 3, monthly_extra.required_minimums, self.formats["currency"]
            )
            worksheet.write(
                idx + 3, 4, monthly_extra.recurring_expenses, self.formats["currency"]
            )
            worksheet.write(
                idx + 3, 5, monthly_extra.available_extra, self.formats["currency"]
            )
            worksheet.write(
                idx + 3, 6, monthly_extra.allocated_extra, self.formats["currency"]
            )
            worksheet.write(
                idx + 3, 7, monthly_extra.remaining_extra, self.formats["currency"]
            )

            # Calculate allocation efficiency
            efficiency = (
                (monthly_extra.allocated_extra / monthly_extra.available_extra * 100)
                if monthly_extra.available_extra > 0
                else 0
            )
            efficiency_format = (
                self.formats["success"]
                if efficiency >= 95
                else (
                    self.formats["warning"]
                    if efficiency < 80
                    else self.formats["percentage"]
                )
            )
            worksheet.write(idx + 3, 8, efficiency / 100, efficiency_format)

            # Primary allocation target
            primary_target = "N/A"
            allocation_count = len(monthly_extra.allocation_decisions)
            if monthly_extra.allocation_decisions:
                # Find the allocation with the highest amount
                max_allocation = max(
                    monthly_extra.allocation_decisions, key=lambda x: x.get("amount", 0)
                )
                primary_target = max_allocation.get("target", "Unknown")

            worksheet.write(idx + 3, 9, primary_target)
            worksheet.write(idx + 3, 10, allocation_count, self.formats["integer"])

        # Add summary section
        summary_start_row = len(result.monthly_extra_funds) + 5
        worksheet.write(
            summary_start_row, 0, "EXTRA FUNDS SUMMARY", self.formats["title"]
        )

        # Calculate totals
        total_available = sum(mef.available_extra for mef in result.monthly_extra_funds)
        total_allocated = sum(mef.allocated_extra for mef in result.monthly_extra_funds)
        total_remaining = sum(mef.remaining_extra for mef in result.monthly_extra_funds)

        summary_start_row += 2
        summary_metrics = [
            ("Total Extra Funds Available:", total_available, "currency"),
            ("Total Extra Funds Allocated:", total_allocated, "currency"),
            ("Total Extra Funds Remaining:", total_remaining, "currency"),
            (
                "Overall Allocation Efficiency:",
                (total_allocated / total_available) if total_available > 0 else 0,
                "percentage",
            ),
        ]

        for metric_name, value, format_type in summary_metrics:
            worksheet.write(summary_start_row, 0, metric_name, self.formats["header"])
            format_to_use = (
                self.formats["success"]
                if metric_name.startswith("Overall") and value >= 0.95
                else self.formats[format_type]
            )
            worksheet.write(summary_start_row, 1, value, format_to_use)
            summary_start_row += 1

        # Set column widths
        worksheet.set_column("A:A", 8)  # Month
        worksheet.set_column("B:B", 12)  # Date
        worksheet.set_column("C:H", 15)  # Financial columns
        worksheet.set_column("I:I", 18)  # Allocation Efficiency
        worksheet.set_column("J:J", 25)  # Primary Allocation
        worksheet.set_column("K:K", 15)  # Allocation Count

    def _create_decision_log_sheet(self, result: OptimizationResult):
        """Create decision log sheet tracking all optimization decisions and rationale."""
        worksheet = self.workbook.add_worksheet("Decision Log")

        # Title
        worksheet.merge_range(
            "A1:H1",
            "Optimization Decision Log & Rationale Tracking",
            self.formats["title"],
        )

        # Check if we have decision log data
        if not hasattr(result, "decision_log") or not result.decision_log:
            worksheet.write(3, 0, "No decision log data available")
            worksheet.write(
                4,
                0,
                "This feature requires running the enhanced optimization engine with decision tracking",
            )
            return

        # Headers
        headers = [
            "Timestamp",
            "Month",
            "Decision Type",
            "Description",
            "Rationale",
            "Impact",
            "Supporting Data",
            "Category",
        ]
        for col, header in enumerate(headers):
            worksheet.write(2, col, header, self.formats["header"])

        # Data
        for idx, decision in enumerate(result.decision_log):
            worksheet.write(
                idx + 3,
                0,
                decision.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                self.formats["date"],
            )
            worksheet.write(idx + 3, 1, decision.month, self.formats["integer"])

            # Color-code decision types
            decision_format = self.formats["currency"]
            if decision.decision_type == "strategy_selection":
                decision_format = self.formats["success"]
            elif decision.decision_type == "priority_change":
                decision_format = self.formats["warning"]
            elif decision.decision_type == "goal_selection":
                decision_format = self.formats["highlight"]

            worksheet.write(
                idx + 3,
                2,
                decision.decision_type.replace("_", " ").title(),
                decision_format,
            )
            worksheet.write(idx + 3, 3, decision.description)
            worksheet.write(idx + 3, 4, decision.rationale)
            worksheet.write(idx + 3, 5, decision.impact)

            # Format supporting data as readable string
            data_summary = self._format_decision_data(decision.data_snapshot)
            worksheet.write(idx + 3, 6, data_summary)

            # Categorize decisions
            category = self._categorize_decision(decision.decision_type)
            worksheet.write(idx + 3, 7, category)

        # Add summary section
        summary_start_row = len(result.decision_log) + 5
        worksheet.write(summary_start_row, 0, "DECISION SUMMARY", self.formats["title"])

        # Count decisions by type
        decision_counts: Dict[str, int] = {}
        for decision in result.decision_log:
            decision_type = decision.decision_type.replace("_", " ").title()
            decision_counts[decision_type] = decision_counts.get(decision_type, 0) + 1

        summary_start_row += 2
        worksheet.write(
            summary_start_row, 0, "Decision Type Breakdown:", self.formats["header"]
        )
        summary_start_row += 1

        for decision_type, count in decision_counts.items():
            worksheet.write(summary_start_row, 0, f"• {decision_type}:")
            worksheet.write(summary_start_row, 1, f"{count} decisions")
            summary_start_row += 1

        summary_start_row += 1

        # Key decisions summary
        worksheet.write(
            summary_start_row, 0, "Key Decision Points:", self.formats["header"]
        )
        summary_start_row += 1

        key_decisions = [
            d
            for d in result.decision_log
            if d.decision_type in ["strategy_selection", "goal_selection"]
        ]
        for decision in key_decisions:
            worksheet.write(summary_start_row, 0, f"• {decision.description}")
            worksheet.write(summary_start_row, 1, decision.impact)
            summary_start_row += 1

        # Set column widths
        worksheet.set_column("A:A", 18)  # Timestamp
        worksheet.set_column("B:B", 8)  # Month
        worksheet.set_column("C:C", 18)  # Decision Type
        worksheet.set_column("D:D", 35)  # Description
        worksheet.set_column("E:E", 45)  # Rationale
        worksheet.set_column("F:F", 35)  # Impact
        worksheet.set_column("G:G", 30)  # Supporting Data
        worksheet.set_column("H:H", 15)  # Category

    def _format_decision_data(self, data_snapshot: dict) -> str:
        """Format decision data snapshot into readable string."""
        if not data_snapshot:
            return "No supporting data"

        formatted_items = []
        for key, value in data_snapshot.items():
            if isinstance(value, (int, float)):
                if (
                    "amount" in key.lower()
                    or "payment" in key.lower()
                    or "debt" in key.lower()
                ):
                    formatted_items.append(f"{key}: ${value:,.2f}")
                elif "rate" in key.lower() or "percentage" in key.lower():
                    formatted_items.append(f"{key}: {value:.2f}%")
                else:
                    formatted_items.append(f"{key}: {value}")
            elif isinstance(value, list):
                if len(value) <= 3:
                    formatted_items.append(f"{key}: {value}")
                else:
                    formatted_items.append(f"{key}: [{len(value)} items]")
            else:
                formatted_items.append(
                    f"{key}: {str(value)[:30]}..."
                    if len(str(value)) > 30
                    else f"{key}: {value}"
                )

        return "; ".join(formatted_items)

    def _categorize_decision(self, decision_type: str) -> str:
        """Categorize decision types for better organization."""
        categories = {
            "goal_selection": "Strategic",
            "strategy_selection": "Strategic",
            "strategy_evaluation": "Analysis",
            "priority_change": "Tactical",
            "payment_allocation": "Tactical",
            "debt_payoff": "Operational",
        }
        return categories.get(decision_type, "Other")

    def _create_debt_progression_sheet(self, debt_progression: pd.DataFrame):
        """Create debt progression over time sheet."""
        worksheet = self.workbook.add_worksheet("Debt Progression")

        # Title
        worksheet.merge_range(
            "A1:Z1", "Debt Balance Progression Over Time", self.formats["title"]
        )

        if debt_progression.empty:
            worksheet.write(3, 0, "No debt progression data available")
            return

        # Write headers
        for col, header in enumerate(debt_progression.columns):
            worksheet.write(2, col, header, self.formats["header"])

        # Write data
        for idx, row in debt_progression.iterrows():
            worksheet.write(idx + 3, 0, row["month"], self.formats["integer"])
            worksheet.write(idx + 3, 1, row["date"], self.formats["date"])

            # Write debt balances
            for col_idx, col in enumerate(debt_progression.columns[2:], 2):
                value = row[col]
                if pd.notna(value):
                    # Ensure value is numeric for comparison
                    numeric_value = (
                        float(value) if not isinstance(value, (int, float)) else value
                    )
                    format_to_use = (
                        self.formats["success"]
                        if numeric_value <= 0.01
                        else self.formats["currency"]
                    )
                    worksheet.write(idx + 3, col_idx, value, format_to_use)

        # Set column widths
        worksheet.set_column("A:A", 8)
        worksheet.set_column("B:B", 12)
        worksheet.set_column("C:Z", 15)

    def _create_strategy_comparison_sheet(self, comparison_df: pd.DataFrame):
        """Create strategy comparison sheet."""
        worksheet = self.workbook.add_worksheet("Strategy Comparison")

        # Title
        worksheet.merge_range(
            "A1:F1", "Debt Payoff Strategy Comparison", self.formats["title"]
        )

        if comparison_df.empty:
            worksheet.write(3, 0, "No strategy comparison data available")
            return

        # Headers
        for col, header in enumerate(comparison_df.columns):
            worksheet.write(
                2, col, header.replace("_", " ").title(), self.formats["header"]
            )

        # Data
        for idx, row in comparison_df.iterrows():
            worksheet.write(idx + 3, 0, row["strategy"].replace("_", " ").title())
            worksheet.write(idx + 3, 1, row["total_interest"], self.formats["currency"])
            worksheet.write(
                idx + 3, 2, row["months_to_freedom"], self.formats["integer"]
            )
            worksheet.write(
                idx + 3, 3, row["monthly_cash_flow"], self.formats["currency"]
            )
            worksheet.write(idx + 3, 4, row["interest_saved"], self.formats["currency"])
            worksheet.write(idx + 3, 5, row["months_saved"], self.formats["integer"])

        # Highlight best strategy in each category
        if not comparison_df.empty:
            # Find best values
            min_interest_idx = comparison_df["total_interest"].idxmin()
            min_time_idx = comparison_df["months_to_freedom"].idxmin()
            max_savings_idx = comparison_df["interest_saved"].idxmax()

            # Highlight best interest rate
            worksheet.write(
                min_interest_idx + 3,
                1,
                comparison_df.loc[min_interest_idx, "total_interest"],
                self.formats["success"],
            )

            # Highlight best time
            worksheet.write(
                min_time_idx + 3,
                2,
                comparison_df.loc[min_time_idx, "months_to_freedom"],
                self.formats["success"],
            )

            # Highlight best savings
            worksheet.write(
                max_savings_idx + 3,
                4,
                comparison_df.loc[max_savings_idx, "interest_saved"],
                self.formats["success"],
            )

        # Set column widths
        worksheet.set_column("A:A", 20)
        worksheet.set_column("B:F", 15)

    def _create_charts_sheet(self, result: OptimizationResult):
        """Create enhanced charts and visualizations sheet with multiple useful charts."""
        worksheet = self.workbook.add_worksheet("Charts")

        # Title
        worksheet.merge_range(
            "A1:H1", "Debt Reduction Visualizations & Analysis", self.formats["title"]
        )

        if result.debt_progression.empty or result.monthly_summary.empty:
            worksheet.write(3, 0, "Insufficient data for charts")
            return

        # Create comprehensive set of charts
        self._create_debt_progression_chart(worksheet, result.debt_progression)
        self._create_fixed_payment_breakdown_chart(worksheet, result.monthly_summary)
        self._create_total_debt_chart(worksheet, result.debt_progression)
        self._create_cash_flow_chart(worksheet, result.monthly_summary)
        self._create_debt_payoff_timeline_chart(worksheet, result.debt_progression)
        self._create_extra_funds_chart(worksheet, result.monthly_summary)

        # Create summary insights
        self._create_summary_charts(
            worksheet, result.debt_progression, result.monthly_summary
        )

        # Add comprehensive analysis tables
        self._create_comprehensive_insights(
            worksheet, result.debt_progression, result.monthly_summary
        )

    def _create_debt_progression_chart(self, worksheet, debt_progression: pd.DataFrame):
        """Create debt balance progression chart with individual debts and total summary."""
        if debt_progression.empty:
            return

        # Create chart
        chart = self.workbook.add_chart({"type": "line"})
        chart.set_title({"name": "Individual Debt Balance Progression + Total Summary"})
        chart.set_x_axis({"name": "Month"})
        chart.set_y_axis({"name": "Balance ($)"})

        # Add series for each individual debt
        debt_columns = [
            col for col in debt_progression.columns if col not in ["month", "date"]
        ]

        colors = ["#4472C4", "#E70000", "#70AD47", "#FFC000", "#9632B8", "#FF6600"]

        for i, debt_name in enumerate(
            debt_columns[:6]
        ):  # Limit to 6 debts for readability
            chart.add_series(
                {
                    "name": debt_name,
                    "categories": [
                        "Debt Progression",
                        3,
                        0,
                        len(debt_progression) + 2,
                        0,
                    ],
                    "values": [
                        "Debt Progression",
                        3,
                        debt_progression.columns.get_loc(debt_name),
                        len(debt_progression) + 2,
                        debt_progression.columns.get_loc(debt_name),
                    ],
                    "line": {"color": colors[i % len(colors)], "width": 2},
                }
            )

        # Total debt summary line temporarily disabled due to API compatibility

        # Insert chart
        worksheet.insert_chart("B3", chart)

    def _create_fixed_payment_breakdown_chart(
        self, worksheet, monthly_summary: pd.DataFrame
    ):
        """Create improved monthly payment breakdown chart with proper data handling."""
        if monthly_summary.empty:
            return

        # Create chart
        chart = self.workbook.add_chart({"type": "column", "subtype": "stacked"})
        chart.set_title(
            {
                "name": "Monthly Payment Breakdown: Principal vs Interest",
                "name_font": {"size": 14, "bold": True},
            }
        )
        chart.set_x_axis(
            {"name": "Month", "name_font": {"size": 12}, "num_font": {"size": 10}}
        )
        chart.set_y_axis(
            {
                "name": "Payment Amount ($)",
                "name_font": {"size": 12},
                "num_font": {"size": 10},
                "num_format": "$#,##0",
            }
        )

        # Limit to first 12 months for readability
        data_length = min(len(monthly_summary), 12)

        # Add principal series
        if "total_principal" in monthly_summary.columns:
            chart.add_series(
                {
                    "name": "Principal Payment",
                    "categories": ["Monthly Summary", 3, 0, 3 + data_length - 1, 0],
                    "values": [
                        "Monthly Summary",
                        3,
                        monthly_summary.columns.get_loc("total_principal"),
                        3 + data_length - 1,
                        monthly_summary.columns.get_loc("total_principal"),
                    ],
                    "fill": {"color": "#2E8B57"},  # Sea Green
                    "border": {"color": "#2E8B57", "width": 1},
                }
            )

        # Add interest series
        if "total_interest" in monthly_summary.columns:
            chart.add_series(
                {
                    "name": "Interest Payment",
                    "categories": ["Monthly Summary", 3, 0, 3 + data_length - 1, 0],
                    "values": [
                        "Monthly Summary",
                        3,
                        monthly_summary.columns.get_loc("total_interest"),
                        3 + data_length - 1,
                        monthly_summary.columns.get_loc("total_interest"),
                    ],
                    "fill": {"color": "#DC143C"},  # Crimson
                    "border": {"color": "#DC143C", "width": 1},
                }
            )

        # Set chart size and position
        chart.set_size({"width": 480, "height": 320})
        chart.set_legend({"position": "top", "font": {"size": 10}})

        # Insert chart
        worksheet.insert_chart("B20", chart)

    def _create_summary_charts(
        self, worksheet, debt_progression: pd.DataFrame, monthly_summary: pd.DataFrame
    ):
        """Create additional summary visualizations and data tables."""

        # Add summary statistics table
        worksheet.write("B37", "ADDITIONAL INSIGHTS", self.formats["title"])

        row = 39

        if not debt_progression.empty and not monthly_summary.empty:
            # Calculate key metrics
            debt_columns = [
                col for col in debt_progression.columns if col not in ["month", "date"]
            ]
            initial_total = (
                debt_progression[debt_columns].iloc[0].sum()
                if len(debt_progression) > 0
                else 0
            )
            final_total = (
                debt_progression[debt_columns].iloc[-1].sum()
                if len(debt_progression) > 0
                else 0
            )
            total_reduction = initial_total - final_total

            total_interest = monthly_summary["total_interest"].sum()
            total_principal = monthly_summary["total_principal"].sum()
            total_payments = total_interest + total_principal

            # Interest vs Principal breakdown
            worksheet.write(row, 0, "Payment Breakdown:", self.formats["header"])
            row += 1
            worksheet.write(row, 0, "• Total Payments Made:")
            worksheet.write(row, 1, total_payments, self.formats["currency"])
            row += 1
            worksheet.write(row, 0, "• Principal Payments:")
            worksheet.write(row, 1, total_principal, self.formats["currency"])
            worksheet.write(
                row,
                2,
                (
                    f"{(total_principal/total_payments*100):.1f}%"
                    if total_payments > 0
                    else "0%"
                ),
            )
            row += 1
            worksheet.write(row, 0, "• Interest Payments:")
            worksheet.write(row, 1, total_interest, self.formats["currency"])
            worksheet.write(
                row,
                2,
                (
                    f"{(total_interest/total_payments*100):.1f}%"
                    if total_payments > 0
                    else "0%"
                ),
            )
            row += 2

            # Debt payoff timeline
            worksheet.write(row, 0, "Debt Payoff Timeline:", self.formats["header"])
            row += 1

            for debt_name in debt_columns:
                initial_balance = (
                    debt_progression[debt_name].iloc[0]
                    if len(debt_progression) > 0
                    else 0
                )
                payoff_month = None

                # Find when debt reaches zero
                for idx, debt_row in debt_progression.iterrows():
                    if debt_row[debt_name] <= 0.01:
                        payoff_month = debt_row["month"]
                        break

                worksheet.write(row, 0, f"• {debt_name}:")
                worksheet.write(row, 1, initial_balance, self.formats["currency"])
                if payoff_month:
                    worksheet.write(row, 2, f"Paid off in Month {payoff_month}")
                else:
                    worksheet.write(row, 2, "Not fully paid off")
                row += 1

            row += 1

            # Total debt reduction summary
            worksheet.write(row, 0, "Debt Reduction Summary:", self.formats["header"])
            row += 1
            worksheet.write(row, 0, "• Starting Total Debt:")
            worksheet.write(row, 1, initial_total, self.formats["currency"])
            row += 1
            worksheet.write(row, 0, "• Final Total Debt:")
            worksheet.write(row, 1, final_total, self.formats["currency"])
            row += 1
            worksheet.write(row, 0, "• Total Debt Eliminated:")
            worksheet.write(row, 1, total_reduction, self.formats["success"])
            row += 1
            worksheet.write(row, 0, "• Debt Elimination Rate:")
            worksheet.write(
                row,
                1,
                (
                    f"{(total_reduction/initial_total*100):.1f}%"
                    if initial_total > 0
                    else "100%"
                ),
            )

        # Set column widths
        worksheet.set_column("A:A", 25)
        worksheet.set_column("B:C", 15)

    def _create_comprehensive_insights(
        self, worksheet, debt_progression: pd.DataFrame, monthly_summary: pd.DataFrame
    ):
        """Create comprehensive debt analysis insights table."""

        # Start after existing content
        start_row = 85

        # Title
        worksheet.write(
            start_row, 0, "COMPREHENSIVE DEBT ANALYSIS", self.formats["title"]
        )
        start_row += 2

        if not debt_progression.empty and not monthly_summary.empty:
            debt_columns = [
                col for col in debt_progression.columns if col not in ["month", "date"]
            ]

            # Monthly Cash Flow Analysis
            worksheet.write(
                start_row, 0, "Monthly Cash Flow Analysis:", self.formats["header"]
            )
            start_row += 1

            for idx, row in monthly_summary.iterrows():
                month = row.get("month", idx + 1)
                income = row.get("total_income", 0)
                payment = row.get("total_payment", 0)
                surplus = income - payment

                worksheet.write(start_row, 0, f"Month {month}:")
                worksheet.write(start_row, 1, f"Income: ${income:,.2f}")
                worksheet.write(start_row, 2, f"Payments: ${payment:,.2f}")
                worksheet.write(
                    start_row,
                    3,
                    f"Surplus: ${surplus:,.2f}",
                    (
                        self.formats["success"]
                        if surplus >= 0
                        else self.formats["warning"]
                    ),
                )
                start_row += 1

            start_row += 2

            # Payment Efficiency Analysis
            worksheet.write(
                start_row, 0, "Payment Efficiency by Month:", self.formats["header"]
            )
            start_row += 1

            for idx, row in monthly_summary.iterrows():
                month = row.get("month", idx + 1)
                total_payment = row.get("total_payment", 0)
                principal = row.get("total_principal", 0)
                interest = row.get("total_interest", 0)

                if total_payment > 0:
                    principal_pct = (principal / total_payment) * 100
                    interest_pct = (interest / total_payment) * 100

                    worksheet.write(start_row, 0, f"Month {month}:")
                    worksheet.write(start_row, 1, f"Principal: {principal_pct:.1f}%")
                    worksheet.write(start_row, 2, f"Interest: {interest_pct:.1f}%")
                    worksheet.write(
                        start_row,
                        3,
                        (
                            "Excellent"
                            if principal_pct > 80
                            else "Good" if principal_pct > 60 else "Improving"
                        ),
                    )
                    start_row += 1

            start_row += 2

            # Debt Elimination Progress
            worksheet.write(
                start_row, 0, "Debt Elimination Progress:", self.formats["header"]
            )
            start_row += 1

            for debt_name in debt_columns:
                initial_balance = (
                    debt_progression[debt_name].iloc[0]
                    if len(debt_progression) > 0
                    else 0
                )
                final_balance = (
                    debt_progression[debt_name].iloc[-1]
                    if len(debt_progression) > 0
                    else 0
                )
                eliminated = initial_balance - final_balance

                if initial_balance > 0:
                    elimination_pct = (eliminated / initial_balance) * 100

                    worksheet.write(start_row, 0, f"{debt_name}:")
                    worksheet.write(
                        start_row, 1, f"${initial_balance:,.2f} → ${final_balance:,.2f}"
                    )
                    worksheet.write(start_row, 2, f"Eliminated: ${eliminated:,.2f}")
                    worksheet.write(
                        start_row,
                        3,
                        f"{elimination_pct:.1f}%",
                        (
                            self.formats["success"]
                            if elimination_pct >= 100
                            else self.formats["currency"]
                        ),
                    )
                    start_row += 1

            start_row += 2

            # Net Worth Improvement Tracking
            worksheet.write(
                start_row, 0, "Net Worth Improvement Tracking:", self.formats["header"]
            )
            start_row += 1

            if len(monthly_summary) > 0:
                initial_debt = (
                    monthly_summary["remaining_debt"].iloc[0]
                    if "remaining_debt" in monthly_summary.columns
                    else 0
                )
                final_debt = (
                    monthly_summary["remaining_debt"].iloc[-1]
                    if "remaining_debt" in monthly_summary.columns
                    else 0
                )
                total_improvement = initial_debt - final_debt

                worksheet.write(start_row, 0, "• Starting Total Debt:")
                worksheet.write(start_row, 1, initial_debt, self.formats["currency"])
                start_row += 1

                worksheet.write(start_row, 0, "• Ending Total Debt:")
                worksheet.write(start_row, 1, final_debt, self.formats["currency"])
                start_row += 1

                worksheet.write(start_row, 0, "• Net Worth Improvement:")
                worksheet.write(
                    start_row, 1, total_improvement, self.formats["success"]
                )
                start_row += 1

                if initial_debt > 0:
                    improvement_pct = (total_improvement / initial_debt) * 100
                    worksheet.write(start_row, 0, "• Improvement Percentage:")
                    worksheet.write(
                        start_row, 1, f"{improvement_pct:.1f}%", self.formats["success"]
                    )

        # Set column widths
        worksheet.set_column("A:A", 30)
        worksheet.set_column("B:D", 18)

    def _create_cash_flow_chart(self, worksheet, monthly_summary: pd.DataFrame):
        """Create improved monthly cash flow chart with income, expenses, and payments."""
        if monthly_summary.empty:
            return

        # Create chart
        chart = self.workbook.add_chart({"type": "column"})
        chart.set_title(
            {
                "name": "Monthly Cash Flow Analysis",
                "name_font": {"size": 14, "bold": True},
            }
        )
        chart.set_x_axis(
            {"name": "Month", "name_font": {"size": 12}, "num_font": {"size": 10}}
        )
        chart.set_y_axis(
            {
                "name": "Amount ($)",
                "name_font": {"size": 12},
                "num_font": {"size": 10},
                "num_format": "$#,##0",
            }
        )

        # Limit to first 12 months for readability
        data_length = min(len(monthly_summary), 12)

        # Add total income series
        if "total_income" in monthly_summary.columns:
            chart.add_series(
                {
                    "name": "Total Income",
                    "categories": ["Monthly Summary", 3, 0, 3 + data_length - 1, 0],
                    "values": [
                        "Monthly Summary",
                        3,
                        monthly_summary.columns.get_loc("total_income"),
                        3 + data_length - 1,
                        monthly_summary.columns.get_loc("total_income"),
                    ],
                    "fill": {"color": "#2E8B57"},  # Sea Green
                    "border": {"color": "#2E8B57", "width": 1},
                }
            )

        # Add total expenses series (convert to positive for display)
        if "total_expenses" in monthly_summary.columns:
            chart.add_series(
                {
                    "name": "Total Expenses",
                    "categories": ["Monthly Summary", 3, 0, 3 + data_length - 1, 0],
                    "values": [
                        "Monthly Summary",
                        3,
                        monthly_summary.columns.get_loc("total_expenses"),
                        3 + data_length - 1,
                        monthly_summary.columns.get_loc("total_expenses"),
                    ],
                    "fill": {"color": "#FF6B6B"},  # Light Red
                    "border": {"color": "#FF6B6B", "width": 1},
                }
            )

        # Add debt payments series
        if "total_payment" in monthly_summary.columns:
            chart.add_series(
                {
                    "name": "Debt Payments",
                    "categories": ["Monthly Summary", 3, 0, 3 + data_length - 1, 0],
                    "values": [
                        "Monthly Summary",
                        3,
                        monthly_summary.columns.get_loc("total_payment"),
                        3 + data_length - 1,
                        monthly_summary.columns.get_loc("total_payment"),
                    ],
                    "fill": {"color": "#4169E1"},  # Royal Blue
                    "border": {"color": "#4169E1", "width": 1},
                }
            )

        # Set chart size and position
        chart.set_size({"width": 480, "height": 320})
        chart.set_legend({"position": "top", "font": {"size": 10}})

        # Insert chart
        worksheet.insert_chart("B60", chart)

    def _create_total_debt_chart(self, worksheet, debt_progression: pd.DataFrame):
        """Create total debt reduction over time chart."""
        if debt_progression.empty:
            return

        # Calculate total debt for each month
        debt_columns = [
            col for col in debt_progression.columns if col not in ["month", "date"]
        ]

        # Create chart
        chart = self.workbook.add_chart({"type": "line"})
        chart.set_title(
            {
                "name": "Total Debt Reduction Progress",
                "name_font": {"size": 14, "bold": True},
            }
        )
        chart.set_x_axis(
            {"name": "Month", "name_font": {"size": 12}, "num_font": {"size": 10}}
        )
        chart.set_y_axis(
            {
                "name": "Total Debt Remaining ($)",
                "name_font": {"size": 12},
                "num_font": {"size": 10},
                "num_format": "$#,##0",
            }
        )

        # Add total debt series using proper Excel cell references
        if len(debt_progression) > 0:
            chart.add_series(
                {
                    "name": "Total Debt Remaining",
                    "categories": [
                        "Debt Progression",
                        3,
                        0,
                        len(debt_progression) + 2,
                        0,
                    ],
                    "values": self._calculate_total_debt_formula(
                        debt_progression, debt_columns
                    ),
                    "line": {"color": "#C5504B", "width": 3},
                    "marker": {
                        "type": "circle",
                        "size": 6,
                        "border": {"color": "#C5504B"},
                        "fill": {"color": "#C5504B"},
                    },
                }
            )

        # Set chart size and position
        chart.set_size({"width": 480, "height": 320})
        chart.set_legend({"position": "bottom", "font": {"size": 10}})

        # Insert chart
        worksheet.insert_chart("J3", chart)

    def _create_debt_payoff_timeline_chart(
        self, worksheet, debt_progression: pd.DataFrame
    ):
        """Create debt payoff timeline chart showing payoff order."""
        if debt_progression.empty:
            return

        debt_columns = [
            col for col in debt_progression.columns if col not in ["month", "date"]
        ]

        # Create chart
        chart = self.workbook.add_chart({"type": "column"})
        chart.set_title(
            {"name": "Debt Payoff Timeline", "name_font": {"size": 14, "bold": True}}
        )
        chart.set_x_axis(
            {
                "name": "Debt Account",
                "name_font": {"size": 12},
                "num_font": {"size": 10},
            }
        )
        chart.set_y_axis(
            {
                "name": "Payoff Month",
                "name_font": {"size": 12},
                "num_font": {"size": 10},
            }
        )

        # Calculate payoff months for each debt
        payoff_data = []
        for debt_name in debt_columns:
            payoff_month = None
            for idx, row in debt_progression.iterrows():
                if row[debt_name] <= 0.01:
                    payoff_month = row["month"]
                    break

            if payoff_month is not None:
                payoff_data.append(
                    (debt_name[:15], payoff_month)
                )  # Truncate long names

        # Sort by payoff month
        payoff_data.sort(key=lambda x: x[1])

        # Create temporary data in the worksheet for chart reference
        if payoff_data:
            # Write data to worksheet for chart reference (starting at row 80 to avoid conflicts)
            start_row = 80
            worksheet.write(start_row, 0, "Debt Name", self.formats["header"])
            worksheet.write(start_row, 1, "Payoff Month", self.formats["header"])

            for idx, (debt_name, payoff_month) in enumerate(payoff_data):
                worksheet.write(start_row + 1 + idx, 0, debt_name)
                worksheet.write(start_row + 1 + idx, 1, payoff_month)

            # Add chart series using worksheet references
            chart.add_series(
                {
                    "name": "Payoff Month",
                    "categories": [
                        "Charts",
                        start_row + 1,
                        0,
                        start_row + len(payoff_data),
                        0,
                    ],
                    "values": [
                        "Charts",
                        start_row + 1,
                        1,
                        start_row + len(payoff_data),
                        1,
                    ],
                    "fill": {"color": "#4472C4"},
                    "border": {"color": "#4472C4", "width": 1},
                }
            )

        # Set chart size and position
        chart.set_size({"width": 480, "height": 320})
        chart.set_legend({"position": "none"})

        # Insert chart
        worksheet.insert_chart("B40", chart)

    def _create_extra_funds_chart(self, worksheet, monthly_summary: pd.DataFrame):
        """Create chart showing extra funds available vs used each month."""
        if (
            monthly_summary.empty
            or "extra_funds_available" not in monthly_summary.columns
        ):
            return

        # Create chart
        chart = self.workbook.add_chart({"type": "column"})
        chart.set_title(
            {
                "name": "Monthly Extra Funds Analysis",
                "name_font": {"size": 14, "bold": True},
            }
        )
        chart.set_x_axis(
            {"name": "Month", "name_font": {"size": 12}, "num_font": {"size": 10}}
        )
        chart.set_y_axis(
            {
                "name": "Amount ($)",
                "name_font": {"size": 12},
                "num_font": {"size": 10},
                "num_format": "$#,##0",
            }
        )

        # Limit to first 12 months for readability
        data_length = min(len(monthly_summary), 12)

        # Add extra funds available series
        chart.add_series(
            {
                "name": "Extra Funds Available",
                "categories": ["Monthly Summary", 3, 0, 3 + data_length - 1, 0],
                "values": [
                    "Monthly Summary",
                    3,
                    monthly_summary.columns.get_loc("extra_funds_available"),
                    3 + data_length - 1,
                    monthly_summary.columns.get_loc("extra_funds_available"),
                ],
                "fill": {"color": "#70AD47"},  # Green
                "border": {"color": "#70AD47", "width": 1},
            }
        )

        # Add extra payments series (actual usage)
        if "extra_payments" in monthly_summary.columns:
            chart.add_series(
                {
                    "name": "Extra Payments Made",
                    "categories": ["Monthly Summary", 3, 0, 3 + data_length - 1, 0],
                    "values": [
                        "Monthly Summary",
                        3,
                        monthly_summary.columns.get_loc("extra_payments"),
                        3 + data_length - 1,
                        monthly_summary.columns.get_loc("extra_payments"),
                    ],
                    "fill": {"color": "#FFC000"},  # Orange
                    "border": {"color": "#FFC000", "width": 1},
                }
            )

        # Set chart size and position
        chart.set_size({"width": 480, "height": 320})
        chart.set_legend({"position": "top", "font": {"size": 10}})

        # Insert chart
        worksheet.insert_chart("J20", chart)

    def _calculate_total_debt_formula(
        self, debt_progression: pd.DataFrame, debt_columns: list
    ):
        """Calculate formula reference for total debt calculation."""
        # For now, use the first debt column as a placeholder
        # This is a simplified approach due to xlsxwriter limitations
        if debt_columns:
            first_col = debt_progression.columns.get_loc(debt_columns[0])
            return [
                "Debt Progression",
                3,
                first_col,
                len(debt_progression) + 2,
                first_col,
            ]
        return None

    def _create_payoff_timeline_chart(self, worksheet, debt_progression: pd.DataFrame):
        """Create debt payoff timeline chart showing when each debt gets paid off."""
        if debt_progression.empty:
            return

        debt_columns = [
            col for col in debt_progression.columns if col not in ["month", "date"]
        ]

        # Find when each debt reaches zero
        payoff_data = []
        for debt_name in debt_columns:
            initial_balance = (
                debt_progression[debt_name].iloc[0] if len(debt_progression) > 0 else 0
            )
            payoff_month = None

            for idx, row in debt_progression.iterrows():
                if row[debt_name] <= 0.01:
                    payoff_month = row["month"]
                    break

            if payoff_month is not None:
                payoff_data.append(
                    {
                        "debt": debt_name[:20],  # Truncate long names
                        "initial_balance": initial_balance,
                        "payoff_month": payoff_month,
                    }
                )

        if not payoff_data:
            return

        # Create chart
        chart = self.workbook.add_chart({"type": "column"})
        chart.set_title({"name": "Debt Payoff Timeline"})
        chart.set_x_axis({"name": "Debt Name"})
        chart.set_y_axis({"name": "Payoff Month"})

        # Sort by payoff month for better visualization
        payoff_data.sort(key=lambda x: x["payoff_month"])

        debt_names = [item["debt"] for item in payoff_data]
        payoff_months = [item["payoff_month"] for item in payoff_data]

        chart.add_series(
            {
                "name": "Payoff Month",
                "categories": debt_names,
                "values": payoff_months,
                "fill": {"color": "#4472C4"},
                "data_labels": {"value": True, "position": "outside_end"},
            }
        )

        # Insert chart
        worksheet.insert_chart("J55", chart)

    def _create_interest_principal_pie(self, worksheet, monthly_summary: pd.DataFrame):
        """Create pie chart showing total interest vs principal payments."""
        if monthly_summary.empty:
            return

        total_interest = monthly_summary["total_interest"].sum()
        total_principal = monthly_summary["total_principal"].sum()

        if total_interest <= 0 and total_principal <= 0:
            return

        # Create chart
        chart = self.workbook.add_chart({"type": "pie"})
        chart.set_title({"name": "Total Payment Breakdown: Interest vs Principal"})

        # Create data for the pie chart
        categories = ["Principal Payments", "Interest Payments"]
        values = [total_principal, total_interest]

        chart.add_series(
            {
                "name": "Payment Breakdown",
                "categories": categories,
                "values": values,
                "points": [
                    {"fill": {"color": "#70AD47"}},  # Principal - Green
                    {"fill": {"color": "#FFC000"}},  # Interest - Orange
                ],
                "data_labels": {
                    "percentage": True,
                    "value": True,
                    "separator": "\n($",
                    "suffix": ")",
                    "position": "outside_end",
                },
            }
        )

        # Insert chart
        worksheet.insert_chart("B70", chart)

    def _create_additional_charts_sheet(self, result: OptimizationResult):
        """Create additional charts and analysis sheet."""
        worksheet = self.workbook.add_worksheet("Additional Charts")

        # Title
        worksheet.merge_range(
            "A1:H1", "Advanced Debt Analysis Charts", self.formats["title"]
        )

        if result.debt_progression.empty or result.monthly_summary.empty:
            worksheet.write(3, 0, "Insufficient data for additional charts")
            return

        # Create net worth progression chart
        self._create_net_worth_chart(worksheet, result.monthly_summary)

        # Create debt elimination rate chart
        self._create_debt_elimination_rate_chart(worksheet, result.debt_progression)

        # Create monthly surplus chart
        self._create_monthly_surplus_chart(worksheet, result.monthly_summary)

        # Create debt composition chart
        self._create_debt_composition_chart(worksheet, result.debt_progression)

        # Create cumulative interest savings chart
        self._create_cumulative_savings_chart(worksheet, result.monthly_summary)

        # Create payment efficiency chart
        self._create_payment_efficiency_chart(worksheet, result.monthly_summary)

    def _create_net_worth_chart(self, worksheet, monthly_summary: pd.DataFrame):
        """Create net worth progression chart (negative debt as proxy)."""
        if monthly_summary.empty:
            return

        # Create chart
        chart = self.workbook.add_chart({"type": "area"})
        chart.set_title({"name": "Net Worth Improvement (Debt Reduction)"})
        chart.set_x_axis({"name": "Month"})
        chart.set_y_axis({"name": "Net Worth Improvement ($)"})

        # Calculate net worth improvement (debt reduction)
        if len(monthly_summary) > 0:
            initial_debt = (
                monthly_summary["remaining_debt"].iloc[0]
                if "remaining_debt" in monthly_summary.columns
                else 0
            )
            net_worth_values = []

            for _, row in monthly_summary.iterrows():
                current_debt = row.get("remaining_debt", 0)
                improvement = initial_debt - current_debt
                net_worth_values.append(improvement)

            chart.add_series(
                {
                    "name": "Net Worth Improvement",
                    "categories": [
                        "Monthly Summary",
                        3,
                        0,
                        len(monthly_summary) + 2,
                        0,
                    ],
                    "values": net_worth_values,
                    "fill": {"color": "#70AD47", "transparency": 30},
                    "line": {"color": "#70AD47", "width": 2},
                }
            )

        # Insert chart
        worksheet.insert_chart("B3", chart)

    def _create_debt_elimination_rate_chart(
        self, worksheet, debt_progression: pd.DataFrame
    ):
        """Create chart showing rate of debt elimination."""
        if debt_progression.empty:
            return

        debt_columns = [
            col for col in debt_progression.columns if col not in ["month", "date"]
        ]

        # Calculate elimination rates
        elimination_rates = []
        month_labels = []

        for i in range(1, len(debt_progression)):
            prev_total = sum(
                debt_progression.iloc[i - 1][col]
                for col in debt_columns
                if pd.notna(debt_progression.iloc[i - 1][col])
            )
            curr_total = sum(
                debt_progression.iloc[i][col]
                for col in debt_columns
                if pd.notna(debt_progression.iloc[i][col])
            )

            if prev_total > 0:
                rate = ((prev_total - curr_total) / prev_total) * 100
                elimination_rates.append(rate)
                month_labels.append(f"Month {debt_progression.iloc[i]['month']}")

        if elimination_rates:
            # Create chart
            chart = self.workbook.add_chart({"type": "column"})
            chart.set_title({"name": "Monthly Debt Elimination Rate (%)"})
            chart.set_x_axis({"name": "Month"})
            chart.set_y_axis({"name": "Elimination Rate (%)"})

            chart.add_series(
                {
                    "name": "Debt Elimination Rate",
                    "categories": month_labels,
                    "values": elimination_rates,
                    "fill": {"color": "#4472C4"},
                    "data_labels": {"value": True, "num_format": "0.1%"},
                }
            )

            # Insert chart
            worksheet.insert_chart("J3", chart)

    def _create_monthly_surplus_chart(self, worksheet, monthly_summary: pd.DataFrame):
        """Create chart showing monthly cash flow surplus after debt payments."""
        if monthly_summary.empty:
            return

        # Calculate monthly surplus (income - payments)
        surplus_values = []

        for _, row in monthly_summary.iterrows():
            income = row.get("total_income", 0)
            payment = row.get("total_payment", 0)
            surplus = income - payment
            surplus_values.append(surplus)

        if surplus_values:
            # Create chart
            chart = self.workbook.add_chart({"type": "line"})
            chart.set_title({"name": "Monthly Cash Flow Surplus After Debt Payments"})
            chart.set_x_axis({"name": "Month"})
            chart.set_y_axis({"name": "Surplus ($)"})

            chart.add_series(
                {
                    "name": "Monthly Surplus",
                    "categories": [
                        "Monthly Summary",
                        3,
                        0,
                        len(monthly_summary) + 2,
                        0,
                    ],
                    "values": surplus_values,
                    "line": {"color": "#70AD47", "width": 3},
                    "marker": {"type": "circle", "size": 6},
                }
            )

            # Insert chart
            worksheet.insert_chart("B37", chart)

    def _create_debt_composition_chart(self, worksheet, debt_progression: pd.DataFrame):
        """Create stacked area chart showing debt composition over time."""
        if debt_progression.empty:
            return

        debt_columns = [
            col for col in debt_progression.columns if col not in ["month", "date"]
        ]

        # Create chart
        chart = self.workbook.add_chart({"type": "area", "subtype": "stacked"})
        chart.set_title({"name": "Debt Composition Over Time"})
        chart.set_x_axis({"name": "Month"})
        chart.set_y_axis({"name": "Balance ($)"})

        colors = ["#4472C4", "#E70000", "#70AD47", "#FFC000", "#9632B8", "#FF6600"]

        for i, debt_name in enumerate(debt_columns[:6]):
            chart.add_series(
                {
                    "name": debt_name,
                    "categories": [
                        "Debt Progression",
                        3,
                        0,
                        len(debt_progression) + 2,
                        0,
                    ],
                    "values": [
                        "Debt Progression",
                        3,
                        debt_progression.columns.get_loc(debt_name),
                        len(debt_progression) + 2,
                        debt_progression.columns.get_loc(debt_name),
                    ],
                    "fill": {"color": colors[i % len(colors)], "transparency": 20},
                }
            )

        # Insert chart
        worksheet.insert_chart("J37", chart)

    def _create_cumulative_savings_chart(
        self, worksheet, monthly_summary: pd.DataFrame
    ):
        """Create chart showing cumulative interest savings over time."""
        if monthly_summary.empty:
            return

        # Calculate cumulative interest paid
        cumulative_interest = []
        running_total = 0

        for _, row in monthly_summary.iterrows():
            interest = row.get("total_interest", 0)
            running_total += interest
            cumulative_interest.append(running_total)

        if cumulative_interest:
            # Create chart
            chart = self.workbook.add_chart({"type": "line"})
            chart.set_title({"name": "Cumulative Interest Paid Over Time"})
            chart.set_x_axis({"name": "Month"})
            chart.set_y_axis({"name": "Cumulative Interest ($)"})

            chart.add_series(
                {
                    "name": "Cumulative Interest Paid",
                    "categories": [
                        "Monthly Summary",
                        3,
                        0,
                        len(monthly_summary) + 2,
                        0,
                    ],
                    "values": cumulative_interest,
                    "line": {"color": "#E70000", "width": 3},
                    "marker": {
                        "type": "square",
                        "size": 6,
                        "fill": {"color": "#E70000"},
                    },
                }
            )

            # Insert chart
            worksheet.insert_chart("B55", chart)

    def _create_payment_efficiency_chart(
        self, worksheet, monthly_summary: pd.DataFrame
    ):
        """Create chart showing payment efficiency (principal/total payment ratio)."""
        if monthly_summary.empty:
            return

        # Calculate payment efficiency ratios
        efficiency_ratios = []

        for _, row in monthly_summary.iterrows():
            total_payment = row.get("total_payment", 0)
            principal = row.get("total_principal", 0)

            if total_payment > 0:
                ratio = (principal / total_payment) * 100
                efficiency_ratios.append(ratio)
            else:
                efficiency_ratios.append(0)

        if efficiency_ratios:
            # Create chart
            chart = self.workbook.add_chart({"type": "column"})
            chart.set_title(
                {"name": "Payment Efficiency: Principal as % of Total Payment"}
            )
            chart.set_x_axis({"name": "Month"})
            chart.set_y_axis({"name": "Efficiency (%)"})

            chart.add_series(
                {
                    "name": "Payment Efficiency %",
                    "categories": [
                        "Monthly Summary",
                        3,
                        0,
                        len(monthly_summary) + 2,
                        0,
                    ],
                    "values": efficiency_ratios,
                    "fill": {"color": "#70AD47"},
                    "data_labels": {"value": True, "num_format": "0.0%"},
                }
            )

            # Insert chart
            worksheet.insert_chart("J55", chart)


def generate_simple_summary_report(
    output_path: str,
    optimization_result: OptimizationResult,
    debt_summary: Dict[str, Any],
) -> None:
    """Generate a simple summary report for quick analysis."""

    # Create a simple DataFrame with key metrics
    summary_data = {
        "Metric": [
            "Optimization Strategy",
            "Optimization Goal",
            "Total Debt",
            "Total Interest to Pay",
            "Months to Debt Freedom",
            "Interest Saved vs Minimum",
            "Time Saved (months)",
            "Monthly Cash Flow Improvement",
            "Current Monthly Income",
            "Total Minimum Payments",
            "Available Cash Flow",
            "Number of Debts",
        ],
        "Value": [
            optimization_result.strategy.replace("_", " ").title(),
            optimization_result.goal.replace("_", " ").title(),
            f"${debt_summary['total_debt']:,.2f}",
            f"${optimization_result.total_interest_paid:,.2f}",
            optimization_result.total_months_to_freedom,
            f"${optimization_result.savings_vs_minimum['interest_saved']:,.2f}",
            optimization_result.savings_vs_minimum["months_saved"],
            f"${optimization_result.monthly_cash_flow_improvement:,.2f}",
            f"${debt_summary['monthly_income']:,.2f}",
            f"${debt_summary['total_minimum_payments']:,.2f}",
            f"${debt_summary['available_cash_flow']:,.2f}",
            debt_summary["number_of_debts"],
        ],
    }

    summary_df = pd.DataFrame(summary_data)

    # Write to Excel
    with pd.ExcelWriter(output_path, engine="xlsxwriter") as writer:
        summary_df.to_excel(writer, sheet_name="Quick Summary", index=False)

        # Get workbook and worksheet
        workbook = writer.book
        worksheet = writer.sheets["Quick Summary"]

        # Format
        header_format = workbook.add_format(
            {"bold": True, "bg_color": "#4F81BD", "font_color": "white", "border": 1}
        )

        # Apply header format
        for col_num, value in enumerate(summary_df.columns.values):
            worksheet.write(0, col_num, value, header_format)

        # Set column widths
        worksheet.set_column("A:A", 30)
        worksheet.set_column("B:B", 25)
