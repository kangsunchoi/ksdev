import "@/App.css";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import { Toaster } from "sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { Sidebar } from "@/components/Sidebar";
import Dashboard from "@/pages/Dashboard";
import NewProject from "@/pages/NewProject";
import ProjectDetail from "@/pages/ProjectDetail";
import TemplateLibrary from "@/pages/TemplateLibrary";

function App() {
  return (
    <TooltipProvider delayDuration={200}>
      <BrowserRouter>
        <div className="flex h-screen bg-background overflow-hidden">
          <Sidebar />
          <main className="flex-1 overflow-auto">
            <Routes>
              <Route path="/" element={<Dashboard />} />
              <Route path="/projects/new" element={<NewProject />} />
              <Route path="/projects/:id" element={<ProjectDetail />} />
              <Route path="/projects/:id/edit" element={<NewProject />} />
              <Route path="/templates" element={<TemplateLibrary />} />
            </Routes>
          </main>
        </div>
        <Toaster theme="dark" position="top-right" richColors closeButton />
      </BrowserRouter>
    </TooltipProvider>
  );
}

export default App;
