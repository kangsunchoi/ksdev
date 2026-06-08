import { useState, useEffect, useCallback, useRef } from "react";
import { useNavigate } from "react-router-dom";
import { toast } from "sonner";
import { api } from "@/lib/api";
import { useI18n } from "@/lib/i18n";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  FilePlus2, RefreshCw, Server, FileCheck, FileWarning, Files, ChevronRight, Upload
} from "lucide-react";

const statusColors = {
  draft: "bg-zinc-700 text-zinc-300",
  validated: "bg-amber-600/20 text-amber-400 border border-amber-600/30",
  generated: "bg-emerald-600/20 text-emerald-400 border border-emerald-600/30",
};

const platformLabels = {
  ie3300: "IE3300", ie3400: "IE3400", ie3100: "IE3100", ie9320: "IE9320",
  catalyst_9200: "Cat9200", catalyst_9300: "Cat9300", catalyst_9500: "Cat9500",
  wlc_9800: "WLC9800", c1200: "C1200",
};

export default function Dashboard() {
  const { t } = useI18n();
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [importing, setImporting] = useState(false);
  const fileInputRef = useRef(null);
  const navigate = useNavigate();

  const fetchStats = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const res = await api.getStats();
      setStats(res.data);
    } catch (err) {
      setError(err.message || t("dashboard.loadError"));
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { fetchStats(); }, [fetchStats]);

  const handleImportClick = () => fileInputRef.current?.click();

  const handleImportFile = async (e) => {
    const file = e.target.files?.[0];
    if (!file) return;
    e.target.value = "";

    const name = file.name.toLowerCase();
    const format = name.endsWith(".yaml") || name.endsWith(".yml") ? "yaml" : "json";

    setImporting(true);
    try {
      const content = await file.text();
      const res = await api.importProject({ format, content });
      toast.success(t("dashboard.import.success", { name: res.data.name }));
      navigate(`/projects/${res.data.id}`);
    } catch (err) {
      toast.error(t("dashboard.import.fail", { detail: err.response?.data?.detail || err.message }));
    } finally {
      setImporting(false);
    }
  };

  if (loading) {
    return (
      <div className="p-6" data-testid="dashboard-loading">
        <div className="text-zinc-500 text-sm">{t("dashboard.loading")}</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-6" data-testid="dashboard-error">
        <div className="text-red-400 text-sm">{error}</div>
        <Button variant="outline" size="sm" className="h-8 text-xs mt-3" onClick={fetchStats}>
          <RefreshCw className="w-3.5 h-3.5 mr-1.5" /> {t("common.retry")}
        </Button>
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6" data-testid="dashboard">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-semibold tracking-tight">{t("dashboard.title")}</h1>
          <p className="text-sm text-zinc-500 mt-0.5">{t("dashboard.subtitle")}</p>
        </div>
        <div className="flex gap-2">
          <input
            ref={fileInputRef}
            type="file"
            accept=".json,.yaml,.yml,application/json,text/yaml"
            className="hidden"
            onChange={handleImportFile}
            data-testid="import-file-input"
          />
          <Button
            variant="outline"
            size="sm"
            onClick={handleImportClick}
            disabled={importing}
            data-testid="import-project-btn"
            className="h-8 text-xs"
          >
            <Upload className="w-3.5 h-3.5 mr-1.5" /> {importing ? t("common.importing") : t("common.import")}
          </Button>
          <Button
            variant="outline"
            size="sm"
            onClick={fetchStats}
            data-testid="refresh-stats-btn"
            className="h-8 text-xs"
          >
            <RefreshCw className="w-3.5 h-3.5 mr-1.5" /> {t("common.refresh")}
          </Button>
          <Button
            size="sm"
            onClick={() => navigate("/projects/new")}
            data-testid="new-project-btn"
            className="h-8 text-xs bg-blue-600 hover:bg-blue-700 text-white"
          >
            <FilePlus2 className="w-3.5 h-3.5 mr-1.5" /> {t("common.newConfig")}
          </Button>
        </div>
      </div>

      {/* Stats row */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3" data-testid="stats-grid">
        <StatCard
          icon={Files} label={t("dashboard.stat.total")}
          value={stats?.total_projects ?? 0}
          testId="stat-total-projects"
        />
        <StatCard
          icon={FileWarning} label={t("dashboard.stat.drafts")}
          value={stats?.draft_count ?? 0}
          testId="stat-drafts"
        />
        <StatCard
          icon={FileCheck} label={t("dashboard.stat.generated")}
          value={stats?.generated_count ?? 0}
          color="text-emerald-400"
          testId="stat-generated"
        />
        <StatCard
          icon={Server} label={t("dashboard.stat.templates")}
          value={stats?.total_templates ?? 0}
          color="text-blue-400"
          testId="stat-templates"
        />
      </div>

      {/* Recent projects */}
      <div>
        <h2 className="text-sm font-medium text-zinc-300 mb-3">{t("dashboard.recent")}</h2>
        <div className="border border-border rounded-sm overflow-hidden" data-testid="recent-projects-table">
          <table className="w-full dense-table">
            <thead>
              <tr className="bg-card border-b border-border text-xs text-zinc-500 uppercase tracking-wider">
                <th className="text-left py-2 px-3">{t("dashboard.col.name")}</th>
                <th className="text-left py-2 px-3">{t("dashboard.col.platform")}</th>
                <th className="text-left py-2 px-3">{t("dashboard.col.hostname")}</th>
                <th className="text-left py-2 px-3">{t("dashboard.col.status")}</th>
                <th className="text-right py-2 px-3">{t("dashboard.col.updated")}</th>
                <th className="py-2 px-3 w-8"></th>
              </tr>
            </thead>
            <tbody>
              {(!stats?.recent_projects || stats.recent_projects.length === 0) ? (
                <tr>
                  <td colSpan={6} className="text-center py-8 text-sm text-zinc-600">
                    {t("dashboard.empty")}
                  </td>
                </tr>
              ) : (
                stats.recent_projects.map((p) => (
                  <tr
                    key={p.id}
                    className="border-b border-border hover:bg-zinc-800/40 cursor-pointer btn-transition"
                    onClick={() => navigate(`/projects/${p.id}`)}
                    data-testid={`project-row-${p.id}`}
                  >
                    <td className="py-2 px-3 text-sm font-medium text-zinc-200">{p.name || t("dashboard.unnamed")}</td>
                    <td className="py-2 px-3">
                      <span className="text-xs text-zinc-400 font-mono">
                        {platformLabels[p.device?.platform_family] || p.device?.platform_family || "—"}
                      </span>
                    </td>
                    <td className="py-2 px-3 text-xs font-mono text-zinc-400">
                      {p.device?.hostname || "—"}
                    </td>
                    <td className="py-2 px-3">
                      <Badge className={`text-[10px] px-1.5 py-0 ${statusColors[p.status] || statusColors.draft}`}>
                        {t(`status.${p.status || "draft"}`)}
                      </Badge>
                    </td>
                    <td className="py-2 px-3 text-right text-xs text-zinc-500">
                      {p.updated_at ? new Date(p.updated_at).toLocaleDateString() : "—"}
                    </td>
                    <td className="py-2 px-3">
                      <ChevronRight className="w-3.5 h-3.5 text-zinc-600" />
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

function StatCard({ icon: Icon, label, value, color = "text-zinc-200", testId }) {
  return (
    <div
      className="border border-border rounded-sm p-3 bg-card"
      data-testid={testId}
    >
      <div className="flex items-center gap-2 mb-1.5">
        <Icon className="w-4 h-4 text-zinc-500" />
        <span className="text-xs text-zinc-500 font-medium">{label}</span>
      </div>
      <div className={`text-2xl font-semibold tracking-tight ${color}`}>
        {value}
      </div>
    </div>
  );
}
