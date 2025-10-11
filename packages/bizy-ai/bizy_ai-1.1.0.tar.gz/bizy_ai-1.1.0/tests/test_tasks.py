"""
Tests for TaskManager
Testing task creation, completion, and management
"""

import pytest
from datetime import datetime, timedelta
from agent.tasks import TaskManager
from agent.models import Task


class TestTaskManager:
    """Test TaskManager functionality"""

    def test_create_task(self, test_session):
        """Test TaskManager.create_task()"""
        task_mgr = TaskManager()
        task_mgr.session = test_session

        task = task_mgr.create_task(
            title="Test Task",
            description="Test description",
            priority=2,
            category="development"
        )

        assert task.id is not None
        assert task.title == "Test Task"
        assert task.priority == 2
        assert task.category == "development"

    def test_create_task_with_goal(self, test_session, sample_goal):
        """Test creating task linked to a goal"""
        task_mgr = TaskManager()
        task_mgr.session = test_session

        task = task_mgr.create_task(
            title="Goal Task",
            parent_goal_id=sample_goal.id
        )

        assert task.parent_goal_id == sample_goal.id

    def test_get_task(self, test_session, sample_task):
        """Test retrieving a task by ID"""
        task_mgr = TaskManager()
        task_mgr.session = test_session

        retrieved_task = task_mgr.get_task(sample_task.id)

        assert retrieved_task is not None
        assert retrieved_task.id == sample_task.id
        assert retrieved_task.title == sample_task.title

    def test_complete_task(self, test_session, sample_task):
        """Test completing a task"""
        task_mgr = TaskManager()
        task_mgr.session = test_session

        completed_task = task_mgr.complete_task(sample_task.id)

        assert completed_task.status == "completed"
        assert completed_task.completed_at is not None

    def test_get_tasks_by_status(self, test_session, multiple_tasks):
        """Test filtering tasks by status"""
        task_mgr = TaskManager()
        task_mgr.session = test_session

        pending_tasks = task_mgr.get_tasks_by_status("pending")
        completed_tasks = task_mgr.get_tasks_by_status("completed")

        assert len(pending_tasks) == 2  # Two pending tasks
        assert len(completed_tasks) == 1  # One completed task

    def test_get_tasks_by_goal(self, test_session, sample_goal, multiple_tasks):
        """Test getting tasks for a specific goal"""
        task_mgr = TaskManager()
        task_mgr.session = test_session

        goal_tasks = task_mgr.get_tasks_by_goal(sample_goal.id)

        assert len(goal_tasks) == 4  # All tasks in multiple_tasks fixture
        for task in goal_tasks:
            assert task.parent_goal_id == sample_goal.id

    def test_get_tasks_for_today(self, test_session):
        """Test getting today's tasks"""
        task_mgr = TaskManager()
        task_mgr.session = test_session

        # Create tasks with different due dates
        task_mgr.create_task(title="Today Task", due_date=datetime.now())
        task_mgr.create_task(title="Past Task", due_date=datetime.now() - timedelta(days=1))
        task_mgr.create_task(title="Future Task", due_date=datetime.now() + timedelta(days=7))

        today_tasks = task_mgr.get_tasks_for_today()

        # Should include tasks due today, overdue, and tasks with no due date
        assert len(today_tasks) >= 2

    def test_get_overdue_tasks(self, test_session):
        """Test getting overdue tasks"""
        task_mgr = TaskManager()
        task_mgr.session = test_session

        # Create overdue task
        task_mgr.create_task(
            title="Overdue Task",
            due_date=datetime.now() - timedelta(days=1)
        )

        overdue_tasks = task_mgr.get_overdue_tasks()

        assert len(overdue_tasks) >= 1
        assert overdue_tasks[0].title == "Overdue Task"

    def test_weekly_stats(self, test_session):
        """Test getting weekly statistics"""
        task_mgr = TaskManager()
        task_mgr.session = test_session

        # Create tasks for this week
        task1 = task_mgr.create_task(title="Week Task 1")
        task_mgr.complete_task(task1.id)
        task_mgr.create_task(title="Week Task 2")

        stats = task_mgr.get_weekly_stats()

        assert 'total_tasks_planned' in stats
        assert 'total_tasks_completed' in stats
        assert 'average_completion_rate' in stats

    def test_get_completed_tasks_this_week(self, test_session):
        """Test getting tasks completed this week based on completed_at"""
        task_mgr = TaskManager()
        task_mgr.session = test_session

        # Create and complete tasks this week
        task1 = task_mgr.create_task(title="Completed This Week 1")
        task_mgr.complete_task(task1.id)

        task2 = task_mgr.create_task(title="Completed This Week 2")
        task_mgr.complete_task(task2.id)

        # Create a task from last week (8 days ago)
        from agent.models import Task
        old_task = Task(title="Old Completed Task", status="completed")
        old_task.completed_at = datetime.now() - timedelta(days=8)
        test_session.add(old_task)
        test_session.commit()

        # Create pending task (not completed)
        task_mgr.create_task(title="Pending Task")

        # Get completed tasks for this week
        completed_this_week = task_mgr.get_completed_tasks_this_week()

        # Should only include tasks completed in the last 7 days
        assert len(completed_this_week) == 2
        assert all(task.completed_at is not None for task in completed_this_week)
        assert all(task.status == "completed" for task in completed_this_week)

    def test_get_weekly_task_stats_with_completed_tasks(self, test_session):
        """Test weekly stats calculation based on completed_at dates"""
        task_mgr = TaskManager()
        task_mgr.session = test_session

        # Complete 3 tasks this week
        for i in range(3):
            task = task_mgr.create_task(title=f"Completed Task {i+1}")
            task_mgr.complete_task(task.id)

        # Create 2 pending tasks
        task_mgr.create_task(title="Pending Task 1")
        task_mgr.create_task(title="Pending Task 2")

        # Create old completed task (9 days ago)
        from agent.models import Task
        old_task = Task(title="Old Task", status="completed")
        old_task.completed_at = datetime.now() - timedelta(days=9)
        test_session.add(old_task)
        test_session.commit()

        # Get stats based on actual completions
        stats = task_mgr.get_weekly_task_stats()

        assert stats['tasks_completed_this_week'] == 3
        assert stats['tasks_created_this_week'] >= 5  # All tasks created this week
        assert 'completion_rate' in stats
        assert stats['total_estimated_hours'] >= 0
        assert 'completed_tasks' in stats
        assert len(stats['completed_tasks']) == 3

    def test_get_weekly_task_stats_no_tasks(self, test_session):
        """Test weekly stats with no tasks"""
        task_mgr = TaskManager()
        task_mgr.session = test_session

        stats = task_mgr.get_weekly_task_stats()

        assert stats['tasks_completed_this_week'] == 0
        assert stats['tasks_created_this_week'] == 0
        assert stats['completion_rate'] == 0
        assert len(stats['completed_tasks']) == 0
