import { c as _ } from "./Index-Bv07WiuH.js";
import { i as o, o as $, c as k } from "./config-provider-ROh4C3n3.js";
function h(u, v) {
  for (var m = 0; m < v.length; m++) {
    const t = v[m];
    if (typeof t != "string" && !Array.isArray(t)) {
      for (const a in t)
        if (a !== "default" && !(a in u)) {
          const p = Object.getOwnPropertyDescriptor(t, a);
          p && Object.defineProperty(u, a, p.get ? p : {
            enumerable: !0,
            get: () => t[a]
          });
        }
    }
  }
  return Object.freeze(Object.defineProperty(u, Symbol.toStringTag, {
    value: "Module"
  }));
}
var n = {}, s = {};
Object.defineProperty(s, "__esModule", {
  value: !0
});
s.default = void 0;
var g = {
  // Options
  items_per_page: "/ strana",
  jump_to: "Přejít",
  jump_to_confirm: "potvrdit",
  page: "",
  // Pagination
  prev_page: "Předchozí strana",
  next_page: "Následující strana",
  prev_5: "Předchozích 5 stran",
  next_5: "Následujících 5 stran",
  prev_3: "Předchozí 3 strany",
  next_3: "Následující 3 strany",
  page_size: "velikost stránky"
};
s.default = g;
var d = {}, r = {}, i = {}, P = o.default;
Object.defineProperty(i, "__esModule", {
  value: !0
});
i.default = void 0;
var b = P($), x = k, z = (0, b.default)((0, b.default)({}, x.commonLocale), {}, {
  locale: "cs_CZ",
  today: "Dnes",
  now: "Nyní",
  backToToday: "Zpět na dnešek",
  ok: "OK",
  clear: "Vymazat",
  week: "Týden",
  month: "Měsíc",
  year: "Rok",
  timeSelect: "Vybrat čas",
  dateSelect: "Vybrat datum",
  monthSelect: "Vyberte měsíc",
  yearSelect: "Vyberte rok",
  decadeSelect: "Vyberte dekádu",
  dateFormat: "D.M.YYYY",
  dateTimeFormat: "D.M.YYYY HH:mm:ss",
  previousMonth: "Předchozí měsíc (PageUp)",
  nextMonth: "Následující (PageDown)",
  previousYear: "Předchozí rok (Control + left)",
  nextYear: "Následující rok (Control + right)",
  previousDecade: "Předchozí dekáda",
  nextDecade: "Následující dekáda",
  previousCentury: "Předchozí století",
  nextCentury: "Následující století"
});
i.default = z;
var l = {};
Object.defineProperty(l, "__esModule", {
  value: !0
});
l.default = void 0;
const j = {
  placeholder: "Vybrat čas"
};
l.default = j;
var f = o.default;
Object.defineProperty(r, "__esModule", {
  value: !0
});
r.default = void 0;
var C = f(i), O = f(l);
const Z = {
  lang: Object.assign({
    placeholder: "Vybrat datum",
    rangePlaceholder: ["Od", "Do"]
  }, C.default),
  timePickerLocale: Object.assign({}, O.default)
};
r.default = Z;
var T = o.default;
Object.defineProperty(d, "__esModule", {
  value: !0
});
d.default = void 0;
var D = T(r);
d.default = D.default;
var c = o.default;
Object.defineProperty(n, "__esModule", {
  value: !0
});
n.default = void 0;
var V = c(s), M = c(d), N = c(r), S = c(l);
const e = "${label} není platný ${type}", R = {
  locale: "cs",
  Pagination: V.default,
  DatePicker: N.default,
  TimePicker: S.default,
  Calendar: M.default,
  global: {
    placeholder: "Prosím vyber",
    close: "Zavřít"
  },
  Table: {
    filterTitle: "Filtr",
    filterConfirm: "Potvrdit",
    filterReset: "Obnovit",
    filterEmptyText: "Žádné filtry",
    filterCheckAll: "Vybrat všechny položky",
    filterSearchPlaceholder: "Vyhledat ve filtrech",
    emptyText: "Žádná data",
    selectAll: "Vybrat všechny řádky na současné stránce",
    selectInvert: "Invertovat výběr na současné stránce",
    selectNone: "Odznačit vše",
    selectionAll: "Vybrat všechny řádky",
    sortTitle: "Řadit",
    expand: "Rozbalit řádek",
    collapse: "Zabalit řádek",
    triggerDesc: "Klikni pro sestupné řazení",
    triggerAsc: "Klikni pro vzestupné řazení",
    cancelSort: "Klikni pro zrušení řazení"
  },
  Tour: {
    Next: "Další",
    Previous: "Předchozí",
    Finish: "Dokončit"
  },
  Modal: {
    okText: "OK",
    cancelText: "Zrušit",
    justOkText: "OK"
  },
  Popconfirm: {
    okText: "OK",
    cancelText: "Zrušit"
  },
  Transfer: {
    titles: ["", ""],
    searchPlaceholder: "Vyhledávání",
    itemUnit: "položka",
    itemsUnit: "položek",
    remove: "Odstranit",
    selectCurrent: "Vybrat aktuální stranu",
    removeCurrent: "Smazat aktuální stranu",
    selectAll: "Označit vše",
    removeAll: "Odznačit vše",
    selectInvert: "Opačný výběr"
  },
  Upload: {
    uploading: "Nahrávání...",
    removeFile: "Odstranit soubor",
    uploadError: "Chyba při nahrávání",
    previewFile: "Zobrazit soubor",
    downloadFile: "Stáhnout soubor"
  },
  Empty: {
    description: "Žádná data"
  },
  Icon: {
    icon: "ikona"
  },
  Text: {
    edit: "Upravit",
    copy: "Kopírovat",
    copied: "Zkopírované",
    expand: "Zvětšit"
  },
  Form: {
    optional: "(nepovinné)",
    defaultValidateMessages: {
      default: "Validační chyba pole pro ${label}",
      required: "Prosím vložte ${label}",
      enum: "${label} musí být jeden z [${enum}]",
      whitespace: "${label} nemůže být prázdný znak",
      date: {
        format: "${label} formát datumu je neplatný",
        parse: "${label} není možné konvertovat na datum",
        invalid: "${label} je neplatné datum"
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
        len: "${label} musí být ${len} znaků",
        min: "${label} musí být alespoň ${min} znaků",
        max: "${label} musí být do ${max} znaků",
        range: "${label} musí být mezi ${min}-${max} znaky"
      },
      number: {
        len: "${label} musí být stejný jako ${len}",
        min: "${label} musí být minimálně ${min}",
        max: "${label} musí být maximálně ${max}",
        range: "${label} musí být mezi ${min}-${max}"
      },
      array: {
        len: "Musí být ${len} ${label}",
        min: "Alespoň ${min} ${label}",
        max: "Nejvíc ${max} ${label}",
        range: "Počet ${label} musí být mezi ${min}-${max}"
      },
      pattern: {
        mismatch: "${label} neodpovídá vzoru ${pattern}"
      }
    }
  },
  Image: {
    preview: "Náhled"
  },
  QRCode: {
    expired: "QR kód vypršel",
    refresh: "Obnovit",
    scanned: "Naskenováno"
  },
  ColorPicker: {
    presetEmpty: "Prázdné",
    transparent: "Průhledné",
    singleColor: "Jednobarevné",
    gradientColor: "Přechodové"
  }
};
n.default = R;
var y = n;
const Y = /* @__PURE__ */ _(y), w = /* @__PURE__ */ h({
  __proto__: null,
  default: Y
}, [y]);
export {
  w as c
};
