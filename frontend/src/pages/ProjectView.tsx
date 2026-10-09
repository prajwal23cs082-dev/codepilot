import { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { Folder, File, Code, UploadCloud, Link as LinkIcon, CheckCircle, Database } from "lucide-react";
import axios from "axios";

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

interface Project {
  id: string;
  name: string;
  status: string;
  repository_url: string | null;
}

interface FileNode {
  name: string;
  path: string;
  type: "file" | "directory";
  children?: FileNode[];
}

export default function ProjectView() {
  const { projectId } = useParams();
  const navigate = useNavigate();
  const [project, setProject] = useState<Project | null>(null);
  const [fileTree, setFileTree] = useState<FileNode[]>([]);
  const [repoUrl, setRepoUrl] = useState("");
  const [uploadFile, setUploadFile] = useState<File | null>(null);
  const [taskDescription, setTaskDescription] = useState("");
  const [isAttaching, setIsAttaching] = useState(false);
  const [isIndexing, setIsIndexing] = useState(false);

  useEffect(() => {
    fetchProject();
  }, [projectId]);

  const fetchProject = async () => {
    try {
      const res = await axios.get(`${API_URL}/projects/${projectId}`);
      setProject(res.data);
      if (res.data.status !== 'created') {
        fetchFileTree();
      }
    } catch (err) {
      console.error(err);
    }
  };

  const fetchFileTree = async () => {
    try {
      const res = await axios.get(`${API_URL}/projects/${projectId}/repository/tree`);
      setFileTree(res.data.tree || []);
    } catch (err) {
      console.error(err);
    }
  };

  const handleAttachRepo = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!repoUrl && !uploadFile) return;
    
    setIsAttaching(true);
    const formData = new FormData();
    if (repoUrl) formData.append("repository_url", repoUrl);
    if (uploadFile) formData.append("file", uploadFile);

    try {
      await axios.post(`${API_URL}/projects/${projectId}/repository`, formData);
      fetchProject();
    } catch (err) {
      console.error(err);
      alert("Failed to attach repository");
    } finally {
      setIsAttaching(false);
    }
  };

  const handleIndex = async () => {
    setIsIndexing(true);
    try {
      await axios.post(`${API_URL}/projects/${projectId}/repository/index`);
      fetchProject();
    } catch (err) {
      console.error(err);
      alert("Failed to index repository");
    } finally {
      setIsIndexing(false);
    }
  };

  const handleCreateTask = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!taskDescription.trim()) return;
    
    try {
      const res = await axios.post(`${API_URL}/projects/${projectId}/tasks`, {
        description: taskDescription
      });
      navigate(`/task/${res.data.id}`);
    } catch (err) {
      console.error(err);
    }
  };

  const renderTree = (nodes: FileNode[]) => {
    return (
      <ul className="pl-4 space-y-1">
        {nodes.map((node) => (
          <li key={node.path} className="text-sm">
            <div className="flex items-center gap-2 text-[#8b949e] py-1 hover:text-[#c9d1d9] cursor-pointer">
              {node.type === 'directory' ? <Folder size={14} className="text-blue-400" /> : <File size={14} />}
              {node.name}
            </div>
            {node.children && renderTree(node.children)}
          </li>
        ))}
      </ul>
    );
  };

  if (!project) return <div className="p-8 text-white">Loading...</div>;

  return (
    <div className="p-8 max-w-6xl mx-auto flex flex-col md:flex-row gap-8">
      {/* Left Column: Repo & Indexing */}
      <div className="flex-1 space-y-6">
        <div>
          <h1 className="text-3xl font-bold text-white mb-2">{project.name}</h1>
          <div className="flex items-center gap-2 text-sm">
            <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${
              project.status === 'ready' ? 'bg-green-900 text-green-300' :
              project.status === 'created' ? 'bg-yellow-900 text-yellow-300' :
              'bg-blue-900 text-blue-300'
            }`}>
              {project.status.toUpperCase()}
            </span>
          </div>
        </div>

        {project.status === 'created' ? (
          <div className="bg-[#161b22] border border-[#30363d] rounded-lg p-6">
            <h2 className="text-xl font-semibold text-white mb-4 flex items-center gap-2">
              <UploadCloud size={20} /> Attach Repository
            </h2>
            <form onSubmit={handleAttachRepo} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-[#c9d1d9] mb-1">GitHub URL</label>
                <div className="flex rounded-md shadow-sm">
                  <span className="inline-flex items-center px-3 rounded-l-md border border-r-0 border-[#30363d] bg-[#0d1117] text-[#8b949e]">
                    <LinkIcon size={14} />
                  </span>
                  <input
                    type="url"
                    value={repoUrl}
                    onChange={(e) => setRepoUrl(e.target.value)}
                    disabled={!!uploadFile}
                    className="flex-1 block w-full rounded-none rounded-r-md bg-[#0d1117] border border-[#30363d] px-3 py-2 text-white focus:outline-none focus:border-blue-500"
                    placeholder="https://github.com/user/repo.git"
                  />
                </div>
              </div>
              <div className="text-center text-sm text-[#8b949e]">OR</div>
              <div>
                <label className="block text-sm font-medium text-[#c9d1d9] mb-1">Upload ZIP</label>
                <input
                  type="file"
                  accept=".zip"
                  onChange={(e) => setUploadFile(e.target.files ? e.target.files[0] : null)}
                  disabled={!!repoUrl}
                  className="block w-full text-sm text-[#8b949e] file:mr-4 file:py-2 file:px-4 file:rounded-md file:border-0 file:text-sm file:font-semibold file:bg-[#21262d] file:text-white hover:file:bg-[#30363d] cursor-pointer border border-[#30363d] rounded-md p-1 bg-[#0d1117]"
                />
              </div>
              <button
                type="submit"
                disabled={isAttaching || (!repoUrl && !uploadFile)}
                className="w-full bg-[#238636] hover:bg-[#2ea043] text-white px-4 py-2 rounded-md font-medium transition-colors disabled:opacity-50"
              >
                {isAttaching ? 'Attaching...' : 'Attach Repository'}
              </button>
            </form>
          </div>
        ) : (
          <div className="bg-[#161b22] border border-[#30363d] rounded-lg p-6 space-y-6">
            <div>
              <h2 className="text-xl font-semibold text-white mb-2 flex items-center gap-2">
                <Database size={20} /> Repository Indexing
              </h2>
              <p className="text-sm text-[#8b949e] mb-4">
                CodePilot needs to index the repository to understand the codebase and perform RAG-based context retrieval.
              </p>
              <button
                onClick={handleIndex}
                disabled={isIndexing}
                className="bg-[#21262d] border border-[#30363d] hover:bg-[#30363d] text-white px-4 py-2 rounded-md font-medium transition-colors disabled:opacity-50"
              >
                {isIndexing ? 'Indexing in progress...' : 'Build Code Index'}
              </button>
            </div>

            <div className="border-t border-[#30363d] pt-6">
              <h2 className="text-xl font-semibold text-white mb-4 flex items-center gap-2">
                <Code size={20} /> Create New Task
              </h2>
              <form onSubmit={handleCreateTask} className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-[#c9d1d9] mb-1">Task Description</label>
                  <textarea
                    value={taskDescription}
                    onChange={(e) => setTaskDescription(e.target.value)}
                    rows={4}
                    className="w-full bg-[#0d1117] border border-[#30363d] rounded-md px-3 py-2 text-white focus:outline-none focus:border-blue-500"
                    placeholder="e.g. Add JWT authentication to this FastAPI project. The user model is in models.py..."
                    required
                  />
                </div>
                <button
                  type="submit"
                  disabled={!taskDescription.trim()}
                  className="w-full bg-[#1f6feb] hover:bg-[#388bfd] text-white px-4 py-2 rounded-md font-medium transition-colors disabled:opacity-50"
                >
                  Start CodePilot Agent
                </button>
              </form>
            </div>
          </div>
        )}
      </div>

      {/* Right Column: File Tree */}
      <div className="w-full md:w-80 flex-shrink-0">
        <div className="bg-[#161b22] border border-[#30363d] rounded-lg flex flex-col h-[calc(100vh-6rem)]">
          <div className="p-4 border-b border-[#30363d] bg-[#0d1117] rounded-t-lg">
            <h3 className="font-semibold text-white flex items-center gap-2">
              <Folder size={18} /> File Explorer
            </h3>
          </div>
          <div className="p-2 overflow-auto flex-1 font-mono text-sm">
            {fileTree.length > 0 ? renderTree(fileTree) : (
              <div className="p-4 text-center text-[#8b949e]">
                No files found. Attach a repository first.
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
