import React, { useState } from 'react';
import {
  Sun,
  Thermometer,
  Layers,
  MapPin,
  ShieldCheck,
  AlertTriangle,
  HelpCircle,
  Zap,
  TrendingUp,
  FileText,
  MessageSquare,
  ChevronRight,
  Sliders,
  DollarSign,
  Maximize2,
  RotateCw,
  Plus,
  Trash2,
  TreePine,
  CheckCircle2,
  Info
} from 'lucide-react';
import { PlanningMode, SupportedLanguage, RoofExclusion, PlacedPanel } from './types';

export default function App() {
  // Mode & Global Navigation
  const [mode, setMode] = useState<PlanningMode>('roof');
  const [language, setLanguage] = useState<SupportedLanguage>('en');
  const [showAdvisor, setShowAdvisor] = useState(false);
  const [advisorQuery, setAdvisorQuery] = useState('');
  const [advisorChat, setAdvisorChat] = useState<Array<{ role: 'user' | 'assistant'; text: string }>>([
    {
      role: 'assistant',
      text: 'Namaste! I am your HeatHack Solar Advisor. Ask me why a system size was recommended, what empirical evidence backs the cooling estimates, or which fields need a physical site survey.'
    }
  ]);

  // --- MY ROOF STATE ---
  const [roofAreaSqm, setRoofAreaSqm] = useState(88.5);
  const [setbackMarginM, setSetbackMarginM] = useState(0.5);
  const [panelWattage, setPanelWattage] = useState(500);
  const [monthlyConsumptionKwh, setMonthlyConsumptionKwh] = useState(260);
  const [retailTariff, setRetailTariff] = useState(7.5);
  const [exportTariff, setExportTariff] = useState(2.5);
  const [monthlyYieldAssumption, setMonthlyYieldAssumption] = useState(120); // 100-140
  const [azimuthAngle, setAzimuthAngle] = useState(0); // 0 = South

  // Obstructions
  const [exclusions, setExclusions] = useState<RoofExclusion[]>([
    { id: 'ex-1', type: 'water_tank', label: 'Overhead Water Tank Cluster', area_sqm: 4.8, confirmed: true },
    { id: 'ex-2', type: 'stairwell', label: 'Mumty / Stairwell Tower', area_sqm: 9.5, confirmed: true },
    { id: 'ex-3', type: 'ac_compressor', label: 'Split AC Outdoor Unit', area_sqm: 1.2, confirmed: false }
  ]);

  // Placed Panels
  const [panelCount, setPanelCount] = useState(6); // 6 x 500W = 3.0 kW
  const [selectedPanelId, setSelectedPanelId] = useState<number | null>(null);

  // Derived Roof Geometry
  const confirmedExclusionArea = exclusions
    .filter(e => e.confirmed)
    .reduce((sum, e) => sum + e.area_sqm, 0);
  const setbackDeduction = Math.round(Math.sqrt(roofAreaSqm) * 4 * setbackMarginM * 0.4);
  const usableRoofArea = Math.max(10, Math.round(roofAreaSqm - confirmedExclusionArea - setbackDeduction));

  // Solar Metrics
  const installedKw = Number(((panelCount * panelWattage) / 1000).toFixed(2));
  const panelFootprintSqm = Number((panelCount * 2.1).toFixed(1)); // ~2.1 m² per 500W panel
  const installationAreaSqm = Number((panelCount * 2.8).toFixed(1)); // Including spacing & access
  const monthlyGenKwh = Math.round(installedKw * monthlyYieldAssumption);
  const annualGenKwh = monthlyGenKwh * 12;

  // PM Surya Ghar Subsidy: ₹30,000 * min(kW, 2) + ₹18,000 * min(max(kW - 2, 0), 1)
  const subsidyInr = Math.min(
    78000,
    30000 * Math.min(installedKw, 2) + 18000 * Math.min(Math.max(installedKw - 2, 0), 1)
  );
  const grossCostInr = Math.round(installedKw * 60000);
  const netCostInr = Math.max(0, grossCostInr - subsidyInr);

  // Financials
  const selfConsumedKwh = Math.min(monthlyConsumptionKwh, monthlyGenKwh);
  const exportedKwh = Math.max(0, monthlyGenKwh - monthlyConsumptionKwh);
  const annualSavingsInr = Math.round(
    12 * (selfConsumedKwh * retailTariff + exportedKwh * exportTariff) - grossCostInr * 0.01
  );
  const simplePaybackYears = annualSavingsInr > 0 ? Number((netCostInr / annualSavingsInr).toFixed(1)) : 99;

  // --- MY NEIGHBOURHOOD STATE ---
  const [heatWeight, setHeatWeight] = useState(0.35);
  const [vegWeight, setVegWeight] = useState(0.20);
  const [roofMatWeight, setRoofMatWeight] = useState(0.25);
  const [socioWeight, setSocioWeight] = useState(0.20);
  const [scenarioCoverage, setScenarioCoverage] = useState(70); // % roofs treated
  const [treePlantingCount, setTreePlantingCount] = useState(150);

  // Clusters Data
  const clusters = [
    {
      id: 'cluster-1',
      name: 'North Informal Settlement (Cluster A)',
      lst_c: 47.2,
      ndvi: 0.06,
      roof_type: 'Corrugated Tin Sheets',
      households: 120,
      survey_completed: false,
      survey_note: 'Survey required (tenancy & structural stability)',
      intervention: 'High-SRI Cool-Roof Paint',
      unit_cost: 5000,
      evidence: 'Reference scenario: ~1°C lower daytime indoor temperature (MHT Ahmedabad 2020 study)'
    },
    {
      id: 'cluster-2',
      name: 'Industrial Colony Worker Quarters',
      lst_c: 45.8,
      ndvi: 0.08,
      roof_type: 'Asbestos Cement Sheets',
      households: 85,
      survey_completed: true,
      survey_note: 'Verified low-income tenement block',
      intervention: 'Reflective Coating + Ventilation Audit',
      unit_cost: 5800,
      evidence: 'Reference scenario: ~1°C to 1.5°C peak indoor mitigation upon surface treatment'
    },
    {
      id: 'cluster-3',
      name: 'Central Old Bazaar Mixed-Use Block',
      lst_c: 43.1,
      ndvi: 0.12,
      roof_type: 'Dense Flat Concrete (RCC)',
      households: 210,
      survey_completed: true,
      survey_note: 'Commercial ground floor, residential upper floors',
      intervention: 'Solar PV Canopy + Tree Shading',
      unit_cost: 7200,
      evidence: 'Dual benefit: Rooftop solar shading reduces ceiling heat gain by 0.5°C-1.0°C'
    }
  ];

  // Bill OCR Upload Simulator
  const handleSimulateBillUpload = () => {
    setMonthlyConsumptionKwh(285);
    setRetailTariff(7.65);
    alert('Gemini Bill OCR: Extracted 285 kWh/month average from UGVCL electricity bill!');
  };

  // Chat Advisor Handler
  const handleSendMessage = () => {
    if (!advisorQuery.trim()) return;
    const userMsg = advisorQuery;
    setAdvisorChat(prev => [...prev, { role: 'user', text: userMsg }]);
    setAdvisorQuery('');

    setTimeout(() => {
      let reply = '';
      if (userMsg.toLowerCase().includes('why') || userMsg.toLowerCase().includes('recommend')) {
        reply = `The ${installedKw} kW system is recommended because it covers ${(monthlyGenKwh / monthlyConsumptionKwh * 100).toFixed(0)}% of your monthly power demand (${monthlyConsumptionKwh} kWh) while claiming ₹${subsidyInr.toLocaleString('en-IN')} in central PM Surya Ghar subsidy. Moving higher yields diminished returns due to the ₹78,000 subsidy cap.`;
      } else if (userMsg.toLowerCase().includes('evidence') || userMsg.toLowerCase().includes('cooling')) {
        reply = 'Cooling estimates are strictly derived from peer-reviewed empirical studies: Vellingiri et al. (2020) with Mahila Housing Trust observed an average 1°C lower indoor daytime temperature in coated tin-roof homes in Ahmedabad. Satellite surface temperatures are NOT indoor temperatures.';
      } else {
        reply = language === 'hi' 
          ? `आपकी ${installedKw} kW सौर प्रणाली अनुमानित ₹${annualSavingsInr.toLocaleString('en-IN')} वार्षिक बचत उत्पन्न करेगी। ध्यान दें कि वास्तविक स्थापना से पूर्व स्ट्रक्चरल सर्वे आवश्यक है।`
          : `Your ${installedKw} kW conceptual system delivers an estimated annual net savings of ₹${annualSavingsInr.toLocaleString('en-IN')} with an expected payback of ${simplePaybackYears} years. Note that on-site structural checks are mandatory before contracting.`;
      }
      setAdvisorChat(prev => [...prev, { role: 'assistant', text: reply }]);
    }, 600);
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col">
      {/* Top Navigation Bar */}
      <header className="border-b border-slate-800 bg-slate-900/80 backdrop-blur sticky top-0 z-40 px-4 py-3 flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-amber-500 to-solar-blue flex items-center justify-center shadow-lg shadow-amber-500/20">
            <Sun className="w-6 h-6 text-slate-950 font-bold" />
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <h1 className="font-bold text-lg tracking-tight text-white">HeatHack Solar</h1>
              <span className="text-xs bg-amber-500/10 text-amber-400 border border-amber-500/30 px-2 py-0.5 rounded-full font-mono">
                AI & Earth Observation
              </span>
            </div>
            <p className="text-xs text-slate-400">
              Plan solar on your roof. Prioritise cooling in your neighbourhood.
            </p>
          </div>
        </div>

        {/* Mode Selector Switch */}
        <div className="flex items-center bg-slate-800 p-1 rounded-xl border border-slate-700">
          <button
            onClick={() => setMode('roof')}
            className={`flex items-center space-x-2 px-4 py-1.5 rounded-lg text-sm font-medium transition ${
              mode === 'roof'
                ? 'bg-solar-blue text-white shadow-md'
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            <Sun className="w-4 h-4" />
            <span>My Roof</span>
          </button>
          <button
            onClick={() => setMode('neighbourhood')}
            className={`flex items-center space-x-2 px-4 py-1.5 rounded-lg text-sm font-medium transition ${
              mode === 'neighbourhood'
                ? 'bg-amber-600 text-white shadow-md'
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            <Thermometer className="w-4 h-4" />
            <span>My Neighbourhood</span>
          </button>
        </div>

        {/* Action Controls */}
        <div className="flex items-center space-x-3">
          {/* Language Selector */}
          <select
            value={language}
            onChange={(e) => setLanguage(e.target.value as SupportedLanguage)}
            className="bg-slate-800 border border-slate-700 text-xs rounded-lg px-2.5 py-1.5 text-slate-300 focus:outline-none focus:ring-1 focus:ring-amber-500"
          >
            <option value="en">English</option>
            <option value="hi">हिंदी (Hindi)</option>
            <option value="bn">বাংলা (Bengali)</option>
          </select>

          {/* AI Advisor Button */}
          <button
            onClick={() => setShowAdvisor(!showAdvisor)}
            className={`flex items-center space-x-1.5 px-3 py-1.5 rounded-lg text-xs font-medium border transition ${
              showAdvisor
                ? 'bg-amber-500 text-black border-amber-400 shadow-lg shadow-amber-500/20'
                : 'bg-slate-800 hover:bg-slate-750 text-slate-300 border-slate-700'
            }`}
          >
            <MessageSquare className="w-3.5 h-3.5" />
            <span>AI Advisor</span>
          </button>
        </div>
      </header>

      {/* Main Content Viewport */}
      <main className="flex-1 flex overflow-hidden">
        {/* ======================================================== */}
        {/* MODE 1: MY ROOF VIEW                                    */}
        {/* ======================================================== */}
        {mode === 'roof' && (
          <div className="flex-1 flex flex-col lg:flex-row h-full overflow-y-auto lg:overflow-hidden">
            {/* Left Spatial Viewport & Canvas */}
            <div className="flex-1 bg-slate-900/60 p-4 flex flex-col border-r border-slate-800 relative">
              {/* Top Map Context Info */}
              <div className="flex items-center justify-between mb-3 text-xs text-slate-400">
                <div className="flex items-center space-x-2">
                  <MapPin className="w-4 h-4 text-amber-400" />
                  <span className="font-medium text-slate-200">Shanti Nagar, Ward 12, Ahmedabad (23.0315° N, 72.5813° E)</span>
                  <span className="bg-slate-800 px-2 py-0.5 rounded text-slate-400 border border-slate-700">Sentinel-2 & High-Res Ortho</span>
                </div>
                <div className="text-amber-400/90 font-mono text-[11px] bg-amber-950/40 border border-amber-800/40 px-2 py-0.5 rounded">
                  Concept layout — installer verification required
                </div>
              </div>

              {/* Simulated Interactive Satellite Roof Viewport */}
              <div className="flex-1 bg-slate-950 rounded-2xl border border-slate-800 relative overflow-hidden flex flex-col items-center justify-center p-6 shadow-inner">
                {/* Background Satellite Grid Texture */}
                <div className="absolute inset-0 opacity-25 bg-[radial-gradient(#38bdf8_1px,transparent_1px)] [background-size:16px_16px]"></div>

                {/* Roof Canvas Wrapper */}
                <div className="relative w-[480px] h-[340px] bg-slate-800/90 rounded-xl border-2 border-slate-600 shadow-2xl overflow-hidden flex items-center justify-center">
                  {/* Setback dashed border */}
                  <div className="absolute inset-3 border-2 border-dashed border-amber-500/60 rounded-lg pointer-events-none z-10">
                    <span className="absolute top-1 left-2 text-[10px] text-amber-400 bg-slate-900/80 px-1 rounded">
                      Setback ({setbackMarginM}m)
                    </span>
                  </div>

                  {/* Confirmed Obstructions (Red Shaded) */}
                  {exclusions.filter(e => e.confirmed).map((ex, idx) => (
                    <div
                      key={ex.id}
                      className="absolute bg-red-600/60 border border-red-500 rounded p-1 text-[10px] text-white flex flex-col items-center justify-center z-10 shadow-lg backdrop-blur-sm"
                      style={{
                        top: idx === 0 ? '16px' : '65%',
                        right: idx === 0 ? '20px' : '25%',
                        width: idx === 0 ? '80px' : '100px',
                        height: idx === 0 ? '60px' : '70px',
                      }}
                    >
                      <span className="font-semibold">{ex.type === 'water_tank' ? '💧 Water Tank' : '🚪 Mumty'}</span>
                      <span className="text-[9px] text-red-200">{ex.area_sqm} m²</span>
                    </div>
                  ))}

                  {/* Virtual Solar Panels Grid (Blue Rectangles) */}
                  <div
                    className="grid grid-cols-3 gap-2.5 z-20 transition-transform duration-300"
                    style={{ transform: `rotate(${azimuthAngle}deg)` }}
                  >
                    {Array.from({ length: panelCount }).map((_, idx) => (
                      <div
                        key={idx}
                        onClick={() => setSelectedPanelId(idx + 1)}
                        className={`w-24 h-14 rounded border cursor-pointer flex flex-col items-center justify-center transition shadow-md ${
                          selectedPanelId === idx + 1
                            ? 'bg-cyan-500 border-white text-slate-950 scale-105 shadow-cyan-500/50'
                            : 'bg-solar-blue/80 hover:bg-solar-blue border-blue-400/60 text-white'
                        }`}
                      >
                        <span className="text-[10px] font-mono font-bold tracking-wider">PV #{idx + 1}</span>
                        <span className="text-[8px] opacity-80">{panelWattage}W Monocrystal</span>
                      </div>
                    ))}
                  </div>

                  {/* Remaining Space Label */}
                  <div className="absolute bottom-2 right-2 text-[10px] text-slate-400 bg-slate-900/80 px-2 py-0.5 rounded border border-slate-700">
                    Uncovered Usable: {(usableRoofArea - panelFootprintSqm).toFixed(1)} m²
                  </div>
                </div>

                {/* Legend bar */}
                <div className="mt-4 flex flex-wrap items-center justify-center gap-4 text-xs text-slate-300 bg-slate-900/90 border border-slate-800 px-4 py-2 rounded-xl">
                  <div className="flex items-center space-x-1.5">
                    <span className="w-3.5 h-3.5 rounded bg-solar-blue border border-blue-400 inline-block"></span>
                    <span>Proposed Panels ({panelCount})</span>
                  </div>
                  <div className="flex items-center space-x-1.5">
                    <span className="w-3.5 h-3.5 rounded bg-red-600/60 border border-red-500 inline-block"></span>
                    <span>Exclusions ({confirmedExclusionArea} m²)</span>
                  </div>
                  <div className="flex items-center space-x-1.5">
                    <span className="w-3.5 h-3.5 border-2 border-dashed border-amber-500 inline-block"></span>
                    <span>Setbacks ({setbackMarginM}m)</span>
                  </div>
                  <div className="flex items-center space-x-1.5">
                    <span className="w-3.5 h-3.5 rounded bg-slate-800 border border-slate-600 inline-block"></span>
                    <span>Remaining Roof</span>
                  </div>
                </div>

                {/* Spatial Controls */}
                <div className="mt-3 flex items-center space-x-3 text-xs">
                  <div className="flex items-center space-x-1 bg-slate-800 border border-slate-700 px-2 py-1 rounded-lg">
                    <RotateCw className="w-3.5 h-3.5 text-slate-400" />
                    <span>Azimuth:</span>
                    <input
                      type="range"
                      min="-45"
                      max="45"
                      value={azimuthAngle}
                      onChange={(e) => setAzimuthAngle(Number(e.target.value))}
                      className="w-20 accent-amber-500 cursor-pointer"
                    />
                    <span className="font-mono">{azimuthAngle}°</span>
                  </div>

                  <div className="flex items-center space-x-1 bg-slate-800 border border-slate-700 px-2 py-1 rounded-lg">
                    <span>Panels:</span>
                    <button
                      onClick={() => setPanelCount(Math.max(1, panelCount - 1))}
                      className="px-1.5 py-0.5 bg-slate-700 rounded hover:bg-slate-600"
                    >
                      -
                    </button>
                    <span className="font-mono px-1 font-bold text-amber-400">{panelCount}</span>
                    <button
                      onClick={() => setPanelCount(Math.min(18, panelCount + 1))}
                      className="px-1.5 py-0.5 bg-slate-700 rounded hover:bg-slate-600"
                    >
                      +
                    </button>
                  </div>
                </div>
              </div>

              {/* Area Breakdown Banner */}
              <div className="mt-3 grid grid-cols-4 gap-2 text-center text-xs">
                <div className="bg-slate-800/60 border border-slate-700/60 p-2 rounded-xl">
                  <div className="text-slate-400">Total Roof</div>
                  <div className="text-sm font-bold text-white mt-0.5">{roofAreaSqm} m²</div>
                </div>
                <div className="bg-slate-800/60 border border-slate-700/60 p-2 rounded-xl">
                  <div className="text-slate-400">Usable Area</div>
                  <div className="text-sm font-bold text-emerald-400 mt-0.5">{usableRoofArea} m²</div>
                </div>
                <div className="bg-slate-800/60 border border-slate-700/60 p-2 rounded-xl">
                  <div className="text-slate-400">Panel Footprint</div>
                  <div className="text-sm font-bold text-solar-cyan mt-0.5">{panelFootprintSqm} m²</div>
                </div>
                <div className="bg-slate-800/60 border border-slate-700/60 p-2 rounded-xl">
                  <div className="text-slate-400">Installation Space</div>
                  <div className="text-sm font-bold text-amber-400 mt-0.5">{installationAreaSqm} m²</div>
                </div>
              </div>
            </div>

            {/* Right Solar Planning & Financial Sidebar */}
            <div className="w-full lg:w-[420px] bg-slate-900 p-5 overflow-y-auto flex flex-col space-y-5">
              {/* Electricity & Bill Intake Card */}
              <div className="bg-slate-800/60 border border-slate-700 rounded-2xl p-4">
                <div className="flex items-center justify-between mb-3">
                  <div className="flex items-center space-x-2">
                    <Zap className="w-4 h-4 text-amber-400" />
                    <h3 className="font-semibold text-sm text-white">Electricity Profile</h3>
                  </div>
                  <button
                    onClick={handleSimulateBillUpload}
                    className="flex items-center space-x-1 text-xs text-amber-400 hover:text-amber-300 bg-amber-500/10 border border-amber-500/20 px-2 py-1 rounded-lg transition"
                  >
                    <FileText className="w-3 h-3" />
                    <span>Upload Bill (Gemini OCR)</span>
                  </button>
                </div>

                <div className="space-y-3 text-xs">
                  <div className="flex items-center justify-between">
                    <span className="text-slate-400">Monthly Consumption:</span>
                    <div className="flex items-center space-x-1">
                      <input
                        type="number"
                        value={monthlyConsumptionKwh}
                        onChange={(e) => setMonthlyConsumptionKwh(Number(e.target.value))}
                        className="w-16 bg-slate-900 border border-slate-700 rounded px-2 py-1 text-right text-white font-mono"
                      />
                      <span className="text-slate-400">kWh</span>
                    </div>
                  </div>

                  <div className="flex items-center justify-between">
                    <span className="text-slate-400">Retail Tariff:</span>
                    <div className="flex items-center space-x-1">
                      <input
                        type="number"
                        step="0.1"
                        value={retailTariff}
                        onChange={(e) => setRetailTariff(Number(e.target.value))}
                        className="w-16 bg-slate-900 border border-slate-700 rounded px-2 py-1 text-right text-white font-mono"
                      />
                      <span className="text-slate-400">₹/unit</span>
                    </div>
                  </div>

                  <div className="flex items-center justify-between">
                    <span className="text-slate-400">Assumed Monthly Yield:</span>
                    <div className="flex items-center space-x-1">
                      <span className="text-amber-400 font-mono font-bold">{monthlyYieldAssumption}</span>
                      <span className="text-slate-400">kWh/kW/mo</span>
                    </div>
                  </div>
                </div>
              </div>

              {/* System Sizing & PM Surya Ghar Subsidy Summary */}
              <div className="bg-gradient-to-br from-slate-800 to-slate-850 border border-slate-700 rounded-2xl p-4 shadow-lg">
                <div className="flex items-center justify-between mb-3">
                  <h3 className="font-semibold text-sm text-white flex items-center space-x-2">
                    <TrendingUp className="w-4 h-4 text-emerald-400" />
                    <span>Selected System Capacity</span>
                  </h3>
                  <span className="text-xs font-mono font-bold px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-400 border border-emerald-500/30">
                    {installedKw} kW DC
                  </span>
                </div>

                <div className="grid grid-cols-2 gap-3 text-xs mb-4">
                  <div className="bg-slate-900/80 p-2.5 rounded-xl border border-slate-700/50">
                    <div className="text-slate-400">Est. Generation</div>
                    <div className="text-base font-bold text-white mt-0.5 font-mono">
                      {monthlyGenKwh} <span className="text-xs font-normal text-slate-400">kWh/mo</span>
                    </div>
                    <div className="text-[10px] text-slate-400 mt-1">({annualGenKwh} kWh/yr)</div>
                  </div>

                  <div className="bg-slate-900/80 p-2.5 rounded-xl border border-slate-700/50">
                    <div className="text-slate-400">Central Subsidy (CFA)</div>
                    <div className="text-base font-bold text-emerald-400 mt-0.5 font-mono">
                      ₹{subsidyInr.toLocaleString('en-IN')}
                    </div>
                    <div className="text-[10px] text-emerald-500/80 mt-1">PM Surya Ghar Yojana</div>
                  </div>
                </div>

                {/* Financial Arithmetic Breakdown */}
                <div className="border-t border-slate-700/80 pt-3 space-y-2 text-xs">
                  <div className="flex justify-between">
                    <span className="text-slate-400">Estimated Gross Cost:</span>
                    <span className="font-mono text-slate-300">₹{grossCostInr.toLocaleString('en-IN')}</span>
                  </div>
                  <div className="flex justify-between text-emerald-400">
                    <span>Eligible Central Subsidy:</span>
                    <span className="font-mono font-semibold">- ₹{subsidyInr.toLocaleString('en-IN')}</span>
                  </div>
                  <div className="flex justify-between font-bold text-white border-t border-slate-700/50 pt-1.5">
                    <span>Net Installation Investment:</span>
                    <span className="font-mono text-amber-400 text-sm">₹{netCostInr.toLocaleString('en-IN')}</span>
                  </div>
                  <div className="flex justify-between text-slate-300 pt-1">
                    <span className="text-slate-400">Annual Net Savings:</span>
                    <span className="font-mono font-semibold text-emerald-400">₹{annualSavingsInr.toLocaleString('en-IN')}/yr</span>
                  </div>
                  <div className="flex justify-between items-center bg-slate-900/90 p-2 rounded-lg border border-slate-700 mt-2">
                    <span className="text-slate-300 font-medium">Simple Payback Period:</span>
                    <span className="text-sm font-bold font-mono text-amber-400">{simplePaybackYears} Years</span>
                  </div>
                </div>
              </div>

              {/* Feasible Size Comparison & Recommendation Explanation */}
              <div className="bg-slate-800/60 border border-slate-700 rounded-2xl p-4">
                <h4 className="text-xs font-semibold text-slate-300 mb-2">System Size Comparison</h4>
                <div className="space-y-2 text-xs">
                  {[
                    { kw: 1.0, cost: 60000, sub: 30000, net: 30000, payback: 4.8, best: false },
                    { kw: 2.0, cost: 120000, sub: 60000, net: 60000, payback: 4.2, best: installedKw === 2.0 },
                    { kw: 3.0, cost: 180000, sub: 78000, net: 102000, payback: 4.9, best: installedKw === 3.0 }
                  ].map((opt) => (
                    <div
                      key={opt.kw}
                      className={`p-2.5 rounded-xl border flex items-center justify-between ${
                        opt.best
                          ? 'bg-solar-blue/20 border-solar-blue text-white'
                          : 'bg-slate-900/40 border-slate-800 text-slate-300'
                      }`}
                    >
                      <div>
                        <div className="font-bold flex items-center space-x-1.5">
                          <span>{opt.kw} kW System</span>
                          {opt.best && (
                            <span className="text-[10px] bg-solar-blue px-1.5 py-0.2 rounded text-white font-normal">
                              Recommended
                            </span>
                          )}
                        </div>
                        <div className="text-[10px] text-slate-400 mt-0.5">
                          Subsidy: ₹{opt.sub.toLocaleString('en-IN')} | Net: ₹{opt.net.toLocaleString('en-IN')}
                        </div>
                      </div>
                      <div className="text-right">
                        <div className="text-xs font-mono font-bold text-amber-400">{opt.payback} yrs</div>
                        <div className="text-[9px] text-slate-400">Payback</div>
                      </div>
                    </div>
                  ))}
                </div>

                <p className="mt-3 text-[11px] text-slate-400 leading-relaxed bg-slate-900/50 p-2 rounded-lg border border-slate-800">
                  <strong className="text-slate-300">Recommendation Rationale:</strong> The subsidy tier covers ₹30,000/kW up to 2 kW, then ₹18,000 for the 3rd kW, capping at ₹78,000. Beyond 3 kW, net metering feed-in rates determine viability.
                </p>
              </div>

              {/* Obstructions Management */}
              <div className="bg-slate-800/60 border border-slate-700 rounded-2xl p-4">
                <div className="flex items-center justify-between mb-2">
                  <h4 className="text-xs font-semibold text-slate-300">Detected Obstacles & Exclusions</h4>
                  <span className="text-[10px] text-slate-400">Gemini Vision Review</span>
                </div>
                <div className="space-y-2 text-xs">
                  {exclusions.map((ex) => (
                    <div
                      key={ex.id}
                      className="flex items-center justify-between p-2 rounded-lg bg-slate-900/60 border border-slate-800"
                    >
                      <div className="flex items-center space-x-2">
                        <input
                          type="checkbox"
                          checked={ex.confirmed}
                          onChange={(e) => {
                            const updated = exclusions.map(item =>
                              item.id === ex.id ? { ...item, confirmed: e.target.checked } : item
                            );
                            setExclusions(updated);
                          }}
                          className="rounded border-slate-700 accent-amber-500"
                        />
                        <span className="text-slate-300">{ex.label}</span>
                      </div>
                      <span className="font-mono text-red-400 text-[11px]">{ex.area_sqm} m²</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        )}

        {/* ======================================================== */}
        {/* MODE 2: MY NEIGHBOURHOOD VIEW                           */}
        {/* ======================================================== */}
        {mode === 'neighbourhood' && (
          <div className="flex-1 flex flex-col lg:flex-row h-full overflow-y-auto lg:overflow-hidden">
            {/* Left Urban Heat Island Matrix & Scenarios */}
            <div className="flex-1 bg-slate-900/60 p-5 flex flex-col border-r border-slate-800 overflow-y-auto">
              {/* Thermal Distinction Alert Box */}
              <div className="bg-amber-950/40 border border-amber-700/50 rounded-2xl p-4 mb-4 text-xs">
                <div className="flex items-start space-x-3">
                  <AlertTriangle className="w-5 h-5 text-amber-400 shrink-0 mt-0.5" />
                  <div>
                    <h4 className="font-bold text-amber-300 text-sm">Critical Thermal Data Distinction</h4>
                    <p className="text-slate-300 mt-1 leading-relaxed">
                      Satellite surface temperature (LST) measures radiometric ground/roof emission and is <strong>coarser than individual roof outlines</strong>.
                      It is <strong>not indoor air temperature</strong> or ambient outdoor air temperature. Indoor cooling estimates must not be subtracted directly from satellite heat maps.
                    </p>
                  </div>
                </div>
              </div>

              {/* Multi-Criteria Weight Sliders */}
              <div className="bg-slate-800/60 border border-slate-700 rounded-2xl p-4 mb-4">
                <div className="flex items-center justify-between mb-3">
                  <h3 className="font-semibold text-sm text-white flex items-center space-x-2">
                    <Sliders className="w-4 h-4 text-amber-400" />
                    <span>Prioritization Ranking Weights</span>
                  </h3>
                  <span className="text-xs text-slate-400">Multi-Criteria Decision Analysis</span>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-4 gap-3 text-xs">
                  <div>
                    <div className="flex justify-between text-slate-400 mb-1">
                      <span>Heat Exposure (LST):</span>
                      <span className="font-mono font-bold text-white">{Math.round(heatWeight * 100)}%</span>
                    </div>
                    <input
                      type="range"
                      min="0"
                      max="1"
                      step="0.05"
                      value={heatWeight}
                      onChange={(e) => setHeatWeight(Number(e.target.value))}
                      className="w-full accent-amber-500"
                    />
                  </div>

                  <div>
                    <div className="flex justify-between text-slate-400 mb-1">
                      <span>Vegetation Deficit:</span>
                      <span className="font-mono font-bold text-white">{Math.round(vegWeight * 100)}%</span>
                    </div>
                    <input
                      type="range"
                      min="0"
                      max="1"
                      step="0.05"
                      value={vegWeight}
                      onChange={(e) => setVegWeight(Number(e.target.value))}
                      className="w-full accent-emerald-500"
                    />
                  </div>

                  <div>
                    <div className="flex justify-between text-slate-400 mb-1">
                      <span>Roof Material Risk:</span>
                      <span className="font-mono font-bold text-white">{Math.round(roofMatWeight * 100)}%</span>
                    </div>
                    <input
                      type="range"
                      min="0"
                      max="1"
                      step="0.05"
                      value={roofMatWeight}
                      onChange={(e) => setRoofMatWeight(Number(e.target.value))}
                      className="w-full accent-red-500"
                    />
                  </div>

                  <div>
                    <div className="flex justify-between text-slate-400 mb-1">
                      <span>Vulnerability Index:</span>
                      <span className="font-mono font-bold text-white">{Math.round(socioWeight * 100)}%</span>
                    </div>
                    <input
                      type="range"
                      min="0"
                      max="1"
                      step="0.05"
                      value={socioWeight}
                      onChange={(e) => setSocioWeight(Number(e.target.value))}
                      className="w-full accent-solar-blue"
                    />
                  </div>
                </div>
              </div>

              {/* Ranked Clusters Table */}
              <div className="bg-slate-800/60 border border-slate-700 rounded-2xl p-4 mb-4">
                <h3 className="font-semibold text-sm text-white mb-3">Priority Ranking & Evidence-Based Interventions</h3>
                <div className="space-y-3">
                  {clusters.map((c, idx) => (
                    <div
                      key={c.id}
                      className="bg-slate-900/80 border border-slate-700/80 rounded-xl p-3.5 text-xs hover:border-amber-500/50 transition"
                    >
                      <div className="flex items-center justify-between mb-2">
                        <div className="flex items-center space-x-2">
                          <span className="w-5 h-5 rounded-full bg-amber-500/20 text-amber-400 border border-amber-500/40 flex items-center justify-center font-bold font-mono">
                            {idx + 1}
                          </span>
                          <h4 className="font-bold text-white text-sm">{c.name}</h4>
                        </div>
                        <div className="flex items-center space-x-2">
                          <span className="bg-red-500/20 text-red-400 border border-red-500/30 px-2 py-0.5 rounded font-mono">
                            LST {c.lst_c}°C
                          </span>
                          {!c.survey_completed ? (
                            <span className="bg-amber-500/20 text-amber-400 border border-amber-500/30 px-2 py-0.5 rounded font-medium flex items-center space-x-1">
                              <AlertTriangle className="w-3 h-3" />
                              <span>Survey required</span>
                            </span>
                          ) : (
                            <span className="bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 px-2 py-0.5 rounded font-medium">
                              Survey Verified
                            </span>
                          )}
                        </div>
                      </div>

                      <div className="grid grid-cols-2 md:grid-cols-4 gap-2 text-slate-300 mb-2">
                        <div>
                          <span className="text-slate-400">Roofing:</span> {c.roof_type}
                        </div>
                        <div>
                          <span className="text-slate-400">Target Households:</span> {c.households}
                        </div>
                        <div>
                          <span className="text-slate-400">Cost / Household:</span> ₹{c.unit_cost.toLocaleString('en-IN')}
                        </div>
                        <div>
                          <span className="text-slate-400">Cluster Budget:</span> ₹{(c.unit_cost * c.households).toLocaleString('en-IN')}
                        </div>
                      </div>

                      <div className="bg-slate-950/70 border border-slate-800 p-2.5 rounded-lg flex items-start space-x-2 text-[11px] text-slate-300">
                        <Info className="w-4 h-4 text-solar-cyan shrink-0 mt-0.5" />
                        <div>
                          <strong className="text-white">Evidence Citation:</strong> {c.evidence}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Before-and-After Scenario Modeler */}
              <div className="bg-slate-800/60 border border-slate-700 rounded-2xl p-4">
                <h3 className="font-semibold text-sm text-white mb-2">Neighbourhood Cooling Scenario Modeler</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs mt-3">
                  <div className="space-y-3">
                    <div>
                      <div className="flex justify-between text-slate-300 mb-1">
                        <span>Roof Coating Coverage:</span>
                        <span className="font-mono text-amber-400">{scenarioCoverage}% of eligible roofs</span>
                      </div>
                      <input
                        type="range"
                        min="20"
                        max="100"
                        value={scenarioCoverage}
                        onChange={(e) => setScenarioCoverage(Number(e.target.value))}
                        className="w-full accent-amber-500"
                      />
                    </div>

                    <div>
                      <div className="flex justify-between text-slate-300 mb-1">
                        <span>Proposed Shade Trees:</span>
                        <span className="font-mono text-emerald-400">{treePlantingCount} saplings</span>
                      </div>
                      <input
                        type="range"
                        min="0"
                        max="500"
                        value={treePlantingCount}
                        onChange={(e) => setTreePlantingCount(Number(e.target.value))}
                        className="w-full accent-emerald-500"
                      />
                    </div>
                  </div>

                  <div className="bg-slate-900/90 border border-slate-700 p-3 rounded-xl flex flex-col justify-between">
                    <div>
                      <div className="text-slate-400">Aggregated Programme Budget (Pilot)</div>
                      <div className="text-xl font-bold font-mono text-amber-400 mt-1">
                        ₹{Math.round((scenarioCoverage * 120 * 50) + (treePlantingCount * 1200)).toLocaleString('en-IN')}
                      </div>
                    </div>
                    <div className="text-[11px] text-slate-400 mt-2">
                      Covers cool-roof surface treatment, labour, primer, and tree planting with 1-year maintenance buffer.
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* Right Neighbourhood Budgeting & Guideline Sidebar */}
            <div className="w-full lg:w-[400px] bg-slate-900 p-5 overflow-y-auto space-y-4">
              <div className="bg-slate-800/60 border border-slate-700 rounded-2xl p-4">
                <h3 className="font-semibold text-sm text-white mb-3">Municipal Programme Budgeting</h3>
                
                <div className="space-y-3 text-xs">
                  <div className="p-2.5 rounded-lg bg-slate-900/80 border border-slate-800">
                    <div className="text-slate-400">Illustrative Tin Roof Unit Arithmetic:</div>
                    <ul className="list-disc pl-4 mt-1 text-slate-300 space-y-0.5 font-mono text-[11px]">
                      <li>Roof Area: 40 m²</li>
                      <li>Installed Rate: ₹100/m²</li>
                      <li>Surface Preparation: ₹1,000</li>
                      <li>Cost per household: ₹5,000</li>
                      <li>Cost for 100 identical homes: ₹5.0 Lakh</li>
                    </ul>
                  </div>

                  <div className="p-2.5 rounded-lg bg-red-950/20 border border-red-800/40 text-red-300 text-[11px]">
                    <strong>Subsidy Boundary:</strong> PM Surya Ghar solar subsidy must <em>NOT</em> be applied to cool-roof paint, ventilation hardware, or general repair work.
                  </div>
                </div>
              </div>

              {/* Scientific Evidence Repository Summary */}
              <div className="bg-slate-800/60 border border-slate-700 rounded-2xl p-4 text-xs">
                <h4 className="font-semibold text-slate-200 mb-2">Cooling Evidence Database</h4>
                <div className="space-y-2 text-slate-300 text-[11px]">
                  <div className="p-2 bg-slate-900/50 rounded border border-slate-800">
                    <div className="font-bold text-amber-400">Ahmedabad MHT 2020 Study (16 homes)</div>
                    <p className="mt-0.5 text-slate-400">
                      ~1°C lower daytime mean indoor air temperature on coated tin roofs. Unverified Airlite ventilation paradoxically drew higher heat indoors.
                    </p>
                  </div>
                  <div className="p-2 bg-slate-900/50 rounded border border-slate-800">
                    <div className="font-bold text-emerald-400">US EPA Heat Island Guidelines</div>
                    <p className="mt-0.5 text-slate-400">
                      Trees provide shade & evapotranspiration. Proposed plantings must be checked against rooftop solar lines to avoid shade reduction.
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}
      </main>

      {/* Multilingual AI Advisor Drawer */}
      {showAdvisor && (
        <div className="fixed bottom-4 right-4 w-96 h-[480px] bg-slate-900 border border-slate-700 rounded-2xl shadow-2xl flex flex-col z-50 overflow-hidden backdrop-blur">
          <div className="p-3 bg-slate-800 border-b border-slate-700 flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <MessageSquare className="w-4 h-4 text-amber-400" />
              <span className="font-bold text-sm text-white">HeatHack AI Advisor</span>
            </div>
            <button
              onClick={() => setShowAdvisor(false)}
              className="text-slate-400 hover:text-white text-xs px-2 py-0.5 rounded"
            >
              ✕
            </button>
          </div>

          <div className="flex-1 p-3 overflow-y-auto space-y-3 text-xs">
            {advisorChat.map((msg, i) => (
              <div
                key={i}
                className={`p-2.5 rounded-xl ${
                  msg.role === 'assistant'
                    ? 'bg-slate-800 text-slate-200 border border-slate-700'
                    : 'bg-solar-blue text-white ml-6'
                }`}
              >
                {msg.text}
              </div>
            ))}
          </div>

          <div className="p-2.5 bg-slate-800 border-t border-slate-700 flex items-center space-x-2">
            <input
              type="text"
              placeholder="Ask in English, Hindi, or Bengali..."
              value={advisorQuery}
              onChange={(e) => setAdvisorQuery(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleSendMessage()}
              className="flex-1 bg-slate-900 border border-slate-700 rounded-lg px-3 py-1.5 text-xs text-white focus:outline-none focus:ring-1 focus:ring-amber-500"
            />
            <button
              onClick={handleSendMessage}
              className="bg-amber-500 hover:bg-amber-400 text-black font-semibold px-3 py-1.5 rounded-lg text-xs transition"
            >
              Send
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
