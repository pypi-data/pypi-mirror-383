from rich.progress import Progress, SpinnerColumn, TextColumn

def setup_progress_bar(task_description):
    """Initialize and display a progress bar for the setup process."""
    with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), expand=True) as progress:
        task = progress.add_task(task_description, total=None)
        return progress, task

def update_progress(progress, task, completed_steps):
    """Update the progress bar with the number of completed steps."""
    progress.update(task, completed=completed_steps)

def complete_progress(progress, task):
    """Mark the progress task as complete."""
    progress.update(task, completed=task.total)