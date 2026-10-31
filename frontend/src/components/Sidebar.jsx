import {
  LayoutDashboard,
  Map,
  RadioTower,
  BrainCircuit,
  BellRing,
  History,
  ShieldAlert,
  Activity,
} from "lucide-react";

import { NavLink } from "react-router-dom";

function Sidebar() {
  const menuItems = [
    {
      name: "Dashboard",
      path: "/",
      icon: LayoutDashboard,
    },
    {
      name: "Live GIS",
      path: "/gis",
      icon: Map,
    },
    {
      name: "Sensors",
      path: "/sensors",
      icon: RadioTower,
    },
    {
      name: "ML Prediction",
      path: "/ml",
      icon: BrainCircuit,
    },
    {
      name: "Alerts",
      path: "/alerts",
      icon: BellRing,
    },
    {
      name: "History",
      path: "/history",
      icon: History,
    },
  ];

  return (
    <aside className="sidebar">

      <div className="sidebar-logo">
        <div className="logo-icon">
          <ShieldAlert size={24} />
        </div>

        <div>
          <h2>Landslide</h2>
          <span>Early Warning</span>
        </div>
      </div>

      <nav className="sidebar-nav">

        <div className="nav-title">
          MONITORING
        </div>

        {menuItems.map((item) => {
          const Icon = item.icon;

          return (
            <NavLink
              key={item.path}
              to={item.path}
              className={({ isActive }) =>
                isActive ? "nav-item active" : "nav-item"
              }
            >
              <Icon size={19} />
              <span>{item.name}</span>
            </NavLink>
          );
        })}

      </nav>

      <div className="sidebar-status">
        <div className="status-icon">
          <Activity size={18} />
        </div>

        <div>
          <strong>System Online</strong>
          <span>Monitoring active</span>
        </div>

        <span className="online-dot"></span>
      </div>

    </aside>
  );
}

export default Sidebar;