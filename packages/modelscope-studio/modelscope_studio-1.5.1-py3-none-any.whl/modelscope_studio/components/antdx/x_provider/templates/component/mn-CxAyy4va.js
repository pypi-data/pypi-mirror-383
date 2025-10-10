import { a as d, c as i } from "./XProvider-C2bF5aL8.js";
const l = window.ms_globals.dayjs;
function u(n, s) {
  for (var o = 0; o < s.length; o++) {
    const t = s[o];
    if (typeof t != "string" && !Array.isArray(t)) {
      for (const e in t)
        if (e !== "default" && !(e in n)) {
          const _ = Object.getOwnPropertyDescriptor(t, e);
          _ && Object.defineProperty(n, e, _.get ? _ : {
            enumerable: !0,
            get: () => t[e]
          });
        }
    }
  }
  return Object.freeze(Object.defineProperty(n, Symbol.toStringTag, {
    value: "Module"
  }));
}
var a = {
  exports: {}
};
(function(n, s) {
  (function(o, t) {
    n.exports = t(l);
  })(i, function(o) {
    function t(r) {
      return r && typeof r == "object" && "default" in r ? r : {
        default: r
      };
    }
    var e = t(o), _ = {
      name: "mn",
      weekdays: "Ням_Даваа_Мягмар_Лхагва_Пүрэв_Баасан_Бямба".split("_"),
      months: "Нэгдүгээр сар_Хоёрдугаар сар_Гуравдугаар сар_Дөрөвдүгээр сар_Тавдугаар сар_Зургадугаар сар_Долдугаар сар_Наймдугаар сар_Есдүгээр сар_Аравдугаар сар_Арван нэгдүгээр сар_Арван хоёрдугаар сар".split("_"),
      weekdaysShort: "Ням_Дав_Мяг_Лха_Пүр_Баа_Бям".split("_"),
      monthsShort: "1 сар_2 сар_3 сар_4 сар_5 сар_6 сар_7 сар_8 сар_9 сар_10 сар_11 сар_12 сар".split("_"),
      weekdaysMin: "Ня_Да_Мя_Лх_Пү_Ба_Бя".split("_"),
      ordinal: function(r) {
        return r;
      },
      formats: {
        LT: "HH:mm",
        LTS: "HH:mm:ss",
        L: "YYYY-MM-DD",
        LL: "YYYY оны MMMMын D",
        LLL: "YYYY оны MMMMын D HH:mm",
        LLLL: "dddd, YYYY оны MMMMын D HH:mm"
      },
      relativeTime: {
        future: "%s",
        past: "%s",
        s: "саяхан",
        m: "м",
        mm: "%dм",
        h: "1ц",
        hh: "%dц",
        d: "1ө",
        dd: "%dө",
        M: "1с",
        MM: "%dс",
        y: "1ж",
        yy: "%dж"
      }
    };
    return e.default.locale(_, null, !0), _;
  });
})(a);
var m = a.exports;
const f = /* @__PURE__ */ d(m), p = /* @__PURE__ */ u({
  __proto__: null,
  default: f
}, [m]);
export {
  p as m
};
