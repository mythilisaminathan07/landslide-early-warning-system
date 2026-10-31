import { useEffect, useState } from "react";

import {
  MapContainer,
  TileLayer,
  Marker,
  Popup,
  Circle,
  CircleMarker,
  Tooltip,
  useMap
} from "react-leaflet";

import {
  Map as MapIcon,
  Layers,
  Navigation,
} from "lucide-react";

import L from "leaflet";
import parseGeoraster from "georaster";
import GeoRasterLayer from "georaster-layer-for-leaflet";

import "leaflet/dist/leaflet.css";


function SusceptibilityLayer({ onLoaded }) {

  const map = useMap();

  const [_loading, setLoading] = useState(true);


  useEffect(() => {

    let rasterLayer = null;


    const loadRaster = async () => {

      try {

        const response = await fetch(
          "/rasters/Landslide_Susceptibility_Probability.tif"
        );


        if (!response.ok) {

          throw new Error(
            "Could not load susceptibility raster"
          );

        }


        const arrayBuffer =
          await response.arrayBuffer();


        const georaster =
          await parseGeoraster(arrayBuffer);


        console.log(
          "Susceptibility GeoRaster:",
          georaster
        );


        rasterLayer = new GeoRasterLayer({

          georaster: georaster,

          opacity: 0.65,

          resolution: 64,


          pixelValuesToColorFn: (values) => {

            const value = values[0];


            if (
              value === null ||
              value === undefined ||
              value === -9999
            ) {

              return null;

            }


            if (value < 0.2) {

              return "#2e8b57";

            }


            if (value < 0.4) {

              return "#9acd32";

            }


            if (value < 0.6) {

              return "#f1c40f";

            }


            if (value < 0.8) {

              return "#e67e22";

            }


            return "#c0392b";

          },

        });


        rasterLayer.addTo(map);


        map.fitBounds(
          rasterLayer.getBounds()
        );


        setLoading(false);


        if (onLoaded) {

          onLoaded(true);

        }

      } catch (error) {

        console.error(
          "Raster loading error:",
          error
        );


        setLoading(false);


        if (onLoaded) {

          onLoaded(false);

        }

      }

    };


    loadRaster();


    return () => {

      if (rasterLayer) {

        map.removeLayer(rasterLayer);

      }

    };

  }, [map, onLoaded]);


  return null;

}


/*
  Choose marker color based on
  current real-time risk.
*/

function getRiskColor(riskLevel) {

  switch (riskLevel) {

    case "LOW":
      return "#2e8b57";

    case "MEDIUM":
      return "#f1c40f";

    case "HIGH":
      return "#e67e22";

    case "CRITICAL":
      return "#c0392b";

    default:
      return "#2e7773";

  }

}


/*
  GIS Page
*/

function GIS() {

  const nilgirisCenter = [
    11.4102,
    76.6950,
  ];


  const [rasterLoaded, setRasterLoaded] =
    useState(false);


  const [sensors, setSensors] =
    useState([]);
  const [weatherLocations, setWeatherLocations] = useState([]);

  /*
    Load sensor risk data
    immediately and every 5 seconds.
  */

  useEffect(() => {


    const fetchRiskData = () => {

      fetch(
        "http://127.0.0.1:8000/api/risk"
      )

        .then((response) => {

          if (!response.ok) {

            throw new Error(
              "Could not load risk data"
            );

          }

          return response.json();

        })

        .then((data) => {

          setSensors(data.sensors);

        })

        .catch((error) => {

          console.error(
            "Risk data loading error:",
            error
          );

        });

    };


    // First request
    fetchRiskData();

    // Refresh every 3 seconds
    const interval = setInterval(
      fetchRiskData,
      3000
    );

    return () => {
      clearInterval(interval);
    };
  }, []);


  /*
    Load weather data for locations without physical sensors.
    Refresh every 60 seconds.
  */

  useEffect(() => {
    const fetchWeatherLocations = async () => {
      try {
        const response = await fetch("http://127.0.0.1:8000/api/weather");

        if (!response.ok) {
          throw new Error("Could not load weather locations");
        }

        const data = await response.json();
        setWeatherLocations(data.locations || []);
      } catch (error) {
        console.error("Weather locations loading error:", error);
      }
    };

    fetchWeatherLocations();

    const interval = setInterval(fetchWeatherLocations, 60000);
    return () => clearInterval(interval);
  }, []);


  /*
    Fix Leaflet marker icons.
  */

  useEffect(() => {

    delete L.Icon.Default.prototype._getIconUrl;


    L.Icon.Default.mergeOptions({

      iconRetinaUrl:
        "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png",

      iconUrl:
        "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png",

      shadowUrl:
        "https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png",

    });

  }, []);


  return (

    <div className="page">


      {/* Page heading */}

      <div className="page-heading">

        <h1>Live GIS</h1>

        <p>
          Real-time landslide susceptibility
          and sensor risk monitoring
        </p>

      </div>


      {/* Toolbar */}

      <div className="gis-toolbar">

        <div className="gis-info">

          <div className="stat-icon">

            <MapIcon size={19} />

          </div>


          <div>

            <strong>
              Nilgiris District
            </strong>

            <span>
              Susceptibility & Sensor Risk Map
            </span>

          </div>

        </div>


        <div className="gis-tools">

          <div className="gis-tool">

            <Layers size={16} />

            <span>
              Susceptibility
            </span>

          </div>


          <div className="gis-tool" style={{
            background: sensors.some(s => s.gps_valid && s.location?.latitude != null) ? "#e4f4eb" : "#fef3c7",
          }}>
            <Navigation size={16} color={sensors.some(s => s.gps_valid && s.location?.latitude != null) ? "#23845a" : "#b45309"} />
            <span style={{
              color: sensors.some(s => s.gps_valid && s.location?.latitude != null) ? "#23845a" : "#b45309",
              fontWeight: 600,
            }}>
              {sensors.some(s => s.gps_valid && s.location?.latitude != null) ? "Node GPS Active" : "No GPS fix"}
            </span>
          </div>

          <div className="gis-tool">
            <span
              style={{
                display: "inline-block",
                width: "8px",
                height: "8px",
                borderRadius: "50%",
                background: "#60a5fa",
                marginRight: "6px",
              }}
            />
            <span>Weather API</span>
          </div>

        </div>

      </div>


      {/* Map */}

      <div className="gis-map-card">

        <MapContainer

          center={nilgirisCenter}

          zoom={10}

          scrollWheelZoom={true}

          className="gis-map"

        >


          {/* OpenStreetMap */}

          <TileLayer

            attribution="&copy; OpenStreetMap contributors"

            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"

          />


          {/* ML susceptibility raster */}

          <SusceptibilityLayer
            onLoaded={setRasterLoaded}
          />


          {/* Nilgiris marker */}

          <Marker
            position={nilgirisCenter}
          >

            <Popup>

              <strong>
                Nilgiris District
              </strong>

              <br />

              Landslide monitoring area

            </Popup>

          </Marker>


          {/* Monitoring area */}

          <Circle

            center={nilgirisCenter}

            radius={15000}

            pathOptions={{

              color: "#2e7773",

              fillOpacity: 0,

            }}

          />


          {/* Live sensor risk markers */}
          {sensors.map((sensor) => {
            const hasGps = sensor.gps_valid && sensor.location?.latitude != null && sensor.location?.longitude != null;
            if (!hasGps) {
              // Only plot marker if gps_valid is true. Otherwise do not draw fake marker!
              return null;
            }

            const riskColor = getRiskColor(sensor.risk_level);
            const readings = sensor.readings || {};

            return (
              <CircleMarker
                key={sensor.sensor_id}
                center={[
                  sensor.location.latitude,
                  sensor.location.longitude,
                ]}
                radius={12}
                pathOptions={{
                  color: "#ffffff",
                  weight: 2,
                  fillColor: riskColor,
                  fillOpacity: 0.95,
                }}
              >
                <Popup>
                  <div style={{ minWidth: "190px" }}>
                    <strong style={{ fontSize: "14px" }}>{sensor.sensor_id}</strong>
                    <br />
                    <strong style={{ color: riskColor, fontSize: "13px" }}>
                      Risk Level: {sensor.risk_level || "LOW"}
                    </strong>
                    <br />
                    Risk Score: <strong>{sensor.risk_score ?? 0} / 100</strong>
                    <br />
                    <span style={{ fontSize: "11px", color: "#666" }}>
                      GPS: {sensor.location.latitude.toFixed(4)}, {sensor.location.longitude.toFixed(4)}
                    </span>
                    <hr style={{ margin: "6px 0", borderColor: "#eee" }} />
                    {readings.rain_detected !== undefined ? (
                      <div style={{ fontSize: "12px", lineHeight: "1.4" }}>
                        <div>Rain Sensor: <strong style={{ color: readings.rain_detected ? "#c0392b" : "#23845a" }}>{readings.rain_detected ? "Detected" : "Not detected"}</strong></div>
                        <div>Soil Moisture: <strong>{readings.soil_moisture != null ? `${readings.soil_moisture}%` : "—"}</strong></div>
                        <div>Tilt Angle: <strong>{readings.tilt != null ? `${readings.tilt}° (Δ ${readings.tilt_change ?? 0}°)` : "—"}</strong></div>
                        <div>Motion Gyro: <strong>{readings.motion_gyro != null ? `${readings.motion_gyro}°/s` : "—"}</strong></div>
                      </div>
                    ) : (
                      <div style={{ fontSize: "12px", lineHeight: "1.4" }}>
                        <div>Rainfall: <strong>{readings.rainfall ?? "—"} mm</strong></div>
                        <div>Soil Moisture: <strong>{readings.soil_moisture ?? "—"}%</strong></div>
                        <div>Tilt: <strong>{readings.tilt ?? "—"}°</strong></div>
                      </div>
                    )}
                    {sensor.contributing_factors && sensor.contributing_factors.length > 0 && (
                      <div style={{ marginTop: "6px", fontSize: "10px", color: "#444" }}>
                        <strong>Risk Factors:</strong>
                        <ul style={{ margin: "2px 0 0 12px", padding: 0 }}>
                          {sensor.contributing_factors.map((factor, idx) => (
                            <li key={idx}>{factor}</li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </div>
                </Popup>
              </CircleMarker>
            );
          })}


          {/* Weather API locations without physical sensors */}
          {weatherLocations.map((location) => (
            <CircleMarker
              key={location.location_id}
              center={[location.latitude, location.longitude]}
              radius={8}
              pathOptions={{
                color: "#2563eb",
                fillColor: "#60a5fa",
                fillOpacity: 0.9,
                weight: 2,
              }}
            >
              <Tooltip direction="top">
                Weather-monitored area
              </Tooltip>

              <Popup>
                <div>
                  <strong>{location.name}</strong>
                  <br />
                  <span>Monitoring type: Weather API</span>
                  <br />
                  <span>Location ID: {location.location_id}</span>

                  {location.weather?.available ? (
                    <>
                      <hr />
                      <div>
                        <strong>Current weather</strong>
                      </div>
                      <div>
                        Temperature: {location.weather.readings?.temperature_c ?? "N/A"} °C
                      </div>
                      <div>
                        Humidity: {location.weather.readings?.humidity_percent ?? "N/A"}%
                      </div>
                      <div>
                        Rain: {location.weather.readings?.rain_mm ?? "N/A"} mm
                      </div>
                      <div>
                        Precipitation: {location.weather.readings?.precipitation_mm ?? "N/A"} mm
                      </div>
                      <div>
                        Pressure: {location.weather.readings?.pressure_hpa ?? "N/A"} hPa
                      </div>
                      <div>
                        <small>
                          Source: {location.weather.source || "Weather API"}
                        </small>
                      </div>
                      {location.weather.observed_at && (
                        <div>
                          <small>
                            Updated: {location.weather.observed_at}
                          </small>
                        </div>
                      )}
                    </>
                  ) : (
                    <p>Weather data currently unavailable.</p>
                  )}
                </div>
              </Popup>
            </CircleMarker>
          ))}


        </MapContainer>

      </div>


      {/* Susceptibility legend */}

      <div className="gis-legend">


        <div className="legend-title">

          Susceptibility Level

        </div>


        <div className="legend-items">


          <div>

            <span
              className="legend-color very-low"
            ></span>

            Very Low

          </div>


          <div>

            <span
              className="legend-color low"
            ></span>

            Low

          </div>


          <div>

            <span
              className="legend-color medium"
            ></span>

            Medium

          </div>


          <div>

            <span
              className="legend-color high"
            ></span>

            High

          </div>


          <div>

            <span
              className="legend-color very-high"
            ></span>

            Very High

          </div>

        </div>


        {/* Raster status */}

        <div className="raster-status">

          <span
            className={
              rasterLoaded
                ? "status-success"
                : "status-loading"
            }
          >

            {rasterLoaded

              ? "Susceptibility raster loaded"

              : "Loading raster..."}

          </span>

        </div>


        {/* Sensor status */}

        <div className="raster-status">

          <span className="status-success">

            {sensors.length} live sensors connected

          </span>

        </div>


        {/* Weather API location status */}
        <div className="raster-status">
          <span className="status-success">
            {weatherLocations.length} weather-monitored locations
          </span>
        </div>

        {/* Map marker legend */}
        <div className="raster-status">
          <span
            style={{
              display: "inline-block",
              width: "10px",
              height: "10px",
              borderRadius: "50%",
              background: "#60a5fa",
              border: "2px solid #2563eb",
              marginRight: "8px",
            }}
          />
          Weather API location
        </div>


        {/* Risk marker legend */}

        <div className="sensor-risk-legend">

          <div className="legend-title">

            Live Sensor Risk

          </div>


          <div className="legend-items">


            <div>

              <span
                className="risk-dot risk-low"
              ></span>

              Low

            </div>


            <div>

              <span
                className="risk-dot risk-medium"
              ></span>

              Medium

            </div>


            <div>

              <span
                className="risk-dot risk-high"
              ></span>

              High

            </div>


            <div>

              <span
                className="risk-dot risk-critical"
              ></span>

              Critical

            </div>

          </div>

        </div>

      </div>


    </div>

  );

}


export default GIS;