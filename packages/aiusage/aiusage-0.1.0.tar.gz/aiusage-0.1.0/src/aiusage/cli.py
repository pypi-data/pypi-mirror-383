"""
Command-line interface for AI credit usage analysis.
"""

from datetime import datetime
from typing import Annotated, Optional

import cyclopts

from aiusage import __version__
from aiusage import config as config_module
from aiusage.core import calculate_progress, ordinal_suffix


# ANSI color codes
class Colors:
    GREEN = '\033[92m'  # Light green
    RED = '\033[91m'  # Light red
    YELLOW = '\033[93m'  # Yellow
    RESET = '\033[0m'  # Reset to default
    BOLD = '\033[1m'


app = cyclopts.App(
    name='aiusage',
    help=f'💳 Track AI credit usage across billing cycles and avoid overages. (v{__version__})',
    version=__version__,
)


def display_analysis(percentage: float, target_day: int) -> None:
    """Display the credit usage analysis."""
    result = calculate_progress(percentage, target_day=target_day)

    print(f'\n💳 Credit Usage Analysis (v{__version__})')
    print(f'{"=" * 50}')
    print(f'Current Date: {datetime.now().strftime("%Y-%m-%d")}')
    print(f'Billing Cycle: Day {result["days_since_renewal"]} of {result["days_in_billing_cycle"]}')
    print(f'Renewal Day: {ordinal_suffix(result["target_day"])} of the month')
    print('\n🎯 Analysis:')
    print(f'  Credits Used: {result["current_percentage"]:.1f}%')

    # Color-code the difference based on good/bad
    diff_color = Colors.GREEN if result['ratio'] < 1 else Colors.RED if result['ratio'] > 1 else Colors.YELLOW
    print(f'  Difference: {diff_color}{result["difference_percentage"]:+.1f}%{Colors.RESET}')

    # Color-code the status
    status_color = Colors.GREEN if result['ratio'] < 1 else Colors.RED if result['ratio'] > 1 else Colors.YELLOW
    print(f'  Status: {status_color}{result["status"].upper()}{Colors.RESET}')

    print('\n🔮 Projection (at current rate):')
    print(f'  Expected usage by renewal: {result["projected_usage"]:.1f}%')

    # Color-code the remaining credits
    remaining_color = Colors.GREEN if result['projected_remaining'] > 0 else Colors.RED
    print(f'  Expected surplus: {remaining_color}{result["projected_remaining"]:.1f}%{Colors.RESET}')

    if result['ratio'] > 1:
        print(
            f"\n{Colors.RED}⚠️  WARNING: You're using credits {result['difference_percentage']:.1f}% "
            f'faster than time!{Colors.RESET}'
        )
        if result['projected_remaining'] < 0:
            print(
                f"   {Colors.RED}💥 You'll exceed 100% usage by {abs(result['projected_remaining']):.1f}% "
                f'before renewal!{Colors.RESET}'
            )
        else:
            print(
                f'   {Colors.RED}At this rate, you may run out before renewal day {result["target_day"]}{Colors.RESET}'
            )
    elif result['ratio'] < 1:
        print(
            f"\n{Colors.GREEN}✅ Great! You're conserving credits - using {abs(result['difference_percentage']):.1f}% "
            f'slower than time{Colors.RESET}'
        )
        print(
            f"   {Colors.GREEN}You'll have ~{result['projected_remaining']:.1f}% "
            f'credits remaining at renewal.{Colors.RESET}'
        )
    else:
        print(f"\n{Colors.YELLOW}✓ Perfect! You're using credits at exactly the expected rate.{Colors.RESET}")
        print(f"   {Colors.YELLOW}You'll use exactly 100% by day {result['target_day']}.{Colors.RESET}")

    print()


def prompt_for_renewal_day(saved_day: Optional[int] = None) -> int:
    """Prompt user for renewal day."""
    if saved_day:
        print(f'Using saved renewal day: {saved_day}\n')
        return saved_day

    while True:
        day_input = input('Enter your renewal day (1-31) [default: 1]: ').strip()
        if not day_input:
            return 1
        try:
            day = int(day_input)
            if not 1 <= day <= 31:
                print('  ⚠️  Please enter a day between 1 and 31')
                continue
            # Ask if they want to save it
            if day != 1:
                save_input = input('Save this renewal day for future use? (Y/n): ').strip().lower()
                if save_input != 'n':
                    config_module.save_renewal_day(day)
                    print('✓ Renewal day saved')
            return day
        except ValueError:
            print('  ⚠️  Please enter a valid number')


def prompt_for_percentage() -> float:
    """Prompt user for percentage."""
    while True:
        pct_input = input('Enter your current credit usage percentage (0-100): ').strip()
        if not pct_input:
            print('  ⚠️  Percentage is required')
            continue
        try:
            percentage = float(pct_input)
            if percentage < 0:
                print('  ⚠️  Percentage cannot be negative')
                continue
            return percentage
        except ValueError:
            print('  ⚠️  Please enter a valid number')


@app.default
def check(
    percentage: Annotated[
        Optional[float],
        cyclopts.Parameter(
            name=['--percentage', '--percent'],
            show_default=False,
            help='📊 Current credit usage percentage (0-100). If omitted, will prompt interactively.',
        ),
    ] = None,
    renewal_day: Annotated[
        Optional[int],
        cyclopts.Parameter(
            name='--renewal-day',
            show_default=False,
            help='📅 Day of month when credits renew (1-31). Uses saved value or prompts if omitted.',
        ),
    ] = None,
    reset_renewal_day: Annotated[
        bool,
        cyclopts.Parameter(
            name='--reset-renewal-day',
            help='🔄 Reset the saved renewal day configuration.',
        ),
    ] = False,
) -> None:
    """
    🔍 Check AI credit usage and compare against billing cycle progress.

    Analyzes your current credit consumption rate and projects whether you'll
    stay within budget before the next renewal. Shows visual indicators for
    credit health: 🟢 conserving, 🟡 on track, or 🔴 overspending.

    [bold green]Examples:[/bold green]
        aiusage 35                             # Positional: 35% usage, use saved renewal day
        aiusage 35 15                          # Positional: 35% usage, renewal on 15th
        aiusage --percent 35                   # Named (short form)
        aiusage --percentage 35 --renewal-day 15  # Named (long form)
        aiusage                                # Interactive mode (prompts for values)
        aiusage --reset-renewal-day            # Reset saved renewal day
    """
    # Handle reset renewal day flag
    if reset_renewal_day:
        print('🔄 Reset Renewal Day\n')

        # Show current saved value if exists
        saved_day = config_module.load_renewal_day()
        if saved_day:
            print(f'Current saved renewal day: {saved_day}')
        else:
            print('No renewal day currently saved.')

        # Prompt for new value
        while True:
            day_input = input('\nEnter new renewal day (1-31): ').strip()
            if not day_input:
                print('❌ Cancelled - no changes made')
                return
            try:
                new_day = int(day_input)
                if not 1 <= new_day <= 31:
                    print('  ⚠️  Please enter a day between 1 and 31')
                    continue
                break
            except ValueError:
                print('  ⚠️  Please enter a valid number')

        # Save the new value
        config_module.save_renewal_day(new_day)
        print(f'✓ Renewal day saved: {new_day}')
        return

    # Interactive mode if no percentage provided
    if percentage is None:
        print('💳 AI Credit Usage Checker\n')
        saved_day = config_module.load_renewal_day()
        target_day = renewal_day if renewal_day is not None else prompt_for_renewal_day(saved_day)
        percentage = prompt_for_percentage()
        print()
    else:
        # If renewal_day not provided, try to load saved value
        if renewal_day is None:
            saved_day = config_module.load_renewal_day()
            target_day = saved_day if saved_day else 1
        else:
            target_day = renewal_day

    display_analysis(percentage, target_day)


def main() -> None:
    """Main entry point for the CLI."""
    app()


if __name__ == '__main__':
    main()
