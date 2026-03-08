<<<<<<< HEAD
# convert_report.py
import pandas as pd
import json
import sys
from datetime import datetime
from pathlib import Path

def parse_excel_to_strategy(excel_path: str) -> dict:
    # === 读取三个工作表 ===
    perf_df = pd.read_excel(excel_path, sheet_name="表现")
    trades_df = pd.read_excel(excel_path, sheet_name="交易清单")
    attrs_df = pd.read_excel(excel_path, sheet_name="属性")

    # === 提取性能指标（从"表现"表）===
    def get_value(df, key):
        row = df[df.iloc[:, 0] == key]
        return row.iloc[0, 1] if not row.empty else None

    perf = {
        "initialCapital": float(get_value(perf_df, "初始资本")),
        "netProfitUsd": float(get_value(perf_df, "净损益")),
        "netProfitPct": float(str(get_value(perf_df, "总收益率")).replace('%', '')),
        "grossProfitUsd": float(get_value(perf_df, "毛利润")),
        "grossLossUsd": float(get_value(perf_df, "毛亏损")),
        "profitFactor": float(get_value(perf_df, "盈利因子")),
        "sharpeRatio": float(get_value(perf_df, "夏普比率")),
        "sortinoRatio": float(get_value(perf_df, "索提诺比率")),
        "maxDrawdownIntrabarUsd": float(get_value(perf_df, "最大回撤(资金内)")),
        "maxDrawdownIntrabarPct": float(str(get_value(perf_df, "最大回撤(%)")).replace('%', '')),
        "buyAndHoldReturnUsd": float(get_value(perf_df, "买入持有损益")),
        "buyAndHoldReturnPct": float(str(get_value(perf_df, "买入持有收益率")).replace('%', '')),
        "cagr": float(str(get_value(perf_df, "年化复合增长率")).replace('%', ''))
    }

    # === 多头/空头统计（假设在"表现"表下方）===
    long_short = {
        "long": {
            "netProfitUsd": float(get_value(perf_df, "多头净损益")),
            "netProfitPct": float(str(get_value(perf_df, "多头收益率")).replace('%', '')),
            "totalTrades": int(get_value(perf_df, "多头总交易")),
            "winRate": float(str(get_value(perf_df, "多头胜率")).replace('%', '')),
            "avgWin": float(get_value(perf_df, "多头平均盈利")),
            "avgLoss": float(get_value(perf_df, "多头平均亏损")),
            "profitFactor": float(get_value(perf_df, "多头盈利因子"))
        },
        "short": {
            "netProfitUsd": float(get_value(perf_df, "空头净损益")),
            "netProfitPct": float(str(get_value(perf_df, "空头收益率")).replace('%', '')),
            "totalTrades": int(get_value(perf_df, "空头总交易")),
            "winRate": float(str(get_value(perf_df, "空头胜率")).replace('%', '')),
            "avgWin": float(get_value(perf_df, "空头平均盈利")),
            "avgLoss": float(get_value(perf_df, "空头平均亏损")),
            "profitFactor": float(get_value(perf_df, "空头盈利因子"))
        }
    }

    # === 交易明细 ===
    trades = []
    for _, row in trades_df.iterrows():
        trades.append({
            "tradeId": int(row["编号"]),
            "type": row["类型"],
            "entryTime": row["进场时间"].isoformat() + "Z",
            "exitTime": row["出场时间"].isoformat() + "Z",
            "entryPrice": float(row["进场价格"]),
            "exitPrice": float(row["出场价格"]),
            "pnlUsd": float(row["盈亏($)"]),
            "pnlPct": float(str(row["盈亏(%)"]).replace('%', '')),
            "barsHeld": int(row["持仓K线数"]),
            "signal": row["信号"]
        })

    # === 构建权益曲线（按出场时间累计）===
    equity_curve = []
    capital = perf["initialCapital"]
    sorted_trades = sorted(trades, key=lambda x: x["exitTime"])
    for t in sorted_trades:
        capital += t["pnlUsd"]
        equity_curve.append({
            "timestamp": t["exitTime"],
            "equity": round(capital, 2)
        })

    # === 策略参数 ===
    params = {}
    for _, row in attrs_df.iterrows():
        key = row["name"]
        val = row["value"]
        # 尝试转数字/布尔
        if isinstance(val, str):
            if val.lower() == "true": val = True
            elif val.lower() == "false": val = False
            elif val.replace('.', '', 1).isdigit():
                val = float(val) if '.' in val else int(val)
        params[key] = val

    # === 从文件名提取 ID（示例）===
    filename = Path(excel_path).stem
    strategy_id = filename.lower().replace(" ", "_").replace("-", "_")

    return {
        "strategyId": strategy_id,
        "name": filename,
        "symbol": "BINANCE:ETHUSDT.P",  # 可从参数中提取
        "timeframe": "15m",
        "backtestPeriod": {
            "start": sorted_trades[0]["entryTime"] if trades else "2025-08-01T00:00:00Z",
            "end": sorted_trades[-1]["exitTime"] if trades else "2026-03-08T00:00:00Z"
        },
        "lastUpdated": datetime.utcnow().isoformat() + "Z",
        "performance": perf,
        "longShort": long_short,
        "trades": trades,
        "equityCurve": equity_curve,
        "params": params
    }

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("用法: python convert_report.py <input.xlsx> <output.json>")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2]

    strategy = parse_excel_to_strategy(input_file)

    # 读取现有 strategies.json（如果存在）
    all_strategies = {}
    try:
        with open(output_file, 'r', encoding='utf-8') as f:
            all_strategies = json.load(f)
    except FileNotFoundError:
        pass

    # 更新或新增该策略
    all_strategies[strategy["strategyId"]] = strategy

    # 写回
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(all_strategies, f, indent=2, ensure_ascii=False)

    print(f"✅ 已生成策略: {strategy['name']}")
=======
# convert_report.py
import pandas as pd
import json
import sys
from datetime import datetime
from pathlib import Path

def parse_excel_to_strategy(excel_path: str) -> dict:
    # === 读取三个工作表 ===
    perf_df = pd.read_excel(excel_path, sheet_name="表现")
    trades_df = pd.read_excel(excel_path, sheet_name="交易清单")
    attrs_df = pd.read_excel(excel_path, sheet_name="属性")

    # === 提取性能指标（从"表现"表）===
    def get_value(df, key):
        row = df[df.iloc[:, 0] == key]
        return row.iloc[0, 1] if not row.empty else None

    perf = {
        "initialCapital": float(get_value(perf_df, "初始资本")),
        "netProfitUsd": float(get_value(perf_df, "净损益")),
        "netProfitPct": float(str(get_value(perf_df, "总收益率")).replace('%', '')),
        "grossProfitUsd": float(get_value(perf_df, "毛利润")),
        "grossLossUsd": float(get_value(perf_df, "毛亏损")),
        "profitFactor": float(get_value(perf_df, "盈利因子")),
        "sharpeRatio": float(get_value(perf_df, "夏普比率")),
        "sortinoRatio": float(get_value(perf_df, "索提诺比率")),
        "maxDrawdownIntrabarUsd": float(get_value(perf_df, "最大回撤(资金内)")),
        "maxDrawdownIntrabarPct": float(str(get_value(perf_df, "最大回撤(%)")).replace('%', '')),
        "buyAndHoldReturnUsd": float(get_value(perf_df, "买入持有损益")),
        "buyAndHoldReturnPct": float(str(get_value(perf_df, "买入持有收益率")).replace('%', '')),
        "cagr": float(str(get_value(perf_df, "年化复合增长率")).replace('%', ''))
    }

    # === 多头/空头统计（假设在"表现"表下方）===
    long_short = {
        "long": {
            "netProfitUsd": float(get_value(perf_df, "多头净损益")),
            "netProfitPct": float(str(get_value(perf_df, "多头收益率")).replace('%', '')),
            "totalTrades": int(get_value(perf_df, "多头总交易")),
            "winRate": float(str(get_value(perf_df, "多头胜率")).replace('%', '')),
            "avgWin": float(get_value(perf_df, "多头平均盈利")),
            "avgLoss": float(get_value(perf_df, "多头平均亏损")),
            "profitFactor": float(get_value(perf_df, "多头盈利因子"))
        },
        "short": {
            "netProfitUsd": float(get_value(perf_df, "空头净损益")),
            "netProfitPct": float(str(get_value(perf_df, "空头收益率")).replace('%', '')),
            "totalTrades": int(get_value(perf_df, "空头总交易")),
            "winRate": float(str(get_value(perf_df, "空头胜率")).replace('%', '')),
            "avgWin": float(get_value(perf_df, "空头平均盈利")),
            "avgLoss": float(get_value(perf_df, "空头平均亏损")),
            "profitFactor": float(get_value(perf_df, "空头盈利因子"))
        }
    }

    # === 交易明细 ===
    trades = []
    for _, row in trades_df.iterrows():
        trades.append({
            "tradeId": int(row["编号"]),
            "type": row["类型"],
            "entryTime": row["进场时间"].isoformat() + "Z",
            "exitTime": row["出场时间"].isoformat() + "Z",
            "entryPrice": float(row["进场价格"]),
            "exitPrice": float(row["出场价格"]),
            "pnlUsd": float(row["盈亏($)"]),
            "pnlPct": float(str(row["盈亏(%)"]).replace('%', '')),
            "barsHeld": int(row["持仓K线数"]),
            "signal": row["信号"]
        })

    # === 构建权益曲线（按出场时间累计）===
    equity_curve = []
    capital = perf["initialCapital"]
    sorted_trades = sorted(trades, key=lambda x: x["exitTime"])
    for t in sorted_trades:
        capital += t["pnlUsd"]
        equity_curve.append({
            "timestamp": t["exitTime"],
            "equity": round(capital, 2)
        })

    # === 策略参数 ===
    params = {}
    for _, row in attrs_df.iterrows():
        key = row["name"]
        val = row["value"]
        # 尝试转数字/布尔
        if isinstance(val, str):
            if val.lower() == "true": val = True
            elif val.lower() == "false": val = False
            elif val.replace('.', '', 1).isdigit():
                val = float(val) if '.' in val else int(val)
        params[key] = val

    # === 从文件名提取 ID（示例）===
    filename = Path(excel_path).stem
    strategy_id = filename.lower().replace(" ", "_").replace("-", "_")

    return {
        "strategyId": strategy_id,
        "name": filename,
        "symbol": "BINANCE:ETHUSDT.P",  # 可从参数中提取
        "timeframe": "15m",
        "backtestPeriod": {
            "start": sorted_trades[0]["entryTime"] if trades else "2025-08-01T00:00:00Z",
            "end": sorted_trades[-1]["exitTime"] if trades else "2026-03-08T00:00:00Z"
        },
        "lastUpdated": datetime.utcnow().isoformat() + "Z",
        "performance": perf,
        "longShort": long_short,
        "trades": trades,
        "equityCurve": equity_curve,
        "params": params
    }

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("用法: python convert_report.py <input.xlsx> <output.json>")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2]

    strategy = parse_excel_to_strategy(input_file)

    # 读取现有 strategies.json（如果存在）
    all_strategies = {}
    try:
        with open(output_file, 'r', encoding='utf-8') as f:
            all_strategies = json.load(f)
    except FileNotFoundError:
        pass

    # 更新或新增该策略
    all_strategies[strategy["strategyId"]] = strategy

    # 写回
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(all_strategies, f, indent=2, ensure_ascii=False)

    print(f"✅ 已生成策略: {strategy['name']}")
>>>>>>> 09d64ffa4fc579681da8fc65dd6a4c4f5612766c
    print(f"📄 输出到: {output_file}")