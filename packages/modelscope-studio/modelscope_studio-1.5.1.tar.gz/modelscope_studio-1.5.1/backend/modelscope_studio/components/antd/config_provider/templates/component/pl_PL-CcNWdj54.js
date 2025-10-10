import { c as w } from "./Index-Bv07WiuH.js";
import { i as o, o as _, c as $ } from "./config-provider-ROh4C3n3.js";
function v(u, y) {
  for (var m = 0; m < y.length; m++) {
    const a = y[m];
    if (typeof a != "string" && !Array.isArray(a)) {
      for (const t in a)
        if (t !== "default" && !(t in u)) {
          const c = Object.getOwnPropertyDescriptor(a, t);
          c && Object.defineProperty(u, t, c.get ? c : {
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
var i = {}, n = {};
Object.defineProperty(n, "__esModule", {
  value: !0
});
n.default = void 0;
var k = {
  // Options
  items_per_page: "na stronę",
  jump_to: "Idź do",
  jump_to_confirm: "potwierdź",
  page: "",
  // Pagination
  prev_page: "Poprzednia strona",
  next_page: "Następna strona",
  prev_5: "Poprzednie 5 stron",
  next_5: "Następne 5 stron",
  prev_3: "Poprzednie 3 strony",
  next_3: "Następne 3 strony",
  page_size: "rozmiar strony"
};
n.default = k;
var s = {}, r = {}, d = {}, P = o.default;
Object.defineProperty(d, "__esModule", {
  value: !0
});
d.default = void 0;
var f = P(_), j = $, g = (0, f.default)((0, f.default)({}, j.commonLocale), {}, {
  locale: "pl_PL",
  today: "Dzisiaj",
  now: "Teraz",
  backToToday: "Ustaw dzisiaj",
  ok: "OK",
  clear: "Wyczyść",
  week: "Tydzień",
  month: "Miesiąc",
  year: "Rok",
  timeSelect: "Ustaw czas",
  dateSelect: "Ustaw datę",
  monthSelect: "Wybierz miesiąc",
  yearSelect: "Wybierz rok",
  decadeSelect: "Wybierz dekadę",
  dateFormat: "D/M/YYYY",
  dateTimeFormat: "D/M/YYYY HH:mm:ss",
  previousMonth: "Poprzedni miesiąc (PageUp)",
  nextMonth: "Następny miesiąc (PageDown)",
  previousYear: "Ostatni rok (Ctrl + left)",
  nextYear: "Następny rok (Ctrl + right)",
  previousDecade: "Ostatnia dekada",
  nextDecade: "Następna dekada",
  previousCentury: "Ostatni wiek",
  nextCentury: "Następny wiek"
});
d.default = g;
var l = {};
Object.defineProperty(l, "__esModule", {
  value: !0
});
l.default = void 0;
const x = {
  placeholder: "Wybierz godzinę"
};
l.default = x;
var b = o.default;
Object.defineProperty(r, "__esModule", {
  value: !0
});
r.default = void 0;
var h = b(d), O = b(l);
const L = {
  lang: Object.assign({
    placeholder: "Wybierz datę",
    rangePlaceholder: ["Data początkowa", "Data końcowa"],
    yearFormat: "YYYY",
    monthFormat: "MMMM",
    monthBeforeYear: !0,
    shortWeekDays: ["Niedz", "Pon", "Wt", "Śr", "Czw", "Pt", "Sob"],
    shortMonths: ["Sty", "Lut", "Mar", "Kwi", "Maj", "Cze", "Lip", "Sie", "Wrz", "Paź", "Lis", "Gru"]
  }, h.default),
  timePickerLocale: Object.assign({}, O.default)
};
r.default = L;
var M = o.default;
Object.defineProperty(s, "__esModule", {
  value: !0
});
s.default = void 0;
var T = M(r);
s.default = T.default;
var p = o.default;
Object.defineProperty(i, "__esModule", {
  value: !0
});
i.default = void 0;
var S = p(n), D = p(s), W = p(r), Y = p(l);
const e = "${label} nie posiada poprawnej wartości dla typu ${type}", U = {
  locale: "pl",
  Pagination: S.default,
  DatePicker: W.default,
  TimePicker: Y.default,
  Calendar: D.default,
  global: {
    placeholder: "Wybierz",
    close: "Zamknij"
  },
  Table: {
    filterTitle: "Menu filtra",
    filterConfirm: "OK",
    filterReset: "Usuń filtry",
    filterEmptyText: "Brak filtrów",
    filterCheckAll: "Wybierz wszystkie elementy",
    filterSearchPlaceholder: "Szukaj w filtrach",
    emptyText: "Brak danych",
    selectAll: "Zaznacz bieżącą stronę",
    selectInvert: "Odwróć zaznaczenie",
    selectNone: "Wyczyść",
    selectionAll: "Wybierz wszystkie",
    sortTitle: "Sortowanie",
    expand: "Rozwiń wiersz",
    collapse: "Zwiń wiersz",
    triggerDesc: "Sortuj malejąco",
    triggerAsc: "Sortuj rosnąco",
    cancelSort: "Usuń sortowanie"
  },
  Tour: {
    Next: "Dalej",
    Previous: "Wróć",
    Finish: "Zakończ"
  },
  Modal: {
    okText: "OK",
    cancelText: "Anuluj",
    justOkText: "OK"
  },
  Popconfirm: {
    okText: "OK",
    cancelText: "Anuluj"
  },
  Transfer: {
    titles: ["", ""],
    searchPlaceholder: "Szukaj",
    itemUnit: "obiekt",
    itemsUnit: "obiekty",
    remove: "Usuń",
    selectCurrent: "Wybierz aktualną stronę",
    removeCurrent: "Usuń aktualną stronę",
    selectAll: "Wybierz wszystkie",
    removeAll: "Usuń wszystkie",
    selectInvert: "Odwróć wybór"
  },
  Upload: {
    uploading: "Wysyłanie...",
    removeFile: "Usuń plik",
    uploadError: "Błąd wysyłania",
    previewFile: "Podejrzyj plik",
    downloadFile: "Pobieranie pliku"
  },
  Empty: {
    description: "Brak danych"
  },
  Icon: {
    icon: "Ikona"
  },
  Text: {
    edit: "Edytuj",
    copy: "Kopiuj",
    copied: "Skopiowany",
    expand: "Rozwiń"
  },
  Form: {
    optional: "(opcjonalne)",
    defaultValidateMessages: {
      default: "Błąd walidacji dla pola ${label}",
      required: "Pole ${label} jest wymagane",
      enum: "Pole ${label} musi posiadać wartość z listy: [${enum}]",
      whitespace: "Pole ${label} nie może być puste",
      date: {
        format: "${label} posiada zły format daty",
        parse: "${label} nie może zostać zinterpretowane jako data",
        invalid: "${label} jest niepoprawną datą"
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
        len: "${label} musi posiadać ${len} znaków",
        min: "${label} musi posiadać co namniej ${min} znaków",
        max: "${label} musi posiadać maksymalnie ${max} znaków",
        range: "${label} musi posiadać między ${min} a ${max} znaków"
      },
      number: {
        len: "${label} musi mieć wartość o długości ${len}",
        min: "${label} musi mieć wartość większą lub równą ${min}",
        max: "${label} musi mieć wartość mniejszą lub równą ${max}",
        range: "${label} musi mieć wartość pomiędzy ${min} a ${max}"
      },
      array: {
        len: "${label} musi posiadać ${len} elementów",
        min: "${label} musi posiadać co najmniej ${min} elementów",
        max: "${label} musi posiadać maksymalnie ${max} elementów",
        range: "${label} musi posiadać między ${min} a ${max} elementów"
      },
      pattern: {
        mismatch: "${label} nie posiada wartości zgodnej ze wzorem ${pattern}"
      }
    }
  },
  Image: {
    preview: "Podgląd"
  }
};
i.default = U;
var z = i;
const C = /* @__PURE__ */ w(z), F = /* @__PURE__ */ v({
  __proto__: null,
  default: C
}, [z]);
export {
  F as p
};
