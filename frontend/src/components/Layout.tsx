import { Outlet, NavLink } from "react-router-dom";
import { LayoutDashboard, FolderKanban, Activity } from "lucide-react";
import { clsx } from "clsx";

export default function Layout() {
  return (
    <div className="flex h-screen bg-[#0d1117] text-[#c9d1d9] font-sans">
      {/* Sidebar */}
      <div className="w-64 border-r border-[#30363d] bg-[#161b22] flex flex-col">
        <div className="p-4 border-b border-[#30363d] flex items-center gap-2">
          <div className="w-8 h-8 rounded bg-blue-600 flex items-center justify-center font-bold text-white">
            CP
          </div>
          <span className="font-semibold text-lg">CodePilot</span>
        </div>
        
        <nav className="flex-1 p-2 space-y-1">
          <NavLink
            to="/"
            className={({ isActive }) =>
              clsx(
                "flex items-center gap-3 px-3 py-2 rounded-md transition-colors",
                isActive ? "bg-[#1f6feb] text-white" : "hover:bg-[#30363d] text-[#8b949e] hover:text-[#c9d1d9]"
              )
            }
          >
            <LayoutDashboard size={18} />
            Dashboard
          </NavLink>
          
          <div className="px-3 pt-4 pb-2 text-xs font-semibold text-[#8b949e] uppercase tracking-wider">
            Workspace
          </div>
          
          {/* We will ideally fetch active projects and list them here, for now just a generic link */}
          <NavLink
            to="/project/new"
            className={({ isActive }) =>
              clsx(
                "flex items-center gap-3 px-3 py-2 rounded-md transition-colors",
                isActive ? "bg-[#1f6feb] text-white" : "hover:bg-[#30363d] text-[#8b949e] hover:text-[#c9d1d9]"
              )
            }
          >
            <FolderKanban size={18} />
            Projects
          </NavLink>

          <div className="px-3 pt-4 pb-2 text-xs font-semibold text-[#8b949e] uppercase tracking-wider">
            Metrics
          </div>
          <NavLink
            to="/evaluation"
            className={({ isActive }) =>
              clsx(
                "flex items-center gap-3 px-3 py-2 rounded-md transition-colors",
                isActive ? "bg-[#1f6feb] text-white" : "hover:bg-[#30363d] text-[#8b949e] hover:text-[#c9d1d9]"
              )
            }
          >
            <Activity size={18} />
            Evaluation
          </NavLink>
        </nav>
        
        <div className="p-4 border-t border-[#30363d] text-xs text-[#8b949e]">
          Autonomous AI Software Engineer
        </div>
      </div>
      
      {/* Main Content */}
      <div className="flex-1 flex flex-col overflow-hidden">
        <main className="flex-1 overflow-auto bg-[#0d1117]">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
