"""
Guardian Workflow Executor
Executes no-code workflows created by the workflow builder
"""

import asyncio
import json
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from workflow_builder import GuardianWorkflowBuilder, WorkflowNode
from orchestrator import guardian_orchestrator

logger = logging.getLogger(__name__)

class WorkflowExecutionContext:
    """Context for workflow execution"""
    
    def __init__(self, workflow_id: str, execution_id: str, input_data: Dict[str, Any]):
        self.workflow_id = workflow_id
        self.execution_id = execution_id
        self.input_data = input_data
        self.variables = input_data.copy()
        self.node_results = {}
        self.current_node = None
        self.execution_status = "running"
        self.start_time = datetime.now()
        self.end_time = None
        self.error_message = None

class WorkflowExecutor:
    """
    Executes workflows created by the no-code workflow builder
    """
    
    def __init__(self, workflow_builder: GuardianWorkflowBuilder):
        self.workflow_builder = workflow_builder
        self.active_executions = {}
        
    async def execute_workflow(self, workflow_id: str, input_data: Dict[str, Any]) -> str:
        """Execute a workflow with input data"""
        
        if workflow_id not in self.workflow_builder.workflows:
            raise ValueError(f"Workflow '{workflow_id}' not found")
        
        execution_id = f"exec_{workflow_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Create execution context
        context = WorkflowExecutionContext(workflow_id, execution_id, input_data)
        self.active_executions[execution_id] = context
        
        logger.info(f"🚀 Starting workflow execution: {execution_id}")
        
        try:
            # Find start node (trigger node)
            workflow = self.workflow_builder.workflows[workflow_id]
            start_node = None
            
            for node_id, node_data in workflow["nodes"].items():
                if node_data["type"] == "trigger":
                    start_node = node_id
                    break
            
            if not start_node:
                raise ValueError("No trigger node found in workflow")
            
            # Execute workflow starting from trigger node
            await self._execute_node(context, start_node)
            
            # Mark execution as completed
            context.execution_status = "completed"
            context.end_time = datetime.now()
            
            logger.info(f"✅ Workflow execution completed: {execution_id}")
            
        except Exception as e:
            context.execution_status = "failed"
            context.error_message = str(e)
            context.end_time = datetime.now()
            
            logger.error(f"❌ Workflow execution failed: {execution_id} - {e}")
            raise
        
        return execution_id
    
    async def _execute_node(self, context: WorkflowExecutionContext, node_id: str):
        """Execute a specific node in the workflow"""
        
        workflow = self.workflow_builder.workflows[context.workflow_id]
        node_data = workflow["nodes"].get(node_id)
        
        if not node_data:
            raise ValueError(f"Node '{node_id}' not found in workflow")
        
        context.current_node = node_id
        
        logger.info(f"🔄 Executing node: {node_data['name']} ({node_data['type']})")
        
        try:
            if node_data["type"] == "trigger":
                result = await self._execute_trigger_node(context, node_data)
            elif node_data["type"] == "action":
                result = await self._execute_action_node(context, node_data)
            elif node_data["type"] == "condition":
                result = await self._execute_condition_node(context, node_data)
            elif node_data["type"] == "parallel":
                result = await self._execute_parallel_node(context, node_data)
            else:
                raise ValueError(f"Unknown node type: {node_data['type']}")
            
            # Store node result
            context.node_results[node_id] = {
                "status": "completed",
                "result": result,
                "timestamp": datetime.now().isoformat()
            }
            
            # Execute next nodes
            await self._execute_next_nodes(context, node_id)
            
        except Exception as e:
            context.node_results[node_id] = {
                "status": "failed",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
            raise
    
    async def _execute_trigger_node(self, context: WorkflowExecutionContext, node_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a trigger node"""
        logger.info(f"🚀 Trigger: {node_data['name']}")
        
        # Validate required fields
        required_fields = node_data["config"].get("required_fields", [])
        missing_fields = [field for field in required_fields if field not in context.input_data]
        
        if missing_fields:
            raise ValueError(f"Missing required fields: {missing_fields}")
        
        return {
            "trigger_type": node_data["config"].get("trigger_type"),
            "validated_data": context.input_data
        }
    
    async def _execute_action_node(self, context: WorkflowExecutionContext, node_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute an action node"""
        config = node_data["config"]
        agent = config.get("agent")
        action = config.get("action")
        
        logger.info(f"⚡ Action: {node_data['name']} - {agent}.{action}")
        
        if agent and action:
            # Create task data for A2A agent
            task_data = {
                "method": action,
                "params": {
                    "patient_id": context.variables.get("patient_id"),
                    "flight_number": context.variables.get("flight_number"),
                    "execution_id": context.execution_id,
                    **context.variables  # Include all context variables
                }
            }
            
            # Send task to agent via orchestrator
            result = await guardian_orchestrator._send_a2a_task(agent, task_data)
            
            return {
                "agent": agent,
                "action": action,
                "result": result,
                "status": "success"
            }
        else:
            # Handle non-agent actions
            if action == "log_completion":
                return {
                    "action": "log_completion",
                    "message": "Workflow completed successfully",
                    "status": "success"
                }
            
            return {
                "action": action,
                "status": "success"
            }
    
    async def _execute_condition_node(self, context: WorkflowExecutionContext, node_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a condition node"""
        condition = node_data["config"].get("condition")
        
        logger.info(f"❓ Condition: {node_data['name']} - {condition}")
        
        # Simulate condition evaluation
        if condition == "flight_eta_less_than_6_hours":
            # In real implementation, this would check actual flight ETA
            await asyncio.sleep(2)  # Simulate waiting
            result = True  # Simulate condition met
        else:
            result = True  # Default to true for other conditions
        
        return {
            "condition": condition,
            "result": result,
            "status": "evaluated"
        }
    
    async def _execute_parallel_node(self, context: WorkflowExecutionContext, node_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a parallel node"""
        logger.info(f"🔄 Parallel: {node_data['name']}")
        
        # Find all nodes that depend on this parallel node
        workflow = self.workflow_builder.workflows[context.workflow_id]
        dependent_nodes = []
        
        for connection in workflow["connections"]:
            if connection["from"] == context.current_node:
                dependent_nodes.append(connection["to"])
        
        # Execute dependent nodes in parallel
        if dependent_nodes:
            tasks = []
            for node_id in dependent_nodes:
                task = self._execute_node(context, node_id)
                tasks.append(task)
            
            # Wait for all parallel tasks to complete
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Check results
            successful_tasks = 0
            failed_tasks = 0
            
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    failed_tasks += 1
                    logger.error(f"❌ Parallel task {dependent_nodes[i]} failed: {result}")
                else:
                    successful_tasks += 1
            
            return {
                "parallel_execution": True,
                "successful_tasks": successful_tasks,
                "failed_tasks": failed_tasks,
                "total_tasks": len(dependent_nodes),
                "status": "completed" if failed_tasks == 0 else "partial_failure"
            }
        
        return {
            "parallel_execution": True,
            "status": "completed"
        }
    
    async def _execute_next_nodes(self, context: WorkflowExecutionContext, current_node_id: str):
        """Execute next nodes based on workflow connections"""
        
        workflow = self.workflow_builder.workflows[context.workflow_id]
        
        # Find next nodes
        next_nodes = []
        for connection in workflow["connections"]:
            if connection["from"] == current_node_id:
                next_nodes.append(connection["to"])
        
        # Execute next nodes (except for parallel nodes which handle their own execution)
        for next_node_id in next_nodes:
            node_data = workflow["nodes"].get(next_node_id)
            if node_data and node_data["type"] != "parallel":
                await self._execute_node(context, next_node_id)
    
    def get_execution_status(self, execution_id: str) -> Optional[Dict[str, Any]]:
        """Get status of workflow execution"""
        if execution_id not in self.active_executions:
            return None
        
        context = self.active_executions[execution_id]
        
        return {
            "execution_id": execution_id,
            "workflow_id": context.workflow_id,
            "status": context.execution_status,
            "start_time": context.start_time.isoformat(),
            "end_time": context.end_time.isoformat() if context.end_time else None,
            "current_node": context.current_node,
            "node_results": context.node_results,
            "error_message": context.error_message,
            "execution_duration": (
                (context.end_time or datetime.now()) - context.start_time
            ).total_seconds()
        }
    
    def list_active_executions(self) -> Dict[str, Dict[str, Any]]:
        """List all active workflow executions"""
        return {
            execution_id: self.get_execution_status(execution_id)
            for execution_id in self.active_executions.keys()
        }

# Example usage and testing
async def test_workflow_execution():
    """Test workflow execution with sample data"""
    
    # Create workflow builder and executor
    builder = GuardianWorkflowBuilder()
    executor = WorkflowExecutor(builder)
    
    # Create a workflow from template
    workflow_id = builder.create_workflow_from_template(
        "medical_tourism_basic", 
        "Test Medical Tourism Workflow"
    )
    
    # Sample input data
    input_data = {
        "patient_id": "P001",
        "patient_name": "John Doe",
        "flight_number": "AA1234",
        "flight_date": "2024-02-15",
        "flight_time": "14:30:00",
        "hotel_ref": "HOTEL_REF_001",
        "hospital_ref": "MED_APPT_001",
        "emergency_contacts": ["+1-555-0001"],
        "special_requirements": "Wheelchair accessible",
        "medical_conditions": ["Diabetes"]
    }
    
    print("🚀 Testing Workflow Execution")
    print("=" * 50)
    
    # Execute workflow
    execution_id = await executor.execute_workflow(workflow_id, input_data)
    
    print(f"✅ Workflow executed with ID: {execution_id}")
    
    # Get execution status
    status = executor.get_execution_status(execution_id)
    
    print(f"\n📊 Execution Status:")
    print(f"   Status: {status['status']}")
    print(f"   Duration: {status['execution_duration']:.2f} seconds")
    print(f"   Nodes executed: {len(status['node_results'])}")
    
    # Show node results
    print(f"\n📋 Node Results:")
    for node_id, result in status["node_results"].items():
        print(f"   {node_id}: {result['status']}")

if __name__ == "__main__":
    # Run test
    asyncio.run(test_workflow_execution())
