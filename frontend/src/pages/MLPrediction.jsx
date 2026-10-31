import { useState } from "react";

import {
  BrainCircuit,
  Mountain,
  Waves,
  Compass,
  CloudRain,
  Layers,
  Map,
  Route,
  AlertTriangle,
  CheckCircle2,
} from "lucide-react";

function MLPrediction() {
  const [formData, setFormData] = useState({
    DEM_Final: "",
    Slope: "",
    Aspect: "",
    Rainfall: "",
    Clay: "",
    LULC: "",
    Road_Dist: "",
  });

  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const fields = [
    {
      name: "DEM_Final",
      label: "Elevation / DEM",
      placeholder: "e.g. 1800",
      icon: Mountain,
    },
    {
      name: "Slope",
      label: "Slope",
      placeholder: "e.g. 25",
      icon: Waves,
    },
    {
      name: "Aspect",
      label: "Aspect",
      placeholder: "e.g. 180",
      icon: Compass,
    },
    {
      name: "Rainfall",
      label: "Rainfall",
      placeholder: "e.g. 150",
      icon: CloudRain,
    },
    {
      name: "Clay",
      label: "Clay Content",
      placeholder: "e.g. 30",
      icon: Layers,
    },
    {
      name: "LULC",
      label: "Land Use / Land Cover",
      placeholder: "e.g. 40",
      icon: Map,
    },
    {
      name: "Road_Dist",
      label: "Distance to Road",
      placeholder: "e.g. 100",
      icon: Route,
    },
  ];

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    setLoading(true);
    setResult(null);

    try {
      const response = await fetch(
        "http://127.0.0.1:8000/api/predict",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            DEM_Final: Number(formData.DEM_Final),
            Slope: Number(formData.Slope),
            Aspect: Number(formData.Aspect),
            Rainfall: Number(formData.Rainfall),
            Clay: Number(formData.Clay),
            LULC: Number(formData.LULC),
            Road_Dist: Number(formData.Road_Dist),
          }),
        }
      );

      if (!response.ok) {
        throw new Error("Prediction request failed");
      }

      const data = await response.json();

      setResult(data);
    } catch (error) {
      console.error(error);
      alert("Could not connect to the ML backend.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="page">

      <div className="page-heading">
        <h1>ML Prediction</h1>

        <p>
          Analyze landslide susceptibility using the trained
          Random Forest model.
        </p>
      </div>

      <div className="prediction-container">

        <div className="prediction-card">

          <div className="section-header">
            <div>
              <h2>Environmental Factors</h2>

              <p
                style={{
                  margin: "6px 0 0",
                  color: "#7a8d8b",
                  fontSize: "12px",
                }}
              >
                Enter the seven GIS factors used by the ML model.
              </p>
            </div>

            <div className="stat-icon">
              <BrainCircuit size={20} />
            </div>
          </div>

          <form
            onSubmit={handleSubmit}
            className="prediction-form"
          >

            {fields.map((field) => {
              const Icon = field.icon;

              return (
                <div className="form-group" key={field.name}>

                  <label>
                    <span
                      style={{
                        display: "flex",
                        alignItems: "center",
                        gap: "6px",
                      }}
                    >
                      <Icon size={15} />
                      {field.label}
                    </span>
                  </label>

                  <input
                    type="number"
                    step="any"
                    name={field.name}
                    value={formData[field.name]}
                    onChange={handleChange}
                    placeholder={field.placeholder}
                    required
                  />

                </div>
              );
            })}

            <button
              type="submit"
              className="predict-btn"
              disabled={loading}
            >
              <BrainCircuit size={18} />

              {loading
                ? "Analyzing..."
                : "Predict Landslide Risk"}
            </button>

          </form>

        </div>

        {result && (
          <div className="prediction-result">

            <div className="section-header">

              <h2>Prediction Result</h2>

              {result.prediction === 1 ? (
                <AlertTriangle size={22} />
              ) : (
                <CheckCircle2 size={22} />
              )}

            </div>

            <div className="result-grid">

              <div className="result-item">
                <span>Prediction</span>

                <strong>
                  {result.prediction === 1
                    ? "Landslide"
                    : "Non-Landslide"}
                </strong>
              </div>

              <div className="result-item">
                <span>Probability</span>

                <strong>
                  {result.probability}%
                </strong>
              </div>

              <div className="result-item">
                <span>Risk Level</span>

                <strong>
                  {result.risk_level}
                </strong>
              </div>

            </div>

          </div>
        )}

      </div>

    </div>
  );
}

export default MLPrediction;