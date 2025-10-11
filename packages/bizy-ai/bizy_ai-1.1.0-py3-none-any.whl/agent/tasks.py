from datetime import datetime, timedelta, date
from sqlalchemy import and_, or_
from agent.models import Task, DailyLog, get_session

class TaskManager:
    def __init__(self):
        self.session = get_session()
    
    def create_task(self, title, description=None, priority=3, category=None, 
                    estimated_hours=None, due_date=None, parent_goal_id=None, 
                    dependencies=None, tags=None):
        """Create a new task"""
        task = Task(
            title=title,
            description=description,
            priority=priority,
            category=category,
            estimated_hours=estimated_hours,
            due_date=due_date,
            parent_goal_id=parent_goal_id,
            dependencies=dependencies or [],
            tags=tags or []
        )
        self.session.add(task)
        self.session.commit()
        return task
    
    def get_task(self, task_id):
        """Get a specific task by ID"""
        return self.session.query(Task).filter(Task.id == task_id).first()
    
    def get_tasks_for_today(self):
        """Get all tasks due today or overdue"""
        today = datetime.now().date()
        tomorrow = today + timedelta(days=1)
        
        tasks = self.session.query(Task).filter(
            and_(
                Task.status.in_(['pending', 'in_progress']),
                or_(
                    Task.due_date == None,
                    Task.due_date < datetime.combine(tomorrow, datetime.min.time())
                )
            )
        ).order_by(Task.priority, Task.due_date).all()
        
        return tasks
    
    def get_tasks_by_status(self, status):
        """Get all tasks with a specific status"""
        return self.session.query(Task).filter(Task.status == status).all()
    
    def get_tasks_by_goal(self, goal_id):
        """Get all tasks linked to a specific goal"""
        return self.session.query(Task).filter(Task.parent_goal_id == goal_id).all()
    
    def get_tasks_by_category(self, category):
        """Get all tasks in a specific category"""
        return self.session.query(Task).filter(Task.category == category).all()
    
    def get_overdue_tasks(self):
        """Get all overdue tasks"""
        now = datetime.now()
        return self.session.query(Task).filter(
            and_(
                Task.status.in_(['pending', 'in_progress']),
                Task.due_date < now
            )
        ).order_by(Task.priority).all()
    
    def update_task(self, task_id, **kwargs):
        """Update task fields"""
        task = self.get_task(task_id)
        if task:
            for key, value in kwargs.items():
                if hasattr(task, key):
                    setattr(task, key, value)
            self.session.commit()
        return task
    
    def complete_task(self, task_id, actual_hours=None):
        """Mark a task as completed"""
        task = self.get_task(task_id)
        if task:
            task.status = 'completed'
            task.completed_at = datetime.now()
            if actual_hours:
                task.actual_hours = actual_hours
            self.session.commit()
        return task
    
    def block_task(self, task_id, reason=None):
        """Mark a task as blocked"""
        task = self.get_task(task_id)
        if task:
            task.status = 'blocked'
            if reason:
                task.notes = f"{task.notes or ''}\n[BLOCKED] {reason}"
            self.session.commit()
        return task
    
    def delete_task(self, task_id):
        """Delete a task"""
        task = self.get_task(task_id)
        if task:
            self.session.delete(task)
            self.session.commit()
            return True
        return False
    
    def get_tasks_for_date_range(self, start_date, end_date):
        """Get all tasks within a date range"""
        return self.session.query(Task).filter(
            and_(
                Task.due_date >= start_date,
                Task.due_date <= end_date
            )
        ).order_by(Task.due_date, Task.priority).all()
    
    def get_daily_summary(self, date_obj=None):
        """Get summary of tasks for a specific day"""
        if date_obj is None:
            date_obj = datetime.now()
        
        if isinstance(date_obj, date) and not isinstance(date_obj, datetime):
            date_obj = datetime.combine(date_obj, datetime.min.time())
        
        day_start = date_obj.replace(hour=0, minute=0, second=0, microsecond=0)
        day_end = day_start + timedelta(days=1)
        
        # Get tasks due on this day
        tasks_due = self.session.query(Task).filter(
            and_(
                Task.due_date >= day_start,
                Task.due_date < day_end
            )
        ).all()
        
        # Get tasks completed on this day
        tasks_completed = self.session.query(Task).filter(
            and_(
                Task.completed_at >= day_start,
                Task.completed_at < day_end
            )
        ).all()
        
        return {
            'date': date_obj.strftime('%Y-%m-%d'),
            'tasks_due': len(tasks_due),
            'tasks_completed': len(tasks_completed),
            'completion_rate': len(tasks_completed) / len(tasks_due) if tasks_due else 0,
            'completed_tasks': [t.to_dict() for t in tasks_completed],
            'pending_tasks': [t.to_dict() for t in tasks_due if t.status != 'completed']
        }
    
    def get_yesterday_summary(self):
        """Get summary for yesterday"""
        yesterday = datetime.now() - timedelta(days=1)
        return self.get_daily_summary(yesterday)
    
    def create_daily_log(self, date, tasks_completed, tasks_planned, 
                        wins=None, blockers=None, learnings=None, 
                        energy_level=None, mood=None, notes=None):
        """Create or update daily log"""
        # Check if log already exists
        existing_log = self.session.query(DailyLog).filter(
            DailyLog.date == date.replace(hour=0, minute=0, second=0, microsecond=0)
        ).first()
        
        completion_rate = tasks_completed / tasks_planned if tasks_planned > 0 else 0
        
        if existing_log:
            existing_log.tasks_completed = tasks_completed
            existing_log.tasks_planned = tasks_planned
            existing_log.completion_rate = completion_rate
            existing_log.wins = wins
            existing_log.blockers = blockers
            existing_log.learnings = learnings
            existing_log.energy_level = energy_level
            existing_log.mood = mood
            existing_log.notes = notes
            log = existing_log
        else:
            log = DailyLog(
                date=date.replace(hour=0, minute=0, second=0, microsecond=0),
                tasks_completed=tasks_completed,
                tasks_planned=tasks_planned,
                completion_rate=completion_rate,
                wins=wins,
                blockers=blockers,
                learnings=learnings,
                energy_level=energy_level,
                mood=mood,
                notes=notes
            )
            self.session.add(log)
        
        self.session.commit()
        return log
    
    def get_weekly_stats(self, start_date=None):
        """Get statistics for the past week"""
        if start_date is None:
            start_date = datetime.now() - timedelta(days=7)
        
        end_date = datetime.now()
        
        logs = self.session.query(DailyLog).filter(
            and_(
                DailyLog.date >= start_date,
                DailyLog.date <= end_date
            )
        ).order_by(DailyLog.date).all()
        
        if not logs:
            return {
                'total_tasks_completed': 0,
                'total_tasks_planned': 0,
                'average_completion_rate': 0,
                'days_logged': 0
            }
        
        total_completed = sum(log.tasks_completed for log in logs)
        total_planned = sum(log.tasks_planned for log in logs)
        avg_completion = sum(log.completion_rate for log in logs if log.completion_rate) / len(logs)
        
        return {
            'total_tasks_completed': total_completed,
            'total_tasks_planned': total_planned,
            'average_completion_rate': avg_completion,
            'days_logged': len(logs),
            'logs': [log.to_dict() for log in logs]
        }
    
    def get_task_velocity(self, days=30):
        """
        Calculate average tasks completed per day over a period.
        Uses actual completed_at timestamps for accurate velocity calculation.
        """
        # Get tasks completed in the specified period
        completed_tasks = self.get_completed_tasks_this_week(days=days)

        if not completed_tasks:
            return 0.0

        # Calculate velocity as tasks per day
        velocity = len(completed_tasks) / days
        return velocity

    def get_completed_tasks_this_week(self, days=7):
        """Get tasks completed in the last N days based on completed_at timestamp"""
        # Use UTC time to match database timestamps
        now = datetime.utcnow()
        start_date = now - timedelta(days=days)

        completed_tasks = self.session.query(Task).filter(
            and_(
                Task.status == 'completed',
                Task.completed_at >= start_date,
                Task.completed_at <= now
            )
        ).order_by(Task.completed_at.desc()).all()

        return completed_tasks

    def get_created_tasks_this_week(self, days=7):
        """Get tasks created in the last N days based on created_at timestamp"""
        # Use UTC time to match database timestamps
        now = datetime.utcnow()
        start_date = now - timedelta(days=days)

        created_tasks = self.session.query(Task).filter(
            and_(
                Task.created_at >= start_date,
                Task.created_at <= now
            )
        ).order_by(Task.created_at.desc()).all()

        return created_tasks

    def get_weekly_task_stats(self, days=7):
        """
        Get weekly statistics based on actual task completion dates (completed_at).
        This is more accurate than DailyLog-based stats as it reflects actual work completed.
        """
        completed_tasks = self.get_completed_tasks_this_week(days)
        created_tasks = self.get_created_tasks_this_week(days)

        # Calculate statistics
        tasks_completed = len(completed_tasks)
        tasks_created = len(created_tasks)

        # Calculate completion rate (completed vs created this week)
        completion_rate = (tasks_completed / tasks_created * 100) if tasks_created > 0 else 0

        # Calculate total estimated hours
        total_estimated_hours = sum(
            task.estimated_hours or 0 for task in completed_tasks
        )

        # Calculate total actual hours
        total_actual_hours = sum(
            task.actual_hours or 0 for task in completed_tasks
        )

        # Break down by category
        categories = {}
        for task in completed_tasks:
            category = task.category or 'uncategorized'
            if category not in categories:
                categories[category] = 0
            categories[category] += 1

        # Break down by priority
        priorities = {}
        for task in completed_tasks:
            priority = task.priority
            if priority not in priorities:
                priorities[priority] = 0
            priorities[priority] += 1

        return {
            'tasks_completed_this_week': tasks_completed,
            'tasks_created_this_week': tasks_created,
            'completion_rate': completion_rate,
            'total_estimated_hours': total_estimated_hours,
            'total_actual_hours': total_actual_hours,
            'completed_tasks': [task.to_dict() for task in completed_tasks],
            'categories': categories,
            'priorities': priorities,
            'period_days': days
        }

    def close(self):
        """Close the database session"""
        self.session.close()
