import { Routes, Route } from "react-router-dom";

import Sidebar from "./components/Sidebar";
import Header from "./components/Header";

import Dashboard from "./pages/Dashboard";
import GIS from "./pages/GIS";
import Sensors from "./pages/Sensors";
import MLPrediction from "./pages/MLPrediction";
import Alerts from "./pages/Alerts";
import History from "./pages/History";

import "./App.css";

function App() {
  return (
    <div className="app-layout">

      <Sidebar />

      <div className="main-area">

        <Header />

        <main className="content-area">

          <Routes>

            <Route path="/" element={<Dashboard />} />
            <Route path="/gis" element={<GIS />} />
            <Route path="/sensors" element={<Sensors />} />
            <Route path="/ml" element={<MLPrediction />} />
            <Route path="/alerts" element={<Alerts />} />
            <Route path="/history" element={<History />} />

          </Routes>

        </main>

      </div>

    </div>
  );
}

export default App;