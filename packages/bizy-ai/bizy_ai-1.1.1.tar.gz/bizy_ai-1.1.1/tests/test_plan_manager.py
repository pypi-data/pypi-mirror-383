"""
Tests for plan_manager module
Testing business plan display and stats integration
"""

import pytest
from agent.tasks import TaskManager
from agent.models import Goal, BusinessPlan


class TestPlanManagerStats:
    """Test plan manager stats integration"""

    def test_weekly_task_stats_keys(self, test_session, sample_goal):
        """Test that get_weekly_task_stats returns correct keys for plan display"""
        task_mgr = TaskManager()
        task_mgr.session = test_session

        # Create some completed tasks
        for i in range(3):
            task = task_mgr.create_task(
                title=f"Test Task {i+1}",
                parent_goal_id=sample_goal.id
            )
            task_mgr.complete_task(task.id)

        # Get stats
        stats = task_mgr.get_weekly_task_stats()

        # Verify new keys exist (used by plan show command)
        assert 'tasks_completed_this_week' in stats
        assert 'tasks_created_this_week' in stats
        assert 'completion_rate' in stats
        assert 'total_estimated_hours' in stats
        assert 'completed_tasks' in stats
        assert 'categories' in stats

        # Verify old keys don't exist
        assert 'average_completion_rate' not in stats
        assert 'total_tasks_completed' not in stats
        assert 'total_tasks_planned' not in stats

        # Verify values are correct
        assert stats['tasks_completed_this_week'] == 3
        assert stats['completion_rate'] >= 0

    def test_velocity_uses_completed_at(self, test_session):
        """Test that velocity is calculated using completed_at timestamps"""
        task_mgr = TaskManager()
        task_mgr.session = test_session

        # Create and complete tasks
        for i in range(5):
            task = task_mgr.create_task(title=f"Task {i+1}")
            task_mgr.complete_task(task.id)

        # Get velocity (should be > 0 now that we use completed_at)
        velocity = task_mgr.get_task_velocity(days=7)

        assert velocity > 0, "Velocity should be greater than 0 when tasks are completed"
        assert velocity == pytest.approx(5/7, rel=0.01), "Velocity should be ~0.71 tasks/day (5 tasks / 7 days)"

    def test_stats_with_no_tasks(self, test_session):
        """Test stats display with no tasks"""
        task_mgr = TaskManager()
        task_mgr.session = test_session

        stats = task_mgr.get_weekly_task_stats()

        assert stats['tasks_completed_this_week'] == 0
        assert stats['tasks_created_this_week'] == 0
        assert stats['completion_rate'] == 0
        assert len(stats['completed_tasks']) == 0
