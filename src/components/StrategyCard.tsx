// src/components/StrategyCard.tsx
export function StrategyCard({ strategy }: { strategy: any }) {
  const { performance, name, lastUpdated } = strategy;
  const isProfitable = performance.netProfitPct > 0;

  return (
    <div className="bg-gray-800 rounded-xl p-5 border border-cyan-900/30 hover:border-cyan-500 transition-all hover:scale-[1.02]">
      <h2 className="text-lg font-semibold text-white mb-2">{name}</h2>
      <div className="flex items-center mb-3">
        <span className={`text-xl font-bold ${isProfitable ? 'text-green-400' : 'text-red-400'}`}>
          {isProfitable ? '+' : ''}{performance.netProfitPct.toFixed(2)}%
        </span>
        <span className="ml-2 text-sm text-gray-400">({performance.netProfitUsd.toFixed(2)} USD)</span>
      </div>
      <div className="text-sm text-gray-400">
        胜率: {((strategy.longShort.long.winRate + strategy.longShort.short.winRate) / 2).toFixed(1)}% · 
        更新: {new Date(lastUpdated).toLocaleDateString()}
      </div>
    </div>
  );
}