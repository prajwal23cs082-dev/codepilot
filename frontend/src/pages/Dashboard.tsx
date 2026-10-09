import { useState, useEffect } from "react";
import { Link, useNavigate } from "react-router-dom";
import { Plus, Folder, Clock, CheckCircle, XCircle } from "lucide-react";
import axios from "axios";

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

interface Project {
  id: string;
  name: string;
  status: str;
  created_at: string;
}

export default function Dashboard() {
  const [projects, setProjects] = useState<Project[]>([]);
  const [showModal, setShowModal] = useState(false);
  const [newProjectName, setNewProjectName] = useState("");
  const navigate = useNavigate();

  useEffect(() => {
    fetchProjects();
  }, []);

  const fetchProjects = async () => {
    try {
      const res = await axios.get(`${API_URL}/projects`);
      setProjects(res.data);
    } catch (err) {
      console.error(err);
    }
  };

  const handleCreateProject = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newProjectName.trim()) return;
    
    try {
      const res = await axios.post(`${API_URL}/projects`, { name: newProjectName });
      setShowModal(false);
      setNewProjectName("");
      navigate(`/project/${res.data.id}`);
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <div className="p-8 max-w-6xl mx-auto">
      <div className="flex justify-between items-center mb-8">
        <div>
          <h1 className="text-3xl font-bold text-white mb-2">Dashboard</h1>
          <p className="text-[#8b949e]">Welcome to CodePilot. Select a project or create a new one to begin.</p>
        </div>
        <button 
          onClick={() => setShowModal(true)}
          className="bg-[#238636] hover:bg-[#2ea043] text-white px-4 py-2 rounded-md font-medium flex items-center gap-2 transition-colors"
        >
          <Plus size={18} />
          New Project
        </button>
      </div>

      {/* Stats row - placeholder values for now */}
      <div className="grid grid-cols-4 gap-4 mb-8">
        <div className="bg-[#161b22] border border-[#30363d] rounded-lg p-4">
          <div className="text-[#8b949e] text-sm font-medium mb-1">Total Projects</div>
          <div className="text-2xl font-bold text-white">{projects.length}</div>
        </div>
        <div className="bg-[#161b22] border border-[#30363d] rounded-lg p-4">
          <div className="text-[#8b949e] text-sm font-medium mb-1">Tasks Completed</div>
          <div className="text-2xl font-bold text-white">0</div>
        </div>
        <div className="bg-[#161b22] border border-[#30363d] rounded-lg p-4">
          <div className="text-[#8b949e] text-sm font-medium mb-1">Success Rate</div>
          <div className="text-2xl font-bold text-white">100%</div>
        </div>
        <div className="bg-[#161b22] border border-[#30363d] rounded-lg p-4">
          <div className="text-[#8b949e] text-sm font-medium mb-1">Avg. Iterations</div>
          <div className="text-2xl font-bold text-white">2.5</div>
        </div>
      </div>

      <h2 className="text-xl font-semibold text-white mb-4">Recent Projects</h2>
      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {projects.length === 0 ? (
          <div className="col-span-full py-12 text-center text-[#8b949e] border border-dashed border-[#30363d] rounded-lg">
            No projects found. Create one to get started.
          </div>
        ) : (
          projects.map(project => (
            <Link 
              key={project.id} 
              to={`/project/${project.id}`}
              className="bg-[#161b22] border border-[#30363d] rounded-lg p-5 hover:border-[#8b949e] transition-colors group"
            >
              <div className="flex items-start justify-between mb-3">
                <div className="flex items-center gap-2 text-blue-400 group-hover:text-blue-300">
                  <Folder size={20} />
                  <span className="font-semibold text-lg">{project.name}</span>
                </div>
              </div>
              <div className="flex items-center gap-4 text-sm text-[#8b949e]">
                <div className="flex items-center gap-1">
                  {project.status === "ready" ? <CheckCircle size={14} className="text-green-400"/> : 
                   project.status === "error" ? <XCircle size={14} className="text-red-400"/> : 
                   <Clock size={14} />}
                  <span className="capitalize">{project.status}</span>
                </div>
                <div className="flex items-center gap-1">
                  <span>{new Date(project.created_at).toLocaleDateString()}</span>
                </div>
              </div>
            </Link>
          ))
        )}
      </div>

      {showModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-[#161b22] border border-[#30363d] rounded-xl shadow-2xl w-full max-w-md overflow-hidden">
            <div className="p-4 border-b border-[#30363d] flex justify-between items-center bg-[#0d1117]">
              <h3 className="font-semibold text-white">Create New Project</h3>
              <button onClick={() => setShowModal(false)} className="text-[#8b949e] hover:text-white">
                <XCircle size={20} />
              </button>
            </div>
            <form onSubmit={handleCreateProject} className="p-6">
              <div className="mb-4">
                <label className="block text-sm font-medium text-[#c9d1d9] mb-2">Project Name</label>
                <input 
                  type="text" 
                  value={newProjectName}
                  onChange={e => setNewProjectName(e.target.value)}
                  className="w-full bg-[#0d1117] border border-[#30363d] rounded-md px-3 py-2 text-white focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500"
                  placeholder="e.g. FastAPI Auth Project"
                  autoFocus
                />
              </div>
              <div className="flex justify-end gap-3 mt-6">
                <button 
                  type="button" 
                  onClick={() => setShowModal(false)}
                  className="px-4 py-2 rounded-md bg-[#21262d] border border-[#30363d] text-white hover:bg-[#30363d] transition-colors"
                >
                  Cancel
                </button>
                <button 
                  type="submit"
                  disabled={!newProjectName.trim()}
                  className="px-4 py-2 rounded-md bg-[#238636] text-white font-medium hover:bg-[#2ea043] transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  Create
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
