import { c as _ } from "./Index-Bv07WiuH.js";
import { i as l, o as $, c as g } from "./config-provider-ROh4C3n3.js";
function h(m, v) {
  for (var c = 0; c < v.length; c++) {
    const a = v[c];
    if (typeof a != "string" && !Array.isArray(a)) {
      for (const t in a)
        if (t !== "default" && !(t in m)) {
          const p = Object.getOwnPropertyDescriptor(a, t);
          p && Object.defineProperty(m, t, p.get ? p : {
            enumerable: !0,
            get: () => a[t]
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
var P = {
  // Options
  items_per_page: "/ str",
  jump_to: "Idi na",
  jump_to_confirm: "potvrdi",
  page: "",
  // Pagination
  prev_page: "Prijašnja stranica",
  next_page: "Sljedeća stranica",
  prev_5: "Prijašnjih 5 stranica",
  next_5: "Sljedećih 5 stranica",
  prev_3: "Prijašnje 3 stranice",
  next_3: "Sljedeće 3 stranice",
  page_size: "Page Size"
};
n.default = P;
var d = {}, r = {}, u = {}, k = l.default;
Object.defineProperty(u, "__esModule", {
  value: !0
});
u.default = void 0;
var j = k($), O = g, x = (0, j.default)((0, j.default)({}, O.commonLocale), {}, {
  locale: "hr_HR",
  today: "Danas",
  now: "Sad",
  backToToday: "Natrag na danas",
  ok: "OK",
  clear: "Očisti",
  week: "Sedmica",
  month: "Mjesec",
  year: "Godina",
  timeSelect: "odaberite vrijeme",
  dateSelect: "odaberite datum",
  weekSelect: "Odaberite tjedan",
  monthSelect: "Odaberite mjesec",
  yearSelect: "Odaberite godinu",
  decadeSelect: "Odaberite desetljeće",
  dateFormat: "D.M.YYYY",
  dateTimeFormat: "D.M.YYYY HH:mm:ss",
  previousMonth: "Prošli mjesec (PageUp)",
  nextMonth: "Sljedeći mjesec (PageDown)",
  previousYear: "Prošla godina (Control + left)",
  nextYear: "Sljedeća godina (Control + right)",
  previousDecade: "Prošlo desetljeće",
  nextDecade: "Sljedeće desetljeće",
  previousCentury: "Prošlo stoljeće",
  nextCentury: "Sljedeće stoljeće"
});
u.default = x;
var i = {};
Object.defineProperty(i, "__esModule", {
  value: !0
});
i.default = void 0;
const y = {
  placeholder: "Odaberite vrijeme",
  rangePlaceholder: ["Vrijeme početka", "Vrijeme završetka"]
};
i.default = y;
var b = l.default;
Object.defineProperty(r, "__esModule", {
  value: !0
});
r.default = void 0;
var R = b(u), S = b(i);
const z = {
  lang: Object.assign({
    placeholder: "Odaberite datum",
    yearPlaceholder: "Odaberite godinu",
    quarterPlaceholder: "Odaberite četvrtinu",
    monthPlaceholder: "Odaberite mjesec",
    weekPlaceholder: "Odaberite tjedan",
    rangePlaceholder: ["Početni datum", "Završni datum"],
    rangeYearPlaceholder: ["Početna godina", "Završna godina"],
    rangeMonthPlaceholder: ["Početni mjesec", "Završni mjesec"],
    rangeWeekPlaceholder: ["Početni tjedan", "Završni tjedan"]
  }, R.default),
  timePickerLocale: Object.assign({}, S.default)
};
r.default = z;
var H = l.default;
Object.defineProperty(d, "__esModule", {
  value: !0
});
d.default = void 0;
var M = H(r);
d.default = M.default;
var s = l.default;
Object.defineProperty(o, "__esModule", {
  value: !0
});
o.default = void 0;
var T = s(n), D = s(d), K = s(r), Y = s(i);
const e = "${label} nije valjan ${type}", w = {
  locale: "hr",
  Pagination: T.default,
  DatePicker: K.default,
  TimePicker: Y.default,
  Calendar: D.default,
  global: {
    placeholder: "Molimo označite",
    close: "Zatvori"
  },
  Table: {
    filterTitle: "Filter meni",
    filterConfirm: "OK",
    filterReset: "Reset",
    filterEmptyText: "Nema filtera",
    emptyText: "Nema podataka",
    selectAll: "Označi trenutnu stranicu",
    selectInvert: "Invertiraj trenutnu stranicu",
    selectionAll: "Odaberite sve podatke",
    sortTitle: "Sortiraj",
    expand: "Proširi redak",
    collapse: "Sažmi redak",
    triggerDesc: "Kliknite za sortiranje silazno",
    triggerAsc: "Kliknite za sortiranje uzlazno",
    cancelSort: "Kliknite da biste otkazali sortiranje"
  },
  Tour: {
    Next: "Slijedeći",
    Previous: "Prethodni",
    Finish: "Završi"
  },
  Modal: {
    okText: "OK",
    cancelText: "Odustani",
    justOkText: "OK"
  },
  Popconfirm: {
    okText: "OK",
    cancelText: "Odustani"
  },
  Transfer: {
    titles: ["", ""],
    searchPlaceholder: "Pretraži ovdje",
    itemUnit: "stavka",
    itemsUnit: "stavke",
    remove: "Ukloniti",
    selectCurrent: "Odaberite trenutnu stranicu",
    removeCurrent: "Ukloni trenutnu stranicu",
    selectAll: "Odaberite sve podatke",
    removeAll: "Uklonite sve podatke",
    selectInvert: "Obrni trenutnu stranicu"
  },
  Upload: {
    uploading: "Upload u tijeku...",
    removeFile: "Makni datoteku",
    uploadError: "Greška kod uploada",
    previewFile: "Pogledaj datoteku",
    downloadFile: "Preuzmi datoteku"
  },
  Empty: {
    description: "Nema podataka"
  },
  Icon: {
    icon: "ikona"
  },
  Text: {
    edit: "Uredi",
    copy: "Kopiraj",
    copied: "Kopiranje uspješno",
    expand: "Proširi"
  },
  Form: {
    optional: "(neobavezno)",
    defaultValidateMessages: {
      default: "Pogreška provjere valjanosti polja za ${label}",
      required: "Molimo unesite ${label}",
      enum: "${label} mora biti jedan od [${enum}]",
      whitespace: "${label} ne može biti prazan znak",
      date: {
        format: "${label} format datuma je nevažeći",
        parse: "${label} ne može se pretvoriti u datum",
        invalid: "${label} je nevažeći datum"
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
        len: "${label} mora biti ${len} slova",
        min: "${label} mora biti najmanje ${min} slova",
        max: "${label} mora biti do ${max} slova",
        range: "${label} mora biti između ${min}-${max} slova"
      },
      number: {
        len: "${label} mora biti jednak ${len}",
        min: "${label} mora biti minimalano ${min}",
        max: "${label} mora biti maksimalano ${max}",
        range: "${label} mora biti između ${min}-${max}"
      },
      array: {
        len: "Mora biti ${len} ${label}",
        min: "Najmanje ${min} ${label}",
        max: "Najviše ${max} ${label}",
        range: "Količina ${label} mora biti između ${min}-${max}"
      },
      pattern: {
        mismatch: "${label} ne odgovara obrascu ${pattern}"
      }
    }
  },
  Image: {
    preview: "Pregled"
  }
};
o.default = w;
var f = o;
const C = /* @__PURE__ */ _(f), N = /* @__PURE__ */ h({
  __proto__: null,
  default: C
}, [f]);
export {
  N as h
};
