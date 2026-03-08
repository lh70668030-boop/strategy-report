// src/components/EquityCurveChart.tsx
'use client';

import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

interface EquityPoint {
  timestamp: string;
  equity: number;
}

export function EquityCurveChart({ data }: { data: EquityPoint[] }) {
  const chartData = data.map(d => ({
    date: new Date(d.timestamp).toLocaleDateString(),
    equity: d.equity
  }));

  return (
    <div className="bg-gray-800 p-4 rounded-xl border border-cyan-900/30">
      <h3 className="text-lg font-medium mb-3 text-cyan-300">Equity Curve</h3>
      <div className="h-80">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
            <XAxis dataKey="date" stroke="#9CA3AF" fontSize={12} />
            <YAxis stroke="#9CA3AF" fontSize={12} />
            <Tooltip 
              contentStyle={{ backgroundColor: '#1F2937', borderColor: '#06B6D4' }}
              labelStyle={{ color: '#06B6D4' }}
            />
            <Line 
              type="monotone" 
              dataKey="equity" 
              stroke="#06B6D4" 
              strokeWidth={2}
              dot={false}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}