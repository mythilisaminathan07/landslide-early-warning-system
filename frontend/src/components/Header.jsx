import { Bell, Circle } from "lucide-react";

function Header() {
  return (
    <header className="top-header">

      <div className="header-title">
        <h1>Landslide Monitoring Dashboard</h1>
        <p>Nilgiris District, Tamil Nadu</p>
      </div>

      <div className="header-actions">

        <div className="live-status">
          <Circle size={9} fill="currentColor" />
          <span>LIVE</span>
        </div>

        <button className="notification-btn">
          <Bell size={19} />
          <span className="notification-count">3</span>
        </button>

      </div>

    </header>
  );
}

export default Header;