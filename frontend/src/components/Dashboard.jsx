import React, { useState, useEffect, useMemo } from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip as RechartsTooltip, ResponsiveContainer, AreaChart, Area, ScatterChart, Scatter, ZAxis, Legend } from 'recharts';
import { ComposableMap, Geographies, Geography, Sphere, Graticule, ZoomableGroup } from 'react-simple-maps';
import { scaleLinear } from 'd3-scale';
import dashboardService from '../services/dashboardService';

const geoUrl = "https://cdn.jsdelivr.net/npm/world-atlas@2/countries-110m.json";

// A beautifully styled custom tooltip for Recharts
const CustomTooltip = ({ active, payload, label }) => {
  if (active && payload && payload.length) {
    return (
      <div className="bg-white border border-slate-100 p-4 rounded-lg shadow-lg">
        <p className="font-semibold text-slate-800 mb-2">{label}</p>
        {payload.map((entry, index) => (
          <p key={index} className="text-sm text-slate-600 flex items-center gap-2">
            <span className="w-3 h-3 rounded-full" style={{ backgroundColor: entry.color || entry.fill }}></span>
            <span className="font-medium">{entry.name}:</span>
            <span>{typeof entry.value === 'number' ? entry.value.toLocaleString() : entry.value}</span>
          </p>
        ))}
      </div>
    );
  }
  return null;
};

const Dashboard = () => {
  const [regionTxt, setRegionTxt] = useState('');
  const [countryTxt, setCountryTxt] = useState('');
  const [gname, setGname] = useState('');
  const [loading, setLoading] = useState(false);

  // Data States
  const [mapData, setMapData] = useState({});
  const [trendChartData, setTrendChartData] = useState([]);
  const [attackRegionData, setAttackRegionData] = useState({ data: [], types: [] });
  const [scatterData, setScatterData] = useState([]);

  // Modal and Tooltip State
  const [tooltipContent, setTooltipContent] = useState("");
  const [tooltipPos, setTooltipPos] = useState({ x: 0, y: 0 });
  const [selectedCountry, setSelectedCountry] = useState(null);
  const [countryDetails, setCountryDetails] = useState(null);
  const [loadingDetails, setLoadingDetails] = useState(false);

  const fetchStats = async () => {
    setLoading(true);
    try {
      // 1. Fetch Map Data (Group by Country)
      const p1 = new URLSearchParams();
      if (regionTxt) p1.append('regionTxt', regionTxt); else p1.append('regionTxt', 'ALL');
      if (countryTxt) p1.append('countryTxt', countryTxt); // Unconstrained to get all countries
      if (gname) p1.append('gname', gname); else p1.append('gname', 'ALL');
      p1.append('iyear', 'ALL');
      p1.append('attacktype1Txt', 'ALL');
      p1.append('targtype1Txt', 'ALL');
      p1.append('weaptype1Txt', 'ALL');
      p1.append('casualtyLevel', 'ALL');
      p1.append('page', 0);
      p1.append('size', 1000);

      // 2. Fetch Trend Data (Group by iyear)
      const p2 = new URLSearchParams();
      if (regionTxt) p2.append('regionTxt', regionTxt); else p2.append('regionTxt', 'ALL');
      if (countryTxt) p2.append('countryTxt', countryTxt); else p2.append('countryTxt', 'ALL');
      if (gname) p2.append('gname', gname); else p2.append('gname', 'ALL');
      // No iyear to group by it
      p2.append('attacktype1Txt', 'ALL');
      p2.append('targtype1Txt', 'ALL');
      p2.append('weaptype1Txt', 'ALL');
      p2.append('casualtyLevel', 'ALL');
      p2.append('page', 0);
      p2.append('size', 1000);

      // 3. Fetch Attack Region Data (Group by regionTxt AND attacktype1Txt)
      const p3 = new URLSearchParams();
      if (regionTxt) p3.append('regionTxt', regionTxt);
      if (countryTxt) p3.append('countryTxt', countryTxt); else p3.append('countryTxt', 'ALL');
      if (gname) p3.append('gname', gname); else p3.append('gname', 'ALL');
      p3.append('iyear', 'ALL');
      p3.append('targtype1Txt', 'ALL');
      p3.append('weaptype1Txt', 'ALL');
      p3.append('casualtyLevel', 'ALL');
      p3.append('page', 0);
      p3.append('size', 2000);

      // 4. Fetch Scatter Data (Group by regionTxt)
      const p4 = new URLSearchParams();
      if (regionTxt) p4.append('regionTxt', regionTxt);
      if (countryTxt) p4.append('countryTxt', countryTxt); else p4.append('countryTxt', 'ALL');
      if (gname) p4.append('gname', gname); else p4.append('gname', 'ALL');
      p4.append('iyear', 'ALL');
      p4.append('attacktype1Txt', 'ALL');
      p4.append('targtype1Txt', 'ALL');
      p4.append('weaptype1Txt', 'ALL');
      p4.append('casualtyLevel', 'ALL');
      p4.append('page', 0);
      p4.append('size', 1000);

      const [res1, res2, res3, res4] = await Promise.all([
        dashboardService.getCubeStats(p1),
        dashboardService.getCubeStats(p2),
        dashboardService.getCubeStats(p3),
        dashboardService.getCubeStats(p4)
      ]);

      // Process Map Data
      const mData = {};
      (res1?.data?.content || []).forEach(item => {
        if (item.countryTxt !== 'ALL' && item.countryTxt !== 'Unknown') {
          mData[item.countryTxt] = (mData[item.countryTxt] || 0) + (item.support || 0);
        }
      });
      setMapData(mData);

      // Process Trend Data
      const tData = {};
      (res2?.data?.content || []).forEach(item => {
        if (item.iyear !== 'ALL' && item.iyear !== 'Unknown') {
          tData[item.iyear] = (tData[item.iyear] || 0) + (item.totalCasualties || 0);
        }
      });
      setTrendChartData(Object.keys(tData).sort().map(k => ({ time: k, casualties: tData[k] })));

      // Process Attack Region Data
      const aMap = {};
      const aTypes = new Set();
      (res3?.data?.content || []).forEach(item => {
        if (item.regionTxt !== 'ALL' && item.regionTxt !== 'Unknown' && item.attacktype1Txt !== 'ALL' && item.attacktype1Txt !== 'Unknown') {
          if (!aMap[item.regionTxt]) aMap[item.regionTxt] = { name: item.regionTxt };
          aMap[item.regionTxt][item.attacktype1Txt] = (aMap[item.regionTxt][item.attacktype1Txt] || 0) + (item.support || 0);
          aTypes.add(item.attacktype1Txt);
        }
      });
      
      const aDataSorted = Object.values(aMap).sort((a,b) => {
        const sumA = Object.keys(a).filter(k => k!=='name').reduce((s,k)=>s+a[k],0);
        const sumB = Object.keys(b).filter(k => k!=='name').reduce((s,k)=>s+b[k],0);
        return sumB - sumA;
      }).slice(0, 8);
      
      setAttackRegionData({ data: aDataSorted, types: Array.from(aTypes).slice(0, 6) });

      // Process Scatter Data
      const sMap = {};
      (res4?.data?.content || []).forEach(item => {
        if (item.regionTxt !== 'ALL' && item.regionTxt !== 'Unknown') {
          if (!sMap[item.regionTxt]) sMap[item.regionTxt] = { name: item.regionTxt, attacks: 0, killed: 0 };
          sMap[item.regionTxt].attacks += (item.support || 0);
          sMap[item.regionTxt].killed += (item.totalKilled || 0);
        }
      });
      setScatterData(Object.values(sMap));

    } catch (error) {
      console.error("API Error:", error);
    } finally {
      setLoading(false);
    }
  };

  const [regionOptions, setRegionOptions] = useState([
    "Middle East & North Africa", "South Asia", "South America", 
    "Sub-Saharan Africa", "Western Europe", "Southeast Asia", 
    "Central America & Caribbean", "Eastern Europe", "North America", 
    "East Asia", "Central Asia", "Australasia & Oceania"
  ]);
  const [groupOptions, setGroupOptions] = useState([]);
  const [countryOptions, setCountryOptions] = useState([]);

  useEffect(() => {
    fetchStats();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  useEffect(() => {
    const timer = setTimeout(async () => {
      try {
        const pR = new URLSearchParams();
        pR.append('countryTxt', countryTxt || 'ALL');
        pR.append('gname', gname || 'ALL');
        pR.append('iyear', 'ALL'); pR.append('attacktype1Txt', 'ALL'); pR.append('targtype1Txt', 'ALL'); pR.append('weaptype1Txt', 'ALL'); pR.append('casualtyLevel', 'ALL');
        pR.append('page', 0); pR.append('size', 200);

        const pC = new URLSearchParams();
        pC.append('regionTxt', regionTxt || 'ALL');
        pC.append('gname', gname || 'ALL');
        pC.append('iyear', 'ALL'); pC.append('attacktype1Txt', 'ALL'); pC.append('targtype1Txt', 'ALL'); pC.append('weaptype1Txt', 'ALL'); pC.append('casualtyLevel', 'ALL');
        pC.append('page', 0); pC.append('size', 1000); 

        const pG = new URLSearchParams();
        pG.append('regionTxt', regionTxt || 'ALL');
        pG.append('countryTxt', countryTxt || 'ALL');
        pG.append('iyear', 'ALL'); pG.append('attacktype1Txt', 'ALL'); pG.append('targtype1Txt', 'ALL'); pG.append('weaptype1Txt', 'ALL'); pG.append('casualtyLevel', 'ALL');
        pG.append('page', 0); pG.append('size', 1000); 

        const [rR, rC, rG] = await Promise.all([
          dashboardService.getCubeStats(pR),
          dashboardService.getCubeStats(pC),
          dashboardService.getCubeStats(pG)
        ]);

        const regions = (rR?.data?.content || []).map(i => i.regionTxt).filter(n => n && n !== 'ALL' && n !== 'Unknown');
        const countries = (rC?.data?.content || []).map(i => i.countryTxt).filter(n => n && n !== 'ALL' && n !== 'Unknown');
        const groups = (rG?.data?.content || []).map(i => i.gname).filter(n => n && n !== 'ALL' && n !== 'Unknown');

        // Update options. If an API returns empty (due to invalid intermediate typing), it will correctly clear the options.
        if (regions.length > 0 || !countryTxt) setRegionOptions(regions);
        if (countries.length > 0 || !regionTxt) setCountryOptions(countries.sort());
        if (groups.length > 0 || (!regionTxt && !countryTxt)) setGroupOptions(groups);

      } catch (err) {
        console.error("Failed to fetch interconnected filter options", err);
      }
    }, 400); // 400ms debounce

    return () => clearTimeout(timer);
  }, [regionTxt, countryTxt, gname]);

  const handleFilter = (e) => {
    e.preventDefault();
    fetchStats();
  };

  const fetchCountryDetails = async (countryName) => {
    setSelectedCountry(countryName);
    setLoadingDetails(true);
    try {
      // 1. Fetch Yearly Trend (iyear = any, others = 'ALL')
      const trendParams = new URLSearchParams();
      trendParams.append('countryTxt', countryName);
      trendParams.append('regionTxt', 'ALL');
      trendParams.append('gname', 'ALL');
      trendParams.append('attacktype1Txt', 'ALL');
      trendParams.append('targtype1Txt', 'ALL');
      trendParams.append('weaptype1Txt', 'ALL');
      trendParams.append('casualtyLevel', 'ALL');
      trendParams.append('page', 0);
      trendParams.append('size', 200); 
      
      const trendRes = await dashboardService.getCubeStats(trendParams);
      const trendContent = trendRes?.data?.content || [];
      
      const trendData = trendContent
        .filter(item => item.iyear !== 'ALL' && item.iyear !== 'Unknown')
        .sort((a, b) => a.iyear.localeCompare(b.iyear))
        .map(item => ({ year: item.iyear, attacks: item.support }));

      // 2. Fetch Top Groups (gname = any, others = 'ALL')
      const groupParams = new URLSearchParams();
      groupParams.append('countryTxt', countryName);
      groupParams.append('regionTxt', 'ALL');
      groupParams.append('iyear', 'ALL');
      groupParams.append('attacktype1Txt', 'ALL');
      groupParams.append('targtype1Txt', 'ALL');
      groupParams.append('weaptype1Txt', 'ALL');
      groupParams.append('casualtyLevel', 'ALL');
      groupParams.append('page', 0);
      groupParams.append('size', 200); 
      
      const groupRes = await dashboardService.getCubeStats(groupParams);
      const groupContent = groupRes?.data?.content || [];
      
      const groupData = groupContent
        .filter(item => item.gname !== 'ALL' && item.gname !== 'Unknown')
        .sort((a, b) => b.support - a.support)
        .map(item => ({ name: item.gname, attacks: item.support }))
        .slice(0, 5);
      
      setCountryDetails({ trendData, groupData });
    } catch (err) {
      console.error(err);
    } finally {
      setLoadingDetails(false);
    }
  };

  const colors = ["#2563eb", "#dc2626", "#f59e0b", "#10b981", "#8b5cf6", "#ec4899"];
  const maxAttacks = Math.max(...Object.values(mapData).concat([1]));
  const colorScale = scaleLinear().domain([0, maxAttacks]).range(["#fee2e2", "#991b1b"]);

  return (
    <div className="min-h-screen bg-slate-50 p-6 md:p-10 font-sans relative">
      
      {/* Map Tooltip */}
      {tooltipContent && (
        <div 
          className="fixed bg-slate-900 text-white px-3 py-1.5 rounded-lg text-sm shadow-xl z-50 pointer-events-none transform -translate-x-1/2 -translate-y-full whitespace-nowrap"
          style={{ left: tooltipPos.x, top: tooltipPos.y - 15 }}
        >
          {tooltipContent}
          <div className="absolute w-2 h-2 bg-slate-900 rotate-45 left-1/2 -bottom-1 -translate-x-1/2"></div>
        </div>
      )}

      {/* Country Details Modal */}
      {selectedCountry && (
        <div className="fixed inset-0 bg-slate-900/40 flex items-center justify-center z-40 p-4 backdrop-blur-sm animate-in fade-in duration-200">
          <div className="bg-white rounded-3xl shadow-2xl w-full max-w-4xl max-h-[90vh] overflow-hidden flex flex-col animate-in zoom-in-95 duration-200">
            {/* Modal Header */}
            <div className="px-6 py-4 border-b border-slate-100 flex justify-between items-center bg-slate-50/50">
              <div>
                <h2 className="text-2xl font-black text-slate-900">{selectedCountry}</h2>
                <p className="text-sm text-slate-500 font-medium">Detailed Terrorism Report</p>
              </div>
              <button onClick={() => setSelectedCountry(null)} className="p-2 hover:bg-slate-200 rounded-full transition-colors cursor-pointer">
                <svg className="w-6 h-6 text-slate-500" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" /></svg>
              </button>
            </div>
            
            {/* Modal Body */}
            <div className="p-6 overflow-y-auto flex-1 bg-white">
              {loadingDetails ? (
                <div className="flex flex-col items-center justify-center h-64">
                   <span className="w-10 h-10 border-4 border-blue-500/30 border-t-blue-500 rounded-full animate-spin mb-4"></span>
                   <p className="text-slate-500 font-medium animate-pulse">Analyzing country data...</p>
                </div>
              ) : (
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                  {/* Modal Chart 1: Trend */}
                  <div className="bg-slate-50 p-6 rounded-3xl border border-slate-100">
                    <h3 className="font-bold text-slate-800 mb-6 flex items-center gap-2">
                      <svg className="w-5 h-5 text-blue-500" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 12l3-3 3 3 4-4M8 21l4-4 4 4M3 4h18M4 4h16v12a1 1 0 01-1 1H5a1 1 0 01-1-1V4z" /></svg>
                      Terrorism Through the Years
                    </h3>
                    <div className="h-[250px] w-full">
                      {countryDetails?.trendData?.length > 0 ? (
                        <ResponsiveContainer width="100%" height="100%">
                          <ScatterChart margin={{ top: 10, right: 10, bottom: 0, left: -20 }}>
                            <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e2e8f0" />
                            <XAxis dataKey="year" axisLine={false} tickLine={false} tick={{ fontSize: 11, fill: '#64748b' }} />
                            <YAxis dataKey="attacks" axisLine={false} tickLine={false} tick={{ fontSize: 11, fill: '#64748b' }} />
                            <RechartsTooltip cursor={{ strokeDasharray: '3 3' }} content={<CustomTooltip />} />
                            <Scatter name="Attacks" data={countryDetails.trendData} fill="#3b82f6" line={{ stroke: '#3b82f6', strokeWidth: 2 }} shape="circle" />
                          </ScatterChart>
                        </ResponsiveContainer>
                      ) : (
                        <div className="flex h-full items-center justify-center text-slate-400 text-sm bg-slate-100/50 rounded-xl border border-dashed border-slate-200">No yearly data found.</div>
                      )}
                    </div>
                  </div>
                  
                  {/* Modal Chart 2: Top Groups */}
                  <div className="bg-slate-50 p-6 rounded-3xl border border-slate-100">
                    <h3 className="font-bold text-slate-800 mb-6 flex items-center gap-2">
                      <svg className="w-5 h-5 text-red-500" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" /></svg>
                      Top Terrorist Organizations
                    </h3>
                    <div className="space-y-3">
                      {countryDetails?.groupData?.length > 0 ? (
                        countryDetails.groupData.map((g, i) => (
                          <div key={i} className="flex justify-between items-center bg-white p-4 rounded-xl shadow-sm border border-slate-100 hover:shadow-md transition-shadow">
                            <span className="font-semibold text-slate-700 text-sm truncate pr-4" title={g.name}>{g.name}</span>
                            <span className="bg-red-50 text-red-600 py-1.5 px-3 rounded-lg text-xs font-bold whitespace-nowrap border border-red-100">{g.attacks.toLocaleString()} attacks</span>
                          </div>
                        ))
                      ) : (
                        <div className="flex h-full min-h-[200px] items-center justify-center text-slate-400 text-sm bg-slate-100/50 rounded-xl border border-dashed border-slate-200">No specific group data found.</div>
                      )}
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      <div className="max-w-7xl mx-auto space-y-8">
        
        {/* Header Section */}
        <div className="flex flex-col md:flex-row md:items-end justify-between gap-4">
          <div>
            <h1 className="text-4xl font-black text-slate-900 tracking-tight">Security Analytics</h1>
            <p className="text-slate-500 mt-2 font-medium">Global Risk & Intelligence Dashboard</p>
          </div>
          
          <form onSubmit={handleFilter} className="bg-white p-3 rounded-2xl shadow-sm border border-slate-200 flex flex-wrap md:flex-nowrap gap-3 items-center">
            
            <datalist id="region-list">
              {regionOptions
                .filter(r => !regionTxt || r.toLowerCase().startsWith(regionTxt.toLowerCase()))
                .map(r => <option key={r} value={r} />)}
            </datalist>

            <datalist id="country-list">
              {countryOptions
                .filter(c => !countryTxt || c.toLowerCase().startsWith(countryTxt.toLowerCase()))
                .map(c => <option key={c} value={c} />)}
            </datalist>

            <datalist id="group-list">
              {groupOptions
                .filter(g => !gname || g.toLowerCase().startsWith(gname.toLowerCase()))
                .map(g => <option key={g} value={g} />)}
            </datalist>

            <input 
              type="text" 
              list="region-list"
              placeholder="Region..." 
              value={regionTxt}
              onChange={(e) => setRegionTxt(e.target.value)}
              className="px-4 py-2 bg-slate-50 border-none rounded-xl focus:ring-2 focus:ring-blue-500 outline-none text-sm w-full md:w-36"
            />
            <input 
              type="text" 
              list="country-list"
              placeholder="Country..." 
              value={countryTxt}
              onChange={(e) => setCountryTxt(e.target.value)}
              className="px-4 py-2 bg-slate-50 border-none rounded-xl focus:ring-2 focus:ring-blue-500 outline-none text-sm w-full md:w-36"
            />
            <input 
              type="text" 
              list="group-list"
              placeholder="Terrorist Group..." 
              value={gname}
              onChange={(e) => setGname(e.target.value)}
              className="px-4 py-2 bg-slate-50 border-none rounded-xl focus:ring-2 focus:ring-blue-500 outline-none text-sm w-full md:w-48"
            />
            <button 
              type="submit" 
              disabled={loading}
              className="px-6 py-2 bg-slate-900 hover:bg-slate-800 text-white font-bold rounded-xl transition-colors flex items-center justify-center min-w-[120px] cursor-pointer"
            >
              {loading ? <span className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin"></span> : "Filter"}
            </button>
          </form>
        </div>

        {/* Charts Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          
          {/* Chart 1: Map */}
          <div className="bg-white p-6 rounded-3xl shadow-sm border border-slate-100 flex flex-col col-span-1 lg:col-span-2 hover:shadow-md transition-shadow">
            <div className="mb-4">
              <h3 className="text-xl font-bold text-slate-800">Regions Attacked By Terrorist Groups</h3>
              <p className="text-sm text-slate-500">Geographical heatmap of incident volume. <span className="font-bold text-blue-500">Hover</span> to see metadata, <span className="font-bold text-blue-500">Click</span> for deep analysis.</p>
            </div>
            <div className="flex-1 w-full bg-slate-50 rounded-2xl overflow-hidden border border-slate-100 relative">
              <ComposableMap projectionConfig={{ scale: 140 }} height={400}>
                <ZoomableGroup>
                  <Sphere stroke="#cbd5e1" strokeWidth={0.5} />
                  <Graticule stroke="#cbd5e1" strokeWidth={0.5} />
                  <Geographies geography={geoUrl}>
                    {({ geographies }) =>
                      geographies.map((geo) => {
                        let countryName = geo.properties.name;
                        
                        // Map TopoJSON country names to GTD database names
                        const nameMapping = {
                          "United States of America": "United States",
                          "Dem. Rep. Congo": "Democratic Republic of the Congo",
                          "Dominican Rep.": "Dominican Republic",
                          "Central African Rep.": "Central African Republic",
                          "Eq. Guinea": "Equatorial Guinea",
                          "Bosnia and Herz.": "Bosnia-Herzegovina",
                          "S. Sudan": "South Sudan",
                          "W. Sahara": "Western Sahara",
                          "Solomon Is.": "Solomon Islands",
                          "Falkland Is.": "Falkland Islands",
                          "Republic of Serbia": "Serbia",
                          "Macedonia": "Macedonia",
                          "Syria": "Syria"
                        };
                        
                        if (nameMapping[countryName]) {
                          countryName = nameMapping[countryName];
                        }

                        const attacks = mapData[countryName] || 0;
                        return (
                          <Geography
                            key={geo.rsmKey}
                            geography={geo}
                            fill={attacks > 0 ? colorScale(attacks) : "#f8fafc"}
                            stroke="#cbd5e1"
                            strokeWidth={0.5}
                            onMouseEnter={(e) => {
                              if (attacks > 0) {
                                setTooltipContent(`${countryName}: ${attacks.toLocaleString()} attacks`);
                              } else {
                                setTooltipContent(`${countryName}: No data`);
                              }
                            }}
                            onMouseMove={(e) => {
                              setTooltipPos({ x: e.clientX, y: e.clientY });
                            }}
                            onMouseLeave={() => {
                              setTooltipContent("");
                            }}
                            onClick={() => {
                              if (attacks > 0) fetchCountryDetails(countryName);
                            }}
                            style={{
                              hover: { fill: "#ef4444", outline: "none", cursor: attacks > 0 ? "pointer" : "default" },
                              default: { outline: "none" },
                              pressed: { outline: "none" }
                            }}
                          />
                        );
                      })
                    }
                  </Geographies>
                </ZoomableGroup>
              </ComposableMap>
            </div>
          </div>

          {/* Chart 2: Casualty Trends */}
          <div className="bg-white p-6 rounded-3xl shadow-sm border border-slate-100 flex flex-col hover:shadow-md transition-shadow">
            <div className="mb-6">
              <h3 className="text-xl font-bold text-slate-800">Yearly Casualty Trends</h3>
              <p className="text-sm text-slate-500">Historical progression of total casualties.</p>
            </div>
            <div className="flex-1 w-full h-[350px] min-h-[350px]">
              {trendChartData.length > 0 ? (
                <ResponsiveContainer width="100%" height="100%">
                  <AreaChart data={trendChartData} margin={{ top: 10, right: 10, left: -10, bottom: 0 }}>
                    <defs>
                      <linearGradient id="colorCasualties" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="#10b981" stopOpacity={0.3}/>
                        <stop offset="95%" stopColor="#10b981" stopOpacity={0}/>
                      </linearGradient>
                    </defs>
                    <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e2e8f0" />
                    <XAxis dataKey="time" axisLine={false} tickLine={false} tick={{ fontSize: 12, fill: '#64748b' }} minTickGap={20} />
                    <YAxis axisLine={false} tickLine={false} tick={{ fontSize: 12, fill: '#64748b' }} tickFormatter={(val) => `${val / 1000}k`} />
                    <RechartsTooltip content={<CustomTooltip />} />
                    <Area type="monotone" dataKey="casualties" name="Casualties" stroke="#10b981" strokeWidth={3} fillOpacity={1} fill="url(#colorCasualties)" />
                  </AreaChart>
                </ResponsiveContainer>
              ) : (
                <div className="flex items-center justify-center h-full text-slate-400">No data available</div>
              )}
            </div>
          </div>

          {/* Chart 3: Attack Types by Region */}
          <div className="bg-white p-6 rounded-3xl shadow-sm border border-slate-100 flex flex-col hover:shadow-md transition-shadow">
            <div className="mb-6">
              <h3 className="text-xl font-bold text-slate-800">Tactics by Region</h3>
              <p className="text-sm text-slate-500">Distribution of attack methods across territories.</p>
            </div>
            <div className="flex-1 w-full h-[350px] min-h-[350px]">
              {attackRegionData.data.length > 0 ? (
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={attackRegionData.data} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                    <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e2e8f0" />
                    <XAxis dataKey="name" axisLine={false} tickLine={false} tick={{ fontSize: 11, fill: '#64748b' }} tickFormatter={(val) => val.length > 10 ? val.substring(0, 10) + '...' : val} />
                    <YAxis axisLine={false} tickLine={false} tick={{ fontSize: 12, fill: '#64748b' }} tickFormatter={(val) => `${val / 1000}k`} />
                    <RechartsTooltip content={<CustomTooltip />} cursor={{ fill: '#f8fafc' }} />
                    <Legend iconType="circle" wrapperStyle={{ fontSize: '12px' }} />
                    {attackRegionData.types.map((type, index) => (
                      <Bar key={type} dataKey={type} stackId="a" fill={colors[index % colors.length]} radius={index === attackRegionData.types.length - 1 ? [4, 4, 0, 0] : [0, 0, 0, 0]} />
                    ))}
                  </BarChart>
                </ResponsiveContainer>
              ) : (
                <div className="flex items-center justify-center h-full text-slate-400">No data available</div>
              )}
            </div>
          </div>

          {/* Chart 4: Attacks vs Killed */}
          <div className="bg-white p-6 rounded-3xl shadow-sm border border-slate-100 flex flex-col hover:shadow-md transition-shadow col-span-1 lg:col-span-2">
            <div className="mb-6">
              <h3 className="text-xl font-bold text-slate-800">Incident Volume vs Lethality</h3>
              <p className="text-sm text-slate-500">Correlation between number of attacks and total killed by region.</p>
            </div>
            <div className="flex-1 w-full h-[350px] min-h-[350px]">
              {scatterData.length > 0 ? (
                <ResponsiveContainer width="100%" height="100%">
                  <ScatterChart margin={{ top: 20, right: 20, bottom: 20, left: 20 }}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                    <XAxis type="number" dataKey="attacks" name="Attacks" tick={{ fontSize: 12, fill: '#64748b' }} axisLine={false} tickLine={false} />
                    <YAxis type="number" dataKey="killed" name="Killed" tick={{ fontSize: 12, fill: '#64748b' }} axisLine={false} tickLine={false} />
                    <ZAxis type="category" dataKey="name" name="Region" />
                    <RechartsTooltip cursor={{ strokeDasharray: '3 3' }} content={<CustomTooltip />} />
                    <Scatter name="Regions" data={scatterData} fill="#ec4899" shape="circle" />
                  </ScatterChart>
                </ResponsiveContainer>
              ) : (
                <div className="flex items-center justify-center h-full text-slate-400">No data available</div>
              )}
            </div>
          </div>

        </div>
      </div>
    </div>
  );
};

export default Dashboard;
