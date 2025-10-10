import typer
from rich.console import Console
from rich.table import Table
from rich import print as rprint
from . import db, gmail, analyzer

app = typer.Typer()
console = Console()


@app.command()
def auth():
    """Authenticate with Gmail via OAuth2"""
    try:
        gmail.authenticate()
        rprint("[green]✓[/green] Successfully authenticated with Gmail!")
    except FileNotFoundError as e:
        rprint(f"[red]✗[/red] {str(e)}")
        raise typer.Exit(code=1)
    except Exception as e:
        rprint(f"[red]✗[/red] Authentication failed: {str(e)}")
        raise typer.Exit(code=1)


@app.command()
def sync(max_results: int = typer.Option(100, help="Maximum number of emails to fetch")):
    """Fetch new emails matching job-related keywords and store in database"""
    try:
        db.init_db()
        
        rprint("[cyan]Fetching emails from Gmail...[/cyan]")
        emails = gmail.fetch_job_emails(max_results=max_results)
        
        new_count = 0
        for email in emails:
            if not db.email_exists(email['id']):
                category = analyzer.classify_email(email['subject'], email['sender'])
                db.insert_email(
                    email['id'],
                    email['subject'],
                    email['sender'],
                    email['date'],
                    category
                )
                new_count += 1
        
        rprint(f"[green]✓[/green] Synced {new_count} new email(s)")
        
    except Exception as e:
        rprint(f"[red]✗[/red] Sync failed: {str(e)}")
        raise typer.Exit(code=1)


@app.command()
def stats():
    """Print total counts of each stage"""
    try:
        db.init_db()
        
        console.print("\n[bold cyan]📊 JOB APPLICATION STATISTICS[/bold cyan]\n")
        
        detailed_stats = db.get_detailed_stats()
        
        console.print("[bold magenta]📋 OVERVIEW[/bold magenta]\n")
        
        overview_lines = [
            f"Total Applications:      {detailed_stats['total_applications']}",
            f"Total Interviews:        {detailed_stats['total_interviews']}",
            f"Total Offers:            {detailed_stats['total_offers']}",
            f"Total Rejections:        {detailed_stats['total_rejections']}",
            "",
            f"Interview Rate:          {detailed_stats['interview_rate']:.1f}%",
            f"Offer Rate:              {detailed_stats['offer_rate']:.1f}%",
            f"Rejection Rate:          {detailed_stats['rejection_rate']:.1f}%",
            f"Interview → Offer Rate:  {detailed_stats['interview_to_offer_rate']:.1f}%",
        ]
        
        for line in overview_lines:
            console.print(f"  {line}")
        
        console.print("\n[bold cyan]🔄 PIPELINE STATUS[/bold cyan]\n")
        
        pipeline_lines = [
            f"Pending Applications:    {detailed_stats['pending_applications']}",
            f"Closed Applications:     {detailed_stats['closed_applications']}",
            f"Pending Rate:            {detailed_stats['pending_rate']:.1f}%",
        ]
        
        for line in pipeline_lines:
            console.print(f"  {line}")
        
        console.print("\n[bold green]📅 MONTHLY BREAKDOWN[/bold green]\n")
        
        monthly_data = db.get_monthly_breakdown()
        
        if monthly_data:
            table = Table(show_header=True, header_style="bold")
            table.add_column("Month", style="cyan")
            table.add_column("Apps", justify="right", style="white")
            table.add_column("Interviews", justify="right", style="yellow")
            table.add_column("Offers", justify="right", style="green")
            table.add_column("Rejections", justify="right", style="red")
            table.add_column("Int Rate", justify="right", style="magenta")
            
            for month in monthly_data:
                table.add_row(
                    month["month"],
                    str(month["applications"]),
                    str(month["interviews"]),
                    str(month["offers"]),
                    str(month["rejections"]),
                    f"{month['interview_rate']:.1f}%"
                )
            
            console.print(table)
        else:
            console.print("  [dim]No monthly data available[/dim]")
        
        console.print("\n[bold yellow]📋 APPLICATION DETAILS[/bold yellow]\n")
        
        emails = db.get_all_emails()
        console.print(f"Total applications found: {len(emails)}\n")
        
        for i, email in enumerate(emails):
            # Extract company name from sender
            sender = email['sender']
            company = sender.split('@')[1].split('.')[0].title() if '@' in sender else 'Unknown'
            
            # Extract job title from subject (simplified)
            subject = email['subject']
            job_title = subject.split(' - ')[0] if ' - ' in subject else 'unknown'
            if len(job_title) > 30:
                job_title = job_title[:27] + "..."
            
            # Status with icons
            category = email['category']
            if category == "Rejection":
                status = "[red]✗ rejection[/red]"
            elif category == "Interview":
                status = "[green]✔ interviews[/green]"
            elif category == "Offer":
                status = "[green]✔ offer[/green]"
            else:
                status = "[yellow]○ pending[/yellow]"
            
            console.print(f"{i:2d}. [cyan]{company}[/cyan] - [white]{job_title}[/white] | [dim]{email['date']}[/dim] | {status}")
        
        console.print()
        
    except Exception as e:
        rprint(f"[red]✗[/red] Failed to get stats: {str(e)}")
        raise typer.Exit(code=1)


def main():
    app()


if __name__ == "__main__":
    main()

