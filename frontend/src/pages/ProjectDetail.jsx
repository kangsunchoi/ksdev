import { useState, useEffect, useCallback, useMemo } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { toast } from "sonner";
import { api } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { ScrollArea } from "@/components/ui/scroll-area";
import {
  CheckCircle2, AlertTriangle, Info, XCircle, Copy, Download, Pencil,
  Play, ShieldCheck, Loader2, Trash2, FileText, FileJson, FileCode, History
} from "lucide-react";

const statusMap = {
  draft: { label: "Draft", class: "bg-zinc-700 text-zinc-300" },
  validated: { label: "Validated", class: "bg-amber-600/20 text-amber-400 border border-amber-600/30" },
  generated: { label: "Generated", class: "bg-emerald-600/20 text-emerald-400 border border-emerald-600/30" },
};

const platformLabels = {
  ie3300: "IE3300", ie3400: "IE3400", ie9320: "IE9320",
  catalyst_9200: "Cat9200", catalyst_9300: "Cat9300", catalyst_9500: "Cat9500",
  wlc_9800: "WLC9800",
};

export default function ProjectDetail() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [project, setProject] = useState(null);
  const [loading, setLoading] = useState(true);
  const [validating, setValidating] = useState(false);
  const [generating, setGenerating] = useState(false);
  const [tab, setTab] = useState("clean");

  const fetchProject = useCallback(async () => {
    try {
      setLoading(true);
      const res = await api.getProject(id);
      setProject(res.data);
    } catch {
      toast.error("Failed to load project");
      navigate("/");
    } finally {
      setLoading(false);
    }
  }, [id, navigate]);

  useEffect(() => { fetchProject(); }, [fetchProject]);

  const handleValidate = async () => {
    setValidating(true);
    try {
      const res = await api.validateProject(id);
      setProject(prev => ({ ...prev, validation_results: res.data.findings, status: res.data.status }));
      const s = res.data.summary;
      if (s.errors > 0) toast.error(`Validation: ${s.errors} error(s), ${s.warnings} warning(s)`);
      else if (s.warnings > 0) toast.warning(`Validation passed with ${s.warnings} warning(s)`);
      else toast.success("Validation passed. Ready to generate.");
    } catch (e) {
      toast.error("Validation failed: " + (e.response?.data?.detail || e.message));
    } finally {
      setValidating(false);
    }
  };

  const handleGenerate = async () => {
    setGenerating(true);
    try {
      const res = await api.generateConfig(id);
      if (res.data.status === "validation_failed") {
        toast.error(res.data.message);
        setProject(prev => ({ ...prev, validation_results: res.data.findings }));
      } else {
        setProject(prev => ({ ...prev, generated_config: res.data.config, status: "generated", validation_results: res.data.findings }));
        setTab("clean");
        toast.success("Configuration generated successfully");
      }
    } catch (e) {
      toast.error("Generation failed: " + (e.response?.data?.detail || e.message));
    } finally {
      setGenerating(false);
    }
  };

  const handleExport = async (format) => {
    try {
      const res = await api.exportProject(id, format);
      const { content, filename } = res.data;
      const blob = new Blob([content], { type: "text/plain" });
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = filename;
      a.click();
      URL.revokeObjectURL(url);
      toast.success(`Exported as ${format.toUpperCase()}`);
    } catch (e) {
      toast.error("Export failed: " + (e.response?.data?.detail || e.message));
    }
  };

  const handleDelete = async () => {
    if (!window.confirm("Delete this project? This cannot be undone.")) return;
    try {
      await api.deleteProject(id);
      toast.success("Project deleted");
      navigate("/");
    } catch (e) {
      toast.error("Delete failed");
    }
  };

  const copyToClipboard = (text) => {
    navigator.clipboard.writeText(text);
    toast.success("Copied to clipboard");
  };

  if (loading) return <div className="p-6 text-sm text-zinc-500">Loading project...</div>;
  if (!project) return <div className="p-6 text-sm text-zinc-500">Project not found.</div>;

  const config = project.generated_config;
  const findings = project.validation_results || [];
  const errors = findings.filter(f => f.severity === "error");
  const warnings = findings.filter(f => f.severity === "warning");
  const infos = findings.filter(f => f.severity === "info");

  return (
    <div className="flex flex-col h-full" data-testid="project-detail">
      <ProjectHeader project={project} navigate={navigate} id={id}
        onValidate={handleValidate} validating={validating}
        onGenerate={handleGenerate} generating={generating}
        onDelete={handleDelete} />

      <div className="flex-1 flex overflow-hidden">
        <div className="flex-1 flex flex-col overflow-hidden">
          <Tabs value={tab} onValueChange={setTab} className="flex-1 flex flex-col overflow-hidden">
            <TabBar tab={tab} findingsCount={findings.length} />

            <CleanConfigTab config={config} copyToClipboard={copyToClipboard} />
            <AnnotatedConfigTab config={config} copyToClipboard={copyToClipboard} />
            <ValidationTab findings={findings} errors={errors} warnings={warnings} infos={infos} />
            <ChecklistTab config={config} />
            <RevisionsTab project={project} />
            <ExportTab config={config} onExport={handleExport} />
          </Tabs>
        </div>
      </div>
    </div>
  );
}

function ProjectHeader({ project, navigate, id, onValidate, validating, onGenerate, generating, onDelete }) {
  return (
    <div className="h-14 border-b border-border flex items-center justify-between px-6 shrink-0">
      <div className="flex items-center gap-3">
        <h1 className="text-sm font-semibold text-zinc-200">{project.name || "Unnamed Project"}</h1>
        <Badge className={`text-[10px] px-1.5 py-0 ${statusMap[project.status]?.class || statusMap.draft.class}`}>
          {statusMap[project.status]?.label || "Draft"}
        </Badge>
        <span className="text-xs text-zinc-500 font-mono">
          {platformLabels[project.device?.platform_family]} | {project.device?.hostname}
        </span>
      </div>
      <div className="flex gap-2 mr-32 relative z-50">
        <Button variant="outline" size="sm" className="h-8 text-xs" onClick={() => navigate(`/projects/${id}/edit`)} data-testid="edit-project-btn">
          <Pencil className="w-3.5 h-3.5 mr-1" /> Edit
        </Button>
        <Button variant="outline" size="sm" className="h-8 text-xs" onClick={onValidate} disabled={validating} data-testid="validate-btn">
          {validating ? <Loader2 className="w-3.5 h-3.5 mr-1 animate-spin" /> : <ShieldCheck className="w-3.5 h-3.5 mr-1" />}
          Validate
        </Button>
        <Button size="sm" className="h-8 text-xs bg-blue-600 hover:bg-blue-700 text-white" onClick={onGenerate} disabled={generating} data-testid="generate-btn">
          {generating ? <Loader2 className="w-3.5 h-3.5 mr-1 animate-spin" /> : <Play className="w-3.5 h-3.5 mr-1" />}
          Generate
        </Button>
        <Button variant="outline" size="sm" className="h-8 text-xs text-red-400 hover:text-red-300 hover:border-red-400/50" onClick={onDelete} data-testid="delete-project-btn">
          <Trash2 className="w-3.5 h-3.5" />
        </Button>
      </div>
    </div>
  );
}

function TabBar({ findingsCount }) {
  return (
    <div className="border-b border-border px-6 pt-2">
      <TabsList className="bg-transparent h-8 p-0 gap-0">
        <TabsTrigger value="clean" className="text-xs h-8 rounded-none border-b-2 border-transparent data-[state=active]:border-blue-500 data-[state=active]:bg-transparent data-[state=active]:text-blue-400" data-testid="tab-clean">
          Clean Config
        </TabsTrigger>
        <TabsTrigger value="annotated" className="text-xs h-8 rounded-none border-b-2 border-transparent data-[state=active]:border-blue-500 data-[state=active]:bg-transparent data-[state=active]:text-blue-400" data-testid="tab-annotated">
          Annotated
        </TabsTrigger>
        <TabsTrigger value="validation" className="text-xs h-8 rounded-none border-b-2 border-transparent data-[state=active]:border-blue-500 data-[state=active]:bg-transparent data-[state=active]:text-blue-400" data-testid="tab-validation">
          Validation {findingsCount > 0 && <span className="ml-1 text-[10px]">({findingsCount})</span>}
        </TabsTrigger>
        <TabsTrigger value="checklist" className="text-xs h-8 rounded-none border-b-2 border-transparent data-[state=active]:border-blue-500 data-[state=active]:bg-transparent data-[state=active]:text-blue-400" data-testid="tab-checklist">
          Checklist
        </TabsTrigger>
        <TabsTrigger value="revisions" className="text-xs h-8 rounded-none border-b-2 border-transparent data-[state=active]:border-blue-500 data-[state=active]:bg-transparent data-[state=active]:text-blue-400" data-testid="tab-revisions">
          Revisions
        </TabsTrigger>
        <TabsTrigger value="export" className="text-xs h-8 rounded-none border-b-2 border-transparent data-[state=active]:border-blue-500 data-[state=active]:bg-transparent data-[state=active]:text-blue-400" data-testid="tab-export">
          Export
        </TabsTrigger>
      </TabsList>
    </div>
  );
}

function CleanConfigTab({ config, copyToClipboard }) {
  return (
    <TabsContent value="clean" className="flex-1 overflow-hidden m-0">
      {config?.clean_config ? (
        <div className="relative h-full">
          <Button variant="outline" size="sm" className="absolute top-3 right-3 z-10 h-7 text-xs" onClick={() => copyToClipboard(config.clean_config)} data-testid="copy-clean-config-btn">
            <Copy className="w-3 h-3 mr-1" /> Copy
          </Button>
          <ScrollArea className="h-full">
            <pre className="config-output m-4 min-h-full" data-testid="clean-config-output">{config.clean_config}</pre>
          </ScrollArea>
        </div>
      ) : (
        <EmptyState message="No config generated yet. Click 'Generate' to create configuration." />
      )}
    </TabsContent>
  );
}

function AnnotatedConfigTab({ config, copyToClipboard }) {
  return (
    <TabsContent value="annotated" className="flex-1 overflow-hidden m-0">
      {config?.annotated_config ? (
        <div className="relative h-full">
          <Button variant="outline" size="sm" className="absolute top-3 right-3 z-10 h-7 text-xs" onClick={() => copyToClipboard(config.annotated_config)} data-testid="copy-annotated-btn">
            <Copy className="w-3 h-3 mr-1" /> Copy
          </Button>
          <ScrollArea className="h-full">
            <pre className="config-output m-4 min-h-full" data-testid="annotated-config-output">
              {config.annotated_config.split("\n").map((line, i) => (
                <span key={i} className={getAnnotationClass(line)}>
                  {line}{"\n"}
                </span>
              ))}
            </pre>
          </ScrollArea>
        </div>
      ) : (
        <EmptyState message="No annotated config available. Generate config first." />
      )}
    </TabsContent>
  );
}

function getAnnotationClass(line) {
  if (line.startsWith("! >>")) return "text-blue-400";
  if (line.startsWith("!")) return "text-zinc-600";
  return "";
}

function ValidationTab({ findings, errors, warnings, infos }) {
  return (
    <TabsContent value="validation" className="flex-1 overflow-hidden m-0">
      <ScrollArea className="h-full">
        <div className="p-4 space-y-2" data-testid="validation-results">
          {findings.length === 0 ? (
            <EmptyState message="No validation results. Click 'Validate' to check your configuration." />
          ) : (
            <>
              <div className="flex gap-3 mb-4 text-xs">
                <span className="text-red-400">{errors.length} error(s)</span>
                <span className="text-amber-400">{warnings.length} warning(s)</span>
                <span className="text-blue-400">{infos.length} info(s)</span>
              </div>
              {findings.map((f, i) => (
                <FindingRow key={`${f.severity}-${f.field}-${i}`} finding={f} />
              ))}
            </>
          )}
        </div>
      </ScrollArea>
    </TabsContent>
  );
}

function ChecklistTab({ config }) {
  return (
    <TabsContent value="checklist" className="flex-1 overflow-hidden m-0">
      <ScrollArea className="h-full">
        <div className="p-4 space-y-2" data-testid="checklist-output">
          {config?.checklist?.length > 0 ? (
            config.checklist.map((c, i) => (
              <div key={`${c.section}-${c.type}-${i}`} className="flex gap-3 p-2 border border-border rounded-sm text-sm" data-testid={`checklist-item-${i}`}>
                <div className="shrink-0 mt-0.5">
                  {c.type === "action_required" ? (
                    <AlertTriangle className="w-4 h-4 text-amber-400" />
                  ) : (
                    <CheckCircle2 className="w-4 h-4 text-blue-400" />
                  )}
                </div>
                <div>
                  <div className="text-xs text-zinc-500 font-medium">{c.section}</div>
                  <div className="text-sm text-zinc-300">{c.item}</div>
                </div>
              </div>
            ))
          ) : (
            <EmptyState message="No checklist available. Generate config first." />
          )}
        </div>
      </ScrollArea>
    </TabsContent>
  );
}

function ExportTab({ config, onExport }) {
  return (
    <TabsContent value="export" className="flex-1 overflow-hidden m-0">
      <div className="p-6 space-y-4" data-testid="export-panel">
        <h3 className="text-sm font-medium text-zinc-300">Export Project</h3>
        <div className="grid grid-cols-3 gap-3">
          <ExportCard icon={FileText} label="Clean Config (TXT)" desc="CLI commands only, ready for paste" format="txt" onClick={onExport} disabled={!config} />
          <ExportCard icon={FileJson} label="Project (JSON)" desc="Full project data with all settings" format="json" onClick={onExport} />
          <ExportCard icon={FileCode} label="Project (YAML)" desc="Full project data in YAML format" format="yaml" onClick={onExport} />
        </div>
        <div className="text-xs text-zinc-600 mt-4">
          DOCX and PDF export will be available in a future release.
        </div>
      </div>
    </TabsContent>
  );
}

function RevisionsTab({ project }) {
  const revisions = useMemo(() => {
    const list = (project?.revisions || []).slice();
    list.reverse(); // newest first
    return list;
  }, [project]);

  const [selectedId, setSelectedId] = useState(null);
  const selected = useMemo(
    () => revisions.find(r => r.id === selectedId) || revisions[0],
    [revisions, selectedId]
  );

  const diffRows = useMemo(() => {
    if (!selected) return [];
    return buildProjectDiff(selected.snapshot, project);
  }, [selected, project]);

  return (
    <TabsContent value="revisions" className="flex-1 overflow-hidden m-0">
      <div className="h-full flex" data-testid="revisions-panel">
        <div className="w-72 border-r border-border overflow-hidden flex flex-col shrink-0">
          <div className="px-3 py-2 border-b border-border flex items-center gap-2 text-xs text-zinc-400">
            <History className="w-3.5 h-3.5" />
            <span>{revisions.length} revision(s)</span>
          </div>
          <ScrollArea className="flex-1">
            <div className="p-1.5 space-y-1">
              {revisions.length === 0 && (
                <div className="text-xs text-zinc-600 p-3">No revisions yet. Updates to this project will be tracked here.</div>
              )}
              {revisions.map((r, i) => (
                <button
                  key={r.id}
                  onClick={() => setSelectedId(r.id)}
                  data-testid={`revision-item-${i}`}
                  className={`w-full text-left px-2 py-1.5 rounded-sm text-xs btn-transition border ${
                    (selected?.id === r.id)
                      ? "bg-blue-500/10 border-blue-500/30 text-blue-300"
                      : "border-transparent text-zinc-400 hover:bg-zinc-800/40"
                  }`}
                >
                  <div className="font-mono text-[11px] text-zinc-500">#{revisions.length - i}</div>
                  <div className="text-[11px]">
                    {r.timestamp ? new Date(r.timestamp).toLocaleString() : "—"}
                  </div>
                  <div className="text-[10px] text-zinc-600 mt-0.5 truncate">
                    {r.snapshot?.name || "Unnamed snapshot"}
                  </div>
                </button>
              ))}
            </div>
          </ScrollArea>
        </div>
        <div className="flex-1 overflow-hidden flex flex-col">
          <div className="px-4 py-2 border-b border-border flex items-center justify-between text-xs">
            <div className="text-zinc-400">
              {selected ? (
                <>Comparing <span className="text-amber-400 font-mono">revision {new Date(selected.timestamp).toLocaleString()}</span> → <span className="text-emerald-400 font-mono">current</span></>
              ) : (
                <>Select a revision on the left to see changes.</>
              )}
            </div>
            {selected && (
              <div className="flex gap-3 text-[11px]">
                <span className="text-emerald-400">+{diffRows.filter(r => r.kind === "add").length} added</span>
                <span className="text-red-400">-{diffRows.filter(r => r.kind === "remove").length} removed</span>
                <span className="text-amber-400">~{diffRows.filter(r => r.kind === "change").length} changed</span>
              </div>
            )}
          </div>
          <ScrollArea className="flex-1">
            <div className="p-3" data-testid="revision-diff">
              {!selected && (
                <EmptyState message="No revision selected." />
              )}
              {selected && diffRows.length === 0 && (
                <div className="text-xs text-zinc-500 p-2">No differences detected between this revision and the current project.</div>
              )}
              {selected && diffRows.length > 0 && (
                <div className="border border-border rounded-sm overflow-hidden">
                  <table className="w-full dense-table text-xs">
                    <thead>
                      <tr className="bg-card border-b border-border text-[10px] text-zinc-500 uppercase">
                        <th className="text-left px-3 py-1.5 w-12">Op</th>
                        <th className="text-left px-3 py-1.5">Field</th>
                        <th className="text-left px-3 py-1.5">Previous</th>
                        <th className="text-left px-3 py-1.5">Current</th>
                      </tr>
                    </thead>
                    <tbody>
                      {diffRows.map((r, i) => (
                        <DiffRow key={`${r.path}-${i}`} row={r} />
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </div>
          </ScrollArea>
        </div>
      </div>
    </TabsContent>
  );
}

const DIFF_OP_STYLE = {
  add: { sign: "+", color: "text-emerald-400" },
  remove: { sign: "-", color: "text-red-400" },
  change: { sign: "~", color: "text-amber-400" },
};

function DiffRow({ row }) {
  const cfg = DIFF_OP_STYLE[row.kind] || DIFF_OP_STYLE.change;
  return (
    <tr className="border-b border-border/60 hover:bg-zinc-800/30" data-testid={`diff-row-${row.kind}`}>
      <td className={`px-3 py-1.5 font-mono font-bold ${cfg.color}`}>{cfg.sign}</td>
      <td className="px-3 py-1.5 font-mono text-zinc-400">{row.path}</td>
      <td className="px-3 py-1.5 font-mono text-zinc-500 break-all">{row.before}</td>
      <td className="px-3 py-1.5 font-mono text-zinc-200 break-all">{row.after}</td>
    </tr>
  );
}

const DIFF_IGNORED_KEYS = new Set([
  "_id", "id", "created_at", "updated_at", "validation_results",
  "generated_config", "revisions", "status", "_uid"
]);

function formatDiffValue(v) {
  if (v === undefined || v === null) return "—";
  if (typeof v === "string") return v === "" ? "—" : v;
  if (typeof v === "number" || typeof v === "boolean") return String(v);
  try { return JSON.stringify(v); } catch { return String(v); }
}

function buildProjectDiff(prev, curr) {
  const rows = [];
  const walk = (a, b, path) => {
    const aIsObj = a && typeof a === "object" && !Array.isArray(a);
    const bIsObj = b && typeof b === "object" && !Array.isArray(b);
    const aIsArr = Array.isArray(a);
    const bIsArr = Array.isArray(b);

    if (aIsObj && bIsObj) {
      const keys = new Set([...Object.keys(a || {}), ...Object.keys(b || {})]);
      keys.forEach(k => {
        if (DIFF_IGNORED_KEYS.has(k)) return;
        walk(a?.[k], b?.[k], path ? `${path}.${k}` : k);
      });
      return;
    }
    if (aIsArr || bIsArr) {
      const arrA = aIsArr ? a : [];
      const arrB = bIsArr ? b : [];
      const max = Math.max(arrA.length, arrB.length);
      for (let i = 0; i < max; i++) {
        walk(arrA[i], arrB[i], `${path}[${i}]`);
      }
      return;
    }
    const ea = a === undefined || a === null || a === "";
    const eb = b === undefined || b === null || b === "";
    if (ea && eb) return;
    if (ea && !eb) {
      rows.push({ kind: "add", path, before: "—", after: formatDiffValue(b) });
    } else if (!ea && eb) {
      rows.push({ kind: "remove", path, before: formatDiffValue(a), after: "—" });
    } else if (formatDiffValue(a) !== formatDiffValue(b)) {
      rows.push({ kind: "change", path, before: formatDiffValue(a), after: formatDiffValue(b) });
    }
  };
  walk(prev || {}, curr || {}, "");
  return rows;
}

function FindingRow({ finding }) {
  const icons = { error: XCircle, warning: AlertTriangle, info: Info };
  const colors = { error: "severity-error", warning: "severity-warning", info: "severity-info" };
  const Icon = icons[finding.severity] || Info;

  return (
    <div className={`flex gap-3 p-2.5 border rounded-sm text-sm ${colors[finding.severity]}`} data-testid={`finding-${finding.severity}`}>
      <Icon className="w-4 h-4 shrink-0 mt-0.5" />
      <div className="flex-1 min-w-0">
        <div className="text-xs opacity-70 font-mono">{finding.field}</div>
        <div className="text-sm">{finding.message}</div>
      </div>
    </div>
  );
}

function EmptyState({ message }) {
  return (
    <div className="flex items-center justify-center h-full text-sm text-zinc-600 p-8">
      {message}
    </div>
  );
}

function ExportCard({ icon: Icon, label, desc, format, onClick, disabled }) {
  return (
    <button
      className="border border-border rounded-sm p-4 text-left hover:bg-zinc-800/40 btn-transition disabled:opacity-40 disabled:cursor-not-allowed"
      onClick={() => onClick(format)}
      disabled={disabled}
      data-testid={`export-${format}-btn`}
    >
      <Icon className="w-5 h-5 text-zinc-400 mb-2" />
      <div className="text-sm font-medium text-zinc-200">{label}</div>
      <div className="text-xs text-zinc-500 mt-0.5">{desc}</div>
      <div className="mt-2">
        <span className="inline-flex items-center text-xs text-blue-400">
          <Download className="w-3 h-3 mr-1" /> Download
        </span>
      </div>
    </button>
  );
}
