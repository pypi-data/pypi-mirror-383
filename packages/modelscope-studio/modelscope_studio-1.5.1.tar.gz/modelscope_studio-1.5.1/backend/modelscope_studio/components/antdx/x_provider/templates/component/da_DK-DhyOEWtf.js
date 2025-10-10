import { a as $ } from "./XProvider-C2bF5aL8.js";
import { i, o as b, c as k } from "./config-provider-CivlQzIf.js";
function y(m, f) {
  for (var g = 0; g < f.length; g++) {
    const t = f[g];
    if (typeof t != "string" && !Array.isArray(t)) {
      for (const a in t)
        if (a !== "default" && !(a in m)) {
          const c = Object.getOwnPropertyDescriptor(t, a);
          c && Object.defineProperty(m, a, c.get ? c : {
            enumerable: !0,
            get: () => t[a]
          });
        }
    }
  }
  return Object.freeze(Object.defineProperty(m, Symbol.toStringTag, {
    value: "Module"
  }));
}
var o = {}, d = {};
Object.defineProperty(d, "__esModule", {
  value: !0
});
d.default = void 0;
var D = {
  // Options
  items_per_page: "/ side",
  jump_to: "Gå til",
  jump_to_confirm: "bekræft",
  page: "Side",
  // Pagination
  prev_page: "Forrige Side",
  next_page: "Næste Side",
  prev_5: "Forrige 5 Sider",
  next_5: "Næste 5 Sider",
  prev_3: "Forrige 3 Sider",
  next_3: "Næste 3 Sider",
  page_size: "sidestørrelse"
};
d.default = D;
var n = {}, r = {}, s = {}, x = i.default;
Object.defineProperty(s, "__esModule", {
  value: !0
});
s.default = void 0;
var p = x(b), K = k, j = (0, p.default)((0, p.default)({}, K.commonLocale), {}, {
  locale: "da_DK",
  today: "I dag",
  now: "Nu",
  backToToday: "Gå til i dag",
  ok: "OK",
  clear: "Ryd",
  week: "Uge",
  month: "Måned",
  year: "År",
  timeSelect: "Vælg tidspunkt",
  dateSelect: "Vælg dato",
  monthSelect: "Vælg måned",
  yearSelect: "Vælg år",
  decadeSelect: "Vælg årti",
  dateFormat: "D/M/YYYY",
  dateTimeFormat: "D/M/YYYY HH:mm:ss",
  previousMonth: "Forrige måned (Page Up)",
  nextMonth: "Næste måned (Page Down)",
  previousYear: "Forrige år (Ctrl-venstre pil)",
  nextYear: "Næste år (Ctrl-højre pil)",
  previousDecade: "Forrige årti",
  nextDecade: "Næste årti",
  previousCentury: "Forrige århundrede",
  nextCentury: "Næste århundrede"
});
s.default = j;
var l = {};
Object.defineProperty(l, "__esModule", {
  value: !0
});
l.default = void 0;
const S = {
  placeholder: "Vælg tid",
  rangePlaceholder: ["Starttidspunkt", "Sluttidspunkt"]
};
l.default = S;
var v = i.default;
Object.defineProperty(r, "__esModule", {
  value: !0
});
r.default = void 0;
var F = v(s), h = v(l);
const P = {
  lang: Object.assign({
    placeholder: "Vælg dato",
    rangePlaceholder: ["Startdato", "Slutdato"]
  }, F.default),
  timePickerLocale: Object.assign({}, h.default)
};
r.default = P;
var O = i.default;
Object.defineProperty(n, "__esModule", {
  value: !0
});
n.default = void 0;
var T = O(r);
n.default = T.default;
var u = i.default;
Object.defineProperty(o, "__esModule", {
  value: !0
});
o.default = void 0;
var M = u(d), N = u(n), V = u(r), Y = u(l);
const e = "${label} er ikke en gyldig ${type}", w = {
  locale: "da",
  DatePicker: V.default,
  TimePicker: Y.default,
  Calendar: N.default,
  Pagination: M.default,
  global: {
    close: "Luk"
  },
  Table: {
    filterTitle: "Filtermenu",
    filterConfirm: "OK",
    filterReset: "Nulstil",
    filterEmptyText: "Ingen filtre",
    emptyText: "Ingen data",
    selectAll: "Vælg alle",
    selectNone: "Ryd alt data",
    selectInvert: "Invertér valg",
    selectionAll: "Vælg alt data",
    sortTitle: "Sortér",
    expand: "Udvid række",
    collapse: "Flet række",
    triggerDesc: "Klik for at sortere faldende",
    triggerAsc: "Klik for at sortere stigende",
    cancelSort: "Klik for at annullere sortering"
  },
  Tour: {
    Next: "Næste",
    Previous: "Forrige",
    Finish: "Færdiggørelse"
  },
  Modal: {
    okText: "OK",
    cancelText: "Afbryd",
    justOkText: "OK"
  },
  Popconfirm: {
    okText: "OK",
    cancelText: "Afbryd"
  },
  Transfer: {
    titles: ["", ""],
    searchPlaceholder: "Søg her",
    itemUnit: "element",
    itemsUnit: "elementer"
  },
  Upload: {
    uploading: "Uploader...",
    removeFile: "Fjern fil",
    uploadError: "Fejl ved upload",
    previewFile: "Forhåndsvisning",
    downloadFile: "Download fil"
  },
  Empty: {
    description: "Ingen data"
  },
  Form: {
    optional: "(valgfrit)",
    defaultValidateMessages: {
      default: "Feltvalideringsfejl ${label}",
      required: "Indtast venligst ${label}",
      enum: "${label} skal være en af [${enum}]",
      whitespace: "${label} kan ikke være et tomt tegn",
      date: {
        format: "${label} Datoformatet er ugyldigt",
        parse: "${label} kan ikke konverteres til en dato",
        invalid: "${label} er en ugyldig dato"
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
        len: "${label} skal være ${len} tegn",
        min: "${label} mindst ${min} tegn",
        max: "${label} op til ${max} tegn",
        range: "${label} skal være mellem ${min} og ${max} tegn"
      },
      number: {
        len: "${label} skal være lig med ${len}",
        min: "${label} Minimumsværdien er ${min}",
        max: "${label} maksimal værdi er ${max}",
        range: "${label} skal være mellem ${min}-${max}"
      },
      array: {
        len: "Skal være ${len} ${label}",
        min: "Mindst  ${min} ${label}",
        max: "Højst ${max} ${label}",
        range: "Mængden af ${label} skal være mellem ${min}-${max}"
      },
      pattern: {
        mismatch: "${label} stemmer ikke overens med mønsteret ${pattern}"
      }
    }
  }
};
o.default = w;
var _ = o;
const R = /* @__PURE__ */ $(_), I = /* @__PURE__ */ y({
  __proto__: null,
  default: R
}, [_]);
export {
  I as d
};
