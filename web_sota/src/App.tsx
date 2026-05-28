import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AppLayout } from '@/components/layout/app-layout';
import { Dashboard } from '@/pages/dashboard';
import Hierarchy from '@/pages/hierarchy';
import ScriptConsole from '@/pages/script-console';
import AvatarPipeline from '@/pages/avatar-pipeline';
import PluginManager from '@/pages/plugin-manager';
import { Chat } from '@/pages/chat';
import { Settings } from '@/pages/settings';
import FleetMesh from '@/pages/mesh';
import { Tools } from '@/pages/tools';
import { Status } from '@/pages/status';
import { Apps } from '@/pages/apps';
import { AgentTools } from '@/pages/agent-tools';
import { Help } from '@/pages/help';

function App() {
  return (
    <Router>
      <AppLayout>
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/hierarchy" element={<Hierarchy />} />
          <Route path="/script-console" element={<ScriptConsole />} />
          <Route path="/avatar-pipeline" element={<AvatarPipeline />} />
          <Route path="/plugins" element={<PluginManager />} />
          <Route path="/chat" element={<Chat />} />
          <Route path="/tools" element={<Tools />} />
          <Route path="/mesh" element={<FleetMesh />} />
          <Route path="/status" element={<Status />} />
          <Route path="/apps" element={<Apps />} />
          <Route path="/agent-tools" element={<AgentTools />} />
          <Route path="/help" element={<Help />} />
          <Route path="/settings" element={<Settings />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </AppLayout>
    </Router>
  );
}

export default App;
