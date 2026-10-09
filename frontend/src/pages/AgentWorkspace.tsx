import { useState, useEffect, useRef } from "react";
import { useParams } from "react-router-dom";
import { Play, Square, FileCode, Search, Code, CheckCircle, XCircle, Wrench, FileDiff, Cpu, ChevronDown, ChevronRight } from "lucide-react";
import axios from "axios";

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

interface Task {
  id: string;
  project_id: string;
  description: string;
  status: string;
}

interface TraceStep {
  type: string;
  content: string;
  created_at: string;
}

interface Trace {
  run_id: string;
  status: string;
  iterations: number;
  steps: TraceStep[];
}

export default function AgentWorkspace() {
  const { taskId } = useParams();
  const [task, setTask] = useState<Task | null>(null);
  const [traces, setTraces] = useState<Trace[]>([]);
  const [isPolling, setIsPolling] = useState(false);
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    fetchTask();
    fetchTrace();
  }, [taskId]);

  useEffect(() => {
    let interval: number;
    if (isPolling) {
      interval = window.setInterval(fetchTrace, 2000);
    }
    return () => window.clearInterval(interval);
  }, [isPolling, taskId]);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [traces]);

  const fetchTask = async () => {
    try {
      const res = await axios.get(`${API_URL}/tasks/${taskId}`);
      setTask(res.data);
      if (res.data.status === 'running') {
        setIsPolling(true);
      } else {
        setIsPolling(false);
      }
    } catch (err) {
      console.error(err);
    }
  };

  const fetchTrace = async () => {
    try {
      const res = await axios.get(`${API_URL}/tasks/${taskId}/trace`);
      setTraces(res.data.traces || []);
      
      // If the latest run is completed or failed, stop polling and update task status
      const latest = res.data.traces[res.data.traces.length - 1];
      if (latest && (latest.status === 'completed' || latest.status === 'failed')) {
        setIsPolling(false);
        fetchTask();
      }
    } catch (err) {
      console.error(err);
    }
  };

  const handleStart = async () => {
    try {
      await axios.post(`${API_URL}/tasks/${taskId}/start`);
      fetchTask();
      setIsPolling(true);
    } catch (err) {
      console.error(err);
      alert("Failed to start agent");
    }
  };

  const getStepIcon = (type: string) => {
    switch (type) {
      case 'planner': return <FileCode size={16} className="text-purple-400" />;
      case 'coder': return <Code size={16} className="text-blue-400" />;
      case 'tools': return <Wrench size={16} className="text-orange-400" />;
      case 'tester': return <CheckCircle size={16} className="text-green-400" />;
      case 'debugger': return <Search size={16} className="text-red-400" />;
      default: return <Cpu size={16} className="text-gray-400" />;
    }
  };

  if (!task) return <div className="p-8 text-white">Loading...</div>;

  const currentTrace = traces[traces.length - 1];

  return (
    <div className="flex flex-col h-full bg-[#0d1117]">
      {/* Header */}
      <div className="flex-none p-4 border-b border-[#30363d] bg-[#161b22] flex justify-between items-center">
        <div>
          <h1 className="text-xl font-bold text-white mb-1">Agent Workspace</h1>
          <p className="text-sm text-[#8b949e] truncate max-w-2xl">{task.description}</p>
        </div>
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2 text-sm font-medium">
            Status: 
            <span className={`px-2 py-1 rounded-full text-xs ${
              task.status === 'completed' ? 'bg-green-900 text-green-300' :
              task.status === 'failed' ? 'bg-red-900 text-red-300' :
              task.status === 'running' ? 'bg-blue-900 text-blue-300' :
              'bg-[#30363d] text-[#c9d1d9]'
            }`}>
              {task.status.toUpperCase()}
            </span>
          </div>
          
          {task.status === 'pending' && (
            <button 
              onClick={handleStart}
              className="bg-[#238636] hover:bg-[#2ea043] text-white px-4 py-2 rounded-md font-medium flex items-center gap-2 transition-colors"
            >
              <Play size={16} /> Start Agent
            </button>
          )}
          {task.status === 'running' && (
            <button 
              disabled
              className="bg-[#21262d] border border-[#30363d] text-white px-4 py-2 rounded-md font-medium flex items-center gap-2 opacity-70 cursor-not-allowed"
            >
              <span className="animate-spin mr-1">⚪</span> Running...
            </button>
          )}
        </div>
      </div>

      {/* Main Layout */}
      <div className="flex-1 flex overflow-hidden">
        {/* Left/Center Column: Agent Trace & Logs */}
        <div className="flex-1 flex flex-col border-r border-[#30363d]">
          <div className="p-3 bg-[#0d1117] border-b border-[#30363d] font-semibold text-white flex items-center gap-2">
            <Cpu size={18} /> Agent Execution Trace
          </div>
          
          <div ref={scrollRef} className="flex-1 overflow-auto p-4 space-y-4">
            {currentTrace ? (
              <div className="space-y-4">
                {currentTrace.steps.map((step, idx) => (
                  <div key={idx} className="bg-[#161b22] border border-[#30363d] rounded-lg overflow-hidden">
                    <div className="px-4 py-2 bg-[#21262d] border-b border-[#30363d] flex items-center gap-3">
                      {getStepIcon(step.type)}
                      <span className="font-semibold text-[#c9d1d9] capitalize">{step.type} Phase</span>
                      <span className="text-xs text-[#8b949e] ml-auto">
                        {new Date(step.created_at).toLocaleTimeString()}
                      </span>
                    </div>
                    <div className="p-4 font-mono text-sm text-[#e6edf3] whitespace-pre-wrap">
                      {step.content.replace(/^"|"$/g, '')}
                    </div>
                  </div>
                ))}
                {task.status === 'running' && (
                  <div className="flex items-center justify-center p-4 text-[#8b949e] gap-2">
                    <span className="animate-pulse">●</span>
                    <span className="animate-pulse animation-delay-200">●</span>
                    <span className="animate-pulse animation-delay-400">●</span>
                  </div>
                )}
              </div>
            ) : (
              <div className="h-full flex items-center justify-center text-[#8b949e]">
                {task.status === 'pending' ? 'Click "Start Agent" to begin execution.' : 'No trace data available.'}
              </div>
            )}
          </div>
        </div>

        {/* Right Column: Code Diff / Current State */}
        <div className="w-1/3 flex flex-col bg-[#0d1117]">
          <div className="p-3 bg-[#0d1117] border-b border-[#30363d] font-semibold text-white flex items-center gap-2">
            <FileDiff size={18} /> Current Changes
          </div>
          <div className="flex-1 overflow-auto p-4">
            <div className="text-[#8b949e] text-sm text-center mt-10">
              {/* In a complete implementation, this would show real-time git diff */}
              Diff viewer would appear here.
              <br/><br/>
              The agent modifies files directly in the isolated workspace.
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
