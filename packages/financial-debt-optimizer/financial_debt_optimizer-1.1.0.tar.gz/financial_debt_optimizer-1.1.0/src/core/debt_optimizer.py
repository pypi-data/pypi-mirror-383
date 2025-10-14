from dataclasses import dataclass
from datetime import date, datetime, timedelta
from typing import List, Dict, Tuple, Optional, Any
import pandas as pd
import numpy as np
from enum import Enum

from .financial_calc import (
    Debt, Income, RecurringExpense, FutureIncome, DebtAnalyzer, 
    generate_amortization_schedule, calculate_total_monthly_income
)


class OptimizationGoal(Enum):
    """Available optimization goals."""
    MINIMIZE_INTEREST = "minimize_interest"
    MINIMIZE_TIME = "minimize_time"
    MAXIMIZE_CASHFLOW = "maximize_cashflow"


class PaymentStrategy(Enum):
    """Available payment strategies."""
    AVALANCHE = "avalanche"  # Highest interest rate first
    SNOWBALL = "snowball"    # Lowest balance first
    HYBRID = "hybrid"        # Balance of both strategies
    CUSTOM = "custom"        # User-defined order


@dataclass
class DecisionLogEntry:
    """Individual decision log entry tracking priority changes and rationale."""
    timestamp: datetime
    month: int
    decision_type: str  # 'strategy_selection', 'priority_change', 'payment_allocation', 'goal_adjustment'
    description: str
    rationale: str
    impact: str
    data_snapshot: Dict[str, Any]


@dataclass
class MonthlyExtraFunds:
    """Track extra funds available and their allocation for each month."""
    month: int
    date: date
    total_income: float
    required_minimums: float
    recurring_expenses: float
    available_extra: float
    allocated_extra: float
    remaining_extra: float
    allocation_decisions: List[Dict[str, Any]]


@dataclass
class OptimizationResult:
    """Results from debt optimization analysis."""
    strategy: str
    goal: str
    total_interest_paid: float
    total_months_to_freedom: int
    monthly_cash_flow_improvement: float
    payment_schedule: pd.DataFrame
    monthly_summary: pd.DataFrame
    debt_progression: pd.DataFrame
    savings_vs_minimum: Dict[str, float]
    decision_log: List[DecisionLogEntry]
    monthly_extra_funds: List[MonthlyExtraFunds]


@dataclass
class DebtPaymentPlan:
    """Individual debt payment plan."""
    debt_name: str
    current_balance: float
    monthly_payment: float
    months_to_payoff: int
    total_interest: float
    payoff_order: int


class DebtOptimizer:
    """Main debt optimization engine."""
    
    def __init__(self, debts: List[Debt], income_sources: List[Income], 
                 recurring_expenses: List[RecurringExpense] = None, 
                 future_income: List[FutureIncome] = None,
                 future_expenses: List = None,
                 settings: Dict[str, Any] = None):
        """Initialize the debt optimizer with debts, income, expenses, and future income."""
        self.debts = debts.copy()
        self.income_sources = income_sources.copy()
        self.recurring_expenses = recurring_expenses.copy() if recurring_expenses else []
        self.future_income = future_income.copy() if future_income else []
        self.future_expenses = future_expenses.copy() if future_expenses else []
        self.settings = settings or {}
        
        # Calculate basic metrics
        self.total_debt = DebtAnalyzer.calculate_total_debt(self.debts)
        self.total_minimum_payments = DebtAnalyzer.calculate_total_minimum_payments(self.debts)
        self.monthly_income = calculate_total_monthly_income(self.income_sources)
        
        # Calculate monthly recurring expenses
        self.total_monthly_recurring_expenses = self._calculate_monthly_recurring_expenses()
        
        # Default settings
        self.current_bank_balance = self.settings.get('current_bank_balance', 2000.0)
        
        # Calculate available cash flow after minimum payments AND recurring expenses
        self.available_cash_flow = self.monthly_income - self.total_minimum_payments - self.total_monthly_recurring_expenses
        
        # Use available cash flow for extra debt payments (after accounting for all expenses)
        self.available_extra_payment = max(0, self.available_cash_flow)
        
        # Initialize decision logging
        self.decision_log: List[DecisionLogEntry] = []
        self.monthly_extra_funds: List[MonthlyExtraFunds] = []
        self.current_simulation_month = 0
    
    def _calculate_monthly_recurring_expenses(self) -> float:
        """Calculate total monthly equivalent of all recurring expenses."""
        total_monthly_expenses = 0.0
        
        for expense in self.recurring_expenses:
            if expense.frequency == 'monthly':
                total_monthly_expenses += expense.amount
            elif expense.frequency == 'bi-weekly':
                # Bi-weekly = 26 times per year = 26/12 per month
                total_monthly_expenses += expense.amount * (26 / 12)
            elif expense.frequency == 'quarterly':
                # Quarterly = 4 times per year = 4/12 per month
                total_monthly_expenses += expense.amount * (4 / 12)
            elif expense.frequency == 'annually':
                # Annual = 1 time per year = 1/12 per month
                total_monthly_expenses += expense.amount * (1 / 12)
        
        return total_monthly_expenses
    
    def calculate_available_extra_payment(self, additional_extra: float = 0.0) -> float:
        """Calculate available extra payment amount."""
        # Use automatically calculated available extra payment plus any additional amount
        return self.available_extra_payment + additional_extra
    
    def log_decision(self, decision_type: str, description: str, rationale: str, 
                    impact: str, data_snapshot: Dict[str, Any] = None) -> None:
        """Log a decision for audit trail and learning purposes."""
        entry = DecisionLogEntry(
            timestamp=datetime.now(),
            month=self.current_simulation_month,
            decision_type=decision_type,
            description=description,
            rationale=rationale,
            impact=impact,
            data_snapshot=data_snapshot or {}
        )
        self.decision_log.append(entry)
    
    def track_monthly_extra_funds(self, month: int, date_val: date, total_income: float, 
                                 required_minimums: float, recurring_expenses: float,
                                 available_extra: float, allocated_extra: float,
                                 allocation_decisions: List[Dict[str, Any]]) -> None:
        """Track extra funds and their allocation for each month."""
        monthly_extra = MonthlyExtraFunds(
            month=month,
            date=date_val,
            total_income=total_income,
            required_minimums=required_minimums,
            recurring_expenses=recurring_expenses,
            available_extra=available_extra,
            allocated_extra=allocated_extra,
            remaining_extra=available_extra - allocated_extra,
            allocation_decisions=allocation_decisions
        )
        self.monthly_extra_funds.append(monthly_extra)
    
    def _get_strategy_selection_rationale(self, best_result: 'OptimizationResult', 
                                        all_results: List['OptimizationResult'], 
                                        goal: OptimizationGoal) -> str:
        """Generate rationale for why a specific strategy was selected."""
        if goal == OptimizationGoal.MINIMIZE_INTEREST:
            interest_savings = [r.total_interest_paid for r in all_results]
            return f"Selected for lowest interest cost: ${best_result.total_interest_paid:,.2f} vs others: {[f'${i:,.2f}' for i in interest_savings if i != best_result.total_interest_paid]}"
        elif goal == OptimizationGoal.MINIMIZE_TIME:
            time_comparisons = [r.total_months_to_freedom for r in all_results]
            return f"Selected for shortest payoff time: {best_result.total_months_to_freedom} months vs others: {[t for t in time_comparisons if t != best_result.total_months_to_freedom]}"
        elif goal == OptimizationGoal.MAXIMIZE_CASHFLOW:
            cashflow_comparisons = [r.monthly_cash_flow_improvement for r in all_results]
            return f"Selected for best cash flow: ${best_result.monthly_cash_flow_improvement:,.2f}/month vs others: {[f'${c:,.2f}' for c in cashflow_comparisons if c != best_result.monthly_cash_flow_improvement]}"
        else:
            return "Selected based on overall optimization metrics"
    
    def optimize_debt_strategy(
        self, 
        goal: OptimizationGoal = OptimizationGoal.MINIMIZE_INTEREST,
        extra_payment: float = 0.0
    ) -> OptimizationResult:
        """Find the optimal debt repayment strategy based on the specified goal."""
        
        # Log initial decision
        self.log_decision(
            decision_type="goal_selection",
            description=f"Selected optimization goal: {goal.value}",
            rationale=f"User specified goal to {goal.value.replace('_', ' ')}",
            impact="Determines strategy comparison criteria",
            data_snapshot={
                "goal": goal.value,
                "extra_payment": extra_payment,
                "total_debt": self.total_debt,
                "available_extra": self.available_extra_payment
            }
        )
        
        # Test different strategies
        strategies_to_test = [PaymentStrategy.AVALANCHE, PaymentStrategy.SNOWBALL]
        
        if len(self.debts) > 2:
            strategies_to_test.append(PaymentStrategy.HYBRID)
        
        # Log strategy testing decision
        self.log_decision(
            decision_type="strategy_evaluation",
            description=f"Testing {len(strategies_to_test)} strategies: {[s.value for s in strategies_to_test]}",
            rationale="Comparing multiple strategies to find optimal approach for selected goal",
            impact="Will determine which strategy provides best results",
            data_snapshot={"strategies": [s.value for s in strategies_to_test]}
        )
        
        results = []
        
        for strategy in strategies_to_test:
            # Clear decision log for each strategy simulation
            temp_log = self.decision_log.copy()
            temp_extra = self.monthly_extra_funds.copy()
            
            result = self._simulate_strategy(
                strategy=strategy,
                extra_payment=extra_payment
            )
            
            # Store strategy-specific logs
            result.decision_log = self.decision_log.copy()
            result.monthly_extra_funds = self.monthly_extra_funds.copy()
            
            # Reset for next strategy
            self.decision_log = temp_log
            self.monthly_extra_funds = temp_extra
            
            results.append(result)
        
        # Select best strategy based on goal
        best_result = self._select_best_strategy(results, goal)
        
        # Note: Final strategy selection decision will be added directly to the best_result.decision_log
        
        # Update result with final decision log (preserve the strategy-specific data that was already stored)
        # The decision_log and monthly_extra_funds were already correctly set in lines 241-242
        # Just add the final strategy selection decision to the existing log
        if hasattr(best_result, 'decision_log') and best_result.decision_log:
            best_result.decision_log.extend([
                DecisionLogEntry(
                    timestamp=datetime.now(),
                    month=self.current_simulation_month,
                    decision_type="strategy_selection",
                    description=f"Selected {best_result.strategy} strategy",
                    rationale=self._get_strategy_selection_rationale(best_result, results, goal),
                    impact=f"Will save ${best_result.savings_vs_minimum['interest_saved']:,.2f} in interest",
                    data_snapshot={
                        "selected_strategy": best_result.strategy,
                        "total_interest": best_result.total_interest_paid,
                        "months_to_freedom": best_result.total_months_to_freedom
                    }
                )
            ])
        
        return best_result
    
    def _simulate_strategy(
        self, 
        strategy: PaymentStrategy,
        extra_payment: float
    ) -> OptimizationResult:
        """Simulate a specific debt repayment strategy."""
        
        # Order debts according to strategy
        if strategy == PaymentStrategy.AVALANCHE:
            ordered_debts = DebtAnalyzer.rank_debts_by_avalanche(self.debts)
            debt_ordering_reason = "Highest interest rate first to minimize total interest cost"
        elif strategy == PaymentStrategy.SNOWBALL:
            ordered_debts = DebtAnalyzer.rank_debts_by_snowball(self.debts)
            debt_ordering_reason = "Lowest balance first to maximize psychological momentum"
        elif strategy == PaymentStrategy.HYBRID:
            ordered_debts = self._create_hybrid_order()
            debt_ordering_reason = "Balanced approach considering both interest rate and balance size"
        else:
            ordered_debts = self.debts.copy()
            debt_ordering_reason = "Original order maintained"
        
        # Log debt ordering decision
        self.log_decision(
            decision_type="priority_change",
            description=f"Ordered debts using {strategy.value} strategy",
            rationale=debt_ordering_reason,
            impact=f"Payment priority: {[d.name for d in ordered_debts]}",
            data_snapshot={
                "strategy": strategy.value,
                "debt_order": [{
                    "name": d.name,
                    "balance": d.balance,
                    "rate": d.interest_rate,
                    "minimum": d.minimum_payment
                } for d in ordered_debts]
            }
        )
        
        # Calculate total available extra payment
        total_extra = self.calculate_available_extra_payment(extra_payment)
        
        # Log extra payment allocation decision
        self.log_decision(
            decision_type="payment_allocation",
            description=f"Allocated ${total_extra:,.2f} extra payment per month",
            rationale=f"Using available cash flow (${self.available_extra_payment:,.2f}) plus additional extra (${extra_payment:,.2f})",
            impact=f"Will accelerate debt payoff and reduce interest costs",
            data_snapshot={
                "base_extra_payment": self.available_extra_payment,
                "additional_extra": extra_payment,
                "total_extra": total_extra
            }
        )
        
        # Simulate month-by-month payments
        simulation_result = self._run_payment_simulation(
            ordered_debts, total_extra
        )
        
        return OptimizationResult(
            strategy=strategy.value,
            goal="simulation",  # Will be updated by calling function
            total_interest_paid=simulation_result['total_interest'],
            total_months_to_freedom=simulation_result['total_months'],
            monthly_cash_flow_improvement=simulation_result['cash_flow_improvement'],
            payment_schedule=simulation_result['payment_schedule'],
            monthly_summary=simulation_result['monthly_summary'],
            debt_progression=simulation_result['debt_progression'],
            savings_vs_minimum=simulation_result['savings_comparison'],
            decision_log=[],  # Will be populated by calling function
            monthly_extra_funds=[]  # Will be populated by calling function
        )
    
    def _create_hybrid_order(self) -> List[Debt]:
        """Create a hybrid ordering that balances interest rate and balance."""
        # Calculate a hybrid score: normalized interest rate + normalized inverse balance
        if not self.debts:
            return []
        
        max_rate = max(debt.interest_rate for debt in self.debts)
        min_rate = min(debt.interest_rate for debt in self.debts)
        max_balance = max(debt.balance for debt in self.debts)
        min_balance = min(debt.balance for debt in self.debts)
        
        def hybrid_score(debt: Debt) -> float:
            # Normalize interest rate (0-1)
            rate_score = (debt.interest_rate - min_rate) / (max_rate - min_rate) if max_rate > min_rate else 0.5
            
            # Normalize inverse balance (0-1, smaller balance = higher score)
            balance_score = (max_balance - debt.balance) / (max_balance - min_balance) if max_balance > min_balance else 0.5
            
            # Weight interest rate more heavily (70% rate, 30% balance)
            return 0.7 * rate_score + 0.3 * balance_score
        
        return sorted(self.debts, key=hybrid_score, reverse=True)
    
    def _run_payment_simulation(
        self, 
        ordered_debts: List[Debt], 
        extra_payment: float
    ) -> Dict[str, Any]:
        """Run detailed chronological event-by-event payment simulation with enhanced decision logging."""
        
        # Log the start of simulation with detailed debt prioritization info
        self.log_decision(
            decision_type="priority_change",
            description=f"Starting simulation with debt priority order",
            rationale=self._get_debt_prioritization_rationale(ordered_debts),
            impact=f"Will focus extra payments on priority debts to optimize strategy",
            data_snapshot={
                "debt_priority_order": [{
                    "rank": idx + 1,
                    "name": debt.name,
                    "balance": debt.balance,
                    "interest_rate": debt.interest_rate,
                    "minimum_payment": debt.minimum_payment,
                    "priority_score": self._calculate_priority_score(debt, ordered_debts)
                } for idx, debt in enumerate(ordered_debts)],
                "total_extra_available": extra_payment
            }
        )
        
        # Initialize tracking variables
        current_debts = [(debt, debt.balance) for debt in ordered_debts]
        initial_debts = [(debt, debt.balance) for debt in ordered_debts]  # Save initial state for progression
        payment_schedule = []
        monthly_summary = []
        debt_progression = []
        
        total_interest_paid = 0.0
        bank_balance = self.current_bank_balance
        current_simulation_month = 0
        
        start_date = date.today()
        end_date = start_date + timedelta(days=365 * 10)  # 10 years maximum
        
        # Validate debt due dates
        for debt in ordered_debts:
            if not isinstance(debt.due_date, int) or debt.due_date < 1 or debt.due_date > 31:
                raise ValueError(f"Invalid due_date for debt '{debt.name}': {debt.due_date}")
        
        # Add opening balance
        payment_schedule.append({
            'date': start_date,
            'type': 'opening_balance',
            'description': 'Opening Bank Balance',
            'amount': 0.0,
            'interest_portion': 0.0,
            'principal_portion': 0.0,
            'remaining_balance': sum(balance for _, balance in current_debts),
            'bank_balance': bank_balance,
            'debt_balance': '',  # Blank for opening balance
            'debt_name': ''  # Blank for opening balance
        })
        
        # Generate all events chronologically
        events = self._generate_chronological_events(start_date, end_date)
        
        # Process events in chronological order, but group same-day events together
        i = 0
        last_month = None
        
        while i < len(events):
            # Get current date and collect all events for this date
            current_date = events[i][0]
            current_month = (current_date.year, current_date.month)
            
            # Update simulation month counter when we enter a new month
            if last_month != current_month:
                if last_month is not None:
                    current_simulation_month += 1
                last_month = current_month
            
            same_day_events = []
            
            while i < len(events) and events[i][0] == current_date:
                same_day_events.append(events[i])
                i += 1
            
            # Process same-day events in proper order:
            # 1. All income events first
            # 2. All expense events
            # 3. All debt payment events
            # 4. Make extra payments with remaining cash
            
            # Step 1: Process all income events for this day
            daily_income = 0
            for event_date, event_type, event_data in same_day_events:
                if event_type == 'income':
                    income_amount = event_data['amount']
                    bank_balance += income_amount
                    daily_income += income_amount
                    
                    payment_schedule.append({
                        'date': event_date,
                        'type': 'income',
                        'description': event_data['description'],
                        'amount': income_amount,
                        'interest_portion': 0.0,
                        'principal_portion': 0.0,
                        'remaining_balance': sum(balance for _, balance in current_debts),
                        'bank_balance': bank_balance,
                        'debt_balance': '',  # Blank for income
                        'debt_name': ''  # Blank for income
                    })
            
            # Step 2: Process all expense events for this day
            for event_date, event_type, event_data in same_day_events:
                if event_type == 'expense':
                    full_expense_amount = event_data['amount']
                    # Always process the full expense amount (recurring expenses are essential)
                    bank_balance -= full_expense_amount
                    
                    # Always record the expense event
                    payment_schedule.append({
                        'date': event_date,
                        'type': 'expense',
                        'description': event_data['description'],
                        'amount': -full_expense_amount,
                        'interest_portion': 0.0,
                        'principal_portion': 0.0,
                        'remaining_balance': sum(balance for _, balance in current_debts),
                        'bank_balance': bank_balance,
                        'debt_balance': '',  # Blank for expenses
                        'debt_name': ''  # Blank for expenses
                    })
            
            # Step 3: Process all debt payment events for this day (minimum payments only)
            for event_date, event_type, event_data in same_day_events:
                if event_type == 'debt_payment':
                    debt = event_data['debt']
                    
                    # Find current balance for this debt
                    debt_index = None
                    current_balance = 0
                    for idx, (d, bal) in enumerate(current_debts):
                        if d.name == debt.name:
                            debt_index = idx
                            current_balance = bal
                            break
                    
                    # Only make payments on debts that still have a balance
                    if debt_index is not None and current_balance > 0.01:
                        # Calculate interest charge on current balance
                        interest_charge = debt.calculate_interest_charge(current_balance)
                        
                        # Calculate minimum payment required
                        required_payment = min(debt.minimum_payment, current_balance + interest_charge)
                        min_principal = max(0, required_payment - interest_charge)
                        min_principal = min(min_principal, current_balance)
                        
                        # Make the payment if we have funds available
                        actual_payment = min(required_payment, bank_balance)
                        
                        # Update balances
                        if actual_payment > 0.01:
                            current_balance -= min_principal
                            bank_balance -= actual_payment
                            total_interest_paid += interest_charge
                        
                        current_balance = max(0, current_balance)  # Ensure no negative balance
                        
                        # Update debt balance
                        current_debts[debt_index] = (debt, current_balance)
                        
                        # Record the payment
                        payment_schedule.append({
                            'date': event_date,
                            'type': 'payment',
                            'description': f'{debt.name} Payment',
                            'amount': -actual_payment,
                            'interest_portion': interest_charge,
                            'principal_portion': min_principal,
                            'remaining_balance': sum(balance for _, balance in current_debts),
                            'bank_balance': bank_balance,
                            'debt_balance': current_balance,  # Balance of this specific debt after payment
                            'debt_name': debt.name  # Name of the debt being paid
                        })
            
            # Step 4: After all same-day minimum payments, make extra payments with remaining cash
            # Only do this if we received income today or have sufficient cash flow
            if daily_income > 0 or bank_balance > 0:
                # Calculate how much cash we need to reserve for upcoming minimum payments
                # Look ahead to find all minimum payments due before the next income event
                reserved_for_minimums = 0
                
                # Find next income date after current date
                next_income_date = None
                for event_date, event_type, _ in events[i:]:
                    if event_type == 'income' and event_date > current_date:
                        next_income_date = event_date
                        break
                
                # If no future income found, use a reasonable timeframe (30 days)
                if next_income_date is None:
                    next_income_date = current_date + timedelta(days=30)
                
                # Calculate required reserves for all minimum payments AND recurring expenses until next income
                reserved_for_expenses = 0
                for event_date, event_type, event_data in events[i:]:
                    if event_date > next_income_date:
                        break
                    if event_type == 'debt_payment':
                        debt = event_data['debt']
                        # Find current balance for this debt
                        for idx, (d, bal) in enumerate(current_debts):
                            if d.name == debt.name:
                                current_balance = bal
                                break
                        else:
                            current_balance = 0
                        
                        # Only reserve money for debts that still have balances
                        if current_balance > 0.01:
                            interest_charge = debt.calculate_interest_charge(current_balance)
                            min_payment_needed = min(debt.minimum_payment, current_balance + interest_charge)
                            reserved_for_minimums += min_payment_needed
                    elif event_type == 'expense':
                        # Only reserve money for expenses that DON'T happen on the same day as income
                        # Check if there's income on the same day as this expense
                        same_day_income = False
                        for future_event_date, future_event_type, future_event_data in events[i:]:
                            if future_event_date == event_date and future_event_type == 'income':
                                # Check if the income amount covers the expense
                                if future_event_data['amount'] >= event_data['amount']:
                                    same_day_income = True
                                    break
                            elif future_event_date > event_date:
                                break
                        
                        # Only reserve if expense isn't covered by same-day income
                        if not same_day_income:
                            expense_amount = event_data['amount']
                            reserved_for_expenses += expense_amount
                
                total_reserved = reserved_for_minimums + reserved_for_expenses
                # Calculate available cash for extra payments (after reserving for minimum payments AND expenses)
                available_for_extra = max(0, bank_balance - total_reserved)
                
                if available_for_extra > 0.01:
                    # Find the priority debt (first debt in ordered list with remaining balance)
                    priority_debt = None
                    priority_debt_index = None
                    priority_balance = 0
                    
                    for priority_debt_candidate in ordered_debts:
                        for idx, (d, bal) in enumerate(current_debts):
                            if d.name == priority_debt_candidate.name and bal > 0.01:
                                priority_debt = d
                                priority_debt_index = idx
                                priority_balance = bal
                                break
                        if priority_debt:
                            break
                    
                    # Apply extra payment if we have a priority debt
                    if priority_debt and priority_debt_index is not None:
                        # Use available extra cash (limited by debt balance)
                        max_extra_payment = min(available_for_extra, priority_balance)
                        
                        if max_extra_payment > 0.01:
                            # Log the extra payment decision with detailed rationale
                            self.current_simulation_month = current_simulation_month
                            self.log_decision(
                                decision_type="payment_allocation",
                                description=f"Allocated ${max_extra_payment:,.2f} extra payment to {priority_debt.name}",
                                rationale=self._get_extra_payment_rationale(priority_debt, ordered_debts, available_for_extra, priority_balance),
                                impact=f"Reduces {priority_debt.name} balance from ${priority_balance:,.2f} to ${priority_balance - max_extra_payment:,.2f}",
                                data_snapshot={
                                    "available_extra": available_for_extra,
                                    "allocated_amount": max_extra_payment,
                                    "target_debt": priority_debt.name,
                                    "target_balance_before": priority_balance,
                                    "target_balance_after": priority_balance - max_extra_payment,
                                    "target_interest_rate": priority_debt.interest_rate,
                                    "bank_balance_before": bank_balance + max_extra_payment,
                                    "bank_balance_after": bank_balance,
                                    "reserved_for_minimums": reserved_for_minimums,
                                    "reserved_for_expenses": reserved_for_expenses,
                                    "total_reserved": total_reserved
                                }
                            )
                            
                            # Track extra funds allocation for monthly summary
                            self.track_monthly_extra_funds(
                                month=current_simulation_month,
                                date_val=current_date,
                                total_income=daily_income,
                                required_minimums=reserved_for_minimums,
                                recurring_expenses=sum(event[2]['amount'] for event in same_day_events if event[1] == 'expense'),
                                available_extra=available_for_extra,
                                allocated_extra=max_extra_payment,
                                allocation_decisions=[{
                                    "target": priority_debt.name,
                                    "amount": max_extra_payment,
                                    "reason": f"Priority debt (rank #{ordered_debts.index(priority_debt) + 1})",
                                    "impact": f"${priority_balance - max_extra_payment:,.2f} remaining"
                                }]
                            )
                            
                            # Apply the extra payment (pure principal)
                            new_balance = priority_balance - max_extra_payment
                            current_debts[priority_debt_index] = (priority_debt, new_balance)
                            bank_balance -= max_extra_payment
                            
                            # Record the extra payment
                            payment_schedule.append({
                                'date': current_date,
                                'type': 'extra_payment',
                                'description': f'{priority_debt.name} Extra Payment (After Reserving for Minimums & Expenses)',
                                'amount': -max_extra_payment,
                                'interest_portion': 0.0,
                                'principal_portion': max_extra_payment,
                                'remaining_balance': sum(balance for _, balance in current_debts),
                                'bank_balance': bank_balance,
                                'debt_balance': new_balance,  # Balance of this specific debt after payment
                                'debt_name': priority_debt.name  # Name of the debt being paid
                            })
            
            # Check if all debts are paid off AFTER processing all events for this day
            if not any(balance > 0.01 for _, balance in current_debts):
                break
        
        # Generate monthly summaries
        monthly_summary = self._generate_monthly_summaries(payment_schedule)
        debt_progression = self._generate_debt_progression(payment_schedule, initial_debts)
        
        # Calculate total months
        months_to_freedom = 0
        if payment_schedule:
            last_date = payment_schedule[-1]['date']
            months_to_freedom = ((last_date.year - start_date.year) * 12 + 
                               (last_date.month - start_date.month))
        
        # Calculate savings
        minimum_only_interest = self._calculate_minimum_only_scenario()
        
        return {
            'total_interest': total_interest_paid,
            'total_months': max(1, months_to_freedom),
            'cash_flow_improvement': extra_payment,
            'payment_schedule': pd.DataFrame(payment_schedule),
            'monthly_summary': pd.DataFrame(monthly_summary),
            'debt_progression': pd.DataFrame(debt_progression),
            'final_bank_balance': bank_balance,
            'savings_comparison': {
                'interest_saved': max(0, minimum_only_interest - total_interest_paid),
                'months_saved': 0
            }
        }
    
    def _generate_chronological_events(self, start_date: date, end_date: date) -> List[Tuple[date, str, Dict]]:
        """Generate all financial events in chronological order."""
        events = []
        
        # Generate income events
        for income_source in self.income_sources:
            income_dates = income_source.get_payment_dates(start_date, end_date)
            for income_date in income_dates:
                events.append((income_date, 'income', {
                    'amount': income_source.amount,
                    'description': f'{income_source.source} ({income_source.frequency})'
                }))
        
        # Generate future income events
        for future_income in self.future_income:
            # Handle both new format (start_date) and legacy format (date)
            if future_income.is_recurring() and hasattr(future_income, 'get_occurrences'):
                # Recurring income - get all occurrences in the date range
                occurrences = future_income.get_occurrences(start_date, end_date)
                for occurrence_date, amount in occurrences:
                    events.append((occurrence_date, 'income', {
                        'amount': amount,
                        'description': f'{future_income.description} ({future_income.frequency})'
                    }))
            else:
                # One-time income event
                income_date = future_income.date if future_income.date else future_income.start_date
                if income_date and start_date <= income_date <= end_date:
                    events.append((income_date, 'income', {
                        'amount': future_income.amount,
                        'description': future_income.description
                    }))
        
        # Generate recurring expense events
        for expense in self.recurring_expenses:
            expense_dates = expense.get_payment_dates(start_date, end_date)
            for expense_date in expense_dates:
                events.append((expense_date, 'expense', {
                    'amount': expense.amount,
                    'description': expense.description
                }))
        
        # Generate future expense events
        for future_expense in self.future_expenses:
            # Handle both new format (start_date) and legacy format (date)
            if future_expense.is_recurring() and hasattr(future_expense, 'get_occurrences'):
                # Recurring expense - get all occurrences in the date range
                occurrences = future_expense.get_occurrences(start_date, end_date)
                for occurrence_date, amount in occurrences:
                    events.append((occurrence_date, 'expense', {
                        'amount': amount,
                        'description': f'{future_expense.description} ({future_expense.frequency})'
                    }))
            else:
                # One-time expense event
                expense_date = future_expense.date if future_expense.date else future_expense.start_date
                if expense_date and start_date <= expense_date <= end_date:
                    events.append((expense_date, 'expense', {
                        'amount': future_expense.amount,
                        'description': future_expense.description
                    }))
        
        # Generate debt payment events (monthly on due dates)
        current_date = start_date
        while current_date <= end_date:
            for debt in self.debts:
                try:
                    due_date = current_date.replace(day=debt.due_date)
                    if start_date <= due_date <= end_date:
                        events.append((due_date, 'debt_payment', {'debt': debt}))
                except ValueError:
                    # Handle invalid due dates (e.g., Feb 30)
                    last_day = self._get_month_end_date(current_date)
                    if start_date <= last_day <= end_date:
                        events.append((last_day, 'debt_payment', {'debt': debt}))
            
            # Move to next month
            try:
                if current_date.month == 12:
                    current_date = current_date.replace(year=current_date.year + 1, month=1)
                else:
                    current_date = current_date.replace(month=current_date.month + 1)
            except ValueError:
                break
        
        # Sort events chronologically, with income before payments on same day
        def event_sort_key(event):
            event_date, event_type, _ = event
            # Priority: income first, then expenses, then debt payments, then extra payments
            type_priority = {
                'income': 1,
                'expense': 2, 
                'debt_payment': 3,
                'extra_payment': 4
            }
            return (event_date, type_priority.get(event_type, 5))
        
        return sorted(events, key=event_sort_key)
    
    def _generate_monthly_summaries(self, payment_schedule: List[Dict]) -> List[Dict]:
        """Generate enhanced monthly summary data from payment schedule with detailed extra funds and expense tracking."""
        summaries = []
        current_month = None
        month_data = {
            'income': 0, 'regular_income': 0, 'future_income': 0,
            'expenses': 0, 'recurring_expenses': 0, 'future_expenses': 0,
            'payments': 0, 'minimum_payments': 0, 'extra_payments': 0,
            'interest': 0, 'principal': 0,
            'expense_details': [], 'income_details': []
        }
        last_event = None
        
        for event in payment_schedule:
            if not isinstance(event, dict) or 'date' not in event:
                continue
                
            event_date = event['date']
            event_month = (event_date.year, event_date.month)
            last_event = event
            
            if current_month is None:
                current_month = event_month
            elif event_month != current_month:
                # Calculate extra funds available for previous month
                extra_funds_available = max(0, month_data['income'] - month_data['expenses'] - month_data['minimum_payments'])
                
                # Save previous month's data
                if month_data['income'] > 0 or month_data['payments'] > 0 or month_data['expenses'] > 0:
                    summaries.append({
                        'month': len(summaries) + 1,
                        'date': date(current_month[0], current_month[1], 1),
                        'total_income': month_data['income'],
                        'regular_income': month_data['regular_income'],
                        'future_income': month_data['future_income'],
                        'total_expenses': month_data['expenses'],
                        'recurring_expenses': month_data['recurring_expenses'],
                        'total_payment': month_data['payments'],
                        'minimum_payments': month_data['minimum_payments'],
                        'extra_payments': month_data['extra_payments'],
                        'extra_funds_available': extra_funds_available,
                        'total_interest': month_data['interest'],
                        'total_principal': month_data['principal'],
                        'expense_details': '; '.join(month_data['expense_details']) if month_data['expense_details'] else 'None',
                        'income_details': '; '.join(month_data['income_details']) if month_data['income_details'] else 'Regular income only',
                        'remaining_debt': last_event.get('remaining_balance', 0) if last_event else 0,
                        'debts_remaining': 0,  # Will be calculated based on remaining_debt
                        'bank_balance': last_event.get('bank_balance', 0) if last_event else 0
                    })
                
                # Reset for new month
                current_month = event_month
                month_data = {
                    'income': 0, 'regular_income': 0, 'future_income': 0,
                    'expenses': 0, 'recurring_expenses': 0, 'future_expenses': 0,
                    'payments': 0, 'minimum_payments': 0, 'extra_payments': 0,
                    'interest': 0, 'principal': 0,
                    'expense_details': [], 'income_details': []
                }
            
            # Accumulate data for current month
            event_type = event.get('type', '')
            event_amount = event.get('amount', 0)
            event_description = event.get('description', '')
            
            if event_type == 'income':
                month_data['income'] += event_amount
                # Determine if this is regular income or future income
                # Check if this income event comes from a regular income source or future income source
                is_regular_income = False
                
                # Check against regular income sources
                for regular_income in self.income_sources:
                    regular_desc = f"{regular_income.source} ({regular_income.frequency})"
                    if event_description == regular_desc:
                        is_regular_income = True
                        break
                
                if is_regular_income:
                    month_data['regular_income'] += event_amount
                else:
                    month_data['future_income'] += event_amount
                    month_data['income_details'].append(f"{event_description}: ${event_amount:,.2f}")
            
            elif event_type == 'expense':
                month_data['expenses'] += event_amount
                # Determine if this is a recurring expense or future expense
                is_recurring = any(expense.description == event_description for expense in self.recurring_expenses)
                if is_recurring:
                    month_data['recurring_expenses'] += event_amount
                else:
                    month_data['future_expenses'] += event_amount
                month_data['expense_details'].append(f"{event_description}: ${event_amount:.2f}")
            
            elif event_type in ['payment', 'debt_payment']:
                payment_amount = abs(event_amount)
                month_data['payments'] += payment_amount
                month_data['minimum_payments'] += payment_amount
                month_data['interest'] += event.get('interest_portion', 0)
                month_data['principal'] += event.get('principal_portion', 0)
            
            elif event_type == 'extra_payment':
                payment_amount = abs(event_amount)
                month_data['payments'] += payment_amount
                month_data['extra_payments'] += payment_amount
                month_data['interest'] += event.get('interest_portion', 0)
                month_data['principal'] += event.get('principal_portion', 0)
        
        # Add final month if there's data
        if current_month and (month_data['income'] > 0 or month_data['payments'] > 0 or month_data['expenses'] > 0):
            # Calculate extra funds available for final month
            extra_funds_available = max(0, month_data['income'] - month_data['expenses'] - month_data['minimum_payments'])
            
            summaries.append({
                'month': len(summaries) + 1,
                'date': date(current_month[0], current_month[1], 1),
                'total_income': month_data['income'],
                'regular_income': month_data['regular_income'],
                'future_income': month_data['future_income'],
                'total_expenses': month_data['expenses'],
                'recurring_expenses': month_data['recurring_expenses'],
                'total_payment': month_data['payments'],
                'minimum_payments': month_data['minimum_payments'],
                'extra_payments': month_data['extra_payments'],
                'extra_funds_available': extra_funds_available,
                'total_interest': month_data['interest'],
                'total_principal': month_data['principal'],
                'expense_details': '; '.join(month_data['expense_details']) if month_data['expense_details'] else 'None',
                'income_details': '; '.join(month_data['income_details']) if month_data['income_details'] else 'Regular income only',
                'remaining_debt': last_event.get('remaining_balance', 0) if last_event else 0,
                'debts_remaining': 0,
                'bank_balance': last_event.get('bank_balance', 0) if last_event else 0
            })
        
        return summaries
    
    def _calculate_monthly_extra_funds(self, month_tuple, total_income, total_expenses, minimum_payments):
        """Calculate available and allocated extra funds for a specific month using monthly extra funds data."""
        # Try to find matching monthly extra funds data
        month_year = date(month_tuple[0], month_tuple[1], 1) if month_tuple else date.today()
        
        # Look for monthly extra funds entries that match this month
        allocated_extra = 0
        for mef in self.monthly_extra_funds:
            # Check if this monthly extra fund entry is for this month
            if (hasattr(mef, 'date') and 
                mef.date.year == month_year.year and 
                mef.date.month == month_year.month):
                allocated_extra += mef.allocated_extra
        
        # Calculate available extra funds
        # Available = Total Income - Total Expenses - Minimum Payments
        available_extra = max(0, total_income - total_expenses - minimum_payments)
        
        # If we don't have monthly extra funds data, use the calculated amount as both available and allocated
        if allocated_extra == 0 and available_extra > 0:
            allocated_extra = available_extra
        
        return available_extra, allocated_extra
    
    def _generate_debt_progression(self, payment_schedule: List[Dict], initial_debts: List[Tuple]) -> List[Dict]:
        """Generate debt progression data from payment schedule."""
        progression = []
        debt_balances = {debt.name: balance for debt, balance in initial_debts}
        
        current_month = None
        monthly_debt_changes = {debt.name: 0 for debt, _ in initial_debts}
        
        for event in payment_schedule:
            if not isinstance(event, dict) or 'date' not in event:
                continue
                
            event_date = event['date']
            event_month = (event_date.year, event_date.month)
            
            # Update debt balances based on payments (both regular and extra)
            if event['type'] in ['payment', 'extra_payment'] and 'description' in event:
                # Extract debt name from description 
                # (e.g., "Credit Card 1 Payment" -> "Credit Card 1" or "Credit Card 1 Extra Payment (After...)" -> "Credit Card 1")
                description = event['description']
                if description.endswith(' Payment'):
                    # Regular payment: "Debt Name Payment"
                    debt_name = description[:-8]  # Remove ' Payment'
                elif ' Extra Payment (' in description:
                    # Extra payment: "Debt Name Extra Payment (After...)"
                    debt_name = description.split(' Extra Payment (')[0]
                else:
                    # Fallback - use the description as-is
                    debt_name = description
                principal_payment = event.get('principal_portion', 0)
                
                if debt_name in debt_balances and principal_payment > 0:
                    # Track the change for this month
                    if current_month != event_month:
                        # Save previous month's data if we have changes
                        if current_month is not None and any(change > 0 for change in monthly_debt_changes.values()):
                            progression.append({
                                'month': len(progression) + 1,
                                'date': date(current_month[0], current_month[1], 1),
                                **{name: balance for name, balance in debt_balances.items()}
                            })
                        
                        # Reset for new month
                        current_month = event_month
                        monthly_debt_changes = {debt.name: 0 for debt, _ in initial_debts}
                    
                    # Update debt balance
                    debt_balances[debt_name] -= principal_payment
                    debt_balances[debt_name] = max(0, debt_balances[debt_name])
                    monthly_debt_changes[debt_name] += principal_payment
        
        # Add final month if we have changes
        if current_month is not None and any(change > 0 for change in monthly_debt_changes.values()):
            progression.append({
                'month': len(progression) + 1,
                'date': date(current_month[0], current_month[1], 1),
                **{name: balance for name, balance in debt_balances.items()}
            })
        
        return progression
    
    def _get_month_end_date(self, month_start: date) -> date:
        """Get the last day of the month for the given date."""
        if month_start.month == 12:
            next_month = month_start.replace(year=month_start.year + 1, month=1)
        else:
            next_month = month_start.replace(month=month_start.month + 1)
        
        return next_month.replace(day=1) - timedelta(days=1)
    
    def _get_payment_date(self, month_date: date, due_day: int) -> date:
        """Get the payment date for a debt in the given month."""
        try:
            # Ensure due_day is within valid range
            if not isinstance(due_day, int) or due_day < 1 or due_day > 31:
                raise ValueError(f"Invalid due_day: {due_day}")
            
            return month_date.replace(day=due_day)
        except ValueError:
            # Handle cases where due_day doesn't exist in the month (e.g., Feb 30)
            return self._get_month_end_date(month_date)
    
    def _calculate_minimum_only_scenario(self) -> float:
        """Calculate total interest if only making minimum payments."""
        total_interest = 0.0
        
        for debt in self.debts:
            schedule = generate_amortization_schedule(
                debt, debt.minimum_payment, date.today()
            )
            total_interest += schedule['interest'].sum()
        
        return total_interest
    
    
    
    def _select_best_strategy(
        self, 
        results: List[OptimizationResult], 
        goal: OptimizationGoal
    ) -> OptimizationResult:
        """Select the best strategy based on the optimization goal."""
        
        if goal == OptimizationGoal.MINIMIZE_INTEREST:
            best = min(results, key=lambda r: r.total_interest_paid)
        elif goal == OptimizationGoal.MINIMIZE_TIME:
            best = min(results, key=lambda r: r.total_months_to_freedom)
        elif goal == OptimizationGoal.MAXIMIZE_CASHFLOW:
            best = max(results, key=lambda r: r.monthly_cash_flow_improvement)
        else:
            best = results[0]  # Default to first result
        
        # Update the goal in the result
        best.goal = goal.value
        return best
    
    def compare_strategies(
        self, 
        extra_payment: float = 0.0
    ) -> pd.DataFrame:
        """Compare all available strategies side by side."""
        
        strategies = [PaymentStrategy.AVALANCHE, PaymentStrategy.SNOWBALL]
        if len(self.debts) > 2:
            strategies.append(PaymentStrategy.HYBRID)
        
        comparison_data = []
        
        for strategy in strategies:
            result = self._simulate_strategy(strategy, extra_payment)
            comparison_data.append({
                'strategy': strategy.value,
                'total_interest': result.total_interest_paid,
                'months_to_freedom': result.total_months_to_freedom,
                'monthly_cash_flow': result.monthly_cash_flow_improvement,
                'interest_saved': result.savings_vs_minimum['interest_saved'],
                'months_saved': result.savings_vs_minimum['months_saved']
            })
        
        return pd.DataFrame(comparison_data)
    
    def generate_debt_summary(self) -> Dict[str, Any]:
        """Generate comprehensive summary of current debt situation."""
        
        analyzer = DebtAnalyzer()
        
        return {
            'total_debt': self.total_debt,
            'total_minimum_payments': self.total_minimum_payments,
            'monthly_income': self.monthly_income,
            'available_cash_flow': self.available_cash_flow,
            'available_extra_payment': self.available_extra_payment,
            'current_bank_balance': self.current_bank_balance,
            'weighted_avg_interest_rate': analyzer.calculate_weighted_average_rate(self.debts),
            'number_of_debts': len(self.debts),
            'highest_interest_debt': max(self.debts, key=lambda d: d.interest_rate).name if self.debts else None,
            'largest_debt': max(self.debts, key=lambda d: d.balance).name if self.debts else None,
            'debt_details': [
                {
                    'name': debt.name,
                    'balance': debt.balance,
                    'minimum_payment': debt.minimum_payment,
                    'interest_rate': debt.interest_rate,
                    'due_date': debt.due_date,
                    'months_with_minimum': debt.calculate_months_to_payoff(debt.minimum_payment)
                }
                for debt in self.debts
            ]
        }
    
    def _get_debt_prioritization_rationale(self, ordered_debts: List[Debt]) -> str:
        """Generate detailed rationale for debt prioritization."""
        if not ordered_debts:
            return "No debts to prioritize"
        
        rationale_parts = []
        rationale_parts.append(f"Prioritized {len(ordered_debts)} debts based on optimization strategy:")
        
        for idx, debt in enumerate(ordered_debts[:3]):  # Show top 3 priorities
            rank = idx + 1
            reasons = []
            
            # Interest rate reasoning
            if debt.interest_rate >= 15:
                reasons.append(f"high interest rate ({debt.interest_rate:.2f}%)")
            elif debt.interest_rate >= 8:
                reasons.append(f"moderate interest rate ({debt.interest_rate:.2f}%)")
            else:
                reasons.append(f"low interest rate ({debt.interest_rate:.2f}%)")
            
            # Balance reasoning
            if debt.balance <= 2000:
                reasons.append(f"small balance (${debt.balance:,.2f})")
            elif debt.balance <= 10000:
                reasons.append(f"medium balance (${debt.balance:,.2f})")
            else:
                reasons.append(f"large balance (${debt.balance:,.2f})")
            
            # Payment ratio
            if debt.balance > 0:
                payment_ratio = debt.minimum_payment / debt.balance
                if payment_ratio >= 0.05:
                    reasons.append("fast minimum payoff rate")
                elif payment_ratio >= 0.02:
                    reasons.append("moderate minimum payoff rate")
                else:
                    reasons.append("slow minimum payoff rate")
            
            reason_text = ", ".join(reasons)
            rationale_parts.append(f"  #{rank}: {debt.name} - {reason_text}")
        
        if len(ordered_debts) > 3:
            rationale_parts.append(f"  ... and {len(ordered_debts) - 3} other debts in strategic order")
        
        return "; ".join(rationale_parts)
    
    def _calculate_priority_score(self, debt: Debt, ordered_debts: List[Debt]) -> float:
        """Calculate a priority score for a debt (higher = more priority)."""
        try:
            position = ordered_debts.index(debt)
            # Higher score for earlier position (lower index = higher priority)
            return len(ordered_debts) - position
        except ValueError:
            return 0.0
    
    def _get_extra_payment_rationale(self, priority_debt: Debt, ordered_debts: List[Debt], 
                                   available_extra: float, priority_balance: float) -> str:
        """Generate detailed rationale for extra payment allocation."""
        reasons = []
        
        # Priority position
        try:
            position = ordered_debts.index(priority_debt)
            reasons.append(f"Priority rank #{position + 1} in debt order")
        except ValueError:
            reasons.append("Selected debt")
        
        # Interest rate comparison
        all_rates = [d.interest_rate for d in ordered_debts]
        max_rate = max(all_rates)
        if priority_debt.interest_rate == max_rate:
            reasons.append(f"highest interest rate ({priority_debt.interest_rate:.2f}%)")
        elif priority_debt.interest_rate >= sum(all_rates) / len(all_rates):
            reasons.append(f"above-average interest rate ({priority_debt.interest_rate:.2f}%)")
        else:
            reasons.append(f"strategic priority despite lower rate ({priority_debt.interest_rate:.2f}%)")
        
        # Balance consideration
        if priority_balance <= available_extra:
            reasons.append(f"can be paid off completely with available funds")
        else:
            payoff_percent = (available_extra / priority_balance) * 100
            reasons.append(f"will pay off {payoff_percent:.1f}% of remaining balance")
        
        # Financial impact
        monthly_interest_saved = priority_debt.calculate_interest_charge(min(available_extra, priority_balance))
        reasons.append(f"saves ${monthly_interest_saved:.2f}/month in interest")
        
        return ", ".join(reasons)
