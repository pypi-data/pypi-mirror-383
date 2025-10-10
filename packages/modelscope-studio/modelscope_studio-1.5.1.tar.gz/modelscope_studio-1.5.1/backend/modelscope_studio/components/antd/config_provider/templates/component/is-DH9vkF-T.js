import { c as j, d as h } from "./Index-Bv07WiuH.js";
const L = window.ms_globals.dayjs;
function v(a, o) {
  for (var u = 0; u < o.length; u++) {
    const e = o[u];
    if (typeof e != "string" && !Array.isArray(e)) {
      for (const n in e)
        if (n !== "default" && !(n in a)) {
          const s = Object.getOwnPropertyDescriptor(e, n);
          s && Object.defineProperty(a, n, s.get ? s : {
            enumerable: !0,
            get: () => e[n]
          });
        }
    }
  }
  return Object.freeze(Object.defineProperty(a, Symbol.toStringTag, {
    value: "Module"
  }));
}
var _ = {
  exports: {}
};
(function(a, o) {
  (function(u, e) {
    a.exports = e(L);
  })(h, function(u) {
    function e(t) {
      return t && typeof t == "object" && "default" in t ? t : {
        default: t
      };
    }
    var n = e(u), s = {
      s: ["nokkrar sekúndur", "nokkrar sekúndur", "nokkrum sekúndum"],
      m: ["mínúta", "mínútu", "mínútu"],
      mm: ["mínútur", "mínútur", "mínútum"],
      h: ["klukkustund", "klukkustund", "klukkustund"],
      hh: ["klukkustundir", "klukkustundir", "klukkustundum"],
      d: ["dagur", "dag", "degi"],
      dd: ["dagar", "daga", "dögum"],
      M: ["mánuður", "mánuð", "mánuði"],
      MM: ["mánuðir", "mánuði", "mánuðum"],
      y: ["ár", "ár", "ári"],
      yy: ["ár", "ár", "árum"]
    };
    function r(t, k, f, g) {
      var p = function(m, c, M, y) {
        var Y = y ? 0 : M ? 1 : 2, b = m.length === 2 && c % 10 == 1 ? m[0] : m, d = s[b][Y];
        return m.length === 1 ? d : "%d " + d;
      }(f, t, g, k);
      return p.replace("%d", t);
    }
    var i = {
      name: "is",
      weekdays: "sunnudagur_mánudagur_þriðjudagur_miðvikudagur_fimmtudagur_föstudagur_laugardagur".split("_"),
      months: "janúar_febrúar_mars_apríl_maí_júní_júlí_ágúst_september_október_nóvember_desember".split("_"),
      weekStart: 1,
      weekdaysShort: "sun_mán_þri_mið_fim_fös_lau".split("_"),
      monthsShort: "jan_feb_mar_apr_maí_jún_júl_ágú_sep_okt_nóv_des".split("_"),
      weekdaysMin: "Su_Má_Þr_Mi_Fi_Fö_La".split("_"),
      ordinal: function(t) {
        return t;
      },
      formats: {
        LT: "H:mm",
        LTS: "H:mm:ss",
        L: "DD.MM.YYYY",
        LL: "D. MMMM YYYY",
        LLL: "D. MMMM YYYY [kl.] H:mm",
        LLLL: "dddd, D. MMMM YYYY [kl.] H:mm"
      },
      relativeTime: {
        future: "eftir %s",
        past: "fyrir %s síðan",
        s: r,
        m: r,
        mm: r,
        h: r,
        hh: r,
        d: r,
        dd: r,
        M: r,
        MM: r,
        y: r,
        yy: r
      }
    };
    return n.default.locale(i, null, !0), i;
  });
})(_);
var l = _.exports;
const w = /* @__PURE__ */ j(l), D = /* @__PURE__ */ v({
  __proto__: null,
  default: w
}, [l]);
export {
  D as i
};
