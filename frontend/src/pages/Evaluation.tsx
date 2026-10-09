import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, LineChart, Line } from 'recharts';
import { Activity, Target, Clock, Zap } from 'lucide-react';

const mockData = [
  { name: 'Task 1', success: 100, iterations: 2, time: 45 },
  { name: 'Task 2', success: 100, iterations: 1, time: 20 },
  { name: 'Task 3', success: 0, iterations: 5, time: 120 },
  { name: 'Task 4', success: 100, iterations: 3, time: 65 },
  { name: 'Task 5', success: 100, iterations: 2, time: 50 },
];

export default function Evaluation() {
  return (
    <div className="p-8 max-w-6xl mx-auto">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-white mb-2">Evaluation Metrics</h1>
        <p className="text-[#8b949e]">Performance and reliability metrics for CodePilot across benchmark tasks.</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        <div className="bg-[#161b22] border border-[#30363d] rounded-lg p-5">
          <div className="flex items-center gap-3 mb-2 text-[#8b949e]">
            <Target size={18} className="text-green-400" />
            <span className="font-semibold text-sm uppercase tracking-wider">Success Rate</span>
          </div>
          <div className="text-3xl font-bold text-white">80%</div>
          <div className="text-xs text-green-400 mt-1">↑ 5% from last week</div>
        </div>
        
        <div className="bg-[#161b22] border border-[#30363d] rounded-lg p-5">
          <div className="flex items-center gap-3 mb-2 text-[#8b949e]">
            <Activity size={18} className="text-blue-400" />
            <span className="font-semibold text-sm uppercase tracking-wider">Avg Iterations</span>
          </div>
          <div className="text-3xl font-bold text-white">2.6</div>
          <div className="text-xs text-[#8b949e] mt-1">Self-correction loops</div>
        </div>

        <div className="bg-[#161b22] border border-[#30363d] rounded-lg p-5">
          <div className="flex items-center gap-3 mb-2 text-[#8b949e]">
            <Clock size={18} className="text-yellow-400" />
            <span className="font-semibold text-sm uppercase tracking-wider">Avg Latency</span>
          </div>
          <div className="text-3xl font-bold text-white">60s</div>
          <div className="text-xs text-green-400 mt-1">↓ 12s improvement</div>
        </div>

        <div className="bg-[#161b22] border border-[#30363d] rounded-lg p-5">
          <div className="flex items-center gap-3 mb-2 text-[#8b949e]">
            <Zap size={18} className="text-purple-400" />
            <span className="font-semibold text-sm uppercase tracking-wider">Tool Accuracy</span>
          </div>
          <div className="text-3xl font-bold text-white">92%</div>
          <div className="text-xs text-[#8b949e] mt-1">Valid tool calls</div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-[#161b22] border border-[#30363d] rounded-lg p-6">
          <h3 className="text-lg font-semibold text-white mb-6">Task Completion Time (s)</h3>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={mockData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#30363d" />
                <XAxis dataKey="name" stroke="#8b949e" />
                <YAxis stroke="#8b949e" />
                <Tooltip 
                  contentStyle={{ backgroundColor: '#0d1117', borderColor: '#30363d', color: '#c9d1d9' }}
                  itemStyle={{ color: '#58a6ff' }}
                />
                <Bar dataKey="time" fill="#1f6feb" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="bg-[#161b22] border border-[#30363d] rounded-lg p-6">
          <h3 className="text-lg font-semibold text-white mb-6">Iterations per Task</h3>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={mockData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#30363d" />
                <XAxis dataKey="name" stroke="#8b949e" />
                <YAxis stroke="#8b949e" />
                <Tooltip 
                  contentStyle={{ backgroundColor: '#0d1117', borderColor: '#30363d', color: '#c9d1d9' }}
                />
                <Line type="monotone" dataKey="iterations" stroke="#3fb950" strokeWidth={3} dot={{ r: 6, fill: '#0d1117', stroke: '#3fb950', strokeWidth: 2 }} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>
    </div>
  );
}
