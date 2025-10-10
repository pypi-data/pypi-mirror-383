import { a as b } from "./XProvider-C2bF5aL8.js";
import { i as o, o as g, c as x } from "./config-provider-CivlQzIf.js";
function k(p, f) {
  for (var s = 0; s < f.length; s++) {
    const a = f[s];
    if (typeof a != "string" && !Array.isArray(a)) {
      for (const l in a)
        if (l !== "default" && !(l in p)) {
          const m = Object.getOwnPropertyDescriptor(a, l);
          m && Object.defineProperty(p, l, m.get ? m : {
            enumerable: !0,
            get: () => a[l]
          });
        }
    }
  }
  return Object.freeze(Object.defineProperty(p, Symbol.toStringTag, {
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
  items_per_page: "/ ಪುಟ",
  jump_to: "ಜಿಗಿತವನ್ನು",
  jump_to_confirm: "ಖಚಿತಪಡಿಸಲು ಜಿಗಿತವನ್ನು",
  page: "",
  // Pagination
  prev_page: "ಹಿಂದಿನ ಪುಟ",
  next_page: "ಮುಂದಿನ ಪುಟ",
  prev_5: "ಹಿಂದಿನ 5 ಪುಟಗಳು",
  next_5: "ಮುಂದಿನ 5 ಪುಟಗಳು",
  prev_3: "ಹಿಂದಿನ 3 ಪುಟಗಳು",
  next_3: "ಮುಂದಿನ 3 ಪುಟಗಳು",
  page_size: "Page Size"
};
i.default = h;
var d = {}, t = {}, c = {}, y = o.default;
Object.defineProperty(c, "__esModule", {
  value: !0
});
c.default = void 0;
var _ = y(g), P = x, I = (0, _.default)((0, _.default)({}, P.commonLocale), {}, {
  locale: "kn_IN",
  today: "ಇಂದು",
  now: "ಈಗ",
  backToToday: "ಇಂದು ಹಿಂದಿರುಗಿ",
  ok: "ಸರಿ",
  clear: "ಸ್ಪಷ್ಟ",
  week: "ವಾರ",
  month: "ತಿಂಗಳು",
  year: "ವರ್ಷ",
  timeSelect: "ಸಮಯ ಆಯ್ಕೆಮಾಡಿ",
  dateSelect: "ದಿನಾಂಕವನ್ನು ಆಯ್ಕೆ ಮಾಡಿ",
  weekSelect: "ಒಂದು ವಾರದ ಆರಿಸಿ",
  monthSelect: "ಒಂದು ತಿಂಗಳು ಆಯ್ಕೆಮಾಡಿ",
  yearSelect: "ಒಂದು ವರ್ಷ ಆರಿಸಿ",
  decadeSelect: "ಒಂದು ದಶಕದ ಆಯ್ಕೆಮಾಡಿ",
  dateFormat: "M/D/YYYY",
  dateTimeFormat: "M/D/YYYY HH:mm:ss",
  previousMonth: "ಹಿಂದಿನ ತಿಂಗಳು (ಪೇಜ್ಅಪ್)",
  nextMonth: "ಮುಂದಿನ ತಿಂಗಳು (ಪೇಜ್ಡೌನ್)",
  previousYear: "ಕಳೆದ ವರ್ಷ (Ctrl + ಎಡ)",
  nextYear: "ಮುಂದಿನ ವರ್ಷ (Ctrl + ಬಲ)",
  previousDecade: "ಕಳೆದ ದಶಕ",
  nextDecade: "ಮುಂದಿನ ದಶಕ",
  previousCentury: "ಕಳೆದ ಶತಮಾನ",
  nextCentury: "ಮುಂದಿನ ಶತಮಾನ"
});
c.default = I;
var r = {};
Object.defineProperty(r, "__esModule", {
  value: !0
});
r.default = void 0;
const N = {
  placeholder: "ಸಮಯ ಆಯ್ಕೆಮಾಡಿ"
};
r.default = N;
var $ = o.default;
Object.defineProperty(t, "__esModule", {
  value: !0
});
t.default = void 0;
var j = $(c), T = $(r);
const M = {
  lang: Object.assign({
    placeholder: "ದಿನಾಂಕ ಆಯ್ಕೆಮಾಡಿ",
    yearPlaceholder: "ವರ್ಷ ಆಯ್ಕೆಮಾಡಿ",
    rangePlaceholder: ["ಪ್ರಾರಂಭ ದಿನಾಂಕ", "ಅಂತಿಮ ದಿನಾಂಕ"],
    quarterPlaceholder: "ಕಾಲುಭಾಗವನ್ನು ಆಯ್ಕೆಮಾಡಿ",
    monthPlaceholder: "ತಿಂಗಳನ್ನು ಆಯ್ಕೆಮಾಡಿ",
    weekPlaceholder: "ವಾರವನ್ನು ಆಯ್ಕೆಮಾಡಿ",
    rangeYearPlaceholder: ["ಉದ್ಘಾಟನಾ ವರ್ಷ", "ಅಂತಿಮ ವರ್ಷ"],
    rangeQuarterPlaceholder: ["ತ್ರೈಮಾಸಿಕದ ಆರಂಭ", "ಅಂತಿಮ ತ್ರೈಮಾಸಿಕ"],
    rangeMonthPlaceholder: ["ಆರಂಭಿಕ ತಿಂಗಳು", "ಅಂತಿಮ ತಿಂಗಳು"],
    rangeWeekPlaceholder: ["ತೆರೆಯುವ ವಾರ", "ಅಂತಿಮ ವಾರ"]
  }, j.default),
  timePickerLocale: Object.assign({}, T.default)
};
t.default = M;
var O = o.default;
Object.defineProperty(d, "__esModule", {
  value: !0
});
d.default = void 0;
var D = O(t);
d.default = D.default;
var u = o.default;
Object.defineProperty(n, "__esModule", {
  value: !0
});
n.default = void 0;
var S = u(i), Y = u(d), C = u(t), w = u(r);
const e = "${label} ಮಾನ್ಯವಾದ ${type} ಅಲ್ಲ", F = {
  locale: "kn",
  Pagination: S.default,
  DatePicker: C.default,
  TimePicker: w.default,
  Calendar: Y.default,
  // locales for all comoponents
  global: {
    placeholder: "ದಯವಿಟ್ಟು ಆರಿಸಿ",
    close: "ಮುಚ್ಚಿ"
  },
  Table: {
    filterTitle: "ಪಟ್ಟಿ ಸೋಸಿ",
    filterConfirm: "ಸರಿ",
    filterReset: "ಮರುಹೊಂದಿಸಿ",
    emptyText: "ಮಾಹಿತಿ ಇಲ್ಲ",
    selectAll: "ಪ್ರಸ್ತುತ ಪುಟವನ್ನು ಆಯ್ಕೆಮಾಡಿ",
    selectInvert: "ಪ್ರಸ್ತುತ ಪುಟವನ್ನು ತಿರುಗಿಸಿ",
    sortTitle: "ವಿಂಗಡಿಸಿ",
    filterEmptyText: "ಫಿಲ್ಟರ್ ಇಲ್ಲ",
    filterCheckAll: "ಎಲ್ಲಾ ಐಟಂಗಳನ್ನು ಆಯ್ಕೆಮಾಡಿ",
    filterSearchPlaceholder: "ಫಿಲ್ಟರ್‌ಗಳೊಂದಿಗೆ ಹುಡುಕಿ",
    selectNone: "ಯಾವುದನ್ನೂ ಆಯ್ಕೆ ಮಾಡಬೇಡಿ",
    selectionAll: "ಎಲ್ಲಾ ಡೇಟಾವನ್ನು ಆಯ್ಕೆಮಾಡಿ",
    expand: "ಶ್ರೇಣಿಯನ್ನು ವಿಸ್ತರಿಸಿ",
    collapse: "ಸಾಲುಗಳನ್ನು ಸಂಕುಚಿಸಿ",
    triggerDesc: "ಅವರೋಹಣ ಕ್ರಮದಲ್ಲಿ ವಿಂಗಡಿಸಲು ಕ್ಲಿಕ್ ಮಾಡಿ",
    triggerAsc: "ಏರೋಹಣ ಕ್ರಮದಲ್ಲಿ ವಿಂಗಡಿಸಲು ಕ್ಲಿಕ್ ಮಾಡಿ",
    cancelSort: "ವಿಂಗಡಣೆಯನ್ನು ರದ್ದುಗೊಳಿಸಲು ಕ್ಲಿಕ್ ಮಾಡಿ"
  },
  Tour: {
    Next: "ಮುಂದುವರೆಸಿ",
    Previous: "ಹಿಂದೆಯಾಗಿ",
    Finish: "ಮುಗಿಸಿ"
  },
  Modal: {
    okText: "ಸರಿ",
    cancelText: "ರದ್ದು",
    justOkText: "ಸರಿ"
  },
  Popconfirm: {
    okText: "ಸರಿ",
    cancelText: "ರದ್ದು"
  },
  Transfer: {
    titles: ["", ""],
    notFoundContent: "ದೊರೆತಿಲ್ಲ",
    searchPlaceholder: "ಇಲ್ಲಿ ಹುಡುಕಿ",
    itemUnit: "ವಿಷಯ",
    itemsUnit: "ವಿಷಯಗಳು"
  },
  Upload: {
    uploading: "ಏರಿಸಿ...",
    removeFile: "ಫೈಲ್ ತೆಗೆದುಹಾಕಿ",
    uploadError: "ಏರಿಸುವ ದೋಷ",
    previewFile: "ಫೈಲ್ ಮುನ್ನೋಟ",
    downloadFile: "ಫೈಲ್ ಡೌನ್‌ಲೋಡ್ ಮಾಡಿ"
  },
  Empty: {
    description: "ಮಾಹಿತಿ ಇಲ್ಲ"
  },
  Icon: {
    icon: "ಚಿಹ್ನೆ"
  },
  Text: {
    edit: "ಸಂಪಾದಿಸಿ",
    copy: "ಪ್ರತಿಯನ್ನು ತೆಗೆದುಕೊಳ್ಳಿ",
    copied: "ನಕಲಿಸಲಾಗಿದೆ",
    expand: "ಶ್ರೇಣಿಯನ್ನು ವಿಸ್ತರಿಸಿ",
    collapse: "ಸಾಲುಗಳನ್ನು ಸಂಕುಚಿಸಿ"
  },
  Form: {
    optional: "(ಐಚ್ಛಿಕ)",
    defaultValidateMessages: {
      default: "${label} ಗಾಗಿ ಕ್ಷೇತ್ರ ಮೌಲ್ಯೀಕರಣ ದೋಷ",
      required: "${label} ನಮೂದಿಸಿ",
      enum: "${label} [${enum}] ನಲ್ಲಿ ಒಂದಾಗಿರಬೇಕು.",
      whitespace: "${label} ಖಾಲಿ ಅಕ್ಷರವಾಗಿರಬಾರದು",
      date: {
        format: "${label} ದಿನಾಂಕ ಸ್ವರೂಪವು ಅಮಾನ್ಯವಾಗಿದೆ",
        parse: "${label} ಅನ್ನು ದಿನಾಂಕಕ್ಕೆ ಪರಿವರ್ತಿಸಲಾಗುವುದಿಲ್ಲ",
        invalid: "${label} ಒಂದು ಅಮಾನ್ಯ ದಿನಾಂಕವಾಗಿದೆ"
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
        len: "${label} ${len} ಅಕ್ಷರಗಳಾಗಿರಬೇಕು",
        min: "${label} ಕನಿಷ್ಠ ${min} ಅಕ್ಷರಗಳಾಗಿರಬೇಕು",
        max: "${label} ಗರಿಷ್ಠ ${max} ಅಕ್ಷರಗಳಾಗಿರಬೇಕು",
        range: "${label} ${min}-${max} ಅಕ್ಷರಗಳ ನಡುವೆ ಇರಬೇಕು"
      },
      number: {
        len: "${label} ${len} ಗೆ ಸಮನಾಗಿರಬೇಕು",
        min: "${label} ಕನಿಷ್ಠ ${min} ಆಗಿರಬೇಕು",
        max: "${label} ಹೆಚ್ಚೆಂದರೆ ${max} ಆಗಿರಬೇಕು",
        range: "${label} ${min}-${max} ನಡುವೆ ಇರಬೇಕು"
      },
      array: {
        len: "${label} ${len} ಗೆ ಸಮನಾಗಿರಬೇಕು",
        min: "${label} ಕನಿಷ್ಠ ${min} ಆಗಿರಬೇಕು",
        max: "${label} ಹೆಚ್ಚೆಂದರೆ ${max} ಆಗಿರಬೇಕು",
        range: "${label} ${min}-${max} ನಡುವೆ ಇರಬೇಕು"
      },
      pattern: {
        mismatch: "${label} ಮಾದರಿಯು ${pattern} ಗೆ ಹೊಂದಿಕೆಯಾಗುವುದಿಲ್ಲ"
      }
    }
  },
  Image: {
    preview: "ಮುನ್ನೋಟ"
  },
  QRCode: {
    expired: "QR ಕೋಡ್ ಅವಧಿ ಮೀರಿದೆ",
    refresh: "ನವೀಕರಿಸಿ"
  }
};
n.default = F;
var v = n;
const R = /* @__PURE__ */ b(v), E = /* @__PURE__ */ k({
  __proto__: null,
  default: R
}, [v]);
export {
  E as k
};
