import { NavLink, useLocation } from "react-router-dom";
import { LayoutDashboard, FilePlus2, Library, Server } from "lucide-react";

const navItems = [
  { to: "/", icon: LayoutDashboard, label: "Dashboard", exact: true },
  { to: "/projects/new", icon: FilePlus2, label: "New Config" },
  { to: "/templates", icon: Library, label: "Templates" },
];

export const Sidebar = () => {
  const location = useLocation();

  return (
    <aside
      data-testid="sidebar-nav"
      className="w-56 flex-shrink-0 border-r border-border bg-card flex flex-col"
    >
      <div className="h-14 flex items-center px-4 border-b border-border gap-2">
        <Server className="w-5 h-5 text-blue-500" />
        <span className="font-semibold text-sm tracking-tight text-foreground">
          NetConfig Builder
        </span>
      </div>

      <nav className="flex-1 py-3 px-2 space-y-0.5">
        {navItems.map((item) => {
          const isActive = item.exact
            ? location.pathname === item.to
            : location.pathname.startsWith(item.to);
          return (
            <NavLink
              key={item.to}
              to={item.to}
              data-testid={`nav-${item.label.toLowerCase().replace(/\s/g, "-")}`}
              className={`flex items-center gap-2.5 px-3 py-2 rounded-sm text-sm font-medium btn-transition ${
                isActive
                  ? "bg-blue-600/15 text-blue-400 border-l-2 border-blue-500"
                  : "text-zinc-400 hover:text-zinc-200 hover:bg-zinc-800/60"
              }`}
            >
              <item.icon className="w-4 h-4" />
              {item.label}
            </NavLink>
          );
        })}
      </nav>

      <div className="p-3 border-t border-border">
        <div className="text-[11px] text-zinc-600 leading-tight">
          NetConfig Builder v1.0<br />
          Cisco IOS-XE Config Tool
        </div>
      </div>
    </aside>
  );
};
