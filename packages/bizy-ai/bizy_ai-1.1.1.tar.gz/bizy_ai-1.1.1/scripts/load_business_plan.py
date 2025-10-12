#!/usr/bin/env python3
"""Script to load business plan from YAML into the database"""

import yaml
import sys
import os
from datetime import datetime
from agent.models import get_session, BusinessPlan
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt

console = Console()

def load_business_plan(file_path=None, plan_name=None):
    """Load a business plan from YAML into database"""

    console.print()

    # If no file path provided, request one
    if not file_path:
        file_path = Prompt.ask("📁 [bold]Enter path to business plan YAML file[/bold]")

    # Expand user path if needed
    file_path = os.path.expanduser(file_path)

    # Check if file exists
    if not os.path.exists(file_path):
        console.print(f"[bold red]❌ Error: File not found: {file_path}[/bold red]")
        return False

    # Read the YAML file
    try:
        with open(file_path, 'r') as f:
            file_content = f.read()
            plan_data = yaml.safe_load(file_content)
    except Exception as e:
        console.print(f"[bold red]❌ Error reading YAML file: {e}[/bold red]")
        return False

    session = get_session()

    try:
        # Get plan name: CLI option > YAML 'name' field > first # header > prompt user
        if not plan_name:
            # Try to get name from YAML 'name' field
            plan_name = plan_data.get('name')

        if not plan_name:
            # Try to extract from first # header in file
            for line in file_content.split('\n'):
                line = line.strip()
                if line.startswith('# ') and not line.startswith('##'):
                    plan_name = line[2:].strip()
                    break

        if not plan_name:
            # Prompt user for name
            plan_name = Prompt.ask(f"📝 [bold]Enter business plan name[/bold]")

        # Deactivate any existing active plans
        active_plans = session.query(BusinessPlan).filter_by(is_active=True).all()
        for plan in active_plans:
            plan.is_active = False
            console.print(f"[yellow]⚠ Deactivated existing plan: {plan.name}[/yellow]")

        # Create new business plan
        new_plan = BusinessPlan(
            name=plan_name,
            version=plan_data.get('version', '1.0'),
            vision=plan_data.get('vision', ''),
            mission=plan_data.get('mission', ''),
            value_proposition=plan_data.get('value_proposition', ''),
            target_market=plan_data.get('target_market', ''),
            revenue_model=plan_data.get('revenue_model', ''),
            is_active=True
        )

        session.add(new_plan)
        session.commit()

        console.print(Panel(
            f"[green]✅ Business Plan Loaded Successfully[/green]\n\n"
            f"Name: {new_plan.name}\n"
            f"Version: {new_plan.version}\n"
            f"ID: {new_plan.id}\n"
            f"Created: {new_plan.created_at.strftime('%Y-%m-%d %H:%M:%S')}\n"
            f"Active: {'Yes' if new_plan.is_active else 'No'}",
            title="Success",
            border_style="green"
        ))

        console.print()
        return True

    except Exception as e:
        console.print(f"[bold red]❌ Error creating business plan: {e}[/bold red]")
        session.rollback()
        return False
    finally:
        session.close()

if __name__ == "__main__":
    # Check for command line argument
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
    else:
        file_path = None

    load_business_plan(file_path)
