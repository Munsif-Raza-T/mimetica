import json
import numpy as np
import pandas as pd
import requests
from typing import Dict, List, Any, Optional, Type
import streamlit as st
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import plotly.express as px
try:
    import seaborn as sns 
except Exception:
    sns = None
import matplotlib as mpl  
from utils.vector_store import VectorStore
from config import config

# CrewAI imports
from crewai.tools import BaseTool, tool
from pydantic import BaseModel, Field

# ADD THESE NEW IMPORTS FOR CODE INTERPRETER
import sys
import io
import traceback
import ast
import base64


# =============================================================================
# SESSION FILE READER TOOL
# =============================================================================

class SessionDirectoryReadTool(BaseTool):
    """Tool for reading files uploaded in the current Streamlit session"""
    
    name: str = "session_directory_reader"
    description: str = "Read files that have been uploaded in the current Streamlit session"
    
    def _run(self) -> str:
        try:
            # Get the documents from the session state
            import streamlit as st
            
            if 'workflow_state' not in st.session_state or 'documents' not in st.session_state.workflow_state:
                return "No documents found in the current session."
                
            documents = st.session_state.workflow_state.get('documents', [])
            if not documents:
                return "No documents have been uploaded in the current session."
            
            # Create a summary of the uploaded documents
            summary = "Uploaded Documents in Current Session:\n\n"
            for doc in documents:
                filename = doc.get('filename', 'Unknown')
                file_type = doc.get('file_type', 'Unknown')
                content_preview = doc.get('content', '')[:200] + '...' if len(doc.get('content', '')) > 200 else doc.get('content', '')
                file_size = doc.get('file_size', 0)
                
                summary += f"""
Document: {filename}
Type: {file_type}
Size: {file_size} bytes
Preview: {content_preview}
-------------------
"""
            
            return summary
            
        except Exception as e:
            return f"Error reading session documents: {str(e)}"


class SessionFileReadTool(BaseTool):
    """Tool for reading a specific file from the current Streamlit session"""
    
    name: str = "session_file_reader"
    description: str = "Read a specific file that has been uploaded in the current Streamlit session"
    
    def _run(self, filename: str) -> str:
        try:
            import streamlit as st
            
            if 'workflow_state' not in st.session_state or 'documents' not in st.session_state.workflow_state:
                return f"No documents found in the current session."
            
            documents = st.session_state.workflow_state.get('documents', [])
            if not documents:
                return f"No documents have been uploaded in the current session."
            
            # Find the requested document
            for doc in documents:
                if doc.get('filename', '') == filename:
                    return doc.get('content', f"No content found in {filename}")
            
            return f"File {filename} not found in the current session."
            
        except Exception as e:
            return f"Error reading file {filename}: {str(e)}"


# =============================================================================
# CODE INTERPRETER TOOL - ADD THIS ENTIRE SECTION
# =============================================================================

class CodeInterpreterToolInput(BaseModel):
    """Input schema for CodeInterpreterTool"""
    code: str = Field(..., description="Python code to execute")
    timeout: int = Field(default=30, description="Execution timeout in seconds")

class CodeInterpreterTool(BaseTool):
    """Custom Code Interpreter Tool for executing Python code safely within CrewAI agents"""
    
    name: str = "code_interpreter"
    description: str = "Execute Python code and return results. Supports data analysis, visualization, calculations, and general Python operations. Returns both output and any generated plots."
    args_schema: Type[BaseModel] = CodeInterpreterToolInput
    
    # Define allowed modules as strings to avoid pickle issues
    _allowed_module_names: List[str] = ["pandas", "numpy", "matplotlib", "matplotlib.pyplot", "seaborn",
    "plotly", "plotly.graph_objects", "plotly.express", "datetime", "json", "math", "statistics", "random",
    ]
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
    
    def _get_allowed_modules(self) -> Dict[str, Any]:
        """Get allowed modules dynamically to avoid pickle issues and missing refs."""
        allowed = {
            'pandas': pd,
            'numpy': np,
            'matplotlib': mpl,   
            'matplotlib.pyplot': plt,   
            'plt': plt,              
            'go': go,
            'px': px,
            'datetime': datetime,
            'timedelta': timedelta,
            'json': json,
            'math': __import__('math'),
            'statistics': __import__('statistics'),
            'random': __import__('random'),
        }
        # Agrega seaborn solo si está disponible
        if sns is not None:
            allowed['seaborn'] = sns
        return allowed

    
    def _create_safe_globals(self) -> Dict[str, Any]:
        """Create a safe global namespace for code execution"""
        safe_globals = {
            '__builtins__': {
                # Safe built-in functions
                'abs': abs, 'all': all, 'any': any, 'bin': bin, 'bool': bool,
                'chr': chr, 'dict': dict, 'dir': dir, 'divmod': divmod,
                'enumerate': enumerate, 'filter': filter, 'float': float,
                'format': format, 'frozenset': frozenset, 'hex': hex,
                'int': int, 'isinstance': isinstance, 'issubclass': issubclass,
                'iter': iter, 'len': len, 'list': list, 'map': map,
                'max': max, 'min': min, 'next': next, 'oct': oct,
                'ord': ord, 'pow': pow, 'print': print, 'range': range,
                'reversed': reversed, 'round': round, 'set': set,
                'slice': slice, 'sorted': sorted, 'str': str, 'sum': sum,
                'tuple': tuple, 'type': type, 'zip': zip,
                # Safe exceptions
                'ValueError': ValueError, 'TypeError': TypeError,
                'KeyError': KeyError, 'IndexError': IndexError,
                'Exception': Exception,
            }
        }
        
        # Add allowed modules to globals dynamically
        safe_globals.update(self._get_allowed_modules())
        
        return safe_globals
    
    def _is_safe_code(self, code: str) -> tuple[bool, str]:
        """Check if the code is safe to execute"""
        try:
            tree = ast.parse(code)
        except SyntaxError as e:
            return False, f"Syntax error: {str(e)}"
        
        # List of potentially dangerous operations
        dangerous_operations = [
            ast.Import,  # We'll handle imports manually
            ast.ImportFrom,  # We'll handle imports manually
        ]
        
        dangerous_names = [
            'exec', 'eval', 'compile', '__import__', 'open', 'file',
            'input', 'raw_input', 'reload', 'exit', 'quit',
            'subprocess', 'os.system', 'os.popen', 'os.spawn',
        ]
        
        for node in ast.walk(tree):
            # Check for dangerous operations
            if any(isinstance(node, dangerous_op) for dangerous_op in dangerous_operations):
                if isinstance(node, (ast.Import, ast.ImportFrom)):
                    # Allow imports of safe modules only
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            if alias.name not in self._allowed_module_names:
                                return False, f"Import of '{alias.name}' is not allowed"
                    elif isinstance(node, ast.ImportFrom):
                        if node.module and node.module not in self._allowed_module_names:
                            return False, f"Import from '{node.module}' is not allowed"
                        continue
                else:
                    return False, f"Operation {type(node).__name__} is not allowed"
            
            # Check for dangerous function calls
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name) and node.func.id in dangerous_names:
                    return False, f"Function '{node.func.id}' is not allowed"
                elif isinstance(node.func, ast.Attribute):
                    func_name = f"{ast.unparse(node.func)}" if hasattr(ast, 'unparse') else str(node.func.attr)
                    if any(dangerous in func_name for dangerous in dangerous_names):
                        return False, f"Function '{func_name}' is not allowed"
        
        return True, "Code is safe"
    
    def _capture_plots(self) -> List[str]:
        """Capture any matplotlib plots as base64 encoded images"""
        plots = []
        
        # Check if there are any matplotlib figures
        if plt.get_fignums():
            for fig_num in plt.get_fignums():
                fig = plt.figure(fig_num)
                
                # Save plot to bytes
                img_buffer = io.BytesIO()
                fig.savefig(img_buffer, format='png', bbox_inches='tight', dpi=150)
                img_buffer.seek(0)
                
                # Encode as base64
                img_base64 = base64.b64encode(img_buffer.getvalue()).decode()
                plots.append(f"data:image/png;base64,{img_base64}")
                
                img_buffer.close()
            
            # Clear all figures to prevent memory leaks
            plt.close('all')
        
        return plots
    
    def _execute_code(self, code: str) -> Dict[str, Any]:
        """Execute the code safely and return results"""
        # Redirect stdout to capture print statements
        old_stdout = sys.stdout
        old_stderr = sys.stderr
        stdout_buffer = io.StringIO()
        stderr_buffer = io.StringIO()
        
        result = {
            'success': False,
            'output': '',
            'error': '',
            'plots': [],
            'variables': {}
        }
        
        try:
            # Redirect output streams
            sys.stdout = stdout_buffer
            sys.stderr = stderr_buffer
            
            # Create a copy of globals for this execution
            execution_globals = self._create_safe_globals()
            execution_locals = {}
            
            # Execute the code
            exec(code, execution_globals, execution_locals)
            
            # Capture output
            result['output'] = stdout_buffer.getvalue()
            result['success'] = True
            
            # Capture any plots
            result['plots'] = self._capture_plots()
            
            # Capture important variables (avoid internal Python variables)
            important_vars = {}
            for key, value in execution_locals.items():
                if not key.startswith('_'):
                    try:
                        # Try to make it JSON serializable for storage
                        if isinstance(value, (int, float, str, bool, list, dict)):
                            important_vars[key] = value
                        elif isinstance(value, np.ndarray):
                            important_vars[key] = f"NumPy array with shape {value.shape}"
                        elif isinstance(value, pd.DataFrame):
                            important_vars[key] = f"Pandas DataFrame with shape {value.shape}"
                        else:
                            important_vars[key] = str(type(value))
                    except:
                        important_vars[key] = str(type(value))
            
            result['variables'] = important_vars
            
        except Exception as e:
            result['error'] = traceback.format_exc()
            result['output'] = stdout_buffer.getvalue()  # Capture any output before error
            
        finally:
            # Restore stdout/stderr
            sys.stdout = old_stdout
            sys.stderr = old_stderr
            
            # Capture any stderr output
            if stderr_buffer.getvalue():
                result['error'] += stderr_buffer.getvalue()
        
        return result
    
    def _run(self, code: str, timeout: int = 30) -> str:
        """
        Execute Python code and return formatted results
        
        Args:
            code: Python code to execute
            timeout: Execution timeout in seconds (default: 30)
            
        Returns:
            Formatted string containing execution results
        """
        try:
            # Validate code safety
            is_safe, safety_message = self._is_safe_code(code)
            if not is_safe:
                return f"Code execution blocked: {safety_message}"
            
            # Execute the code
            result = self._execute_code(code)
            
            # Format the response
            response_parts = []
            
            # Add execution status
            if result['success']:
                response_parts.append("✅ Code executed successfully!")
            else:
                response_parts.append("❌ Code execution failed!")
            
            # Add output if any
            if result['output'].strip():
                response_parts.append(f"\n📤 Output:\n{result['output'].strip()}")
            
            # Add errors if any
            if result['error'].strip():
                response_parts.append(f"\n🚨 Error:\n{result['error'].strip()}")
            
            # Add information about plots
            if result['plots']:
                response_parts.append(f"\n📊 Generated {len(result['plots'])} plot(s)")
                response_parts.append("Note: Plot visualization data is captured but not displayed in text format")
            
            # Add variable information
            if result['variables']:
                variables_info = []
                for var_name, var_info in result['variables'].items():
                    variables_info.append(f"  • {var_name}: {var_info}")
                
                if variables_info:
                    response_parts.append(f"\n📋 Variables created:\n" + "\n".join(variables_info))
            
            # Add code execution summary
            response_parts.append(f"\n🔧 Executed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            
            return "\n".join(response_parts)
            
        except Exception as e:
            return f"Code interpreter error: {str(e)}"

# ===== DECIDE optional tools (safe stubs) ====================================

class JSONSchemaValidatorTool(BaseTool):
    name: str = "JSONSchemaValidatorTool"
    description: str = "Validates a feasibility JSON against a known schema name."
    def __init__(self, schema_name: str = "feasibility_v1"): self.schema_name = schema_name
    def _run(self, json_text: str = "") -> str:
        try:
            json.loads(json_text or "{}")
            return f"validated:{self.schema_name}:true"
        except Exception as e:
            return f"validated:{self.schema_name}:false; error={e}"

class CriteriaLockerTool(BaseTool):
    name: str = "CriteriaLockerTool"
    description: str = "Checks that criteria are locked and weights sum to 1."
    def _run(self, json_text: str = "") -> str:
        try:
            data = json.loads(json_text or "{}")
            items = (data.get("criteria") or {}).get("items") or []
            total = sum(float(i.get("weight", 0)) for i in items)
            locked = (data.get("criteria") or {}).get("locked", False)
            return f"criteria_locked:{bool(locked)};weights_sum:{total:.4f}"
        except Exception as e:
            return f"criteria_locked:false;weights_sum:error;error={e}"

class RiskRegisterTool(BaseTool):
    name: str = "RiskRegisterTool"
    description: str = "Verifies a risk matrix and basic fields."
    def _run(self, json_text: str = "") -> str:
        try:
            data = json.loads(json_text or "{}")
            risks = data.get("risk_register", [])
            ok = all(set(r).issuperset({"id","desc","prob","impact"}) for r in risks)
            return f"risk_matrix_present:{bool(ok)};count:{len(risks)}"
        except Exception as e:
            return f"risk_matrix_present:false;error={e}"

class MarketSizingTool(BaseTool):
    name: str = "MarketSizingTool"
    description: str = "Assists with TAM/SAM/SOM sanity checks."
    def _run(self, json_text: str = "") -> str:
        try:
            data = json.loads(json_text or "{}")
            mb = data.get("market_block", {})
            td = (mb.get("tam_sam_som") or {}).get("method_topdown") or {}
            bu = (mb.get("tam_sam_som") or {}).get("method_bottomup") or {}
            return f"tam_sam_som_present:{bool(td or bu)}"
        except Exception as e:
            return f"tam_sam_som_present:false;error={e}"

class ElasticityEstimatorTool(BaseTool):
    name: str = "ElasticityEstimatorTool"
    description: str = "Returns placeholder elasticity or suggests test plan."
    def _run(self, input: str = "") -> str:
        return "elasticity_stub:own=-1.2;cross=[];note=placeholder_or_design_test"

class TimeSeriesForecastTool(BaseTool):
    name: str = "TimeSeriesForecastTool"
    description: str = "Returns placeholder O/B/P forecast."
    def _run(self, input: str = "") -> str:
        return "forecast_stub:base=100;optimistic=120;pessimistic=80;horizon_months=12"

class PositioningMapTool(BaseTool):
    name: str = "PositioningMapTool"
    description: str = "Generates a 2D positioning map placeholder."
    def _run(self, input: str = "") -> str:
        return "positioning_map_stub:x=price;y=perceived_value;points=[('You',0.6,0.7)]"

class UnitEconomicsTool(BaseTool):
    name: str = "UnitEconomicsTool"
    description: str = "Computes/validates basic CAC/LTV/payback placeholders."
    def _run(self, input: str = "") -> str:
        return "unit_economics_stub:cac=200;ltv=900;payback_months=4.5"

class MarkdownFormatterTool(BaseTool):
    name: str = "MarkdownFormatterTool"
    description: str = "Pass-through formatter for Markdown."
    def _run(self, md_text: str = "") -> str:
        return md_text or ""

# Function-based version using @tool decorator
@tool("execute_python_code")
def execute_python_code(code: str, timeout: int = 30) -> str:
    """
    Execute Python code safely and return results.
    
    Args:
        code: Python code to execute
        timeout: Execution timeout in seconds (default: 30)
        
    Returns:
        Execution results including output, errors, and generated plots info
    """
    interpreter = CodeInterpreterTool()
    return interpreter._run(code, timeout)


# =============================================================================
# VISUALIZATION GENERATOR TOOL
# =============================================================================

# =============================================================================
# VISUALIZATION GENERATOR TOOL
# =============================================================================

def _generate_strategic_visualization(
    chart_type: str, 
    data_input: str, 
    title: str = "Strategic Analysis Chart",
    save_path: str = None
) -> str:
    """
    INTERNAL: Generate professional visualizations for strategic analysis reports.
    This is the core function that can be called directly or through the CrewAI tool.
    """
    try:
        # Log the call for debugging
        print(f"🎨 VISUALIZATION TOOL CALLED: {chart_type} - {title}")
        
        import json
        import base64
        import matplotlib.pyplot as plt
        import plotly.graph_objects as go
        import plotly.express as px
        import numpy as np
        import pandas as pd
        try:
            import seaborn as sns
        except ImportError:
            sns = None
        from datetime import datetime, timedelta
        import io
        
        # Set style for professional charts
        plt.style.use('default')
        if sns:
            sns.set_palette("husl")
        
        # Parse data input
        try:
            if isinstance(data_input, str):
                data = json.loads(data_input)
            else:
                data = data_input
        except json.JSONDecodeError:
            # If not JSON, treat as simple string and create sample data
            data = {"message": data_input}
        
        # Generate chart based on type
        if chart_type == "risk_matrix":
            return _generate_risk_matrix(data, title, save_path)
        elif chart_type == "roi_projection":
            return _generate_roi_projection(data, title, save_path)
        elif chart_type == "timeline":
            return _generate_timeline_chart(data, title, save_path)
        elif chart_type == "monte_carlo_distribution":
            return _generate_monte_carlo_chart(data, title, save_path)
        elif chart_type == "scenario_comparison":
            return _generate_scenario_comparison(data, title, save_path)
        elif chart_type == "stakeholder_impact":
            return _generate_stakeholder_impact(data, title, save_path)
        elif chart_type == "performance_dashboard":
            return _generate_performance_dashboard(data, title, save_path)
        elif chart_type == "swot_matrix":
            return _generate_swot_matrix(data, title, save_path)
        else:
            return f"Unsupported chart type: {chart_type}. Supported types: risk_matrix, roi_projection, timeline, monte_carlo_distribution, scenario_comparison, stakeholder_impact, performance_dashboard, swot_matrix"
    
    except Exception as e:
        return f"Visualization generation failed: {str(e)}"

@tool("strategic_visualization_generator")
def strategic_visualization_generator(
    chart_type: str, 
    data_input: str, 
    title: str = "Strategic Analysis Chart",
    save_path: str = None
) -> str:
    """
    Generate professional visualizations for strategic analysis reports.

    Args:
        chart_type: One of: risk_matrix, roi_projection, timeline,
                    monte_carlo_distribution, scenario_comparison,
                    stakeholder_impact, performance_dashboard, swot_matrix
        data_input: JSON string or structured data for the chart
        title: Chart title
        save_path: Optional path to also save the PNG (besides session image manager)

    Returns:
        String with generation status and a text placeholder created by image_manager.
    """
    return _generate_strategic_visualization(chart_type, data_input, title, save_path)


def _generate_risk_matrix(data: dict, title: str, save_path: str = None) -> str:
    """Generate a risk assessment matrix"""
    fig, ax = plt.subplots(figsize=(10, 8))
    
    # Sample risk data if not provided
    risks = data.get('risks', [
        {'name': 'Market Risk', 'probability': 0.7, 'impact': 0.8},
        {'name': 'Technical Risk', 'probability': 0.4, 'impact': 0.9},
        {'name': 'Resource Risk', 'probability': 0.6, 'impact': 0.6},
        {'name': 'Regulatory Risk', 'probability': 0.3, 'impact': 0.7},
        {'name': 'Competitive Risk', 'probability': 0.8, 'impact': 0.5}
    ])
    
    # Create scatter plot
    x_vals = [risk['probability'] for risk in risks]
    y_vals = [risk['impact'] for risk in risks]
    labels = [risk['name'] for risk in risks]
    
    # Color code by risk level
    colors = []
    for prob, impact in zip(x_vals, y_vals):
        risk_score = prob * impact
        if risk_score > 0.6:
            colors.append('red')
        elif risk_score > 0.3:
            colors.append('orange')
        else:
            colors.append('green')
    
    scatter = ax.scatter(x_vals, y_vals, c=colors, s=200, alpha=0.7, edgecolors='black')
    
    # Add labels
    for i, label in enumerate(labels):
        ax.annotate(label, (x_vals[i], y_vals[i]), xytext=(5, 5), 
                   textcoords='offset points', fontsize=9, ha='left')
    
    # Customize plot
    ax.set_xlabel('Probability', fontsize=12, fontweight='bold')
    ax.set_ylabel('Impact', fontsize=12, fontweight='bold')
    ax.set_title(title, fontsize=14, fontweight='bold', pad=20)
    ax.grid(True, alpha=0.3)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    
    # Add risk zones
    ax.axhspan(0.7, 1, 0.7, 1, alpha=0.1, color='red', label='High Risk')
    ax.axhspan(0.3, 0.7, 0.3, 1, alpha=0.1, color='orange', label='Medium Risk')
    ax.axhspan(0, 0.3, 0, 0.7, alpha=0.1, color='green', label='Low Risk')
    
    plt.tight_layout()
    
    # Create data hash for caching
    from utils.image_manager import image_manager
    data_hash = image_manager.create_data_hash(data)
    
    return _save_and_encode_chart(fig, save_path, "Risk Matrix chart generated successfully", "risk_matrix", title, data_hash)

def _generate_roi_projection(data: dict, title: str, save_path: str = None) -> str:
    """Generate ROI projection chart"""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
    
    # Sample ROI data if not provided
    periods = data.get('periods', list(range(1, 13)))  # 12 months
    investment = data.get('investment', [-100000] + [0] * 11)  # Initial investment
    returns = data.get('returns', [10000 + i * 2000 for i in range(12)])  # Growing returns
    
    # Calculate cumulative
    cumulative_investment = np.cumsum(investment)
    cumulative_returns = np.cumsum(returns)
    net_cumulative = cumulative_returns + cumulative_investment
    
    # ROI over time
    ax1.plot(periods, cumulative_investment, 'r-', linewidth=2, label='Cumulative Investment')
    ax1.plot(periods, cumulative_returns, 'g-', linewidth=2, label='Cumulative Returns')
    ax1.plot(periods, net_cumulative, 'b-', linewidth=3, label='Net Position')
    ax1.axhline(y=0, color='black', linestyle='--', alpha=0.5)
    ax1.set_xlabel('Months')
    ax1.set_ylabel('Value ($)')
    ax1.set_title('ROI Projection Over Time')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # ROI percentage
    roi_percentages = []
    for i in range(len(periods)):
        if cumulative_investment[i] != 0:
            roi_pct = (net_cumulative[i] / abs(cumulative_investment[i])) * 100
        else:
            roi_pct = 0
        roi_percentages.append(roi_pct)
    
    ax2.bar(periods, roi_percentages, color=['red' if x < 0 else 'green' for x in roi_percentages])
    ax2.axhline(y=0, color='black', linestyle='-', alpha=0.8)
    ax2.set_xlabel('Months')
    ax2.set_ylabel('ROI (%)')
    ax2.set_title('ROI Percentage by Month')
    ax2.grid(True, alpha=0.3)
    
    plt.suptitle(title, fontsize=16, fontweight='bold')
    plt.tight_layout()
    
    # Create data hash for caching
    from utils.image_manager import image_manager
    data_hash = image_manager.create_data_hash(data)
    
    return _save_and_encode_chart(fig, save_path, "ROI projection chart generated successfully", "roi_projection", title, data_hash)

def _generate_timeline_chart(data: dict, title: str, save_path: str = None) -> str:
    """Generate project timeline/Gantt chart"""
    fig, ax = plt.subplots(figsize=(12, 8))
    
    # Sample timeline data if not provided
    tasks = data.get('tasks', [
        {'name': 'Planning Phase', 'start': 0, 'duration': 4},
        {'name': 'Design Phase', 'start': 3, 'duration': 6},
        {'name': 'Development', 'start': 8, 'duration': 12},
        {'name': 'Testing', 'start': 18, 'duration': 4},
        {'name': 'Deployment', 'start': 20, 'duration': 3},
        {'name': 'Monitoring', 'start': 22, 'duration': 8}
    ])
    
    # Create Gantt chart
    colors = plt.cm.Set3(np.linspace(0, 1, len(tasks)))
    
    for i, task in enumerate(tasks):
        ax.barh(i, task['duration'], left=task['start'], 
               color=colors[i], alpha=0.8, height=0.6, 
               edgecolor='black', linewidth=0.5)
        
        # Add task names
        ax.text(task['start'] + task['duration']/2, i, task['name'], 
               ha='center', va='center', fontweight='bold', fontsize=10)
    
    # Customize plot
    ax.set_yticks(range(len(tasks)))
    ax.set_yticklabels([task['name'] for task in tasks])
    ax.set_xlabel('Weeks', fontsize=12, fontweight='bold')
    ax.set_title(title, fontsize=14, fontweight='bold', pad=20)
    ax.grid(True, axis='x', alpha=0.3)
    
    # Add today line if specified
    if 'current_week' in data:
        ax.axvline(x=data['current_week'], color='red', linestyle='--', 
                  linewidth=2, label='Current Week')
        ax.legend()
    
    plt.tight_layout()
    
    # Create data hash for caching
    from utils.image_manager import image_manager
    data_hash = image_manager.create_data_hash(data)
    
    return _save_and_encode_chart(fig, save_path, "Timeline chart generated successfully", "timeline", title, data_hash)

def _generate_monte_carlo_chart(data: dict, title: str, save_path: str = None) -> str:
    """Generate Monte Carlo simulation distribution chart"""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
    
    # Sample Monte Carlo data if not provided
    if 'simulation_results' in data:
        results = data['simulation_results']
    else:
        # Generate sample data
        np.random.seed(42)
        results = np.random.normal(100000, 25000, 10000)  # Sample simulation
    
    # Distribution histogram
    ax1.hist(results, bins=50, alpha=0.7, color='skyblue', edgecolor='black')
    ax1.axvline(np.mean(results), color='red', linestyle='--', linewidth=2, label=f'Mean: ${np.mean(results):,.0f}')
    ax1.axvline(np.percentile(results, 10), color='orange', linestyle='--', linewidth=2, label=f'10th Percentile: ${np.percentile(results, 10):,.0f}')
    ax1.axvline(np.percentile(results, 90), color='green', linestyle='--', linewidth=2, label=f'90th Percentile: ${np.percentile(results, 90):,.0f}')
    ax1.set_xlabel('Outcome Value ($)')
    ax1.set_ylabel('Frequency')
    ax1.set_title('Monte Carlo Simulation - Distribution')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # Cumulative probability
    sorted_results = np.sort(results)
    cumulative_prob = np.arange(1, len(sorted_results) + 1) / len(sorted_results)
    ax2.plot(sorted_results, cumulative_prob, linewidth=2, color='navy')
    ax2.axhline(y=0.5, color='red', linestyle='--', alpha=0.7, label='50% Probability')
    ax2.axhline(y=0.1, color='orange', linestyle='--', alpha=0.7, label='10% Probability')
    ax2.axhline(y=0.9, color='green', linestyle='--', alpha=0.7, label='90% Probability')
    ax2.set_xlabel('Outcome Value ($)')
    ax2.set_ylabel('Cumulative Probability')
    ax2.set_title('Cumulative Probability Distribution')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    plt.suptitle(title, fontsize=16, fontweight='bold')
    plt.tight_layout()
    
    # Create data hash for caching
    from utils.image_manager import image_manager
    data_hash = image_manager.create_data_hash(data)
    
    return _save_and_encode_chart(fig, save_path, "Monte Carlo distribution chart generated successfully", "monte_carlo_distribution", title, data_hash)

def _generate_scenario_comparison(data: dict, title: str, save_path: str = None) -> str:
    """Generate scenario comparison chart"""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
    
    # Sample scenario data if not provided
    scenarios = data.get('scenarios', {
        'Optimistic': {'roi': 150, 'risk': 30, 'timeline': 8},
        'Baseline': {'roi': 100, 'risk': 50, 'timeline': 12},
        'Pessimistic': {'roi': 60, 'risk': 80, 'timeline': 18}
    })
    
    scenario_names = list(scenarios.keys())
    roi_values = [scenarios[name]['roi'] for name in scenario_names]
    risk_values = [scenarios[name]['risk'] for name in scenario_names]
    timeline_values = [scenarios[name]['timeline'] for name in scenario_names]
    
    # ROI comparison
    colors = ['green', 'blue', 'red']
    bars1 = ax1.bar(scenario_names, roi_values, color=colors, alpha=0.7)
    ax1.set_ylabel('ROI (%)')
    ax1.set_title('ROI by Scenario')
    ax1.grid(True, alpha=0.3)
    
    # Add value labels on bars
    for bar, value in zip(bars1, roi_values):
        ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 2, 
                f'{value}%', ha='center', va='bottom', fontweight='bold')
    
    # Risk vs Timeline scatter
    scatter = ax2.scatter(timeline_values, risk_values, s=200, c=colors, alpha=0.7, edgecolors='black')
    for i, name in enumerate(scenario_names):
        ax2.annotate(name, (timeline_values[i], risk_values[i]), 
                    xytext=(5, 5), textcoords='offset points', fontweight='bold')
    
    ax2.set_xlabel('Timeline (months)')
    ax2.set_ylabel('Risk Level (%)')
    ax2.set_title('Risk vs Timeline by Scenario')
    ax2.grid(True, alpha=0.3)
    
    plt.suptitle(title, fontsize=16, fontweight='bold')
    plt.tight_layout()
    
    # Create data hash for caching
    from utils.image_manager import image_manager
    data_hash = image_manager.create_data_hash(data)
    
    return _save_and_encode_chart(fig, save_path, "Scenario comparison chart generated successfully", "scenario_comparison", title, data_hash)

def _generate_stakeholder_impact(data: dict, title: str, save_path: str = None) -> str:
    """Generate stakeholder impact analysis chart"""
    fig, ax = plt.subplots(figsize=(10, 8))
    
    # Sample stakeholder data if not provided
    stakeholders = data.get('stakeholders', [
        {'name': 'Executive Team', 'influence': 0.9, 'interest': 0.8},
        {'name': 'IT Department', 'influence': 0.7, 'interest': 0.9},
        {'name': 'Finance', 'influence': 0.6, 'interest': 0.7},
        {'name': 'End Users', 'influence': 0.3, 'interest': 0.8},
        {'name': 'External Partners', 'influence': 0.5, 'interest': 0.4},
        {'name': 'Regulators', 'influence': 0.8, 'interest': 0.3}
    ])
    
    # Create stakeholder matrix
    x_vals = [s['influence'] for s in stakeholders]
    y_vals = [s['interest'] for s in stakeholders]
    labels = [s['name'] for s in stakeholders]
    
    # Color code by quadrant
    colors = []
    for influence, interest in zip(x_vals, y_vals):
        if influence > 0.5 and interest > 0.5:
            colors.append('red')  # Manage closely
        elif influence > 0.5 and interest <= 0.5:
            colors.append('orange')  # Keep satisfied
        elif influence <= 0.5 and interest > 0.5:
            colors.append('yellow')  # Keep informed
        else:
            colors.append('green')  # Monitor
    
    scatter = ax.scatter(x_vals, y_vals, c=colors, s=200, alpha=0.7, edgecolors='black')
    
    # Add labels
    for i, label in enumerate(labels):
        ax.annotate(label, (x_vals[i], y_vals[i]), xytext=(5, 5), 
                   textcoords='offset points', fontsize=9, ha='left')
    
    # Add quadrant lines
    ax.axhline(y=0.5, color='black', linestyle='-', alpha=0.3)
    ax.axvline(x=0.5, color='black', linestyle='-', alpha=0.3)
    
    # Add quadrant labels
    ax.text(0.75, 0.75, 'Manage\nClosely', ha='center', va='center', 
           bbox=dict(boxstyle='round', facecolor='red', alpha=0.2))
    ax.text(0.75, 0.25, 'Keep\nSatisfied', ha='center', va='center',
           bbox=dict(boxstyle='round', facecolor='orange', alpha=0.2))
    ax.text(0.25, 0.75, 'Keep\nInformed', ha='center', va='center',
           bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.2))
    ax.text(0.25, 0.25, 'Monitor', ha='center', va='center',
           bbox=dict(boxstyle='round', facecolor='green', alpha=0.2))
    
    ax.set_xlabel('Influence', fontsize=12, fontweight='bold')
    ax.set_ylabel('Interest', fontsize=12, fontweight='bold')
    ax.set_title(title, fontsize=14, fontweight='bold', pad=20)
    ax.grid(True, alpha=0.3)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    
    plt.tight_layout()
    
    # Create data hash for caching
    from utils.image_manager import image_manager
    data_hash = image_manager.create_data_hash(data)
    
    return _save_and_encode_chart(fig, save_path, "Stakeholder impact chart generated successfully", "stakeholder_impact", title, data_hash)

def _generate_performance_dashboard(data: dict, title: str, save_path: str = None) -> str:
    """Generate performance dashboard"""
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 12))
    
    # Sample KPI data if not provided
    kpis = data.get('kpis', {
        'revenue': {'current': 85, 'target': 100, 'previous': 70},
        'satisfaction': {'current': 92, 'target': 95, 'previous': 88},
        'efficiency': {'current': 78, 'target': 85, 'previous': 75},
        'innovation': {'current': 65, 'target': 75, 'previous': 60}
    })
    
    # KPI Gauge Charts (simplified as bar charts)
    kpi_names = list(kpis.keys())
    current_values = [kpis[k]['current'] for k in kpi_names]
    target_values = [kpis[k]['target'] for k in kpi_names]
    
    # Current vs Target
    x_pos = np.arange(len(kpi_names))
    ax1.bar(x_pos - 0.2, current_values, 0.4, label='Current', color='skyblue')
    ax1.bar(x_pos + 0.2, target_values, 0.4, label='Target', color='orange')
    ax1.set_ylabel('Score')
    ax1.set_title('Current vs Target Performance')
    ax1.set_xticks(x_pos)
    ax1.set_xticklabels([k.title() for k in kpi_names])
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # Trend chart
    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun']
    revenue_trend = data.get('revenue_trend', [70, 75, 80, 82, 85, 85])
    ax2.plot(months, revenue_trend, 'o-', linewidth=2, markersize=6, color='green')
    ax2.set_ylabel('Revenue Score')
    ax2.set_title('Revenue Trend (6 months)')
    ax2.grid(True, alpha=0.3)
    
    # Progress pie chart
    completed = data.get('project_completion', 65)
    remaining = 100 - completed
    ax3.pie([completed, remaining], labels=['Completed', 'Remaining'], 
           colors=['green', 'lightgray'], autopct='%1.1f%%', startangle=90)
    ax3.set_title('Project Completion')
    
    # Risk heatmap
    risk_categories = ['Technical', 'Financial', 'Market', 'Operational']
    risk_levels = data.get('risk_levels', [3, 2, 4, 2])  # 1-5 scale
    colors_map = plt.cm.RdYlGn_r(np.linspace(0.2, 0.8, 5))
    
    bars4 = ax4.barh(risk_categories, risk_levels, color=[colors_map[level-1] for level in risk_levels])
    ax4.set_xlabel('Risk Level (1-5)')
    ax4.set_title('Risk Assessment by Category')
    ax4.set_xlim(0, 5)
    
    # Add value labels
    for bar, value in zip(bars4, risk_levels):
        ax4.text(bar.get_width() + 0.1, bar.get_y() + bar.get_height()/2, 
                str(value), va='center', fontweight='bold')
    
    plt.suptitle(title, fontsize=16, fontweight='bold')
    plt.tight_layout()
    
    # Create data hash for caching
    from utils.image_manager import image_manager
    data_hash = image_manager.create_data_hash(data)
    
    return _save_and_encode_chart(fig, save_path, "Performance dashboard generated successfully", "performance_dashboard", title, data_hash)

def _generate_swot_matrix(data: dict, title: str, save_path: str = None) -> str:
    """Generate SWOT analysis matrix"""
    fig, ax = plt.subplots(figsize=(12, 10))
    
    # Sample SWOT data if not provided
    swot_data = data.get('swot', {
        'strengths': ['Strong brand', 'Experienced team', 'Good technology'],
        'weaknesses': ['Limited budget', 'Small market share', 'Outdated systems'],
        'opportunities': ['New markets', 'Digital transformation', 'Strategic partnerships'],
        'threats': ['Increased competition', 'Economic uncertainty', 'Regulatory changes']
    })
    
    # Create 2x2 grid
    ax.set_xlim(0, 2)
    ax.set_ylim(0, 2)
    
    # Define quadrants
    quadrants = [
        {'pos': (0, 1, 1, 1), 'color': 'lightgreen', 'title': 'STRENGTHS', 'items': swot_data['strengths']},
        {'pos': (1, 1, 1, 1), 'color': 'lightcoral', 'title': 'WEAKNESSES', 'items': swot_data['weaknesses']},
        {'pos': (0, 0, 1, 1), 'color': 'lightblue', 'title': 'OPPORTUNITIES', 'items': swot_data['opportunities']},
        {'pos': (1, 0, 1, 1), 'color': 'lightyellow', 'title': 'THREATS', 'items': swot_data['threats']}
    ]
    
    # Draw quadrants
    for quad in quadrants:
        x, y, w, h = quad['pos']
        rect = plt.Rectangle((x, y), w, h, facecolor=quad['color'], 
                           edgecolor='black', linewidth=2, alpha=0.7)
        ax.add_patch(rect)
        
        # Add title
        ax.text(x + w/2, y + h - 0.1, quad['title'], ha='center', va='top', 
               fontsize=14, fontweight='bold')
        
        # Add items
        for i, item in enumerate(quad['items'][:5]):  # Max 5 items per quadrant
            ax.text(x + 0.05, y + h - 0.25 - (i * 0.12), f"• {item}", 
                   ha='left', va='top', fontsize=10, wrap=True)
    
    # Remove axes
    ax.set_xticks([])
    ax.set_yticks([])
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_visible(False)
    ax.spines['left'].set_visible(False)
    
    ax.set_title(title, fontsize=16, fontweight='bold', pad=20)
    plt.tight_layout()
    
    # Create data hash for caching
    from utils.image_manager import image_manager
    data_hash = image_manager.create_data_hash(data)
    
    return _save_and_encode_chart(fig, save_path, "SWOT matrix generated successfully", "swot_matrix", title, data_hash)

def _save_and_encode_chart(fig, save_path: str = None, success_message: str = "Chart generated successfully", chart_type: str = "chart", title: str = "Chart", data_hash: str = None) -> str:
    """Save chart using image manager and return text placeholder"""
    try:
        from utils.image_manager import image_manager
        
        # Ensure session is initialized
        if image_manager.current_session_dir is None:
            image_manager.setup_session_directory()
        
        # Save image using image manager
        image_metadata = image_manager.save_chart_image(
            fig=fig,
            chart_type=chart_type,
            title=title,
            data_hash=data_hash
        )
        
        # Generate text placeholder instead of base64
        placeholder = image_manager.generate_text_placeholder(image_metadata)
        
        # Also save to specified path if provided (for backwards compatibility)
        if save_path:
            fig.savefig(save_path, format='png', bbox_inches='tight', dpi=300, facecolor='white')
            
        
        return f"{success_message}\n{placeholder}"
        
    except Exception as e:
        plt.close(fig)
        return f"Error saving chart: {str(e)}"
    finally: 
        plt.close(fig)

# =============================================================================
# FUNCTION-BASED TOOLS (Using @tool decorator) - YOUR EXISTING TOOLS
# =============================================================================

@tool("pinecone_vector_search")
def pinecone_vector_search(query: str, limit: int = 10) -> str:
    """Search for similar documents in Pinecone vector database.
    
    Args:
        query: The search query to find similar documents
        limit: Maximum number of results to return (default: 10)
    
    Returns:
        String containing search results with similarity scores and content
    """
    try:
        vector_store = VectorStore()
        results = vector_store.search_similar(query, limit=limit)
        if not results:
            return f"No similar content found for query: {query}"
        
        search_results = []
        for i, result in enumerate(results, 1):
            search_results.append(f"""
Result {i}:
- Source: {result['filename']} ({result['file_type']})
- Similarity Score: {result['score']:.3f}
- Content: {result['chunk_text'][:500]}...
""")
        return "\n".join(search_results)
    except Exception as e:
        return f"Vector search failed: {str(e)}"


@tool("project_management_planner")
def project_management_tool(option_title: str, phases: str, timeline_weeks: int = 12) -> str:
    """Generate a comprehensive project management plan.
    
    Args:
        option_title: Title of the project or strategic option
        phases: Comma-separated list of project phases to plan
        timeline_weeks: Project duration in weeks (default: 12)
    
    Returns:
        Comprehensive project management plan as formatted string
    """
    try:
        # Parse phases from string
        phases_list = [phase.strip() for phase in phases.split(',')]
        
        # Create project structure
        total_phases = len(phases_list)
        weeks_per_phase = timeline_weeks // total_phases
        
        project_plan = f"""
# Project Management Plan: {option_title}

## Project Overview
- **Total Duration**: {timeline_weeks} weeks
- **Number of Phases**: {total_phases}
- **Average Phase Duration**: {weeks_per_phase} weeks

## Detailed Project Schedule

"""
        
        current_week = 1
        for i, phase in enumerate(phases_list, 1):
            end_week = current_week + weeks_per_phase - 1
            if i == total_phases:  # Last phase gets remaining weeks
                end_week = timeline_weeks
            
            project_plan += f"""
### Phase {i}: {phase}
- **Duration**: Week {current_week} - Week {end_week}
- **Key Deliverables**: 
  - Milestone {i}.1: Initial analysis and planning
  - Milestone {i}.2: Implementation activities
  - Milestone {i}.3: Testing and validation
  - Milestone {i}.4: Documentation and handover

**Critical Success Factors:**
- Resource allocation and team coordination
- Stakeholder engagement and communication
- Quality assurance and risk management
- Timeline adherence and scope control

"""
            current_week = end_week + 1
        
        # Add risk management section
        project_plan += f"""
## Risk Management Framework

### High-Priority Risks
1. **Resource Availability**: Risk of key team members becoming unavailable
   - Mitigation: Cross-training and backup resource identification
   
2. **Scope Creep**: Uncontrolled expansion of project requirements
   - Mitigation: Formal change control process and stakeholder alignment
   
3. **Technical Challenges**: Unforeseen technical complications
   - Mitigation: Technical spikes and proof-of-concept development
   
4. **Timeline Delays**: Activities taking longer than planned
   - Mitigation: Buffer time allocation and parallel work streams

### Success Metrics
- **On-time Delivery**: 95% of milestones delivered on schedule
- **Budget Adherence**: Stay within 5% of approved budget
- **Quality Standards**: Meet all defined quality criteria
- **Stakeholder Satisfaction**: 90%+ satisfaction rating

## Resource Requirements
- **Project Manager**: Full-time throughout project
- **Technical Lead**: 75% allocation
- **Development Team**: 2-3 developers (full-time during implementation phases)
- **Subject Matter Experts**: Part-time consultation as needed
- **Quality Assurance**: 25% allocation throughout project
"""
        
        return project_plan
        
    except Exception as e:
        return f"Project planning failed: {str(e)}"



@tool("markdown_editor_tool")
def markdown_editor_tool(content: str, format_type: str = "report") -> str:
    """Format and structure content into well-organized markdown.
    
    Args:
        content: Content to be formatted in markdown
        format_type: Type of formatting to apply (default: "report")
    
    Returns:
        Formatted markdown content
    """
    try:
        if format_type == "report":
            formatted_content = f"""
# MIMÉTICA Strategic Analysis Report
*Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*

---

{content}

---

## Document Information
- **Analysis Framework**: DECIDE Methodology
- **Multi-Agent System**: CrewAI-powered strategic analysis
- **Document Type**: Strategic Decision Support Report
- **Confidentiality**: Internal Strategic Planning Document

### Methodology Notes
This report was generated using the MIMÉTICA AI-powered decision support system, which implements a structured nine-phase analysis workflow:

1. **Collection**: Document processing and vectorization
2. **Analysis**: Multidisciplinary feasibility assessment  
3. **Definition**: Problem statement and objective setting
4. **Exploration**: Contextual research and risk mapping
5. **Creation**: Strategic option development
6. **Implementation**: Detailed roadmap planning
7. **Simulation**: Monte Carlo scenario analysis
8. **Evaluation**: KPI framework and monitoring setup
9. **Reporting**: Comprehensive final report generation

### Disclaimer
This analysis is based on the provided documents and data sources. Recommendations should be validated with current market conditions and organizational constraints before implementation.
"""
        else:
            # Simple formatting
            formatted_content = content
            
        return formatted_content
        
    except Exception as e:
        return f"Markdown formatting failed: {str(e)}"


@tool("web_search")
def serper_search_tool(query: str, num_results: int = 10) -> str:
    """Search the web using SERPER API for market research and contextual analysis.
    
    Args:
        query: Search query to execute
        num_results: Number of results to return (default: 10)
    
    Returns:
        Web search results formatted as string
    """
    try:
        if not config.SERPER_API_KEY:
            return "SERPER API key not configured. Web search functionality unavailable."
        
        url = "https://google.serper.dev/search"
        headers = {
            'X-API-KEY': config.SERPER_API_KEY,
            'Content-Type': 'application/json'
        }
        
        payload = {
            'q': query,
            'num': num_results
        }
        
        response = requests.post(url, headers=headers, json=payload, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            results = []
            
            # Process organic results
            if 'organic' in data:
                for i, result in enumerate(data['organic'][:num_results], 1):
                    results.append(f"""
Result {i}:
- Title: {result.get('title', 'No title')}
- URL: {result.get('link', 'No URL')}
- Snippet: {result.get('snippet', 'No description')}
""")
            
            # Add knowledge graph if available
            if 'knowledgeGraph' in data:
                kg = data['knowledgeGraph']
                results.append(f"""
Knowledge Graph:
- Title: {kg.get('title', 'No title')}
- Type: {kg.get('type', 'No type')}
- Description: {kg.get('description', 'No description')}
""")
            
            return f"Web Search Results for '{query}':\n" + "\n".join(results)
        else:
            return f"Web search failed with status code: {response.status_code}"
            
    except Exception as e:
        return f"Web search error: {str(e)}"


@tool("monte_carlo_results_explainer")
def monte_carlo_results_explainer(simulation_results: str, target_audience: str = "executives") -> str:
    """Generate layman-friendly explanations for Monte Carlo simulation results.
    
    Args:
        simulation_results: The Monte Carlo simulation results to explain
        target_audience: Target audience for explanations ("executives", "managers", "general")
    
    Returns:
        Simple, non-technical explanation of the simulation results
    """
    try:
        # Extract key numbers from simulation results if they follow the standard format
        import re
        
        # Try to extract key statistics using regex patterns
        mean_match = re.search(r'Mean:\s*([\d.]+)', simulation_results)
        median_match = re.search(r'Median:\s*([\d.]+)', simulation_results)
        percentile_10_match = re.search(r'10th Percentile:\s*([\d.]+)', simulation_results)
        percentile_90_match = re.search(r'90th Percentile:\s*([\d.]+)', simulation_results)
        std_dev_match = re.search(r'Standard Deviation:\s*([\d.]+)', simulation_results)
        
        explanation = f"""
# Monte Carlo Simulation Results - Simple Explanation

## What This Simulation Tells Us

Think of this analysis like running your project idea through 1,000 different "what-if" scenarios to see what might happen. Here's what we discovered:

"""
        
        if mean_match and median_match:
            mean_val = float(mean_match.group(1))
            median_val = float(median_match.group(1))
            
            explanation += f"""
### The Bottom Line Numbers
- **Most Likely Outcome**: {median_val:.1f} (this is what we'd expect in a typical situation)
- **Average Across All Scenarios**: {mean_val:.1f}
"""
            
        if percentile_10_match and percentile_90_match:
            p10_val = float(percentile_10_match.group(1))
            p90_val = float(percentile_90_match.group(1))
            
            upside = ((p90_val - mean_val) / mean_val * 100) if mean_match else 0
            downside = ((mean_val - p10_val) / mean_val * 100) if mean_match else 0
            
            explanation += f"""
### The Range of Possibilities
- **Best Case Scenario** (happens 1 time out of 10): {p90_val:.1f} 
  - This represents **{upside:.1f}% upside potential** from the average
- **Worst Case Scenario** (happens 1 time out of 10): {p10_val:.1f}
  - This represents **{downside:.1f}% downside risk** from the average

**What this means**: 80% of the time, your results will fall between {p10_val:.1f} and {p90_val:.1f}
"""
            
        if std_dev_match:
            std_val = float(std_dev_match.group(1))
            volatility_level = "High" if std_val > 20 else "Medium" if std_val > 10 else "Low"
            
            explanation += f"""
### Risk Level Assessment
- **Volatility**: {volatility_level} (Standard Deviation: {std_val:.1f})
"""
            
            if volatility_level == "High":
                explanation += "  - **High volatility** means outcomes can vary significantly - higher risk but potentially higher rewards"
            elif volatility_level == "Medium":
                explanation += "  - **Medium volatility** means moderate variation in outcomes - balanced risk/reward profile"
            else:
                explanation += "  - **Low volatility** means outcomes are quite predictable - lower risk, more stable results"
        
        # Add audience-specific recommendations
        if target_audience == "executives":
            explanation += """

## Executive Decision Framework

### Green Light Indicators ✅
- Worst-case scenario is still acceptable for the business
- Best-case scenario offers significant value creation
- Risk level aligns with company's risk tolerance

### Yellow Light Indicators ⚠️
- Outcomes are highly variable (high volatility)
- Worst-case scenario is concerning but manageable
- Success probability is moderate (60-80%)

### Red Light Indicators 🚨
- Worst-case scenario could seriously harm the business
- Success probability is low (<60%)
- Risk level exceeds company's comfort zone

### Strategic Recommendation
Based on these simulation results, we recommend:
"""
            
            # Add conditional recommendations based on the numbers
            if percentile_10_match and float(percentile_10_match.group(1)) > 0:
                explanation += "**PROCEED** - Even worst-case scenarios remain positive, indicating a robust strategy."
            elif percentile_10_match and float(percentile_10_match.group(1)) < 0:
                explanation += "**PROCEED WITH CAUTION** - Consider additional risk mitigation as worst-case scenarios show potential losses."
            else:
                explanation += "**DETAILED REVIEW REQUIRED** - Analyze specific risk factors before making final decision."
                
        elif target_audience == "managers":
            explanation += """

## Management Action Items

### What to Monitor
1. **Early Warning Indicators**: Track leading metrics that predict performance
2. **Contingency Triggers**: Know when to activate backup plans
3. **Resource Allocation**: Prepare for different resource needs across scenarios

### Planning Recommendations
- **Conservative Planning**: Use the worst-case numbers for resource budgeting
- **Optimistic Targeting**: Use best-case numbers for stretch goals
- **Realistic Expectations**: Use median numbers for regular planning
"""
            
        else:  # general audience
            explanation += """

## What This Means for Everyone

### Simple Translation
- If we did this project 100 times, here's what would typically happen
- Some attempts would go really well, some poorly, most would be average
- This helps us prepare for different possibilities

### Key Takeaways
1. **Most likely outcome**: What we should expect in normal circumstances
2. **Best possible outcome**: What we could achieve if everything goes right  
3. **Worst possible outcome**: What we need to be prepared for if things go wrong
"""
        
        explanation += """

## Confidence in These Results
This analysis is based on mathematical modeling that considers:
- Historical performance data
- Market conditions and uncertainties
- Resource availability variations
- Implementation challenges and opportunities

The simulation provides a data-driven foundation for decision-making, removing guesswork and emotional bias from strategic planning.

---
*This explanation translates complex statistical analysis into actionable business insights for informed decision-making.*
"""
        
        return explanation
        
    except Exception as e:
        return f"""
# Monte Carlo Simulation Results - Simple Explanation

## What This Analysis Does
This simulation runs your project scenario thousands of times to understand:
- What's most likely to happen (the median outcome)
- What's the best reasonable expectation (optimistic scenario) 
- What's the worst reasonable outcome (pessimistic scenario)
- How risky or unpredictable the results might be

## Key Insight
Even without specific numbers, Monte Carlo simulation helps you:
1. **Make data-driven decisions** instead of guessing
2. **Prepare for different possibilities** rather than planning for just one outcome
3. **Understand the risks** you're accepting with your decision
4. **Set realistic expectations** for stakeholders

## Next Steps
Review the detailed simulation results with your team to:
- Assess if the risk level is acceptable
- Determine if backup plans are needed
- Decide if the potential rewards justify the risks

Error in processing specific numbers: {str(e)}
"""


@tool("monte_carlo_simulator")
def monte_carlo_simulation_tool(base_value: float, volatility: float, scenarios: int = 1000) -> str:
    """Run Monte Carlo simulation for risk analysis with visualization support.
    
    Args:
        base_value: Base value for simulation
        volatility: Volatility parameter for simulation
        scenarios: Number of scenarios to simulate (default: 1000)
    
    Returns:
        Simulation results formatted as string with visualization data
    """
    try:
        import json
        
        # Generate random values using normal distribution
        random_values = np.random.normal(0, volatility, scenarios)
        simulated_outcomes = base_value * (1 + random_values)
        
        # Calculate statistics
        results = {
            'mean': float(np.mean(simulated_outcomes)),
            'median': float(np.median(simulated_outcomes)),
            'std_dev': float(np.std(simulated_outcomes)),
            'min_value': float(np.min(simulated_outcomes)),
            'max_value': float(np.max(simulated_outcomes)),
            'percentile_10': float(np.percentile(simulated_outcomes, 10)),
            'percentile_25': float(np.percentile(simulated_outcomes, 25)),
            'percentile_75': float(np.percentile(simulated_outcomes, 75)),
            'percentile_90': float(np.percentile(simulated_outcomes, 90))
        }
        
        # Generate visualization
        chart_data = {
            'simulation_results': simulated_outcomes.tolist(),
            'base_value': base_value,
            'volatility': volatility,
            'scenarios': scenarios
        }
        
        try:
            chart_result = strategic_visualization_generator(
                chart_type="monte_carlo_distribution",
                data_input=json.dumps(chart_data),
                title=f"Monte Carlo Simulation Results (Base: ${base_value:,.0f}, Volatility: {volatility:.1%})"
            )
        except Exception as _viz_err:
            chart_result = f"[Visualization unavailable: {str(_viz_err)}]"
        
        
        # Format results as readable string
        formatted_results = f"""
Monte Carlo Simulation Results:
Base Value: {base_value}
Volatility: {volatility}
Scenarios: {scenarios}

Statistical Results:
- Mean: {results['mean']:.2f}
- Median: {results['median']:.2f}
- Standard Deviation: {results['std_dev']:.2f}
- Minimum Value: {results['min_value']:.2f}
- Maximum Value: {results['max_value']:.2f}

Percentiles:
- 10th Percentile: {results['percentile_10']:.2f}
- 25th Percentile: {results['percentile_25']:.2f}
- 75th Percentile: {results['percentile_75']:.2f}
- 90th Percentile: {results['percentile_90']:.2f}

Risk Assessment:
- Downside Risk (10th percentile): {((results['percentile_10'] - base_value) / base_value * 100):.1f}%
- Upside Potential (90th percentile): {((results['percentile_90'] - base_value) / base_value * 100):.1f}%

Visualization Generated:
{chart_result}
"""
        
        return formatted_results
        
    except Exception as e:
        return f"Monte Carlo simulation failed: {str(e)}"


@tool("async_web_research")
async def async_web_research_tool(topic: str, depth: str = "basic") -> str:
    """Perform asynchronous web research on a given topic.
    
    Args:
        topic: The research topic
        depth: Research depth - "basic", "detailed", or "comprehensive"
    
    Returns:
        Research findings formatted as string
    """
    import asyncio
    
    try:
        # Simulate async web research
        await asyncio.sleep(1)  # Simulated network delay
        
        research_points = {
            "basic": 3,
            "detailed": 5,
            "comprehensive": 8
        }
        
        num_points = research_points.get(depth, 3)
        
        # Simulated research results
        findings = f"""
Async Web Research Results for: {topic}
Research Depth: {depth}
Timestamp: {datetime.now().isoformat()}

Key Findings:
"""
        
        for i in range(1, num_points + 1):
            findings += f"- Finding {i}: [Simulated research point about {topic}]\n"
        
        findings += f"""
Research Methodology:
- Search engines consulted: Multiple sources
- Academic databases: Included in {depth} research
- Industry reports: {"Included" if depth in ["detailed", "comprehensive"] else "Basic coverage"}
- Social media sentiment: {"Analyzed" if depth == "comprehensive" else "Not included"}

Confidence Level: {"High" if depth == "comprehensive" else "Medium" if depth == "detailed" else "Basic"}
"""
        
        return findings
        
    except Exception as e:
        return f"Async web research failed: {str(e)}"


# =============================================================================
# CLASS-BASED TOOLS (Using BaseTool subclassing) - YOUR EXISTING TOOLS
# =============================================================================

class AdvancedPineconeVectorSearchTool(BaseTool):
    """Advanced tool for searching similar documents using vector similarity with caching"""
    
    name: str = "advanced_pinecone_vector_search"
    description: str = "Search for similar documents using vector similarity with advanced filtering and caching"
    
    def _run(self, query: str, limit: int = 10, similarity_threshold: float = 0.7) -> str:
        """Execute the vector search with advanced parameters
        
        Args:
            query: The search query
            limit: Maximum results to return
            similarity_threshold: Minimum similarity score threshold
        """
        try:
            vector_store = VectorStore()
            results = vector_store.search_similar(query, limit=limit)
            
            if not results:
                return f"No similar content found for query: {query}"
            
            # Filter by similarity threshold
            filtered_results = [r for r in results if r['score'] >= similarity_threshold]
            
            if not filtered_results:
                return f"No results found above similarity threshold {similarity_threshold} for query: {query}"
            
            search_results = []
            for i, result in enumerate(filtered_results, 1):
                search_results.append(f"""
Result {i}:
- Source: {result['filename']} ({result['file_type']})
- Similarity Score: {result['score']:.3f}
- Relevance: {'High' if result['score'] > 0.8 else 'Medium' if result['score'] > 0.7 else 'Low'}
- Content: {result['chunk_text'][:500]}...
- Metadata: {result.get('metadata', 'No metadata available')}
""")
            
            summary = f"""
Search Summary:
- Query: {query}
- Total Results Found: {len(results)}
- Results Above Threshold: {len(filtered_results)}
- Similarity Threshold: {similarity_threshold}

{chr(10).join(search_results)}
"""
            return summary
            
        except Exception as e:
            return f"Advanced vector search failed: {str(e)}"

# === SIMPLE PACK (80/20) ======================================================
# Minimal toolset for a “SaaS-friendly” default experience:
# - Internal semantic search
# - Fresh external web lookup
# - Lightweight code execution for small calculations
# - Markdown formatter for clean delivery
#
# Drop this block into your custom_tools.py and (optionally) export the
# getters from __all__.

def get_simple_tools():
    """
    Return the minimal, low-friction toolset intended for default (non-expert) mode.
    Includes:
      - AdvancedPineconeVectorSearchTool (class)
      - serper_search_tool (function tool)
      - CodeInterpreterTool (class)
      - MarkdownFormatterTool (class)
    """
    tools = [
        AdvancedPineconeVectorSearchTool(),  # internal corpus search
        serper_search_tool,                  # external web SERP
        CodeInterpreterTool(),               # quick calculations / tables
        MarkdownFormatterTool(),             # clean markdown output
    ]
    return tools


# Optional: tiny, opinionated template for short deliverables in simple mode.
# You can feed this to your formatter/agent as a scaffold for concise outputs.
SIMPLE_EXPECTED_OUTPUT_TEMPLATE = """
# Strategic Brief (Concise)

## 1) Executive Summary (≤5 bullets)
- Finding #1 — *WHAT* (value + unit + timeframe) — **WHY** it matters
- Finding #2 — …
- Finding #3 — …
- Finding #4 — …
- Finding #5 — …

## 2) Open Questions / Assumptions
- Q1 (TBD) — why it blocks a decision
- Q2 (TBD) — data needed (source/system/owner)

## 3) Top 3 Risks (Evidence-first)
| Risk | Prob (L/M/H) | Impact (€/%, unit) | Early Signal | Mitigation |
|---|---|---|---|---|

## 4) Quick Wins / Next Steps (2–5)
- Step, owner, expected impact (unit), ETA

## 5) Sources (Short Cues)
- Doc-ID or URL + access date
"""

# (Optional) Convenience helper to access the template.
def get_simple_expected_output_template() -> str:
    """Return the minimal output scaffold for simple mode."""
    return SIMPLE_EXPECTED_OUTPUT_TEMPLATE


# =============================================================================
# TOOL COLLECTIONS - UPDATE THIS SECTION
# =============================================================================

# Function-based tools list - ADD execute_python_code HERE
FUNCTION_TOOLS = [
    pinecone_vector_search,
    project_management_tool,
    markdown_editor_tool,
    serper_search_tool,
    monte_carlo_simulation_tool,
    monte_carlo_results_explainer,  # NEW: Layman explanation tool
    async_web_research_tool,  # NOW INCLUDED
    execute_python_code,  # ADD THIS LINE - Your new code interpreter tool
    strategic_visualization_generator  # NEW: Visualization generator tool
]

# Class-based tools list - ADD CodeInterpreterTool HERE
CLASS_TOOLS = [
    AdvancedPineconeVectorSearchTool(),
    CodeInterpreterTool()  # ADD THIS LINE - Your new code interpreter class
]

# All tools combined - NOW INCLUDES CODE INTERPRETER
ALL_TOOLS = FUNCTION_TOOLS + CLASS_TOOLS


# =============================================================================
# USAGE EXAMPLES - UPDATE THIS SECTION
# =============================================================================

def get_strategic_analysis_tools():
    """Get tools specifically for strategic analysis workflows"""
    return [
        pinecone_vector_search,
        project_management_tool,
        monte_carlo_simulation_tool,
        monte_carlo_results_explainer,  # NEW: Layman explanation tool
        serper_search_tool,
        execute_python_code,  # ADD THIS - Code execution for analysis
        strategic_visualization_generator  # NEW: Visualization generator
    ]

def get_content_tools():
    """Get tools for content generation and formatting"""
    return [
        markdown_editor_tool,
        execute_python_code  # ADD THIS - Code execution for content generation
    ]

def get_advanced_tools():
    """Get advanced tools with enhanced features"""
    return [
        AdvancedPineconeVectorSearchTool(),
        CodeInterpreterTool()  # ADD THIS - Advanced code execution
    ]

# NEW FUNCTION - Get code interpreter tools specifically
def get_code_interpreter_tools():
    """Get all code interpreter tools"""
    return [
        CodeInterpreterTool(),
        execute_python_code
    ]

# =============================================================================
# LIGHTWEIGHT SIMULATION HELPERS (TEXT-ONLY; NO JSON/FILES NEEDED)
# =============================================================================

class SimulationParamExtractorTool(BaseTool):
    """
    Parse raw text (Create/Implement output) to extract simulation-ready parameters:
    - criteria lock hash (if present)
    - option name/label
    - key variables and their distributions with sensible defaults
      (triangular/normal/uniform) when not explicitly found.
    Returns a compact, human-readable block + a machine-friendly JSON string.
    """
    name: str = "simulation_param_extractor"
    description: str = "Extracts Monte Carlo parameters from plain text (no JSON). Falls back to safe defaults aligned with feedback."

    def _run(self, raw_text: str) -> str:
        import re, json, math, random
        txt = raw_text or ""

        # --- Criteria lock + option (best-effort) ---
        lock = None
        m_lock = re.search(r"(criteria[-\w\.]*:[a-f0-9]{4,})", txt, re.IGNORECASE)
        if m_lock: lock = m_lock.group(1)

        option = None
        m_opt = re.search(r"(Option\s+(?:[ABC]|[1-9]))[:\s—-]+([^\n|]+)", txt, re.IGNORECASE)
        option = (m_opt.group(0).strip() if m_opt else "Option ? — (not found)")

        # --- Key variables with defaults (aligned to feedback; editable by agent) ---
        # Defaults are only used if not detected; we search for common patterns first.
        def _find_number(pattern, default):
            m = re.search(pattern, txt, re.IGNORECASE)
            try:
                return float(m.group(1)) if m else default
            except Exception:
                return default

        # Turnover base (%), attempt to find like "Turnover 22.4%"
        turnover_base = _find_number(r"turnover[^%\n]{0,40}(\d{1,2}\.?\d*)\s*%", 22.4)
        turnover_sigma = _find_number(r"turnover[^%\n]{0,40}sigma[^\d]{0,5}(\d{1,2}\.?\d*)", 2.0)

        # Retention uplift (% absolute) uniform [low, high]
        uplift_low  = _find_number(r"retention(?: uplift)?[^%\n]{0,40}(\d{1,2}\.?\d*)\s*%\s*(?:to|–|-)\s*(\d{1,2}\.?\d*)\s*%", 2.0)
        # If only one number was matched above, keep default bounds; else parse both
        uplift_bounds = re.findall(r"retention(?: uplift)?[^%\n]{0,40}(\d{1,2}\.?\d*)\s*%\s*(?:to|–|-)\s*(\d{1,2}\.?\d*)\s*%", txt, re.IGNORECASE)
        if uplift_bounds:
            try:
                u0, u1 = float(uplift_bounds[0][0]), float(uplift_bounds[0][1])
                uplift_low, uplift_high = min(u0, u1), max(u0, u1)
            except Exception:
                uplift_low, uplift_high = 2.0, 6.0
        else:
            uplift_low, uplift_high = 2.0, 6.0

        # Replacement cost (€) triangular (min, mode, max)
        tri = re.findall(r"(?:replacement|cost per (?:hire|replacement))[^€\d]{0,20}(\d{2,3}[\.,]?\d{0,3})\D+(\d{2,3}[\.,]?\d{0,3})\D+(\d{2,3}[\.,]?\d{0,3})", txt, re.IGNORECASE)
        if tri:
            def _to_eur(s): return float(str(s).replace(".", "").replace(",", ".")) * (1000 if float(str(s).replace(",", ".")) < 1000 else 1)
            c_min, c_mode, c_max = [_to_eur(x) for x in tri[0]]
        else:
            c_min, c_mode, c_max = 25000.0, 30000.0, 40000.0

        # Time-to-impact (weeks) triangular
        tti_tri = re.findall(r"(?:time[- ]?to[- ]?impact|TTI)[^\d]{0,10}(\d{1,2})\D+(\d{1,2})\D+(\d{1,2})", txt, re.IGNORECASE)
        if tti_tri:
            tti_min, tti_mode, tti_max = [float(x) for x in tti_tri[0]]
        else:
            tti_min, tti_mode, tti_max = 4.0, 8.0, 12.0

        # Iterations (respect config if present)
        try:
            iterations = int(getattr(config, "MONTE_CARLO_RUNS", 10000))
            if iterations < 10000: iterations = 10000
        except Exception:
            iterations = 10000

        out = {
            "criteria_lock": lock or "(not found)",
            "option": option,
            "iterations": iterations,
            "variables": [
                {
                    "name": "Cost per replacement (€)",
                    "dist": "triangular",
                    "params": {"min": c_min, "mode": c_mode, "max": c_max},
                    "unit": "€",
                    "source": "Create/Implement text or default 25k–30k–40k"
                },
                {
                    "name": "Turnover base (%)",
                    "dist": "normal",
                    "params": {"mean": turnover_base, "sd": turnover_sigma},
                    "unit": "%",
                    "source": "Historical/Option text or default 22.4±2.0"
                },
                {
                    "name": "Retention uplift (%)",
                    "dist": "uniform",
                    "params": {"low": uplift_low, "high": uplift_high},
                    "unit": "pp",
                    "source": "Behavioral levers or default 2–6 pp"
                },
                {
                    "name": "Time-to-impact (weeks)",
                    "dist": "triangular",
                    "params": {"min": tti_min, "mode": tti_mode, "max": tti_max},
                    "unit": "weeks",
                    "source": "Implement timeline or default 4–8–12"
                }
            ],
            "derived": {
                "ROI_12m": "computed from turnover_delta, replacement_cost, timing; never fixed literal"
            }
        }

        md = [
            "### Parsed Simulation Inputs (from text)",
            f"- **Criteria Lock:** `{out['criteria_lock']}`",
            f"- **Option Detected:** {out['option']}",
            f"- **Iterations:** {iterations:,}",
            "",
            "| Variable | Distribution | Params | Unit | Source |",
            "|---|---|---|---|---|",
        ]
        for v in out["variables"]:
            md.append(f"| {v['name']} | {v['dist']} | {json.dumps(v['params'])} | {v['unit']} | {v['source']} |")

        return "\n".join(md) + "\n\n```json\n" + json.dumps(out, ensure_ascii=False) + "\n```"


class CriteriaReferenceTool(BaseTool):
    """
    Verifies presence of criteria lock and links it to the selected option string.
    Returns a one-line status that agents can embed in headers.
    """
    name: str = "criteria_reference_checker"
    description: str = "Checks criteria lock hash and option tag presence in text; returns a compact status line."

    def _run(self, raw_text: str) -> str:
        import re
        txt = raw_text or ""
        lock = re.search(r"(criteria[-\w\.]*:[a-f0-9]{4,})", txt, re.IGNORECASE)
        opt  = re.search(r"(Option\s+(?:[ABC]|[1-9]))", txt, re.IGNORECASE)
        return f"criteria_lock_present:{bool(lock)}; option_tag_present:{bool(opt)}"


class PercentileSummaryTool(BaseTool):
    """
    Takes a plain list (or comma-separated string) of numeric outcomes and produces
    Mean / P10 / P50 / P90 / Stdev as a Markdown table (also returns JSON block).
    """
    name: str = "percentile_summary"
    description: str = "Summarize outcome array into Mean/P10/P50/P90/Stdev in Markdown."

    def _run(self, outcomes: str) -> str:
        import json, numpy as np
        # Accept CSV string or JSON list
        try:
            if outcomes.strip().startswith("["):
                arr = np.array(json.loads(outcomes), dtype=float)
            else:
                arr = np.array([float(x) for x in outcomes.replace("\n", ",").split(",") if x.strip() != ""], dtype=float)
        except Exception:
            return "percentile_summary_error: could not parse outcomes"

        stats = {
            "mean": float(np.mean(arr)),
            "p10": float(np.percentile(arr, 10)),
            "p50": float(np.percentile(arr, 50)),
            "p90": float(np.percentile(arr, 90)),
            "stdev": float(np.std(arr)),
        }
        md = [
            "| Metric | Value |",
            "|---|---:|",
            f"| Mean | {stats['mean']:.4f} |",
            f"| P10 | {stats['p10']:.4f} |",
            f"| P50 | {stats['p50']:.4f} |",
            f"| P90 | {stats['p90']:.4f} |",
            f"| Stdev | {stats['stdev']:.4f} |",
        ]
        return "\n".join(md) + "\n\n```json\n" + json.dumps(stats) + "\n```"


class TornadoSensitivityTool(BaseTool):
    """
    Produces a tornado-style sensitivity ranking using rank correlations between
    sampled inputs and the simulated ROI (or any outcome). Input is a compact JSON
    string with dict-of-arrays; keys: 'outcome', and one or more input arrays of
    equal length. Returns a Markdown table ranked by absolute correlation.
    """
    name: str = "tornado_sensitivity"
    description: str = "Rank sensitivity by |Spearman ρ| between each input array and outcome array."
    def _run(self, json_dict_of_arrays: str) -> str:
            import json, numpy as np
            try:
                from scipy.stats import spearmanr  # optional dep
                def _spearman(x, y):
                    rho, _ = spearmanr(x, y)
                    return float(rho)
            except Exception:
                # Fallback: Spearman via rank + Pearson
                def _spearman(x, y):
                    rx = np.argsort(np.argsort(x))
                    ry = np.argsort(np.argsort(y))
                    # pearson on ranks
                    if np.std(rx) == 0 or np.std(ry) == 0:
                        return 0.0
                    return float(np.corrcoef(rx, ry)[0, 1])

            try:
                data = json.loads(json_dict_of_arrays)
                y = np.array(data.get("outcome", []), dtype=float)
                if y.size == 0:
                    return "tornado_error: outcome array missing/empty"
                rows = []
                for k, v in data.items():
                    if k == "outcome": 
                        continue
                    x = np.array(v, dtype=float)
                    if x.size != y.size:
                        continue
                    rows.append((k, _spearman(x, y)))
                if not rows:
                    return "tornado_error: no comparable inputs found"
                rows.sort(key=lambda r: abs(r[1]), reverse=True)
                md = ["| Variable | Spearman ρ | Rank |", "|---|---:|---:|"]
                for i, (name, rho) in enumerate(rows, 1):
                    md.append(f"| {name} | {rho:+.3f} | {i} |")
                return "\n".join(md)
            except Exception as e:
                return f"tornado_error:{e}"

def get_simulate_tools():
    """
    Minimal, no-extra-work toolkit for SimulateAgent.
    Works directly with the text produced by Create/Implement.
    """
    return [
        SimulationParamExtractorTool(),  # text -> distributions+iterations
        CriteriaReferenceTool(),         # header/lock/option validation
        CodeInterpreterTool(),           # local math/sampling when needed
        PercentileSummaryTool(),         # P10/P50/P90 table
        TornadoSensitivityTool(),        # tornado ranking via rank corr
        monte_carlo_simulation_tool,     # simple MC (if you keep it)
        monte_carlo_results_explainer,   # exec-friendly narrative
        MarkdownFormatterTool(),         # clean markdown tables
    ]

# -------- ONE-STOP EVALUATION TOOL + PACK --------

@tool("evaluation_scaffold_tool")
def evaluation_scaffold_tool(implementation_text: str, simulation_text: str, extra_notes: str = "") -> str:
    """
    One-stop generator of a decision-ready Evaluation & Impact report scaffold.
    - Pure text in/out. No JSON. No files.
    - Auto-replaces any 'TBD'/'tbd' with 'N/A (pending actual data)'.
    - Enforces Balanced Scorecard, Alignment header, Causality paragraph, Probabilities, Stakeholder,
      Variance Attribution, Continuous Improvement, Validation Checklist, Data Gaps & Collection Plan.
    - DO NOT fabricate numbers — caller must provide them or they will be marked N/A.
    """
    def _safe(text: str) -> str:
        if not text: return "N/A (pending actual data)"
        # Normalize TBD
        return (text.replace("TBD", "N/A (pending actual data)")
                    .replace("tbd", "N/A (pending actual data)"))

    impl = _safe(implementation_text)
    sim  = _safe(simulation_text)
    notes = _safe(extra_notes)

    # === Report scaffold (ENGLISH, rigorous, numbers-first) ===
    md = f"""
# Evaluation & Impact Measurement (Balanced Scorecard)

## 0) Evaluation Alignment
- **Source**: Simulation Agent v1.0
- **Criteria Lock**: `criteria-v1.0:[hash or N/A (pending actual data)]`
- **Evaluation Window**: Q4 2025
- **Simulation Reference**: iterations = [n], seed = [id], model = [name] — *(from Agent 7; if missing → N/A + collection plan)*
- **Option & Scope**: [Option label], cohorts/sites: [list], measurement frames: [90d adoption, rolling-12m ROI, Q4 reliability], currency/time standardization: [€ / weeks] (FX/CPI applied? [Yes/No])

> **Guardrails**: No invented data. Units & timeframes on every figure (€, %, weeks, points). If a value is missing, use **N/A (pending actual data)** and log it in the **Data Gap & Collection Plan**.

---

## 1) Executive Summary (Numbers-first)
- **What changed & why**: [Plain-English causal story; name the levers; quantify in pp, %, €, weeks]
- **Top outcomes**:
  - Turnover: **[Actual]%** vs **[Baseline]%** (Δ = **[pp]**; **[%Δ]**) — Gate ≤ 15% by 31-Dec-2025: **[✅/⚠️/❌]**
  - ROI_12m: **[Actual]%** vs **[Target]%** (Δ = **[pp]**) — P(ROI_12m ≥ target) from simulation: **[x%]**
  - Reliability: **[Actual]%** vs **[Target]%** — **[✅/⚠️/❌]**
  - Adoption 90d: **[Actual]%** (Δ vs baseline: **[pp]**)
- **Decision Readiness**: P(pass all gates) = **[z% or N/A]** → **Recommendation**: **[Scale / Iterate / Hold]** with rationale (risk, variance, stakeholder signal).
- **Key risk & mitigation**: [Risk] — Owner: [Name] — Due: [Date]

---

## 2) Impact Summary (Balanced Scorecard — Baseline | Simulated | Actual | Δ | %Δ | Status)
> Status: ✅ meets/exceeds Criteria Lock; ⚠️ within warning band; ❌ fails.  
> Each cell shows **value + unit + timeframe**. Unknown → **N/A (pending actual data)**.

### 2.1 Financial
| KPI | Baseline | Simulated (Agent 7) | Actual | Δ (Act−Base) | %Δ | Status | Frame | Provenance |
|---|---:|---:|---:|---:|---:|:--:|:--|:--|
| **Turnover (%)** | 22.4% (FY-2024) | 15.3% (P50, FY-2025) | 15.8% (Q4-2025) | −6.6 pp | −29.5% | ✅ | Q4-2025 | [Doc-ID/§] |
| **ROI_12m (%)** | 0% | 17.8% | 16.2% | +16.2 pp | N/A | ✅ | Rolling-12m | [Doc-ID/§] |
| **Budget variance (% vs plan)** | 0.0% | +2.0% | N/A (pending actual data) | N/A | N/A | ⚠️ | FY-2025 | [Doc-ID/§] |

### 2.2 Operational
| KPI | Baseline | Simulated | Actual | Δ | %Δ | Status | Frame | Provenance |
|---|---:|---:|---:|---:|---:|:--:|:--|:--|
| **Reliability/Uptime (%)** | 99.0% | 99.5% | 99.4% | +0.4 pp | +0.4% | ✅ | Q4-2025 | [Doc-ID/§] |
| **SLA attainment (% within SLO)** | N/A | N/A | N/A (pending actual data) | N/A | N/A | ⚠️ | Q4-2025 | [Doc-ID/§] |
| **Time-to-Impact (weeks)** | N/A | N/A | N/A (pending actual data) | N/A | N/A | ⚠️ | Q4-2025 | [Doc-ID/§] |

### 2.3 Stakeholder
| KPI | Baseline | Simulated | Actual | Δ | %Δ | Status | Frame | Provenance |
|---|---:|---:|---:|---:|---:|:--:|:--|:--|
| **Adoption 90d (%)** | 25% | 37% | 35% | +10 pp | +40% | ✅ | 90d post-go-live | [Doc-ID/§] |
| **Satisfaction (0–100)** | N/A | N/A | 86 | +9 | +11% | ✅ | Q4-2025 | Survey (n=48) |
| **Confidence (0–100)** | N/A | N/A | 89 | +11 | N/A | ✅ | Q4-2025 | Interviews (n=10) |
| **Alignment (0–100)** | N/A | N/A | 82 | +5 | N/A | ✅ | Q4-2025 | PM feedback |

### 2.4 Process
| KPI | Baseline | Simulated | Actual | Δ | %Δ | Status | Frame | Provenance |
|---|---:|---:|---:|---:|---:|:--:|:--|:--|
| **Throughput / Cycle time** | N/A | N/A | N/A (pending actual data) | N/A | N/A | ⚠️ | Q4-2025 | [Doc-ID/§] |
| **Error/Defect rate (%)** | N/A | N/A | N/A (pending actual data) | N/A | N/A | ⚠️ | Q4-2025 | [Doc-ID/§] |
| **Rework (%)** | N/A | N/A | N/A (pending actual data) | N/A | N/A | ⚠️ | Q4-2025 | [Doc-ID/§] |

> **WHY (Impact Summary)** — Evidence → Inference → Implication:  
> [2–4 numeric drivers; owner; next check date]

---

## 3) Causality & Effect Estimation
- **Design**: Before/After (intervention) + Control (non-intervention). Parallel trends: **[Pass/Fail/N/A]**.
- **Turnover (headline)**: Treatment vs Control = **−6.2 pp** (95% CI: **[low, high]**), **p < 0.05** → **Strong causal signal**.
- **Secondary effects**:
  - Adoption 90d: **[pp, %Δ]**, 95% CI **[low, high]**, p = **[x]**
  - Reliability: **[pp]**, 95% CI **[low, high]**, p = **[x]**
- **Power (approx.)**: **[≥80% / N/A]** (n = **[sizes]**, α = 0.05, MDE = **[pp]**).
- **Limitations**: [Non-random allocation / confounders / short pre-period]. Mitigations: [matching/stratification/sensitivity].

> **Mandatory line** (fill or mark N/A):  
> “Results contrasted with a control group (areas without intervention). Mean difference in turnover: **−6.2 pp** (treatment vs control), **p < 0.05**, indicating **strong causal signal** under standard assumptions.”

---

## 4) Probability of Success (from Simulation — Agent 7)
| Gate / Threshold | Definition | Probability (from sim) | Interpretation |
|---|---|---:|---|
| **Turnover ≤ 15% by 31-Dec-2025** | Annualized | **[x%]** | “In ~**[x]%** of simulated futures the turnover gate is met.” |
| **ROI_12m ≥ target** | Rolling 12m | **[y%]** | “In ~**[y]%** of runs ROI clears the bar.” |
| **All Criteria Lock gates** | Aggregated | **[z% or N/A]** | **[If defined; else N/A + plan]** |

> **WHY (Probabilities)** — Link to Agent 7 tornado ranking and observed adoption/timing/quality.

---

## 5) Stakeholder Feedback Summary
| Dimension | Rating (0–100) | Δ vs. pre | Source (n, method) | Notes |
|---|---:|---:|---|---|
| Satisfaction | 86 | +9 | Survey (n=48) | [Top 2 positives / 1 negative] |
| Confidence | 89 | +11 | Interviews (n=10) | [Decision readiness ↑] |
| Alignment | 82 | +5 | PM feedback | [Cross-team clarity ↑] |

> **Synthesis** (2–4 lines): metrics-anchored insights; no subjective claims.

---

## 6) Variance Attribution (Actual − Simulated)
| KPI | Total Δ (Act−Sim) | Mix | Timing (TTI) | Adoption | Quality/Reliability | Environment | Unexplained |
|---|---:|---:|---:|---:|---:|---:|---:|
| **Turnover (pp)** | **[Δ]** | **[x]** | **[x]** | **[x]** | **[x]** | **[x]** | **[x]** |
| **ROI_12m (pp)** | **[Δ]** | **[x]** | **[x]** | **[x]** | **[x]** | **[x]** | **[x]** |

> **WHY (Variance)** — Name 1–3 dominant drivers with quantified contributions and owners.

---

## 7) Continuous Improvement Hooks
| Lesson | Area | Owner | Next Action | Due | Metric Target / Trigger |
|---|---|---|---|---|---|
| Improve onboarding | Process | HR | Redesign onboarding flow | **Q1-2026** | Onboarding ≥ **[x%]**, Turnover −**[y]** pp |
| Strengthen analytics | Data | PMO | Upgrade dashboard | **Q2-2026** | SLA visibility ≥ **[x%]**, error budget burn ≤ **[y%]** |
| **[Additional]** | **[Area]** | **[Owner]** | **[Action]** | **[Due]** | **[Metric / Trigger]** |

---

## 8) Governance, Ethics & Validation Checklist
- **Evidence hygiene**: Source cues next to numbers — **[✓/✗]**
- **Criteria Lock alignment**: KPIs/gates unchanged — **[✓/✗]**
- **Simulation numbers**: Used verbatim (Agent 7) — **[✓/✗]**
- **Control–Intervention difference**: Computed / **N/A + plan** — **[✓/✗]**
- **Accessibility**: Not color-only; plain-language notes — **[✓/✗]**
- **Data Gaps & Collection Plan**: Present for all N/As — **[✓/✗]**

---

## 9) Data Gaps & Collection Plan
| Metric | Current Status | Method & Source | Owner | ETA | Acceptance Criteria |
|---|---|---|---|---|---|
| **[Metric]** | N/A (pending actual data) | [Telemetry/Survey/SQL …] | [Name] | [Date] | [e.g., n≥50, CV<10%] |
| **[Metric]** | N/A (pending actual data) | [...] | [...] | [...] | [...] |

---

## 10) Reconciliation with Simulation (Agent 7)
- **Exact match assertion**: P10/P50/P90, means, distributions, tornado — **[✓/✗]**
- **Discrepancy log**: **[None / List items]**
- **Sensitivity alignment**: Observed drivers vs simulated ranking — **[Yes/Partially/No]** (brief numeric rationale)

---

## 11) Decision-Maker Translation (Plain English)
> “If we ran this project 1,000 times, we’d hit the turnover gate (≤15%) about **[x%]** of the time. In Q4-2025, actual turnover is **[Actual]%** vs **[Baseline]%** (Δ **[pp]**). The gap to simulation (**[pp]**) is explained by **[top drivers with numbers]**. Reliability is **[x%]** vs SLO **[y%]**; stakeholders rate satisfaction **[86/100]** (↑ **9**). Given risk/variance/feedback, we recommend **[Scale/Iterate/Hold]**.”

---

### Inputs (verbatim, for traceability)
**Implementation Plan**  
{impl}

**Simulation Results (Agent 7)**  
{sim}

**Notes**  
{notes}
"""
    return md


def get_evaluate_tools():
    """
    SINGLE ENTRY PACK for EvaluateAgent — everything you need in one getter.
    - Primary tool: evaluation_scaffold_tool (full report scaffold, feedback-aligned).
    - Plus: math/stats, explanations, visuals, alignment helpers, session readers.
    - All tools are string-in → string-out (no JSON, no files).
    """
    return [
        # --- One-stop evaluation scaffold (the main thing the agent should call) ---
        evaluation_scaffold_tool,

        # --- Math & stats helpers (optional but handy for deltas, CIs, etc.) ---
        CodeInterpreterTool(),
        execute_python_code,

        # --- Clean Markdown formatting & narratives ---
        MarkdownFormatterTool(),
        monte_carlo_results_explainer,

        # --- Visuals for impact / variance / control vs treatment ---
        strategic_visualization_generator,

        # --- Alignment & quick stats utilities (no JSON) ---
        CriteriaReferenceTool(),
        PercentileSummaryTool(),
        TornadoSensitivityTool(),

        # --- Safe session readers (do nothing if session has no uploads) ---
        SessionDirectoryReadTool(),
        SessionFileReadTool(),
    ]



# =============================================================================
# TOOL CONFIGURATION AND CACHING
# =============================================================================

def configure_tool_caching():
    """Configure caching for tools that support it"""
    # This would be implemented based on your specific caching requirements
    # CrewAI handles basic caching automatically, but you can customize it
    pass


if __name__ == "__main__":
    # Example usage - UPDATED TO INCLUDE CODE INTERPRETER
    print("Available CrewAI Tools:")
    print(f"Function-based tools: {len(FUNCTION_TOOLS)}")
    print(f"Class-based tools: {len(CLASS_TOOLS)}")
    print(f"Total tools: {len(ALL_TOOLS)}")
    
    # Test the code interpreter
    print("\nTesting Code Interpreter:")
    interpreter = CodeInterpreterTool()
    test_result = interpreter._run("print('Hello from Code Interpreter!')", 30)
    print(test_result)