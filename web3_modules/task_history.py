"""
Task History Tracking for AgentX

Stores and retrieves task execution history with:
- Local file-based storage
- Task status tracking
- Performance metrics
- Search and filter capabilities
"""

import json
import os
import time
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from pathlib import Path


@dataclass
class TaskRecord:
    """Task record structure"""
    task_id: str
    agent_id: int
    requester_id: int
    description: str
    task_type: str
    input_data: Dict[str, Any]
    budget: str
    status: str  # "pending", "executing", "completed", "failed"
    created_at: int
    completed_at: Optional[int] = None
    result: Optional[Dict[str, Any]] = None
    execution_time: Optional[float] = None
    payment_tx: Optional[str] = None
    attestation_tx: Optional[str] = None
    score: Optional[int] = None


class TaskHistoryManager:
    """
    Manage task history with file-based storage
    
    Features:
    - Store task records
    - Query by status, agent, date
    - Performance analytics
    - Export/import
    """
    
    def __init__(self, storage_path: Optional[str] = None):
        """
        Initialize Task History Manager
        
        Args:
            storage_path: Path to store task history (default: ~/.agentx/tasks.json)
        """
        if storage_path is None:
            home = Path.home()
            agentx_dir = home / ".agentx"
            agentx_dir.mkdir(exist_ok=True)
            storage_path = str(agentx_dir / "tasks.json")
        
        self.storage_path = storage_path
        self.tasks: Dict[str, TaskRecord] = {}
        self._load()
    
    def _load(self):
        """Load tasks from storage"""
        try:
            if os.path.exists(self.storage_path):
                with open(self.storage_path, 'r') as f:
                    data = json.load(f)
                    for task_id, task_data in data.items():
                        self.tasks[task_id] = TaskRecord(**task_data)
        except Exception as e:
            print(f"⚠️  Failed to load task history: {e}")
    
    def _save(self):
        """Save tasks to storage"""
        try:
            with open(self.storage_path, 'w') as f:
                data = {k: asdict(v) for k, v in self.tasks.items()}
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"⚠️  Failed to save task history: {e}")
    
    def create_task(
        self,
        task_id: str,
        agent_id: int,
        requester_id: int,
        description: str,
        task_type: str,
        input_data: Dict[str, Any],
        budget: str
    ) -> TaskRecord:
        """
        Create new task record
        
        Args:
            task_id: Unique task identifier
            agent_id: Agent token ID
            requester_id: Requester's agent ID
            description: Task description
            task_type: Type of task
            input_data: Task input data
            budget: Task budget
        
        Returns:
            Created TaskRecord
        """
        task = TaskRecord(
            task_id=task_id,
            agent_id=agent_id,
            requester_id=requester_id,
            description=description,
            task_type=task_type,
            input_data=input_data,
            budget=budget,
            status="pending",
            created_at=int(time.time())
        )
        
        self.tasks[task_id] = task
        self._save()
        
        return task
    
    def update_status(self, task_id: str, status: str, result: Optional[Dict] = None):
        """
        Update task status
        
        Args:
            task_id: Task identifier
            status: New status
            result: Optional task result
        """
        if task_id not in self.tasks:
            raise ValueError(f"Task {task_id} not found")
        
        task = self.tasks[task_id]
        task.status = status
        
        if status == "executing":
            pass  # Just update status
        
        elif status == "completed":
            task.completed_at = int(time.time())
            task.execution_time = task.completed_at - task.created_at
            if result:
                task.result = result
        
        elif status == "failed":
            task.completed_at = int(time.time())
            if result:
                task.result = result
        
        self._save()
    
    def set_payment_tx(self, task_id: str, tx_hash: str):
        """Set payment transaction hash"""
        if task_id in self.tasks:
            self.tasks[task_id].payment_tx = tx_hash
            self._save()
    
    def set_attestation_tx(self, task_id: str, tx_hash: str, score: int):
        """Set attestation transaction hash and score"""
        if task_id in self.tasks:
            self.tasks[task_id].attestation_tx = tx_hash
            self.tasks[task_id].score = score
            self._save()
    
    def get_task(self, task_id: str) -> Optional[TaskRecord]:
        """Get task by ID"""
        return self.tasks.get(task_id)
    
    def get_tasks_by_status(self, status: str) -> List[TaskRecord]:
        """Get all tasks with specific status"""
        return [
            task for task in self.tasks.values()
            if task.status == status
        ]
    
    def get_tasks_by_agent(self, agent_id: int) -> List[TaskRecord]:
        """Get all tasks for specific agent"""
        return [
            task for task in self.tasks.values()
            if task.agent_id == agent_id
        ]
    
    def get_tasks_by_requester(self, requester_id: int) -> List[TaskRecord]:
        """Get all tasks from specific requester"""
        return [
            task for task in self.tasks.values()
            if task.requester_id == requester_id
        ]
    
    def get_recent_tasks(self, limit: int = 10) -> List[TaskRecord]:
        """Get most recent tasks"""
        sorted_tasks = sorted(
            self.tasks.values(),
            key=lambda x: x.created_at,
            reverse=True
        )
        return sorted_tasks[:limit]
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get task statistics"""
        if not self.tasks:
            return {
                "total_tasks": 0,
                "completed": 0,
                "failed": 0,
                "pending": 0,
                "avg_execution_time": 0,
                "success_rate": 0
            }
        
        total = len(self.tasks)
        completed = sum(1 for t in self.tasks.values() if t.status == "completed")
        failed = sum(1 for t in self.tasks.values() if t.status == "failed")
        pending = sum(1 for t in self.tasks.values() if t.status == "pending")
        
        execution_times = [
            t.execution_time for t in self.tasks.values()
            if t.execution_time is not None
        ]
        avg_time = sum(execution_times) / len(execution_times) if execution_times else 0
        
        return {
            "total_tasks": total,
            "completed": completed,
            "failed": failed,
            "pending": pending,
            "executing": sum(1 for t in self.tasks.values() if t.status == "executing"),
            "avg_execution_time": round(avg_time, 2),
            "success_rate": round(completed / total * 100, 2) if total > 0 else 0,
            "total_budget": sum(float(t.budget.replace('$', '')) for t in self.tasks.values() if t.budget.startswith('$'))
        }
    
    def export_tasks(self, output_path: str, task_ids: Optional[List[str]] = None):
        """Export tasks to JSON file"""
        if task_ids:
            tasks_to_export = {
                tid: asdict(self.tasks[tid])
                for tid in task_ids if tid in self.tasks
            }
        else:
            tasks_to_export = {
                tid: asdict(task)
                for tid, task in self.tasks.items()
            }
        
        with open(output_path, 'w') as f:
            json.dump(tasks_to_export, f, indent=2)
        
        print(f"✅ Exported {len(tasks_to_export)} tasks to {output_path}")
    
    def clear_old_tasks(self, days_old: int = 30):
        """Clear tasks older than specified days"""
        cutoff = int(time.time()) - (days_old * 24 * 60 * 60)
        
        to_delete = [
            task_id for task_id, task in self.tasks.items()
            if task.created_at < cutoff and task.status in ["completed", "failed"]
        ]
        
        for task_id in to_delete:
            del self.tasks[task_id]
        
        self._save()
        
        print(f"🗑️  Cleared {len(to_delete)} old tasks")
        
        return len(to_delete)


# Global instance for CLI usage
_task_history = None

def get_task_history() -> TaskHistoryManager:
    """Get or create global task history instance"""
    global _task_history
    if _task_history is None:
        _task_history = TaskHistoryManager()
    return _task_history
