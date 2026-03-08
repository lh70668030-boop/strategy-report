// src/app/strategies/[id]/page.tsx
'use client';

import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

export default async function StrategyPage({ params }: { params: { id: string } }) {
  const res = await fetch('/data/strategies.json', { cache: 'no-store' });
  const allStrategies = await res.json();
  const strategy = allStrategies[params.id];

  if (!strategy) {
    return <div className="p-10 text-red-400">Strategy not found</div>;
  }

  const chartData = strategy.equityCurve.map((point: any) => ({
    date: new Date(point.timestamp).toLocaleDateString(),
    equity: point.equity
  }));

  return (
    <div className="min-h-screen bg-gray-900 text-white p-8">
      <h1 className="text-2xl font-bold mb-6">{strategy.name}</h1>
      
      <div className="bg-gray-800 p-6 rounded-xl mb-8">
        <h2 className="text-lg mb-4 text-cyan-300">Equity Curve</h2>
        <div className="h-80">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
              <XAxis dataKey="date" stroke="#9CA3AF" />
              <YAxis stroke="#9CA3AF" />
              <Tooltip contentStyle={{ backgroundColor: '#1F2937' }} />
              <Line type="monotone" dataKey="equity" stroke="#06B6D4" strokeWidth={2} dot={false} />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
}