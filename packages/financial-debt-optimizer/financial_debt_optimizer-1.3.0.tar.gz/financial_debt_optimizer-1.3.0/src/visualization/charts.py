from pathlib import Path
from typing import Dict, List, Optional, Tuple

import matplotlib.pyplot as plt
import pandas as pd

from core.debt_optimizer import OptimizationResult
from core.financial_calc import Debt


class DebtVisualization:
    """Create visualizations for debt analysis and progress tracking."""

    def __init__(self, style: str = "seaborn-v0_8-whitegrid"):
        """Initialize visualization with style settings."""
        try:
            plt.style.use(style)
        except OSError:
            # Fallback to default if seaborn style not available
            plt.style.use("default")

        # Set color palette
        self.colors = [
            "#1f77b4",
            "#ff7f0e",
            "#2ca02c",
            "#d62728",
            "#9467bd",
            "#8c564b",
            "#e377c2",
            "#7f7f7f",
            "#bcbd22",
            "#17becf",
        ]

    def plot_debt_progression(
        self,
        debt_progression: pd.DataFrame,
        save_path: Optional[str] = None,
        figsize: Tuple[int, int] = (12, 8),
    ) -> plt.Figure:
        """Create a line chart showing debt balance progression over time."""

        fig, ax = plt.subplots(figsize=figsize)

        # Get debt columns (exclude month and date)
        debt_columns = [
            col for col in debt_progression.columns if col not in ["month", "date"]
        ]

        # Plot each debt
        for i, debt_name in enumerate(
            debt_columns[:8]
        ):  # Limit to 8 debts for readability
            color = self.colors[i % len(self.colors)]
            ax.plot(
                debt_progression["month"],
                debt_progression[debt_name],
                label=debt_name,
                linewidth=2.5,
                color=color,
                marker="o",
                markersize=4,
            )

        # Formatting
        ax.set_xlabel("Month", fontsize=12)
        ax.set_ylabel("Debt Balance ($)", fontsize=12)
        ax.set_title(
            "Debt Balance Progression Over Time", fontsize=16, fontweight="bold", pad=20
        )

        # Format y-axis as currency
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f"${x:,.0f}"))

        # Add grid
        ax.grid(True, alpha=0.3)

        # Legend
        if len(debt_columns) <= 6:
            ax.legend(bbox_to_anchor=(1.05, 1), loc="upper left")
        else:
            ax.legend(bbox_to_anchor=(1.05, 1), loc="upper left", ncol=2)

        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches="tight")

        return fig

    def plot_payment_breakdown(
        self,
        monthly_summary: pd.DataFrame,
        save_path: Optional[str] = None,
        figsize: Tuple[int, int] = (12, 8),
    ) -> plt.Figure:
        """Create a stacked bar chart showing principal vs interest payments."""

        fig, ax = plt.subplots(figsize=figsize)

        # Create stacked bar chart
        bar_width = 0.8
        months = monthly_summary["month"]

        ax.bar(
            months,
            monthly_summary["total_principal"],
            bar_width,
            label="Principal Payment",
            color="#2ca02c",
            alpha=0.8,
        )

        ax.bar(
            months,
            monthly_summary["total_interest"],
            bar_width,
            bottom=monthly_summary["total_principal"],
            label="Interest Payment",
            color="#ff7f0e",
            alpha=0.8,
        )

        # Formatting
        ax.set_xlabel("Month", fontsize=12)
        ax.set_ylabel("Payment Amount ($)", fontsize=12)
        ax.set_title(
            "Monthly Payment Breakdown: Principal vs Interest",
            fontsize=16,
            fontweight="bold",
            pad=20,
        )

        # Format y-axis as currency
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f"${x:,.0f}"))

        # Add grid
        ax.grid(True, alpha=0.3, axis="y")

        # Legend
        ax.legend(loc="upper right")

        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches="tight")

        return fig

    def plot_strategy_comparison(
        self,
        comparison_df: pd.DataFrame,
        save_path: Optional[str] = None,
        figsize: Tuple[int, int] = (14, 10),
    ) -> plt.Figure:
        """Create a comparison chart for different debt strategies."""

        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=figsize)

        strategies = comparison_df["strategy"].str.replace("_", " ").str.title()

        # Total Interest Comparison
        bars1 = ax1.bar(
            strategies,
            comparison_df["total_interest"],
            color=self.colors[: len(strategies)],
        )
        ax1.set_title("Total Interest Paid", fontsize=14, fontweight="bold")
        ax1.set_ylabel("Total Interest ($)")
        ax1.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f"${x:,.0f}"))
        ax1.tick_params(axis="x", rotation=45)

        # Add value labels on bars
        for bar in bars1:
            height = bar.get_height()
            ax1.text(
                bar.get_x() + bar.get_width() / 2.0,
                height,
                f"${height:,.0f}",
                ha="center",
                va="bottom",
                fontsize=10,
            )

        # Time to Freedom Comparison
        bars2 = ax2.bar(
            strategies,
            comparison_df["months_to_freedom"],
            color=self.colors[: len(strategies)],
        )
        ax2.set_title("Time to Debt Freedom", fontsize=14, fontweight="bold")
        ax2.set_ylabel("Months")
        ax2.tick_params(axis="x", rotation=45)

        # Add value labels on bars
        for bar in bars2:
            height = bar.get_height()
            years = int(height // 12)
            months = int(height % 12)
            ax2.text(
                bar.get_x() + bar.get_width() / 2.0,
                height,
                f"{years}y {months}m",
                ha="center",
                va="bottom",
                fontsize=10,
            )

        # Interest Saved Comparison
        bars3 = ax3.bar(
            strategies,
            comparison_df["interest_saved"],
            color=self.colors[: len(strategies)],
        )
        ax3.set_title(
            "Interest Saved vs Minimum Payments", fontsize=14, fontweight="bold"
        )
        ax3.set_ylabel("Interest Saved ($)")
        ax3.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f"${x:,.0f}"))
        ax3.tick_params(axis="x", rotation=45)

        # Add value labels on bars
        for bar in bars3:
            height = bar.get_height()
            ax3.text(
                bar.get_x() + bar.get_width() / 2.0,
                height,
                f"${height:,.0f}",
                ha="center",
                va="bottom",
                fontsize=10,
            )

        # Months Saved Comparison
        bars4 = ax4.bar(
            strategies,
            comparison_df["months_saved"],
            color=self.colors[: len(strategies)],
        )
        ax4.set_title("Time Saved vs Minimum Payments", fontsize=14, fontweight="bold")
        ax4.set_ylabel("Months Saved")
        ax4.tick_params(axis="x", rotation=45)

        # Add value labels on bars
        for bar in bars4:
            height = bar.get_height()
            ax4.text(
                bar.get_x() + bar.get_width() / 2.0,
                height,
                f"{height}",
                ha="center",
                va="bottom",
                fontsize=10,
            )

        plt.suptitle(
            "Debt Repayment Strategy Comparison", fontsize=16, fontweight="bold"
        )
        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches="tight")

        return fig

    def plot_debt_composition(
        self,
        debts: List[Debt],
        save_path: Optional[str] = None,
        figsize: Tuple[int, int] = (10, 8),
    ) -> plt.Figure:
        """Create a pie chart showing debt composition by balance."""

        fig, ax = plt.subplots(figsize=figsize)

        # Prepare data
        debt_names = [debt.name for debt in debts]
        debt_balances = [debt.balance for debt in debts]

        # Create pie chart
        pie_result = ax.pie(
            debt_balances,
            labels=debt_names,
            autopct="%1.1f%%",
            startangle=90,
            colors=self.colors[: len(debts)],
            explode=[0.05] * len(debts),  # Slight separation for each slice
        )

        # Unpack the pie chart result safely
        if len(pie_result) >= 3:
            wedges, texts, autotexts = pie_result[:3]
        else:
            wedges, texts = pie_result[:2]
            autotexts = None

        # Formatting
        ax.set_title(
            "Debt Composition by Balance", fontsize=16, fontweight="bold", pad=20
        )

        # Improve text formatting
        if autotexts:
            for autotext in autotexts:
                autotext.set_color("white")
                autotext.set_fontweight("bold")
                autotext.set_fontsize(10)

        # Add legend with balance amounts
        legend_labels = [
            f"{name}: ${balance:,.2f}"
            for name, balance in zip(debt_names, debt_balances)
        ]
        ax.legend(legend_labels, bbox_to_anchor=(1.05, 1), loc="upper left")

        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches="tight")

        return fig

    def plot_interest_rate_comparison(
        self,
        debts: List[Debt],
        save_path: Optional[str] = None,
        figsize: Tuple[int, int] = (12, 8),
    ) -> plt.Figure:
        """Create a horizontal bar chart comparing interest rates."""

        fig, ax = plt.subplots(figsize=figsize)

        # Sort debts by interest rate
        sorted_debts = sorted(debts, key=lambda d: d.interest_rate, reverse=True)

        debt_names = [debt.name for debt in sorted_debts]
        interest_rates = [debt.interest_rate for debt in sorted_debts]
        balances = [debt.balance for debt in sorted_debts]

        # Create horizontal bar chart
        bars = ax.barh(debt_names, interest_rates, color=self.colors[: len(debts)])

        # Color bars based on interest rate (red = high, green = low)
        max_rate = max(interest_rates)
        min_rate = min(interest_rates)

        for i, (bar, rate) in enumerate(zip(bars, interest_rates)):
            # Normalize rate to 0-1 scale
            norm_rate = (
                (rate - min_rate) / (max_rate - min_rate) if max_rate > min_rate else 0
            )
            # Color from green (low) to red (high)
            from matplotlib.cm import get_cmap

            colormap = get_cmap("RdYlGn_r")
            color = colormap(norm_rate)
            bar.set_color(color)

        # Formatting
        ax.set_xlabel("Interest Rate (%)", fontsize=12)
        ax.set_title(
            "Debt Interest Rate Comparison", fontsize=16, fontweight="bold", pad=20
        )

        # Add value labels on bars
        for i, (bar, balance) in enumerate(zip(bars, balances)):
            width = bar.get_width()
            ax.text(
                width + 0.1,
                bar.get_y() + bar.get_height() / 2,
                f"{width:.2f}% (${balance:,.0f})",
                ha="left",
                va="center",
                fontsize=10,
            )

        # Add grid
        ax.grid(True, alpha=0.3, axis="x")

        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches="tight")

        return fig

    def create_dashboard(
        self,
        optimization_result: OptimizationResult,
        debts: List[Debt],
        comparison_df: Optional[pd.DataFrame] = None,
        save_path: Optional[str] = None,
        figsize: Tuple[int, int] = (20, 16),
    ) -> plt.Figure:
        """Create a comprehensive dashboard with multiple charts."""

        if comparison_df is not None:
            fig = plt.figure(figsize=figsize)
            gs = fig.add_gridspec(3, 3, hspace=0.3, wspace=0.3)
        else:
            fig = plt.figure(figsize=(16, 12))
            gs = fig.add_gridspec(2, 2, hspace=0.3, wspace=0.3)

        # Debt Progression Chart
        if comparison_df is not None:
            ax1 = fig.add_subplot(gs[0, :2])
        else:
            ax1 = fig.add_subplot(gs[0, :])

        debt_columns = [
            col
            for col in optimization_result.debt_progression.columns
            if col not in ["month", "date"]
        ]
        for i, debt_name in enumerate(debt_columns[:6]):
            color = self.colors[i % len(self.colors)]
            ax1.plot(
                optimization_result.debt_progression["month"],
                optimization_result.debt_progression[debt_name],
                label=debt_name,
                linewidth=2,
                color=color,
            )
        ax1.set_title("Debt Balance Progression", fontsize=14, fontweight="bold")
        ax1.set_xlabel("Month")
        ax1.set_ylabel("Balance ($)")
        ax1.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f"${x:,.0f}"))
        ax1.legend(bbox_to_anchor=(1.05, 1), loc="upper left")
        ax1.grid(True, alpha=0.3)

        # Payment Breakdown Chart
        if comparison_df is not None:
            ax2 = fig.add_subplot(gs[0, 2])
        else:
            ax2 = fig.add_subplot(gs[1, 0])
        ax2.bar(
            optimization_result.monthly_summary["month"][:12],  # First 12 months
            optimization_result.monthly_summary["total_principal"][:12],
            label="Principal",
            color="#2ca02c",
            alpha=0.8,
        )
        ax2.bar(
            optimization_result.monthly_summary["month"][:12],
            optimization_result.monthly_summary["total_interest"][:12],
            bottom=optimization_result.monthly_summary["total_principal"][:12],
            label="Interest",
            color="#ff7f0e",
            alpha=0.8,
        )
        ax2.set_title("Payment Breakdown (First Year)", fontsize=14, fontweight="bold")
        ax2.set_xlabel("Month")
        ax2.set_ylabel("Payment ($)")
        ax2.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f"${x:,.0f}"))
        ax2.legend()
        ax2.grid(True, alpha=0.3, axis="y")

        # Debt Composition Pie Chart
        if comparison_df is not None:
            ax3 = fig.add_subplot(gs[1, 0])
        else:
            ax3 = fig.add_subplot(gs[1, 1])

        debt_names = [debt.name for debt in debts]
        debt_balances = [debt.balance for debt in debts]
        ax3.pie(
            debt_balances,
            labels=debt_names,
            autopct="%1.1f%%",
            colors=self.colors[: len(debts)],
        )
        ax3.set_title("Debt Composition", fontsize=14, fontweight="bold")

        # Interest Rate Comparison (only show if there are multiple charts)
        if comparison_df is not None:
            ax4 = fig.add_subplot(gs[1, 1])
            sorted_debts = sorted(debts, key=lambda d: d.interest_rate, reverse=True)
            debt_names = [debt.name for debt in sorted_debts]
            interest_rates = [debt.interest_rate for debt in sorted_debts]
            bars = ax4.barh(debt_names, interest_rates, color=self.colors[: len(debts)])
            ax4.set_title("Interest Rates", fontsize=14, fontweight="bold")
            ax4.set_xlabel("Interest Rate (%)")

        # Strategy Comparison (if available)
        if comparison_df is not None:
            ax5 = fig.add_subplot(gs[1, 2])
            strategies = comparison_df["strategy"].str.replace("_", " ").str.title()
            bars = ax5.bar(
                strategies,
                comparison_df["total_interest"],
                color=self.colors[: len(strategies)],
            )
            ax5.set_title("Strategy Comparison", fontsize=14, fontweight="bold")
            ax5.set_ylabel("Total Interest ($)")
            ax5.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f"${x:,.0f}"))
            ax5.tick_params(axis="x", rotation=45)

            # Summary metrics
            ax6 = fig.add_subplot(gs[2, :])
            ax6.axis("off")

            # Create summary text
            total_debt = sum(debt.balance for debt in debts)
            summary_text = f"""
OPTIMIZATION SUMMARY
Strategy: {optimization_result.strategy.replace('_', ' ').title()}
Total Debt: ${total_debt:,.2f}
Total Interest: ${optimization_result.total_interest_paid:,.2f}
Time to Freedom: {optimization_result.total_months_to_freedom} months
Interest Saved: ${optimization_result.savings_vs_minimum['interest_saved']:,.2f}
Time Saved: {optimization_result.savings_vs_minimum['months_saved']} months
            """.strip()

            ax6.text(
                0.5,
                0.5,
                summary_text,
                transform=ax6.transAxes,
                fontsize=14,
                verticalalignment="center",
                horizontalalignment="center",
                bbox=dict(boxstyle="round", facecolor="lightblue", alpha=0.8),
            )

        plt.suptitle("Debt Optimization Dashboard", fontsize=18, fontweight="bold")

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches="tight")

        return fig


def save_all_charts(
    optimization_result: OptimizationResult,
    debts: List[Debt],
    comparison_df: Optional[pd.DataFrame] = None,
    output_dir: str = "charts",
) -> Dict[str, str]:
    """Save all charts to individual files."""

    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)

    viz = DebtVisualization()
    saved_files = {}

    # Debt progression chart
    fig1 = viz.plot_debt_progression(optimization_result.debt_progression)
    debt_prog_path = output_path / "debt_progression.png"
    fig1.savefig(debt_prog_path, dpi=300, bbox_inches="tight")
    saved_files["debt_progression"] = str(debt_prog_path)
    plt.close(fig1)

    # Payment breakdown chart
    fig2 = viz.plot_payment_breakdown(optimization_result.monthly_summary)
    payment_path = output_path / "payment_breakdown.png"
    fig2.savefig(payment_path, dpi=300, bbox_inches="tight")
    saved_files["payment_breakdown"] = str(payment_path)
    plt.close(fig2)

    # Debt composition chart
    fig3 = viz.plot_debt_composition(debts)
    composition_path = output_path / "debt_composition.png"
    fig3.savefig(composition_path, dpi=300, bbox_inches="tight")
    saved_files["debt_composition"] = str(composition_path)
    plt.close(fig3)

    # Interest rate comparison
    fig4 = viz.plot_interest_rate_comparison(debts)
    interest_path = output_path / "interest_rates.png"
    fig4.savefig(interest_path, dpi=300, bbox_inches="tight")
    saved_files["interest_rates"] = str(interest_path)
    plt.close(fig4)

    # Strategy comparison (if available)
    if comparison_df is not None:
        fig5 = viz.plot_strategy_comparison(comparison_df)
        strategy_path = output_path / "strategy_comparison.png"
        fig5.savefig(strategy_path, dpi=300, bbox_inches="tight")
        saved_files["strategy_comparison"] = str(strategy_path)
        plt.close(fig5)

    # Dashboard
    fig6 = viz.create_dashboard(optimization_result, debts, comparison_df)
    dashboard_path = output_path / "dashboard.png"
    fig6.savefig(dashboard_path, dpi=300, bbox_inches="tight")
    saved_files["dashboard"] = str(dashboard_path)
    plt.close(fig6)

    return saved_files
