# -*- coding: utf-8 -*-
from core.indicators import sma, prev_high, prev_low
from ._common import SHORT, last_done, point

META = dict(
    id="s07_h_breakout", name="小时线突破", timeframe="1h", family="趋势", verdict="待验证", order=7,
    summary="日内版的趋势突破：小时收盘创新高且在均线之上就买，跌破近期低点就卖（做空相反）。",
    logic=[("方向", "小时收盘价高于 200 小时均线做多（打开做空后：低于则做空）"),
           ("入场", "小时收盘价创 N 小时新高，下一小时开盘买入（做空：创 N 小时新低）"),
           ("止损", "没有单独的止损价，出场规则本身就是止损"), ("仓位", "满仓，不加杠杆"),
           ("出场", "小时收盘价跌破 N/2 小时新低（空单：升破 N/2 小时新高），下一小时开盘平仓")],
    params=[dict(key="entry", name="突破小时数", value=48, min=6, max=720, desc="12 最接近日内；336（14 天）最稳，但已经等同日线趋势"),
            dict(key="exit", name="离场小时数", value=24, min=3, max=360, desc="通常取突破小时数的一半"),
            dict(key="ma", name="方向均线小时数", value=200, min=1, max=1000, desc="填 1 表示不过滤"), SHORT],
    finding="第 6 课：73 条日内规则里只有突破类在 2024–2026 年扣费后还赚钱（12 条里 10 条）。但参数之间差别很大：12 小时 +69%，24 小时 −12%，48 小时 +20%，336 小时 +81%。手续费吃掉约一半利润。",
)


def build(B, P):
    c, h, l, n = B["c"], B["h"], B["l"], len(B["c"])
    N, X, sh, use_ma = int(P["entry"]), int(P["exit"]), P["short"] >= 1, P["ma"] > 1
    ma = sma(c, int(P["ma"])) if use_ma else [None] * n
    hiN, loN, hiX, loX = prev_high(h, N), prev_low(l, N), prev_high(h, X), prev_low(l, X)
    ok = [hiN[i] is not None and (ma[i] is not None or not use_ma) for i in range(n)]
    k = last_done(B)
    up = max(max(h[k - N + 1:k + 1]), ma[k] or 0)
    dn = min(min(l[k - N + 1:k + 1]), ma[k] or float("inf"))
    return dict(enter=[ok[i] and c[i] > hiN[i] and (not use_ma or c[i] > ma[i]) for i in range(n)],
                exit=[loX[i] is not None and c[i] < loX[i] for i in range(n)],
                enter_s=[ok[i] and c[i] < loN[i] and (not use_ma or c[i] < ma[i]) for i in range(n)] if sh else None,
                exit_s=[hiX[i] is not None and c[i] > hiX[i] for i in range(n)] if sh else None,
                sizing="full", warmup=max(int(P["ma"]), N) + 1, exit_name="收盘破%d小时高低" % X,
                points=dict(long=point(up, "小时收盘价高于", stop=min(l[k - X + 1:k + 1]), size=1.0, note="止损价是离场线，会随行情移动"),
                            short=point(dn, "小时收盘价低于", stop=max(h[k - X + 1:k + 1]), size=1.0, note="止损价是离场线，会随行情移动") if sh else None),
                levels=[("方向均线", ma[k]), ("%d 小时最高 / 最低" % N, "%.2f / %.2f" % (max(h[k - N + 1:k + 1]), min(l[k - N + 1:k + 1]))),
                        ("%d 小时最高 / 最低（离场线）" % X, "%.2f / %.2f" % (max(h[k - X + 1:k + 1]), min(l[k - X + 1:k + 1])))])
