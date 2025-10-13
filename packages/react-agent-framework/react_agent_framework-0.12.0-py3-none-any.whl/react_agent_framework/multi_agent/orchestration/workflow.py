"""
Workflow management for multi-agent task execution.

Provides DAG-based workflow definition and execution.
"""

import time
import threading
from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, List, Set, Optional, Any, Callable


class WorkflowStatus(str, Enum):
    """Workflow execution status."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class StepType(str, Enum):
    """Workflow step type."""

    SEQUENTIAL = "sequential"  # Execute in sequence
    PARALLEL = "parallel"  # Execute in parallel
    CONDITIONAL = "conditional"  # Execute if condition met
    LOOP = "loop"  # Execute multiple times


@dataclass
class WorkflowStep:
    """
    A step in a workflow.

    Attributes:
        step_id: Unique step identifier
        name: Human-readable step name
        step_type: Type of step
        action: Action to execute (function or agent task)
        params: Step parameters
        dependencies: IDs of steps that must complete first
        condition: Condition function for conditional steps
        max_retries: Maximum retry attempts
        timeout: Step timeout in seconds
    """

    step_id: str
    name: str
    action: Callable
    step_type: StepType = StepType.SEQUENTIAL
    params: Dict[str, Any] = field(default_factory=dict)
    dependencies: Set[str] = field(default_factory=set)
    condition: Optional[Callable] = None
    max_retries: int = 3
    timeout: float = 60.0

    # Execution state
    status: WorkflowStatus = WorkflowStatus.PENDING
    result: Optional[Any] = None
    error: Optional[str] = None
    start_time: Optional[float] = None
    end_time: Optional[float] = None
    retry_count: int = 0

    def can_execute(self, completed_steps: Set[str]) -> bool:
        """Check if step can execute (dependencies met)."""
        return self.dependencies.issubset(completed_steps)

    def should_execute(self, context: Dict[str, Any]) -> bool:
        """Check if step should execute (condition met)."""
        if self.step_type != StepType.CONDITIONAL:
            return True

        if self.condition is None:
            return True

        return self.condition(context)

    def execute(self, context: Dict[str, Any]) -> Any:
        """
        Execute step action.

        Args:
            context: Workflow context

        Returns:
            Step result
        """
        self.status = WorkflowStatus.RUNNING
        self.start_time = time.time()

        try:
            # Merge params with context
            exec_params = {**self.params, **context}

            # Execute action
            result = self.action(**exec_params)

            self.status = WorkflowStatus.COMPLETED
            self.result = result
            self.end_time = time.time()

            return result

        except Exception as e:
            self.status = WorkflowStatus.FAILED
            self.error = str(e)
            self.end_time = time.time()
            raise


class Workflow:
    """
    Workflow definition (DAG of steps).

    Example:
        >>> workflow = Workflow("data-pipeline")
        >>>
        >>> # Add steps
        >>> workflow.add_step(
        ...     step_id="fetch",
        ...     name="Fetch Data",
        ...     action=fetch_data,
        ...     params={"source": "api"}
        ... )
        >>>
        >>> workflow.add_step(
        ...     step_id="process",
        ...     name="Process Data",
        ...     action=process_data,
        ...     dependencies={"fetch"}
        ... )
        >>>
        >>> workflow.add_step(
        ...     step_id="save",
        ...     name="Save Results",
        ...     action=save_results,
        ...     dependencies={"process"}
        ... )
        >>>
        >>> # Execute
        >>> engine = WorkflowEngine()
        >>> result = engine.execute(workflow)
    """

    def __init__(self, workflow_id: str, name: Optional[str] = None):
        """
        Initialize workflow.

        Args:
            workflow_id: Unique workflow identifier
            name: Human-readable workflow name
        """
        self.workflow_id = workflow_id
        self.name = name or workflow_id
        self.steps: Dict[str, WorkflowStep] = {}
        self.metadata: Dict[str, Any] = {}

    def add_step(
        self,
        step_id: str,
        name: str,
        action: Callable,
        step_type: StepType = StepType.SEQUENTIAL,
        params: Optional[Dict[str, Any]] = None,
        dependencies: Optional[Set[str]] = None,
        condition: Optional[Callable] = None,
        max_retries: int = 3,
        timeout: float = 60.0
    ) -> "Workflow":
        """
        Add step to workflow.

        Args:
            step_id: Step identifier
            name: Step name
            action: Action function
            step_type: Type of step
            params: Step parameters
            dependencies: Dependency step IDs
            condition: Condition function
            max_retries: Max retry attempts
            timeout: Step timeout

        Returns:
            Self for chaining
        """
        step = WorkflowStep(
            step_id=step_id,
            name=name,
            action=action,
            step_type=step_type,
            params=params or {},
            dependencies=dependencies or set(),
            condition=condition,
            max_retries=max_retries,
            timeout=timeout
        )

        self.steps[step_id] = step
        return self

    def get_ready_steps(self, completed_steps: Set[str]) -> List[WorkflowStep]:
        """Get steps ready to execute."""
        return [
            step for step in self.steps.values()
            if step.status == WorkflowStatus.PENDING
            and step.can_execute(completed_steps)
        ]

    def get_parallel_steps(self) -> List[List[str]]:
        """Get groups of steps that can run in parallel."""
        # Topological sort with parallel grouping
        completed = set()
        parallel_groups = []

        while len(completed) < len(self.steps):
            # Find steps with dependencies met
            ready = [
                step_id for step_id, step in self.steps.items()
                if step_id not in completed
                and step.dependencies.issubset(completed)
            ]

            if not ready:
                break  # Circular dependency or error

            parallel_groups.append(ready)
            completed.update(ready)

        return parallel_groups

    def validate(self) -> bool:
        """Validate workflow (check for cycles, missing dependencies)."""
        # Check for missing dependencies
        all_steps = set(self.steps.keys())
        for step in self.steps.values():
            if not step.dependencies.issubset(all_steps):
                return False

        # Check for cycles (simple DFS)
        def has_cycle(step_id: str, visited: Set[str], stack: Set[str]) -> bool:
            visited.add(step_id)
            stack.add(step_id)

            step = self.steps[step_id]
            for dep in step.dependencies:
                if dep not in visited:
                    if has_cycle(dep, visited, stack):
                        return True
                elif dep in stack:
                    return True

            stack.remove(step_id)
            return False

        visited = set()
        for step_id in self.steps:
            if step_id not in visited:
                if has_cycle(step_id, visited, set()):
                    return False

        return True


class WorkflowEngine:
    """
    Workflow execution engine.

    Executes workflows with support for:
    - Sequential execution
    - Parallel execution
    - Conditional steps
    - Retry logic
    - Timeout handling

    Example:
        >>> engine = WorkflowEngine()
        >>> result = engine.execute(workflow, context={"input": data})
    """

    def __init__(self):
        """Initialize workflow engine."""
        self._lock = threading.Lock()

    def execute(
        self,
        workflow: Workflow,
        context: Optional[Dict[str, Any]] = None,
        parallel: bool = True
    ) -> Dict[str, Any]:
        """
        Execute workflow.

        Args:
            workflow: Workflow to execute
            context: Initial context
            parallel: Enable parallel execution

        Returns:
            Dictionary with results and metadata
        """
        if not workflow.validate():
            raise ValueError("Invalid workflow: contains cycles or missing dependencies")

        context = context or {}
        completed_steps = set()
        failed_steps = set()

        start_time = time.time()

        if parallel:
            # Execute in parallel groups
            parallel_groups = workflow.get_parallel_steps()

            for group in parallel_groups:
                self._execute_parallel_group(
                    workflow,
                    group,
                    context,
                    completed_steps,
                    failed_steps
                )
        else:
            # Execute sequentially
            while len(completed_steps) < len(workflow.steps):
                ready_steps = workflow.get_ready_steps(completed_steps)

                if not ready_steps:
                    break  # No more steps can execute

                for step in ready_steps:
                    success = self._execute_step(step, context)
                    if success:
                        completed_steps.add(step.step_id)
                    else:
                        failed_steps.add(step.step_id)

        end_time = time.time()

        # Collect results
        results = {
            "workflow_id": workflow.workflow_id,
            "status": "completed" if not failed_steps else "failed",
            "completed_steps": len(completed_steps),
            "failed_steps": len(failed_steps),
            "total_steps": len(workflow.steps),
            "duration": end_time - start_time,
            "step_results": {
                step_id: step.result
                for step_id, step in workflow.steps.items()
                if step.result is not None
            },
            "errors": {
                step_id: step.error
                for step_id, step in workflow.steps.items()
                if step.error is not None
            }
        }

        return results

    def _execute_parallel_group(
        self,
        workflow: Workflow,
        step_ids: List[str],
        context: Dict[str, Any],
        completed_steps: Set[str],
        failed_steps: Set[str]
    ):
        """Execute a group of steps in parallel."""
        threads = []

        for step_id in step_ids:
            step = workflow.steps[step_id]

            # Check condition
            if not step.should_execute(context):
                completed_steps.add(step_id)
                continue

            thread = threading.Thread(
                target=self._execute_step_thread,
                args=(step, context, completed_steps, failed_steps)
            )
            threads.append(thread)
            thread.start()

        # Wait for all threads
        for thread in threads:
            thread.join()

    def _execute_step_thread(
        self,
        step: WorkflowStep,
        context: Dict[str, Any],
        completed_steps: Set[str],
        failed_steps: Set[str]
    ):
        """Execute step in thread."""
        success = self._execute_step(step, context)

        with self._lock:
            if success:
                completed_steps.add(step.step_id)
                # Update context with result
                if step.result is not None:
                    context[step.step_id] = step.result
            else:
                failed_steps.add(step.step_id)

    def _execute_step(
        self,
        step: WorkflowStep,
        context: Dict[str, Any]
    ) -> bool:
        """
        Execute single step with retry logic.

        Args:
            step: Step to execute
            context: Execution context

        Returns:
            True if successful
        """
        for attempt in range(step.max_retries):
            try:
                step.retry_count = attempt
                step.execute(context)

                # Update context with result
                if step.result is not None:
                    context[step.step_id] = step.result

                return True

            except Exception as e:
                if attempt < step.max_retries - 1:
                    # Retry
                    time.sleep(0.1 * (2 ** attempt))  # Exponential backoff
                    continue
                else:
                    # Failed after retries
                    step.status = WorkflowStatus.FAILED
                    step.error = str(e)
                    return False

        return False
