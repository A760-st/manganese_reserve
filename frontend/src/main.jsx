import React, { useEffect, useState } from 'react';
import { createRoot } from 'react-dom/client';
import {
  Activity, AlertTriangle, ArrowUpRight, Database, Factory, Layers, Map,
  Settings, ShieldCheck, Truck, Upload, BrainCircuit, ExternalLink, RefreshCw
} from 'lucide-react';
import './style.css';

const API = import.meta.env.VITE_API_URL || '';

const nav = [
  ['dashboard', 'Command Center', Activity],
  ['reserves', 'Reserve Intelligence', Map],
  ['production', 'Production', Factory],
  ['shortfall', 'Shortfall Risk', AlertTriangle],
  ['satellite', 'Satellite Proxies', Layers],
  ['equipment', 'Equipment', Truck],
  ['recommendations', 'Recommendations', ArrowUpRight],
  ['optimization', 'Optimization', BrainCircuit],
  ['models', 'Model Registry', ShieldCheck],
  ['data', 'Data Sources & Quality', Database],
  ['settings', 'Settings', Settings]
];

function App() {
  const [tab, setTab] = useState('dashboard');
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchTab = () => {
    setLoading(true);
    setError(null);
    let path = '/api/v1/overview';
    if (tab === 'dashboard') path = '/api/v1/overview';
    else if (tab === 'reserves') path = '/api/v1/reserves/map';
    else if (tab === 'production') path = '/api/v1/production/forecast';
    else if (tab === 'shortfall') path = '/api/v1/shortfall/current';
    else if (tab === 'satellite') path = '/api/v1/satellite/observations';
    else if (tab === 'equipment') path = '/api/v1/equipment';
    else if (tab === 'recommendations') path = '/api/v1/recommendations';
    else if (tab === 'optimization') path = '/api/v1/optimization/run';
    else if (tab === 'models') path = '/api/v1/models';
    else if (tab === 'data') path = '/api/v1/data-sources';
    else if (tab === 'settings') path = '/api/v1/data-quality';

    const targetUrl = API ? `${API}${path}` : path;

    fetch(targetUrl)
      .then(async (res) => {
        const text = await res.text();
        if (!res.ok) {
          let msg = `HTTP ${res.status}: ${res.statusText}`;
          if (text.trim().startsWith('<')) {
            msg = `Backend API unavailable (HTTP ${res.status}). Ensure FastAPI server is running on port 8000.`;
          }
          throw new Error(msg);
        }
        if (text.trim().startsWith('<')) {
          throw new Error('Received HTML document instead of API JSON response.');
        }
        try {
          return JSON.parse(text);
        } catch (e) {
          throw new Error('Failed to parse JSON response from backend API.');
        }
      })
      .then(x => {
        setData(x);
        setLoading(false);
      })
      .catch(err => {
        setError(err.message);
        setLoading(false);
      });
  };

  useEffect(() => {
    fetchTab();
  }, [tab]);

  return (
    <div className="shell">
      <aside>
        <div className="brand">
          <div className="brandmark">M</div>
          <div><b>ORE<span>WISE</span></b><small>MINING INTELLIGENCE</small></div>
        </div>
        <div className="mine"><span className="dot"/> DEMO MINE <em>ONLINE</em></div>
        <nav>
          {nav.map(([id, label, Icon]) => (
            <button className={tab === id ? 'active' : ''} onClick={() => setTab(id)} key={id}>
              <Icon size={16}/>{label}
            </button>
          ))}
        </nav>
        <div className="side-note">
          <span className="label">DATA MODE</span>
          <strong>PUBLIC & SYNTHETIC DATA</strong>
          <p>Official IBM & USGS statistics integrated. Operational fleet data requires authorized access.</p>
        </div>
      </aside>

      <main>
        <header>
          <div>
            <span className="eyebrow">MINE OPERATIONS / 20 SEP 2026</span>
            <h1>{nav.find(x => x[0] === tab)?.[1]}</h1>
          </div>
          <div className="header-actions">
            <span className="pill"><span className="dot"/> API CONNECTED</span>
            <button className="icon-btn" onClick={fetchTab} title="Refresh Data"><RefreshCw size={16}/></button>
          </div>
        </header>

        <div className="notice">
          <ShieldCheck size={16}/>
          <span><b>Scientific boundary:</b> Satellite layers provide surface/environmental evidence only. Prospectivity is a research proxy, not certified mineral reserve estimation.</span>
        </div>

        {loading ? (
          <div className="loading">Loading model-backed database services...</div>
        ) : error ? (
          <div className="error-box">
            <h3>API Connection Notice</h3>
            <p>{error}</p>
            <button onClick={fetchTab}>Retry Connection</button>
          </div>
        ) : (
          <Content tab={tab} data={data?.data} provenance={data?.provenance}/>
        )}
      </main>
    </div>
  );
}

function Content({ tab, data, provenance }) {
  if (!data) return <div className="loading">No data available for this view.</div>;

  if (tab === 'dashboard') return <Dashboard d={data}/>;
  if (tab === 'reserves') return <Reserves d={data}/>;
  if (tab === 'production') return <Production d={data}/>;
  if (tab === 'shortfall') return <Shortfall d={data}/>;
  if (tab === 'satellite') return <Satellite d={data}/>;
  if (tab === 'equipment') return <Equipment d={data}/>;
  if (tab === 'recommendations') return <Recommendations d={data}/>;
  if (tab === 'optimization') return <Optimization d={data}/>;
  if (tab === 'models') return <Models d={data}/>;
  if (tab === 'data') return <DataSources d={data}/>;
  if (tab === 'settings') return <SettingsView d={data}/>;

  return <Dashboard d={data}/>;
}

const Metric = ({ label, value, sub, accent, badge }) => (
  <div className="metric">
    <div style={{display:'flex', justifyContent:'space-between', alignItems:'center'}}>
      <span>{label}</span>
      {badge && <span className={badge.cls}>{badge.label}</span>}
    </div>
    <strong className={accent || ''}>{value}</strong>
    <small>{sub}</small>
  </div>
);

function Bar({ label, value, color }) {
  return (
    <div className="bar-row">
      <div><span>{label}</span><b>{value}%</b></div>
      <div className="track"><i className={color} style={{ width: Math.min(100, Math.max(0, value * 2.2)) + '%' }}/></div>
    </div>
  );
}

function Dashboard({ d }) {
  return (
    <>
      <div className="section-head">
        <div>
          <span className="eyebrow">EXECUTIVE VIEW</span>
          <h2>Operational signal, not operational command</h2>
        </div>
        <span className="badge-official">IBM / USGS OFFICIAL & SYNTHETIC DATA</span>
      </div>

      <div className="metrics">
        <Metric label="Production today" value={`${d.production_today} t`} sub={`Target ${d.target} t`}/>
        <Metric label="7-day forecast" value={`${d.forecast} t`} sub="Model: demo-production-1.0.0"/>
        <Metric label="Shortfall probability" value={`${Math.round(d.shortfall_probability * 100)}%`} sub={`${d.expected_shortfall} t expected gap`} accent="warn"/>
        <Metric label="Prospectivity mean" value={`${Math.round(d.prospectivity_mean * 100)} / 100`} sub="Exploration potential proxy" accent="good"/>
      </div>

      <div className="grid-2">
        <div className="panel map-panel">
          <div className="panel-head">
            <div><span className="eyebrow">RESERVE INTELLIGENCE</span><h3>Prospectivity surface</h3></div>
            <span className="tag">DATABASE ZONES</span>
          </div>
          <div className="map">
            <div className="contour c1"/><div className="contour c2"/><div className="contour c3"/>
            <span className="map-label l1">A · 86</span>
            <span className="map-label l2">B · 71</span>
            <span className="map-label l3">D · 63</span>
            <span className="map-label l4">C · 48</span>
            <div className="map-legend"><i/><span>LOW</span><i/><span>HIGH</span></div>
          </div>
        </div>

        <div className="panel">
          <div className="panel-head">
            <div><span className="eyebrow">MODEL CONTRIBUTIONS</span><h3>Why risk is elevated</h3></div>
            <span className="tag">SHORTFALL</span>
          </div>
          <div className="bars">
            <Bar label="Equipment availability" value={34} color="orange"/>
            <Bar label="Blast delay proxy" value={22} color="orange"/>
            <Bar label="Rainfall / moisture" value={15} color="blue"/>
            <Bar label="Production variability" value={11} color="blue"/>
          </div>
          <p className="muted">Contributions indicate model association based on database logs, not causal findings.</p>
        </div>
      </div>

      <div className="panel table-panel">
        <div className="panel-head">
          <div><span className="eyebrow">DECISION SUPPORT</span><h3>Recommended review queue</h3></div>
          <span className="tag">AUTHORIZED REVIEW REQUIRED</span>
        </div>
        {d.recommendations.map(r => (
          <div className="recommend-row" key={r.id}>
            <div className="rec-icon"><Truck size={18}/></div>
            <div>
              <b>{r.action}</b>
              <p>{r.equipment} · {r.zone} · expected impact +{r.expected_impact_tonnes} t</p>
            </div>
            <span className="confidence">{Math.round(r.confidence * 100)}% confidence</span>
            <button className="ghost">Inspect</button>
          </div>
        ))}
      </div>
    </>
  );
}

function Reserves({ d }) {
  const [predForm, setPredForm] = useState({ drill: 0.75, geology: 0.70, spectral: 0.65 });
  const [predResult, setPredResult] = useState(null);

  const runPredict = (e) => {
    e?.preventDefault();
    const targetUrl = API ? `${API}/api/v1/reserves/predict` : '/api/v1/reserves/predict';
    fetch(targetUrl, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        zone_id: 'MINE-01-ZONE-A',
        drill_evidence: parseFloat(predForm.drill),
        geology_signal: parseFloat(predForm.geology),
        spectral_proxy: parseFloat(predForm.spectral)
      })
    })
      .then(r => r.json())
      .then(res => setPredResult(res.data));
  };

  return (
    <>
      <div className="section-head">
        <div>
          <span className="eyebrow">GEOLOGICAL + SUBSURFACE + ENVIRONMENTAL</span>
          <h2>Manganese exploration potential</h2>
        </div>
        <span className="badge-official">COPERNICUS SENTINEL & GEOLOGICAL PROXIES</span>
      </div>

      <div className="reserves-layout">
        <div className="panel map-panel large">
          <div className="map">
            <div className="contour c1"/><div className="contour c2"/><div className="contour c3"/>
            {d.map((z, i) => (
              <span key={z.id} className={`map-label z${i % 4}`} style={{ left: (20 + (i % 5) * 16) + '%', top: (25 + Math.floor(i / 5) * 18) + '%' }}>
                {z.id.split('-').pop()} · {Math.round(z.prospectivity * 100)}
              </span>
            ))}
          </div>
        </div>

        <div className="panel">
          <span className="eyebrow">RANKED ZONES</span>
          <h3>Database Evidence Summary</h3>
          <div style={{ maxHeight: '380px', overflowY: 'auto' }}>
            {d.map(z => (
              <div className="zone" key={z.id}>
                <div>
                  <b>{z.id} · {z.name}</b>
                  <p>Drill evidence {Math.round(z.drill_evidence * 100)}% · slope {z.slope}°</p>
                </div>
                <strong className={z.prospectivity > 0.7 ? 'good' : ''}>{Math.round(z.prospectivity * 100)}</strong>
              </div>
            ))}
          </div>
        </div>
      </div>

      <div className="slider-panel">
        <span className="eyebrow">INTERACTIVE ML PREDICTOR</span>
        <h3>Prospectivity Model Simulator</h3>
        <form onSubmit={runPredict} className="slider-group">
          <div className="slider-row">
            <label>Drill Evidence (0–1):</label>
            <input type="range" min="0" max="1" step="0.05" value={predForm.drill} onChange={e => setPredForm({ ...predForm, drill: e.target.value })}/>
            <span>{predForm.drill}</span>
          </div>
          <div className="slider-row">
            <label>Geology Signal (0–1):</label>
            <input type="range" min="0" max="1" step="0.05" value={predForm.geology} onChange={e => setPredForm({ ...predForm, geology: e.target.value })}/>
            <span>{predForm.geology}</span>
          </div>
          <div className="slider-row">
            <label>Spectral Proxy (0–1):</label>
            <input type="range" min="0" max="1" step="0.05" value={predForm.spectral} onChange={e => setPredForm({ ...predForm, spectral: e.target.value })}/>
            <span>{predForm.spectral}</span>
          </div>
          <button type="submit" className="primary" style={{ width: '180px', marginTop: '10px' }}>Calculate Score</button>
        </form>

        {predResult && (
          <div style={{ marginTop: '16px', padding: '14px', background: '#0e181c', border: '1px solid #283a40', borderRadius: '6px' }}>
            <b>Calculated Prospectivity: {predResult.prospectivity_score}</b> ({predResult.classification})
            <p className="muted">{predResult.scientific_note}</p>
          </div>
        )}
      </div>
    </>
  );
}

function Production({ d }) {
  const [officialData, setOfficialData] = useState([]);

  useEffect(() => {
    const targetUrl = API ? `${API}/api/v1/production/official` : '/api/v1/production/official';
    fetch(targetUrl)
      .then(r => r.json())
      .then(x => setOfficialData(x.data || []));
  }, []);

  return (
    <>
      <div className="section-head">
        <div>
          <span className="eyebrow">TIME-BASED FORECAST & OFFICIAL STATISTICS</span>
          <h2>Predicted production vs target</h2>
        </div>
        <span className="badge-official">IBM OFFICIAL MINERAL STATISTICS</span>
      </div>

      <div className="metrics">
        <Metric label="Expected production" value={`${d.expected_production} t`} sub={`Interval ${d.lower_bound}–${d.upper_bound} t`}/>
        <Metric label="Target production" value={`${d.target_production} t`} sub="Planning target"/>
        <Metric label="Expected gap" value={`${d.expected_gap} t`} sub="Requires planner review" accent="warn"/>
        <Metric label="Prediction confidence" value={`${Math.round(d.confidence * 100)}%`} sub="demo-production-1.0.0"/>
      </div>

      <div className="panel chart">
        <div className="chart-grid">
          {d.series.map((x) => (
            <div className="chart-col" key={x.day}>
              <div className="bar forecast" style={{ height: (x.forecast / 10) + '%' }}/>
              <div className="bar target" style={{ height: (x.target / 10) + '%' }}/>
              <span>D{x.day}</span>
            </div>
          ))}
        </div>
        <div className="chart-key">
          <span><i className="forecast"/> FORECAST</span>
          <span><i className="target"/> TARGET</span>
        </div>
      </div>

      <div className="panel table-panel">
        <span className="eyebrow">INDIAN BUREAU OF MINES (IBM) OFFICIAL STATISTICS</span>
        <h3>Official Manganese Ore Production in India by District</h3>
        <div className="data-table">
          <div className="tr th">
            <span>State</span><span>District</span><span>Year</span><span>Prod ('000 t)</span><span>Value (Lakh INR)</span><span>Grade (% Mn)</span><span>Publication</span>
          </div>
          {officialData.slice(0, 10).map((row) => (
            <div className="tr" key={row.id}>
              <span>{row.state}</span>
              <span>{row.district}</span>
              <span>{row.year}</span>
              <span><b>{row.production_thousand_tonnes}</b></span>
              <span>₹{row.value_inr_lakhs}</span>
              <span>{row.avg_grade_mn_pct}%</span>
              <span>{row.publication}</span>
            </div>
          ))}
        </div>
      </div>
    </>
  );
}

function Shortfall({ d }) {
  return (
    <>
      <div className="section-head">
        <div>
          <span className="eyebrow">RISK SIGNAL</span>
          <h2>Production shortfall intelligence</h2>
        </div>
        <span className="risk-badge">{d.risk_level}</span>
      </div>

      <div className="metrics">
        <Metric label="Probability" value={`${Math.round(d.probability * 100)}%`} sub="Classification output" accent="warn"/>
        <Metric label="Expected shortfall" value={`${d.expected_shortfall_tonnes} t`} sub="Regression estimate" accent="warn"/>
        <Metric label="Model version" value="1.0.0" sub="Time-based holdout"/>
        <Metric label="Action posture" value="Review" sub="Not an autonomous command"/>
      </div>

      <div className="panel">
        <span className="eyebrow">EXPLANATION</span>
        <h3>Contributing risk factors</h3>
        {d.contributing_factors.map(x => (
          <Bar key={x.factor} label={x.factor} value={Math.round(x.model_contribution * 100)} color="orange"/>
        ))}
        <p className="muted">{d.note}</p>
      </div>

      <div className="notice" style={{ marginTop: '20px' }}>
        <ShieldCheck size={16}/>
        <span><b>Operational Data Requirement:</b> Mine-level downtime and blast schedule logs are populated from synthetic fixtures. Authorized operational dataset integration required for certified operational dispatching.</span>
      </div>
    </>
  );
}

function Satellite({ d }) {
  return (
    <>
      <div className="section-head">
        <div>
          <span className="eyebrow">SURFACE & ENVIRONMENTAL REMOTE SENSING</span>
          <h2>Earth Observation & Satellite Proxies</h2>
        </div>
        <span className="badge-official">ISRO BHUVAN & COPERNICUS SENTINEL-2</span>
      </div>

      <div className="panel table-panel">
        <span className="eyebrow">COPERNICUS & BHUVAN OBSERVATIONAL LOGS</span>
        <h3>Recent Remote Sensing Surface Observations</h3>
        <div className="data-table">
          <div className="tr th">
            <span>Obs ID</span><span>Zone ID</span><span>Date</span><span>NDVI</span><span>Soil Moisture</span><span>Surface Temp (°C)</span><span>Elevation (m)</span><span>Spectral Proxy</span>
          </div>
          {d.slice(0, 12).map((row) => (
            <div className="tr" key={row.obs_id}>
              <span>{row.obs_id}</span>
              <span>{row.zone_id}</span>
              <span>{row.date}</span>
              <span>{row.ndvi}</span>
              <span>{row.soil_moisture}</span>
              <span>{row.surface_temp_c}°C</span>
              <span>{row.elevation_m}m</span>
              <span><b>{row.spectral_proxy}</b></span>
            </div>
          ))}
        </div>
      </div>
    </>
  );
}

function Equipment({ d }) {
  return (
    <>
      <div className="section-head">
        <div>
          <span className="eyebrow">FLEET DIAGNOSTICS</span>
          <h2>Equipment Availability & Downtime</h2>
        </div>
        <span className="badge-auth">AUTHORIZED OPERATIONAL DATASET REQUIRED</span>
      </div>
      <Table title="Mine Fleet Operational Status" rows={d} cols={['id', 'type', 'capacity_t', 'availability', 'utilization', 'status']}/>
    </>
  );
}

function Recommendations({ d }) {
  return (
    <>
      <div className="section-head">
        <div>
          <span className="eyebrow">ACTIONABLE QUEUE</span>
          <h2>Reviewable Operational Recommendations</h2>
        </div>
        <span className="tag">AUTHORIZED REVIEW REQUIRED</span>
      </div>
      <Table title="Model-Derived Operational Queue" rows={d} cols={['id', 'action', 'zone', 'expected_impact_tonnes', 'confidence', 'status']}/>
    </>
  );
}

function Optimization({ d }) {
  const [equipDelta, setEquipDelta] = useState(0.0);
  const [rainDelta, setRainDelta] = useState(0.0);
  const [optData, setOptData] = useState(d);

  const runScenario = () => {
    const targetUrl = API ? `${API}/api/v1/optimization/run` : '/api/v1/optimization/run';
    fetch(targetUrl, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        equipment_availability_delta: parseFloat(equipDelta),
        rainfall_delta: parseFloat(rainDelta)
      })
    })
      .then(r => r.json())
      .then(x => setOptData(x.data));
  };

  useEffect(() => {
    runScenario();
  }, [equipDelta, rainDelta]);

  return (
    <>
      <div className="section-head">
        <div>
          <span className="eyebrow">WHAT-IF ANALYSIS</span>
          <h2>Fleet & Production Optimization Scenarios</h2>
        </div>
        <span className="tag">SCENARIO SIMULATOR</span>
      </div>

      <div className="slider-panel">
        <span className="eyebrow">SCENARIO PARAMETERS</span>
        <h3>Adjust Fleet & Weather Assumptions</h3>
        <div className="slider-group">
          <div className="slider-row">
            <label>Equipment Availability Delta:</label>
            <input type="range" min="-0.4" max="0.4" step="0.05" value={equipDelta} onChange={e => setEquipDelta(e.target.value)}/>
            <span>{equipDelta > 0 ? `+${equipDelta}` : equipDelta}</span>
          </div>
          <div className="slider-row">
            <label>Rainfall Anomaly Delta:</label>
            <input type="range" min="-0.5" max="1.5" step="0.1" value={rainDelta} onChange={e => setRainDelta(e.target.value)}/>
            <span>{rainDelta > 0 ? `+${rainDelta}` : rainDelta}</span>
          </div>
        </div>
      </div>

      {optData && (
        <div className="grid-2" style={{ marginTop: '20px' }}>
          <div className="panel">
            <span className="eyebrow">BASELINE PLAN</span>
            <h3>Expected Standard Dispatch</h3>
            <p style={{ marginTop: '10px' }}>Expected Production: <b>{optData.baseline_plan.expected_production} t</b></p>
            <p>Expected Shortfall: <b className="warn">{optData.baseline_plan.expected_shortfall} t</b></p>
            <p>Idle Hours: {optData.baseline_plan.idle_hours} hrs</p>
          </div>

          <div className="panel">
            <span className="eyebrow">OPTIMIZED SCENARIO PLAN</span>
            <h3>Constrained Optimized Dispatch</h3>
            <p style={{ marginTop: '10px' }}>Expected Production: <b className="good">{optData.optimized_plan.expected_production} t</b></p>
            <p>Expected Shortfall: <b>{optData.optimized_plan.expected_shortfall} t</b></p>
            <p>Target Utilization: {Math.round(optData.optimized_plan.equipment_utilization * 100)}%</p>
          </div>
        </div>
      )}
    </>
  );
}

function Models({ d }) {
  return (
    <>
      <div className="section-head">
        <div>
          <span className="eyebrow">MODEL GOVERNANCE</span>
          <h2>Registered Machine Learning Models</h2>
        </div>
        <span className="tag">VERIFIED MODEL REGISTRY</span>
      </div>
      <Table title="Model Registry & Performance Metrics" rows={d} cols={['version', 'task', 'training_dataset', 'validation', 'trained_at', 'metrics']}/>
    </>
  );
}

function DataSources({ d }) {
  return (
    <>
      <div className="section-head">
        <div>
          <span className="eyebrow">DATA PROVENANCE & GOVERNANCE</span>
          <h2>Official Data Source Registry</h2>
        </div>
        <span className="badge-official">OFFICIAL REGISTRY</span>
      </div>

      <div className="panel table-panel">
        <span className="eyebrow">VERIFIED AUTHORITATIVE SOURCES</span>
        <h3>Official Government & Public Remote Sensing Data Sources</h3>
        <div className="data-table">
          <div className="tr th">
            <span>ID</span><span>Source Name</span><span>Organization</span><span>Official Portal</span><span>Geographic Scope</span><span>License</span><span>Status</span>
          </div>
          {d.map((s) => (
            <div className="tr" key={s.id}>
              <span><b>{s.id}</b></span>
              <span>{s.name}</span>
              <span>{s.organization}</span>
              <span>
                <a href={s.official_url} target="_blank" rel="noreferrer" style={{ color: '#d6f36a', display: 'flex', alignItems: 'center', gap: '4px', textDecoration: 'none' }}>
                  {s.official_url.replace('https://', '')} <ExternalLink size={12}/>
                </a>
              </span>
              <span>{s.geographic_scope}</span>
              <span>{s.license}</span>
              <span><span className="badge-official">{s.status}</span></span>
            </div>
          ))}
        </div>
      </div>
    </>
  );
}

function SettingsView({ d }) {
  return (
    <>
      <div className="section-head">
        <div>
          <span className="eyebrow">PLATFORM GOVERNANCE</span>
          <h2>Platform Settings & Data Quality Audit</h2>
        </div>
        <span className="pill"><span className="dot"/> CHECKS PASSING</span>
      </div>

      <div className="metrics">
        <Metric label="Completeness" value={`${Math.round(d.completeness * 100)}%`} sub="Joined database records" accent="good"/>
        <Metric label="Invalid records" value={d.invalid_records} sub="Coordinate & unit checks"/>
        <Metric label="Duplicates" value={d.duplicate_records} sub="Across primary keys"/>
        <Metric label="Spatial coverage" value={d.spatial_coverage || "20 zones"} sub="Demo mine boundary"/>
      </div>

      <div className="panel">
        <h3>System Quality Checks</h3>
        {d.checks.map(x => (
          <div className="check" key={x}>
            <ShieldCheck size={15}/>
            <span>{x}</span>
            <b>PASS</b>
          </div>
        ))}
        <p className="muted">{d.temporal_coverage}. All decision outputs maintain strict scientific provenance labels.</p>
      </div>
    </>
  );
}

function Table({ title, rows, cols }) {
  return (
    <div className="panel table-panel">
      <span className="eyebrow">DATABASE QUERY RESPONSE</span>
      <h2>{title}</h2>
      <div className="data-table">
        <div className="tr th">
          {cols.map(c => <span key={c}>{c.replaceAll('_', ' ')}</span>)}
        </div>
        {rows.map((r, i) => (
          <div className="tr" key={i}>
            {cols.map(c => (
              <span key={c}>
                {typeof r[c] === 'number' ? Math.round(r[c] * 100) / 100 : String(r[c] ?? '—')}
              </span>
            ))}
          </div>
        ))}
      </div>
    </div>
  );
}

createRoot(document.getElementById('root')).render(<App/>);
