import {
  Navigate,
  Route,
  BrowserRouter as Router,
  Routes,
} from "react-router-dom";
import { AppLayout } from "@/components/layout/app-layout";
import { AgentTools } from "@/pages/agent-tools";
import { Apps } from "@/pages/apps";
import AvatarPipeline from "@/pages/avatar-pipeline";
import { Chat } from "@/pages/chat";
import { Dashboard } from "@/pages/dashboard";
import { Help } from "@/pages/help";
import Hierarchy from "@/pages/hierarchy";
import Logging from "@/pages/Logging";
import FleetMesh from "@/pages/mesh";
import PluginManager from "@/pages/plugin-manager";
import ScriptConsole from "@/pages/script-console";
import { Settings } from "@/pages/settings";
import { Status } from "@/pages/status";
import { Tools } from "@/pages/tools";

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
          <Route path="/logs" element={<Logging />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </AppLayout>
    </Router>
  );
}

export default App;
