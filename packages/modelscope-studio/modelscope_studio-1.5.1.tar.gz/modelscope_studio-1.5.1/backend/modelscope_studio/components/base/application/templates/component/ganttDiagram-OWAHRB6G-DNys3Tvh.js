import { aR as Ge, aS as Mn, aT as Qe, aU as Je, aV as Ke, aW as re, aX as Sn, _ as f, g as Fn, s as Un, q as En, p as In, a as An, b as Ln, c as _t, d as qt, e as Yn, l as Qt, k as Wn, j as On, y as Nn, u as Hn } from "./mermaid.core-VANNf1YM.js";
import { e as Vn, g as Pn, H as tt, I as Rn, J as zn } from "./Index-HF_NH3zS.js";
import { b as Bn, t as Ae, c as qn, a as Zn, l as Xn } from "./linear-C_DknxDj.js";
import { i as jn } from "./init-DjUOC4st.js";
function Gn(t, e) {
  let n;
  if (e === void 0)
    for (const r of t)
      r != null && (n < r || n === void 0 && r >= r) && (n = r);
  else {
    let r = -1;
    for (let i of t)
      (i = e(i, ++r, t)) != null && (n < i || n === void 0 && i >= i) && (n = i);
  }
  return n;
}
function Qn(t, e) {
  let n;
  if (e === void 0)
    for (const r of t)
      r != null && (n > r || n === void 0 && r >= r) && (n = r);
  else {
    let r = -1;
    for (let i of t)
      (i = e(i, ++r, t)) != null && (n > i || n === void 0 && i >= i) && (n = i);
  }
  return n;
}
function Jn(t) {
  return t;
}
var Xt = 1, ie = 2, me = 3, Zt = 4, Le = 1e-6;
function Kn(t) {
  return "translate(" + t + ",0)";
}
function $n(t) {
  return "translate(0," + t + ")";
}
function tr(t) {
  return (e) => +t(e);
}
function er(t, e) {
  return e = Math.max(0, t.bandwidth() - e * 2) / 2, t.round() && (e = Math.round(e)), (n) => +t(n) + e;
}
function nr() {
  return !this.__axis;
}
function $e(t, e) {
  var n = [], r = null, i = null, a = 6, s = 6, D = 3, S = typeof window < "u" && window.devicePixelRatio > 1 ? 0 : 0.5, k = t === Xt || t === Zt ? -1 : 1, p = t === Zt || t === ie ? "x" : "y", A = t === Xt || t === me ? Kn : $n;
  function x(y) {
    var R = r ?? (e.ticks ? e.ticks.apply(e, n) : e.domain()), I = i ?? (e.tickFormat ? e.tickFormat.apply(e, n) : Jn), et = Math.max(a, 0) + D, rt = e.range(), nt = +rt[0] + S, Z = +rt[rt.length - 1] + S, X = (e.bandwidth ? er : tr)(e.copy(), S), $ = y.selection ? y.selection() : y, w = $.selectAll(".domain").data([null]), N = $.selectAll(".tick").data(R, e).order(), C = N.exit(), U = N.enter().append("g").attr("class", "tick"), _ = N.select("line"), M = N.select("text");
    w = w.merge(w.enter().insert("path", ".tick").attr("class", "domain").attr("stroke", "currentColor")), N = N.merge(U), _ = _.merge(U.append("line").attr("stroke", "currentColor").attr(p + "2", k * a)), M = M.merge(U.append("text").attr("fill", "currentColor").attr(p, k * et).attr("dy", t === Xt ? "0em" : t === me ? "0.71em" : "0.32em")), y !== $ && (w = w.transition(y), N = N.transition(y), _ = _.transition(y), M = M.transition(y), C = C.transition(y).attr("opacity", Le).attr("transform", function(b) {
      return isFinite(b = X(b)) ? A(b + S) : this.getAttribute("transform");
    }), U.attr("opacity", Le).attr("transform", function(b) {
      var L = this.parentNode.__axis;
      return A((L && isFinite(L = L(b)) ? L : X(b)) + S);
    })), C.remove(), w.attr("d", t === Zt || t === ie ? s ? "M" + k * s + "," + nt + "H" + S + "V" + Z + "H" + k * s : "M" + S + "," + nt + "V" + Z : s ? "M" + nt + "," + k * s + "V" + S + "H" + Z + "V" + k * s : "M" + nt + "," + S + "H" + Z), N.attr("opacity", 1).attr("transform", function(b) {
      return A(X(b) + S);
    }), _.attr(p + "2", k * a), M.attr(p, k * et).text(I), $.filter(nr).attr("fill", "none").attr("font-size", 10).attr("font-family", "sans-serif").attr("text-anchor", t === ie ? "start" : t === Zt ? "end" : "middle"), $.each(function() {
      this.__axis = X;
    });
  }
  return x.scale = function(y) {
    return arguments.length ? (e = y, x) : e;
  }, x.ticks = function() {
    return n = Array.from(arguments), x;
  }, x.tickArguments = function(y) {
    return arguments.length ? (n = y == null ? [] : Array.from(y), x) : n.slice();
  }, x.tickValues = function(y) {
    return arguments.length ? (r = y == null ? null : Array.from(y), x) : r && r.slice();
  }, x.tickFormat = function(y) {
    return arguments.length ? (i = y, x) : i;
  }, x.tickSize = function(y) {
    return arguments.length ? (a = s = +y, x) : a;
  }, x.tickSizeInner = function(y) {
    return arguments.length ? (a = +y, x) : a;
  }, x.tickSizeOuter = function(y) {
    return arguments.length ? (s = +y, x) : s;
  }, x.tickPadding = function(y) {
    return arguments.length ? (D = +y, x) : D;
  }, x.offset = function(y) {
    return arguments.length ? (S = +y, x) : S;
  }, x;
}
function rr(t) {
  return $e(Xt, t);
}
function ir(t) {
  return $e(me, t);
}
const ar = Math.PI / 180, sr = 180 / Math.PI, Jt = 18, tn = 0.96422, en = 1, nn = 0.82521, rn = 4 / 29, Mt = 6 / 29, an = 3 * Mt * Mt, or = Mt * Mt * Mt;
function sn(t) {
  if (t instanceof lt) return new lt(t.l, t.a, t.b, t.opacity);
  if (t instanceof dt) return on(t);
  t instanceof Ge || (t = Mn(t));
  var e = ce(t.r), n = ce(t.g), r = ce(t.b), i = ae((0.2225045 * e + 0.7168786 * n + 0.0606169 * r) / en), a, s;
  return e === n && n === r ? a = s = i : (a = ae((0.4360747 * e + 0.3850649 * n + 0.1430804 * r) / tn), s = ae((0.0139322 * e + 0.0971045 * n + 0.7141733 * r) / nn)), new lt(116 * i - 16, 500 * (a - i), 200 * (i - s), t.opacity);
}
function cr(t, e, n, r) {
  return arguments.length === 1 ? sn(t) : new lt(t, e, n, r ?? 1);
}
function lt(t, e, n, r) {
  this.l = +t, this.a = +e, this.b = +n, this.opacity = +r;
}
Qe(lt, cr, Je(Ke, {
  brighter(t) {
    return new lt(this.l + Jt * (t ?? 1), this.a, this.b, this.opacity);
  },
  darker(t) {
    return new lt(this.l - Jt * (t ?? 1), this.a, this.b, this.opacity);
  },
  rgb() {
    var t = (this.l + 16) / 116, e = isNaN(this.a) ? t : t + this.a / 500, n = isNaN(this.b) ? t : t - this.b / 200;
    return e = tn * se(e), t = en * se(t), n = nn * se(n), new Ge(oe(3.1338561 * e - 1.6168667 * t - 0.4906146 * n), oe(-0.9787684 * e + 1.9161415 * t + 0.033454 * n), oe(0.0719453 * e - 0.2289914 * t + 1.4052427 * n), this.opacity);
  }
}));
function ae(t) {
  return t > or ? Math.pow(t, 1 / 3) : t / an + rn;
}
function se(t) {
  return t > Mt ? t * t * t : an * (t - rn);
}
function oe(t) {
  return 255 * (t <= 31308e-7 ? 12.92 * t : 1.055 * Math.pow(t, 1 / 2.4) - 0.055);
}
function ce(t) {
  return (t /= 255) <= 0.04045 ? t / 12.92 : Math.pow((t + 0.055) / 1.055, 2.4);
}
function lr(t) {
  if (t instanceof dt) return new dt(t.h, t.c, t.l, t.opacity);
  if (t instanceof lt || (t = sn(t)), t.a === 0 && t.b === 0) return new dt(NaN, 0 < t.l && t.l < 100 ? 0 : NaN, t.l, t.opacity);
  var e = Math.atan2(t.b, t.a) * sr;
  return new dt(e < 0 ? e + 360 : e, Math.sqrt(t.a * t.a + t.b * t.b), t.l, t.opacity);
}
function ge(t, e, n, r) {
  return arguments.length === 1 ? lr(t) : new dt(t, e, n, r ?? 1);
}
function dt(t, e, n, r) {
  this.h = +t, this.c = +e, this.l = +n, this.opacity = +r;
}
function on(t) {
  if (isNaN(t.h)) return new lt(t.l, 0, 0, t.opacity);
  var e = t.h * ar;
  return new lt(t.l, Math.cos(e) * t.c, Math.sin(e) * t.c, t.opacity);
}
Qe(dt, ge, Je(Ke, {
  brighter(t) {
    return new dt(this.h, this.c, this.l + Jt * (t ?? 1), this.opacity);
  },
  darker(t) {
    return new dt(this.h, this.c, this.l - Jt * (t ?? 1), this.opacity);
  },
  rgb() {
    return on(this).rgb();
  }
}));
function ur(t) {
  return function(e, n) {
    var r = t((e = ge(e)).h, (n = ge(n)).h), i = re(e.c, n.c), a = re(e.l, n.l), s = re(e.opacity, n.opacity);
    return function(D) {
      return e.h = r(D), e.c = i(D), e.l = a(D), e.opacity = s(D), e + "";
    };
  };
}
const fr = ur(Sn);
function hr(t, e) {
  t = t.slice();
  var n = 0, r = t.length - 1, i = t[n], a = t[r], s;
  return a < i && (s = n, n = r, r = s, s = i, i = a, a = s), t[n] = e.floor(i), t[r] = e.ceil(a), t;
}
const le = /* @__PURE__ */ new Date(), ue = /* @__PURE__ */ new Date();
function G(t, e, n, r) {
  function i(a) {
    return t(a = arguments.length === 0 ? /* @__PURE__ */ new Date() : /* @__PURE__ */ new Date(+a)), a;
  }
  return i.floor = (a) => (t(a = /* @__PURE__ */ new Date(+a)), a), i.ceil = (a) => (t(a = new Date(a - 1)), e(a, 1), t(a), a), i.round = (a) => {
    const s = i(a), D = i.ceil(a);
    return a - s < D - a ? s : D;
  }, i.offset = (a, s) => (e(a = /* @__PURE__ */ new Date(+a), s == null ? 1 : Math.floor(s)), a), i.range = (a, s, D) => {
    const S = [];
    if (a = i.ceil(a), D = D == null ? 1 : Math.floor(D), !(a < s) || !(D > 0)) return S;
    let k;
    do
      S.push(k = /* @__PURE__ */ new Date(+a)), e(a, D), t(a);
    while (k < a && a < s);
    return S;
  }, i.filter = (a) => G((s) => {
    if (s >= s) for (; t(s), !a(s); ) s.setTime(s - 1);
  }, (s, D) => {
    if (s >= s)
      if (D < 0) for (; ++D <= 0; )
        for (; e(s, -1), !a(s); )
          ;
      else for (; --D >= 0; )
        for (; e(s, 1), !a(s); )
          ;
  }), n && (i.count = (a, s) => (le.setTime(+a), ue.setTime(+s), t(le), t(ue), Math.floor(n(le, ue))), i.every = (a) => (a = Math.floor(a), !isFinite(a) || !(a > 0) ? null : a > 1 ? i.filter(r ? (s) => r(s) % a === 0 : (s) => i.count(0, s) % a === 0) : i)), i;
}
const Ft = G(() => {
}, (t, e) => {
  t.setTime(+t + e);
}, (t, e) => e - t);
Ft.every = (t) => (t = Math.floor(t), !isFinite(t) || !(t > 0) ? null : t > 1 ? G((e) => {
  e.setTime(Math.floor(e / t) * t);
}, (e, n) => {
  e.setTime(+e + n * t);
}, (e, n) => (n - e) / t) : Ft);
Ft.range;
const mt = 1e3, at = mt * 60, gt = at * 60, yt = gt * 24, ve = yt * 7, Ye = yt * 30, fe = yt * 365, pt = G((t) => {
  t.setTime(t - t.getMilliseconds());
}, (t, e) => {
  t.setTime(+t + e * mt);
}, (t, e) => (e - t) / mt, (t) => t.getUTCSeconds());
pt.range;
const Yt = G((t) => {
  t.setTime(t - t.getMilliseconds() - t.getSeconds() * mt);
}, (t, e) => {
  t.setTime(+t + e * at);
}, (t, e) => (e - t) / at, (t) => t.getMinutes());
Yt.range;
const dr = G((t) => {
  t.setUTCSeconds(0, 0);
}, (t, e) => {
  t.setTime(+t + e * at);
}, (t, e) => (e - t) / at, (t) => t.getUTCMinutes());
dr.range;
const Wt = G((t) => {
  t.setTime(t - t.getMilliseconds() - t.getSeconds() * mt - t.getMinutes() * at);
}, (t, e) => {
  t.setTime(+t + e * gt);
}, (t, e) => (e - t) / gt, (t) => t.getHours());
Wt.range;
const mr = G((t) => {
  t.setUTCMinutes(0, 0, 0);
}, (t, e) => {
  t.setTime(+t + e * gt);
}, (t, e) => (e - t) / gt, (t) => t.getUTCHours());
mr.range;
const Tt = G((t) => t.setHours(0, 0, 0, 0), (t, e) => t.setDate(t.getDate() + e), (t, e) => (e - t - (e.getTimezoneOffset() - t.getTimezoneOffset()) * at) / yt, (t) => t.getDate() - 1);
Tt.range;
const be = G((t) => {
  t.setUTCHours(0, 0, 0, 0);
}, (t, e) => {
  t.setUTCDate(t.getUTCDate() + e);
}, (t, e) => (e - t) / yt, (t) => t.getUTCDate() - 1);
be.range;
const gr = G((t) => {
  t.setUTCHours(0, 0, 0, 0);
}, (t, e) => {
  t.setUTCDate(t.getUTCDate() + e);
}, (t, e) => (e - t) / yt, (t) => Math.floor(t / yt));
gr.range;
function xt(t) {
  return G((e) => {
    e.setDate(e.getDate() - (e.getDay() + 7 - t) % 7), e.setHours(0, 0, 0, 0);
  }, (e, n) => {
    e.setDate(e.getDate() + n * 7);
  }, (e, n) => (n - e - (n.getTimezoneOffset() - e.getTimezoneOffset()) * at) / ve);
}
const Ht = xt(0), Ot = xt(1), cn = xt(2), ln = xt(3), vt = xt(4), un = xt(5), fn = xt(6);
Ht.range;
Ot.range;
cn.range;
ln.range;
vt.range;
un.range;
fn.range;
function wt(t) {
  return G((e) => {
    e.setUTCDate(e.getUTCDate() - (e.getUTCDay() + 7 - t) % 7), e.setUTCHours(0, 0, 0, 0);
  }, (e, n) => {
    e.setUTCDate(e.getUTCDate() + n * 7);
  }, (e, n) => (n - e) / ve);
}
const hn = wt(0), Kt = wt(1), yr = wt(2), kr = wt(3), Ut = wt(4), pr = wt(5), Tr = wt(6);
hn.range;
Kt.range;
yr.range;
kr.range;
Ut.range;
pr.range;
Tr.range;
const Nt = G((t) => {
  t.setDate(1), t.setHours(0, 0, 0, 0);
}, (t, e) => {
  t.setMonth(t.getMonth() + e);
}, (t, e) => e.getMonth() - t.getMonth() + (e.getFullYear() - t.getFullYear()) * 12, (t) => t.getMonth());
Nt.range;
const vr = G((t) => {
  t.setUTCDate(1), t.setUTCHours(0, 0, 0, 0);
}, (t, e) => {
  t.setUTCMonth(t.getUTCMonth() + e);
}, (t, e) => e.getUTCMonth() - t.getUTCMonth() + (e.getUTCFullYear() - t.getUTCFullYear()) * 12, (t) => t.getUTCMonth());
vr.range;
const kt = G((t) => {
  t.setMonth(0, 1), t.setHours(0, 0, 0, 0);
}, (t, e) => {
  t.setFullYear(t.getFullYear() + e);
}, (t, e) => e.getFullYear() - t.getFullYear(), (t) => t.getFullYear());
kt.every = (t) => !isFinite(t = Math.floor(t)) || !(t > 0) ? null : G((e) => {
  e.setFullYear(Math.floor(e.getFullYear() / t) * t), e.setMonth(0, 1), e.setHours(0, 0, 0, 0);
}, (e, n) => {
  e.setFullYear(e.getFullYear() + n * t);
});
kt.range;
const bt = G((t) => {
  t.setUTCMonth(0, 1), t.setUTCHours(0, 0, 0, 0);
}, (t, e) => {
  t.setUTCFullYear(t.getUTCFullYear() + e);
}, (t, e) => e.getUTCFullYear() - t.getUTCFullYear(), (t) => t.getUTCFullYear());
bt.every = (t) => !isFinite(t = Math.floor(t)) || !(t > 0) ? null : G((e) => {
  e.setUTCFullYear(Math.floor(e.getUTCFullYear() / t) * t), e.setUTCMonth(0, 1), e.setUTCHours(0, 0, 0, 0);
}, (e, n) => {
  e.setUTCFullYear(e.getUTCFullYear() + n * t);
});
bt.range;
function br(t, e, n, r, i, a) {
  const s = [[pt, 1, mt], [pt, 5, 5 * mt], [pt, 15, 15 * mt], [pt, 30, 30 * mt], [a, 1, at], [a, 5, 5 * at], [a, 15, 15 * at], [a, 30, 30 * at], [i, 1, gt], [i, 3, 3 * gt], [i, 6, 6 * gt], [i, 12, 12 * gt], [r, 1, yt], [r, 2, 2 * yt], [n, 1, ve], [e, 1, Ye], [e, 3, 3 * Ye], [t, 1, fe]];
  function D(k, p, A) {
    const x = p < k;
    x && ([k, p] = [p, k]);
    const y = A && typeof A.range == "function" ? A : S(k, p, A), R = y ? y.range(k, +p + 1) : [];
    return x ? R.reverse() : R;
  }
  function S(k, p, A) {
    const x = Math.abs(p - k) / A, y = Bn(([, , et]) => et).right(s, x);
    if (y === s.length) return t.every(Ae(k / fe, p / fe, A));
    if (y === 0) return Ft.every(Math.max(Ae(k, p, A), 1));
    const [R, I] = s[x / s[y - 1][2] < s[y][2] / x ? y - 1 : y];
    return R.every(I);
  }
  return [D, S];
}
const [xr, wr] = br(kt, Nt, Ht, Tt, Wt, Yt);
function he(t) {
  if (0 <= t.y && t.y < 100) {
    var e = new Date(-1, t.m, t.d, t.H, t.M, t.S, t.L);
    return e.setFullYear(t.y), e;
  }
  return new Date(t.y, t.m, t.d, t.H, t.M, t.S, t.L);
}
function de(t) {
  if (0 <= t.y && t.y < 100) {
    var e = new Date(Date.UTC(-1, t.m, t.d, t.H, t.M, t.S, t.L));
    return e.setUTCFullYear(t.y), e;
  }
  return new Date(Date.UTC(t.y, t.m, t.d, t.H, t.M, t.S, t.L));
}
function It(t, e, n) {
  return {
    y: t,
    m: e,
    d: n,
    H: 0,
    M: 0,
    S: 0,
    L: 0
  };
}
function Cr(t) {
  var e = t.dateTime, n = t.date, r = t.time, i = t.periods, a = t.days, s = t.shortDays, D = t.months, S = t.shortMonths, k = At(i), p = Lt(i), A = At(a), x = Lt(a), y = At(s), R = Lt(s), I = At(D), et = Lt(D), rt = At(S), nt = Lt(S), Z = {
    a: d,
    A: v,
    b: c,
    B: l,
    c: null,
    d: Pe,
    e: Pe,
    f: Xr,
    g: ri,
    G: ai,
    H: Br,
    I: qr,
    j: Zr,
    L: dn,
    m: jr,
    M: Gr,
    p: o,
    q: V,
    Q: Be,
    s: qe,
    S: Qr,
    u: Jr,
    U: Kr,
    V: $r,
    w: ti,
    W: ei,
    x: null,
    X: null,
    y: ni,
    Y: ii,
    Z: si,
    "%": ze
  }, X = {
    a: W,
    A: H,
    b: Q,
    B: z,
    c: null,
    d: Re,
    e: Re,
    f: ui,
    g: vi,
    G: xi,
    H: oi,
    I: ci,
    j: li,
    L: gn,
    m: fi,
    M: hi,
    p: B,
    q: st,
    Q: Be,
    s: qe,
    S: di,
    u: mi,
    U: gi,
    V: yi,
    w: ki,
    W: pi,
    x: null,
    X: null,
    y: Ti,
    Y: bi,
    Z: wi,
    "%": ze
  }, $ = {
    a: _,
    A: M,
    b,
    B: L,
    c: h,
    d: He,
    e: He,
    f: Vr,
    g: Ne,
    G: Oe,
    H: Ve,
    I: Ve,
    j: Wr,
    L: Hr,
    m: Yr,
    M: Or,
    p: U,
    q: Lr,
    Q: Rr,
    s: zr,
    S: Nr,
    u: Fr,
    U: Ur,
    V: Er,
    w: Sr,
    W: Ir,
    x: m,
    X: T,
    y: Ne,
    Y: Oe,
    Z: Ar,
    "%": Pr
  };
  Z.x = w(n, Z), Z.X = w(r, Z), Z.c = w(e, Z), X.x = w(n, X), X.X = w(r, X), X.c = w(e, X);
  function w(g, E) {
    return function(Y) {
      var u = [], K = -1, F = 0, q = g.length, P, ot, ut;
      for (Y instanceof Date || (Y = /* @__PURE__ */ new Date(+Y)); ++K < q; )
        g.charCodeAt(K) === 37 && (u.push(g.slice(F, K)), (ot = We[P = g.charAt(++K)]) != null ? P = g.charAt(++K) : ot = P === "e" ? " " : "0", (ut = E[P]) && (P = ut(Y, ot)), u.push(P), F = K + 1);
      return u.push(g.slice(F, K)), u.join("");
    };
  }
  function N(g, E) {
    return function(Y) {
      var u = It(1900, void 0, 1), K = C(u, g, Y += "", 0), F, q;
      if (K != Y.length) return null;
      if ("Q" in u) return new Date(u.Q);
      if ("s" in u) return new Date(u.s * 1e3 + ("L" in u ? u.L : 0));
      if (E && !("Z" in u) && (u.Z = 0), "p" in u && (u.H = u.H % 12 + u.p * 12), u.m === void 0 && (u.m = "q" in u ? u.q : 0), "V" in u) {
        if (u.V < 1 || u.V > 53) return null;
        "w" in u || (u.w = 1), "Z" in u ? (F = de(It(u.y, 0, 1)), q = F.getUTCDay(), F = q > 4 || q === 0 ? Kt.ceil(F) : Kt(F), F = be.offset(F, (u.V - 1) * 7), u.y = F.getUTCFullYear(), u.m = F.getUTCMonth(), u.d = F.getUTCDate() + (u.w + 6) % 7) : (F = he(It(u.y, 0, 1)), q = F.getDay(), F = q > 4 || q === 0 ? Ot.ceil(F) : Ot(F), F = Tt.offset(F, (u.V - 1) * 7), u.y = F.getFullYear(), u.m = F.getMonth(), u.d = F.getDate() + (u.w + 6) % 7);
      } else ("W" in u || "U" in u) && ("w" in u || (u.w = "u" in u ? u.u % 7 : "W" in u ? 1 : 0), q = "Z" in u ? de(It(u.y, 0, 1)).getUTCDay() : he(It(u.y, 0, 1)).getDay(), u.m = 0, u.d = "W" in u ? (u.w + 6) % 7 + u.W * 7 - (q + 5) % 7 : u.w + u.U * 7 - (q + 6) % 7);
      return "Z" in u ? (u.H += u.Z / 100 | 0, u.M += u.Z % 100, de(u)) : he(u);
    };
  }
  function C(g, E, Y, u) {
    for (var K = 0, F = E.length, q = Y.length, P, ot; K < F; ) {
      if (u >= q) return -1;
      if (P = E.charCodeAt(K++), P === 37) {
        if (P = E.charAt(K++), ot = $[P in We ? E.charAt(K++) : P], !ot || (u = ot(g, Y, u)) < 0) return -1;
      } else if (P != Y.charCodeAt(u++))
        return -1;
    }
    return u;
  }
  function U(g, E, Y) {
    var u = k.exec(E.slice(Y));
    return u ? (g.p = p.get(u[0].toLowerCase()), Y + u[0].length) : -1;
  }
  function _(g, E, Y) {
    var u = y.exec(E.slice(Y));
    return u ? (g.w = R.get(u[0].toLowerCase()), Y + u[0].length) : -1;
  }
  function M(g, E, Y) {
    var u = A.exec(E.slice(Y));
    return u ? (g.w = x.get(u[0].toLowerCase()), Y + u[0].length) : -1;
  }
  function b(g, E, Y) {
    var u = rt.exec(E.slice(Y));
    return u ? (g.m = nt.get(u[0].toLowerCase()), Y + u[0].length) : -1;
  }
  function L(g, E, Y) {
    var u = I.exec(E.slice(Y));
    return u ? (g.m = et.get(u[0].toLowerCase()), Y + u[0].length) : -1;
  }
  function h(g, E, Y) {
    return C(g, e, E, Y);
  }
  function m(g, E, Y) {
    return C(g, n, E, Y);
  }
  function T(g, E, Y) {
    return C(g, r, E, Y);
  }
  function d(g) {
    return s[g.getDay()];
  }
  function v(g) {
    return a[g.getDay()];
  }
  function c(g) {
    return S[g.getMonth()];
  }
  function l(g) {
    return D[g.getMonth()];
  }
  function o(g) {
    return i[+(g.getHours() >= 12)];
  }
  function V(g) {
    return 1 + ~~(g.getMonth() / 3);
  }
  function W(g) {
    return s[g.getUTCDay()];
  }
  function H(g) {
    return a[g.getUTCDay()];
  }
  function Q(g) {
    return S[g.getUTCMonth()];
  }
  function z(g) {
    return D[g.getUTCMonth()];
  }
  function B(g) {
    return i[+(g.getUTCHours() >= 12)];
  }
  function st(g) {
    return 1 + ~~(g.getUTCMonth() / 3);
  }
  return {
    format: function(g) {
      var E = w(g += "", Z);
      return E.toString = function() {
        return g;
      }, E;
    },
    parse: function(g) {
      var E = N(g += "", !1);
      return E.toString = function() {
        return g;
      }, E;
    },
    utcFormat: function(g) {
      var E = w(g += "", X);
      return E.toString = function() {
        return g;
      }, E;
    },
    utcParse: function(g) {
      var E = N(g += "", !0);
      return E.toString = function() {
        return g;
      }, E;
    }
  };
}
var We = {
  "-": "",
  _: " ",
  0: "0"
}, J = /^\s*\d+/, Dr = /^%/, _r = /[\\^$*+?|[\]().{}]/g;
function O(t, e, n) {
  var r = t < 0 ? "-" : "", i = (r ? -t : t) + "", a = i.length;
  return r + (a < n ? new Array(n - a + 1).join(e) + i : i);
}
function Mr(t) {
  return t.replace(_r, "\\$&");
}
function At(t) {
  return new RegExp("^(?:" + t.map(Mr).join("|") + ")", "i");
}
function Lt(t) {
  return new Map(t.map((e, n) => [e.toLowerCase(), n]));
}
function Sr(t, e, n) {
  var r = J.exec(e.slice(n, n + 1));
  return r ? (t.w = +r[0], n + r[0].length) : -1;
}
function Fr(t, e, n) {
  var r = J.exec(e.slice(n, n + 1));
  return r ? (t.u = +r[0], n + r[0].length) : -1;
}
function Ur(t, e, n) {
  var r = J.exec(e.slice(n, n + 2));
  return r ? (t.U = +r[0], n + r[0].length) : -1;
}
function Er(t, e, n) {
  var r = J.exec(e.slice(n, n + 2));
  return r ? (t.V = +r[0], n + r[0].length) : -1;
}
function Ir(t, e, n) {
  var r = J.exec(e.slice(n, n + 2));
  return r ? (t.W = +r[0], n + r[0].length) : -1;
}
function Oe(t, e, n) {
  var r = J.exec(e.slice(n, n + 4));
  return r ? (t.y = +r[0], n + r[0].length) : -1;
}
function Ne(t, e, n) {
  var r = J.exec(e.slice(n, n + 2));
  return r ? (t.y = +r[0] + (+r[0] > 68 ? 1900 : 2e3), n + r[0].length) : -1;
}
function Ar(t, e, n) {
  var r = /^(Z)|([+-]\d\d)(?::?(\d\d))?/.exec(e.slice(n, n + 6));
  return r ? (t.Z = r[1] ? 0 : -(r[2] + (r[3] || "00")), n + r[0].length) : -1;
}
function Lr(t, e, n) {
  var r = J.exec(e.slice(n, n + 1));
  return r ? (t.q = r[0] * 3 - 3, n + r[0].length) : -1;
}
function Yr(t, e, n) {
  var r = J.exec(e.slice(n, n + 2));
  return r ? (t.m = r[0] - 1, n + r[0].length) : -1;
}
function He(t, e, n) {
  var r = J.exec(e.slice(n, n + 2));
  return r ? (t.d = +r[0], n + r[0].length) : -1;
}
function Wr(t, e, n) {
  var r = J.exec(e.slice(n, n + 3));
  return r ? (t.m = 0, t.d = +r[0], n + r[0].length) : -1;
}
function Ve(t, e, n) {
  var r = J.exec(e.slice(n, n + 2));
  return r ? (t.H = +r[0], n + r[0].length) : -1;
}
function Or(t, e, n) {
  var r = J.exec(e.slice(n, n + 2));
  return r ? (t.M = +r[0], n + r[0].length) : -1;
}
function Nr(t, e, n) {
  var r = J.exec(e.slice(n, n + 2));
  return r ? (t.S = +r[0], n + r[0].length) : -1;
}
function Hr(t, e, n) {
  var r = J.exec(e.slice(n, n + 3));
  return r ? (t.L = +r[0], n + r[0].length) : -1;
}
function Vr(t, e, n) {
  var r = J.exec(e.slice(n, n + 6));
  return r ? (t.L = Math.floor(r[0] / 1e3), n + r[0].length) : -1;
}
function Pr(t, e, n) {
  var r = Dr.exec(e.slice(n, n + 1));
  return r ? n + r[0].length : -1;
}
function Rr(t, e, n) {
  var r = J.exec(e.slice(n));
  return r ? (t.Q = +r[0], n + r[0].length) : -1;
}
function zr(t, e, n) {
  var r = J.exec(e.slice(n));
  return r ? (t.s = +r[0], n + r[0].length) : -1;
}
function Pe(t, e) {
  return O(t.getDate(), e, 2);
}
function Br(t, e) {
  return O(t.getHours(), e, 2);
}
function qr(t, e) {
  return O(t.getHours() % 12 || 12, e, 2);
}
function Zr(t, e) {
  return O(1 + Tt.count(kt(t), t), e, 3);
}
function dn(t, e) {
  return O(t.getMilliseconds(), e, 3);
}
function Xr(t, e) {
  return dn(t, e) + "000";
}
function jr(t, e) {
  return O(t.getMonth() + 1, e, 2);
}
function Gr(t, e) {
  return O(t.getMinutes(), e, 2);
}
function Qr(t, e) {
  return O(t.getSeconds(), e, 2);
}
function Jr(t) {
  var e = t.getDay();
  return e === 0 ? 7 : e;
}
function Kr(t, e) {
  return O(Ht.count(kt(t) - 1, t), e, 2);
}
function mn(t) {
  var e = t.getDay();
  return e >= 4 || e === 0 ? vt(t) : vt.ceil(t);
}
function $r(t, e) {
  return t = mn(t), O(vt.count(kt(t), t) + (kt(t).getDay() === 4), e, 2);
}
function ti(t) {
  return t.getDay();
}
function ei(t, e) {
  return O(Ot.count(kt(t) - 1, t), e, 2);
}
function ni(t, e) {
  return O(t.getFullYear() % 100, e, 2);
}
function ri(t, e) {
  return t = mn(t), O(t.getFullYear() % 100, e, 2);
}
function ii(t, e) {
  return O(t.getFullYear() % 1e4, e, 4);
}
function ai(t, e) {
  var n = t.getDay();
  return t = n >= 4 || n === 0 ? vt(t) : vt.ceil(t), O(t.getFullYear() % 1e4, e, 4);
}
function si(t) {
  var e = t.getTimezoneOffset();
  return (e > 0 ? "-" : (e *= -1, "+")) + O(e / 60 | 0, "0", 2) + O(e % 60, "0", 2);
}
function Re(t, e) {
  return O(t.getUTCDate(), e, 2);
}
function oi(t, e) {
  return O(t.getUTCHours(), e, 2);
}
function ci(t, e) {
  return O(t.getUTCHours() % 12 || 12, e, 2);
}
function li(t, e) {
  return O(1 + be.count(bt(t), t), e, 3);
}
function gn(t, e) {
  return O(t.getUTCMilliseconds(), e, 3);
}
function ui(t, e) {
  return gn(t, e) + "000";
}
function fi(t, e) {
  return O(t.getUTCMonth() + 1, e, 2);
}
function hi(t, e) {
  return O(t.getUTCMinutes(), e, 2);
}
function di(t, e) {
  return O(t.getUTCSeconds(), e, 2);
}
function mi(t) {
  var e = t.getUTCDay();
  return e === 0 ? 7 : e;
}
function gi(t, e) {
  return O(hn.count(bt(t) - 1, t), e, 2);
}
function yn(t) {
  var e = t.getUTCDay();
  return e >= 4 || e === 0 ? Ut(t) : Ut.ceil(t);
}
function yi(t, e) {
  return t = yn(t), O(Ut.count(bt(t), t) + (bt(t).getUTCDay() === 4), e, 2);
}
function ki(t) {
  return t.getUTCDay();
}
function pi(t, e) {
  return O(Kt.count(bt(t) - 1, t), e, 2);
}
function Ti(t, e) {
  return O(t.getUTCFullYear() % 100, e, 2);
}
function vi(t, e) {
  return t = yn(t), O(t.getUTCFullYear() % 100, e, 2);
}
function bi(t, e) {
  return O(t.getUTCFullYear() % 1e4, e, 4);
}
function xi(t, e) {
  var n = t.getUTCDay();
  return t = n >= 4 || n === 0 ? Ut(t) : Ut.ceil(t), O(t.getUTCFullYear() % 1e4, e, 4);
}
function wi() {
  return "+0000";
}
function ze() {
  return "%";
}
function Be(t) {
  return +t;
}
function qe(t) {
  return Math.floor(+t / 1e3);
}
var Dt, $t;
Ci({
  dateTime: "%x, %X",
  date: "%-m/%-d/%Y",
  time: "%-I:%M:%S %p",
  periods: ["AM", "PM"],
  days: ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"],
  shortDays: ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"],
  months: ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"],
  shortMonths: ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
});
function Ci(t) {
  return Dt = Cr(t), $t = Dt.format, Dt.parse, Dt.utcFormat, Dt.utcParse, Dt;
}
function Di(t) {
  return new Date(t);
}
function _i(t) {
  return t instanceof Date ? +t : +/* @__PURE__ */ new Date(+t);
}
function kn(t, e, n, r, i, a, s, D, S, k) {
  var p = qn(), A = p.invert, x = p.domain, y = k(".%L"), R = k(":%S"), I = k("%I:%M"), et = k("%I %p"), rt = k("%a %d"), nt = k("%b %d"), Z = k("%B"), X = k("%Y");
  function $(w) {
    return (S(w) < w ? y : D(w) < w ? R : s(w) < w ? I : a(w) < w ? et : r(w) < w ? i(w) < w ? rt : nt : n(w) < w ? Z : X)(w);
  }
  return p.invert = function(w) {
    return new Date(A(w));
  }, p.domain = function(w) {
    return arguments.length ? x(Array.from(w, _i)) : x().map(Di);
  }, p.ticks = function(w) {
    var N = x();
    return t(N[0], N[N.length - 1], w ?? 10);
  }, p.tickFormat = function(w, N) {
    return N == null ? $ : k(N);
  }, p.nice = function(w) {
    var N = x();
    return (!w || typeof w.range != "function") && (w = e(N[0], N[N.length - 1], w ?? 10)), w ? x(hr(N, w)) : p;
  }, p.copy = function() {
    return Zn(p, kn(t, e, n, r, i, a, s, D, S, k));
  }, p;
}
function Mi() {
  return jn.apply(kn(xr, wr, kt, Nt, Ht, Tt, Wt, Yt, pt, $t).domain([new Date(2e3, 0, 1), new Date(2e3, 0, 2)]), arguments);
}
var pn = {
  exports: {}
};
(function(t, e) {
  (function(n, r) {
    t.exports = r();
  })(Vn, function() {
    var n = "day";
    return function(r, i, a) {
      var s = function(k) {
        return k.add(4 - k.isoWeekday(), n);
      }, D = i.prototype;
      D.isoWeekYear = function() {
        return s(this).year();
      }, D.isoWeek = function(k) {
        if (!this.$utils().u(k)) return this.add(7 * (k - this.isoWeek()), n);
        var p, A, x, y, R = s(this), I = (p = this.isoWeekYear(), A = this.$u, x = (A ? a.utc : a)().year(p).startOf("year"), y = 4 - x.isoWeekday(), x.isoWeekday() > 4 && (y += 7), x.add(y, n));
        return R.diff(I, "week") + 1;
      }, D.isoWeekday = function(k) {
        return this.$utils().u(k) ? this.day() || 7 : this.day(this.day() % 7 ? k : k - 7);
      };
      var S = D.startOf;
      D.startOf = function(k, p) {
        var A = this.$utils(), x = !!A.u(p) || p;
        return A.p(k) === "isoweek" ? x ? this.date(this.date() - (this.isoWeekday() - 1)).startOf("day") : this.date(this.date() - 1 - (this.isoWeekday() - 1) + 7).endOf("day") : S.bind(this)(k, p);
      };
    };
  });
})(pn);
var Si = pn.exports;
const Fi = /* @__PURE__ */ Pn(Si);
var ye = function() {
  var t = /* @__PURE__ */ f(function(L, h, m, T) {
    for (m = m || {}, T = L.length; T--; m[L[T]] = h) ;
    return m;
  }, "o"), e = [6, 8, 10, 12, 13, 14, 15, 16, 17, 18, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 33, 35, 36, 38, 40], n = [1, 26], r = [1, 27], i = [1, 28], a = [1, 29], s = [1, 30], D = [1, 31], S = [1, 32], k = [1, 33], p = [1, 34], A = [1, 9], x = [1, 10], y = [1, 11], R = [1, 12], I = [1, 13], et = [1, 14], rt = [1, 15], nt = [1, 16], Z = [1, 19], X = [1, 20], $ = [1, 21], w = [1, 22], N = [1, 23], C = [1, 25], U = [1, 35], _ = {
    trace: /* @__PURE__ */ f(function() {
    }, "trace"),
    yy: {},
    symbols_: {
      error: 2,
      start: 3,
      gantt: 4,
      document: 5,
      EOF: 6,
      line: 7,
      SPACE: 8,
      statement: 9,
      NL: 10,
      weekday: 11,
      weekday_monday: 12,
      weekday_tuesday: 13,
      weekday_wednesday: 14,
      weekday_thursday: 15,
      weekday_friday: 16,
      weekday_saturday: 17,
      weekday_sunday: 18,
      weekend: 19,
      weekend_friday: 20,
      weekend_saturday: 21,
      dateFormat: 22,
      inclusiveEndDates: 23,
      topAxis: 24,
      axisFormat: 25,
      tickInterval: 26,
      excludes: 27,
      includes: 28,
      todayMarker: 29,
      title: 30,
      acc_title: 31,
      acc_title_value: 32,
      acc_descr: 33,
      acc_descr_value: 34,
      acc_descr_multiline_value: 35,
      section: 36,
      clickStatement: 37,
      taskTxt: 38,
      taskData: 39,
      click: 40,
      callbackname: 41,
      callbackargs: 42,
      href: 43,
      clickStatementDebug: 44,
      $accept: 0,
      $end: 1
    },
    terminals_: {
      2: "error",
      4: "gantt",
      6: "EOF",
      8: "SPACE",
      10: "NL",
      12: "weekday_monday",
      13: "weekday_tuesday",
      14: "weekday_wednesday",
      15: "weekday_thursday",
      16: "weekday_friday",
      17: "weekday_saturday",
      18: "weekday_sunday",
      20: "weekend_friday",
      21: "weekend_saturday",
      22: "dateFormat",
      23: "inclusiveEndDates",
      24: "topAxis",
      25: "axisFormat",
      26: "tickInterval",
      27: "excludes",
      28: "includes",
      29: "todayMarker",
      30: "title",
      31: "acc_title",
      32: "acc_title_value",
      33: "acc_descr",
      34: "acc_descr_value",
      35: "acc_descr_multiline_value",
      36: "section",
      38: "taskTxt",
      39: "taskData",
      40: "click",
      41: "callbackname",
      42: "callbackargs",
      43: "href"
    },
    productions_: [0, [3, 3], [5, 0], [5, 2], [7, 2], [7, 1], [7, 1], [7, 1], [11, 1], [11, 1], [11, 1], [11, 1], [11, 1], [11, 1], [11, 1], [19, 1], [19, 1], [9, 1], [9, 1], [9, 1], [9, 1], [9, 1], [9, 1], [9, 1], [9, 1], [9, 1], [9, 1], [9, 1], [9, 2], [9, 2], [9, 1], [9, 1], [9, 1], [9, 2], [37, 2], [37, 3], [37, 3], [37, 4], [37, 3], [37, 4], [37, 2], [44, 2], [44, 3], [44, 3], [44, 4], [44, 3], [44, 4], [44, 2]],
    performAction: /* @__PURE__ */ f(function(h, m, T, d, v, c, l) {
      var o = c.length - 1;
      switch (v) {
        case 1:
          return c[o - 1];
        case 2:
          this.$ = [];
          break;
        case 3:
          c[o - 1].push(c[o]), this.$ = c[o - 1];
          break;
        case 4:
        case 5:
          this.$ = c[o];
          break;
        case 6:
        case 7:
          this.$ = [];
          break;
        case 8:
          d.setWeekday("monday");
          break;
        case 9:
          d.setWeekday("tuesday");
          break;
        case 10:
          d.setWeekday("wednesday");
          break;
        case 11:
          d.setWeekday("thursday");
          break;
        case 12:
          d.setWeekday("friday");
          break;
        case 13:
          d.setWeekday("saturday");
          break;
        case 14:
          d.setWeekday("sunday");
          break;
        case 15:
          d.setWeekend("friday");
          break;
        case 16:
          d.setWeekend("saturday");
          break;
        case 17:
          d.setDateFormat(c[o].substr(11)), this.$ = c[o].substr(11);
          break;
        case 18:
          d.enableInclusiveEndDates(), this.$ = c[o].substr(18);
          break;
        case 19:
          d.TopAxis(), this.$ = c[o].substr(8);
          break;
        case 20:
          d.setAxisFormat(c[o].substr(11)), this.$ = c[o].substr(11);
          break;
        case 21:
          d.setTickInterval(c[o].substr(13)), this.$ = c[o].substr(13);
          break;
        case 22:
          d.setExcludes(c[o].substr(9)), this.$ = c[o].substr(9);
          break;
        case 23:
          d.setIncludes(c[o].substr(9)), this.$ = c[o].substr(9);
          break;
        case 24:
          d.setTodayMarker(c[o].substr(12)), this.$ = c[o].substr(12);
          break;
        case 27:
          d.setDiagramTitle(c[o].substr(6)), this.$ = c[o].substr(6);
          break;
        case 28:
          this.$ = c[o].trim(), d.setAccTitle(this.$);
          break;
        case 29:
        case 30:
          this.$ = c[o].trim(), d.setAccDescription(this.$);
          break;
        case 31:
          d.addSection(c[o].substr(8)), this.$ = c[o].substr(8);
          break;
        case 33:
          d.addTask(c[o - 1], c[o]), this.$ = "task";
          break;
        case 34:
          this.$ = c[o - 1], d.setClickEvent(c[o - 1], c[o], null);
          break;
        case 35:
          this.$ = c[o - 2], d.setClickEvent(c[o - 2], c[o - 1], c[o]);
          break;
        case 36:
          this.$ = c[o - 2], d.setClickEvent(c[o - 2], c[o - 1], null), d.setLink(c[o - 2], c[o]);
          break;
        case 37:
          this.$ = c[o - 3], d.setClickEvent(c[o - 3], c[o - 2], c[o - 1]), d.setLink(c[o - 3], c[o]);
          break;
        case 38:
          this.$ = c[o - 2], d.setClickEvent(c[o - 2], c[o], null), d.setLink(c[o - 2], c[o - 1]);
          break;
        case 39:
          this.$ = c[o - 3], d.setClickEvent(c[o - 3], c[o - 1], c[o]), d.setLink(c[o - 3], c[o - 2]);
          break;
        case 40:
          this.$ = c[o - 1], d.setLink(c[o - 1], c[o]);
          break;
        case 41:
        case 47:
          this.$ = c[o - 1] + " " + c[o];
          break;
        case 42:
        case 43:
        case 45:
          this.$ = c[o - 2] + " " + c[o - 1] + " " + c[o];
          break;
        case 44:
        case 46:
          this.$ = c[o - 3] + " " + c[o - 2] + " " + c[o - 1] + " " + c[o];
          break;
      }
    }, "anonymous"),
    table: [{
      3: 1,
      4: [1, 2]
    }, {
      1: [3]
    }, t(e, [2, 2], {
      5: 3
    }), {
      6: [1, 4],
      7: 5,
      8: [1, 6],
      9: 7,
      10: [1, 8],
      11: 17,
      12: n,
      13: r,
      14: i,
      15: a,
      16: s,
      17: D,
      18: S,
      19: 18,
      20: k,
      21: p,
      22: A,
      23: x,
      24: y,
      25: R,
      26: I,
      27: et,
      28: rt,
      29: nt,
      30: Z,
      31: X,
      33: $,
      35: w,
      36: N,
      37: 24,
      38: C,
      40: U
    }, t(e, [2, 7], {
      1: [2, 1]
    }), t(e, [2, 3]), {
      9: 36,
      11: 17,
      12: n,
      13: r,
      14: i,
      15: a,
      16: s,
      17: D,
      18: S,
      19: 18,
      20: k,
      21: p,
      22: A,
      23: x,
      24: y,
      25: R,
      26: I,
      27: et,
      28: rt,
      29: nt,
      30: Z,
      31: X,
      33: $,
      35: w,
      36: N,
      37: 24,
      38: C,
      40: U
    }, t(e, [2, 5]), t(e, [2, 6]), t(e, [2, 17]), t(e, [2, 18]), t(e, [2, 19]), t(e, [2, 20]), t(e, [2, 21]), t(e, [2, 22]), t(e, [2, 23]), t(e, [2, 24]), t(e, [2, 25]), t(e, [2, 26]), t(e, [2, 27]), {
      32: [1, 37]
    }, {
      34: [1, 38]
    }, t(e, [2, 30]), t(e, [2, 31]), t(e, [2, 32]), {
      39: [1, 39]
    }, t(e, [2, 8]), t(e, [2, 9]), t(e, [2, 10]), t(e, [2, 11]), t(e, [2, 12]), t(e, [2, 13]), t(e, [2, 14]), t(e, [2, 15]), t(e, [2, 16]), {
      41: [1, 40],
      43: [1, 41]
    }, t(e, [2, 4]), t(e, [2, 28]), t(e, [2, 29]), t(e, [2, 33]), t(e, [2, 34], {
      42: [1, 42],
      43: [1, 43]
    }), t(e, [2, 40], {
      41: [1, 44]
    }), t(e, [2, 35], {
      43: [1, 45]
    }), t(e, [2, 36]), t(e, [2, 38], {
      42: [1, 46]
    }), t(e, [2, 37]), t(e, [2, 39])],
    defaultActions: {},
    parseError: /* @__PURE__ */ f(function(h, m) {
      if (m.recoverable)
        this.trace(h);
      else {
        var T = new Error(h);
        throw T.hash = m, T;
      }
    }, "parseError"),
    parse: /* @__PURE__ */ f(function(h) {
      var m = this, T = [0], d = [], v = [null], c = [], l = this.table, o = "", V = 0, W = 0, H = 2, Q = 1, z = c.slice.call(arguments, 1), B = Object.create(this.lexer), st = {
        yy: {}
      };
      for (var g in this.yy)
        Object.prototype.hasOwnProperty.call(this.yy, g) && (st.yy[g] = this.yy[g]);
      B.setInput(h, st.yy), st.yy.lexer = B, st.yy.parser = this, typeof B.yylloc > "u" && (B.yylloc = {});
      var E = B.yylloc;
      c.push(E);
      var Y = B.options && B.options.ranges;
      typeof st.yy.parseError == "function" ? this.parseError = st.yy.parseError : this.parseError = Object.getPrototypeOf(this).parseError;
      function u(it) {
        T.length = T.length - 2 * it, v.length = v.length - it, c.length = c.length - it;
      }
      f(u, "popStack");
      function K() {
        var it;
        return it = d.pop() || B.lex() || Q, typeof it != "number" && (it instanceof Array && (d = it, it = d.pop()), it = m.symbols_[it] || it), it;
      }
      f(K, "lex");
      for (var F, q, P, ot, ut = {}, zt, ft, Ie, Bt; ; ) {
        if (q = T[T.length - 1], this.defaultActions[q] ? P = this.defaultActions[q] : ((F === null || typeof F > "u") && (F = K()), P = l[q] && l[q][F]), typeof P > "u" || !P.length || !P[0]) {
          var ne = "";
          Bt = [];
          for (zt in l[q])
            this.terminals_[zt] && zt > H && Bt.push("'" + this.terminals_[zt] + "'");
          B.showPosition ? ne = "Parse error on line " + (V + 1) + `:
` + B.showPosition() + `
Expecting ` + Bt.join(", ") + ", got '" + (this.terminals_[F] || F) + "'" : ne = "Parse error on line " + (V + 1) + ": Unexpected " + (F == Q ? "end of input" : "'" + (this.terminals_[F] || F) + "'"), this.parseError(ne, {
            text: B.match,
            token: this.terminals_[F] || F,
            line: B.yylineno,
            loc: E,
            expected: Bt
          });
        }
        if (P[0] instanceof Array && P.length > 1)
          throw new Error("Parse Error: multiple actions possible at state: " + q + ", token: " + F);
        switch (P[0]) {
          case 1:
            T.push(F), v.push(B.yytext), c.push(B.yylloc), T.push(P[1]), F = null, W = B.yyleng, o = B.yytext, V = B.yylineno, E = B.yylloc;
            break;
          case 2:
            if (ft = this.productions_[P[1]][1], ut.$ = v[v.length - ft], ut._$ = {
              first_line: c[c.length - (ft || 1)].first_line,
              last_line: c[c.length - 1].last_line,
              first_column: c[c.length - (ft || 1)].first_column,
              last_column: c[c.length - 1].last_column
            }, Y && (ut._$.range = [c[c.length - (ft || 1)].range[0], c[c.length - 1].range[1]]), ot = this.performAction.apply(ut, [o, W, V, st.yy, P[1], v, c].concat(z)), typeof ot < "u")
              return ot;
            ft && (T = T.slice(0, -1 * ft * 2), v = v.slice(0, -1 * ft), c = c.slice(0, -1 * ft)), T.push(this.productions_[P[1]][0]), v.push(ut.$), c.push(ut._$), Ie = l[T[T.length - 2]][T[T.length - 1]], T.push(Ie);
            break;
          case 3:
            return !0;
        }
      }
      return !0;
    }, "parse")
  }, M = /* @__PURE__ */ function() {
    var L = {
      EOF: 1,
      parseError: /* @__PURE__ */ f(function(m, T) {
        if (this.yy.parser)
          this.yy.parser.parseError(m, T);
        else
          throw new Error(m);
      }, "parseError"),
      // resets the lexer, sets new input
      setInput: /* @__PURE__ */ f(function(h, m) {
        return this.yy = m || this.yy || {}, this._input = h, this._more = this._backtrack = this.done = !1, this.yylineno = this.yyleng = 0, this.yytext = this.matched = this.match = "", this.conditionStack = ["INITIAL"], this.yylloc = {
          first_line: 1,
          first_column: 0,
          last_line: 1,
          last_column: 0
        }, this.options.ranges && (this.yylloc.range = [0, 0]), this.offset = 0, this;
      }, "setInput"),
      // consumes and returns one char from the input
      input: /* @__PURE__ */ f(function() {
        var h = this._input[0];
        this.yytext += h, this.yyleng++, this.offset++, this.match += h, this.matched += h;
        var m = h.match(/(?:\r\n?|\n).*/g);
        return m ? (this.yylineno++, this.yylloc.last_line++) : this.yylloc.last_column++, this.options.ranges && this.yylloc.range[1]++, this._input = this._input.slice(1), h;
      }, "input"),
      // unshifts one char (or a string) into the input
      unput: /* @__PURE__ */ f(function(h) {
        var m = h.length, T = h.split(/(?:\r\n?|\n)/g);
        this._input = h + this._input, this.yytext = this.yytext.substr(0, this.yytext.length - m), this.offset -= m;
        var d = this.match.split(/(?:\r\n?|\n)/g);
        this.match = this.match.substr(0, this.match.length - 1), this.matched = this.matched.substr(0, this.matched.length - 1), T.length - 1 && (this.yylineno -= T.length - 1);
        var v = this.yylloc.range;
        return this.yylloc = {
          first_line: this.yylloc.first_line,
          last_line: this.yylineno + 1,
          first_column: this.yylloc.first_column,
          last_column: T ? (T.length === d.length ? this.yylloc.first_column : 0) + d[d.length - T.length].length - T[0].length : this.yylloc.first_column - m
        }, this.options.ranges && (this.yylloc.range = [v[0], v[0] + this.yyleng - m]), this.yyleng = this.yytext.length, this;
      }, "unput"),
      // When called from action, caches matched text and appends it on next action
      more: /* @__PURE__ */ f(function() {
        return this._more = !0, this;
      }, "more"),
      // When called from action, signals the lexer that this rule fails to match the input, so the next matching rule (regex) should be tested instead.
      reject: /* @__PURE__ */ f(function() {
        if (this.options.backtrack_lexer)
          this._backtrack = !0;
        else
          return this.parseError("Lexical error on line " + (this.yylineno + 1) + `. You can only invoke reject() in the lexer when the lexer is of the backtracking persuasion (options.backtrack_lexer = true).
` + this.showPosition(), {
            text: "",
            token: null,
            line: this.yylineno
          });
        return this;
      }, "reject"),
      // retain first n characters of the match
      less: /* @__PURE__ */ f(function(h) {
        this.unput(this.match.slice(h));
      }, "less"),
      // displays already matched input, i.e. for error messages
      pastInput: /* @__PURE__ */ f(function() {
        var h = this.matched.substr(0, this.matched.length - this.match.length);
        return (h.length > 20 ? "..." : "") + h.substr(-20).replace(/\n/g, "");
      }, "pastInput"),
      // displays upcoming input, i.e. for error messages
      upcomingInput: /* @__PURE__ */ f(function() {
        var h = this.match;
        return h.length < 20 && (h += this._input.substr(0, 20 - h.length)), (h.substr(0, 20) + (h.length > 20 ? "..." : "")).replace(/\n/g, "");
      }, "upcomingInput"),
      // displays the character position where the lexing error occurred, i.e. for error messages
      showPosition: /* @__PURE__ */ f(function() {
        var h = this.pastInput(), m = new Array(h.length + 1).join("-");
        return h + this.upcomingInput() + `
` + m + "^";
      }, "showPosition"),
      // test the lexed token: return FALSE when not a match, otherwise return token
      test_match: /* @__PURE__ */ f(function(h, m) {
        var T, d, v;
        if (this.options.backtrack_lexer && (v = {
          yylineno: this.yylineno,
          yylloc: {
            first_line: this.yylloc.first_line,
            last_line: this.last_line,
            first_column: this.yylloc.first_column,
            last_column: this.yylloc.last_column
          },
          yytext: this.yytext,
          match: this.match,
          matches: this.matches,
          matched: this.matched,
          yyleng: this.yyleng,
          offset: this.offset,
          _more: this._more,
          _input: this._input,
          yy: this.yy,
          conditionStack: this.conditionStack.slice(0),
          done: this.done
        }, this.options.ranges && (v.yylloc.range = this.yylloc.range.slice(0))), d = h[0].match(/(?:\r\n?|\n).*/g), d && (this.yylineno += d.length), this.yylloc = {
          first_line: this.yylloc.last_line,
          last_line: this.yylineno + 1,
          first_column: this.yylloc.last_column,
          last_column: d ? d[d.length - 1].length - d[d.length - 1].match(/\r?\n?/)[0].length : this.yylloc.last_column + h[0].length
        }, this.yytext += h[0], this.match += h[0], this.matches = h, this.yyleng = this.yytext.length, this.options.ranges && (this.yylloc.range = [this.offset, this.offset += this.yyleng]), this._more = !1, this._backtrack = !1, this._input = this._input.slice(h[0].length), this.matched += h[0], T = this.performAction.call(this, this.yy, this, m, this.conditionStack[this.conditionStack.length - 1]), this.done && this._input && (this.done = !1), T)
          return T;
        if (this._backtrack) {
          for (var c in v)
            this[c] = v[c];
          return !1;
        }
        return !1;
      }, "test_match"),
      // return next match in input
      next: /* @__PURE__ */ f(function() {
        if (this.done)
          return this.EOF;
        this._input || (this.done = !0);
        var h, m, T, d;
        this._more || (this.yytext = "", this.match = "");
        for (var v = this._currentRules(), c = 0; c < v.length; c++)
          if (T = this._input.match(this.rules[v[c]]), T && (!m || T[0].length > m[0].length)) {
            if (m = T, d = c, this.options.backtrack_lexer) {
              if (h = this.test_match(T, v[c]), h !== !1)
                return h;
              if (this._backtrack) {
                m = !1;
                continue;
              } else
                return !1;
            } else if (!this.options.flex)
              break;
          }
        return m ? (h = this.test_match(m, v[d]), h !== !1 ? h : !1) : this._input === "" ? this.EOF : this.parseError("Lexical error on line " + (this.yylineno + 1) + `. Unrecognized text.
` + this.showPosition(), {
          text: "",
          token: null,
          line: this.yylineno
        });
      }, "next"),
      // return next match that has a token
      lex: /* @__PURE__ */ f(function() {
        var m = this.next();
        return m || this.lex();
      }, "lex"),
      // activates a new lexer condition state (pushes the new lexer condition state onto the condition stack)
      begin: /* @__PURE__ */ f(function(m) {
        this.conditionStack.push(m);
      }, "begin"),
      // pop the previously active lexer condition state off the condition stack
      popState: /* @__PURE__ */ f(function() {
        var m = this.conditionStack.length - 1;
        return m > 0 ? this.conditionStack.pop() : this.conditionStack[0];
      }, "popState"),
      // produce the lexer rule set which is active for the currently active lexer condition state
      _currentRules: /* @__PURE__ */ f(function() {
        return this.conditionStack.length && this.conditionStack[this.conditionStack.length - 1] ? this.conditions[this.conditionStack[this.conditionStack.length - 1]].rules : this.conditions.INITIAL.rules;
      }, "_currentRules"),
      // return the currently active lexer condition state; when an index argument is provided it produces the N-th previous condition state, if available
      topState: /* @__PURE__ */ f(function(m) {
        return m = this.conditionStack.length - 1 - Math.abs(m || 0), m >= 0 ? this.conditionStack[m] : "INITIAL";
      }, "topState"),
      // alias for begin(condition)
      pushState: /* @__PURE__ */ f(function(m) {
        this.begin(m);
      }, "pushState"),
      // return the number of states currently on the stack
      stateStackSize: /* @__PURE__ */ f(function() {
        return this.conditionStack.length;
      }, "stateStackSize"),
      options: {
        "case-insensitive": !0
      },
      performAction: /* @__PURE__ */ f(function(m, T, d, v) {
        switch (d) {
          case 0:
            return this.begin("open_directive"), "open_directive";
          case 1:
            return this.begin("acc_title"), 31;
          case 2:
            return this.popState(), "acc_title_value";
          case 3:
            return this.begin("acc_descr"), 33;
          case 4:
            return this.popState(), "acc_descr_value";
          case 5:
            this.begin("acc_descr_multiline");
            break;
          case 6:
            this.popState();
            break;
          case 7:
            return "acc_descr_multiline_value";
          case 8:
            break;
          case 9:
            break;
          case 10:
            break;
          case 11:
            return 10;
          case 12:
            break;
          case 13:
            break;
          case 14:
            this.begin("href");
            break;
          case 15:
            this.popState();
            break;
          case 16:
            return 43;
          case 17:
            this.begin("callbackname");
            break;
          case 18:
            this.popState();
            break;
          case 19:
            this.popState(), this.begin("callbackargs");
            break;
          case 20:
            return 41;
          case 21:
            this.popState();
            break;
          case 22:
            return 42;
          case 23:
            this.begin("click");
            break;
          case 24:
            this.popState();
            break;
          case 25:
            return 40;
          case 26:
            return 4;
          case 27:
            return 22;
          case 28:
            return 23;
          case 29:
            return 24;
          case 30:
            return 25;
          case 31:
            return 26;
          case 32:
            return 28;
          case 33:
            return 27;
          case 34:
            return 29;
          case 35:
            return 12;
          case 36:
            return 13;
          case 37:
            return 14;
          case 38:
            return 15;
          case 39:
            return 16;
          case 40:
            return 17;
          case 41:
            return 18;
          case 42:
            return 20;
          case 43:
            return 21;
          case 44:
            return "date";
          case 45:
            return 30;
          case 46:
            return "accDescription";
          case 47:
            return 36;
          case 48:
            return 38;
          case 49:
            return 39;
          case 50:
            return ":";
          case 51:
            return 6;
          case 52:
            return "INVALID";
        }
      }, "anonymous"),
      rules: [/^(?:%%\{)/i, /^(?:accTitle\s*:\s*)/i, /^(?:(?!\n||)*[^\n]*)/i, /^(?:accDescr\s*:\s*)/i, /^(?:(?!\n||)*[^\n]*)/i, /^(?:accDescr\s*\{\s*)/i, /^(?:[\}])/i, /^(?:[^\}]*)/i, /^(?:%%(?!\{)*[^\n]*)/i, /^(?:[^\}]%%*[^\n]*)/i, /^(?:%%*[^\n]*[\n]*)/i, /^(?:[\n]+)/i, /^(?:\s+)/i, /^(?:%[^\n]*)/i, /^(?:href[\s]+["])/i, /^(?:["])/i, /^(?:[^"]*)/i, /^(?:call[\s]+)/i, /^(?:\([\s]*\))/i, /^(?:\()/i, /^(?:[^(]*)/i, /^(?:\))/i, /^(?:[^)]*)/i, /^(?:click[\s]+)/i, /^(?:[\s\n])/i, /^(?:[^\s\n]*)/i, /^(?:gantt\b)/i, /^(?:dateFormat\s[^#\n;]+)/i, /^(?:inclusiveEndDates\b)/i, /^(?:topAxis\b)/i, /^(?:axisFormat\s[^#\n;]+)/i, /^(?:tickInterval\s[^#\n;]+)/i, /^(?:includes\s[^#\n;]+)/i, /^(?:excludes\s[^#\n;]+)/i, /^(?:todayMarker\s[^\n;]+)/i, /^(?:weekday\s+monday\b)/i, /^(?:weekday\s+tuesday\b)/i, /^(?:weekday\s+wednesday\b)/i, /^(?:weekday\s+thursday\b)/i, /^(?:weekday\s+friday\b)/i, /^(?:weekday\s+saturday\b)/i, /^(?:weekday\s+sunday\b)/i, /^(?:weekend\s+friday\b)/i, /^(?:weekend\s+saturday\b)/i, /^(?:\d\d\d\d-\d\d-\d\d\b)/i, /^(?:title\s[^\n]+)/i, /^(?:accDescription\s[^#\n;]+)/i, /^(?:section\s[^\n]+)/i, /^(?:[^:\n]+)/i, /^(?::[^#\n;]+)/i, /^(?::)/i, /^(?:$)/i, /^(?:.)/i],
      conditions: {
        acc_descr_multiline: {
          rules: [6, 7],
          inclusive: !1
        },
        acc_descr: {
          rules: [4],
          inclusive: !1
        },
        acc_title: {
          rules: [2],
          inclusive: !1
        },
        callbackargs: {
          rules: [21, 22],
          inclusive: !1
        },
        callbackname: {
          rules: [18, 19, 20],
          inclusive: !1
        },
        href: {
          rules: [15, 16],
          inclusive: !1
        },
        click: {
          rules: [24, 25],
          inclusive: !1
        },
        INITIAL: {
          rules: [0, 1, 3, 5, 8, 9, 10, 11, 12, 13, 14, 17, 23, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52],
          inclusive: !0
        }
      }
    };
    return L;
  }();
  _.lexer = M;
  function b() {
    this.yy = {};
  }
  return f(b, "Parser"), b.prototype = _, _.Parser = b, new b();
}();
ye.parser = ye;
var Ui = ye;
tt.extend(Fi);
tt.extend(Rn);
tt.extend(zn);
var Ze = {
  friday: 5,
  saturday: 6
}, ct = "", xe = "", we = void 0, Ce = "", Vt = [], Pt = [], De = /* @__PURE__ */ new Map(), _e = [], te = [], Et = "", Me = "", Tn = ["active", "done", "crit", "milestone", "vert"], Se = [], Rt = !1, Fe = !1, Ue = "sunday", ee = "saturday", ke = 0, Ei = /* @__PURE__ */ f(function() {
  _e = [], te = [], Et = "", Se = [], jt = 0, Te = void 0, Gt = void 0, j = [], ct = "", xe = "", Me = "", we = void 0, Ce = "", Vt = [], Pt = [], Rt = !1, Fe = !1, ke = 0, De = /* @__PURE__ */ new Map(), Nn(), Ue = "sunday", ee = "saturday";
}, "clear"), Ii = /* @__PURE__ */ f(function(t) {
  xe = t;
}, "setAxisFormat"), Ai = /* @__PURE__ */ f(function() {
  return xe;
}, "getAxisFormat"), Li = /* @__PURE__ */ f(function(t) {
  we = t;
}, "setTickInterval"), Yi = /* @__PURE__ */ f(function() {
  return we;
}, "getTickInterval"), Wi = /* @__PURE__ */ f(function(t) {
  Ce = t;
}, "setTodayMarker"), Oi = /* @__PURE__ */ f(function() {
  return Ce;
}, "getTodayMarker"), Ni = /* @__PURE__ */ f(function(t) {
  ct = t;
}, "setDateFormat"), Hi = /* @__PURE__ */ f(function() {
  Rt = !0;
}, "enableInclusiveEndDates"), Vi = /* @__PURE__ */ f(function() {
  return Rt;
}, "endDatesAreInclusive"), Pi = /* @__PURE__ */ f(function() {
  Fe = !0;
}, "enableTopAxis"), Ri = /* @__PURE__ */ f(function() {
  return Fe;
}, "topAxisEnabled"), zi = /* @__PURE__ */ f(function(t) {
  Me = t;
}, "setDisplayMode"), Bi = /* @__PURE__ */ f(function() {
  return Me;
}, "getDisplayMode"), qi = /* @__PURE__ */ f(function() {
  return ct;
}, "getDateFormat"), Zi = /* @__PURE__ */ f(function(t) {
  Vt = t.toLowerCase().split(/[\s,]+/);
}, "setIncludes"), Xi = /* @__PURE__ */ f(function() {
  return Vt;
}, "getIncludes"), ji = /* @__PURE__ */ f(function(t) {
  Pt = t.toLowerCase().split(/[\s,]+/);
}, "setExcludes"), Gi = /* @__PURE__ */ f(function() {
  return Pt;
}, "getExcludes"), Qi = /* @__PURE__ */ f(function() {
  return De;
}, "getLinks"), Ji = /* @__PURE__ */ f(function(t) {
  Et = t, _e.push(t);
}, "addSection"), Ki = /* @__PURE__ */ f(function() {
  return _e;
}, "getSections"), $i = /* @__PURE__ */ f(function() {
  let t = Xe();
  const e = 10;
  let n = 0;
  for (; !t && n < e; )
    t = Xe(), n++;
  return te = j, te;
}, "getTasks"), vn = /* @__PURE__ */ f(function(t, e, n, r) {
  const i = t.format(e.trim()), a = t.format("YYYY-MM-DD");
  return r.includes(i) || r.includes(a) ? !1 : n.includes("weekends") && (t.isoWeekday() === Ze[ee] || t.isoWeekday() === Ze[ee] + 1) || n.includes(t.format("dddd").toLowerCase()) ? !0 : n.includes(i) || n.includes(a);
}, "isInvalidDate"), ta = /* @__PURE__ */ f(function(t) {
  Ue = t;
}, "setWeekday"), ea = /* @__PURE__ */ f(function() {
  return Ue;
}, "getWeekday"), na = /* @__PURE__ */ f(function(t) {
  ee = t;
}, "setWeekend"), bn = /* @__PURE__ */ f(function(t, e, n, r) {
  if (!n.length || t.manualEndTime)
    return;
  let i;
  t.startTime instanceof Date ? i = tt(t.startTime) : i = tt(t.startTime, e, !0), i = i.add(1, "d");
  let a;
  t.endTime instanceof Date ? a = tt(t.endTime) : a = tt(t.endTime, e, !0);
  const [s, D] = ra(i, a, e, n, r);
  t.endTime = s.toDate(), t.renderEndTime = D;
}, "checkTaskDates"), ra = /* @__PURE__ */ f(function(t, e, n, r, i) {
  let a = !1, s = null;
  for (; t <= e; )
    a || (s = e.toDate()), a = vn(t, n, r, i), a && (e = e.add(1, "d")), t = t.add(1, "d");
  return [e, s];
}, "fixTaskDates"), pe = /* @__PURE__ */ f(function(t, e, n) {
  n = n.trim();
  const i = /^after\s+(?<ids>[\d\w- ]+)/.exec(n);
  if (i !== null) {
    let s = null;
    for (const S of i.groups.ids.split(" ")) {
      let k = Ct(S);
      k !== void 0 && (!s || k.endTime > s.endTime) && (s = k);
    }
    if (s)
      return s.endTime;
    const D = /* @__PURE__ */ new Date();
    return D.setHours(0, 0, 0, 0), D;
  }
  let a = tt(n, e.trim(), !0);
  if (a.isValid())
    return a.toDate();
  {
    Qt.debug("Invalid date:" + n), Qt.debug("With date format:" + e.trim());
    const s = new Date(n);
    if (s === void 0 || isNaN(s.getTime()) || // WebKit browsers can mis-parse invalid dates to be ridiculously
    // huge numbers, e.g. new Date('202304') gets parsed as January 1, 202304.
    // This can cause virtually infinite loops while rendering, so for the
    // purposes of Gantt charts we'll just treat any date beyond 10,000 AD/BC as
    // invalid.
    s.getFullYear() < -1e4 || s.getFullYear() > 1e4)
      throw new Error("Invalid date:" + n);
    return s;
  }
}, "getStartDate"), xn = /* @__PURE__ */ f(function(t) {
  const e = /^(\d+(?:\.\d+)?)([Mdhmswy]|ms)$/.exec(t.trim());
  return e !== null ? [Number.parseFloat(e[1]), e[2]] : [NaN, "ms"];
}, "parseDuration"), wn = /* @__PURE__ */ f(function(t, e, n, r = !1) {
  n = n.trim();
  const a = /^until\s+(?<ids>[\d\w- ]+)/.exec(n);
  if (a !== null) {
    let p = null;
    for (const x of a.groups.ids.split(" ")) {
      let y = Ct(x);
      y !== void 0 && (!p || y.startTime < p.startTime) && (p = y);
    }
    if (p)
      return p.startTime;
    const A = /* @__PURE__ */ new Date();
    return A.setHours(0, 0, 0, 0), A;
  }
  let s = tt(n, e.trim(), !0);
  if (s.isValid())
    return r && (s = s.add(1, "d")), s.toDate();
  let D = tt(t);
  const [S, k] = xn(n);
  if (!Number.isNaN(S)) {
    const p = D.add(S, k);
    p.isValid() && (D = p);
  }
  return D.toDate();
}, "getEndDate"), jt = 0, St = /* @__PURE__ */ f(function(t) {
  return t === void 0 ? (jt = jt + 1, "task" + jt) : t;
}, "parseId"), ia = /* @__PURE__ */ f(function(t, e) {
  let n;
  e.substr(0, 1) === ":" ? n = e.substr(1, e.length) : n = e;
  const r = n.split(","), i = {};
  Ee(r, i, Tn);
  for (let s = 0; s < r.length; s++)
    r[s] = r[s].trim();
  let a = "";
  switch (r.length) {
    case 1:
      i.id = St(), i.startTime = t.endTime, a = r[0];
      break;
    case 2:
      i.id = St(), i.startTime = pe(void 0, ct, r[0]), a = r[1];
      break;
    case 3:
      i.id = St(r[0]), i.startTime = pe(void 0, ct, r[1]), a = r[2];
      break;
  }
  return a && (i.endTime = wn(i.startTime, ct, a, Rt), i.manualEndTime = tt(a, "YYYY-MM-DD", !0).isValid(), bn(i, ct, Pt, Vt)), i;
}, "compileData"), aa = /* @__PURE__ */ f(function(t, e) {
  let n;
  e.substr(0, 1) === ":" ? n = e.substr(1, e.length) : n = e;
  const r = n.split(","), i = {};
  Ee(r, i, Tn);
  for (let a = 0; a < r.length; a++)
    r[a] = r[a].trim();
  switch (r.length) {
    case 1:
      i.id = St(), i.startTime = {
        type: "prevTaskEnd",
        id: t
      }, i.endTime = {
        data: r[0]
      };
      break;
    case 2:
      i.id = St(), i.startTime = {
        type: "getStartDate",
        startData: r[0]
      }, i.endTime = {
        data: r[1]
      };
      break;
    case 3:
      i.id = St(r[0]), i.startTime = {
        type: "getStartDate",
        startData: r[1]
      }, i.endTime = {
        data: r[2]
      };
      break;
  }
  return i;
}, "parseData"), Te, Gt, j = [], Cn = {}, sa = /* @__PURE__ */ f(function(t, e) {
  const n = {
    section: Et,
    type: Et,
    processed: !1,
    manualEndTime: !1,
    renderEndTime: null,
    raw: {
      data: e
    },
    task: t,
    classes: []
  }, r = aa(Gt, e);
  n.raw.startTime = r.startTime, n.raw.endTime = r.endTime, n.id = r.id, n.prevTaskId = Gt, n.active = r.active, n.done = r.done, n.crit = r.crit, n.milestone = r.milestone, n.vert = r.vert, n.order = ke, ke++;
  const i = j.push(n);
  Gt = n.id, Cn[n.id] = i - 1;
}, "addTask"), Ct = /* @__PURE__ */ f(function(t) {
  const e = Cn[t];
  return j[e];
}, "findTaskById"), oa = /* @__PURE__ */ f(function(t, e) {
  const n = {
    section: Et,
    type: Et,
    description: t,
    task: t,
    classes: []
  }, r = ia(Te, e);
  n.startTime = r.startTime, n.endTime = r.endTime, n.id = r.id, n.active = r.active, n.done = r.done, n.crit = r.crit, n.milestone = r.milestone, n.vert = r.vert, Te = n, te.push(n);
}, "addTaskOrg"), Xe = /* @__PURE__ */ f(function() {
  const t = /* @__PURE__ */ f(function(n) {
    const r = j[n];
    let i = "";
    switch (j[n].raw.startTime.type) {
      case "prevTaskEnd": {
        const a = Ct(r.prevTaskId);
        r.startTime = a.endTime;
        break;
      }
      case "getStartDate":
        i = pe(void 0, ct, j[n].raw.startTime.startData), i && (j[n].startTime = i);
        break;
    }
    return j[n].startTime && (j[n].endTime = wn(j[n].startTime, ct, j[n].raw.endTime.data, Rt), j[n].endTime && (j[n].processed = !0, j[n].manualEndTime = tt(j[n].raw.endTime.data, "YYYY-MM-DD", !0).isValid(), bn(j[n], ct, Pt, Vt))), j[n].processed;
  }, "compileTask");
  let e = !0;
  for (const [n, r] of j.entries())
    t(n), e = e && r.processed;
  return e;
}, "compileTasks"), ca = /* @__PURE__ */ f(function(t, e) {
  let n = e;
  _t().securityLevel !== "loose" && (n = On(e)), t.split(",").forEach(function(r) {
    Ct(r) !== void 0 && (_n(r, () => {
      window.open(n, "_self");
    }), De.set(r, n));
  }), Dn(t, "clickable");
}, "setLink"), Dn = /* @__PURE__ */ f(function(t, e) {
  t.split(",").forEach(function(n) {
    let r = Ct(n);
    r !== void 0 && r.classes.push(e);
  });
}, "setClass"), la = /* @__PURE__ */ f(function(t, e, n) {
  if (_t().securityLevel !== "loose" || e === void 0)
    return;
  let r = [];
  if (typeof n == "string") {
    r = n.split(/,(?=(?:(?:[^"]*"){2})*[^"]*$)/);
    for (let a = 0; a < r.length; a++) {
      let s = r[a].trim();
      s.startsWith('"') && s.endsWith('"') && (s = s.substr(1, s.length - 2)), r[a] = s;
    }
  }
  r.length === 0 && r.push(t), Ct(t) !== void 0 && _n(t, () => {
    Hn.runFunc(e, ...r);
  });
}, "setClickFun"), _n = /* @__PURE__ */ f(function(t, e) {
  Se.push(function() {
    const n = document.querySelector(`[id="${t}"]`);
    n !== null && n.addEventListener("click", function() {
      e();
    });
  }, function() {
    const n = document.querySelector(`[id="${t}-text"]`);
    n !== null && n.addEventListener("click", function() {
      e();
    });
  });
}, "pushFun"), ua = /* @__PURE__ */ f(function(t, e, n) {
  t.split(",").forEach(function(r) {
    la(r, e, n);
  }), Dn(t, "clickable");
}, "setClickEvent"), fa = /* @__PURE__ */ f(function(t) {
  Se.forEach(function(e) {
    e(t);
  });
}, "bindFunctions"), ha = {
  getConfig: /* @__PURE__ */ f(() => _t().gantt, "getConfig"),
  clear: Ei,
  setDateFormat: Ni,
  getDateFormat: qi,
  enableInclusiveEndDates: Hi,
  endDatesAreInclusive: Vi,
  enableTopAxis: Pi,
  topAxisEnabled: Ri,
  setAxisFormat: Ii,
  getAxisFormat: Ai,
  setTickInterval: Li,
  getTickInterval: Yi,
  setTodayMarker: Wi,
  getTodayMarker: Oi,
  setAccTitle: Ln,
  getAccTitle: An,
  setDiagramTitle: In,
  getDiagramTitle: En,
  setDisplayMode: zi,
  getDisplayMode: Bi,
  setAccDescription: Un,
  getAccDescription: Fn,
  addSection: Ji,
  getSections: Ki,
  getTasks: $i,
  addTask: sa,
  findTaskById: Ct,
  addTaskOrg: oa,
  setIncludes: Zi,
  getIncludes: Xi,
  setExcludes: ji,
  getExcludes: Gi,
  setClickEvent: ua,
  setLink: ca,
  getLinks: Qi,
  bindFunctions: fa,
  parseDuration: xn,
  isInvalidDate: vn,
  setWeekday: ta,
  getWeekday: ea,
  setWeekend: na
};
function Ee(t, e, n) {
  let r = !0;
  for (; r; )
    r = !1, n.forEach(function(i) {
      const a = "^\\s*" + i + "\\s*$", s = new RegExp(a);
      t[0].match(s) && (e[i] = !0, t.shift(1), r = !0);
    });
}
f(Ee, "getTaskTags");
var da = /* @__PURE__ */ f(function() {
  Qt.debug("Something is calling, setConf, remove the call");
}, "setConf"), je = {
  monday: Ot,
  tuesday: cn,
  wednesday: ln,
  thursday: vt,
  friday: un,
  saturday: fn,
  sunday: Ht
}, ma = /* @__PURE__ */ f((t, e) => {
  let n = [...t].map(() => -1 / 0), r = [...t].sort((a, s) => a.startTime - s.startTime || a.order - s.order), i = 0;
  for (const a of r)
    for (let s = 0; s < n.length; s++)
      if (a.startTime >= n[s]) {
        n[s] = a.endTime, a.order = s + e, s > i && (i = s);
        break;
      }
  return i;
}, "getMaxIntersections"), ht, ga = /* @__PURE__ */ f(function(t, e, n, r) {
  const i = _t().gantt, a = _t().securityLevel;
  let s;
  a === "sandbox" && (s = qt("#i" + e));
  const D = a === "sandbox" ? qt(s.nodes()[0].contentDocument.body) : qt("body"), S = a === "sandbox" ? s.nodes()[0].contentDocument : document, k = S.getElementById(e);
  ht = k.parentElement.offsetWidth, ht === void 0 && (ht = 1200), i.useWidth !== void 0 && (ht = i.useWidth);
  const p = r.db.getTasks();
  let A = [];
  for (const C of p)
    A.push(C.type);
  A = N(A);
  const x = {};
  let y = 2 * i.topPadding;
  if (r.db.getDisplayMode() === "compact" || i.displayMode === "compact") {
    const C = {};
    for (const _ of p)
      C[_.section] === void 0 ? C[_.section] = [_] : C[_.section].push(_);
    let U = 0;
    for (const _ of Object.keys(C)) {
      const M = ma(C[_], U) + 1;
      U += M, y += M * (i.barHeight + i.barGap), x[_] = M;
    }
  } else {
    y += p.length * (i.barHeight + i.barGap);
    for (const C of A)
      x[C] = p.filter((U) => U.type === C).length;
  }
  k.setAttribute("viewBox", "0 0 " + ht + " " + y);
  const R = D.select(`[id="${e}"]`), I = Mi().domain([Qn(p, function(C) {
    return C.startTime;
  }), Gn(p, function(C) {
    return C.endTime;
  })]).rangeRound([0, ht - i.leftPadding - i.rightPadding]);
  function et(C, U) {
    const _ = C.startTime, M = U.startTime;
    let b = 0;
    return _ > M ? b = 1 : _ < M && (b = -1), b;
  }
  f(et, "taskCompare"), p.sort(et), rt(p, ht, y), Yn(R, y, ht, i.useMaxWidth), R.append("text").text(r.db.getDiagramTitle()).attr("x", ht / 2).attr("y", i.titleTopMargin).attr("class", "titleText");
  function rt(C, U, _) {
    const M = i.barHeight, b = M + i.barGap, L = i.topPadding, h = i.leftPadding, m = Xn().domain([0, A.length]).range(["#00B9FA", "#F95002"]).interpolate(fr);
    Z(b, L, h, U, _, C, r.db.getExcludes(), r.db.getIncludes()), X(h, L, U, _), nt(C, b, L, h, M, m, U), $(b, L), w(h, L, U, _);
  }
  f(rt, "makeGantt");
  function nt(C, U, _, M, b, L, h) {
    C.sort((l, o) => l.vert === o.vert ? 0 : l.vert ? 1 : -1);
    const T = [...new Set(C.map((l) => l.order))].map((l) => C.find((o) => o.order === l));
    R.append("g").selectAll("rect").data(T).enter().append("rect").attr("x", 0).attr("y", function(l, o) {
      return o = l.order, o * U + _ - 2;
    }).attr("width", function() {
      return h - i.rightPadding / 2;
    }).attr("height", U).attr("class", function(l) {
      for (const [o, V] of A.entries())
        if (l.type === V)
          return "section section" + o % i.numberSectionStyles;
      return "section section0";
    }).enter();
    const d = R.append("g").selectAll("rect").data(C).enter(), v = r.db.getLinks();
    if (d.append("rect").attr("id", function(l) {
      return l.id;
    }).attr("rx", 3).attr("ry", 3).attr("x", function(l) {
      return l.milestone ? I(l.startTime) + M + 0.5 * (I(l.endTime) - I(l.startTime)) - 0.5 * b : I(l.startTime) + M;
    }).attr("y", function(l, o) {
      return o = l.order, l.vert ? i.gridLineStartPadding : o * U + _;
    }).attr("width", function(l) {
      return l.milestone ? b : l.vert ? 0.08 * b : I(l.renderEndTime || l.endTime) - I(l.startTime);
    }).attr("height", function(l) {
      return l.vert ? p.length * (i.barHeight + i.barGap) + i.barHeight * 2 : b;
    }).attr("transform-origin", function(l, o) {
      return o = l.order, (I(l.startTime) + M + 0.5 * (I(l.endTime) - I(l.startTime))).toString() + "px " + (o * U + _ + 0.5 * b).toString() + "px";
    }).attr("class", function(l) {
      const o = "task";
      let V = "";
      l.classes.length > 0 && (V = l.classes.join(" "));
      let W = 0;
      for (const [Q, z] of A.entries())
        l.type === z && (W = Q % i.numberSectionStyles);
      let H = "";
      return l.active ? l.crit ? H += " activeCrit" : H = " active" : l.done ? l.crit ? H = " doneCrit" : H = " done" : l.crit && (H += " crit"), H.length === 0 && (H = " task"), l.milestone && (H = " milestone " + H), l.vert && (H = " vert " + H), H += W, H += " " + V, o + H;
    }), d.append("text").attr("id", function(l) {
      return l.id + "-text";
    }).text(function(l) {
      return l.task;
    }).attr("font-size", i.fontSize).attr("x", function(l) {
      let o = I(l.startTime), V = I(l.renderEndTime || l.endTime);
      if (l.milestone && (o += 0.5 * (I(l.endTime) - I(l.startTime)) - 0.5 * b, V = o + b), l.vert)
        return I(l.startTime) + M;
      const W = this.getBBox().width;
      return W > V - o ? V + W + 1.5 * i.leftPadding > h ? o + M - 5 : V + M + 5 : (V - o) / 2 + o + M;
    }).attr("y", function(l, o) {
      return l.vert ? i.gridLineStartPadding + p.length * (i.barHeight + i.barGap) + 60 : (o = l.order, o * U + i.barHeight / 2 + (i.fontSize / 2 - 2) + _);
    }).attr("text-height", b).attr("class", function(l) {
      const o = I(l.startTime);
      let V = I(l.endTime);
      l.milestone && (V = o + b);
      const W = this.getBBox().width;
      let H = "";
      l.classes.length > 0 && (H = l.classes.join(" "));
      let Q = 0;
      for (const [B, st] of A.entries())
        l.type === st && (Q = B % i.numberSectionStyles);
      let z = "";
      return l.active && (l.crit ? z = "activeCritText" + Q : z = "activeText" + Q), l.done ? l.crit ? z = z + " doneCritText" + Q : z = z + " doneText" + Q : l.crit && (z = z + " critText" + Q), l.milestone && (z += " milestoneText"), l.vert && (z += " vertText"), W > V - o ? V + W + 1.5 * i.leftPadding > h ? H + " taskTextOutsideLeft taskTextOutside" + Q + " " + z : H + " taskTextOutsideRight taskTextOutside" + Q + " " + z + " width-" + W : H + " taskText taskText" + Q + " " + z + " width-" + W;
    }), _t().securityLevel === "sandbox") {
      let l;
      l = qt("#i" + e);
      const o = l.nodes()[0].contentDocument;
      d.filter(function(V) {
        return v.has(V.id);
      }).each(function(V) {
        var W = o.querySelector("#" + V.id), H = o.querySelector("#" + V.id + "-text");
        const Q = W.parentNode;
        var z = o.createElement("a");
        z.setAttribute("xlink:href", v.get(V.id)), z.setAttribute("target", "_top"), Q.appendChild(z), z.appendChild(W), z.appendChild(H);
      });
    }
  }
  f(nt, "drawRects");
  function Z(C, U, _, M, b, L, h, m) {
    if (h.length === 0 && m.length === 0)
      return;
    let T, d;
    for (const {
      startTime: W,
      endTime: H
    } of L)
      (T === void 0 || W < T) && (T = W), (d === void 0 || H > d) && (d = H);
    if (!T || !d)
      return;
    if (tt(d).diff(tt(T), "year") > 5) {
      Qt.warn("The difference between the min and max time is more than 5 years. This will cause performance issues. Skipping drawing exclude days.");
      return;
    }
    const v = r.db.getDateFormat(), c = [];
    let l = null, o = tt(T);
    for (; o.valueOf() <= d; )
      r.db.isInvalidDate(o, v, h, m) ? l ? l.end = o : l = {
        start: o,
        end: o
      } : l && (c.push(l), l = null), o = o.add(1, "d");
    R.append("g").selectAll("rect").data(c).enter().append("rect").attr("id", (W) => "exclude-" + W.start.format("YYYY-MM-DD")).attr("x", (W) => I(W.start.startOf("day")) + _).attr("y", i.gridLineStartPadding).attr("width", (W) => I(W.end.endOf("day")) - I(W.start.startOf("day"))).attr("height", b - U - i.gridLineStartPadding).attr("transform-origin", function(W, H) {
      return (I(W.start) + _ + 0.5 * (I(W.end) - I(W.start))).toString() + "px " + (H * C + 0.5 * b).toString() + "px";
    }).attr("class", "exclude-range");
  }
  f(Z, "drawExcludeDays");
  function X(C, U, _, M) {
    const b = r.db.getDateFormat(), L = r.db.getAxisFormat();
    let h;
    L ? h = L : b === "D" ? h = "%d" : h = i.axisFormat ?? "%Y-%m-%d";
    let m = ir(I).tickSize(-M + U + i.gridLineStartPadding).tickFormat($t(h));
    const d = /^([1-9]\d*)(millisecond|second|minute|hour|day|week|month)$/.exec(r.db.getTickInterval() || i.tickInterval);
    if (d !== null) {
      const v = d[1], c = d[2], l = r.db.getWeekday() || i.weekday;
      switch (c) {
        case "millisecond":
          m.ticks(Ft.every(v));
          break;
        case "second":
          m.ticks(pt.every(v));
          break;
        case "minute":
          m.ticks(Yt.every(v));
          break;
        case "hour":
          m.ticks(Wt.every(v));
          break;
        case "day":
          m.ticks(Tt.every(v));
          break;
        case "week":
          m.ticks(je[l].every(v));
          break;
        case "month":
          m.ticks(Nt.every(v));
          break;
      }
    }
    if (R.append("g").attr("class", "grid").attr("transform", "translate(" + C + ", " + (M - 50) + ")").call(m).selectAll("text").style("text-anchor", "middle").attr("fill", "#000").attr("stroke", "none").attr("font-size", 10).attr("dy", "1em"), r.db.topAxisEnabled() || i.topAxis) {
      let v = rr(I).tickSize(-M + U + i.gridLineStartPadding).tickFormat($t(h));
      if (d !== null) {
        const c = d[1], l = d[2], o = r.db.getWeekday() || i.weekday;
        switch (l) {
          case "millisecond":
            v.ticks(Ft.every(c));
            break;
          case "second":
            v.ticks(pt.every(c));
            break;
          case "minute":
            v.ticks(Yt.every(c));
            break;
          case "hour":
            v.ticks(Wt.every(c));
            break;
          case "day":
            v.ticks(Tt.every(c));
            break;
          case "week":
            v.ticks(je[o].every(c));
            break;
          case "month":
            v.ticks(Nt.every(c));
            break;
        }
      }
      R.append("g").attr("class", "grid").attr("transform", "translate(" + C + ", " + U + ")").call(v).selectAll("text").style("text-anchor", "middle").attr("fill", "#000").attr("stroke", "none").attr("font-size", 10);
    }
  }
  f(X, "makeGrid");
  function $(C, U) {
    let _ = 0;
    const M = Object.keys(x).map((b) => [b, x[b]]);
    R.append("g").selectAll("text").data(M).enter().append(function(b) {
      const L = b[0].split(Wn.lineBreakRegex), h = -(L.length - 1) / 2, m = S.createElementNS("http://www.w3.org/2000/svg", "text");
      m.setAttribute("dy", h + "em");
      for (const [T, d] of L.entries()) {
        const v = S.createElementNS("http://www.w3.org/2000/svg", "tspan");
        v.setAttribute("alignment-baseline", "central"), v.setAttribute("x", "10"), T > 0 && v.setAttribute("dy", "1em"), v.textContent = d, m.appendChild(v);
      }
      return m;
    }).attr("x", 10).attr("y", function(b, L) {
      if (L > 0)
        for (let h = 0; h < L; h++)
          return _ += M[L - 1][1], b[1] * C / 2 + _ * C + U;
      else
        return b[1] * C / 2 + U;
    }).attr("font-size", i.sectionFontSize).attr("class", function(b) {
      for (const [L, h] of A.entries())
        if (b[0] === h)
          return "sectionTitle sectionTitle" + L % i.numberSectionStyles;
      return "sectionTitle";
    });
  }
  f($, "vertLabels");
  function w(C, U, _, M) {
    const b = r.db.getTodayMarker();
    if (b === "off")
      return;
    const L = R.append("g").attr("class", "today"), h = /* @__PURE__ */ new Date(), m = L.append("line");
    m.attr("x1", I(h) + C).attr("x2", I(h) + C).attr("y1", i.titleTopMargin).attr("y2", M - i.titleTopMargin).attr("class", "today"), b !== "" && m.attr("style", b.replace(/,/g, ";"));
  }
  f(w, "drawToday");
  function N(C) {
    const U = {}, _ = [];
    for (let M = 0, b = C.length; M < b; ++M)
      Object.prototype.hasOwnProperty.call(U, C[M]) || (U[C[M]] = !0, _.push(C[M]));
    return _;
  }
  f(N, "checkUnique");
}, "draw"), ya = {
  setConf: da,
  draw: ga
}, ka = /* @__PURE__ */ f((t) => `
  .mermaid-main-font {
        font-family: ${t.fontFamily};
  }

  .exclude-range {
    fill: ${t.excludeBkgColor};
  }

  .section {
    stroke: none;
    opacity: 0.2;
  }

  .section0 {
    fill: ${t.sectionBkgColor};
  }

  .section2 {
    fill: ${t.sectionBkgColor2};
  }

  .section1,
  .section3 {
    fill: ${t.altSectionBkgColor};
    opacity: 0.2;
  }

  .sectionTitle0 {
    fill: ${t.titleColor};
  }

  .sectionTitle1 {
    fill: ${t.titleColor};
  }

  .sectionTitle2 {
    fill: ${t.titleColor};
  }

  .sectionTitle3 {
    fill: ${t.titleColor};
  }

  .sectionTitle {
    text-anchor: start;
    font-family: ${t.fontFamily};
  }


  /* Grid and axis */

  .grid .tick {
    stroke: ${t.gridColor};
    opacity: 0.8;
    shape-rendering: crispEdges;
  }

  .grid .tick text {
    font-family: ${t.fontFamily};
    fill: ${t.textColor};
  }

  .grid path {
    stroke-width: 0;
  }


  /* Today line */

  .today {
    fill: none;
    stroke: ${t.todayLineColor};
    stroke-width: 2px;
  }


  /* Task styling */

  /* Default task */

  .task {
    stroke-width: 2;
  }

  .taskText {
    text-anchor: middle;
    font-family: ${t.fontFamily};
  }

  .taskTextOutsideRight {
    fill: ${t.taskTextDarkColor};
    text-anchor: start;
    font-family: ${t.fontFamily};
  }

  .taskTextOutsideLeft {
    fill: ${t.taskTextDarkColor};
    text-anchor: end;
  }


  /* Special case clickable */

  .task.clickable {
    cursor: pointer;
  }

  .taskText.clickable {
    cursor: pointer;
    fill: ${t.taskTextClickableColor} !important;
    font-weight: bold;
  }

  .taskTextOutsideLeft.clickable {
    cursor: pointer;
    fill: ${t.taskTextClickableColor} !important;
    font-weight: bold;
  }

  .taskTextOutsideRight.clickable {
    cursor: pointer;
    fill: ${t.taskTextClickableColor} !important;
    font-weight: bold;
  }


  /* Specific task settings for the sections*/

  .taskText0,
  .taskText1,
  .taskText2,
  .taskText3 {
    fill: ${t.taskTextColor};
  }

  .task0,
  .task1,
  .task2,
  .task3 {
    fill: ${t.taskBkgColor};
    stroke: ${t.taskBorderColor};
  }

  .taskTextOutside0,
  .taskTextOutside2
  {
    fill: ${t.taskTextOutsideColor};
  }

  .taskTextOutside1,
  .taskTextOutside3 {
    fill: ${t.taskTextOutsideColor};
  }


  /* Active task */

  .active0,
  .active1,
  .active2,
  .active3 {
    fill: ${t.activeTaskBkgColor};
    stroke: ${t.activeTaskBorderColor};
  }

  .activeText0,
  .activeText1,
  .activeText2,
  .activeText3 {
    fill: ${t.taskTextDarkColor} !important;
  }


  /* Completed task */

  .done0,
  .done1,
  .done2,
  .done3 {
    stroke: ${t.doneTaskBorderColor};
    fill: ${t.doneTaskBkgColor};
    stroke-width: 2;
  }

  .doneText0,
  .doneText1,
  .doneText2,
  .doneText3 {
    fill: ${t.taskTextDarkColor} !important;
  }


  /* Tasks on the critical line */

  .crit0,
  .crit1,
  .crit2,
  .crit3 {
    stroke: ${t.critBorderColor};
    fill: ${t.critBkgColor};
    stroke-width: 2;
  }

  .activeCrit0,
  .activeCrit1,
  .activeCrit2,
  .activeCrit3 {
    stroke: ${t.critBorderColor};
    fill: ${t.activeTaskBkgColor};
    stroke-width: 2;
  }

  .doneCrit0,
  .doneCrit1,
  .doneCrit2,
  .doneCrit3 {
    stroke: ${t.critBorderColor};
    fill: ${t.doneTaskBkgColor};
    stroke-width: 2;
    cursor: pointer;
    shape-rendering: crispEdges;
  }

  .milestone {
    transform: rotate(45deg) scale(0.8,0.8);
  }

  .milestoneText {
    font-style: italic;
  }
  .doneCritText0,
  .doneCritText1,
  .doneCritText2,
  .doneCritText3 {
    fill: ${t.taskTextDarkColor} !important;
  }

  .vert {
    stroke: ${t.vertLineColor};
  }

  .vertText {
    font-size: 15px;
    text-anchor: middle;
    fill: ${t.vertLineColor} !important;
  }

  .activeCritText0,
  .activeCritText1,
  .activeCritText2,
  .activeCritText3 {
    fill: ${t.taskTextDarkColor} !important;
  }

  .titleText {
    text-anchor: middle;
    font-size: 18px;
    fill: ${t.titleColor || t.textColor};
    font-family: ${t.fontFamily};
  }
`, "getStyles"), pa = ka, wa = {
  parser: Ui,
  db: ha,
  renderer: ya,
  styles: pa
};
export {
  wa as diagram
};
