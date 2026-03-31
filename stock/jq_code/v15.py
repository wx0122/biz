from jqdata import *
import pandas as pd
import numpy as np
from scipy import stats

"""
================================================================================
🧠「变盘感知」v15.0 —— v7稳定版 + 三维新信息: 资金流向×财报窗口×尾盘分钟
================================================================================

为什么 v1.0 能跑 43%:
  → momentum + 行业热度 在 2025 AI行情中精准捕获强势板块
  → 选股逻辑简洁有效, 没有过度保护

为什么 v2/v3 变差:
  → v2: 引入组合级保护导致策略永久锁死
  → v3: 抛弃基本面, 纯技术面在震荡市失效

v4 的正确做法:
  ① 继承 v1.0 完整选股框架 (行业热度 + 因子打分)
  ② IC监控结论直接驱动权重:
       当前 debt_ratio ICIR=0.758 唯一有效 → 权重拉满
       pb/pe ICIR=-0.92/-0.77 强烈失效   → 权重归零
       size  ICIR=0.262 边缘有效          → 中等权重
       momentum ICIR负值                  → 最低但不归零(行情会变)
  ③ 每月重算IC → 权重自动跟随市场变化
  ④ 保留v1.0的时序修复(15:30扫描,09:31执行)
  ⑤ 简单可靠的止损止盈, 不引入复杂组合级保护

当前IC结论对应的权重(2026年3月):
  fin_risk(低负债): 45%  ← debt_ratio唯一有效因子
  size(小盘):       20%  ← 边缘有效
  quality(ROE):     15%  ← 质量因子中性
  growth(成长):     12%  ← 成长中性
  momentum:          5%  ← 失效但保留最低权重
  value(PB/PE):      3%  ← 强烈失效, 最低权重

行业热度加成始终生效(不受IC影响):
  热门行业内的票 +0.1~0.5分
  冷门行业内的票 -0.3分
================================================================================
"""


# ================================================================
#  初始化
# ================================================================
def initialize(context):
    set_benchmark('000300.XSHG')
    set_order_cost(OrderCost(
        close_tax=0.001, open_commission=0.0003,
        close_commission=0.0003, min_commission=5
    ), type='stock')
    set_option("avoid_future_data", True)
    set_slippage(FixedSlippage(0.01))

    g.hold_n          = 6
    g.min_money       = 2e7
    g.min_mcap        = 10
    g.max_mcap        = 500

    # 止损/止盈
    g.stop_loss       = -0.07   # 收紧止损, 快速切割小亏损
    g.trail_trigger   = 0.15    # 移动止盈触发
    g.trail_dd        = -0.07   # 移动止盈回撤
    g.rank_thresh     = 0.55    # 因子排名阈值

    # ── 核心: IC驱动的初始权重 (基于当前IC结论) ──────────────
    # 每月重算后自动更新
    g.factor_weights  = {
        'fin_risk': 0.45,   # debt_ratio ICIR=0.758 唯一有效
        'size':     0.20,   # size ICIR=0.262 边缘有效
        'quality':  0.15,   # 质量中性
        'growth':   0.12,   # 成长中性
        'momentum': 0.05,   # 动量失效但保留
        'value':    0.03,   # PB/PE强烈失效
    }

    g.hot_industries   = {}
    g.cold_industries  = set()
    g.minute_scores    = {}    # 尾盘分钟得分缓存 code→score
    g.report_window    = False # 当前是否在财报窗口期
    g.mcap_range      = (10, 400)
    g.entry           = {}
    g.entry_prev_close = {}
    g.pending_buy     = []
    g.pending_sell    = []
    g.factor_pool     = pd.DataFrame()
    g.price_cache     = {}
    g.mkt_uptrend     = True
    g.regime          = 'chaos'

    run_monthly(monthly_ic_update,  monthday=1, time='09:00')
    run_weekly(weekly_style_update, weekday=0,  time='09:10')
    run_daily(daily_open_trade,                 time='09:31')
    run_daily(daily_scan_close,                 time='15:30')


# ================================================================
#  月度: 重算IC → 更新权重
# ================================================================
def monthly_ic_update(context):
    log.info("\n" + "="*50)
    log.info(f"📅 月度IC更新: {context.current_dt.date()}")

    today     = context.current_dt
    start_str = (today - pd.DateOffset(months=18)).strftime('%Y-%m-%d')
    end_str   = str(today.date())

    ic_df = _calc_ic_history(start_str, end_str, forward_n=20, sample_n=300)
    if ic_df is None or ic_df.empty:
        log.info("  ⚠️ IC不足, 沿用上期权重"); return

    ic_stats = _analyze_ic(ic_df, window=6)
    if ic_stats.empty:
        log.info("  ⚠️ IC统计空"); return

    # ── 核心: 直接用ICIR决定权重 ──────────────────────────────
    # 规则:
    #   ICIR > 0.5  → 强有效, 权重×3
    #   0.2~0.5     → 有效, 权重×1.5
    #   -0.2~0.2    → 中性, 权重×1
    #   < -0.2      → 失效, 权重×0.3 (不归零, 因为因子有效性会周期切换)
    #   < -0.5      → 强烈失效, 权重×0.1

    factor_map = {
        'roe':        'quality',
        'debt_ratio': 'fin_risk',
        'size':       'size',
        'pb':         'value',
        'pe':         'value',
        'momentum':   'momentum',
    }

    # 基础权重
    base = {'quality':0.20, 'fin_risk':0.20, 'size':0.20,
            'value':0.20, 'growth':0.10, 'momentum':0.10}

    # 按ICIR调整倍数
    multipliers = {}
    for fname, row in ic_stats.iterrows():
        gname = factor_map.get(fname, fname)
        icir  = float(row['latest_icir'])
        if icir > 0.5:
            mult = 3.0
        elif icir > 0.2:
            mult = 1.5
        elif icir > -0.2:
            mult = 1.0
        elif icir > -0.5:
            mult = 0.3
        else:
            mult = 0.1
        # 取该分组最高倍数
        if gname not in multipliers or mult > multipliers[gname]:
            multipliers[gname] = mult

    # 应用倍数
    raw = {}
    for k, v in base.items():
        raw[k] = v * multipliers.get(k, 1.0)

    total = sum(list(raw.values())) + 1e-8
    g.factor_weights = {k: round(v/total, 3) for k, v in raw.items()}

    # regime判定
    valid = [f for f, r in ic_stats.iterrows()
             if float(r['latest_icir']) > 0.25]
    n = len(valid)
    old_regime = g.regime
    g.regime = 'bull' if n >= 3 else ('bear' if n == 0 else 'chaos')
    if old_regime != g.regime:
        g.factor_pool = pd.DataFrame()

    log.info(f"  有效因子({n}): {', '.join(valid) or '无'}")
    log.info(f"  Regime: {old_regime}→{g.regime}")
    log.info(f"  更新权重:")
    for k, v in sorted(g.factor_weights.items(), key=lambda x: -x[1]):
        bar = '█' * int(v * 25)
        icir_info = ''
        for fname, row in ic_stats.iterrows():
            if factor_map.get(fname) == k:
                icir_info = f"ICIR={float(row['latest_icir']):.3f}"
                break
        log.info(f"    {k:<12} {v*100:>5.1f}%  {bar}  {icir_info}")


# ================================================================
#  周度: 风格 + 行业热度
# ================================================================
def weekly_style_update(context):
    today = context.current_dt
    style = _calc_style_scores(today)

    cap_lbl = '小盘' if style['cap'] > 0.3 else ('大盘' if style['cap'] < -0.3 else '均衡')
    sty_lbl = '成长' if style['style'] > 0.3 else ('价值' if style['style'] < -0.3 else '均衡')

    if cap_lbl == '小盘':
        g.mcap_range = (10, 250)
    elif cap_lbl == '大盘':
        g.mcap_range = (80, 800)
    else:
        g.mcap_range = (15, 500)

    g.hot_industries, g.cold_industries = _calc_industry_heat(today)
    top3 = sorted(g.hot_industries.items(), key=lambda x: -x[1])[:3]
    log.info(f"📊 {cap_lbl}({style['cap']:+.2f}) {sty_lbl}({style['style']:+.2f}) "
             f"市值={g.mcap_range} 热门行业:{len(top3)}个")
    g.factor_pool = pd.DataFrame()


# ================================================================
#  09:31 执行
# ================================================================
def daily_open_trade(context):
    curr = get_current_data()

    # 先卖
    sold = []
    for s in list(g.pending_sell):
        if s not in context.portfolio.positions: continue
        pos = context.portfolio.positions[s]
        if pos.closeable_amount > 0:
            order_target(s, 0)
            pnl = (pos.price - pos.avg_cost) / pos.avg_cost * 100
            try: nm = get_security_info(s).display_name
            except: nm = s
            sold.append(f"{nm}{pnl:+.1f}%")
        g.entry.pop(s, None)
    if sold:
        log.info(f"  卖: {' | '.join(sold)}")
    g.pending_sell = []

    if not g.pending_buy: return

    total  = context.portfolio.total_value
    per    = total / g.hold_n
    bought = 0

    for code in g.pending_buy:
        if code in context.portfolio.positions: continue
        try:
            if curr[code].paused: continue
            lp = curr[code].last_price
            hl = curr[code].high_limit
            if hl > 0 and lp >= hl * 0.99: continue  # ★ 涨停附近不买
            prev = g.entry_prev_close.get(code, lp)
            gap  = (lp - prev) / prev if prev > 0 else 0
            if gap > 0.05:
                log.info(f"  {code}跳空{gap*100:.1f}%放弃"); continue
            order_target_value(code, per)
            g.entry[code] = {'price': lp, 'date': context.current_dt, 'high': lp}
            try: nm = get_security_info(code).display_name
            except: nm = code
            sc = g.factor_pool.loc[code, 'score'] if code in g.factor_pool.index else 0
            log.info(f"  买 {nm} 分:{sc:.3f} [{g.regime}]")
            bought += 1
        except Exception as e:
            log.info(f"  买{code}失败:{e}")

    ret = (context.portfolio.total_value - context.portfolio.starting_cash) \
          / context.portfolio.starting_cash * 100
    log.info(f"  ✅ 买:{bought} 持:{len(context.portfolio.positions)}/{g.hold_n} "
             f"收益:{ret:+.2f}% [{g.regime}]")
    g.pending_buy = []


# ================================================================
#  15:30 扫描
# ================================================================
def daily_scan_close(context):
    today  = context.current_dt
    prev   = context.previous_date

    # 大盘趋势过滤
    g.mkt_uptrend = _get_market_trend(today)
    if not g.mkt_uptrend:
        log.info("  ⚠️ 大盘空头, 持仓压至3只")

    # ★ 改进3: 市场情绪过滤 — 大盘今日下跌时不开新仓
    # 逻辑: 大盘跌的日子买入, 隔天大概率还要继续调整
    mkt_today_ret = _get_today_market_ret(today)
    g.mkt_today_positive = mkt_today_ret >= -0.003  # 允许小幅下跌(-0.3%内)
    if not g.mkt_today_positive:
        log.info(f"  ⚠️ 大盘今日{mkt_today_ret*100:.2f}%, 今日不开新仓")

    # 重建因子池
    _build_factor_pool(context, prev, today)
    if g.factor_pool.empty:
        log.info("  ⚠️ 因子池空"); return

    _cache_prices(context, today)

    # ★ 新信息③: 尾盘分钟得分 (14:30-15:00, 判断今日尾盘强弱)
    g.minute_scores = _calc_minute_scores(
        list(g.factor_pool.index[:100]) +
        list(context.portfolio.positions.keys()),
        today
    )

    # 记录昨收
    g.entry_prev_close = {}
    for code in g.factor_pool.index[:60]:
        grp = g.price_cache.get(code)
        if grp is not None and len(grp) > 0:
            g.entry_prev_close[code] = float(grp['close'].iloc[-1])

    # ── 卖出信号 ──────────────────────────────────────────────
    pending_sell = []

    for s, info in list(g.entry.items()):
        if s not in context.portfolio.positions:
            g.entry.pop(s, None); continue

        pos  = context.portfolio.positions[s]
        ep   = info['price']
        if ep <= 0: continue
        pnl  = (pos.price - ep) / ep
        hold = (context.current_dt - info['date']).days
        info['high'] = max(info.get('high', ep), pos.price)
        hpnl = (info['high'] - ep) / ep

        # 止损
        if pnl <= g.stop_loss:
            pending_sell.append(s)
            log.info(f"  [卖]止损 {s} {pnl*100:.1f}%"); continue

        if hold < 3: continue

        # 移动止盈
        if hpnl >= g.trail_trigger:
            dd = (pos.price - info['high']) / info['high']
            if dd <= g.trail_dd:
                pending_sell.append(s)
                log.info(f"  [卖]移止盈 {s} 峰{hpnl*100:.0f}%→{pnl*100:+.1f}%"); continue

        # 因子排名跌出
        if not g.factor_pool.empty and s in g.factor_pool.index:
            rank_pct = g.factor_pool.index.get_loc(s) / len(g.factor_pool)
            if rank_pct > g.rank_thresh:
                pending_sell.append(s)
                log.info(f"  [卖]排名 {s} {rank_pct*100:.0f}%"); continue

        # 破MA20 (用20日均线,比MA5更稳定)
        grp = g.price_cache.get(s)
        if grp is not None and len(grp) >= 22 and hold >= 3 and pnl < 0.10:
            c = grp['close'].values
            ma20t = np.mean(c[-20:])
            ma20p = np.mean(c[-21:-1])
            if c[-1] < ma20t * 0.97 and ma20t < ma20p:
                pending_sell.append(s)
                log.info(f"  [卖]破MA20 {s} {pnl*100:.1f}%"); continue

    g.pending_sell = pending_sell

    # ── 买入信号 ──────────────────────────────────────────────
    max_hold   = g.hold_n if g.mkt_uptrend else 3
    curr_h     = set(context.portfolio.positions.keys())
    eff_hold   = len(curr_h) - len(pending_sell)
    slots      = max_hold - eff_hold

    # 只买因子分前30%
    score_q70  = float(g.factor_pool['score'].quantile(0.70)) \
                 if not g.factor_pool.empty else -999

    pending_buy = []
    # ★ 市场情绪不佳时不开新仓
    allow_new_buy = g.mkt_today_positive if hasattr(g, 'mkt_today_positive') else True
    if slots > 0 and allow_new_buy:
        ic = {}
        for h in curr_h:
            if h in pending_sell: continue
            ind = _get_ind(h)
            ic[ind] = ic.get(ind, 0) + 1

        for code in g.factor_pool.index[:100]:
            if len(pending_buy) >= slots: break
            if code in curr_h: continue
            sc = float(g.factor_pool.loc[code, 'score'])
            if sc < score_q70: break

            ind = _get_ind(code)
            if ic.get(ind, 0) >= 3: continue

            # ★ 强化入场确认 (四重过滤, 直接针对胜率)
            if not _entry_confirm(code):
                continue

            pending_buy.append(code)
            ic[ind] = ic.get(ind, 0) + 1

        if not pending_buy and slots <= 0:
            _try_replace(context, curr_h, score_q70)
    elif slots > 0 and not allow_new_buy:
        log.info(f"  今日情绪过滤, 不买入")

    g.pending_buy = pending_buy
    log.info(f"  [扫描] 卖:{len(g.pending_sell)} 买:{len(g.pending_buy)} "
             f"池:{len(g.factor_pool)} 权重:{sorted(g.factor_weights.items(), key=lambda x:-x[1])[:3]}")


# ================================================================
#  因子池构建 (IC驱动权重)
# ================================================================
def _build_factor_pool(context, date, today):
    all_sec = get_all_securities(types=['stock'], date=date)
    curr    = get_current_data()
    cutoff  = pd.Timestamp(date) - pd.DateOffset(days=180)

    pool = []
    for s in all_sec.index:
        try:
            if curr[s].is_st or curr[s].paused: continue
            if s[:3] == '688' or s[0] in ('4', '8'): continue
            if pd.Timestamp(all_sec.loc[s, 'start_date']) > cutoff: continue
            pool.append(s)
        except: continue

    if not pool: return

    # 基本面
    try:
        q = query(
            valuation.code, valuation.circulating_market_cap,
            valuation.pb_ratio, valuation.pe_ratio,
            indicator.roe, indicator.inc_net_profit_year_on_year,
            indicator.inc_revenue_year_on_year,
        ).filter(
            valuation.code.in_(pool),
            valuation.circulating_market_cap.between(g.mcap_range[0], g.mcap_range[1]),
            valuation.pb_ratio > 0,
            valuation.pe_ratio > 0,
            indicator.roe > -30,
        )
        df = get_fundamentals(q, date=date)
        if df.empty: return
        df.columns = ['code','mcap','pb','pe','roe','profit_g','rev_g']
        df = df.set_index('code')
    except Exception as e:
        log.info(f"  基本面异常:{e}"); return

    # 负债率 (fin_risk 主因子, 必须拿)
    try:
        q2 = query(balance.code, balance.total_liability, balance.total_assets
                   ).filter(balance.code.in_(df.index.tolist()))
        bd = get_fundamentals(q2, date=date)
        if not bd.empty:
            bd = bd.set_index('code')
            df['debt_ratio'] = (
                bd['total_liability'] / bd['total_assets'].replace(0, np.nan)
            ).reindex(df.index).fillna(0.5)
    except:
        df['debt_ratio'] = 0.5

    # 流动性
    try:
        pm = get_price(df.index.tolist(), count=10, end_date=today,
                       fields=['money'], panel=False)
        if not pm.empty:
            avg_m = pm.groupby('code')['money'].mean()
            df = df[df.index.isin(avg_m[avg_m > g.min_money].index)]
    except: pass

    if len(df) < 20: return

    # 动量 (三段: 短/中/长)
    try:
        ph = get_price(df.index.tolist()[:600], count=132, end_date=today,
                       fields=['close'], panel=False)
        ms, mm, ml = {}, {}, {}
        for code, grp in ph.groupby('code'):
            grp = grp.sort_index()
            c   = grp['close'].values
            if len(c) >= 11:  ms[code] = c[-1] / c[-11] - 1
            if len(c) >= 21:  mm[code] = c[-1] / c[-21] - 1
            if len(c) >= 110: ml[code] = c[-22] / c[0] - 1
        df['mom_s'] = pd.Series(ms).reindex(df.index).fillna(0)
        df['mom_m'] = pd.Series(mm).reindex(df.index).fillna(0)
        df['mom_l'] = pd.Series(ml).reindex(df.index).fillna(0)
        df['momentum'] = df['mom_s']*0.5 + df['mom_m']*0.3 + df['mom_l']*0.2
    except:
        df['momentum'] = 0
        df['mom_s']    = 0
        df['mom_m']    = 0

    df['size'] = df['mcap']
    df = df.fillna(0)

    # ── 因子评分: IC权重驱动 ─────────────────────────────────
    def zscore(s):
        s  = pd.to_numeric(s, errors='coerce').fillna(0)
        m  = s.mean(); sd = s.std()
        return (s - m) / (sd + 1e-8)

    w = g.factor_weights
    df['score'] = 0.0
    if w.get('quality',  0) > 0:
        df['score'] += zscore(df['roe'])                        * w['quality']
    if w.get('fin_risk', 0) > 0:
        # ★ fin_risk = 低负债 (当前唯一有效因子, 权重45%)
        df['score'] += zscore(-df['debt_ratio'])                * w['fin_risk']
    if w.get('size',     0) > 0:
        df['score'] += zscore(-df['size'])                      * w['size']
    if w.get('value',    0) > 0:
        df['score'] += zscore(1/df['pb'].clip(0.1))             * w['value'] * 0.5
        df['score'] += zscore(1/df['pe'].clip(0.1))             * w['value'] * 0.5
    if w.get('growth',   0) > 0:
        df['score'] += zscore(df['profit_g'])                   * w['growth']
    if w.get('momentum', 0) > 0:
        df['score'] += zscore(df['momentum'])                   * w['momentum']

    # ★ 近期强势独立加分 (不受IC权重影响, 始终生效)
    q80s = df['mom_s'].quantile(0.80) if 'mom_s' in df.columns else 0
    q80m = df['mom_m'].quantile(0.80) if 'mom_m' in df.columns else 0
    top_s = df.get('mom_s', pd.Series(0, index=df.index)) >= q80s
    top_m = df.get('mom_m', pd.Series(0, index=df.index)) >= q80m
    df.loc[top_s, 'score']           += 0.3
    df.loc[top_m, 'score']           += 0.2
    df.loc[top_s & top_m, 'score']   += 0.2
    df.loc[df['profit_g'] > 30, 'score'] += 0.2

    # 行业热度加成
    _warmup_ind_cache(df.index.tolist(), str(date))
    ind_map = _get_ind_map(df.index.tolist(), str(date))
    for code in df.index:
        ind  = ind_map.get(code, '')
        heat = g.hot_industries.get(ind, 0)
        if ind in g.cold_industries:
            df.loc[code, 'score'] -= 0.3
        elif heat > 0:
            df.loc[code, 'score'] += min(0.5, heat * 2)

    # ══════════════════════════════════════════════════════════
    # ★ 新信息①: 主力资金净流入加分
    # ══════════════════════════════════════════════════════════
    money_scores = _calc_money_flow_scores(df.index.tolist(), today)
    for code, ms in money_scores.items():
        if code in df.index:
            df.loc[code, 'score'] += ms

    # ══════════════════════════════════════════════════════════
    # ★ 新信息②: 财报窗口期业绩加速加分
    # ══════════════════════════════════════════════════════════
    report_scores = _calc_report_window_scores(df.index.tolist(), date, today)
    g.report_window = report_scores.get('_in_window', False)
    for code, rs in report_scores.items():
        if code in df.index and isinstance(rs, float):
            df.loc[code, 'score'] += rs

    # ══════════════════════════════════════════════════════════
    # ★ 新信息③: 尾盘分钟趋势加分 (从缓存取, 由daily_scan_close更新)
    # ══════════════════════════════════════════════════════════
    for code, ms in g.minute_scores.items():
        if code in df.index:
            df.loc[code, 'score'] += ms

    n_money  = sum(1 for v in money_scores.values() if isinstance(v,float) and v > 0)
    n_report = sum(1 for k,v in report_scores.items() if k!='_in_window' and isinstance(v,float) and v > 0)
    n_minute = sum(1 for v in g.minute_scores.values() if v > 0)
    log.info(f"  新信息: 资金流入{n_money}只+{' 财报窗口期' if g.report_window else ''}"
             f"业绩加速{n_report}只 尾盘强势{n_minute}只")

    g.factor_pool = df.sort_values('score', ascending=False)
    log.info(f"  因子池:{len(df)} [fin_risk:{w.get('fin_risk',0)*100:.0f}% "
             f"size:{w.get('size',0)*100:.0f}% mom:{w.get('momentum',0)*100:.0f}%]")


# ================================================================
#  IC 计算
# ================================================================
def _calc_ic_history(start_str, end_str, forward_n=20, sample_n=300):
    tdays = get_trade_days(start_date=start_str, end_date=end_str)
    sdays = tdays[::21]
    factors    = ['roe', 'pb', 'pe', 'momentum', 'size', 'debt_ratio']
    ic_records = []
    for td in sdays:
        ds  = str(td)
        fds = get_trade_days(start_date=td, count=forward_n+2)
        if len(fds) < forward_n+1: continue
        row = _one_period_ic(ds, str(fds[forward_n]), sample_n, factors)
        if row: ic_records.append(row)
    if not ic_records: return None
    return pd.DataFrame(ic_records).set_index('date')


def _one_period_ic(date_str, future_str, sample_n, factors):
    try:
        q = query(valuation.code, valuation.circulating_market_cap,
                  valuation.pb_ratio, valuation.pe_ratio, indicator.roe,
                  ).filter(valuation.pb_ratio > 0, valuation.pe_ratio > 0)
        df = get_fundamentals(q, date=date_str)
        if df.empty: return None
        df.columns = ['code','mcap','pb','pe','roe']
        df = df.set_index('code')
    except: return None

    if len(df) > sample_n: df = df.sample(n=sample_n, random_state=42)
    codes = df.index.tolist()

    try:
        q2 = query(balance.code, balance.total_liability,
                   balance.total_assets).filter(balance.code.in_(codes))
        bd = get_fundamentals(q2, date=date_str)
        if not bd.empty:
            bd = bd.set_index('code')
            df['debt_ratio'] = (bd['total_liability'] /
                                bd['total_assets'].replace(0, np.nan)
                                ).reindex(df.index).fillna(0.5)
    except: df['debt_ratio'] = 0.5

    try:
        ph = get_price(codes, count=132, end_date=date_str,
                       fields=['close'], panel=False)
        mom = {}
        for code, grp in ph.groupby('code'):
            grp = grp.sort_index()
            if len(grp) >= 110:
                mom[code] = grp['close'].iloc[-22] / grp['close'].iloc[0] - 1
        df['momentum'] = pd.Series(mom)
    except: df['momentum'] = np.nan

    df['size'] = -np.log(df['mcap'].clip(0.01) + 1)

    try:
        p1 = get_price(codes, count=1, end_date=date_str,  fields=['close'], panel=False)
        p2 = get_price(codes, count=1, end_date=future_str, fields=['close'], panel=False)
        c1 = p1.groupby('code')['close'].last()
        c2 = p2.groupby('code')['close'].last()
        df['future_ret'] = (c2/c1-1).reindex(df.index)
    except: return None

    df = df.dropna(subset=['future_ret'])
    if len(df) < 20: return None

    record = {'date': pd.Timestamp(date_str)}
    for f in factors:
        if f not in df.columns: continue
        try:
            sf = df[f].dropna()
            sr = df.loc[sf.index, 'future_ret'].dropna()
            cm = sf.index.intersection(sr.index)
            if len(cm) < 15: continue
            ic, _ = stats.spearmanr(sf[cm], sr[cm])
            record[f'IC_{f}'] = ic
        except: record[f'IC_{f}'] = np.nan
    return record


def _analyze_ic(ic_df, window=6):
    results = {}
    for col in [c for c in ic_df.columns if c.startswith('IC_')]:
        fname  = col[3:]
        series = ic_df[col].dropna()
        if len(series) < window: continue
        rm    = series.rolling(window).mean()
        rs    = series.rolling(window).std()
        icir  = (rm / (rs + 1e-8)).fillna(0)
        results[fname] = {
            'latest_ic':   float(series.iloc[-1]),
            'latest_icir': float(icir.iloc[-1]),
            'win_rate':    float((series > 0).mean()),
        }
    return pd.DataFrame(results).T if results else pd.DataFrame()


# ================================================================
#  辅助函数
# ================================================================
# ================================================================
#  辅助: 强化入场确认 (四重过滤)
# ================================================================
def _entry_confirm(code):
    """
    四重入场过滤, 直接针对胜率:
    ① 站上MA10 且 MA10向上         → 趋势确认
    ② 今日收盘 > 今日开盘 (阳线)   → 当日买盘主导
    ③ 量比 > 1.5                   → 有效放量, 非无量反弹
    ④ 近5日涨幅 > 0                → 短期动量为正
    ⑤ 近20日涨幅 < 25%             → 非超买状态
    缺数据时默认放行(不误杀)
    """
    grp = g.price_cache.get(code)
    if grp is None or len(grp) < 11:
        return True  # 无数据不阻拦

    c = grp['close'].values
    v = grp['volume'].values

    # ① MA10确认
    ma10t = np.mean(c[-10:])
    ma10p = np.mean(c[-11:-1])
    if c[-1] < ma10t:
        return False
    if ma10t < ma10p * 0.996:   # MA10下降中
        return False

    # ② 阳线确认
    if 'open' in grp.columns:
        o = grp['open'].values
        if c[-1] <= o[-1]:
            return False
    else:
        if len(c) >= 2 and c[-1] <= c[-2]:
            return False

    # ③ 量比 > 1.5
    if len(v) >= 11:
        avg_v = np.mean(v[-11:-1])
        if avg_v > 0 and v[-1] / avg_v < 1.5:
            return False

    # ④ 近5日涨幅为正
    if len(c) >= 6:
        ret5 = c[-1] / c[-6] - 1
        if ret5 <= 0:
            return False

    # ⑤ 近20日非超买 (涨幅<25%)
    if len(c) >= 21:
        ret20 = c[-1] / c[-21] - 1
        if ret20 > 0.25:
            return False

    return True


# ================================================================
#  辅助: 获取大盘今日涨跌幅
# ================================================================
def _get_today_market_ret(today):
    """获取沪深300今日涨跌幅"""
    try:
        p = get_price('000300.XSHG', count=2, end_date=today,
                      fields=['close'], panel=False)
        if len(p) >= 2:
            return p['close'].iloc[-1] / p['close'].iloc[-2] - 1
    except:
        pass
    return 0.0


# ================================================================
#  新信息①: 主力资金净流入加分
# ================================================================
def _calc_money_flow_scores(codes, today):
    """
    主力净流入率 = 近5日主力净额 / 近5日总成交额
    > 5%  → +0.5分 (强势主力进场)
    1%~5% → +0.25分 (温和主力流入)
    < -3% → -0.3分 (主力明显出逃)

    JoinQuant get_money_flow 返回字段:
      change_pct, net_amount_main, net_pct_main,
      net_amount_xl, net_pct_xl (超大单)
    """
    scores = {}
    if not codes:
        return scores

    try:
        # 取近5个交易日资金流向
        trade_days = get_trade_days(end_date=today, count=6)
        if len(trade_days) < 2:
            return scores
        start_d = str(trade_days[0])
        end_d   = str(trade_days[-1])

        # 分批查询避免超时
        for i in range(0, len(codes), 100):
            batch = codes[i:i+100]
            try:
                mf = get_money_flow(batch, start_date=start_d, end_date=end_d)
                if mf is None or mf.empty:
                    continue
                # 计算5日累计主力净流入比率
                agg = mf.groupby('code').agg(
                    net_main=('net_pct_main', 'mean'),
                    net_xl=('net_pct_xl', 'mean')
                )
                for code, row in agg.iterrows():
                    net = float(row['net_main'])    # 主力净流入率(%)
                    xl  = float(row['net_xl'])      # 超大单净流入率(%)
                    # 主力 + 超大单联合判断
                    combined = net * 0.6 + xl * 0.4
                    if combined > 5:
                        scores[code] = 0.5
                    elif combined > 1:
                        scores[code] = 0.25
                    elif combined < -3:
                        scores[code] = -0.3
                    else:
                        scores[code] = 0.0
            except:
                continue
    except Exception as e:
        log.info(f"  资金流向异常:{e}")

    return scores


# ================================================================
#  新信息②: 财报窗口期业绩加速加分
# ================================================================
def _calc_report_window_scores(codes, date, today):
    """
    财报披露窗口期:
      Q1财报: 4月1日~4月30日  (披露上年Q4+全年)
      Q2财报: 7月1日~8月31日  (披露Q2中报)
      Q3财报: 10月1日~10月31日(披露Q3)
      年报:   3月1日~4月30日

    窗口期内找净利润增速>50%的票加分:
      增速 > 100% → +0.5分
      增速 50~100% → +0.3分
      增速 20~50%  → +0.15分
      增速 < -20%  → -0.2分 (业绩变脸)
    """
    scores = {'_in_window': False}
    if not codes:
        return scores

    # 判断窗口期
    month = today.month
    in_window = month in [3, 4, 7, 8, 10]
    scores['_in_window'] = in_window

    if not in_window:
        return scores

    try:
        q = query(
            indicator.code,
            indicator.inc_net_profit_year_on_year,   # 净利润同比增速
            indicator.inc_net_profit_annual,         # 净利润环比增速
        ).filter(
            indicator.code.in_(codes[:500])
        )
        df = get_fundamentals(q, date=date)
        if df.empty:
            return scores

        for _, row in df.iterrows():
            code = row['code']
            yoy  = row.get('inc_net_profit_year_on_year', 0) or 0  # 同比
            try:
                yoy = float(yoy)
            except:
                yoy = 0

            if yoy > 100:
                scores[code] = 0.5
            elif yoy > 50:
                scores[code] = 0.3
            elif yoy > 20:
                scores[code] = 0.15
            elif yoy < -20:
                scores[code] = -0.2
    except Exception as e:
        log.info(f"  财报窗口异常:{e}")

    return scores


# ================================================================
#  新信息③: 尾盘分钟趋势加分
# ================================================================
def _calc_minute_scores(codes, today):
    """
    扫描 14:30~15:00 的30分钟分钟线，判断尾盘资金方向

    强势尾盘 (尾盘涨 > 0.5% + 尾盘量 > 全天均量):
      → +0.4分 (次日高开概率高)

    弱势尾盘 (尾盘跌 < -0.5% + 尾盘量放大):
      → -0.3分 (尾盘主力出货, 次日低开)

    平稳:
      → 0分

    注意: JoinQuant日线回测中分钟数据可用
    时间窗口: 在15:30扫描时取当日14:30之后的数据
    """
    scores = {}
    if not codes:
        return scores

    codes = list(set(codes))[:150]

    try:
        # 取当日分钟数据
        # end_date=today 在15:30时能取到当日14:57之前的分钟
        mp = get_price(
            codes,
            end_date=today,
            frequency='minute',
            count=35,           # 取35根1分钟线，覆盖14:25~15:00
            fields=['close', 'volume'],
            panel=False
        )
        if mp is None or mp.empty:
            return scores

        mp = mp.reset_index()
        time_col = mp.columns[0]
        mp[time_col] = pd.to_datetime(mp[time_col])

        # 只取 14:30 之后的数据 (尾盘30分钟)
        tail = mp[mp[time_col].dt.hour >= 14]
        tail = tail[tail[time_col].dt.minute >= 30]

        if tail.empty:
            return scores

        for code, grp in tail.groupby('code'):
            grp = grp.sort_values(time_col)
            if len(grp) < 5:
                continue

            c = grp['close'].values
            v = grp['volume'].values

            # 尾盘涨幅
            tail_ret = (c[-1] - c[0]) / c[0] if c[0] > 0 else 0

            # 尾盘量比 (和当日前段对比)
            # 用全天数据的均量作参照
            all_day = mp[mp['code'] == code] if 'code' in mp.columns else grp
            avg_min_vol = all_day['volume'].mean() if len(all_day) > 0 else v.mean()
            tail_avg_vol = v.mean()
            vol_ratio = tail_avg_vol / avg_min_vol if avg_min_vol > 0 else 1

            if tail_ret > 0.005 and vol_ratio > 1.2:
                # 尾盘强势: 资金在最后30分钟主动买入
                scores[code] = 0.4
            elif tail_ret < -0.005 and vol_ratio > 1.2:
                # 尾盘弱势: 有人在尾盘出货
                scores[code] = -0.3
            elif tail_ret > 0.003:
                scores[code] = 0.2
            else:
                scores[code] = 0.0

    except Exception as e:
        log.info(f"  尾盘分钟异常:{e}")

    return scores


def _get_market_trend(today):
    try:
        p = get_price('000300.XSHG', count=25, end_date=today,
                      fields=['close'], panel=False)
        if len(p) < 22: return True
        c = p['close'].values
        ma20t = np.mean(c[-20:])
        ma20p = np.mean(c[-21:-1])
        return bool(c[-1] > ma20t and ma20t >= ma20p * 0.997)
    except: return True


def _calc_style_scores(today):
    try:
        codes = ['000300.XSHG','000852.XSHG','399006.XSHE','000016.XSHG']
        raw   = get_price(codes, count=25, end_date=today,
                          fields=['close'], panel=False)
        raw   = raw.reset_index()
        dc    = raw.columns[0]
        raw[dc] = pd.to_datetime(raw[dc]).dt.normalize()
        wide  = raw.pivot_table(index=dc, columns='code',
                                values='close', aggfunc='last').ffill()
        ret   = wide.pct_change(20).dropna(how='all')
        if len(ret) == 0: return {'cap':0.0,'style':0.0}
        latest  = ret.iloc[-1]
        cap_d   = latest.get('000852.XSHG',0) - latest.get('000300.XSHG',0)
        sty_d   = latest.get('399006.XSHE',0) - latest.get('000016.XSHG',0)
        cap_std = (ret['000852.XSHG']-ret['000300.XSHG']).std()+1e-8
        sty_std = (ret['399006.XSHE']-ret['000016.XSHG']).std()+1e-8
        return {'cap':round(cap_d/cap_std,3), 'style':round(sty_d/sty_std,3)}
    except: return {'cap':0.0,'style':0.0}


def _calc_industry_heat(today):
    hot, cold = {}, set()
    try:
        inds  = get_industries(name='sw_l1')
        heats = {}
        for code in inds.index:
            try:
                stocks = get_industry_stocks(code)
                sample = stocks[::max(1,len(stocks)//15)][:15]
                p = get_price(sample, count=22, end_date=today,
                              fields=['close'], panel=False)
                if p is None or p.empty: continue
                r5  = p.groupby('code')['close'].apply(
                    lambda x: x.iloc[-1]/x.iloc[-6]-1 if len(x)>=6 else 0).mean()
                r10 = p.groupby('code')['close'].apply(
                    lambda x: x.iloc[-1]/x.iloc[0]-1 if len(x)>=2 else 0).mean()
                heats[code] = r5*0.6 + r10*0.4
            except: continue
        if not heats: return {}, set()
        sh = sorted(heats.items(), key=lambda x:-x[1])
        for c,h in sh[:10]: hot[c] = max(0,h)
        cold = set(c for c,_ in sh[-5:])
    except: pass
    return hot, cold


def _cache_prices(context, today):
    g.price_cache = {}
    targets = list(g.factor_pool.index[:80])
    for s in context.portfolio.positions:
        if s not in targets: targets.append(s)
    if not targets: return
    try:
        ap = get_price(targets, count=25, end_date=today,
                       fields=['open','close','volume'], panel=False)
        if ap is not None and not ap.empty:
            for code, grp in ap.groupby('code'):
                if len(grp) >= 5:
                    g.price_cache[code] = grp.sort_index()
    except: pass


_ind_cache = {}

def _warmup_ind_cache(codes, date):
    miss = [c for c in codes if c not in _ind_cache]
    if not miss: return
    for i in range(0, len(miss), 200):
        batch = miss[i:i+200]
        try:
            result = get_industry(batch, date=date)
            for code, info in result.items():
                sw = info.get('sw_l1', {})
                _ind_cache[code] = sw.get('industry_code','') if sw else ''
        except:
            for code in batch: _ind_cache[code] = ''
    for code in miss:
        if code not in _ind_cache: _ind_cache[code] = ''

def _get_ind_map(codes, date=None):
    if date: _warmup_ind_cache(codes, date)
    return {c: _ind_cache.get(c,'') for c in codes}

def _get_ind(code):
    return _ind_cache.get(code, '')


def _try_replace(context, curr_h, score_threshold):
    if g.factor_pool.empty: return
    worst, ws = None, 999
    for s in curr_h:
        if s in g.factor_pool.index:
            sc = float(g.factor_pool.loc[s, 'score'])
            if sc < ws: ws = sc; worst = s
    if worst is None: return
    for code in g.factor_pool.index[:30]:
        if code in curr_h: continue
        cs = float(g.factor_pool.loc[code, 'score'])
        if cs - ws < 0.18: break
        g.pending_sell.append(worst)
        g.pending_buy.append(code)
        log.info(f"  [替换]{worst}({ws:.2f})→{code}({cs:.2f})")
        break


def handle_data(context, data):
    pass