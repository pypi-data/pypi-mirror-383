import { c as k } from "./Index-Bv07WiuH.js";
import { i, o as $, c as g } from "./config-provider-ROh4C3n3.js";
function S(c, v) {
  for (var m = 0; m < v.length; m++) {
    const a = v[m];
    if (typeof a != "string" && !Array.isArray(a)) {
      for (const r in a)
        if (r !== "default" && !(r in c)) {
          const p = Object.getOwnPropertyDescriptor(a, r);
          p && Object.defineProperty(c, r, p.get ? p : {
            enumerable: !0,
            get: () => a[r]
          });
        }
    }
  }
  return Object.freeze(Object.defineProperty(c, Symbol.toStringTag, {
    value: "Module"
  }));
}
var l = {}, n = {};
Object.defineProperty(n, "__esModule", {
  value: !0
});
n.default = void 0;
var P = {
  // Options
  items_per_page: "/ strani",
  jump_to: "Idi na",
  page: "",
  // Pagination
  prev_page: "Prethodna strana",
  next_page: "Sledeća strana",
  prev_5: "Prethodnih 5 Strana",
  next_5: "Sledećih 5 Strana",
  prev_3: "Prethodnih 3 Strane",
  next_3: "Sledećih 3 Strane",
  page_size: "Page Size"
};
n.default = P;
var d = {}, t = {}, s = {}, j = i.default;
Object.defineProperty(s, "__esModule", {
  value: !0
});
s.default = void 0;
var b = j($), h = g, z = (0, b.default)((0, b.default)({}, h.commonLocale), {}, {
  locale: "sr_RS",
  today: "Danas",
  now: "Sada",
  backToToday: "Vrati se na danas",
  ok: "U redu",
  clear: "Obriši",
  week: "Nedelja",
  month: "Mesec",
  year: "Godina",
  timeSelect: "Izaberi vreme",
  dateSelect: "Izaberi datum",
  monthSelect: "Izaberi mesec",
  yearSelect: "Izaberi godinu",
  decadeSelect: "Izaberi deceniju",
  dateFormat: "DD.MM.YYYY",
  dateTimeFormat: "DD.MM.YYYY HH:mm:ss",
  previousMonth: "Prethodni mesec (PageUp)",
  nextMonth: "Sledeći mesec (PageDown)",
  previousYear: "Prethodna godina (Control + left)",
  nextYear: "Sledeća godina (Control + right)",
  previousDecade: "Prethodna decenija",
  nextDecade: "Sledeća decenija",
  previousCentury: "Prethodni vek",
  nextCentury: "Sledeći vek"
});
s.default = z;
var o = {};
Object.defineProperty(o, "__esModule", {
  value: !0
});
o.default = void 0;
const x = {
  placeholder: "Izaberi vreme",
  rangePlaceholder: ["Vreme početka", "Vreme završetka"]
};
o.default = x;
var f = i.default;
Object.defineProperty(t, "__esModule", {
  value: !0
});
t.default = void 0;
var y = f(s), R = f(o);
const I = {
  lang: Object.assign({
    placeholder: "Izaberi datum",
    yearPlaceholder: "Izaberi godinu",
    quarterPlaceholder: "Izaberi tromesečje",
    monthPlaceholder: "Izaberi mesec",
    weekPlaceholder: "Izaberi sedmicu",
    rangePlaceholder: ["Datum početka", "Datum završetka"],
    rangeYearPlaceholder: ["Godina početka", "Godina završetka"],
    rangeMonthPlaceholder: ["Mesec početka", "Mesec završetka"],
    rangeWeekPlaceholder: ["Sedmica početka", "Sedmica završetka"]
  }, y.default),
  timePickerLocale: Object.assign({}, R.default)
};
t.default = I;
var M = i.default;
Object.defineProperty(d, "__esModule", {
  value: !0
});
d.default = void 0;
var O = M(t);
d.default = O.default;
var u = i.default;
Object.defineProperty(l, "__esModule", {
  value: !0
});
l.default = void 0;
var D = u(n), T = u(d), U = u(t), Y = u(o);
const e = "${label} nije važeći ${type}", w = {
  locale: "sr",
  Pagination: D.default,
  DatePicker: U.default,
  TimePicker: Y.default,
  Calendar: T.default,
  global: {
    placeholder: "Izaberi",
    close: "Zatvori"
  },
  Table: {
    filterTitle: "Meni filtera",
    filterConfirm: "U redu",
    filterReset: "Poništi",
    filterEmptyText: "Nema filtera",
    emptyText: "Nema podataka",
    selectAll: "Izaberi trenutnu stranicu",
    selectInvert: "Obrni izbor trenutne stranice",
    selectNone: "Obriši sve podatke",
    selectionAll: "Izaberi sve podatke",
    sortTitle: "Sortiraj",
    expand: "Proširi red",
    collapse: "Skupi red",
    triggerDesc: "Klikni da sortiraš po padajućem redosledu",
    triggerAsc: "Klikni da sortiraš po rastućem redosledu",
    cancelSort: "Klikni da otkažeš sortiranje"
  },
  Tour: {
    Next: "Sledeće",
    Previous: "Prethodno",
    Finish: "Završi"
  },
  Modal: {
    okText: "U redu",
    cancelText: "Otkaži",
    justOkText: "U redu"
  },
  Popconfirm: {
    okText: "U redu",
    cancelText: "Otkaži"
  },
  Transfer: {
    titles: ["", ""],
    searchPlaceholder: "Pretraži ovde",
    itemUnit: "stavka",
    itemsUnit: "stavki",
    remove: "Ukloni",
    selectCurrent: "Izaberi trenutnu stranicu",
    removeCurrent: "Ukloni trenutnu stranicu",
    selectAll: "Izaberi sve podatke",
    removeAll: "Ukloni sve podatke",
    selectInvert: "Obrni izbor trenutne stranice"
  },
  Upload: {
    uploading: "Otpremanje...",
    removeFile: "Ukloni datoteku",
    uploadError: "Greška pri otpremanju",
    previewFile: "Pregledaj datoteku",
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
    copied: "Kopirano",
    expand: "Proširi"
  },
  Form: {
    optional: "(opcionalno)",
    defaultValidateMessages: {
      default: "Greška pri proveri valjanosti za ${label}",
      required: "Unesi ${label}",
      enum: "${label} mora da bude nešto od [${enum}]",
      whitespace: "${label} ne može biti prazan znak",
      date: {
        format: "${label} format datuma je nevažeći",
        parse: "${label} se ne može konvertovati u datum",
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
        len: "${label} mora da sadrži ${len} znakova",
        min: "${label} mora da sadrži bar ${min} znakova",
        max: "${label} mora da sadrži do ${max} znakova",
        range: "${label} mora da sadrži između ${min} i ${max} znakova"
      },
      number: {
        len: "${label} mora biti jednak ${len}",
        min: "${label} mora biti najmanje ${min}",
        max: "${label} mora biti najviše ${max}",
        range: "${label} mora biti između ${min} i ${max}"
      },
      array: {
        len: "Mora biti ${len} ${label}",
        min: "Najmanje ${min} ${label}",
        max: "najviše ${max} ${label}",
        range: "Iznos ${label} mora biti između ${min} i ${max}"
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
l.default = w;
var _ = l;
const C = /* @__PURE__ */ k(_), q = /* @__PURE__ */ S({
  __proto__: null,
  default: C
}, [_]);
export {
  q as s
};
