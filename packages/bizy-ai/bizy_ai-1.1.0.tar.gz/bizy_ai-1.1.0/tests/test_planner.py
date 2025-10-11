"""
Tests for BusinessPlanner
Testing goal management and progress calculation
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
from agent.planner import BusinessPlanner
from agent.models import Goal, BusinessPlan


class TestBusinessPlanner:
    """Test BusinessPlanner functionality"""

    @patch('agent.planner.anthropic.Anthropic')
    def test_calculate_goal_progress_no_tasks(self, mock_anthropic, test_session, sample_goal):
        """Test progress calculation with no tasks"""
        planner = BusinessPlanner()
        planner.session = test_session
        planner.task_mgr.session = test_session

        progress = planner.calculate_goal_progress(sample_goal.id)

        assert progress == 0

    @patch('agent.planner.anthropic.Anthropic')
    def test_calculate_goal_progress_with_tasks(self, mock_anthropic, test_session, sample_goal):
        """Test progress calculation with completed and pending tasks"""
        planner = BusinessPlanner()
        planner.session = test_session
        planner.task_mgr.session = test_session

        # Create tasks for the goal
        completed_task = planner.task_mgr.create_task(
            title="Completed Task",
            parent_goal_id=sample_goal.id
        )
        planner.task_mgr.complete_task(completed_task.id)

        planner.task_mgr.create_task(
            title="Pending Task",
            parent_goal_id=sample_goal.id
        )

        progress = planner.calculate_goal_progress(sample_goal.id)

        assert progress == 50.0  # 1 out of 2 tasks completed

    @patch('agent.planner.anthropic.Anthropic')
    def test_calculate_goal_progress_all_completed(self, mock_anthropic, test_session, sample_goal):
        """Test progress with all tasks completed"""
        planner = BusinessPlanner()
        planner.session = test_session
        planner.task_mgr.session = test_session

        # Create all completed tasks
        for i in range(3):
            task = planner.task_mgr.create_task(
                title=f"Completed Task {i}",
                parent_goal_id=sample_goal.id
            )
            planner.task_mgr.complete_task(task.id)

        progress = planner.calculate_goal_progress(sample_goal.id)

        assert progress == 100.0

        # Verify goal is marked as completed
        test_session.refresh(sample_goal)
        assert sample_goal.status == "completed"

    @patch('agent.planner.anthropic.Anthropic')
    def test_create_goal(self, mock_anthropic, test_session):
        """Test creating a new goal"""
        planner = BusinessPlanner()
        planner.session = test_session

        goal = planner.create_goal(
            title="New Goal",
            description="Test goal description",
            horizon="monthly",
            target_date=datetime(2025, 12, 31)
        )

        assert goal.id is not None
        assert goal.title == "New Goal"
        assert goal.horizon == "monthly"
        assert goal.status == "active"

    @patch('agent.planner.anthropic.Anthropic')
    def test_get_active_goals(self, mock_anthropic, test_session, sample_goal):
        """Test retrieving active goals"""
        planner = BusinessPlanner()
        planner.session = test_session

        # Create another active goal
        planner.create_goal(title="Another Goal", description="Test goal", horizon="quarterly")

        active_goals = planner.get_active_goals()

        assert len(active_goals) >= 2

    @patch('agent.planner.anthropic.Anthropic')
    def test_break_down_goal(self, mock_anthropic, test_session, sample_goal):
        """Test AI-powered goal breakdown (mocked)"""
        # Mock the AI response
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_content = MagicMock()
        mock_content.text = '''[
            {
                "title": "Task 1",
                "description": "First task",
                "priority": 1,
                "estimated_hours": 8,
                "category": "development",
                "dependencies": []
            },
            {
                "title": "Task 2",
                "description": "Second task",
                "priority": 2,
                "estimated_hours": 4,
                "category": "testing",
                "dependencies": [0]
            }
        ]'''
        mock_response.content = [mock_content]
        mock_client.messages.create.return_value = mock_response
        mock_anthropic.return_value = mock_client

        planner = BusinessPlanner()
        planner.session = test_session
        planner.task_mgr.session = test_session
        planner.client = mock_client

        tasks = planner.break_down_goal(sample_goal.id)

        assert tasks is not None
        assert len(tasks) == 2
        assert tasks[0].title == "Task 1"
        assert tasks[1].title == "Task 2"
        assert all(task.parent_goal_id == sample_goal.id for task in tasks)

    @patch('agent.planner.anthropic.Anthropic')
    def test_create_business_plan(self, mock_anthropic, test_session):
        """Test creating a business plan"""
        planner = BusinessPlanner()
        planner.session = test_session

        plan = planner.create_business_plan(
            vision="Test Vision",
            mission="Test Mission",
            value_proposition="Test Value Prop",
            target_market="Test Market",
            revenue_model="Test Revenue"
        )

        assert plan.id is not None
        assert plan.vision == "Test Vision"
        assert plan.is_active is True

    @patch('agent.planner.anthropic.Anthropic')
    def test_get_active_business_plan(self, mock_anthropic, test_session, sample_business_plan):
        """Test retrieving active business plan"""
        planner = BusinessPlanner()
        planner.session = test_session

        active_plan = planner.get_active_business_plan()

        assert active_plan is not None
        assert active_plan.is_active is True
        assert active_plan.id == sample_business_plan.id

    @patch('agent.planner.anthropic.Anthropic')
    def test_update_goal_progress(self, mock_anthropic, test_session, sample_goal):
        """Test manually updating goal progress"""
        planner = BusinessPlanner()
        planner.session = test_session

        updated_goal = planner.update_goal_progress(sample_goal.id, 75.0)

        assert updated_goal.progress_percentage == 75.0
        assert updated_goal.updated_at is not None
