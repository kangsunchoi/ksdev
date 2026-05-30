import { useState, useEffect, useCallback } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { toast } from "sonner";
import { api } from "@/lib/api";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Badge } from "@/components/ui/badge";
import { ScrollArea } from "@/components/ui/scroll-area";
import {
  ChevronLeft, ChevronRight, Save, Plus, Trash2, CheckCircle2, AlertTriangle, Loader2
} from "lucide-react";

const PLATFORMS = [
  { value: "ie3300", label: "Cisco IE3300", cat: "industrial" },
  { value: "ie3400", label: "Cisco IE3400", cat: "industrial" },
  { value: "ie9320", label: "Cisco IE9320", cat: "industrial" },
  { value: "catalyst_9200", label: "Catalyst 9200", cat: "campus" },
  { value: "catalyst_9300", label: "Catalyst 9300", cat: "campus" },
  { value: "catalyst_9500", label: "Catalyst 9500", cat: "campus" },
  { value: "wlc_9800", label: "WLC 9800", cat: "wireless" },
];

const ROLES = [
  { value: "access_switch", label: "Access Switch" },
  { value: "distribution_switch", label: "Distribution / L3 Switch" },
  { value: "core_switch", label: "Core Switch" },
  { value: "industrial_access", label: "Industrial Access Switch" },
  { value: "industrial_distribution", label: "Industrial Distribution Switch" },
  { value: "wlc", label: "Wireless LAN Controller" },
];

const OS_VERSIONS = ["17.3", "17.6", "17.9", "17.12"];

const INDUSTRIAL_PLATFORMS = ["ie3300", "ie3400", "ie9320"];

const defaultForm = () => ({
  name: "",
  device: { role: "access_switch", vendor: "cisco", platform_family: "", os_family: "ios_xe", os_version: "17.9", hostname: "" },
  management: { mgmt_vlan: "", mgmt_ip: "", mgmt_mask: "255.255.255.0", default_gateway: "", dns_servers: [""], domain_name: "" },
  vlans: [],
  interfaces: { access_ports: [], trunk_ports: [], port_channels: [] },
  routing: { svi_list: [], static_routes: [] },
  stp: { mode: "rapid-pvst", priority: {} },
  services: { ntp_servers: [""], syslog_servers: [""], snmp: { version: "", community: "", v3_user: "", v3_auth_protocol: "", v3_auth_password: "", v3_priv_protocol: "", v3_priv_password: "" }, dhcp_relay: [] },
  security: { aaa: { enabled: true, method: "local", radius_servers: [] }, local_users: [{ username: "", privilege: 15, secret_type: "9" }], ssh: { version: 2, timeout: 60, retries: 3, rsa_bits: 2048 }, banner: "", line_vty: { transport: "ssh", access_class: "" } },
  industrial: { panel_name: "", cabinet_name: "", peer_role: "none", uplink_role: "", ring_link_role: "", multicast_relevance: "", industrial_notes: "" },
  notes: "",
});

export default function NewProject() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [form, setForm] = useState(defaultForm());
  const [step, setStep] = useState(0);
  const [saving, setSaving] = useState(false);
  const [loaded, setLoaded] = useState(!id);

  const isIndustrial = INDUSTRIAL_PLATFORMS.includes(form.device.platform_family);
  const steps = [
    "Device & Management", "VLANs", "Interfaces", "Routing & Services", "Security",
    ...(isIndustrial ? ["Industrial OT"] : []), "Review"
  ];

  useEffect(() => {
    if (id) {
      api.getProject(id).then(res => {
        const p = res.data;
        const merged = defaultForm();
        Object.keys(merged).forEach(k => {
          if (p[k] !== undefined && p[k] !== null) {
            if (typeof merged[k] === 'object' && !Array.isArray(merged[k])) {
              merged[k] = { ...merged[k], ...p[k] };
            } else {
              merged[k] = p[k];
            }
          }
        });
        if (merged.management.dns_servers.length === 0) merged.management.dns_servers = [""];
        if (merged.services.ntp_servers.length === 0) merged.services.ntp_servers = [""];
        if (merged.services.syslog_servers.length === 0) merged.services.syslog_servers = [""];
        if (merged.security.local_users.length === 0) merged.security.local_users = [{ username: "", privilege: 15, secret_type: "9" }];
        setForm(merged);
        setLoaded(true);
      }).catch(() => { toast.error("Failed to load project"); navigate("/"); });
    }
  }, [id, navigate]);

  const upd = useCallback((path, value) => {
    setForm(prev => {
      const next = JSON.parse(JSON.stringify(prev));
      const keys = path.split(".");
      let obj = next;
      for (let i = 0; i < keys.length - 1; i++) {
        if (obj[keys[i]] === undefined) obj[keys[i]] = {};
        obj = obj[keys[i]];
      }
      obj[keys[keys.length - 1]] = value;
      return next;
    });
  }, []);

  const addToArray = (path) => {
    const templates = {
      vlans: { id: "", name: "", description: "" },
      "interfaces.access_ports": { interface: "", vlan: "", voice_vlan: "", description: "", mode: "access" },
      "interfaces.trunk_ports": { interface: "", allowed_vlans: "", native_vlan: "", description: "" },
      "interfaces.port_channels": { id: "", members: [], mode: "trunk", protocol: "lacp", allowed_vlans: "", description: "" },
      "routing.svi_list": { vlan: "", ip: "", mask: "255.255.255.0", description: "" },
      "routing.static_routes": { network: "", mask: "", next_hop: "" },
      "security.local_users": { username: "", privilege: 15, secret_type: "9" },
    };
    setForm(prev => {
      const next = JSON.parse(JSON.stringify(prev));
      const keys = path.split(".");
      let obj = next;
      for (const k of keys) obj = obj[k];
      obj.push({ ...templates[path] });
      return next;
    });
  };

  const removeFromArray = (path, idx) => {
    setForm(prev => {
      const next = JSON.parse(JSON.stringify(prev));
      const keys = path.split(".");
      let obj = next;
      for (const k of keys) obj = obj[k];
      obj.splice(idx, 1);
      return next;
    });
  };

  const updateArrayItem = (path, idx, field, value) => {
    setForm(prev => {
      const next = JSON.parse(JSON.stringify(prev));
      const keys = path.split(".");
      let obj = next;
      for (const k of keys) obj = obj[k];
      obj[idx][field] = value;
      return next;
    });
  };

  const updateStringArray = (path, idx, value) => {
    setForm(prev => {
      const next = JSON.parse(JSON.stringify(prev));
      const keys = path.split(".");
      let obj = next;
      for (const k of keys) obj = obj[k];
      obj[idx] = value;
      return next;
    });
  };

  const addStringToArray = (path) => {
    setForm(prev => {
      const next = JSON.parse(JSON.stringify(prev));
      const keys = path.split(".");
      let obj = next;
      for (const k of keys) obj = obj[k];
      obj.push("");
      return next;
    });
  };

  const handleSave = async () => {
    if (!form.name.trim()) { toast.error("Project name is required"); return; }
    if (!form.device.platform_family) { toast.error("Select a platform"); return; }
    if (!form.device.hostname.trim()) { toast.error("Hostname is required"); return; }
    setSaving(true);
    try {
      if (id) {
        await api.updateProject(id, form);
        toast.success("Project updated");
        navigate(`/projects/${id}`);
      } else {
        const res = await api.createProject(form);
        toast.success("Project created");
        navigate(`/projects/${res.data.id}`);
      }
    } catch (e) {
      toast.error("Save failed: " + (e.response?.data?.detail || e.message));
    } finally {
      setSaving(false);
    }
  };

  if (!loaded) return <div className="p-6 text-sm text-zinc-500">Loading project...</div>;

  const F = ({ label, children, className = "" }) => (
    <div className={className}>
      <Label className="text-xs text-zinc-400 mb-1 block">{label}</Label>
      {children}
    </div>
  );

  const renderStep = () => {
    switch (step) {
      case 0: return <StepDeviceMgmt form={form} upd={upd} F={F} updateStringArray={updateStringArray} addStringToArray={addStringToArray} />;
      case 1: return <StepVlans form={form} addToArray={addToArray} removeFromArray={removeFromArray} updateArrayItem={updateArrayItem} F={F} />;
      case 2: return <StepInterfaces form={form} addToArray={addToArray} removeFromArray={removeFromArray} updateArrayItem={updateArrayItem} F={F} />;
      case 3: return <StepRoutingServices form={form} upd={upd} F={F} addToArray={addToArray} removeFromArray={removeFromArray} updateArrayItem={updateArrayItem} updateStringArray={updateStringArray} addStringToArray={addStringToArray} />;
      case 4: return <StepSecurity form={form} upd={upd} F={F} addToArray={addToArray} removeFromArray={removeFromArray} updateArrayItem={updateArrayItem} />;
      default:
        if (isIndustrial && step === 5) return <StepIndustrial form={form} upd={upd} F={F} />;
        return <StepReview form={form} />;
    }
  };

  return (
    <div className="flex flex-col h-full" data-testid="new-project-page">
      <div className="h-14 border-b border-border flex items-center justify-between px-6 shrink-0">
        <h1 className="text-sm font-semibold">{id ? "Edit Project" : "New Configuration Project"}</h1>
        <Button size="sm" className="h-8 text-xs bg-blue-600 hover:bg-blue-700 text-white" onClick={handleSave} disabled={saving} data-testid="save-project-btn">
          {saving ? <Loader2 className="w-3.5 h-3.5 mr-1.5 animate-spin" /> : <Save className="w-3.5 h-3.5 mr-1.5" />}
          {saving ? "Saving..." : "Save Project"}
        </Button>
      </div>

      <div className="flex-1 flex overflow-hidden">
        {/* Step indicator */}
        <div className="w-48 border-r border-border py-4 px-3 shrink-0 space-y-1 bg-card/50">
          {steps.map((s, i) => (
            <button
              key={i}
              onClick={() => setStep(i)}
              data-testid={`wizard-step-${i}`}
              className={`step-item w-full text-left px-2 py-1.5 rounded-sm btn-transition ${
                step === i ? "active" : i < step ? "completed" : ""
              }`}
            >
              <span className="step-number">
                {i < step ? <CheckCircle2 className="w-3.5 h-3.5" /> : i + 1}
              </span>
              <span className={`text-xs ${step === i ? "text-blue-400 font-medium" : i < step ? "text-emerald-400" : "text-zinc-500"}`}>
                {s}
              </span>
            </button>
          ))}
        </div>

        {/* Step content */}
        <ScrollArea className="flex-1">
          <div className="p-6 max-w-4xl">
            <h2 className="text-base font-medium mb-4 text-zinc-200">{steps[step]}</h2>
            {renderStep()}
          </div>
        </ScrollArea>
      </div>

      {/* Navigation */}
      <div className="h-12 border-t border-border flex items-center justify-between px-6 shrink-0 bg-card/50">
        <Button variant="outline" size="sm" className="h-8 text-xs" onClick={() => setStep(s => Math.max(0, s - 1))} disabled={step === 0} data-testid="prev-step-btn">
          <ChevronLeft className="w-3.5 h-3.5 mr-1" /> Previous
        </Button>
        <span className="text-xs text-zinc-500">Step {step + 1} of {steps.length}</span>
        <Button variant="outline" size="sm" className="h-8 text-xs" onClick={() => setStep(s => Math.min(steps.length - 1, s + 1))} disabled={step === steps.length - 1} data-testid="next-step-btn">
          Next <ChevronRight className="w-3.5 h-3.5 ml-1" />
        </Button>
      </div>
    </div>
  );
}

/* ============ Step Components ============ */

function StepDeviceMgmt({ form, upd, F, updateStringArray, addStringToArray }) {
  return (
    <div className="space-y-6">
      <F label="Project Name">
        <Input className="ncb-input" value={form.name} onChange={e => upd("name", e.target.value)} placeholder="e.g. Factory Floor IE3300" data-testid="input-project-name" />
      </F>
      <div className="grid grid-cols-3 gap-4">
        <F label="Platform Family">
          <Select value={form.device.platform_family} onValueChange={v => upd("device.platform_family", v)}>
            <SelectTrigger className="ncb-select-trigger" data-testid="select-platform">
              <SelectValue placeholder="Select platform" />
            </SelectTrigger>
            <SelectContent>
              <div className="px-2 py-1 text-[10px] text-zinc-500 uppercase">Industrial</div>
              {PLATFORMS.filter(p => p.cat === "industrial").map(p => <SelectItem key={p.value} value={p.value}>{p.label}</SelectItem>)}
              <div className="px-2 py-1 text-[10px] text-zinc-500 uppercase mt-1">Campus</div>
              {PLATFORMS.filter(p => p.cat === "campus").map(p => <SelectItem key={p.value} value={p.value}>{p.label}</SelectItem>)}
              <div className="px-2 py-1 text-[10px] text-zinc-500 uppercase mt-1">Wireless</div>
              {PLATFORMS.filter(p => p.cat === "wireless").map(p => <SelectItem key={p.value} value={p.value}>{p.label}</SelectItem>)}
            </SelectContent>
          </Select>
        </F>
        <F label="OS Version">
          <Select value={form.device.os_version} onValueChange={v => upd("device.os_version", v)}>
            <SelectTrigger className="ncb-select-trigger" data-testid="select-os-version">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              {OS_VERSIONS.map(v => <SelectItem key={v} value={v}>IOS-XE {v}</SelectItem>)}
            </SelectContent>
          </Select>
        </F>
        <F label="Device Role">
          <Select value={form.device.role} onValueChange={v => upd("device.role", v)}>
            <SelectTrigger className="ncb-select-trigger" data-testid="select-role">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              {ROLES.map(r => <SelectItem key={r.value} value={r.value}>{r.label}</SelectItem>)}
            </SelectContent>
          </Select>
        </F>
      </div>
      <div className="grid grid-cols-2 gap-4">
        <F label="Hostname">
          <Input className="ncb-input font-mono" value={form.device.hostname} onChange={e => upd("device.hostname", e.target.value)} placeholder="SW-FLOOR1-01" data-testid="input-hostname" />
        </F>
        <F label="Domain Name">
          <Input className="ncb-input font-mono" value={form.management.domain_name} onChange={e => upd("management.domain_name", e.target.value)} placeholder="corp.local" data-testid="input-domain" />
        </F>
      </div>

      <div className="border-t border-border pt-4">
        <h3 className="text-sm font-medium text-zinc-300 mb-3">Management Network</h3>
        <div className="grid grid-cols-4 gap-3">
          <F label="Management VLAN">
            <Input className="ncb-input font-mono" value={form.management.mgmt_vlan} onChange={e => upd("management.mgmt_vlan", e.target.value)} placeholder="100" data-testid="input-mgmt-vlan" />
          </F>
          <F label="Management IP">
            <Input className="ncb-input font-mono" value={form.management.mgmt_ip} onChange={e => upd("management.mgmt_ip", e.target.value)} placeholder="10.0.100.10" data-testid="input-mgmt-ip" />
          </F>
          <F label="Subnet Mask">
            <Input className="ncb-input font-mono" value={form.management.mgmt_mask} onChange={e => upd("management.mgmt_mask", e.target.value)} placeholder="255.255.255.0" data-testid="input-mgmt-mask" />
          </F>
          <F label="Default Gateway">
            <Input className="ncb-input font-mono" value={form.management.default_gateway} onChange={e => upd("management.default_gateway", e.target.value)} placeholder="10.0.100.1" data-testid="input-gateway" />
          </F>
        </div>
      </div>

      <div>
        <Label className="text-xs text-zinc-400 mb-1 block">DNS Servers</Label>
        {form.management.dns_servers.map((dns, i) => (
          <div key={i} className="flex gap-2 mb-1.5">
            <Input className="ncb-input font-mono flex-1" value={dns} onChange={e => updateStringArray("management.dns_servers", i, e.target.value)} placeholder="10.0.1.10" data-testid={`input-dns-${i}`} />
            {form.management.dns_servers.length > 1 && (
              <Button variant="ghost" size="sm" className="h-8 w-8 p-0 text-zinc-500 hover:text-red-400" onClick={() => {
                const next = [...form.management.dns_servers]; next.splice(i, 1); upd("management.dns_servers", next);
              }}><Trash2 className="w-3.5 h-3.5" /></Button>
            )}
          </div>
        ))}
        <Button variant="ghost" size="sm" className="h-7 text-xs text-zinc-500" onClick={() => addStringToArray("management.dns_servers")} data-testid="add-dns-btn">
          <Plus className="w-3 h-3 mr-1" /> Add DNS
        </Button>
      </div>
    </div>
  );
}

function StepVlans({ form, addToArray, removeFromArray, updateArrayItem, F }) {
  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        <span className="text-xs text-zinc-500">{form.vlans.length} VLAN(s) defined</span>
        <Button variant="outline" size="sm" className="h-7 text-xs" onClick={() => addToArray("vlans")} data-testid="add-vlan-btn">
          <Plus className="w-3 h-3 mr-1" /> Add VLAN
        </Button>
      </div>
      {form.vlans.length === 0 && <div className="text-sm text-zinc-600 py-4 text-center border border-dashed border-border rounded-sm">No VLANs defined. Click "Add VLAN" to start.</div>}
      {form.vlans.map((vlan, i) => (
        <div key={i} className="grid grid-cols-[80px_1fr_1fr_32px] gap-2 items-end" data-testid={`vlan-row-${i}`}>
          <F label={i === 0 ? "ID" : ""}>
            <Input className="ncb-input font-mono" value={vlan.id} onChange={e => updateArrayItem("vlans", i, "id", e.target.value)} placeholder="10" data-testid={`vlan-id-${i}`} />
          </F>
          <F label={i === 0 ? "Name" : ""}>
            <Input className="ncb-input" value={vlan.name} onChange={e => updateArrayItem("vlans", i, "name", e.target.value)} placeholder="DATA" data-testid={`vlan-name-${i}`} />
          </F>
          <F label={i === 0 ? "Description" : ""}>
            <Input className="ncb-input" value={vlan.description} onChange={e => updateArrayItem("vlans", i, "description", e.target.value)} placeholder="User data VLAN" />
          </F>
          <Button variant="ghost" size="sm" className="h-8 w-8 p-0 text-zinc-500 hover:text-red-400" onClick={() => removeFromArray("vlans", i)} data-testid={`remove-vlan-${i}`}>
            <Trash2 className="w-3.5 h-3.5" />
          </Button>
        </div>
      ))}
    </div>
  );
}

function StepInterfaces({ form, addToArray, removeFromArray, updateArrayItem, F }) {
  return (
    <div className="space-y-6">
      {/* Access Ports */}
      <div>
        <div className="flex justify-between items-center mb-3">
          <h3 className="text-sm font-medium text-zinc-300">Access Ports</h3>
          <Button variant="outline" size="sm" className="h-7 text-xs" onClick={() => addToArray("interfaces.access_ports")} data-testid="add-access-port-btn">
            <Plus className="w-3 h-3 mr-1" /> Add
          </Button>
        </div>
        {form.interfaces.access_ports.map((p, i) => (
          <div key={i} className="grid grid-cols-[1fr_80px_80px_1fr_32px] gap-2 items-end mb-2" data-testid={`access-port-${i}`}>
            <F label={i === 0 ? "Interface" : ""}>
              <Input className="ncb-input font-mono" value={p.interface} onChange={e => updateArrayItem("interfaces.access_ports", i, "interface", e.target.value)} placeholder="Gi1/0/1" />
            </F>
            <F label={i === 0 ? "VLAN" : ""}>
              <Input className="ncb-input font-mono" value={p.vlan} onChange={e => updateArrayItem("interfaces.access_ports", i, "vlan", e.target.value)} placeholder="10" />
            </F>
            <F label={i === 0 ? "Voice" : ""}>
              <Input className="ncb-input font-mono" value={p.voice_vlan || ""} onChange={e => updateArrayItem("interfaces.access_ports", i, "voice_vlan", e.target.value)} placeholder="20" />
            </F>
            <F label={i === 0 ? "Description" : ""}>
              <Input className="ncb-input" value={p.description} onChange={e => updateArrayItem("interfaces.access_ports", i, "description", e.target.value)} placeholder="PC Port" />
            </F>
            <Button variant="ghost" size="sm" className="h-8 w-8 p-0 text-zinc-500 hover:text-red-400" onClick={() => removeFromArray("interfaces.access_ports", i)}>
              <Trash2 className="w-3.5 h-3.5" />
            </Button>
          </div>
        ))}
        {form.interfaces.access_ports.length === 0 && <div className="text-xs text-zinc-600 py-2">No access ports configured.</div>}
      </div>

      {/* Trunk Ports */}
      <div className="border-t border-border pt-4">
        <div className="flex justify-between items-center mb-3">
          <h3 className="text-sm font-medium text-zinc-300">Trunk Ports</h3>
          <Button variant="outline" size="sm" className="h-7 text-xs" onClick={() => addToArray("interfaces.trunk_ports")} data-testid="add-trunk-port-btn">
            <Plus className="w-3 h-3 mr-1" /> Add
          </Button>
        </div>
        {form.interfaces.trunk_ports.map((p, i) => (
          <div key={i} className="grid grid-cols-[1fr_1fr_80px_1fr_32px] gap-2 items-end mb-2" data-testid={`trunk-port-${i}`}>
            <F label={i === 0 ? "Interface" : ""}>
              <Input className="ncb-input font-mono" value={p.interface} onChange={e => updateArrayItem("interfaces.trunk_ports", i, "interface", e.target.value)} placeholder="Gi1/0/48" />
            </F>
            <F label={i === 0 ? "Allowed VLANs" : ""}>
              <Input className="ncb-input font-mono" value={p.allowed_vlans} onChange={e => updateArrayItem("interfaces.trunk_ports", i, "allowed_vlans", e.target.value)} placeholder="10,20,100" />
            </F>
            <F label={i === 0 ? "Native" : ""}>
              <Input className="ncb-input font-mono" value={p.native_vlan || ""} onChange={e => updateArrayItem("interfaces.trunk_ports", i, "native_vlan", e.target.value)} placeholder="1" />
            </F>
            <F label={i === 0 ? "Description" : ""}>
              <Input className="ncb-input" value={p.description} onChange={e => updateArrayItem("interfaces.trunk_ports", i, "description", e.target.value)} placeholder="Uplink" />
            </F>
            <Button variant="ghost" size="sm" className="h-8 w-8 p-0 text-zinc-500 hover:text-red-400" onClick={() => removeFromArray("interfaces.trunk_ports", i)}>
              <Trash2 className="w-3.5 h-3.5" />
            </Button>
          </div>
        ))}
        {form.interfaces.trunk_ports.length === 0 && <div className="text-xs text-zinc-600 py-2">No trunk ports configured.</div>}
      </div>

      {/* Port-Channels */}
      <div className="border-t border-border pt-4">
        <div className="flex justify-between items-center mb-3">
          <h3 className="text-sm font-medium text-zinc-300">Port-Channels</h3>
          <Button variant="outline" size="sm" className="h-7 text-xs" onClick={() => addToArray("interfaces.port_channels")} data-testid="add-port-channel-btn">
            <Plus className="w-3 h-3 mr-1" /> Add
          </Button>
        </div>
        {form.interfaces.port_channels.map((pc, i) => (
          <div key={i} className="border border-border rounded-sm p-3 mb-2 space-y-2" data-testid={`port-channel-${i}`}>
            <div className="flex justify-between">
              <span className="text-xs text-zinc-400">Port-Channel {pc.id || "?"}</span>
              <Button variant="ghost" size="sm" className="h-6 w-6 p-0 text-zinc-500 hover:text-red-400" onClick={() => removeFromArray("interfaces.port_channels", i)}>
                <Trash2 className="w-3 h-3" />
              </Button>
            </div>
            <div className="grid grid-cols-4 gap-2">
              <F label="Po ID">
                <Input className="ncb-input font-mono" value={pc.id} onChange={e => updateArrayItem("interfaces.port_channels", i, "id", e.target.value)} placeholder="1" />
              </F>
              <F label="Mode">
                <Select value={pc.mode} onValueChange={v => updateArrayItem("interfaces.port_channels", i, "mode", v)}>
                  <SelectTrigger className="ncb-select-trigger"><SelectValue /></SelectTrigger>
                  <SelectContent>
                    <SelectItem value="trunk">Trunk</SelectItem>
                    <SelectItem value="access">Access</SelectItem>
                  </SelectContent>
                </Select>
              </F>
              <F label="Protocol">
                <Select value={pc.protocol} onValueChange={v => updateArrayItem("interfaces.port_channels", i, "protocol", v)}>
                  <SelectTrigger className="ncb-select-trigger"><SelectValue /></SelectTrigger>
                  <SelectContent>
                    <SelectItem value="lacp">LACP</SelectItem>
                    <SelectItem value="static">Static (on)</SelectItem>
                  </SelectContent>
                </Select>
              </F>
              <F label="Allowed VLANs">
                <Input className="ncb-input font-mono" value={pc.allowed_vlans} onChange={e => updateArrayItem("interfaces.port_channels", i, "allowed_vlans", e.target.value)} placeholder="10,20" />
              </F>
            </div>
            <F label="Members (comma-separated)">
              <Input className="ncb-input font-mono" value={Array.isArray(pc.members) ? pc.members.join(", ") : pc.members}
                onChange={e => updateArrayItem("interfaces.port_channels", i, "members", e.target.value.split(",").map(s => s.trim()))}
                placeholder="Gi1/0/47, Gi1/0/48" />
            </F>
            <F label="Description">
              <Input className="ncb-input" value={pc.description} onChange={e => updateArrayItem("interfaces.port_channels", i, "description", e.target.value)} placeholder="Uplink bundle" />
            </F>
          </div>
        ))}
        {form.interfaces.port_channels.length === 0 && <div className="text-xs text-zinc-600 py-2">No port-channels configured.</div>}
      </div>
    </div>
  );
}

function StepRoutingServices({ form, upd, F, addToArray, removeFromArray, updateArrayItem, updateStringArray, addStringToArray }) {
  return (
    <div className="space-y-6">
      {/* STP */}
      <div>
        <h3 className="text-sm font-medium text-zinc-300 mb-3">Spanning Tree</h3>
        <F label="STP Mode" className="w-48">
          <Select value={form.stp.mode} onValueChange={v => upd("stp.mode", v)}>
            <SelectTrigger className="ncb-select-trigger" data-testid="select-stp-mode"><SelectValue /></SelectTrigger>
            <SelectContent>
              <SelectItem value="rapid-pvst">Rapid-PVST+</SelectItem>
              <SelectItem value="mst">MST</SelectItem>
            </SelectContent>
          </Select>
        </F>
      </div>

      {/* SVIs */}
      <div className="border-t border-border pt-4">
        <div className="flex justify-between items-center mb-3">
          <h3 className="text-sm font-medium text-zinc-300">SVIs (Inter-VLAN Routing)</h3>
          <Button variant="outline" size="sm" className="h-7 text-xs" onClick={() => addToArray("routing.svi_list")} data-testid="add-svi-btn">
            <Plus className="w-3 h-3 mr-1" /> Add SVI
          </Button>
        </div>
        {form.routing.svi_list.map((svi, i) => (
          <div key={i} className="grid grid-cols-[80px_1fr_1fr_1fr_32px] gap-2 items-end mb-2">
            <F label={i === 0 ? "VLAN" : ""}>
              <Input className="ncb-input font-mono" value={svi.vlan} onChange={e => updateArrayItem("routing.svi_list", i, "vlan", e.target.value)} placeholder="10" />
            </F>
            <F label={i === 0 ? "IP Address" : ""}>
              <Input className="ncb-input font-mono" value={svi.ip} onChange={e => updateArrayItem("routing.svi_list", i, "ip", e.target.value)} placeholder="10.1.10.1" />
            </F>
            <F label={i === 0 ? "Mask" : ""}>
              <Input className="ncb-input font-mono" value={svi.mask} onChange={e => updateArrayItem("routing.svi_list", i, "mask", e.target.value)} placeholder="255.255.255.0" />
            </F>
            <F label={i === 0 ? "Description" : ""}>
              <Input className="ncb-input" value={svi.description} onChange={e => updateArrayItem("routing.svi_list", i, "description", e.target.value)} placeholder="Data GW" />
            </F>
            <Button variant="ghost" size="sm" className="h-8 w-8 p-0 text-zinc-500 hover:text-red-400" onClick={() => removeFromArray("routing.svi_list", i)}>
              <Trash2 className="w-3.5 h-3.5" />
            </Button>
          </div>
        ))}
        {form.routing.svi_list.length === 0 && <div className="text-xs text-zinc-600 py-2">No SVIs configured. Required for inter-VLAN routing on L3 platforms.</div>}
      </div>

      {/* Static Routes */}
      <div className="border-t border-border pt-4">
        <div className="flex justify-between items-center mb-3">
          <h3 className="text-sm font-medium text-zinc-300">Static Routes</h3>
          <Button variant="outline" size="sm" className="h-7 text-xs" onClick={() => addToArray("routing.static_routes")} data-testid="add-route-btn">
            <Plus className="w-3 h-3 mr-1" /> Add Route
          </Button>
        </div>
        {form.routing.static_routes.map((r, i) => (
          <div key={i} className="grid grid-cols-[1fr_1fr_1fr_32px] gap-2 items-end mb-2">
            <F label={i === 0 ? "Network" : ""}>
              <Input className="ncb-input font-mono" value={r.network} onChange={e => updateArrayItem("routing.static_routes", i, "network", e.target.value)} placeholder="0.0.0.0" />
            </F>
            <F label={i === 0 ? "Mask" : ""}>
              <Input className="ncb-input font-mono" value={r.mask} onChange={e => updateArrayItem("routing.static_routes", i, "mask", e.target.value)} placeholder="0.0.0.0" />
            </F>
            <F label={i === 0 ? "Next Hop" : ""}>
              <Input className="ncb-input font-mono" value={r.next_hop} onChange={e => updateArrayItem("routing.static_routes", i, "next_hop", e.target.value)} placeholder="10.1.100.254" />
            </F>
            <Button variant="ghost" size="sm" className="h-8 w-8 p-0 text-zinc-500 hover:text-red-400" onClick={() => removeFromArray("routing.static_routes", i)}>
              <Trash2 className="w-3.5 h-3.5" />
            </Button>
          </div>
        ))}
      </div>

      {/* NTP / Syslog */}
      <div className="border-t border-border pt-4 grid grid-cols-2 gap-6">
        <div>
          <Label className="text-xs text-zinc-400 mb-1 block">NTP Servers</Label>
          {form.services.ntp_servers.map((s, i) => (
            <div key={i} className="flex gap-2 mb-1.5">
              <Input className="ncb-input font-mono flex-1" value={s} onChange={e => updateStringArray("services.ntp_servers", i, e.target.value)} placeholder="10.0.1.10" />
              {form.services.ntp_servers.length > 1 && (
                <Button variant="ghost" size="sm" className="h-8 w-8 p-0 text-zinc-500 hover:text-red-400" onClick={() => {
                  const next = [...form.services.ntp_servers]; next.splice(i, 1); upd("services.ntp_servers", next);
                }}><Trash2 className="w-3.5 h-3.5" /></Button>
              )}
            </div>
          ))}
          <Button variant="ghost" size="sm" className="h-7 text-xs text-zinc-500" onClick={() => addStringToArray("services.ntp_servers")}>
            <Plus className="w-3 h-3 mr-1" /> Add NTP
          </Button>
        </div>
        <div>
          <Label className="text-xs text-zinc-400 mb-1 block">Syslog Servers</Label>
          {form.services.syslog_servers.map((s, i) => (
            <div key={i} className="flex gap-2 mb-1.5">
              <Input className="ncb-input font-mono flex-1" value={s} onChange={e => updateStringArray("services.syslog_servers", i, e.target.value)} placeholder="10.0.1.20" />
              {form.services.syslog_servers.length > 1 && (
                <Button variant="ghost" size="sm" className="h-8 w-8 p-0 text-zinc-500 hover:text-red-400" onClick={() => {
                  const next = [...form.services.syslog_servers]; next.splice(i, 1); upd("services.syslog_servers", next);
                }}><Trash2 className="w-3.5 h-3.5" /></Button>
              )}
            </div>
          ))}
          <Button variant="ghost" size="sm" className="h-7 text-xs text-zinc-500" onClick={() => addStringToArray("services.syslog_servers")}>
            <Plus className="w-3 h-3 mr-1" /> Add Syslog
          </Button>
        </div>
      </div>

      {/* SNMP */}
      <div className="border-t border-border pt-4">
        <h3 className="text-sm font-medium text-zinc-300 mb-3">SNMP</h3>
        <div className="grid grid-cols-3 gap-3">
          <F label="Version">
            <Select value={form.services.snmp.version} onValueChange={v => upd("services.snmp.version", v)}>
              <SelectTrigger className="ncb-select-trigger" data-testid="select-snmp-version"><SelectValue placeholder="Select..." /></SelectTrigger>
              <SelectContent>
                <SelectItem value="v2c">SNMPv2c</SelectItem>
                <SelectItem value="v3">SNMPv3</SelectItem>
              </SelectContent>
            </Select>
          </F>
          {form.services.snmp.version === "v2c" && (
            <F label="Community String" className="col-span-2">
              <Input className="ncb-input font-mono" value={form.services.snmp.community} onChange={e => upd("services.snmp.community", e.target.value)} placeholder="public" />
            </F>
          )}
        </div>
        {form.services.snmp.version === "v3" && (
          <div className="grid grid-cols-3 gap-3 mt-3">
            <F label="Username"><Input className="ncb-input font-mono" value={form.services.snmp.v3_user} onChange={e => upd("services.snmp.v3_user", e.target.value)} placeholder="snmpmon" /></F>
            <F label="Auth Protocol">
              <Select value={form.services.snmp.v3_auth_protocol} onValueChange={v => upd("services.snmp.v3_auth_protocol", v)}>
                <SelectTrigger className="ncb-select-trigger"><SelectValue placeholder="Select..." /></SelectTrigger>
                <SelectContent>
                  <SelectItem value="sha">SHA</SelectItem>
                  <SelectItem value="md5">MD5</SelectItem>
                </SelectContent>
              </Select>
            </F>
            <F label="Auth Password"><Input className="ncb-input" type="password" value={form.services.snmp.v3_auth_password} onChange={e => upd("services.snmp.v3_auth_password", e.target.value)} /></F>
            <F label="Privacy Protocol">
              <Select value={form.services.snmp.v3_priv_protocol || ""} onValueChange={v => upd("services.snmp.v3_priv_protocol", v)}>
                <SelectTrigger className="ncb-select-trigger"><SelectValue placeholder="None" /></SelectTrigger>
                <SelectContent>
                  <SelectItem value="aes128">AES-128</SelectItem>
                  <SelectItem value="aes256">AES-256</SelectItem>
                  <SelectItem value="des">DES</SelectItem>
                </SelectContent>
              </Select>
            </F>
            <F label="Privacy Password"><Input className="ncb-input" type="password" value={form.services.snmp.v3_priv_password} onChange={e => upd("services.snmp.v3_priv_password", e.target.value)} /></F>
          </div>
        )}
      </div>
    </div>
  );
}

function StepSecurity({ form, upd, F, addToArray, removeFromArray, updateArrayItem }) {
  return (
    <div className="space-y-6">
      <div>
        <h3 className="text-sm font-medium text-zinc-300 mb-3">Local User Accounts</h3>
        {form.security.local_users.map((u, i) => (
          <div key={i} className="grid grid-cols-[1fr_80px_32px] gap-2 items-end mb-2" data-testid={`user-row-${i}`}>
            <F label={i === 0 ? "Username" : ""}>
              <Input className="ncb-input font-mono" value={u.username} onChange={e => updateArrayItem("security.local_users", i, "username", e.target.value)} placeholder="admin" />
            </F>
            <F label={i === 0 ? "Privilege" : ""}>
              <Input className="ncb-input font-mono" type="number" min={0} max={15} value={u.privilege} onChange={e => updateArrayItem("security.local_users", i, "privilege", parseInt(e.target.value) || 0)} />
            </F>
            <Button variant="ghost" size="sm" className="h-8 w-8 p-0 text-zinc-500 hover:text-red-400" onClick={() => removeFromArray("security.local_users", i)}>
              <Trash2 className="w-3.5 h-3.5" />
            </Button>
          </div>
        ))}
        <Button variant="ghost" size="sm" className="h-7 text-xs text-zinc-500" onClick={() => addToArray("security.local_users")} data-testid="add-user-btn">
          <Plus className="w-3 h-3 mr-1" /> Add User
        </Button>
        <p className="text-[11px] text-zinc-600 mt-1">Passwords will be placeholder text in generated config. Replace before deployment.</p>
      </div>

      <div className="border-t border-border pt-4">
        <h3 className="text-sm font-medium text-zinc-300 mb-3">AAA</h3>
        <div className="grid grid-cols-2 gap-3">
          <F label="Method">
            <Select value={form.security.aaa.method} onValueChange={v => upd("security.aaa.method", v)}>
              <SelectTrigger className="ncb-select-trigger" data-testid="select-aaa-method"><SelectValue /></SelectTrigger>
              <SelectContent>
                <SelectItem value="local">Local</SelectItem>
                <SelectItem value="radius">RADIUS + Local Fallback</SelectItem>
              </SelectContent>
            </Select>
          </F>
        </div>
      </div>

      <div className="border-t border-border pt-4">
        <h3 className="text-sm font-medium text-zinc-300 mb-3">SSH</h3>
        <div className="grid grid-cols-4 gap-3">
          <F label="SSH Version">
            <Input className="ncb-input font-mono" type="number" value={form.security.ssh.version} onChange={e => upd("security.ssh.version", parseInt(e.target.value) || 2)} />
          </F>
          <F label="Timeout (sec)">
            <Input className="ncb-input font-mono" type="number" value={form.security.ssh.timeout} onChange={e => upd("security.ssh.timeout", parseInt(e.target.value) || 60)} />
          </F>
          <F label="Retries">
            <Input className="ncb-input font-mono" type="number" value={form.security.ssh.retries} onChange={e => upd("security.ssh.retries", parseInt(e.target.value) || 3)} />
          </F>
          <F label="RSA Bits">
            <Select value={String(form.security.ssh.rsa_bits)} onValueChange={v => upd("security.ssh.rsa_bits", parseInt(v))}>
              <SelectTrigger className="ncb-select-trigger"><SelectValue /></SelectTrigger>
              <SelectContent>
                <SelectItem value="2048">2048</SelectItem>
                <SelectItem value="4096">4096</SelectItem>
              </SelectContent>
            </Select>
          </F>
        </div>
      </div>

      <div className="border-t border-border pt-4">
        <h3 className="text-sm font-medium text-zinc-300 mb-3">VTY Lines</h3>
        <div className="grid grid-cols-2 gap-3">
          <F label="Transport Input">
            <Select value={form.security.line_vty.transport} onValueChange={v => upd("security.line_vty.transport", v)}>
              <SelectTrigger className="ncb-select-trigger"><SelectValue /></SelectTrigger>
              <SelectContent>
                <SelectItem value="ssh">SSH Only</SelectItem>
                <SelectItem value="ssh telnet">SSH + Telnet</SelectItem>
              </SelectContent>
            </Select>
          </F>
          <F label="Access-Class ACL (optional)">
            <Input className="ncb-input font-mono" value={form.security.line_vty.access_class} onChange={e => upd("security.line_vty.access_class", e.target.value)} placeholder="VTY-ACL" />
          </F>
        </div>
      </div>

      <div className="border-t border-border pt-4">
        <F label="Login Banner">
          <Textarea className="text-sm font-mono bg-transparent min-h-[80px]" value={form.security.banner} onChange={e => upd("security.banner", e.target.value)}
            placeholder="AUTHORIZED ACCESS ONLY. All activity is logged and monitored." data-testid="input-banner" />
        </F>
      </div>

      <div className="border-t border-border pt-4">
        <F label="Project Notes (optional)">
          <Textarea className="text-sm bg-transparent min-h-[60px]" value={form.notes} onChange={e => upd("notes", e.target.value)}
            placeholder="Any additional notes for this configuration..." data-testid="input-notes" />
        </F>
      </div>
    </div>
  );
}

function StepIndustrial({ form, upd, F }) {
  return (
    <div className="space-y-4">
      <div className="p-3 border border-blue-500/20 bg-blue-500/5 rounded-sm text-xs text-blue-400">
        <AlertTriangle className="w-3.5 h-3.5 inline mr-1.5" />
        Industrial OT metadata fields. These do not generate CLI commands but are stored for asset tracking and documentation.
      </div>
      <div className="grid grid-cols-2 gap-4">
        <F label="Panel Name"><Input className="ncb-input" value={form.industrial.panel_name} onChange={e => upd("industrial.panel_name", e.target.value)} placeholder="Panel-A1" data-testid="input-panel-name" /></F>
        <F label="Cabinet Name"><Input className="ncb-input" value={form.industrial.cabinet_name} onChange={e => upd("industrial.cabinet_name", e.target.value)} placeholder="MCC-01" data-testid="input-cabinet-name" /></F>
      </div>
      <div className="grid grid-cols-3 gap-4">
        <F label="Peer Role">
          <Select value={form.industrial.peer_role} onValueChange={v => upd("industrial.peer_role", v)}>
            <SelectTrigger className="ncb-select-trigger" data-testid="select-peer-role"><SelectValue /></SelectTrigger>
            <SelectContent>
              <SelectItem value="none">None</SelectItem>
              <SelectItem value="plc">PLC</SelectItem>
              <SelectItem value="hmi">HMI</SelectItem>
              <SelectItem value="scada">SCADA</SelectItem>
              <SelectItem value="ied">IED</SelectItem>
            </SelectContent>
          </Select>
        </F>
        <F label="Uplink Role"><Input className="ncb-input" value={form.industrial.uplink_role} onChange={e => upd("industrial.uplink_role", e.target.value)} placeholder="distribution" /></F>
        <F label="Ring Link Role"><Input className="ncb-input" value={form.industrial.ring_link_role} onChange={e => upd("industrial.ring_link_role", e.target.value)} placeholder="" /></F>
      </div>
      <F label="Multicast Relevance">
        <Select value={form.industrial.multicast_relevance || ""} onValueChange={v => upd("industrial.multicast_relevance", v)}>
          <SelectTrigger className="ncb-select-trigger"><SelectValue placeholder="Select..." /></SelectTrigger>
          <SelectContent>
            <SelectItem value="none">None</SelectItem>
            <SelectItem value="low">Low</SelectItem>
            <SelectItem value="medium">Medium</SelectItem>
            <SelectItem value="high">High</SelectItem>
          </SelectContent>
        </Select>
      </F>
      <F label="Industrial Notes">
        <Textarea className="text-sm bg-transparent min-h-[60px]" value={form.industrial.industrial_notes} onChange={e => upd("industrial.industrial_notes", e.target.value)}
          placeholder="Floor-level access switch near MCC panel" data-testid="input-industrial-notes" />
      </F>
      <div className="p-3 border border-amber-500/20 bg-amber-500/5 rounded-sm text-xs text-amber-400">
        <AlertTriangle className="w-3.5 h-3.5 inline mr-1.5" />
        PRP, HSR, REP, MRP, PTP, CIP, PROFINET, Modbus TCP, DLR, RedBox are NOT modeled in this release. If these protocols are required, manual verification and configuration is needed.
      </div>
    </div>
  );
}

function StepReview({ form }) {
  const platLabel = PLATFORMS.find(p => p.value === form.device.platform_family)?.label || form.device.platform_family;
  return (
    <div className="space-y-4">
      <div className="text-xs text-zinc-500 mb-2">Review your configuration before saving. You can validate and generate after saving.</div>
      <div className="grid grid-cols-2 gap-4 text-sm">
        <ReviewSection title="Device">
          <ReviewRow label="Project" value={form.name} />
          <ReviewRow label="Platform" value={platLabel} />
          <ReviewRow label="OS" value={`IOS-XE ${form.device.os_version}`} />
          <ReviewRow label="Hostname" value={form.device.hostname} mono />
          <ReviewRow label="Role" value={ROLES.find(r => r.value === form.device.role)?.label} />
        </ReviewSection>
        <ReviewSection title="Management">
          <ReviewRow label="VLAN" value={form.management.mgmt_vlan} mono />
          <ReviewRow label="IP" value={`${form.management.mgmt_ip} / ${form.management.mgmt_mask}`} mono />
          <ReviewRow label="Gateway" value={form.management.default_gateway} mono />
          <ReviewRow label="DNS" value={form.management.dns_servers.filter(Boolean).join(", ")} mono />
          <ReviewRow label="Domain" value={form.management.domain_name} mono />
        </ReviewSection>
      </div>
      <div className="grid grid-cols-3 gap-4 text-sm">
        <ReviewSection title="VLANs">
          {form.vlans.length === 0 ? <span className="text-zinc-600 text-xs">None</span> :
            form.vlans.map((v, i) => <div key={i} className="text-xs font-mono text-zinc-400">VLAN {v.id}: {v.name}</div>)}
        </ReviewSection>
        <ReviewSection title="Interfaces">
          <div className="text-xs text-zinc-400">Access: {form.interfaces.access_ports.length}</div>
          <div className="text-xs text-zinc-400">Trunk: {form.interfaces.trunk_ports.length}</div>
          <div className="text-xs text-zinc-400">Port-Ch: {form.interfaces.port_channels.length}</div>
        </ReviewSection>
        <ReviewSection title="Services">
          <div className="text-xs text-zinc-400">NTP: {form.services.ntp_servers.filter(Boolean).length} server(s)</div>
          <div className="text-xs text-zinc-400">Syslog: {form.services.syslog_servers.filter(Boolean).length} server(s)</div>
          <div className="text-xs text-zinc-400">SNMP: {form.services.snmp.version || "not set"}</div>
        </ReviewSection>
      </div>
    </div>
  );
}

function ReviewSection({ title, children }) {
  return (
    <div className="border border-border rounded-sm p-3" data-testid={`review-${title.toLowerCase()}`}>
      <div className="text-xs text-zinc-500 font-medium mb-2 uppercase tracking-wider">{title}</div>
      <div className="space-y-1">{children}</div>
    </div>
  );
}

function ReviewRow({ label, value, mono }) {
  return (
    <div className="flex justify-between text-xs">
      <span className="text-zinc-500">{label}</span>
      <span className={`text-zinc-300 ${mono ? "font-mono" : ""}`}>{value || "—"}</span>
    </div>
  );
}
