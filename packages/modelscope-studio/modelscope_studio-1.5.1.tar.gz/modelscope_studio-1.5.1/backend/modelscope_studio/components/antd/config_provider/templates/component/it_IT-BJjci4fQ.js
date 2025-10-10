import { c as $ } from "./Index-Bv07WiuH.js";
import { i as o, o as b, c as T } from "./config-provider-ROh4C3n3.js";
function x(u, v) {
  for (var m = 0; m < v.length; m++) {
    const a = v[m];
    if (typeof a != "string" && !Array.isArray(a)) {
      for (const t in a)
        if (t !== "default" && !(t in u)) {
          const p = Object.getOwnPropertyDescriptor(a, t);
          p && Object.defineProperty(u, t, p.get ? p : {
            enumerable: !0,
            get: () => a[t]
          });
        }
    }
  }
  return Object.freeze(Object.defineProperty(u, Symbol.toStringTag, {
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
  items_per_page: "/ pagina",
  jump_to: "vai a",
  jump_to_confirm: "Conferma",
  page: "Pagina",
  // Pagination
  prev_page: "Pagina precedente",
  next_page: "Pagina successiva",
  prev_5: "Precedente 5 pagine",
  next_5: "Prossime 5 pagine",
  prev_3: "Precedente 3 pagine",
  next_3: "Prossime 3 pagine",
  page_size: "dimensioni della pagina"
};
n.default = P;
var c = {}, r = {}, d = {}, S = o.default;
Object.defineProperty(d, "__esModule", {
  value: !0
});
d.default = void 0;
var f = S(b), y = T, I = (0, f.default)((0, f.default)({}, y.commonLocale), {}, {
  locale: "it_IT",
  today: "Oggi",
  now: "Adesso",
  backToToday: "Torna ad oggi",
  ok: "OK",
  clear: "Cancella",
  week: "Settimana",
  month: "Mese",
  year: "Anno",
  timeSelect: "Seleziona l'ora",
  dateSelect: "Seleziona la data",
  monthSelect: "Seleziona il mese",
  yearSelect: "Seleziona l'anno",
  decadeSelect: "Seleziona il decennio",
  dateFormat: "D/M/YYYY",
  dateTimeFormat: "D/M/YYYY HH:mm:ss",
  previousMonth: "Il mese scorso (PageUp)",
  nextMonth: "Il prossimo mese (PageDown)",
  previousYear: "L'anno scorso (Control + sinistra)",
  nextYear: "L'anno prossimo (Control + destra)",
  previousDecade: "Ultimo decennio",
  nextDecade: "Prossimo decennio",
  previousCentury: "Secolo precedente",
  nextCentury: "Prossimo secolo"
});
d.default = I;
var i = {};
Object.defineProperty(i, "__esModule", {
  value: !0
});
i.default = void 0;
const C = {
  placeholder: "Selezionare l'orario",
  rangePlaceholder: ["Inizio orario", "Fine orario"]
};
i.default = C;
var g = o.default;
Object.defineProperty(r, "__esModule", {
  value: !0
});
r.default = void 0;
var h = g(d), z = g(i);
const O = {
  lang: Object.assign({
    placeholder: "Selezionare la data",
    rangePlaceholder: ["Data d'inizio", "Data di fine"]
  }, h.default),
  timePickerLocale: Object.assign({}, z.default)
};
r.default = O;
var j = o.default;
Object.defineProperty(c, "__esModule", {
  value: !0
});
c.default = void 0;
var D = j(r);
c.default = D.default;
var s = o.default;
Object.defineProperty(l, "__esModule", {
  value: !0
});
l.default = void 0;
var M = s(n), A = s(c), R = s(r), k = s(i);
const e = " ${label} non è un ${type} valido", E = {
  locale: "it",
  Pagination: M.default,
  DatePicker: R.default,
  TimePicker: k.default,
  Calendar: A.default,
  global: {
    placeholder: "Selezionare",
    close: "Chiudi"
  },
  Table: {
    filterTitle: "Menù Filtro",
    filterConfirm: "OK",
    filterReset: "Reset",
    filterEmptyText: "Senza filtri",
    filterCheckAll: "Seleziona tutti",
    filterSearchPlaceholder: "Cerca nei filtri",
    emptyText: "Senza dati",
    selectAll: "Seleziona pagina corrente",
    selectInvert: "Inverti selezione nella pagina corrente",
    selectNone: "Deseleziona tutto",
    selectionAll: "Seleziona tutto",
    sortTitle: "Ordina",
    expand: "Espandi riga",
    collapse: "Comprimi riga ",
    triggerDesc: "Clicca per ordinare in modo discendente",
    triggerAsc: "Clicca per ordinare in modo ascendente",
    cancelSort: "Clicca per eliminare l'ordinamento"
  },
  Tour: {
    Next: "Successivo",
    Previous: "Precedente",
    Finish: "Termina"
  },
  Modal: {
    okText: "OK",
    cancelText: "Annulla",
    justOkText: "OK"
  },
  Popconfirm: {
    okText: "OK",
    cancelText: "Annulla"
  },
  Transfer: {
    titles: ["", ""],
    searchPlaceholder: "Cerca qui",
    itemUnit: "elemento",
    itemsUnit: "elementi",
    remove: "Elimina",
    selectCurrent: "Seleziona la pagina corrente",
    removeCurrent: "Rimuovi la pagina corrente",
    selectAll: "Seleziona tutti i dati",
    removeAll: "Rimuovi tutti i dati",
    selectInvert: "Inverti la pagina corrente"
  },
  Upload: {
    uploading: "Caricamento...",
    removeFile: "Rimuovi il file",
    uploadError: "Errore di caricamento",
    previewFile: "Anteprima file",
    downloadFile: "Scarica file"
  },
  Empty: {
    description: "Nessun dato"
  },
  Icon: {
    icon: "icona"
  },
  Text: {
    edit: "modifica",
    copy: "copia",
    copied: "copia effettuata",
    expand: "espandi"
  },
  Form: {
    optional: "(opzionale)",
    defaultValidateMessages: {
      default: "Errore di convalida del campo ${label}",
      required: "Si prega di inserire ${label}",
      enum: "${label} deve essere uno di [${enum}]",
      whitespace: "${label} non può essere un carattere vuoto",
      date: {
        format: "Il formato della data ${label} non è valido",
        parse: "${label} non può essere convertito in una data",
        invalid: "${label} non è una data valida"
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
        len: "${label} deve avere ${len} caratteri",
        min: "${label} deve contenere almeno ${min} caratteri",
        max: "${label} deve contenere fino a ${max} caratteri",
        range: "${label} deve contenere tra ${min}-${max} caratteri"
      },
      number: {
        len: "${label} deve essere uguale a ${len}",
        min: "${label} valore minimo è ${min}",
        max: "${label} valor e massimo è ${max}",
        range: "${label} deve essere compreso tra ${min}-${max}"
      },
      array: {
        len: "Deve essere ${len} ${label}",
        min: "Almeno ${min} ${label}",
        max: "Massimo ${max} ${label}",
        range: "Il totale di ${label} deve essere compreso tra ${min}-${max}"
      },
      pattern: {
        mismatch: "${label} non corrisponde al modello ${pattern}"
      }
    }
  },
  Image: {
    preview: "Anteprima"
  },
  QRCode: {
    expired: "Codice QR scaduto",
    refresh: "Ricarica",
    scanned: "Scansionato"
  },
  ColorPicker: {
    presetEmpty: "Vuoto",
    transparent: "Trasparente",
    singleColor: "Tinta unita",
    gradientColor: "Gradiente"
  }
};
l.default = E;
var _ = l;
const F = /* @__PURE__ */ $(_), q = /* @__PURE__ */ x({
  __proto__: null,
  default: F
}, [_]);
export {
  q as i
};
