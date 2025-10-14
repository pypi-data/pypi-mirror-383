"""
Mermaid diagram renderer for workflow sequences.
Provides clean separation of diagram generation logic from core sequence functionality.
"""

import re
from typing import Dict, Set, Tuple, Any, List
from egregore.core.workflow.base_node import BaseNode, Decision, NodeType


class MermaidRenderer:
    """Renders workflow sequences as Mermaid diagrams"""
    
    def __init__(self):
        self.node_ids: Dict[BaseNode, str] = {}
        self.visited = set()
        
    def render(self, sequence: 'Sequence', mode: str = "overview") -> str:
        """Generate a Mermaid diagram of the workflow pipeline using JSON serialization
        
        Args:
            sequence: The sequence to render
            mode: "overview" for high-level view, "full" for detailed expansion
        """
        if not sequence.start:
            return "```mermaid\ngraph TD\n    EmptySequence[\"Empty Sequence\"]\n```"
        
        # Use the existing JSON serialization which already handles all the traversal correctly
        json_data = sequence.to_json()
        
        return self._render_from_json(json_data, mode=mode)
    
    def _render_from_json(self, json_data: Dict, mode: str = "overview") -> str:
        """Render Mermaid diagram from JSON workflow representation
        
        Args:
            json_data: The JSON representation of the workflow
            mode: "overview" for high-level view, "full" for detailed expansion
        """
        mermaid = ["```mermaid", "graph TD"]
        
        if mode == "full":
            # Full mode: expand nested sequences and show all internal nodes
            self._render_full_expansion(json_data, mermaid)
        else:
            # Overview mode: high-level view (current behavior) 
            self._render_overview(json_data, mermaid)
        
        mermaid.append("```")
        return "\n".join(mermaid)
    
    def _render_overview(self, json_data: Dict, mermaid: List[str]) -> None:
        """Render overview mode (current behavior)"""
        # Process nodes from JSON
        nodes = json_data.get('nodes', [])
        for node_data in nodes:
            node_id = self._sanitize_json_id(node_data['id'])
            node_name = node_data['name']
            node_type = node_data['type']
            
            # Generate appropriate shape based on type
            shape = self._get_json_node_shape(node_id, node_name, node_type, node_data)
            mermaid.append(f'    {shape}')
            
            # Add styling with alias information
            style = self._get_json_node_style(node_type, node_data)  # Phase 4: Pass node_data for alias styling
            mermaid.append(f'    classDef {node_id}_style {style}')
            mermaid.append(f'    class {node_id} {node_id}_style')
        
        # Process connections from JSON
        connections = json_data.get('connections', [])
        for conn_data in connections:
            from_id = self._sanitize_json_id(conn_data['from'])
            to_id = self._sanitize_json_id(conn_data['to'])
            conn_type = conn_data['type']
            
            if conn_type == 'sequence':
                mermaid.append(f'    {from_id} --> {to_id}')
            elif conn_type == 'parallel':
                mermaid.append(f'    {from_id} -.-> {to_id}')
            elif conn_type == 'decision':
                condition = conn_data.get('condition', '')
                mermaid.append(f'    {from_id} -->|"{condition}"| {to_id}')
    
    def _render_full_expansion(self, json_data: Dict, mermaid: List[str]) -> None:
        """Render full expansion mode showing all nested sequence internals"""
        processed_sequences = set()
        sequence_boundaries = {}  # Maps sequence_id -> (first_node_id, last_node_id)
        id_mapping = {}  # Maps original JSON IDs to readable Mermaid IDs
        
        # First create ID mapping for all nodes
        self._create_id_mapping(json_data, id_mapping)
        
        # First pass: render all nodes, expanding nested sequences
        nodes = json_data.get('nodes', [])
        for node_data in nodes:
            self._render_node_full(node_data, mermaid, processed_sequences, sequence_boundaries, id_mapping)
        
        # Second pass: render all connections, including internal sequence connections
        connections = json_data.get('connections', [])
        rendered_connections = set()  # Track rendered connections to avoid duplicates
        for conn_data in connections:
            self._render_connection_full(conn_data, mermaid, processed_sequences, sequence_boundaries, id_mapping, rendered_connections)
    
    def _render_node_full(self, node_data: Dict, mermaid: List[str], processed_sequences: set, sequence_boundaries: dict, id_mapping: dict) -> None:
        """Render a single node in full expansion mode"""
        original_id = node_data['id']
        node_id = id_mapping.get(original_id, self._sanitize_json_id(original_id))
        node_name = node_data['name']
        node_type = node_data['type']
        
        if node_type == 'sequence' and 'nested_workflow' in node_data:
            # Expand nested sequence
            if node_id not in processed_sequences:
                processed_sequences.add(node_id)
                
                # Add a subgraph for the nested sequence
                mermaid.append(f'    subgraph {node_id}_cluster ["{node_name}"]')
                
                # Recursively render the nested workflow nodes
                nested_workflow = node_data['nested_workflow']
                nested_nodes = nested_workflow.get('nodes', [])
                
                # Find entry and exit points based on connections
                first_node_id, exit_node_ids = self._find_sequence_boundaries(nested_workflow, id_mapping)
                
                for nested_node_data in nested_nodes:
                    nested_original_id = nested_node_data['id']
                    nested_node_id = id_mapping.get(nested_original_id, self._sanitize_json_id(nested_original_id))
                    nested_node_name = nested_node_data['name']
                    nested_node_type = nested_node_data['type']
                    
                    # Render nested node
                    shape = self._get_json_node_shape(nested_node_id, nested_node_name, nested_node_type, nested_node_data)
                    mermaid.append(f'        {shape}')
                    
                    # Add styling
                    style = self._get_json_node_style(nested_node_type, nested_node_data)
                    mermaid.append(f'        classDef {nested_node_id}_style {style}')
                    mermaid.append(f'        class {nested_node_id} {nested_node_id}_style')
                
                # Store boundary information
                sequence_boundaries[node_id] = (first_node_id, exit_node_ids)
                
                # Add internal connections for nested sequence
                nested_connections = nested_workflow.get('connections', [])
                nested_rendered_connections = set()  # Track nested connections separately
                for nested_conn_data in nested_connections:
                    nested_from_original = nested_conn_data['from']
                    nested_to_original = nested_conn_data['to']
                    nested_from_id = id_mapping.get(nested_from_original, self._sanitize_json_id(nested_from_original))
                    nested_to_id = id_mapping.get(nested_to_original, self._sanitize_json_id(nested_to_original))
                    nested_conn_type = nested_conn_data['type']
                    
                    nested_connection_key = (nested_from_id, nested_to_id, nested_conn_type)
                    if nested_connection_key not in nested_rendered_connections:
                        if nested_conn_type == 'sequence':
                            mermaid.append(f'        {nested_from_id} --> {nested_to_id}')
                        elif nested_conn_type == 'parallel':
                            mermaid.append(f'        {nested_from_id} -.-> {nested_to_id}')
                        nested_rendered_connections.add(nested_connection_key)
                
                mermaid.append('    end')
        
        elif node_type == 'parallel' and 'children' in node_data:
            # Render parallel node and its children
            shape = self._get_json_node_shape(node_id, node_name, node_type, node_data)
            mermaid.append(f'    {shape}')
            
            # Add styling
            style = self._get_json_node_style(node_type, node_data)
            mermaid.append(f'    classDef {node_id}_style {style}')
            mermaid.append(f'    class {node_id} {node_id}_style')
            
            # Render parallel children as individual nodes
            for child_data in node_data['children']:
                child_original_id = child_data['id']
                child_id = id_mapping.get(child_original_id, self._sanitize_json_id(child_original_id))
                child_name = child_data['name']
                child_type = child_data['type']
                
                child_shape = self._get_json_node_shape(child_id, child_name, child_type, child_data)
                mermaid.append(f'    {child_shape}')
                
                child_style = self._get_json_node_style(child_type, child_data)
                mermaid.append(f'    classDef {child_id}_style {child_style}')
                mermaid.append(f'    class {child_id} {child_id}_style')
                
                # Add parallel connections
                mermaid.append(f'    {node_id} -.-> {child_id}')
        
        else:
            # Regular node
            shape = self._get_json_node_shape(node_id, node_name, node_type, node_data)
            mermaid.append(f'    {shape}')
            
            # Add styling
            style = self._get_json_node_style(node_type, node_data)
            mermaid.append(f'    classDef {node_id}_style {style}')
            mermaid.append(f'    class {node_id} {node_id}_style')
    
    def _render_connection_full(self, conn_data: Dict, mermaid: List[str], processed_sequences: set, sequence_boundaries: dict, id_mapping: dict, rendered_connections: set) -> None:
        """Render connections in full expansion mode"""
        from_original = conn_data['from']
        to_original = conn_data['to']
        from_id = id_mapping.get(from_original, self._sanitize_json_id(from_original))
        to_id = id_mapping.get(to_original, self._sanitize_json_id(to_original))
        conn_type = conn_data['type']
        
        # Skip parallel connections as they're handled in _render_node_full
        if conn_type == 'parallel':
            return
        
        # Handle sequence connections with boundary resolution
        if conn_type == 'sequence':
            # Check if from/to are sequences that were expanded
            from_node_ids = [from_id]
            to_node_id = to_id
            
            # If from is a sequence, use its exit nodes (could be multiple for parallel)
            if from_id in sequence_boundaries:
                _, exit_node_ids = sequence_boundaries[from_id]
                from_node_ids = exit_node_ids
            
            # If to is a sequence, use its first node
            if to_id in sequence_boundaries:
                to_node_id, _ = sequence_boundaries[to_id]
            
            # Create connections from all exit nodes to the target
            for actual_from_id in from_node_ids:
                if actual_from_id and to_node_id:
                    connection_key = (actual_from_id, to_node_id, 'sequence')
                    if connection_key not in rendered_connections:
                        mermaid.append(f'    {actual_from_id} --> {to_node_id}')
                        rendered_connections.add(connection_key)
                
        elif conn_type == 'decision':
            condition = conn_data.get('condition', '')
            # Apply same boundary resolution for decision connections
            from_node_ids = [from_id]
            to_node_id = to_id
            
            if from_id in sequence_boundaries:
                _, exit_node_ids = sequence_boundaries[from_id]
                from_node_ids = exit_node_ids
            
            if to_id in sequence_boundaries:
                to_node_id, _ = sequence_boundaries[to_id]
            
            # Create decision connections from all exit nodes to the target
            for actual_from_id in from_node_ids:
                if actual_from_id and to_node_id:
                    connection_key = (actual_from_id, to_node_id, f'decision_{condition}')
                    if connection_key not in rendered_connections:
                        mermaid.append(f'    {actual_from_id} -->|"{condition}"| {to_node_id}')
                        rendered_connections.add(connection_key)
    
    def _find_sequence_boundaries(self, nested_workflow: Dict, id_mapping: dict) -> Tuple[str, list]:
        """Find the entry and exit nodes of a sequence workflow
        
        Returns:
            Tuple of (first_node_id, exit_node_ids)
            where exit_node_ids is a list because parallel nodes have multiple exits
        """
        nodes = nested_workflow.get('nodes', [])
        connections = nested_workflow.get('connections', [])
        
        if not nodes:
            return None, []
        
        # If only one node, it's both first and last
        if len(nodes) == 1:
            original_id = nodes[0]['id']
            node_id = id_mapping.get(original_id, self._sanitize_json_id(original_id))
            return node_id, [node_id]
        
        # Find nodes that are not targets of any connection (entry points)
        all_original_ids = {node['id'] for node in nodes}
        target_original_ids = {conn['to'] for conn in connections}
        source_original_ids = {conn['from'] for conn in connections}
        
        # Entry nodes have no incoming connections
        entry_original_ids = all_original_ids - target_original_ids
        first_original_id = next(iter(entry_original_ids)) if entry_original_ids else nodes[0]['id']
        first_node_id = id_mapping.get(first_original_id, self._sanitize_json_id(first_original_id))
        
        # For exit nodes, we need to handle parallel nodes specially
        exit_node_ids = []
        
        # Check each node to see if it's an exit point
        for node_data in nodes:
            node_original_id = node_data['id']
            node_type = node_data.get('type', '')
            
            if node_type == 'parallel' and 'children' in node_data:
                # For parallel nodes, the exit points are the children, not the parallel node itself
                for child_data in node_data['children']:
                    child_original_id = child_data['id']
                    child_id = id_mapping.get(child_original_id, self._sanitize_json_id(child_original_id))
                    exit_node_ids.append(child_id)
            elif node_original_id not in source_original_ids:
                # Regular exit node (has no outgoing connections)
                node_id = id_mapping.get(node_original_id, self._sanitize_json_id(node_original_id))
                exit_node_ids.append(node_id)
        
        # If no exit nodes found, use the last node
        if not exit_node_ids:
            last_original_id = nodes[-1]['id']
            last_node_id = id_mapping.get(last_original_id, self._sanitize_json_id(last_original_id))
            exit_node_ids.append(last_node_id)
        
        return first_node_id, exit_node_ids
    
    def _create_id_mapping(self, json_data: Dict, id_mapping: dict) -> None:
        """Create mapping from JSON IDs to readable Mermaid IDs"""
        nodes = json_data.get('nodes', [])
        for node_data in nodes:
            original_id = node_data['id']
            readable_id = self._create_mermaid_id(node_data)
            id_mapping[original_id] = readable_id
            
            # Recursively map nested nodes
            if node_data.get('type') == 'sequence' and 'nested_workflow' in node_data:
                self._create_id_mapping(node_data['nested_workflow'], id_mapping)
            elif node_data.get('type') == 'parallel' and 'children' in node_data:
                for child_data in node_data['children']:
                    child_id = child_data['id']
                    child_readable_id = self._create_mermaid_id(child_data)
                    id_mapping[child_id] = child_readable_id
    
    def _create_mermaid_id(self, node_data: Dict) -> str:
        """Create a readable Mermaid ID from node data, preferring names over IDs"""
        node_name = node_data.get('name', '')
        node_id = node_data.get('id', '')
        node_type = node_data.get('type', '')
        
        # Prefer name if available and meaningful
        if node_name and not node_name.startswith('node_') and not node_name.startswith('parallel_'):
            base_name = node_name
        elif node_type == 'parallel':
            # For parallel nodes, use a generic readable name
            base_name = 'parallel_execution'
        else:
            base_name = node_id
            
        # Sanitize for Mermaid compatibility
        import re
        sanitized = re.sub(r'[^a-zA-Z0-9_]', '_', base_name)
        if re.match(r'^[0-9]+', sanitized):
            sanitized = f'N_{sanitized}'
        return sanitized
    
    def _sanitize_json_id(self, json_id: str) -> str:
        """Sanitize JSON node ID for Mermaid compatibility (legacy)"""
        import re
        # Replace any non-alphanumeric characters with underscores
        sanitized = re.sub(r'[^a-zA-Z0-9_]', '_', json_id)
        if re.match(r'^[0-9]+', sanitized):
            sanitized = f'N_{sanitized}'
        return sanitized
    
    def _get_json_node_shape(self, node_id: str, node_name: str, node_type: str, node_data: Dict) -> str:
        """Get Mermaid shape based on JSON node type with Phase 4 alias visualization"""
        # Phase 4: Enhanced display name with alias information
        display_name = node_name
        if node_type == 'parallel' and node_id == 'parallel_execution':
            display_name = 'parallel_execution'
        
        # Phase 4: Add alias information to display name for better visualization
        effective_name = node_data.get('effective_name', node_name)
        alias = node_data.get('alias')
        canonical_name = node_data.get('canonical_name', node_name)
        
        if alias:
            # For aliased nodes, show: "alias (canonical_name)"
            display_name = f"{effective_name} ({canonical_name})"
        else:
            # For original nodes, just use the name
            display_name = effective_name
        
        if node_type == 'sequence':
            return f'{node_id}[["🔄 {display_name}"]]'
        elif node_type == 'parallel':
            return f'{node_id}{{{{"⚡ {display_name}"}}}}'
        elif node_type == 'decision':
            return f'{node_id}{{{{"❓ {display_name}"}}}}'
        elif node_type == 'agent':
            return f'{node_id}["🤖 {display_name}"]'
        else:
            return f'{node_id}["📋 {display_name}"]'
    
    def _get_json_node_style(self, node_type: str, node_data: Dict = None) -> str:
        """Get Mermaid styling based on JSON node type with Phase 4 alias styling"""
        base_style = ""
        
        if node_type == 'sequence':
            base_style = "fill:#e1f5fe,stroke:#01579b,stroke-width:2px"
        elif node_type == 'parallel':
            base_style = "fill:#f3e5f5,stroke:#4a148c,stroke-width:2px"
        elif node_type == 'decision':
            base_style = "fill:#fff3e0,stroke:#e65100,stroke-width:2px"
        elif node_type == 'agent':
            base_style = "fill:#e8f5e8,stroke:#1b5e20,stroke-width:2px"
        else:
            base_style = "fill:#f5f5f5,stroke:#424242,stroke-width:1px"
        
        # Phase 4: Add special styling for aliased nodes
        if node_data and node_data.get('alias'):
            # Make aliased nodes have a dashed border to distinguish them
            base_style = base_style.replace("stroke-width:2px", "stroke-width:2px,stroke-dasharray: 5 5")
            base_style = base_style.replace("stroke-width:1px", "stroke-width:2px,stroke-dasharray: 5 5")
        
        return base_style
    
    def _sanitize_mermaid_id(self, node: BaseNode) -> str:
        """Create a clean Mermaid-compatible ID for a node"""
        name_part = getattr(node, 'name', str(node))
        # Enhanced sanitization for better readability
        name_part = re.sub(r'[^a-zA-Z0-9_]', '_', name_part)
        if re.match(r'^[0-9]+$', name_part):
            name_part = f'N_{name_part}'
        return f"{name_part}_{id(node) % 10000}"  # Shorter IDs
    
    def _get_node_style(self, node: BaseNode) -> str:
        """Get Mermaid styling based on node type"""
        # Import here to avoid circular imports
        from egregore.core.workflow.sequence.base import Sequence
        
        if isinstance(node, Sequence):
            return "fill:#e1f5fe,stroke:#01579b,stroke-width:2px"
        elif hasattr(node, 'parallel_nodes'):  # ParallelNode
            return "fill:#f3e5f5,stroke:#4a148c,stroke-width:2px"
        elif isinstance(node, Decision):
            return "fill:#fff3e0,stroke:#e65100,stroke-width:2px"
        elif hasattr(node, 'agent'):  # AgentNode
            return "fill:#e8f5e8,stroke:#1b5e20,stroke-width:2px"
        else:
            return "fill:#f5f5f5,stroke:#424242,stroke-width:1px"
    
    def _collect_all_nodes(self, node: BaseNode) -> None:
        """First pass: Collect all nodes and assign IDs without generating output"""
        if not node or id(node) in self.visited:
            return
        self.visited.add(id(node))
        
        # Assign ID to this node
        node_id = self._sanitize_mermaid_id(node)
        self.node_ids[node] = node_id
        print(f"DEBUG: Collected node {node} -> ID {node_id}")
        
        # Recursively collect all connected nodes
        # Sequential connections
        if hasattr(node, 'next_node') and node.next_node:
            self._collect_all_nodes(node.next_node)
        
        # Parallel node children
        if hasattr(node, 'parallel_nodes'):
            for child in node.parallel_nodes:
                self._collect_all_nodes(child)
        
        # Decision node branches
        if isinstance(node, Decision):
            for map_item in node.maps:
                target_node = map_item.node
                if isinstance(target_node, NodeType):
                    target_node = target_node.node_instance
                self._collect_all_nodes(target_node)
        
        # Nested sequences
        from egregore.core.workflow.sequence.base import Sequence
        if isinstance(node, Sequence) and node.start:
            self._collect_all_nodes(node.start)
    
    def _generate_node_definitions(self) -> List[str]:
        """Generate Mermaid node definition lines for all collected nodes"""
        node_lines = []
        
        for node, node_id in self.node_ids.items():
            node_name = getattr(node, 'name', str(node))
            
            # Get appropriate shape for node type
            shape = self._get_node_shape(node, node_id, node_name)
            node_lines.append(f'    {shape}')
            
            # Add styling
            style = self._get_node_style(node)
            node_lines.append(f'    classDef {node_id}_style {style}')
            node_lines.append(f'    class {node_id} {node_id}_style')
        
        return node_lines

    def _get_node_shape(self, node: BaseNode, node_id: str, node_name: str) -> str:
        """Get the appropriate Mermaid shape for different node types"""
        # Import here to avoid circular imports
        from egregore.core.workflow.sequence.base import Sequence
        
        if isinstance(node, Sequence):
            return f'{node_id}[["🔄 {node_name}"]]'
        elif hasattr(node, 'parallel_nodes'):  # ParallelNode
            return f'{node_id}{{{{"⚡ {node_name}"}}}}'
        elif isinstance(node, Decision):
            return f'{node_id}{{{{"❓ {node_name}"}}}}'
        elif hasattr(node, 'agent'):  # AgentNode
            return f'{node_id}["🤖 {node_name}"]'
        else:
            return f'{node_id}["📋 {node_name}"]'
    
    def _traverse_and_collect(self, node: BaseNode, depth: int = 0) -> List[str]:
        """Recursively traverse and collect all nodes"""
        mermaid_lines = []
        
        if not node or id(node) in self.visited:
            return mermaid_lines
        self.visited.add(id(node))
        
        node_id = self._sanitize_mermaid_id(node)
        self.node_ids[node] = node_id
        node_name = getattr(node, 'name', str(node))
        
        # Get appropriate shape for node type
        shape = self._get_node_shape(node, node_id, node_name)
        mermaid_lines.append(f'    {shape}')
        
        # Add styling
        style = self._get_node_style(node)
        mermaid_lines.append(f'    classDef {node_id}_style {style}')
        mermaid_lines.append(f'    class {node_id} {node_id}_style')
        
        # Handle different node types
        parallel_lines = self._handle_parallel_nodes(node, depth)
        mermaid_lines.extend(parallel_lines)
        
        decision_lines = self._handle_decision_nodes(node, depth)
        mermaid_lines.extend(decision_lines)
        
        nested_lines = self._handle_nested_sequences(node, depth) 
        mermaid_lines.extend(nested_lines)
        
        # Continue with next node
        if hasattr(node, 'next_node') and node.next_node:
            child_lines = self._traverse_and_collect(node.next_node, depth)
            mermaid_lines.extend(child_lines)
        
        return mermaid_lines
    
    def _handle_parallel_nodes(self, node: BaseNode, depth: int) -> List[str]:
        """Handle parallel node children"""
        lines = []
        if hasattr(node, 'parallel_nodes'):
            for child in node.parallel_nodes:
                child_lines = self._traverse_and_collect(child, depth + 1)
                lines.extend(child_lines)
        return lines
    
    def _handle_decision_nodes(self, node: BaseNode, depth: int) -> List[str]:
        """Handle decision node branches"""
        lines = []
        if isinstance(node, Decision):
            for map_item in node.maps:
                target_node = map_item.node
                if isinstance(target_node, NodeType):
                    target_node = target_node.node_instance
                child_lines = self._traverse_and_collect(target_node, depth + 1)
                lines.extend(child_lines)
        return lines
    
    def _handle_nested_sequences(self, node: BaseNode, depth: int) -> List[str]:
        """Handle nested sequence traversal"""
        # Import here to avoid circular imports
        from egregore.core.workflow.sequence.base import Sequence
        
        lines = []
        if isinstance(node, Sequence) and node.start:
            child_lines = self._traverse_and_collect(node.start, depth + 1)
            lines.extend(child_lines)
        return lines
    
    def _add_connections(self, mermaid: List[str]) -> None:
        """Add connections between nodes based on collected nodes"""
        connections_added = set()
        
        # Create connections for all collected nodes
        for node in list(self.node_ids.keys()):
            node_id = self.node_ids[node]
            
            self._add_sequential_connections(node, node_id, connections_added, mermaid)
            self._add_parallel_connections(node, node_id, connections_added, mermaid)
            self._add_decision_connections(node, node_id, connections_added, mermaid)
            self._add_nested_sequence_connections(node, node_id, connections_added, mermaid)
    
    def _add_sequential_connections(self, node: BaseNode, node_id: str, 
                                  connections_added: Set[Tuple], mermaid: List[str]) -> None:
        """Add sequential node connections"""
        print(f"DEBUG: Checking sequential connections for {node_id} ({node})")
        print(f"  - has_next_node: {hasattr(node, 'next_node')}")
        if hasattr(node, 'next_node'):
            print(f"  - next_node: {node.next_node}")
            print(f"  - next_node_exists: {node.next_node is not None}")
            if node.next_node:
                print(f"  - next_node_id_in_dict: {id(node.next_node) in self.node_ids}")
                
        if hasattr(node, 'next_node') and node.next_node and id(node.next_node) in self.node_ids:
            next_id = self.node_ids[node.next_node]
            conn_key = (node_id, next_id)
            if conn_key not in connections_added:
                connection_line = f'    {node_id} --> {next_id}'
                mermaid.append(connection_line)
                connections_added.add(conn_key)
                print(f"DEBUG: Added sequential connection: {connection_line}")
            else:
                print(f"DEBUG: Connection already exists: {conn_key}")
        else:
            print(f"DEBUG: No sequential connection for {node_id}")
    
    def _add_parallel_connections(self, node: BaseNode, node_id: str,
                                connections_added: Set[Tuple], mermaid: List[str]) -> None:
        """Add parallel node connections"""
        if hasattr(node, 'parallel_nodes'):
            for child in node.parallel_nodes:
                if id(child) in self.node_ids:
                    child_id = self.node_ids[child]
                    # Parallel fork
                    fork_key = (node_id, child_id)
                    if fork_key not in connections_added:
                        mermaid.append(f'    {node_id} -.-> {child_id}')
                        connections_added.add(fork_key)
                    # Parallel join back (optional - can be removed for cleaner diagrams)
                    # join_key = (child_id, node_id)
                    # if join_key not in connections_added:
                    #     mermaid.append(f'    {child_id} -.-> {node_id}')
                    #     connections_added.add(join_key)
    
    def _add_decision_connections(self, node: BaseNode, node_id: str,
                                connections_added: Set[Tuple], mermaid: List[str]) -> None:
        """Add decision node connections"""
        if isinstance(node, Decision):
            for map_item in node.maps:
                target_node = map_item.node
                if isinstance(target_node, NodeType):
                    target_node = target_node.node_instance
                if id(target_node) in self.node_ids:
                    target_id = self.node_ids[target_node]
                    condition = str(map_item.condition)
                    decision_key = (node_id, target_id, condition)
                    if decision_key not in connections_added:
                        mermaid.append(f'    {node_id} -->|"{condition}"| {target_id}')
                        connections_added.add(decision_key)
    
    def _add_nested_sequence_connections(self, node: BaseNode, node_id: str,
                                       connections_added: Set[Tuple], mermaid: List[str]) -> None:
        """Add nested sequence connections"""
        # Import here to avoid circular imports
        from egregore.core.workflow.sequence.base import Sequence
        
        if isinstance(node, Sequence) and node.start and id(node.start) in self.node_ids:
            start_id = self.node_ids[node.start]
            nested_key = (node_id, start_id)
            if nested_key not in connections_added:
                mermaid.append(f'    {node_id} --> {start_id}')
                connections_added.add(nested_key)


def render_mermaid_schema(sequence: 'Sequence', mode: str = "overview") -> str:
    """Convenience function to render a sequence as Mermaid diagram
    
    Args:
        sequence: The sequence to render
        mode: "overview" for high-level view, "full" for detailed expansion
    """
    renderer = MermaidRenderer()
    return renderer.render(sequence, mode=mode)


# Legacy compatibility function
def sequence_to_mermaid(sequence: 'Sequence') -> str:
    """Legacy function for backward compatibility"""
    return render_mermaid_schema(sequence)