import { c as $ } from "./Index-Bv07WiuH.js";
import { i, o as b, c as k } from "./config-provider-ROh4C3n3.js";
function y(m, v) {
  for (var f = 0; f < v.length; f++) {
    const a = v[f];
    if (typeof a != "string" && !Array.isArray(a)) {
      for (const r in a)
        if (r !== "default" && !(r in m)) {
          const c = Object.getOwnPropertyDescriptor(a, r);
          c && Object.defineProperty(m, r, c.get ? c : {
            enumerable: !0,
            get: () => a[r]
          });
        }
    }
  }
  return Object.freeze(Object.defineProperty(m, Symbol.toStringTag, {
    value: "Module"
  }));
}
var o = {}, n = {};
Object.defineProperty(n, "__esModule", {
  value: !0
});
n.default = void 0;
var j = {
  // Options
  items_per_page: "/ síðu",
  jump_to: "Síða",
  jump_to_confirm: "staðfest",
  page: "",
  // Pagination
  prev_page: "Fyrri síða",
  next_page: "Næsta síða",
  prev_5: "Til baka 5 síður",
  next_5: "Áfram 5 síður",
  prev_3: "Til baka 3 síður",
  next_3: "Áfram 3 síður",
  page_size: "Page Size"
};
n.default = j;
var s = {}, t = {}, u = {}, S = i.default;
Object.defineProperty(u, "__esModule", {
  value: !0
});
u.default = void 0;
var g = S(b), x = k, h = (0, g.default)((0, g.default)({}, x.commonLocale), {}, {
  locale: "is_IS",
  today: "Í dag",
  now: "Núna",
  backToToday: "Til baka til dagsins í dag",
  ok: "Í lagi",
  clear: "Hreinsa",
  week: "Vika",
  month: "Mánuður",
  year: "Ár",
  timeSelect: "Velja tíma",
  dateSelect: "Velja dag",
  monthSelect: "Velja mánuð",
  yearSelect: "Velja ár",
  decadeSelect: "Velja áratug",
  dateFormat: "D/M/YYYY",
  dateTimeFormat: "D/M/YYYY HH:mm:ss",
  previousMonth: "Fyrri mánuður (PageUp)",
  nextMonth: "Næsti mánuður (PageDown)",
  previousYear: "Fyrra ár (Control + left)",
  nextYear: "Næsta ár (Control + right)",
  previousDecade: "Fyrri áratugur",
  nextDecade: "Næsti áratugur",
  previousCentury: "Fyrri öld",
  nextCentury: "Næsta öld"
});
u.default = h;
var l = {};
Object.defineProperty(l, "__esModule", {
  value: !0
});
l.default = void 0;
const P = {
  placeholder: "Velja tíma"
};
l.default = P;
var p = i.default;
Object.defineProperty(t, "__esModule", {
  value: !0
});
t.default = void 0;
var T = p(u), I = p(l);
const V = {
  lang: Object.assign({
    placeholder: "Veldu dag",
    rangePlaceholder: ["Upphafsdagur", "Lokadagur"]
  }, T.default),
  timePickerLocale: Object.assign({}, I.default)
};
t.default = V;
var F = i.default;
Object.defineProperty(s, "__esModule", {
  value: !0
});
s.default = void 0;
var M = F(t);
s.default = M.default;
var d = i.default;
Object.defineProperty(o, "__esModule", {
  value: !0
});
o.default = void 0;
var O = d(n), D = d(s), Y = d(t), N = d(l);
const e = "${label} er ekki gilt ${type}", H = {
  locale: "is",
  Pagination: O.default,
  DatePicker: Y.default,
  TimePicker: N.default,
  Calendar: D.default,
  global: {
    close: "Loka"
  },
  Table: {
    filterTitle: "Afmarkanir",
    filterConfirm: "Staðfesta",
    filterReset: "Núllstilla",
    selectAll: "Velja allt",
    selectInvert: "Viðsnúa vali"
  },
  Tour: {
    Next: "Áfram",
    Previous: "Til baka",
    Finish: "Lokið"
  },
  Modal: {
    okText: "Áfram",
    cancelText: "Hætta við",
    justOkText: "Í lagi"
  },
  Popconfirm: {
    okText: "Áfram",
    cancelText: "Hætta við"
  },
  Transfer: {
    titles: ["", ""],
    searchPlaceholder: "Leita hér",
    itemUnit: "færsla",
    itemsUnit: "færslur"
  },
  Upload: {
    uploading: "Hleð upp...",
    removeFile: "Fjarlægja skrá",
    uploadError: "Villa við að hlaða upp",
    previewFile: "Forskoða skrá",
    downloadFile: "Hlaða niður skrá"
  },
  Empty: {
    description: "Engin gögn"
  },
  Form: {
    optional: "（Valfrjálst）",
    defaultValidateMessages: {
      default: "Villa við staðfestingu reits ${label}",
      required: "gjörðu svo vel að koma inn ${label}",
      enum: "${label} verður að vera einn af [${enum}]",
      whitespace: "${label} getur ekki verið tómur stafur",
      date: {
        format: "${label} dagsetningarsnið er ógilt",
        parse: "Ekki er hægt að breyta ${label} í dag",
        invalid: "${label} er ógild dagsetning"
      },
      types: {
        string: e,
        method: e,
        array: e,
        object: e,
        number: e,
        date: e,
        boolean: e,
        integer: e,
        float: e,
        regexp: e,
        email: e,
        url: e,
        hex: e
      },
      string: {
        len: "${label} verður að vera ${len} stafir",
        min: "${label} er að minnsta kosti ${min} stafir að lengd",
        max: "${label} getur verið allt að ${max} stafir",
        range: "${label} verður að vera á milli ${min}-${max} stafir"
      },
      number: {
        len: "${label} verður að vera jafngildi ${len}",
        min: "Lágmarksgildi ${label} er ${mín}",
        max: "Hámarksgildi ${label} er ${max}",
        range: "${label} verður að vera á milli ${min}-${max}"
      },
      array: {
        len: "Verður að vera ${len}${label}",
        min: "Að minnsta kosti ${min}${label}",
        max: "Í mesta lagi ${max}${label}",
        range: "Magn ${label} verður að vera á milli ${min}-${max}"
      },
      pattern: {
        mismatch: "${label} passar ekki við mynstur ${pattern}"
      }
    }
  }
};
o.default = H;
var _ = o;
const w = /* @__PURE__ */ $(_), L = /* @__PURE__ */ y({
  __proto__: null,
  default: w
}, [_]);
export {
  L as i
};
