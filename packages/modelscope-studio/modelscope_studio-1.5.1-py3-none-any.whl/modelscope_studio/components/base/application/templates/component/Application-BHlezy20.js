import { g as ht, E as C, Z as ge, F as xe, G as _e } from "./Index-HF_NH3zS.js";
var ut = function(t) {
  return lt(t) && !ft(t);
};
function lt(e) {
  return !!e && typeof e == "object";
}
function ft(e) {
  var t = Object.prototype.toString.call(e);
  return t === "[object RegExp]" || t === "[object Date]" || pt(e);
}
var ct = typeof Symbol == "function" && Symbol.for, mt = ct ? Symbol.for("react.element") : 60103;
function pt(e) {
  return e.$$typeof === mt;
}
function bt(e) {
  return Array.isArray(e) ? [] : {};
}
function G(e, t) {
  return t.clone !== !1 && t.isMergeableObject(e) ? N(bt(e), e, t) : e;
}
function gt(e, t, r) {
  return e.concat(t).map(function(n) {
    return G(n, r);
  });
}
function Et(e, t) {
  if (!t.customMerge)
    return N;
  var r = t.customMerge(e);
  return typeof r == "function" ? r : N;
}
function dt(e) {
  return Object.getOwnPropertySymbols ? Object.getOwnPropertySymbols(e).filter(function(t) {
    return Object.propertyIsEnumerable.call(e, t);
  }) : [];
}
function ye(e) {
  return Object.keys(e).concat(dt(e));
}
function Ge(e, t) {
  try {
    return t in e;
  } catch {
    return !1;
  }
}
function vt(e, t) {
  return Ge(e, t) && !(Object.hasOwnProperty.call(e, t) && Object.propertyIsEnumerable.call(e, t));
}
function xt(e, t, r) {
  var n = {};
  return r.isMergeableObject(e) && ye(e).forEach(function(i) {
    n[i] = G(e[i], r);
  }), ye(t).forEach(function(i) {
    vt(e, i) || (Ge(e, i) && r.isMergeableObject(t[i]) ? n[i] = Et(i, r)(e[i], t[i], r) : n[i] = G(t[i], r));
  }), n;
}
function N(e, t, r) {
  r = r || {}, r.arrayMerge = r.arrayMerge || gt, r.isMergeableObject = r.isMergeableObject || ut, r.cloneUnlessOtherwiseSpecified = G;
  var n = Array.isArray(t), i = Array.isArray(e), a = n === i;
  return a ? n ? r.arrayMerge(e, t, r) : xt(e, t, r) : G(t, r);
}
N.all = function(t, r) {
  if (!Array.isArray(t))
    throw new Error("first argument should be an array");
  return t.reduce(function(n, i) {
    return N(n, i, r);
  }, {});
};
var _t = N, yt = _t;
const Ht = /* @__PURE__ */ ht(yt);
var ae = function(e, t) {
  return ae = Object.setPrototypeOf || {
    __proto__: []
  } instanceof Array && function(r, n) {
    r.__proto__ = n;
  } || function(r, n) {
    for (var i in n) Object.prototype.hasOwnProperty.call(n, i) && (r[i] = n[i]);
  }, ae(e, t);
};
function J(e, t) {
  if (typeof t != "function" && t !== null) throw new TypeError("Class extends value " + String(t) + " is not a constructor or null");
  ae(e, t);
  function r() {
    this.constructor = e;
  }
  e.prototype = t === null ? Object.create(t) : (r.prototype = t.prototype, new r());
}
var b = function() {
  return b = Object.assign || function(t) {
    for (var r, n = 1, i = arguments.length; n < i; n++) {
      r = arguments[n];
      for (var a in r) Object.prototype.hasOwnProperty.call(r, a) && (t[a] = r[a]);
    }
    return t;
  }, b.apply(this, arguments);
};
function Tt(e, t) {
  var r = {};
  for (var n in e) Object.prototype.hasOwnProperty.call(e, n) && t.indexOf(n) < 0 && (r[n] = e[n]);
  if (e != null && typeof Object.getOwnPropertySymbols == "function") for (var i = 0, n = Object.getOwnPropertySymbols(e); i < n.length; i++)
    t.indexOf(n[i]) < 0 && Object.prototype.propertyIsEnumerable.call(e, n[i]) && (r[n[i]] = e[n[i]]);
  return r;
}
function K(e, t, r) {
  if (r || arguments.length === 2) for (var n = 0, i = t.length, a; n < i; n++)
    (a || !(n in t)) && (a || (a = Array.prototype.slice.call(t, 0, n)), a[n] = t[n]);
  return e.concat(a || Array.prototype.slice.call(t));
}
function ee(e, t) {
  var r = t && t.cache ? t.cache : Ot, n = t && t.serializer ? t.serializer : It, i = t && t.strategy ? t.strategy : At;
  return i(e, {
    cache: r,
    serializer: n
  });
}
function Bt(e) {
  return e == null || typeof e == "number" || typeof e == "boolean";
}
function St(e, t, r, n) {
  var i = Bt(n) ? n : r(n), a = t.get(i);
  return typeof a > "u" && (a = e.call(this, n), t.set(i, a)), a;
}
function De(e, t, r) {
  var n = Array.prototype.slice.call(arguments, 3), i = r(n), a = t.get(i);
  return typeof a > "u" && (a = e.apply(this, n), t.set(i, a)), a;
}
function Fe(e, t, r, n, i) {
  return r.bind(t, e, n, i);
}
function At(e, t) {
  var r = e.length === 1 ? St : De;
  return Fe(e, this, r, t.cache.create(), t.serializer);
}
function Pt(e, t) {
  return Fe(e, this, De, t.cache.create(), t.serializer);
}
var It = function() {
  return JSON.stringify(arguments);
}, Nt = (
  /** @class */
  function() {
    function e() {
      this.cache = /* @__PURE__ */ Object.create(null);
    }
    return e.prototype.get = function(t) {
      return this.cache[t];
    }, e.prototype.set = function(t, r) {
      this.cache[t] = r;
    }, e;
  }()
), Ot = {
  create: function() {
    return new Nt();
  }
}, te = {
  variadic: Pt
}, m;
(function(e) {
  e[e.EXPECT_ARGUMENT_CLOSING_BRACE = 1] = "EXPECT_ARGUMENT_CLOSING_BRACE", e[e.EMPTY_ARGUMENT = 2] = "EMPTY_ARGUMENT", e[e.MALFORMED_ARGUMENT = 3] = "MALFORMED_ARGUMENT", e[e.EXPECT_ARGUMENT_TYPE = 4] = "EXPECT_ARGUMENT_TYPE", e[e.INVALID_ARGUMENT_TYPE = 5] = "INVALID_ARGUMENT_TYPE", e[e.EXPECT_ARGUMENT_STYLE = 6] = "EXPECT_ARGUMENT_STYLE", e[e.INVALID_NUMBER_SKELETON = 7] = "INVALID_NUMBER_SKELETON", e[e.INVALID_DATE_TIME_SKELETON = 8] = "INVALID_DATE_TIME_SKELETON", e[e.EXPECT_NUMBER_SKELETON = 9] = "EXPECT_NUMBER_SKELETON", e[e.EXPECT_DATE_TIME_SKELETON = 10] = "EXPECT_DATE_TIME_SKELETON", e[e.UNCLOSED_QUOTE_IN_ARGUMENT_STYLE = 11] = "UNCLOSED_QUOTE_IN_ARGUMENT_STYLE", e[e.EXPECT_SELECT_ARGUMENT_OPTIONS = 12] = "EXPECT_SELECT_ARGUMENT_OPTIONS", e[e.EXPECT_PLURAL_ARGUMENT_OFFSET_VALUE = 13] = "EXPECT_PLURAL_ARGUMENT_OFFSET_VALUE", e[e.INVALID_PLURAL_ARGUMENT_OFFSET_VALUE = 14] = "INVALID_PLURAL_ARGUMENT_OFFSET_VALUE", e[e.EXPECT_SELECT_ARGUMENT_SELECTOR = 15] = "EXPECT_SELECT_ARGUMENT_SELECTOR", e[e.EXPECT_PLURAL_ARGUMENT_SELECTOR = 16] = "EXPECT_PLURAL_ARGUMENT_SELECTOR", e[e.EXPECT_SELECT_ARGUMENT_SELECTOR_FRAGMENT = 17] = "EXPECT_SELECT_ARGUMENT_SELECTOR_FRAGMENT", e[e.EXPECT_PLURAL_ARGUMENT_SELECTOR_FRAGMENT = 18] = "EXPECT_PLURAL_ARGUMENT_SELECTOR_FRAGMENT", e[e.INVALID_PLURAL_ARGUMENT_SELECTOR = 19] = "INVALID_PLURAL_ARGUMENT_SELECTOR", e[e.DUPLICATE_PLURAL_ARGUMENT_SELECTOR = 20] = "DUPLICATE_PLURAL_ARGUMENT_SELECTOR", e[e.DUPLICATE_SELECT_ARGUMENT_SELECTOR = 21] = "DUPLICATE_SELECT_ARGUMENT_SELECTOR", e[e.MISSING_OTHER_CLAUSE = 22] = "MISSING_OTHER_CLAUSE", e[e.INVALID_TAG = 23] = "INVALID_TAG", e[e.INVALID_TAG_NAME = 25] = "INVALID_TAG_NAME", e[e.UNMATCHED_CLOSING_TAG = 26] = "UNMATCHED_CLOSING_TAG", e[e.UNCLOSED_TAG = 27] = "UNCLOSED_TAG";
})(m || (m = {}));
var d;
(function(e) {
  e[e.literal = 0] = "literal", e[e.argument = 1] = "argument", e[e.number = 2] = "number", e[e.date = 3] = "date", e[e.time = 4] = "time", e[e.select = 5] = "select", e[e.plural = 6] = "plural", e[e.pound = 7] = "pound", e[e.tag = 8] = "tag";
})(d || (d = {}));
var O;
(function(e) {
  e[e.number = 0] = "number", e[e.dateTime = 1] = "dateTime";
})(O || (O = {}));
function He(e) {
  return e.type === d.literal;
}
function wt(e) {
  return e.type === d.argument;
}
function je(e) {
  return e.type === d.number;
}
function Ve(e) {
  return e.type === d.date;
}
function Xe(e) {
  return e.type === d.time;
}
function ke(e) {
  return e.type === d.select;
}
function We(e) {
  return e.type === d.plural;
}
function Lt(e) {
  return e.type === d.pound;
}
function ze(e) {
  return e.type === d.tag;
}
function Ze(e) {
  return !!(e && typeof e == "object" && e.type === O.number);
}
function se(e) {
  return !!(e && typeof e == "object" && e.type === O.dateTime);
}
var Qe = /[ \xA0\u1680\u2000-\u200A\u202F\u205F\u3000]/, Ct = /(?:[Eec]{1,6}|G{1,5}|[Qq]{1,5}|(?:[yYur]+|U{1,5})|[ML]{1,5}|d{1,2}|D{1,3}|F{1}|[abB]{1,5}|[hkHK]{1,2}|w{1,2}|W{1}|m{1,2}|s{1,2}|[zZOvVxX]{1,4})(?=([^']*'[^']*')*[^']*$)/g;
function Mt(e) {
  var t = {};
  return e.replace(Ct, function(r) {
    var n = r.length;
    switch (r[0]) {
      case "G":
        t.era = n === 4 ? "long" : n === 5 ? "narrow" : "short";
        break;
      case "y":
        t.year = n === 2 ? "2-digit" : "numeric";
        break;
      case "Y":
      case "u":
      case "U":
      case "r":
        throw new RangeError("`Y/u/U/r` (year) patterns are not supported, use `y` instead");
      case "q":
      case "Q":
        throw new RangeError("`q/Q` (quarter) patterns are not supported");
      case "M":
      case "L":
        t.month = ["numeric", "2-digit", "short", "long", "narrow"][n - 1];
        break;
      case "w":
      case "W":
        throw new RangeError("`w/W` (week) patterns are not supported");
      case "d":
        t.day = ["numeric", "2-digit"][n - 1];
        break;
      case "D":
      case "F":
      case "g":
        throw new RangeError("`D/F/g` (day) patterns are not supported, use `d` instead");
      case "E":
        t.weekday = n === 4 ? "long" : n === 5 ? "narrow" : "short";
        break;
      case "e":
        if (n < 4)
          throw new RangeError("`e..eee` (weekday) patterns are not supported");
        t.weekday = ["short", "long", "narrow", "short"][n - 4];
        break;
      case "c":
        if (n < 4)
          throw new RangeError("`c..ccc` (weekday) patterns are not supported");
        t.weekday = ["short", "long", "narrow", "short"][n - 4];
        break;
      case "a":
        t.hour12 = !0;
        break;
      case "b":
      case "B":
        throw new RangeError("`b/B` (period) patterns are not supported, use `a` instead");
      case "h":
        t.hourCycle = "h12", t.hour = ["numeric", "2-digit"][n - 1];
        break;
      case "H":
        t.hourCycle = "h23", t.hour = ["numeric", "2-digit"][n - 1];
        break;
      case "K":
        t.hourCycle = "h11", t.hour = ["numeric", "2-digit"][n - 1];
        break;
      case "k":
        t.hourCycle = "h24", t.hour = ["numeric", "2-digit"][n - 1];
        break;
      case "j":
      case "J":
      case "C":
        throw new RangeError("`j/J/C` (hour) patterns are not supported, use `h/H/K/k` instead");
      case "m":
        t.minute = ["numeric", "2-digit"][n - 1];
        break;
      case "s":
        t.second = ["numeric", "2-digit"][n - 1];
        break;
      case "S":
      case "A":
        throw new RangeError("`S/A` (second) patterns are not supported, use `s` instead");
      case "z":
        t.timeZoneName = n < 4 ? "short" : "long";
        break;
      case "Z":
      case "O":
      case "v":
      case "V":
      case "X":
      case "x":
        throw new RangeError("`Z/O/v/V/X/x` (timeZone) patterns are not supported, use `z` instead");
    }
    return "";
  }), t;
}
var Rt = /[\t-\r \x85\u200E\u200F\u2028\u2029]/i;
function Ut(e) {
  if (e.length === 0)
    throw new Error("Number skeleton cannot be empty");
  for (var t = e.split(Rt).filter(function(f) {
    return f.length > 0;
  }), r = [], n = 0, i = t; n < i.length; n++) {
    var a = i[n], s = a.split("/");
    if (s.length === 0)
      throw new Error("Invalid number skeleton");
    for (var o = s[0], u = s.slice(1), l = 0, h = u; l < h.length; l++) {
      var c = h[l];
      if (c.length === 0)
        throw new Error("Invalid number skeleton");
    }
    r.push({
      stem: o,
      options: u
    });
  }
  return r;
}
function Gt(e) {
  return e.replace(/^(.*?)-/, "");
}
var Te = /^\.(?:(0+)(\*)?|(#+)|(0+)(#+))$/g, Je = /^(@+)?(\+|#+)?[rs]?$/g, Dt = /(\*)(0+)|(#+)(0+)|(0+)/g, qe = /^(0+)$/;
function Be(e) {
  var t = {};
  return e[e.length - 1] === "r" ? t.roundingPriority = "morePrecision" : e[e.length - 1] === "s" && (t.roundingPriority = "lessPrecision"), e.replace(Je, function(r, n, i) {
    return typeof i != "string" ? (t.minimumSignificantDigits = n.length, t.maximumSignificantDigits = n.length) : i === "+" ? t.minimumSignificantDigits = n.length : n[0] === "#" ? t.maximumSignificantDigits = n.length : (t.minimumSignificantDigits = n.length, t.maximumSignificantDigits = n.length + (typeof i == "string" ? i.length : 0)), "";
  }), t;
}
function Ye(e) {
  switch (e) {
    case "sign-auto":
      return {
        signDisplay: "auto"
      };
    case "sign-accounting":
    case "()":
      return {
        currencySign: "accounting"
      };
    case "sign-always":
    case "+!":
      return {
        signDisplay: "always"
      };
    case "sign-accounting-always":
    case "()!":
      return {
        signDisplay: "always",
        currencySign: "accounting"
      };
    case "sign-except-zero":
    case "+?":
      return {
        signDisplay: "exceptZero"
      };
    case "sign-accounting-except-zero":
    case "()?":
      return {
        signDisplay: "exceptZero",
        currencySign: "accounting"
      };
    case "sign-never":
    case "+_":
      return {
        signDisplay: "never"
      };
  }
}
function Ft(e) {
  var t;
  if (e[0] === "E" && e[1] === "E" ? (t = {
    notation: "engineering"
  }, e = e.slice(2)) : e[0] === "E" && (t = {
    notation: "scientific"
  }, e = e.slice(1)), t) {
    var r = e.slice(0, 2);
    if (r === "+!" ? (t.signDisplay = "always", e = e.slice(2)) : r === "+?" && (t.signDisplay = "exceptZero", e = e.slice(2)), !qe.test(e))
      throw new Error("Malformed concise eng/scientific notation");
    t.minimumIntegerDigits = e.length;
  }
  return t;
}
function Se(e) {
  var t = {}, r = Ye(e);
  return r || t;
}
function jt(e) {
  for (var t = {}, r = 0, n = e; r < n.length; r++) {
    var i = n[r];
    switch (i.stem) {
      case "percent":
      case "%":
        t.style = "percent";
        continue;
      case "%x100":
        t.style = "percent", t.scale = 100;
        continue;
      case "currency":
        t.style = "currency", t.currency = i.options[0];
        continue;
      case "group-off":
      case ",_":
        t.useGrouping = !1;
        continue;
      case "precision-integer":
      case ".":
        t.maximumFractionDigits = 0;
        continue;
      case "measure-unit":
      case "unit":
        t.style = "unit", t.unit = Gt(i.options[0]);
        continue;
      case "compact-short":
      case "K":
        t.notation = "compact", t.compactDisplay = "short";
        continue;
      case "compact-long":
      case "KK":
        t.notation = "compact", t.compactDisplay = "long";
        continue;
      case "scientific":
        t = b(b(b({}, t), {
          notation: "scientific"
        }), i.options.reduce(function(u, l) {
          return b(b({}, u), Se(l));
        }, {}));
        continue;
      case "engineering":
        t = b(b(b({}, t), {
          notation: "engineering"
        }), i.options.reduce(function(u, l) {
          return b(b({}, u), Se(l));
        }, {}));
        continue;
      case "notation-simple":
        t.notation = "standard";
        continue;
      case "unit-width-narrow":
        t.currencyDisplay = "narrowSymbol", t.unitDisplay = "narrow";
        continue;
      case "unit-width-short":
        t.currencyDisplay = "code", t.unitDisplay = "short";
        continue;
      case "unit-width-full-name":
        t.currencyDisplay = "name", t.unitDisplay = "long";
        continue;
      case "unit-width-iso-code":
        t.currencyDisplay = "symbol";
        continue;
      case "scale":
        t.scale = parseFloat(i.options[0]);
        continue;
      case "rounding-mode-floor":
        t.roundingMode = "floor";
        continue;
      case "rounding-mode-ceiling":
        t.roundingMode = "ceil";
        continue;
      case "rounding-mode-down":
        t.roundingMode = "trunc";
        continue;
      case "rounding-mode-up":
        t.roundingMode = "expand";
        continue;
      case "rounding-mode-half-even":
        t.roundingMode = "halfEven";
        continue;
      case "rounding-mode-half-down":
        t.roundingMode = "halfTrunc";
        continue;
      case "rounding-mode-half-up":
        t.roundingMode = "halfExpand";
        continue;
      case "integer-width":
        if (i.options.length > 1)
          throw new RangeError("integer-width stems only accept a single optional option");
        i.options[0].replace(Dt, function(u, l, h, c, f, E) {
          if (l)
            t.minimumIntegerDigits = h.length;
          else {
            if (c && f)
              throw new Error("We currently do not support maximum integer digits");
            if (E)
              throw new Error("We currently do not support exact integer digits");
          }
          return "";
        });
        continue;
    }
    if (qe.test(i.stem)) {
      t.minimumIntegerDigits = i.stem.length;
      continue;
    }
    if (Te.test(i.stem)) {
      if (i.options.length > 1)
        throw new RangeError("Fraction-precision stems only accept a single optional option");
      i.stem.replace(Te, function(u, l, h, c, f, E) {
        return h === "*" ? t.minimumFractionDigits = l.length : c && c[0] === "#" ? t.maximumFractionDigits = c.length : f && E ? (t.minimumFractionDigits = f.length, t.maximumFractionDigits = f.length + E.length) : (t.minimumFractionDigits = l.length, t.maximumFractionDigits = l.length), "";
      });
      var a = i.options[0];
      a === "w" ? t = b(b({}, t), {
        trailingZeroDisplay: "stripIfInteger"
      }) : a && (t = b(b({}, t), Be(a)));
      continue;
    }
    if (Je.test(i.stem)) {
      t = b(b({}, t), Be(i.stem));
      continue;
    }
    var s = Ye(i.stem);
    s && (t = b(b({}, t), s));
    var o = Ft(i.stem);
    o && (t = b(b({}, t), o));
  }
  return t;
}
var X = {
  "001": ["H", "h"],
  419: ["h", "H", "hB", "hb"],
  AC: ["H", "h", "hb", "hB"],
  AD: ["H", "hB"],
  AE: ["h", "hB", "hb", "H"],
  AF: ["H", "hb", "hB", "h"],
  AG: ["h", "hb", "H", "hB"],
  AI: ["H", "h", "hb", "hB"],
  AL: ["h", "H", "hB"],
  AM: ["H", "hB"],
  AO: ["H", "hB"],
  AR: ["h", "H", "hB", "hb"],
  AS: ["h", "H"],
  AT: ["H", "hB"],
  AU: ["h", "hb", "H", "hB"],
  AW: ["H", "hB"],
  AX: ["H"],
  AZ: ["H", "hB", "h"],
  BA: ["H", "hB", "h"],
  BB: ["h", "hb", "H", "hB"],
  BD: ["h", "hB", "H"],
  BE: ["H", "hB"],
  BF: ["H", "hB"],
  BG: ["H", "hB", "h"],
  BH: ["h", "hB", "hb", "H"],
  BI: ["H", "h"],
  BJ: ["H", "hB"],
  BL: ["H", "hB"],
  BM: ["h", "hb", "H", "hB"],
  BN: ["hb", "hB", "h", "H"],
  BO: ["h", "H", "hB", "hb"],
  BQ: ["H"],
  BR: ["H", "hB"],
  BS: ["h", "hb", "H", "hB"],
  BT: ["h", "H"],
  BW: ["H", "h", "hb", "hB"],
  BY: ["H", "h"],
  BZ: ["H", "h", "hb", "hB"],
  CA: ["h", "hb", "H", "hB"],
  CC: ["H", "h", "hb", "hB"],
  CD: ["hB", "H"],
  CF: ["H", "h", "hB"],
  CG: ["H", "hB"],
  CH: ["H", "hB", "h"],
  CI: ["H", "hB"],
  CK: ["H", "h", "hb", "hB"],
  CL: ["h", "H", "hB", "hb"],
  CM: ["H", "h", "hB"],
  CN: ["H", "hB", "hb", "h"],
  CO: ["h", "H", "hB", "hb"],
  CP: ["H"],
  CR: ["h", "H", "hB", "hb"],
  CU: ["h", "H", "hB", "hb"],
  CV: ["H", "hB"],
  CW: ["H", "hB"],
  CX: ["H", "h", "hb", "hB"],
  CY: ["h", "H", "hb", "hB"],
  CZ: ["H"],
  DE: ["H", "hB"],
  DG: ["H", "h", "hb", "hB"],
  DJ: ["h", "H"],
  DK: ["H"],
  DM: ["h", "hb", "H", "hB"],
  DO: ["h", "H", "hB", "hb"],
  DZ: ["h", "hB", "hb", "H"],
  EA: ["H", "h", "hB", "hb"],
  EC: ["h", "H", "hB", "hb"],
  EE: ["H", "hB"],
  EG: ["h", "hB", "hb", "H"],
  EH: ["h", "hB", "hb", "H"],
  ER: ["h", "H"],
  ES: ["H", "hB", "h", "hb"],
  ET: ["hB", "hb", "h", "H"],
  FI: ["H"],
  FJ: ["h", "hb", "H", "hB"],
  FK: ["H", "h", "hb", "hB"],
  FM: ["h", "hb", "H", "hB"],
  FO: ["H", "h"],
  FR: ["H", "hB"],
  GA: ["H", "hB"],
  GB: ["H", "h", "hb", "hB"],
  GD: ["h", "hb", "H", "hB"],
  GE: ["H", "hB", "h"],
  GF: ["H", "hB"],
  GG: ["H", "h", "hb", "hB"],
  GH: ["h", "H"],
  GI: ["H", "h", "hb", "hB"],
  GL: ["H", "h"],
  GM: ["h", "hb", "H", "hB"],
  GN: ["H", "hB"],
  GP: ["H", "hB"],
  GQ: ["H", "hB", "h", "hb"],
  GR: ["h", "H", "hb", "hB"],
  GT: ["h", "H", "hB", "hb"],
  GU: ["h", "hb", "H", "hB"],
  GW: ["H", "hB"],
  GY: ["h", "hb", "H", "hB"],
  HK: ["h", "hB", "hb", "H"],
  HN: ["h", "H", "hB", "hb"],
  HR: ["H", "hB"],
  HU: ["H", "h"],
  IC: ["H", "h", "hB", "hb"],
  ID: ["H"],
  IE: ["H", "h", "hb", "hB"],
  IL: ["H", "hB"],
  IM: ["H", "h", "hb", "hB"],
  IN: ["h", "H"],
  IO: ["H", "h", "hb", "hB"],
  IQ: ["h", "hB", "hb", "H"],
  IR: ["hB", "H"],
  IS: ["H"],
  IT: ["H", "hB"],
  JE: ["H", "h", "hb", "hB"],
  JM: ["h", "hb", "H", "hB"],
  JO: ["h", "hB", "hb", "H"],
  JP: ["H", "K", "h"],
  KE: ["hB", "hb", "H", "h"],
  KG: ["H", "h", "hB", "hb"],
  KH: ["hB", "h", "H", "hb"],
  KI: ["h", "hb", "H", "hB"],
  KM: ["H", "h", "hB", "hb"],
  KN: ["h", "hb", "H", "hB"],
  KP: ["h", "H", "hB", "hb"],
  KR: ["h", "H", "hB", "hb"],
  KW: ["h", "hB", "hb", "H"],
  KY: ["h", "hb", "H", "hB"],
  KZ: ["H", "hB"],
  LA: ["H", "hb", "hB", "h"],
  LB: ["h", "hB", "hb", "H"],
  LC: ["h", "hb", "H", "hB"],
  LI: ["H", "hB", "h"],
  LK: ["H", "h", "hB", "hb"],
  LR: ["h", "hb", "H", "hB"],
  LS: ["h", "H"],
  LT: ["H", "h", "hb", "hB"],
  LU: ["H", "h", "hB"],
  LV: ["H", "hB", "hb", "h"],
  LY: ["h", "hB", "hb", "H"],
  MA: ["H", "h", "hB", "hb"],
  MC: ["H", "hB"],
  MD: ["H", "hB"],
  ME: ["H", "hB", "h"],
  MF: ["H", "hB"],
  MG: ["H", "h"],
  MH: ["h", "hb", "H", "hB"],
  MK: ["H", "h", "hb", "hB"],
  ML: ["H"],
  MM: ["hB", "hb", "H", "h"],
  MN: ["H", "h", "hb", "hB"],
  MO: ["h", "hB", "hb", "H"],
  MP: ["h", "hb", "H", "hB"],
  MQ: ["H", "hB"],
  MR: ["h", "hB", "hb", "H"],
  MS: ["H", "h", "hb", "hB"],
  MT: ["H", "h"],
  MU: ["H", "h"],
  MV: ["H", "h"],
  MW: ["h", "hb", "H", "hB"],
  MX: ["h", "H", "hB", "hb"],
  MY: ["hb", "hB", "h", "H"],
  MZ: ["H", "hB"],
  NA: ["h", "H", "hB", "hb"],
  NC: ["H", "hB"],
  NE: ["H"],
  NF: ["H", "h", "hb", "hB"],
  NG: ["H", "h", "hb", "hB"],
  NI: ["h", "H", "hB", "hb"],
  NL: ["H", "hB"],
  NO: ["H", "h"],
  NP: ["H", "h", "hB"],
  NR: ["H", "h", "hb", "hB"],
  NU: ["H", "h", "hb", "hB"],
  NZ: ["h", "hb", "H", "hB"],
  OM: ["h", "hB", "hb", "H"],
  PA: ["h", "H", "hB", "hb"],
  PE: ["h", "H", "hB", "hb"],
  PF: ["H", "h", "hB"],
  PG: ["h", "H"],
  PH: ["h", "hB", "hb", "H"],
  PK: ["h", "hB", "H"],
  PL: ["H", "h"],
  PM: ["H", "hB"],
  PN: ["H", "h", "hb", "hB"],
  PR: ["h", "H", "hB", "hb"],
  PS: ["h", "hB", "hb", "H"],
  PT: ["H", "hB"],
  PW: ["h", "H"],
  PY: ["h", "H", "hB", "hb"],
  QA: ["h", "hB", "hb", "H"],
  RE: ["H", "hB"],
  RO: ["H", "hB"],
  RS: ["H", "hB", "h"],
  RU: ["H"],
  RW: ["H", "h"],
  SA: ["h", "hB", "hb", "H"],
  SB: ["h", "hb", "H", "hB"],
  SC: ["H", "h", "hB"],
  SD: ["h", "hB", "hb", "H"],
  SE: ["H"],
  SG: ["h", "hb", "H", "hB"],
  SH: ["H", "h", "hb", "hB"],
  SI: ["H", "hB"],
  SJ: ["H"],
  SK: ["H"],
  SL: ["h", "hb", "H", "hB"],
  SM: ["H", "h", "hB"],
  SN: ["H", "h", "hB"],
  SO: ["h", "H"],
  SR: ["H", "hB"],
  SS: ["h", "hb", "H", "hB"],
  ST: ["H", "hB"],
  SV: ["h", "H", "hB", "hb"],
  SX: ["H", "h", "hb", "hB"],
  SY: ["h", "hB", "hb", "H"],
  SZ: ["h", "hb", "H", "hB"],
  TA: ["H", "h", "hb", "hB"],
  TC: ["h", "hb", "H", "hB"],
  TD: ["h", "H", "hB"],
  TF: ["H", "h", "hB"],
  TG: ["H", "hB"],
  TH: ["H", "h"],
  TJ: ["H", "h"],
  TL: ["H", "hB", "hb", "h"],
  TM: ["H", "h"],
  TN: ["h", "hB", "hb", "H"],
  TO: ["h", "H"],
  TR: ["H", "hB"],
  TT: ["h", "hb", "H", "hB"],
  TW: ["hB", "hb", "h", "H"],
  TZ: ["hB", "hb", "H", "h"],
  UA: ["H", "hB", "h"],
  UG: ["hB", "hb", "H", "h"],
  UM: ["h", "hb", "H", "hB"],
  US: ["h", "hb", "H", "hB"],
  UY: ["h", "H", "hB", "hb"],
  UZ: ["H", "hB", "h"],
  VA: ["H", "h", "hB"],
  VC: ["h", "hb", "H", "hB"],
  VE: ["h", "H", "hB", "hb"],
  VG: ["h", "hb", "H", "hB"],
  VI: ["h", "hb", "H", "hB"],
  VN: ["H", "h"],
  VU: ["h", "H"],
  WF: ["H", "hB"],
  WS: ["h", "H"],
  XK: ["H", "hB", "h"],
  YE: ["h", "hB", "hb", "H"],
  YT: ["H", "hB"],
  ZA: ["H", "h", "hb", "hB"],
  ZM: ["h", "hb", "H", "hB"],
  ZW: ["H", "h"],
  "af-ZA": ["H", "h", "hB", "hb"],
  "ar-001": ["h", "hB", "hb", "H"],
  "ca-ES": ["H", "h", "hB"],
  "en-001": ["h", "hb", "H", "hB"],
  "en-HK": ["h", "hb", "H", "hB"],
  "en-IL": ["H", "h", "hb", "hB"],
  "en-MY": ["h", "hb", "H", "hB"],
  "es-BR": ["H", "h", "hB", "hb"],
  "es-ES": ["H", "h", "hB", "hb"],
  "es-GQ": ["H", "h", "hB", "hb"],
  "fr-CA": ["H", "h", "hB"],
  "gl-ES": ["H", "h", "hB"],
  "gu-IN": ["hB", "hb", "h", "H"],
  "hi-IN": ["hB", "h", "H"],
  "it-CH": ["H", "h", "hB"],
  "it-IT": ["H", "h", "hB"],
  "kn-IN": ["hB", "h", "H"],
  "ml-IN": ["hB", "h", "H"],
  "mr-IN": ["hB", "hb", "h", "H"],
  "pa-IN": ["hB", "hb", "h", "H"],
  "ta-IN": ["hB", "h", "hb", "H"],
  "te-IN": ["hB", "h", "H"],
  "zu-ZA": ["H", "hB", "hb", "h"]
};
function Vt(e, t) {
  for (var r = "", n = 0; n < e.length; n++) {
    var i = e.charAt(n);
    if (i === "j") {
      for (var a = 0; n + 1 < e.length && e.charAt(n + 1) === i; )
        a++, n++;
      var s = 1 + (a & 1), o = a < 2 ? 1 : 3 + (a >> 1), u = "a", l = Xt(t);
      for ((l == "H" || l == "k") && (o = 0); o-- > 0; )
        r += u;
      for (; s-- > 0; )
        r = l + r;
    } else i === "J" ? r += "H" : r += i;
  }
  return r;
}
function Xt(e) {
  var t = e.hourCycle;
  if (t === void 0 && // @ts-ignore hourCycle(s) is not identified yet
  e.hourCycles && // @ts-ignore
  e.hourCycles.length && (t = e.hourCycles[0]), t)
    switch (t) {
      case "h24":
        return "k";
      case "h23":
        return "H";
      case "h12":
        return "h";
      case "h11":
        return "K";
      default:
        throw new Error("Invalid hourCycle");
    }
  var r = e.language, n;
  r !== "root" && (n = e.maximize().region);
  var i = X[n || ""] || X[r || ""] || X["".concat(r, "-001")] || X["001"];
  return i[0];
}
var re, kt = new RegExp("^".concat(Qe.source, "*")), Wt = new RegExp("".concat(Qe.source, "*$"));
function p(e, t) {
  return {
    start: e,
    end: t
  };
}
var zt = !!String.prototype.startsWith && "_a".startsWith("a", 1), Zt = !!String.fromCodePoint, Qt = !!Object.fromEntries, Jt = !!String.prototype.codePointAt, qt = !!String.prototype.trimStart, Yt = !!String.prototype.trimEnd, $t = !!Number.isSafeInteger, Kt = $t ? Number.isSafeInteger : function(e) {
  return typeof e == "number" && isFinite(e) && Math.floor(e) === e && Math.abs(e) <= 9007199254740991;
}, oe = !0;
try {
  var er = Ke("([^\\p{White_Space}\\p{Pattern_Syntax}]*)", "yu");
  oe = ((re = er.exec("a")) === null || re === void 0 ? void 0 : re[0]) === "a";
} catch {
  oe = !1;
}
var Ae = zt ? (
  // Native
  function(t, r, n) {
    return t.startsWith(r, n);
  }
) : (
  // For IE11
  function(t, r, n) {
    return t.slice(n, n + r.length) === r;
  }
), he = Zt ? String.fromCodePoint : (
  // IE11
  function() {
    for (var t = [], r = 0; r < arguments.length; r++)
      t[r] = arguments[r];
    for (var n = "", i = t.length, a = 0, s; i > a; ) {
      if (s = t[a++], s > 1114111) throw RangeError(s + " is not a valid code point");
      n += s < 65536 ? String.fromCharCode(s) : String.fromCharCode(((s -= 65536) >> 10) + 55296, s % 1024 + 56320);
    }
    return n;
  }
), Pe = (
  // native
  Qt ? Object.fromEntries : (
    // Ponyfill
    function(t) {
      for (var r = {}, n = 0, i = t; n < i.length; n++) {
        var a = i[n], s = a[0], o = a[1];
        r[s] = o;
      }
      return r;
    }
  )
), $e = Jt ? (
  // Native
  function(t, r) {
    return t.codePointAt(r);
  }
) : (
  // IE 11
  function(t, r) {
    var n = t.length;
    if (!(r < 0 || r >= n)) {
      var i = t.charCodeAt(r), a;
      return i < 55296 || i > 56319 || r + 1 === n || (a = t.charCodeAt(r + 1)) < 56320 || a > 57343 ? i : (i - 55296 << 10) + (a - 56320) + 65536;
    }
  }
), tr = qt ? (
  // Native
  function(t) {
    return t.trimStart();
  }
) : (
  // Ponyfill
  function(t) {
    return t.replace(kt, "");
  }
), rr = Yt ? (
  // Native
  function(t) {
    return t.trimEnd();
  }
) : (
  // Ponyfill
  function(t) {
    return t.replace(Wt, "");
  }
);
function Ke(e, t) {
  return new RegExp(e, t);
}
var ue;
if (oe) {
  var Ie = Ke("([^\\p{White_Space}\\p{Pattern_Syntax}]*)", "yu");
  ue = function(t, r) {
    var n;
    Ie.lastIndex = r;
    var i = Ie.exec(t);
    return (n = i[1]) !== null && n !== void 0 ? n : "";
  };
} else
  ue = function(t, r) {
    for (var n = []; ; ) {
      var i = $e(t, r);
      if (i === void 0 || et(i) || sr(i))
        break;
      n.push(i), r += i >= 65536 ? 2 : 1;
    }
    return he.apply(void 0, n);
  };
var nr = (
  /** @class */
  function() {
    function e(t, r) {
      r === void 0 && (r = {}), this.message = t, this.position = {
        offset: 0,
        line: 1,
        column: 1
      }, this.ignoreTag = !!r.ignoreTag, this.locale = r.locale, this.requiresOtherClause = !!r.requiresOtherClause, this.shouldParseSkeletons = !!r.shouldParseSkeletons;
    }
    return e.prototype.parse = function() {
      if (this.offset() !== 0)
        throw Error("parser can only be used once");
      return this.parseMessage(0, "", !1);
    }, e.prototype.parseMessage = function(t, r, n) {
      for (var i = []; !this.isEOF(); ) {
        var a = this.char();
        if (a === 123) {
          var s = this.parseArgument(t, n);
          if (s.err)
            return s;
          i.push(s.val);
        } else {
          if (a === 125 && t > 0)
            break;
          if (a === 35 && (r === "plural" || r === "selectordinal")) {
            var o = this.clonePosition();
            this.bump(), i.push({
              type: d.pound,
              location: p(o, this.clonePosition())
            });
          } else if (a === 60 && !this.ignoreTag && this.peek() === 47) {
            if (n)
              break;
            return this.error(m.UNMATCHED_CLOSING_TAG, p(this.clonePosition(), this.clonePosition()));
          } else if (a === 60 && !this.ignoreTag && le(this.peek() || 0)) {
            var s = this.parseTag(t, r);
            if (s.err)
              return s;
            i.push(s.val);
          } else {
            var s = this.parseLiteral(t, r);
            if (s.err)
              return s;
            i.push(s.val);
          }
        }
      }
      return {
        val: i,
        err: null
      };
    }, e.prototype.parseTag = function(t, r) {
      var n = this.clonePosition();
      this.bump();
      var i = this.parseTagName();
      if (this.bumpSpace(), this.bumpIf("/>"))
        return {
          val: {
            type: d.literal,
            value: "<".concat(i, "/>"),
            location: p(n, this.clonePosition())
          },
          err: null
        };
      if (this.bumpIf(">")) {
        var a = this.parseMessage(t + 1, r, !0);
        if (a.err)
          return a;
        var s = a.val, o = this.clonePosition();
        if (this.bumpIf("</")) {
          if (this.isEOF() || !le(this.char()))
            return this.error(m.INVALID_TAG, p(o, this.clonePosition()));
          var u = this.clonePosition(), l = this.parseTagName();
          return i !== l ? this.error(m.UNMATCHED_CLOSING_TAG, p(u, this.clonePosition())) : (this.bumpSpace(), this.bumpIf(">") ? {
            val: {
              type: d.tag,
              value: i,
              children: s,
              location: p(n, this.clonePosition())
            },
            err: null
          } : this.error(m.INVALID_TAG, p(o, this.clonePosition())));
        } else
          return this.error(m.UNCLOSED_TAG, p(n, this.clonePosition()));
      } else
        return this.error(m.INVALID_TAG, p(n, this.clonePosition()));
    }, e.prototype.parseTagName = function() {
      var t = this.offset();
      for (this.bump(); !this.isEOF() && ar(this.char()); )
        this.bump();
      return this.message.slice(t, this.offset());
    }, e.prototype.parseLiteral = function(t, r) {
      for (var n = this.clonePosition(), i = ""; ; ) {
        var a = this.tryParseQuote(r);
        if (a) {
          i += a;
          continue;
        }
        var s = this.tryParseUnquoted(t, r);
        if (s) {
          i += s;
          continue;
        }
        var o = this.tryParseLeftAngleBracket();
        if (o) {
          i += o;
          continue;
        }
        break;
      }
      var u = p(n, this.clonePosition());
      return {
        val: {
          type: d.literal,
          value: i,
          location: u
        },
        err: null
      };
    }, e.prototype.tryParseLeftAngleBracket = function() {
      return !this.isEOF() && this.char() === 60 && (this.ignoreTag || // If at the opening tag or closing tag position, bail.
      !ir(this.peek() || 0)) ? (this.bump(), "<") : null;
    }, e.prototype.tryParseQuote = function(t) {
      if (this.isEOF() || this.char() !== 39)
        return null;
      switch (this.peek()) {
        case 39:
          return this.bump(), this.bump(), "'";
        case 123:
        case 60:
        case 62:
        case 125:
          break;
        case 35:
          if (t === "plural" || t === "selectordinal")
            break;
          return null;
        default:
          return null;
      }
      this.bump();
      var r = [this.char()];
      for (this.bump(); !this.isEOF(); ) {
        var n = this.char();
        if (n === 39)
          if (this.peek() === 39)
            r.push(39), this.bump();
          else {
            this.bump();
            break;
          }
        else
          r.push(n);
        this.bump();
      }
      return he.apply(void 0, r);
    }, e.prototype.tryParseUnquoted = function(t, r) {
      if (this.isEOF())
        return null;
      var n = this.char();
      return n === 60 || n === 123 || n === 35 && (r === "plural" || r === "selectordinal") || n === 125 && t > 0 ? null : (this.bump(), he(n));
    }, e.prototype.parseArgument = function(t, r) {
      var n = this.clonePosition();
      if (this.bump(), this.bumpSpace(), this.isEOF())
        return this.error(m.EXPECT_ARGUMENT_CLOSING_BRACE, p(n, this.clonePosition()));
      if (this.char() === 125)
        return this.bump(), this.error(m.EMPTY_ARGUMENT, p(n, this.clonePosition()));
      var i = this.parseIdentifierIfPossible().value;
      if (!i)
        return this.error(m.MALFORMED_ARGUMENT, p(n, this.clonePosition()));
      if (this.bumpSpace(), this.isEOF())
        return this.error(m.EXPECT_ARGUMENT_CLOSING_BRACE, p(n, this.clonePosition()));
      switch (this.char()) {
        case 125:
          return this.bump(), {
            val: {
              type: d.argument,
              // value does not include the opening and closing braces.
              value: i,
              location: p(n, this.clonePosition())
            },
            err: null
          };
        case 44:
          return this.bump(), this.bumpSpace(), this.isEOF() ? this.error(m.EXPECT_ARGUMENT_CLOSING_BRACE, p(n, this.clonePosition())) : this.parseArgumentOptions(t, r, i, n);
        default:
          return this.error(m.MALFORMED_ARGUMENT, p(n, this.clonePosition()));
      }
    }, e.prototype.parseIdentifierIfPossible = function() {
      var t = this.clonePosition(), r = this.offset(), n = ue(this.message, r), i = r + n.length;
      this.bumpTo(i);
      var a = this.clonePosition(), s = p(t, a);
      return {
        value: n,
        location: s
      };
    }, e.prototype.parseArgumentOptions = function(t, r, n, i) {
      var a, s = this.clonePosition(), o = this.parseIdentifierIfPossible().value, u = this.clonePosition();
      switch (o) {
        case "":
          return this.error(m.EXPECT_ARGUMENT_TYPE, p(s, u));
        case "number":
        case "date":
        case "time": {
          this.bumpSpace();
          var l = null;
          if (this.bumpIf(",")) {
            this.bumpSpace();
            var h = this.clonePosition(), c = this.parseSimpleArgStyleIfPossible();
            if (c.err)
              return c;
            var f = rr(c.val);
            if (f.length === 0)
              return this.error(m.EXPECT_ARGUMENT_STYLE, p(this.clonePosition(), this.clonePosition()));
            var E = p(h, this.clonePosition());
            l = {
              style: f,
              styleLocation: E
            };
          }
          var x = this.tryParseArgumentClose(i);
          if (x.err)
            return x;
          var _ = p(i, this.clonePosition());
          if (l && Ae(l == null ? void 0 : l.style, "::", 0)) {
            var y = tr(l.style.slice(2));
            if (o === "number") {
              var c = this.parseNumberSkeletonFromString(y, l.styleLocation);
              return c.err ? c : {
                val: {
                  type: d.number,
                  value: n,
                  location: _,
                  style: c.val
                },
                err: null
              };
            } else {
              if (y.length === 0)
                return this.error(m.EXPECT_DATE_TIME_SKELETON, _);
              var g = y;
              this.locale && (g = Vt(y, this.locale));
              var f = {
                type: O.dateTime,
                pattern: g,
                location: l.styleLocation,
                parsedOptions: this.shouldParseSkeletons ? Mt(g) : {}
              }, P = o === "date" ? d.date : d.time;
              return {
                val: {
                  type: P,
                  value: n,
                  location: _,
                  style: f
                },
                err: null
              };
            }
          }
          return {
            val: {
              type: o === "number" ? d.number : o === "date" ? d.date : d.time,
              value: n,
              location: _,
              style: (a = l == null ? void 0 : l.style) !== null && a !== void 0 ? a : null
            },
            err: null
          };
        }
        case "plural":
        case "selectordinal":
        case "select": {
          var H = this.clonePosition();
          if (this.bumpSpace(), !this.bumpIf(","))
            return this.error(m.EXPECT_SELECT_ARGUMENT_OPTIONS, p(H, b({}, H)));
          this.bumpSpace();
          var R = this.parseIdentifierIfPossible(), S = 0;
          if (o !== "select" && R.value === "offset") {
            if (!this.bumpIf(":"))
              return this.error(m.EXPECT_PLURAL_ARGUMENT_OFFSET_VALUE, p(this.clonePosition(), this.clonePosition()));
            this.bumpSpace();
            var c = this.tryParseDecimalInteger(m.EXPECT_PLURAL_ARGUMENT_OFFSET_VALUE, m.INVALID_PLURAL_ARGUMENT_OFFSET_VALUE);
            if (c.err)
              return c;
            this.bumpSpace(), R = this.parseIdentifierIfPossible(), S = c.val;
          }
          var V = this.tryParsePluralOrSelectOptions(t, o, r, R);
          if (V.err)
            return V;
          var x = this.tryParseArgumentClose(i);
          if (x.err)
            return x;
          var ve = p(i, this.clonePosition());
          return o === "select" ? {
            val: {
              type: d.select,
              value: n,
              options: Pe(V.val),
              location: ve
            },
            err: null
          } : {
            val: {
              type: d.plural,
              value: n,
              options: Pe(V.val),
              offset: S,
              pluralType: o === "plural" ? "cardinal" : "ordinal",
              location: ve
            },
            err: null
          };
        }
        default:
          return this.error(m.INVALID_ARGUMENT_TYPE, p(s, u));
      }
    }, e.prototype.tryParseArgumentClose = function(t) {
      return this.isEOF() || this.char() !== 125 ? this.error(m.EXPECT_ARGUMENT_CLOSING_BRACE, p(t, this.clonePosition())) : (this.bump(), {
        val: !0,
        err: null
      });
    }, e.prototype.parseSimpleArgStyleIfPossible = function() {
      for (var t = 0, r = this.clonePosition(); !this.isEOF(); ) {
        var n = this.char();
        switch (n) {
          case 39: {
            this.bump();
            var i = this.clonePosition();
            if (!this.bumpUntil("'"))
              return this.error(m.UNCLOSED_QUOTE_IN_ARGUMENT_STYLE, p(i, this.clonePosition()));
            this.bump();
            break;
          }
          case 123: {
            t += 1, this.bump();
            break;
          }
          case 125: {
            if (t > 0)
              t -= 1;
            else
              return {
                val: this.message.slice(r.offset, this.offset()),
                err: null
              };
            break;
          }
          default:
            this.bump();
            break;
        }
      }
      return {
        val: this.message.slice(r.offset, this.offset()),
        err: null
      };
    }, e.prototype.parseNumberSkeletonFromString = function(t, r) {
      var n = [];
      try {
        n = Ut(t);
      } catch {
        return this.error(m.INVALID_NUMBER_SKELETON, r);
      }
      return {
        val: {
          type: O.number,
          tokens: n,
          location: r,
          parsedOptions: this.shouldParseSkeletons ? jt(n) : {}
        },
        err: null
      };
    }, e.prototype.tryParsePluralOrSelectOptions = function(t, r, n, i) {
      for (var a, s = !1, o = [], u = /* @__PURE__ */ new Set(), l = i.value, h = i.location; ; ) {
        if (l.length === 0) {
          var c = this.clonePosition();
          if (r !== "select" && this.bumpIf("=")) {
            var f = this.tryParseDecimalInteger(m.EXPECT_PLURAL_ARGUMENT_SELECTOR, m.INVALID_PLURAL_ARGUMENT_SELECTOR);
            if (f.err)
              return f;
            h = p(c, this.clonePosition()), l = this.message.slice(c.offset, this.offset());
          } else
            break;
        }
        if (u.has(l))
          return this.error(r === "select" ? m.DUPLICATE_SELECT_ARGUMENT_SELECTOR : m.DUPLICATE_PLURAL_ARGUMENT_SELECTOR, h);
        l === "other" && (s = !0), this.bumpSpace();
        var E = this.clonePosition();
        if (!this.bumpIf("{"))
          return this.error(r === "select" ? m.EXPECT_SELECT_ARGUMENT_SELECTOR_FRAGMENT : m.EXPECT_PLURAL_ARGUMENT_SELECTOR_FRAGMENT, p(this.clonePosition(), this.clonePosition()));
        var x = this.parseMessage(t + 1, r, n);
        if (x.err)
          return x;
        var _ = this.tryParseArgumentClose(E);
        if (_.err)
          return _;
        o.push([l, {
          value: x.val,
          location: p(E, this.clonePosition())
        }]), u.add(l), this.bumpSpace(), a = this.parseIdentifierIfPossible(), l = a.value, h = a.location;
      }
      return o.length === 0 ? this.error(r === "select" ? m.EXPECT_SELECT_ARGUMENT_SELECTOR : m.EXPECT_PLURAL_ARGUMENT_SELECTOR, p(this.clonePosition(), this.clonePosition())) : this.requiresOtherClause && !s ? this.error(m.MISSING_OTHER_CLAUSE, p(this.clonePosition(), this.clonePosition())) : {
        val: o,
        err: null
      };
    }, e.prototype.tryParseDecimalInteger = function(t, r) {
      var n = 1, i = this.clonePosition();
      this.bumpIf("+") || this.bumpIf("-") && (n = -1);
      for (var a = !1, s = 0; !this.isEOF(); ) {
        var o = this.char();
        if (o >= 48 && o <= 57)
          a = !0, s = s * 10 + (o - 48), this.bump();
        else
          break;
      }
      var u = p(i, this.clonePosition());
      return a ? (s *= n, Kt(s) ? {
        val: s,
        err: null
      } : this.error(r, u)) : this.error(t, u);
    }, e.prototype.offset = function() {
      return this.position.offset;
    }, e.prototype.isEOF = function() {
      return this.offset() === this.message.length;
    }, e.prototype.clonePosition = function() {
      return {
        offset: this.position.offset,
        line: this.position.line,
        column: this.position.column
      };
    }, e.prototype.char = function() {
      var t = this.position.offset;
      if (t >= this.message.length)
        throw Error("out of bound");
      var r = $e(this.message, t);
      if (r === void 0)
        throw Error("Offset ".concat(t, " is at invalid UTF-16 code unit boundary"));
      return r;
    }, e.prototype.error = function(t, r) {
      return {
        val: null,
        err: {
          kind: t,
          message: this.message,
          location: r
        }
      };
    }, e.prototype.bump = function() {
      if (!this.isEOF()) {
        var t = this.char();
        t === 10 ? (this.position.line += 1, this.position.column = 1, this.position.offset += 1) : (this.position.column += 1, this.position.offset += t < 65536 ? 1 : 2);
      }
    }, e.prototype.bumpIf = function(t) {
      if (Ae(this.message, t, this.offset())) {
        for (var r = 0; r < t.length; r++)
          this.bump();
        return !0;
      }
      return !1;
    }, e.prototype.bumpUntil = function(t) {
      var r = this.offset(), n = this.message.indexOf(t, r);
      return n >= 0 ? (this.bumpTo(n), !0) : (this.bumpTo(this.message.length), !1);
    }, e.prototype.bumpTo = function(t) {
      if (this.offset() > t)
        throw Error("targetOffset ".concat(t, " must be greater than or equal to the current offset ").concat(this.offset()));
      for (t = Math.min(t, this.message.length); ; ) {
        var r = this.offset();
        if (r === t)
          break;
        if (r > t)
          throw Error("targetOffset ".concat(t, " is at invalid UTF-16 code unit boundary"));
        if (this.bump(), this.isEOF())
          break;
      }
    }, e.prototype.bumpSpace = function() {
      for (; !this.isEOF() && et(this.char()); )
        this.bump();
    }, e.prototype.peek = function() {
      if (this.isEOF())
        return null;
      var t = this.char(), r = this.offset(), n = this.message.charCodeAt(r + (t >= 65536 ? 2 : 1));
      return n ?? null;
    }, e;
  }()
);
function le(e) {
  return e >= 97 && e <= 122 || e >= 65 && e <= 90;
}
function ir(e) {
  return le(e) || e === 47;
}
function ar(e) {
  return e === 45 || e === 46 || e >= 48 && e <= 57 || e === 95 || e >= 97 && e <= 122 || e >= 65 && e <= 90 || e == 183 || e >= 192 && e <= 214 || e >= 216 && e <= 246 || e >= 248 && e <= 893 || e >= 895 && e <= 8191 || e >= 8204 && e <= 8205 || e >= 8255 && e <= 8256 || e >= 8304 && e <= 8591 || e >= 11264 && e <= 12271 || e >= 12289 && e <= 55295 || e >= 63744 && e <= 64975 || e >= 65008 && e <= 65533 || e >= 65536 && e <= 983039;
}
function et(e) {
  return e >= 9 && e <= 13 || e === 32 || e === 133 || e >= 8206 && e <= 8207 || e === 8232 || e === 8233;
}
function sr(e) {
  return e >= 33 && e <= 35 || e === 36 || e >= 37 && e <= 39 || e === 40 || e === 41 || e === 42 || e === 43 || e === 44 || e === 45 || e >= 46 && e <= 47 || e >= 58 && e <= 59 || e >= 60 && e <= 62 || e >= 63 && e <= 64 || e === 91 || e === 92 || e === 93 || e === 94 || e === 96 || e === 123 || e === 124 || e === 125 || e === 126 || e === 161 || e >= 162 && e <= 165 || e === 166 || e === 167 || e === 169 || e === 171 || e === 172 || e === 174 || e === 176 || e === 177 || e === 182 || e === 187 || e === 191 || e === 215 || e === 247 || e >= 8208 && e <= 8213 || e >= 8214 && e <= 8215 || e === 8216 || e === 8217 || e === 8218 || e >= 8219 && e <= 8220 || e === 8221 || e === 8222 || e === 8223 || e >= 8224 && e <= 8231 || e >= 8240 && e <= 8248 || e === 8249 || e === 8250 || e >= 8251 && e <= 8254 || e >= 8257 && e <= 8259 || e === 8260 || e === 8261 || e === 8262 || e >= 8263 && e <= 8273 || e === 8274 || e === 8275 || e >= 8277 && e <= 8286 || e >= 8592 && e <= 8596 || e >= 8597 && e <= 8601 || e >= 8602 && e <= 8603 || e >= 8604 && e <= 8607 || e === 8608 || e >= 8609 && e <= 8610 || e === 8611 || e >= 8612 && e <= 8613 || e === 8614 || e >= 8615 && e <= 8621 || e === 8622 || e >= 8623 && e <= 8653 || e >= 8654 && e <= 8655 || e >= 8656 && e <= 8657 || e === 8658 || e === 8659 || e === 8660 || e >= 8661 && e <= 8691 || e >= 8692 && e <= 8959 || e >= 8960 && e <= 8967 || e === 8968 || e === 8969 || e === 8970 || e === 8971 || e >= 8972 && e <= 8991 || e >= 8992 && e <= 8993 || e >= 8994 && e <= 9e3 || e === 9001 || e === 9002 || e >= 9003 && e <= 9083 || e === 9084 || e >= 9085 && e <= 9114 || e >= 9115 && e <= 9139 || e >= 9140 && e <= 9179 || e >= 9180 && e <= 9185 || e >= 9186 && e <= 9254 || e >= 9255 && e <= 9279 || e >= 9280 && e <= 9290 || e >= 9291 && e <= 9311 || e >= 9472 && e <= 9654 || e === 9655 || e >= 9656 && e <= 9664 || e === 9665 || e >= 9666 && e <= 9719 || e >= 9720 && e <= 9727 || e >= 9728 && e <= 9838 || e === 9839 || e >= 9840 && e <= 10087 || e === 10088 || e === 10089 || e === 10090 || e === 10091 || e === 10092 || e === 10093 || e === 10094 || e === 10095 || e === 10096 || e === 10097 || e === 10098 || e === 10099 || e === 10100 || e === 10101 || e >= 10132 && e <= 10175 || e >= 10176 && e <= 10180 || e === 10181 || e === 10182 || e >= 10183 && e <= 10213 || e === 10214 || e === 10215 || e === 10216 || e === 10217 || e === 10218 || e === 10219 || e === 10220 || e === 10221 || e === 10222 || e === 10223 || e >= 10224 && e <= 10239 || e >= 10240 && e <= 10495 || e >= 10496 && e <= 10626 || e === 10627 || e === 10628 || e === 10629 || e === 10630 || e === 10631 || e === 10632 || e === 10633 || e === 10634 || e === 10635 || e === 10636 || e === 10637 || e === 10638 || e === 10639 || e === 10640 || e === 10641 || e === 10642 || e === 10643 || e === 10644 || e === 10645 || e === 10646 || e === 10647 || e === 10648 || e >= 10649 && e <= 10711 || e === 10712 || e === 10713 || e === 10714 || e === 10715 || e >= 10716 && e <= 10747 || e === 10748 || e === 10749 || e >= 10750 && e <= 11007 || e >= 11008 && e <= 11055 || e >= 11056 && e <= 11076 || e >= 11077 && e <= 11078 || e >= 11079 && e <= 11084 || e >= 11085 && e <= 11123 || e >= 11124 && e <= 11125 || e >= 11126 && e <= 11157 || e === 11158 || e >= 11159 && e <= 11263 || e >= 11776 && e <= 11777 || e === 11778 || e === 11779 || e === 11780 || e === 11781 || e >= 11782 && e <= 11784 || e === 11785 || e === 11786 || e === 11787 || e === 11788 || e === 11789 || e >= 11790 && e <= 11798 || e === 11799 || e >= 11800 && e <= 11801 || e === 11802 || e === 11803 || e === 11804 || e === 11805 || e >= 11806 && e <= 11807 || e === 11808 || e === 11809 || e === 11810 || e === 11811 || e === 11812 || e === 11813 || e === 11814 || e === 11815 || e === 11816 || e === 11817 || e >= 11818 && e <= 11822 || e === 11823 || e >= 11824 && e <= 11833 || e >= 11834 && e <= 11835 || e >= 11836 && e <= 11839 || e === 11840 || e === 11841 || e === 11842 || e >= 11843 && e <= 11855 || e >= 11856 && e <= 11857 || e === 11858 || e >= 11859 && e <= 11903 || e >= 12289 && e <= 12291 || e === 12296 || e === 12297 || e === 12298 || e === 12299 || e === 12300 || e === 12301 || e === 12302 || e === 12303 || e === 12304 || e === 12305 || e >= 12306 && e <= 12307 || e === 12308 || e === 12309 || e === 12310 || e === 12311 || e === 12312 || e === 12313 || e === 12314 || e === 12315 || e === 12316 || e === 12317 || e >= 12318 && e <= 12319 || e === 12320 || e === 12336 || e === 64830 || e === 64831 || e >= 65093 && e <= 65094;
}
function fe(e) {
  e.forEach(function(t) {
    if (delete t.location, ke(t) || We(t))
      for (var r in t.options)
        delete t.options[r].location, fe(t.options[r].value);
    else je(t) && Ze(t.style) || (Ve(t) || Xe(t)) && se(t.style) ? delete t.style.location : ze(t) && fe(t.children);
  });
}
function or(e, t) {
  t === void 0 && (t = {}), t = b({
    shouldParseSkeletons: !0,
    requiresOtherClause: !0
  }, t);
  var r = new nr(e, t).parse();
  if (r.err) {
    var n = SyntaxError(m[r.err.kind]);
    throw n.location = r.err.location, n.originalMessage = r.err.message, n;
  }
  return t != null && t.captureLocation || fe(r.val), r.val;
}
var w;
(function(e) {
  e.MISSING_VALUE = "MISSING_VALUE", e.INVALID_VALUE = "INVALID_VALUE", e.MISSING_INTL_API = "MISSING_INTL_API";
})(w || (w = {}));
var q = (
  /** @class */
  function(e) {
    J(t, e);
    function t(r, n, i) {
      var a = e.call(this, r) || this;
      return a.code = n, a.originalMessage = i, a;
    }
    return t.prototype.toString = function() {
      return "[formatjs Error: ".concat(this.code, "] ").concat(this.message);
    }, t;
  }(Error)
), Ne = (
  /** @class */
  function(e) {
    J(t, e);
    function t(r, n, i, a) {
      return e.call(this, 'Invalid values for "'.concat(r, '": "').concat(n, '". Options are "').concat(Object.keys(i).join('", "'), '"'), w.INVALID_VALUE, a) || this;
    }
    return t;
  }(q)
), hr = (
  /** @class */
  function(e) {
    J(t, e);
    function t(r, n, i) {
      return e.call(this, 'Value for "'.concat(r, '" must be of type ').concat(n), w.INVALID_VALUE, i) || this;
    }
    return t;
  }(q)
), ur = (
  /** @class */
  function(e) {
    J(t, e);
    function t(r, n) {
      return e.call(this, 'The intl string context variable "'.concat(r, '" was not provided to the string "').concat(n, '"'), w.MISSING_VALUE, n) || this;
    }
    return t;
  }(q)
), v;
(function(e) {
  e[e.literal = 0] = "literal", e[e.object = 1] = "object";
})(v || (v = {}));
function lr(e) {
  return e.length < 2 ? e : e.reduce(function(t, r) {
    var n = t[t.length - 1];
    return !n || n.type !== v.literal || r.type !== v.literal ? t.push(r) : n.value += r.value, t;
  }, []);
}
function fr(e) {
  return typeof e == "function";
}
function k(e, t, r, n, i, a, s) {
  if (e.length === 1 && He(e[0]))
    return [{
      type: v.literal,
      value: e[0].value
    }];
  for (var o = [], u = 0, l = e; u < l.length; u++) {
    var h = l[u];
    if (He(h)) {
      o.push({
        type: v.literal,
        value: h.value
      });
      continue;
    }
    if (Lt(h)) {
      typeof a == "number" && o.push({
        type: v.literal,
        value: r.getNumberFormat(t).format(a)
      });
      continue;
    }
    var c = h.value;
    if (!(i && c in i))
      throw new ur(c, s);
    var f = i[c];
    if (wt(h)) {
      (!f || typeof f == "string" || typeof f == "number") && (f = typeof f == "string" || typeof f == "number" ? String(f) : ""), o.push({
        type: typeof f == "string" ? v.literal : v.object,
        value: f
      });
      continue;
    }
    if (Ve(h)) {
      var E = typeof h.style == "string" ? n.date[h.style] : se(h.style) ? h.style.parsedOptions : void 0;
      o.push({
        type: v.literal,
        value: r.getDateTimeFormat(t, E).format(f)
      });
      continue;
    }
    if (Xe(h)) {
      var E = typeof h.style == "string" ? n.time[h.style] : se(h.style) ? h.style.parsedOptions : n.time.medium;
      o.push({
        type: v.literal,
        value: r.getDateTimeFormat(t, E).format(f)
      });
      continue;
    }
    if (je(h)) {
      var E = typeof h.style == "string" ? n.number[h.style] : Ze(h.style) ? h.style.parsedOptions : void 0;
      E && E.scale && (f = f * (E.scale || 1)), o.push({
        type: v.literal,
        value: r.getNumberFormat(t, E).format(f)
      });
      continue;
    }
    if (ze(h)) {
      var x = h.children, _ = h.value, y = i[_];
      if (!fr(y))
        throw new hr(_, "function", s);
      var g = k(x, t, r, n, i, a), P = y(g.map(function(S) {
        return S.value;
      }));
      Array.isArray(P) || (P = [P]), o.push.apply(o, P.map(function(S) {
        return {
          type: typeof S == "string" ? v.literal : v.object,
          value: S
        };
      }));
    }
    if (ke(h)) {
      var H = h.options[f] || h.options.other;
      if (!H)
        throw new Ne(h.value, f, Object.keys(h.options), s);
      o.push.apply(o, k(H.value, t, r, n, i));
      continue;
    }
    if (We(h)) {
      var H = h.options["=".concat(f)];
      if (!H) {
        if (!Intl.PluralRules)
          throw new q(`Intl.PluralRules is not available in this environment.
Try polyfilling it using "@formatjs/intl-pluralrules"
`, w.MISSING_INTL_API, s);
        var R = r.getPluralRules(t, {
          type: h.pluralType
        }).select(f - (h.offset || 0));
        H = h.options[R] || h.options.other;
      }
      if (!H)
        throw new Ne(h.value, f, Object.keys(h.options), s);
      o.push.apply(o, k(H.value, t, r, n, i, f - (h.offset || 0)));
      continue;
    }
  }
  return lr(o);
}
function cr(e, t) {
  return t ? b(b(b({}, e || {}), t || {}), Object.keys(e).reduce(function(r, n) {
    return r[n] = b(b({}, e[n]), t[n] || {}), r;
  }, {})) : e;
}
function mr(e, t) {
  return t ? Object.keys(e).reduce(function(r, n) {
    return r[n] = cr(e[n], t[n]), r;
  }, b({}, e)) : e;
}
function ne(e) {
  return {
    create: function() {
      return {
        get: function(t) {
          return e[t];
        },
        set: function(t, r) {
          e[t] = r;
        }
      };
    }
  };
}
function pr(e) {
  return e === void 0 && (e = {
    number: {},
    dateTime: {},
    pluralRules: {}
  }), {
    getNumberFormat: ee(function() {
      for (var t, r = [], n = 0; n < arguments.length; n++)
        r[n] = arguments[n];
      return new ((t = Intl.NumberFormat).bind.apply(t, K([void 0], r, !1)))();
    }, {
      cache: ne(e.number),
      strategy: te.variadic
    }),
    getDateTimeFormat: ee(function() {
      for (var t, r = [], n = 0; n < arguments.length; n++)
        r[n] = arguments[n];
      return new ((t = Intl.DateTimeFormat).bind.apply(t, K([void 0], r, !1)))();
    }, {
      cache: ne(e.dateTime),
      strategy: te.variadic
    }),
    getPluralRules: ee(function() {
      for (var t, r = [], n = 0; n < arguments.length; n++)
        r[n] = arguments[n];
      return new ((t = Intl.PluralRules).bind.apply(t, K([void 0], r, !1)))();
    }, {
      cache: ne(e.pluralRules),
      strategy: te.variadic
    })
  };
}
var br = (
  /** @class */
  function() {
    function e(t, r, n, i) {
      r === void 0 && (r = e.defaultLocale);
      var a = this;
      if (this.formatterCache = {
        number: {},
        dateTime: {},
        pluralRules: {}
      }, this.format = function(u) {
        var l = a.formatToParts(u);
        if (l.length === 1)
          return l[0].value;
        var h = l.reduce(function(c, f) {
          return !c.length || f.type !== v.literal || typeof c[c.length - 1] != "string" ? c.push(f.value) : c[c.length - 1] += f.value, c;
        }, []);
        return h.length <= 1 ? h[0] || "" : h;
      }, this.formatToParts = function(u) {
        return k(a.ast, a.locales, a.formatters, a.formats, u, void 0, a.message);
      }, this.resolvedOptions = function() {
        var u;
        return {
          locale: ((u = a.resolvedLocale) === null || u === void 0 ? void 0 : u.toString()) || Intl.NumberFormat.supportedLocalesOf(a.locales)[0]
        };
      }, this.getAst = function() {
        return a.ast;
      }, this.locales = r, this.resolvedLocale = e.resolveLocale(r), typeof t == "string") {
        if (this.message = t, !e.__parse)
          throw new TypeError("IntlMessageFormat.__parse must be set to process `message` of type `string`");
        var s = i || {};
        s.formatters;
        var o = Tt(s, ["formatters"]);
        this.ast = e.__parse(t, b(b({}, o), {
          locale: this.resolvedLocale
        }));
      } else
        this.ast = t;
      if (!Array.isArray(this.ast))
        throw new TypeError("A message must be provided as a String or AST.");
      this.formats = mr(e.formats, n), this.formatters = i && i.formatters || pr(this.formatterCache);
    }
    return Object.defineProperty(e, "defaultLocale", {
      get: function() {
        return e.memoizedDefaultLocale || (e.memoizedDefaultLocale = new Intl.NumberFormat().resolvedOptions().locale), e.memoizedDefaultLocale;
      },
      enumerable: !1,
      configurable: !0
    }), e.memoizedDefaultLocale = null, e.resolveLocale = function(t) {
      if (!(typeof Intl.Locale > "u")) {
        var r = Intl.NumberFormat.supportedLocalesOf(t);
        return r.length > 0 ? new Intl.Locale(r[0]) : new Intl.Locale(typeof t == "string" ? t : t[0]);
      }
    }, e.__parse = or, e.formats = {
      number: {
        integer: {
          maximumFractionDigits: 0
        },
        currency: {
          style: "currency"
        },
        percent: {
          style: "percent"
        }
      },
      date: {
        short: {
          month: "numeric",
          day: "numeric",
          year: "2-digit"
        },
        medium: {
          month: "short",
          day: "numeric",
          year: "numeric"
        },
        long: {
          month: "long",
          day: "numeric",
          year: "numeric"
        },
        full: {
          weekday: "long",
          month: "long",
          day: "numeric",
          year: "numeric"
        }
      },
      time: {
        short: {
          hour: "numeric",
          minute: "numeric"
        },
        medium: {
          hour: "numeric",
          minute: "numeric",
          second: "numeric"
        },
        long: {
          hour: "numeric",
          minute: "numeric",
          second: "numeric",
          timeZoneName: "short"
        },
        full: {
          hour: "numeric",
          minute: "numeric",
          second: "numeric",
          timeZoneName: "short"
        }
      }
    }, e;
  }()
);
function gr(e, t) {
  if (t == null) return;
  if (t in e)
    return e[t];
  const r = t.split(".");
  let n = e;
  for (let i = 0; i < r.length; i++)
    if (typeof n == "object") {
      if (i > 0) {
        const a = r.slice(i, r.length).join(".");
        if (a in n) {
          n = n[a];
          break;
        }
      }
      n = n[r[i]];
    } else
      n = void 0;
  return n;
}
const B = {}, Er = (e, t, r) => r && (t in B || (B[t] = {}), e in B[t] || (B[t][e] = r), r), tt = (e, t) => {
  if (t == null) return;
  if (t in B && e in B[t])
    return B[t][e];
  const r = Y(t);
  for (let n = 0; n < r.length; n++) {
    const i = r[n], a = vr(i, e);
    if (a)
      return Er(e, t, a);
  }
};
let Ee;
const F = ge({});
function dr(e) {
  return Ee[e] || null;
}
function rt(e) {
  return e in Ee;
}
function vr(e, t) {
  if (!rt(e))
    return null;
  const r = dr(e);
  return gr(r, t);
}
function xr(e) {
  if (e == null) return;
  const t = Y(e);
  for (let r = 0; r < t.length; r++) {
    const n = t[r];
    if (rt(n))
      return n;
  }
}
function _r(e, ...t) {
  delete B[e], F.update((r) => (r[e] = Ht.all([r[e] || {}, ...t]), r));
}
C([F], ([e]) => Object.keys(e));
F.subscribe((e) => Ee = e);
const W = {};
function yr(e, t) {
  W[e].delete(t), W[e].size === 0 && delete W[e];
}
function nt(e) {
  return W[e];
}
function Hr(e) {
  return Y(e).map((t) => {
    const r = nt(t);
    return [t, r ? [...r] : []];
  }).filter(([, t]) => t.length > 0);
}
function ce(e) {
  return e == null ? !1 : Y(e).some((t) => {
    var r;
    return (r = nt(t)) == null ? void 0 : r.size;
  });
}
function Tr(e, t) {
  return Promise.all(t.map((n) => (yr(e, n), n().then((i) => i.default || i)))).then((n) => _r(e, ...n));
}
const U = {};
function it(e) {
  if (!ce(e))
    return e in U ? U[e] : Promise.resolve();
  const t = Hr(e);
  return U[e] = Promise.all(t.map(([r, n]) => Tr(r, n))).then(() => {
    if (ce(e))
      return it(e);
    delete U[e];
  }), U[e];
}
const Br = {
  number: {
    scientific: {
      notation: "scientific"
    },
    engineering: {
      notation: "engineering"
    },
    compactLong: {
      notation: "compact",
      compactDisplay: "long"
    },
    compactShort: {
      notation: "compact",
      compactDisplay: "short"
    }
  },
  date: {
    short: {
      month: "numeric",
      day: "numeric",
      year: "2-digit"
    },
    medium: {
      month: "short",
      day: "numeric",
      year: "numeric"
    },
    long: {
      month: "long",
      day: "numeric",
      year: "numeric"
    },
    full: {
      weekday: "long",
      month: "long",
      day: "numeric",
      year: "numeric"
    }
  },
  time: {
    short: {
      hour: "numeric",
      minute: "numeric"
    },
    medium: {
      hour: "numeric",
      minute: "numeric",
      second: "numeric"
    },
    long: {
      hour: "numeric",
      minute: "numeric",
      second: "numeric",
      timeZoneName: "short"
    },
    full: {
      hour: "numeric",
      minute: "numeric",
      second: "numeric",
      timeZoneName: "short"
    }
  }
}, Sr = {
  fallbackLocale: null,
  loadingDelay: 200,
  formats: Br,
  warnOnMissingMessages: !0,
  handleMissingMessage: void 0,
  ignoreTag: !0
}, Ar = Sr;
function L() {
  return Ar;
}
const ie = ge(!1);
var Pr = Object.defineProperty, Ir = Object.defineProperties, Nr = Object.getOwnPropertyDescriptors, Oe = Object.getOwnPropertySymbols, Or = Object.prototype.hasOwnProperty, wr = Object.prototype.propertyIsEnumerable, we = (e, t, r) => t in e ? Pr(e, t, {
  enumerable: !0,
  configurable: !0,
  writable: !0,
  value: r
}) : e[t] = r, Lr = (e, t) => {
  for (var r in t || (t = {})) Or.call(t, r) && we(e, r, t[r]);
  if (Oe) for (var r of Oe(t))
    wr.call(t, r) && we(e, r, t[r]);
  return e;
}, Cr = (e, t) => Ir(e, Nr(t));
let me;
const Z = ge(null);
function Le(e) {
  return e.split("-").map((t, r, n) => n.slice(0, r + 1).join("-")).reverse();
}
function Y(e, t = L().fallbackLocale) {
  const r = Le(e);
  return t ? [.../* @__PURE__ */ new Set([...r, ...Le(t)])] : r;
}
function A() {
  return me ?? void 0;
}
Z.subscribe((e) => {
  me = e ?? void 0, typeof window < "u" && e != null && document.documentElement.setAttribute("lang", e);
});
const Mr = (e) => {
  if (e && xr(e) && ce(e)) {
    const {
      loadingDelay: t
    } = L();
    let r;
    return typeof window < "u" && A() != null && t ? r = window.setTimeout(() => ie.set(!0), t) : ie.set(!0), it(e).then(() => {
      Z.set(e);
    }).finally(() => {
      clearTimeout(r), ie.set(!1);
    });
  }
  return Z.set(e);
}, j = Cr(Lr({}, Z), {
  set: Mr
}), Rr = () => typeof window > "u" ? null : window.navigator.language || window.navigator.languages[0], $ = (e) => {
  const t = /* @__PURE__ */ Object.create(null);
  return (n) => {
    const i = JSON.stringify(n);
    return i in t ? t[i] : t[i] = e(n);
  };
};
var Ur = Object.defineProperty, Q = Object.getOwnPropertySymbols, at = Object.prototype.hasOwnProperty, st = Object.prototype.propertyIsEnumerable, Ce = (e, t, r) => t in e ? Ur(e, t, {
  enumerable: !0,
  configurable: !0,
  writable: !0,
  value: r
}) : e[t] = r, de = (e, t) => {
  for (var r in t || (t = {})) at.call(t, r) && Ce(e, r, t[r]);
  if (Q) for (var r of Q(t))
    st.call(t, r) && Ce(e, r, t[r]);
  return e;
}, M = (e, t) => {
  var r = {};
  for (var n in e) at.call(e, n) && t.indexOf(n) < 0 && (r[n] = e[n]);
  if (e != null && Q) for (var n of Q(e))
    t.indexOf(n) < 0 && st.call(e, n) && (r[n] = e[n]);
  return r;
};
const D = (e, t) => {
  const {
    formats: r
  } = L();
  if (e in r && t in r[e])
    return r[e][t];
  throw new Error(`[svelte-i18n] Unknown "${t}" ${e} format.`);
}, Gr = $((e) => {
  var t = e, {
    locale: r,
    format: n
  } = t, i = M(t, ["locale", "format"]);
  if (r == null)
    throw new Error('[svelte-i18n] A "locale" must be set to format numbers');
  return n && (i = D("number", n)), new Intl.NumberFormat(r, i);
}), Dr = $((e) => {
  var t = e, {
    locale: r,
    format: n
  } = t, i = M(t, ["locale", "format"]);
  if (r == null)
    throw new Error('[svelte-i18n] A "locale" must be set to format dates');
  return n ? i = D("date", n) : Object.keys(i).length === 0 && (i = D("date", "short")), new Intl.DateTimeFormat(r, i);
}), Fr = $((e) => {
  var t = e, {
    locale: r,
    format: n
  } = t, i = M(t, ["locale", "format"]);
  if (r == null)
    throw new Error('[svelte-i18n] A "locale" must be set to format time values');
  return n ? i = D("time", n) : Object.keys(i).length === 0 && (i = D("time", "short")), new Intl.DateTimeFormat(r, i);
}), jr = (e = {}) => {
  var t = e, {
    locale: r = A()
  } = t, n = M(t, ["locale"]);
  return Gr(de({
    locale: r
  }, n));
}, Vr = (e = {}) => {
  var t = e, {
    locale: r = A()
  } = t, n = M(t, ["locale"]);
  return Dr(de({
    locale: r
  }, n));
}, Xr = (e = {}) => {
  var t = e, {
    locale: r = A()
  } = t, n = M(t, ["locale"]);
  return Fr(de({
    locale: r
  }, n));
}, kr = $(
  // eslint-disable-next-line @typescript-eslint/no-non-null-assertion
  (e, t = A()) => new br(e, t, L().formats, {
    ignoreTag: L().ignoreTag
  })
), Wr = (e, t = {}) => {
  var r, n, i, a;
  let s = t;
  typeof e == "object" && (s = e, e = s.id);
  const {
    values: o,
    locale: u = A(),
    default: l
  } = s;
  if (u == null)
    throw new Error("[svelte-i18n] Cannot format a message without first setting the initial locale.");
  let h = tt(e, u);
  if (!h)
    h = (a = (i = (n = (r = L()).handleMissingMessage) == null ? void 0 : n.call(r, {
      locale: u,
      id: e,
      defaultValue: l
    })) != null ? i : l) != null ? a : e;
  else if (typeof h != "string")
    return console.warn(`[svelte-i18n] Message with id "${e}" must be of type "string", found: "${typeof h}". Gettin its value through the "$format" method is deprecated; use the "json" method instead.`), h;
  if (!o)
    return h;
  let c = h;
  try {
    c = kr(h, u).format(o);
  } catch (f) {
    f instanceof Error && console.warn(`[svelte-i18n] Message "${e}" has syntax error:`, f.message);
  }
  return c;
}, zr = (e, t) => Xr(t).format(e), Zr = (e, t) => Vr(t).format(e), Qr = (e, t) => jr(t).format(e), Jr = (e, t = A()) => tt(e, t);
C([j, F], () => Wr);
C([j], () => zr);
C([j], () => Zr);
C([j], () => Qr);
C([j, F], () => Jr);
const {
  SvelteComponent: qr,
  attr: I,
  check_outros: Yr,
  children: $r,
  claim_element: Kr,
  create_slot: en,
  detach: pe,
  element: tn,
  empty: Me,
  flush: T,
  get_all_dirty_from_scope: rn,
  get_slot_changes: nn,
  group_outros: an,
  init: sn,
  insert_hydration: ot,
  safe_not_equal: on,
  transition_in: z,
  transition_out: be,
  update_slot_base: hn
} = window.__gradio__svelte__internal, {
  onDestroy: un,
  onMount: ln
} = window.__gradio__svelte__internal;
function Re(e) {
  let t, r, n, i;
  const a = (
    /*#slots*/
    e[9].default
  ), s = en(
    a,
    e,
    /*$$scope*/
    e[8],
    null
  );
  return {
    c() {
      t = tn("div"), s && s.c(), this.h();
    },
    l(o) {
      t = Kr(o, "DIV", {
        class: !0,
        id: !0,
        style: !0
      });
      var u = $r(t);
      s && s.l(u), u.forEach(pe), this.h();
    },
    h() {
      I(t, "class", r = xe(
        "ms-gr-container",
        /*elem_classes*/
        e[1]
      )), I(
        t,
        "id",
        /*elem_id*/
        e[0]
      ), I(t, "style", n = typeof /*elem_style*/
      e[2] == "object" ? _e(
        /*elem_style*/
        e[2]
      ) : (
        /*elem_style*/
        e[2]
      ));
    },
    m(o, u) {
      ot(o, t, u), s && s.m(t, null), i = !0;
    },
    p(o, u) {
      s && s.p && (!i || u & /*$$scope*/
      256) && hn(
        s,
        a,
        o,
        /*$$scope*/
        o[8],
        i ? nn(
          a,
          /*$$scope*/
          o[8],
          u,
          null
        ) : rn(
          /*$$scope*/
          o[8]
        ),
        null
      ), (!i || u & /*elem_classes*/
      2 && r !== (r = xe(
        "ms-gr-container",
        /*elem_classes*/
        o[1]
      ))) && I(t, "class", r), (!i || u & /*elem_id*/
      1) && I(
        t,
        "id",
        /*elem_id*/
        o[0]
      ), (!i || u & /*elem_style*/
      4 && n !== (n = typeof /*elem_style*/
      o[2] == "object" ? _e(
        /*elem_style*/
        o[2]
      ) : (
        /*elem_style*/
        o[2]
      ))) && I(t, "style", n);
    },
    i(o) {
      i || (z(s, o), i = !0);
    },
    o(o) {
      be(s, o), i = !1;
    },
    d(o) {
      o && pe(t), s && s.d(o);
    }
  };
}
function fn(e) {
  let t, r, n = (
    /*visible*/
    e[3] && Re(e)
  );
  return {
    c() {
      n && n.c(), t = Me();
    },
    l(i) {
      n && n.l(i), t = Me();
    },
    m(i, a) {
      n && n.m(i, a), ot(i, t, a), r = !0;
    },
    p(i, [a]) {
      /*visible*/
      i[3] ? n ? (n.p(i, a), a & /*visible*/
      8 && z(n, 1)) : (n = Re(i), n.c(), z(n, 1), n.m(t.parentNode, t)) : n && (an(), be(n, 1, 1, () => {
        n = null;
      }), Yr());
    },
    i(i) {
      r || (z(n), r = !0);
    },
    o(i) {
      be(n), r = !1;
    },
    d(i) {
      i && pe(t), n && n.d(i);
    }
  };
}
function cn(e, t) {
  let r = null;
  return (...n) => {
    r && clearTimeout(r), r = setTimeout(() => e(...n), t);
  };
}
function Ue(e, t) {
  const r = (...n) => e(...n);
  return typeof t == "number" ? cn(r, t) : r;
}
function mn(e, t, r) {
  let {
    $$slots: n = {},
    $$scope: i
  } = t, {
    elem_id: a = ""
  } = t, {
    elem_classes: s = []
  } = t, {
    elem_style: o = {}
  } = t, {
    value: u
  } = t, {
    _internal: l = {}
  } = t, {
    gradio: h
  } = t, {
    attached_events: c = []
  } = t, {
    visible: f = !0
  } = t;
  function E() {
    return {
      theme: h.theme,
      language: Rr() || "en",
      userAgent: navigator.userAgent,
      screen: {
        width: window.innerWidth,
        height: window.innerHeight,
        scrollY: window.scrollY,
        scrollX: window.scrollX
      }
    };
  }
  function x() {
    r(4, u = E()), (l.bind_mount_event || c.includes("mount")) && h.dispatch("mount", E());
  }
  const _ = Ue(() => {
    r(4, u = E()), (l.bind_resize_event || c.includes("resize")) && h.dispatch("resize", E());
  }, 500), y = Ue(() => {
    r(4, u = E()), (l.bind_unmount_event || c.includes("unmount")) && h.dispatch("unmount", E());
  });
  return window.ms_globals.dispatch = (...g) => {
    h.dispatch("custom", g);
  }, ln(() => {
    requestAnimationFrame(() => {
      x();
    }), window.addEventListener("resize", _), window.addEventListener("beforeunload", y);
  }), un(() => {
    window.removeEventListener("resize", _), window.removeEventListener("beforeunload", y);
  }), e.$$set = (g) => {
    "elem_id" in g && r(0, a = g.elem_id), "elem_classes" in g && r(1, s = g.elem_classes), "elem_style" in g && r(2, o = g.elem_style), "value" in g && r(4, u = g.value), "_internal" in g && r(5, l = g._internal), "gradio" in g && r(6, h = g.gradio), "attached_events" in g && r(7, c = g.attached_events), "visible" in g && r(3, f = g.visible), "$$scope" in g && r(8, i = g.$$scope);
  }, [a, s, o, f, u, l, h, c, i, n];
}
class bn extends qr {
  constructor(t) {
    super(), sn(this, t, mn, fn, on, {
      elem_id: 0,
      elem_classes: 1,
      elem_style: 2,
      value: 4,
      _internal: 5,
      gradio: 6,
      attached_events: 7,
      visible: 3
    });
  }
  get elem_id() {
    return this.$$.ctx[0];
  }
  set elem_id(t) {
    this.$$set({
      elem_id: t
    }), T();
  }
  get elem_classes() {
    return this.$$.ctx[1];
  }
  set elem_classes(t) {
    this.$$set({
      elem_classes: t
    }), T();
  }
  get elem_style() {
    return this.$$.ctx[2];
  }
  set elem_style(t) {
    this.$$set({
      elem_style: t
    }), T();
  }
  get value() {
    return this.$$.ctx[4];
  }
  set value(t) {
    this.$$set({
      value: t
    }), T();
  }
  get _internal() {
    return this.$$.ctx[5];
  }
  set _internal(t) {
    this.$$set({
      _internal: t
    }), T();
  }
  get gradio() {
    return this.$$.ctx[6];
  }
  set gradio(t) {
    this.$$set({
      gradio: t
    }), T();
  }
  get attached_events() {
    return this.$$.ctx[7];
  }
  set attached_events(t) {
    this.$$set({
      attached_events: t
    }), T();
  }
  get visible() {
    return this.$$.ctx[3];
  }
  set visible(t) {
    this.$$set({
      visible: t
    }), T();
  }
}
export {
  bn as default
};
