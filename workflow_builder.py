"""
Guardian No-Code Workflow Builder
Visual workflow creation and management for medical tourism orchestration
"""

import json
import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime
import os

class WorkflowNode:
    """Represents a node in the workflow"""
    
    def __init__(self, node_id: str, node_type: str, name: str, config: Dict[str, Any]):
        self.node_id = node_id
        self.node_type = node_type  # trigger, action, condition, parallel
        self.name = name
        self.config = config
        self.next_nodes = []
        self.previous_nodes = []
    
    def add_next_node(self, node_id: str):
        """Add a next node in the workflow"""
        if node_id not in self.next_nodes:
            self.next_nodes.append(node_id)
    
    def add_previous_node(self, node_id: str):
        """Add a previous node in the workflow"""
        if node_id not in self.previous_nodes:
            self.previous_nodes.append(node_id)

class GuardianWorkflowBuilder:
    """
    No-Code Workflow Builder for Guardian Orchestrator
    """
    
    def __init__(self):
        self.workflows = {}
        self.nodes = {}
        self.templates = self._load_workflow_templates()
        
    def _load_workflow_templates(self) -> Dict[str, Dict[str, Any]]:
        """Load pre-built workflow templates"""
        return {
            "medical_tourism_basic": {
                "name": "Basic Medical Tourism Workflow",
                "description": "Standard workflow for medical tourism coordination",
                "nodes": [
                    {
                        "id": "start",
                        "type": "trigger",
                        "name": "Patient Booking Received",
                        "config": {
                            "trigger_type": "patient_booking",
                            "required_fields": ["patient_id", "flight_number", "hotel_ref", "hospital_ref"]
                        }
                    },
                    {
                        "id": "flight_monitor",
                        "type": "action",
                        "name": "Start Flight Monitoring",
                        "config": {
                            "agent": "flight_agent",
                            "action": "TrackFlight",
                            "timeout": 30
                        }
                    },
                    {
                        "id": "wait_trigger",
                        "type": "condition",
                        "name": "Wait for Coordination Trigger",
                        "config": {
                            "condition": "flight_eta_less_than_6_hours",
                            "timeout": 86400  # 24 hours max
                        }
                    },
                    {
                        "id": "parallel_coordination",
                        "type": "parallel",
                        "name": "Parallel Agent Coordination",
                        "config": {
                            "parallel_execution": True,
                            "timeout": 300  # 5 minutes
                        }
                    },
                    {
                        "id": "hotel_coord",
                        "type": "action",
                        "name": "Hotel Coordination",
                        "config": {
                            "agent": "hotel_agent",
                            "action": "ConfirmHotel",
                            "depends_on": "parallel_coordination"
                        }
                    },
                    {
                        "id": "hospital_coord",
                        "type": "action",
                        "name": "Hospital Coordination",
                        "config": {
                            "agent": "hospital_agent",
                            "action": "ConfirmHospital",
                            "depends_on": "parallel_coordination"
                        }
                    },
                    {
                        "id": "notification_coord",
                        "type": "action",
                        "name": "Family Notification",
                        "config": {
                            "agent": "notification_agent",
                            "action": "SendFamilyUpdate",
                            "depends_on": "parallel_coordination"
                        }
                    },
                    {
                        "id": "voice_coord",
                        "type": "action",
                        "name": "Voice Communication",
                        "config": {
                            "agent": "voice_agent",
                            "action": "InitiateCall",
                            "depends_on": "parallel_coordination"
                        }
                    },
                    {
                        "id": "completion",
                        "type": "action",
                        "name": "Workflow Completion",
                        "config": {
                            "action": "log_completion",
                            "depends_on": ["hotel_coord", "hospital_coord", "notification_coord", "voice_coord"]
                        }
                    }
                ],
                "connections": [
                    {"from": "start", "to": "flight_monitor"},
                    {"from": "flight_monitor", "to": "wait_trigger"},
                    {"from": "wait_trigger", "to": "parallel_coordination"},
                    {"from": "parallel_coordination", "to": "hotel_coord"},
                    {"from": "parallel_coordination", "to": "hospital_coord"},
                    {"from": "parallel_coordination", "to": "notification_coord"},
                    {"from": "parallel_coordination", "to": "voice_coord"},
                    {"from": "hotel_coord", "to": "completion"},
                    {"from": "hospital_coord", "to": "completion"},
                    {"from": "notification_coord", "to": "completion"},
                    {"from": "voice_coord", "to": "completion"}
                ]
            },
            
            "emergency_workflow": {
                "name": "Emergency Medical Tourism Workflow",
                "description": "High-priority workflow for emergency medical cases",
                "nodes": [
                    {
                        "id": "emergency_start",
                        "type": "trigger",
                        "name": "Emergency Booking Received",
                        "config": {
                            "trigger_type": "emergency_patient_booking",
                            "priority": "high",
                            "required_fields": ["patient_id", "flight_number", "emergency_level"]
                        }
                    },
                    {
                        "id": "immediate_coordination",
                        "type": "parallel",
                        "name": "Immediate Coordination",
                        "config": {
                            "parallel_execution": True,
                            "timeout": 60,  # 1 minute
                            "priority": "high"
                        }
                    },
                    {
                        "id": "emergency_hotel",
                        "type": "action",
                        "name": "Emergency Hotel Coordination",
                        "config": {
                            "agent": "hotel_agent",
                            "action": "EmergencyHotelBooking",
                            "depends_on": "immediate_coordination"
                        }
                    },
                    {
                        "id": "emergency_hospital",
                        "type": "action",
                        "name": "Emergency Hospital Coordination",
                        "config": {
                            "agent": "hospital_agent",
                            "action": "EmergencyAppointment",
                            "depends_on": "immediate_coordination"
                        }
                    },
                    {
                        "id": "emergency_notification",
                        "type": "action",
                        "name": "Emergency Family Notification",
                        "config": {
                            "agent": "notification_agent",
                            "action": "EmergencyFamilyAlert",
                            "depends_on": "immediate_coordination"
                        }
                    },
                    {
                        "id": "emergency_voice",
                        "type": "action",
                        "name": "Emergency Voice Call",
                        "config": {
                            "agent": "voice_agent",
                            "action": "EmergencyCall",
                            "depends_on": "immediate_coordination"
                        }
                    }
                ],
                "connections": [
                    {"from": "emergency_start", "to": "immediate_coordination"},
                    {"from": "immediate_coordination", "to": "emergency_hotel"},
                    {"from": "immediate_coordination", "to": "emergency_hospital"},
                    {"from": "immediate_coordination", "to": "emergency_notification"},
                    {"from": "immediate_coordination", "to": "emergency_voice"}
                ]
            }
        }
    
    def create_workflow_from_template(self, template_name: str, workflow_name: str) -> str:
        """Create a workflow from a template"""
        if template_name not in self.templates:
            raise ValueError(f"Template '{template_name}' not found")
        
        template = self.templates[template_name]
        workflow_id = f"workflow_{workflow_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Create workflow
        self.workflows[workflow_id] = {
            "id": workflow_id,
            "name": workflow_name,
            "description": template["description"],
            "template": template_name,
            "created_at": datetime.now().isoformat(),
            "nodes": {},
            "connections": template["connections"]
        }
        
        # Create nodes
        for node_data in template["nodes"]:
            node = WorkflowNode(
                node_data["id"],
                node_data["type"],
                node_data["name"],
                node_data["config"]
            )
            self.nodes[f"{workflow_id}_{node_data['id']}"] = node
            self.workflows[workflow_id]["nodes"][node_data["id"]] = node_data
        
        print(f"✅ Created workflow '{workflow_name}' from template '{template_name}'")
        print(f"   Workflow ID: {workflow_id}")
        
        return workflow_id
    
    def create_custom_workflow(self, workflow_name: str, description: str) -> str:
        """Create a custom workflow from scratch"""
        workflow_id = f"workflow_{workflow_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        self.workflows[workflow_id] = {
            "id": workflow_id,
            "name": workflow_name,
            "description": description,
            "template": "custom",
            "created_at": datetime.now().isoformat(),
            "nodes": {},
            "connections": []
        }
        
        print(f"✅ Created custom workflow '{workflow_name}'")
        print(f"   Workflow ID: {workflow_id}")
        
        return workflow_id
    
    def add_node(self, workflow_id: str, node_id: str, node_type: str, name: str, config: Dict[str, Any]):
        """Add a node to a workflow"""
        if workflow_id not in self.workflows:
            raise ValueError(f"Workflow '{workflow_id}' not found")
        
        node = WorkflowNode(node_id, node_type, name, config)
        self.nodes[f"{workflow_id}_{node_id}"] = node
        
        self.workflows[workflow_id]["nodes"][node_id] = {
            "id": node_id,
            "type": node_type,
            "name": name,
            "config": config
        }
        
        print(f"✅ Added {node_type} node '{name}' to workflow '{workflow_id}'")
    
    def connect_nodes(self, workflow_id: str, from_node: str, to_node: str):
        """Connect two nodes in a workflow"""
        if workflow_id not in self.workflows:
            raise ValueError(f"Workflow '{workflow_id}' not found")
        
        # Add to connections list
        connection = {"from": from_node, "to": to_node}
        if connection not in self.workflows[workflow_id]["connections"]:
            self.workflows[workflow_id]["connections"].append(connection)
        
        # Update node connections
        from_node_key = f"{workflow_id}_{from_node}"
        to_node_key = f"{workflow_id}_{to_node}"
        
        if from_node_key in self.nodes:
            self.nodes[from_node_key].add_next_node(to_node)
        if to_node_key in self.nodes:
            self.nodes[to_node_key].add_previous_node(from_node)
        
        print(f"✅ Connected '{from_node}' → '{to_node}' in workflow '{workflow_id}'")
    
    def get_workflow_visualization(self, workflow_id: str) -> str:
        """Generate a visual representation of the workflow"""
        if workflow_id not in self.workflows:
            raise ValueError(f"Workflow '{workflow_id}' not found")
        
        workflow = self.workflows[workflow_id]
        visualization = f"\n🔄 Workflow: {workflow['name']}\n"
        visualization += f"📝 Description: {workflow['description']}\n"
        visualization += f"📅 Created: {workflow['created_at']}\n"
        visualization += "=" * 60 + "\n"
        
        # Show nodes
        visualization += "\n📋 Nodes:\n"
        for node_id, node_data in workflow["nodes"].items():
            node_type_icon = {
                "trigger": "🚀",
                "action": "⚡",
                "condition": "❓",
                "parallel": "🔄"
            }.get(node_data["type"], "📦")
            
            visualization += f"  {node_type_icon} {node_data['name']} ({node_data['type']})\n"
            if node_data["config"].get("agent"):
                visualization += f"    → Agent: {node_data['config']['agent']}\n"
            if node_data["config"].get("action"):
                visualization += f"    → Action: {node_data['config']['action']}\n"
        
        # Show connections
        visualization += "\n🔗 Connections:\n"
        for connection in workflow["connections"]:
            visualization += f"  {connection['from']} → {connection['to']}\n"
        
        return visualization
    
    def list_workflows(self):
        """List all workflows"""
        if not self.workflows:
            print("📭 No workflows created yet")
            return
        
        print("\n📋 Available Workflows:")
        print("=" * 60)
        
        for workflow_id, workflow in self.workflows.items():
            print(f"🆔 ID: {workflow_id}")
            print(f"📝 Name: {workflow['name']}")
            print(f"📄 Description: {workflow['description']}")
            print(f"🏗️ Template: {workflow['template']}")
            print(f"📅 Created: {workflow['created_at']}")
            print(f"📊 Nodes: {len(workflow['nodes'])}")
            print("-" * 60)
    
    def list_templates(self):
        """List available workflow templates"""
        print("\n🎨 Available Workflow Templates:")
        print("=" * 60)
        
        for template_id, template in self.templates.items():
            print(f"🆔 ID: {template_id}")
            print(f"📝 Name: {template['name']}")
            print(f"📄 Description: {template['description']}")
            print(f"📊 Nodes: {len(template['nodes'])}")
            print("-" * 60)
    
    def export_workflow(self, workflow_id: str, filename: str = None):
        """Export workflow to JSON file"""
        if workflow_id not in self.workflows:
            raise ValueError(f"Workflow '{workflow_id}' not found")
        
        if not filename:
            workflow_name = self.workflows[workflow_id]["name"].replace(" ", "_").lower()
            filename = f"{workflow_name}_workflow.json"
        
        workflow_data = self.workflows[workflow_id]
        
        with open(filename, 'w') as f:
            json.dump(workflow_data, f, indent=2)
        
        print(f"✅ Exported workflow to {filename}")
    
    def import_workflow(self, filename: str) -> str:
        """Import workflow from JSON file"""
        with open(filename, 'r') as f:
            workflow_data = json.load(f)
        
        workflow_id = workflow_data["id"]
        self.workflows[workflow_id] = workflow_data
        
        # Recreate nodes
        for node_id, node_data in workflow_data["nodes"].items():
            node = WorkflowNode(
                node_data["id"],
                node_data["type"],
                node_data["name"],
                node_data["config"]
            )
            self.nodes[f"{workflow_id}_{node_id}"] = node
        
        print(f"✅ Imported workflow from {filename}")
        print(f"   Workflow ID: {workflow_id}")
        
        return workflow_id

# Interactive workflow builder
class InteractiveWorkflowBuilder:
    """Interactive command-line workflow builder"""
    
    def __init__(self):
        self.builder = GuardianWorkflowBuilder()
    
    def run(self):
        """Run the interactive workflow builder"""
        print("🎨 Guardian No-Code Workflow Builder")
        print("=" * 50)
        
        while True:
            print("\n📋 Available Commands:")
            print("1. List templates")
            print("2. Create workflow from template")
            print("3. Create custom workflow")
            print("4. List workflows")
            print("5. View workflow")
            print("6. Add node")
            print("7. Connect nodes")
            print("8. Export workflow")
            print("9. Import workflow")
            print("0. Exit")
            
            choice = input("\n🔧 Choose an option (0-9): ").strip()
            
            if choice == "0":
                print("👋 Goodbye!")
                break
            elif choice == "1":
                self.builder.list_templates()
            elif choice == "2":
                self._create_from_template()
            elif choice == "3":
                self._create_custom()
            elif choice == "4":
                self.builder.list_workflows()
            elif choice == "5":
                self._view_workflow()
            elif choice == "6":
                self._add_node()
            elif choice == "7":
                self._connect_nodes()
            elif choice == "8":
                self._export_workflow()
            elif choice == "9":
                self._import_workflow()
            else:
                print("❌ Invalid option. Please try again.")
    
    def _create_from_template(self):
        """Create workflow from template"""
        self.builder.list_templates()
        template_id = input("\n🏗️ Enter template ID: ").strip()
        workflow_name = input("📝 Enter workflow name: ").strip()
        
        try:
            workflow_id = self.builder.create_workflow_from_template(template_id, workflow_name)
            print(f"✅ Workflow created with ID: {workflow_id}")
        except Exception as e:
            print(f"❌ Error: {e}")
    
    def _create_custom(self):
        """Create custom workflow"""
        workflow_name = input("📝 Enter workflow name: ").strip()
        description = input("📄 Enter description: ").strip()
        
        try:
            workflow_id = self.builder.create_custom_workflow(workflow_name, description)
            print(f"✅ Custom workflow created with ID: {workflow_id}")
        except Exception as e:
            print(f"❌ Error: {e}")
    
    def _view_workflow(self):
        """View workflow visualization"""
        if not self.builder.workflows:
            print("📭 No workflows to view")
            return
        
        self.builder.list_workflows()
        workflow_id = input("\n🆔 Enter workflow ID: ").strip()
        
        try:
            visualization = self.builder.get_workflow_visualization(workflow_id)
            print(visualization)
        except Exception as e:
            print(f"❌ Error: {e}")
    
    def _add_node(self):
        """Add node to workflow"""
        if not self.builder.workflows:
            print("📭 No workflows available")
            return
        
        self.builder.list_workflows()
        workflow_id = input("\n🆔 Enter workflow ID: ").strip()
        node_id = input("🔧 Enter node ID: ").strip()
        node_type = input("📦 Enter node type (trigger/action/condition/parallel): ").strip()
        name = input("📝 Enter node name: ").strip()
        
        # Get config based on node type
        config = {}
        if node_type == "action":
            agent = input("🤖 Enter agent name: ").strip()
            action = input("⚡ Enter action name: ").strip()
            config = {"agent": agent, "action": action}
        elif node_type == "condition":
            condition = input("❓ Enter condition: ").strip()
            config = {"condition": condition}
        
        try:
            self.builder.add_node(workflow_id, node_id, node_type, name, config)
        except Exception as e:
            print(f"❌ Error: {e}")
    
    def _connect_nodes(self):
        """Connect nodes in workflow"""
        if not self.builder.workflows:
            print("📭 No workflows available")
            return
        
        self.builder.list_workflows()
        workflow_id = input("\n🆔 Enter workflow ID: ").strip()
        from_node = input("🔗 Enter from node ID: ").strip()
        to_node = input("🔗 Enter to node ID: ").strip()
        
        try:
            self.builder.connect_nodes(workflow_id, from_node, to_node)
        except Exception as e:
            print(f"❌ Error: {e}")
    
    def _export_workflow(self):
        """Export workflow"""
        if not self.builder.workflows:
            print("📭 No workflows to export")
            return
        
        self.builder.list_workflows()
        workflow_id = input("\n🆔 Enter workflow ID: ").strip()
        filename = input("📁 Enter filename (optional): ").strip() or None
        
        try:
            self.builder.export_workflow(workflow_id, filename)
        except Exception as e:
            print(f"❌ Error: {e}")
    
    def _import_workflow(self):
        """Import workflow"""
        filename = input("📁 Enter filename: ").strip()
        
        try:
            workflow_id = self.builder.import_workflow(filename)
            print(f"✅ Workflow imported with ID: {workflow_id}")
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    # Run the interactive builder
    builder = InteractiveWorkflowBuilder()
    builder.run()
