// src/app/page.tsx
export default async function HomePage() {
  const res = await fetch('/data/strategies.json', {
    cache: 'force-cache', // ⬅️ 改为 force-cache
    next: { revalidate: 60 } // 每 60 秒刷新一次
  });
  const strategies = await res.json();

  return (
    <div className="min-h-screen bg-gray-900 text-white p-8">
      <h1 className="text-3xl font-bold mb-8 text-cyan-400">Strategy Dashboard</h1>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {Object.values(strategies).map((s: any) => (
          <Link href={`/strategies/${s.strategyId}`} key={s.strategyId}>
            <div className="bg-gray-800 p-6 rounded-xl border border-cyan-900/50 hover:border-cyan-500 cursor-pointer transition">
              <h2 className="text-xl font-semibold">{s.name}</h2>
              <p className="mt-2 text-green-400">+{s.performance.netProfitPct.toFixed(2)}%</p>
            </div>
          </Link>
        ))}
      </div>
    </div>
  );
}