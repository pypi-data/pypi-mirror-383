#!/usr/bin/env python3
"""
Business Agent Main Scheduler
Runs automated daily tasks on schedule
"""

import schedule
import time
import subprocess
import sys
from datetime import datetime
from rich.console import Console
from dotenv import load_dotenv

load_dotenv()

console = Console()

def run_script(script_name, description):
    """Run a Python script and handle errors"""
    console.print(f"\n[bold cyan]Running {description}...[/bold cyan]")
    console.print(f"[dim]{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}[/dim]\n")
    
    try:
        result = subprocess.run(
            [sys.executable, f"scripts/{script_name}"],
            capture_output=False,
            text=True
        )
        
        if result.returncode == 0:
            console.print(f"[green]✓ {description} completed successfully[/green]\n")
        else:
            console.print(f"[yellow]⚠ {description} finished with warnings[/yellow]\n")
            
    except Exception as e:
        console.print(f"[red]✗ Error running {description}: {e}[/red]\n")

def run_morning_brief():
    """Run morning briefing"""
    run_script("morning_brief.py", "Morning Briefing")

def run_evening_review():
    """Run evening review"""
    run_script("evening_review.py", "Evening Review")

def run_weekly_review():
    """Run weekly review"""
    run_script("weekly_review.py", "Weekly Review")

def main():
    console.print("\n[bold cyan]═══════════════════════════════════════════[/bold cyan]")
    console.print("[bold cyan]  🤖 Business Agent Scheduler Started[/bold cyan]")
    console.print("[bold cyan]═══════════════════════════════════════════[/bold cyan]\n")
    
    # Schedule jobs
    # Morning briefing: Monday-Friday at 8:00 AM
    schedule.every().monday.at("08:00").do(run_morning_brief)
    schedule.every().tuesday.at("08:00").do(run_morning_brief)
    schedule.every().wednesday.at("08:00").do(run_morning_brief)
    schedule.every().thursday.at("08:00").do(run_morning_brief)
    schedule.every().friday.at("08:00").do(run_morning_brief)
    
    # Evening review: Monday-Friday at 6:00 PM
    schedule.every().monday.at("18:00").do(run_evening_review)
    schedule.every().tuesday.at("18:00").do(run_evening_review)
    schedule.every().wednesday.at("18:00").do(run_evening_review)
    schedule.every().thursday.at("18:00").do(run_evening_review)
    schedule.every().friday.at("18:00").do(run_evening_review)
    
    # Weekly review: Sunday at 7:00 PM
    schedule.every().sunday.at("19:00").do(run_weekly_review)
    
    console.print("[bold]📅 Scheduled Tasks:[/bold]")
    console.print("  • Morning Briefings: Mon-Fri at 8:00 AM")
    console.print("  • Evening Reviews: Mon-Fri at 6:00 PM")
    console.print("  • Weekly Review: Sunday at 7:00 PM")
    console.print()
    console.print("[dim]Press Ctrl+C to stop the scheduler[/dim]")
    console.print()
    
    # Keep the scheduler running
    try:
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute
            
    except KeyboardInterrupt:
        console.print("\n\n[yellow]Scheduler stopped by user[/yellow]")
        console.print("[dim]All scheduled tasks have been cancelled[/dim]\n")
        sys.exit(0)

if __name__ == "__main__":
    main()
