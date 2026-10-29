import { useEffect, useState } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { AlertCircle, CheckCircle2, Clock } from 'lucide-react';
import { getJanuaryAnalysis, getHealth } from './api';

function App() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [backendHealthy, setBackendHealthy] = useState(false);

  useEffect(() => {
    const fetchData = async () => {
      try {
        // First check if backend is running
        const health = await getHealth();
        setBackendHealthy(health.status === 'healthy');

        // Fetch the actual analysis data
        const analysisData = await getJanuaryAnalysis();
        setData(analysisData);
        setLoading(false);
      } catch (err) {
        setError(err.message || 'Failed to fetch data from backend. Is the Python server running?');
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  if (loading) {
    return (
      <div className="flex h-screen items-center justify-center bg-gray-50">
        <div className="text-xl font-semibold text-gray-600 animate-pulse">Loading Energy Data...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex h-screen items-center justify-center bg-gray-50 p-6">
        <div className="rounded-lg bg-red-50 p-6 text-red-800 max-w-lg border border-red-200">
          <div className="flex items-center gap-3 mb-2">
            <AlertCircle className="h-6 w-6 text-red-600" />
            <h2 className="text-lg font-bold">Connection Error</h2>
          </div>
          <p>{error}</p>
        </div>
      </div>
    );
  }

  const { summary, timeseries } = data;
  const metrics = summary.metrics;

  return (
    <div className="min-h-screen bg-gray-50 p-8 font-sans">
      <div className="mx-auto max-w-7xl">
        
        {/* Header */}
        <header className="mb-8">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">Wind Forecast Accuracy</h1>
              <p className="text-gray-500 mt-1">Day-Ahead Procurement Analysis • January 2026</p>
            </div>
            <div className="flex items-center gap-2 text-sm">
              <span className="flex items-center gap-1 text-green-700 bg-green-100 px-3 py-1 rounded-full font-medium">
                <CheckCircle2 className="h-4 w-4" /> Live Data
              </span>
              <span className="flex items-center gap-1 text-blue-700 bg-blue-100 px-3 py-1 rounded-full font-medium">
                <Clock className="h-4 w-4" /> D-1 Cutoff: {summary.cutoff_time}
              </span>
            </div>
          </div>
        </header>

        {/* KPI Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
          <Card title="Mean Abs Error (MAE)" value={`${metrics.mae} MW`} subtitle="Average absolute deviation" />
          <Card title="RMSE" value={`${metrics.rmse} MW`} subtitle="Penalizes large errors" />
          <Card title="Bias" value={`${metrics.bias} MW`} subtitle="Positive = Over-forecasted" />
          <Card title="WAPE" value={metrics.wape ? `${metrics.wape}%` : 'N/A'} subtitle="Weighted Abs % Error" />
        </div>

        {/* Chart Section */}
        <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100 mb-8">
          <h2 className="text-xl font-bold text-gray-800 mb-6">Actual vs Forecast Generation (MW)</h2>
          <div className="h-96">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={timeseries} margin={{ top: 5, right: 20, bottom: 5, left: 0 }}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e5e7eb" />
                <XAxis 
                  dataKey="startTime" 
                  tickFormatter={(tick) => new Date(tick).toLocaleDateString('en-GB', { day: 'numeric', month: 'short' })}
                  minTickGap={50}
                />
                <YAxis />
                <Tooltip 
                  labelFormatter={(label) => new Date(label).toLocaleString('en-GB')}
                  formatter={(value) => [Math.round(value) + ' MW']}
                />
                <Legend />
                <Line type="monotone" dataKey="actual" name="Actual Generation" stroke="#2563eb" strokeWidth={2} dot={false} />
                <Line type="monotone" dataKey="forecast" name="D-1 Forecast" stroke="#f59e0b" strokeWidth={2} dot={false} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Data Table */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
          <div className="p-6 border-b border-gray-100">
            <h2 className="text-xl font-bold text-gray-800">Interval Breakdown ({summary.total_intervals} records)</h2>
          </div>
          <div className="overflow-x-auto max-h-96">
            <table className="w-full text-left text-sm text-gray-600">
              <thead className="bg-gray-50 text-gray-900 sticky top-0">
                <tr>
                  <th className="p-4 font-semibold">Delivery Interval</th>
                  <th className="p-4 font-semibold">Forecast Published</th>
                  <th className="p-4 font-semibold text-right">Forecast (MW)</th>
                  <th className="p-4 font-semibold text-right">Actual (MW)</th>
                  <th className="p-4 font-semibold text-right">Error (MW)</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100">
                {timeseries.map((row, idx) => (
                  <tr key={idx} className="hover:bg-gray-50">
                    <td className="p-4">{new Date(row.startTime).toLocaleString('en-GB')}</td>
                    <td className="p-4">{new Date(row.publishTime).toLocaleString('en-GB')}</td>
                    <td className="p-4 text-right font-medium">{Math.round(row.forecast)}</td>
                    <td className="p-4 text-right font-medium">{Math.round(row.actual)}</td>
                    <td className={`p-4 text-right font-medium ${row.error > 0 ? 'text-amber-600' : 'text-blue-600'}`}>
                      {Math.round(row.error)}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
}

// Simple Card Component
function Card({ title, value, subtitle }) {
  return (
    <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
      <h3 className="text-sm font-medium text-gray-500 mb-1">{title}</h3>
      <div className="text-2xl font-bold text-gray-900 mb-1">{value}</div>
      <div className="text-xs text-gray-400">{subtitle}</div>
    </div>
  );
}

export default App;