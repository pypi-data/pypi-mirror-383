import { a as y } from "./XProvider-C2bF5aL8.js";
import { i as o, o as _, c as $ } from "./config-provider-CivlQzIf.js";
function j(c, v) {
  for (var m = 0; m < v.length; m++) {
    const a = v[m];
    if (typeof a != "string" && !Array.isArray(a)) {
      for (const t in a)
        if (t !== "default" && !(t in c)) {
          const p = Object.getOwnPropertyDescriptor(a, t);
          p && Object.defineProperty(c, t, p.get ? p : {
            enumerable: !0,
            get: () => a[t]
          });
        }
    }
  }
  return Object.freeze(Object.defineProperty(c, Symbol.toStringTag, {
    value: "Module"
  }));
}
var n = {}, i = {};
Object.defineProperty(i, "__esModule", {
  value: !0
});
i.default = void 0;
var h = {
  // Options
  items_per_page: "/ strana",
  jump_to: "Choď na",
  jump_to_confirm: "potvrdit",
  page: "",
  // Pagination
  prev_page: "Predchádzajúca strana",
  next_page: "Nasledujúca strana",
  prev_5: "Predchádzajúcich 5 strán",
  next_5: "Nasledujúcich 5 strán",
  prev_3: "Predchádzajúce 3 strany",
  next_3: "Nasledujúce 3 strany",
  page_size: "Page Size"
};
i.default = h;
var d = {}, r = {}, s = {}, g = o.default;
Object.defineProperty(s, "__esModule", {
  value: !0
});
s.default = void 0;
var b = g(_), z = $, x = (0, b.default)((0, b.default)({}, z.commonLocale), {}, {
  locale: "sk_SK",
  today: "Dnes",
  now: "Teraz",
  backToToday: "Späť na dnes",
  ok: "OK",
  clear: "Vymazať",
  week: "Týždeň",
  month: "Mesiac",
  year: "Rok",
  timeSelect: "Vybrať čas",
  dateSelect: "Vybrať dátum",
  monthSelect: "Vybrať mesiac",
  yearSelect: "Vybrať rok",
  decadeSelect: "Vybrať dekádu",
  dateFormat: "D.M.YYYY",
  dateTimeFormat: "D.M.YYYY HH:mm:ss",
  previousMonth: "Predchádzajúci mesiac (PageUp)",
  nextMonth: "Nasledujúci mesiac (PageDown)",
  previousYear: "Predchádzajúci rok (Control + left)",
  nextYear: "Nasledujúci rok (Control + right)",
  previousDecade: "Predchádzajúca dekáda",
  nextDecade: "Nasledujúca dekáda",
  previousCentury: "Predchádzajúce storočie",
  nextCentury: "Nasledujúce storočie"
});
s.default = x;
var l = {};
Object.defineProperty(l, "__esModule", {
  value: !0
});
l.default = void 0;
const S = {
  placeholder: "Vybrať čas"
};
l.default = S;
var f = o.default;
Object.defineProperty(r, "__esModule", {
  value: !0
});
r.default = void 0;
var P = f(s), O = f(l);
const K = {
  lang: Object.assign({
    placeholder: "Vybrať dátum",
    rangePlaceholder: ["Od", "Do"]
  }, P.default),
  timePickerLocale: Object.assign({}, O.default)
};
r.default = K;
var T = o.default;
Object.defineProperty(d, "__esModule", {
  value: !0
});
d.default = void 0;
var D = T(r);
d.default = D.default;
var u = o.default;
Object.defineProperty(n, "__esModule", {
  value: !0
});
n.default = void 0;
var M = u(i), V = u(d), N = u(r), C = u(l);
const e = "${label} nie je platný ${type}", Y = {
  locale: "sk",
  Pagination: M.default,
  DatePicker: N.default,
  TimePicker: C.default,
  Calendar: V.default,
  global: {
    placeholder: "Prosím vyber",
    close: "Zavrieť"
  },
  Table: {
    filterTitle: "Filter",
    filterConfirm: "OK",
    filterReset: "Obnoviť",
    filterEmptyText: "Žiadne filtre",
    filterCheckAll: "Vyber všetky položky",
    filterSearchPlaceholder: "Vyhľadaj vo filtroch",
    emptyText: "Žiadne dáta",
    selectAll: "Označ všetky položky",
    selectInvert: "Opačný výber položiek",
    selectNone: "Odznač všetko",
    selectionAll: "Označ všetko",
    sortTitle: "Zoradiť",
    expand: "Rozbaliť riadok",
    collapse: "Zbaliť riadok",
    triggerDesc: "Kliknutím zoradíš zostupne",
    triggerAsc: "Kliknutím zoradíš vzostupne",
    cancelSort: "Kliknutím zrušíš zoradenie"
  },
  Tour: {
    Next: "Ďalej",
    Previous: "Späť",
    Finish: "Dokončiť"
  },
  Modal: {
    okText: "OK",
    cancelText: "Zrušiť",
    justOkText: "OK"
  },
  Popconfirm: {
    okText: "OK",
    cancelText: "Zrušiť"
  },
  Transfer: {
    titles: ["", ""],
    searchPlaceholder: "Vyhľadávanie",
    itemUnit: "položka",
    itemsUnit: "položiek",
    remove: "Odstráň",
    selectCurrent: "Vyber aktuálnu stranu",
    removeCurrent: "Zmaž aktuálnu stranu",
    selectAll: "Označ všetko",
    removeAll: "Odznač všetko",
    selectInvert: "Opačný výber"
  },
  Upload: {
    uploading: "Nahrávanie...",
    removeFile: "Odstrániť súbor",
    uploadError: "Chyba pri nahrávaní",
    previewFile: "Zobraziť súbor",
    downloadFile: "Stiahnuť súbor"
  },
  Empty: {
    description: "Žiadne dáta"
  },
  Icon: {
    icon: "ikona"
  },
  Text: {
    edit: "Upraviť",
    copy: "Kopírovať",
    copied: "Skopírované",
    expand: "Zväčšiť"
  },
  Form: {
    optional: "(nepovinné)",
    defaultValidateMessages: {
      default: "Validačná chyba poľa pre ${label}",
      required: "Prosím vlož ${label}",
      enum: "${label} musí byť jeden z [${enum}]",
      whitespace: "${label} nemôže byť prázdny znak",
      date: {
        format: "${label} formát dátumu je neplatný",
        parse: "${label} nie je možné konvertovať na dátum",
        invalid: "${label} je neplatný dátum"
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
        len: "${label} musí byť ${len} znakov",
        min: "${label} musí byť aspoň ${min} znakov",
        max: "${label} musí byť do ${max} znakov",
        range: "${label} musí byť medzi ${min}-${max} znakmi"
      },
      number: {
        len: "${label} musí byť rovnaký ako ${len}",
        min: "${label} musí byť minimálne ${min}",
        max: "${label} musí byť maximálne ${max}",
        range: "${label} musí byť medzi ${min}-${max}"
      },
      array: {
        len: "Musí byť ${len} ${label}",
        min: "Aspoň ${min} ${label}",
        max: "Najviac ${max} ${label}",
        range: "Počet ${label} musí byť medzi ${min}-${max}"
      },
      pattern: {
        mismatch: "${label} nezodpovedá vzoru ${pattern}"
      }
    }
  },
  Image: {
    preview: "Náhľad"
  }
};
n.default = Y;
var k = n;
const A = /* @__PURE__ */ y(k), R = /* @__PURE__ */ j({
  __proto__: null,
  default: A
}, [k]);
export {
  R as s
};
