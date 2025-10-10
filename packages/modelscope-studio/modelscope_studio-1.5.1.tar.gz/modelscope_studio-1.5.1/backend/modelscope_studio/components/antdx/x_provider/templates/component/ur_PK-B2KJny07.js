import { a as P } from "./XProvider-C2bF5aL8.js";
import { i as o, o as b, c as g } from "./config-provider-CivlQzIf.js";
function x(s, f) {
  for (var m = 0; m < f.length; m++) {
    const a = f[m];
    if (typeof a != "string" && !Array.isArray(a)) {
      for (const l in a)
        if (l !== "default" && !(l in s)) {
          const p = Object.getOwnPropertyDescriptor(a, l);
          p && Object.defineProperty(s, l, p.get ? p : {
            enumerable: !0,
            get: () => a[l]
          });
        }
    }
  }
  return Object.freeze(Object.defineProperty(s, Symbol.toStringTag, {
    value: "Module"
  }));
}
var n = {}, u = {};
Object.defineProperty(u, "__esModule", {
  value: !0
});
u.default = void 0;
var y = {
  // Options
  items_per_page: "/ صفحہ",
  jump_to: "پاس جاؤ",
  jump_to_confirm: "تصدیق کریں",
  page: "",
  // Pagination
  prev_page: "پچھلا صفحہ",
  next_page: "اگلا صفحہ",
  prev_5: "پچھلے 5 صفحات",
  next_5: "اگلے 5 صفحات",
  prev_3: "پچھلے 3 صفحات",
  next_3: "اگلے 3 صفحات",
  page_size: "Page Size"
};
u.default = y;
var i = {}, r = {}, c = {}, h = o.default;
Object.defineProperty(c, "__esModule", {
  value: !0
});
c.default = void 0;
var _ = h(b), j = g, T = (0, _.default)((0, _.default)({}, j.commonLocale), {}, {
  locale: "ur_PK",
  today: "آج",
  now: "ابھی",
  backToToday: "آج واپس",
  ok: "ٹھیک ہے",
  clear: "صاف",
  week: "ہفتہ",
  month: "مہینہ",
  year: "سال",
  timeSelect: "وقت منتخب کریں",
  dateSelect: "تاریخ منتخب کریں",
  weekSelect: "ایک ہفتہ کا انتخاب کریں",
  monthSelect: "ایک مہینہ کا انتخاب کریں",
  yearSelect: "ایک سال کا انتخاب کریں",
  decadeSelect: "ایک دہائی کا انتخاب کریں",
  dateFormat: "M/D/YYYY",
  dateTimeFormat: "M/D/YYYY HH:mm:ss",
  previousMonth: "پچھلے مہینے (PageUp)",
  nextMonth: "اگلے مہینے (PageDown)",
  previousYear: "گزشتہ سال (Control + left)",
  nextYear: "اگلے سال (Control + right)",
  previousDecade: "پچھلی دہائی",
  nextDecade: "اگلی دہائی",
  previousCentury: "پچھلی صدی",
  nextCentury: "اگلی صدی"
});
c.default = T;
var t = {};
Object.defineProperty(t, "__esModule", {
  value: !0
});
t.default = void 0;
const K = {
  placeholder: "وقت منتخب کریں",
  rangePlaceholder: ["وقت منتخب کریں", "آخر وقت"]
};
t.default = K;
var $ = o.default;
Object.defineProperty(r, "__esModule", {
  value: !0
});
r.default = void 0;
var D = $(c), M = $(t);
const O = {
  lang: Object.assign({
    placeholder: "تاریخ منتخب کریں",
    yearPlaceholder: "سال کو منتخب کریں",
    quarterPlaceholder: "کوارٹر منتخب کریں",
    monthPlaceholder: "ماہ منتخب کریں",
    weekPlaceholder: "ہفتہ منتخب کریں",
    rangePlaceholder: ["شروع کرنے کی تاریخ", "آخری تاریخ"],
    rangeYearPlaceholder: ["آغاز سال", "آخر سال"],
    rangeMonthPlaceholder: ["مہینہ شروع", "اختتامی مہینہ"],
    rangeWeekPlaceholder: ["ہفتے شروع کریں", "اختتام ہفتہ"]
  }, D.default),
  timePickerLocale: Object.assign({}, M.default)
};
r.default = O;
var k = o.default;
Object.defineProperty(i, "__esModule", {
  value: !0
});
i.default = void 0;
var S = k(r);
i.default = S.default;
var d = o.default;
Object.defineProperty(n, "__esModule", {
  value: !0
});
n.default = void 0;
var Y = d(u), w = d(i), C = d(r), F = d(t);
const e = "${label} درست نہیں ہے ${type}", q = {
  locale: "ur",
  Pagination: Y.default,
  DatePicker: C.default,
  TimePicker: F.default,
  Calendar: w.default,
  global: {
    placeholder: "منتخب کریں",
    close: "بند کریں"
  },
  Table: {
    filterTitle: "فلٹر مینو",
    filterConfirm: "ٹھیک ہے",
    filterReset: "ری سیٹ کریں",
    filterEmptyText: "فلٹرز نہیں",
    emptyText: "کوئی ڈیٹا نہیں",
    selectAll: "موجودہ صفحہ منتخب کریں",
    selectInvert: "موجودہ صفحے کو الٹ دیں",
    selectNone: "تمام ڈیٹا صاف کریں",
    selectionAll: "تمام ڈیٹا کو منتخب کریں",
    sortTitle: "ترتیب دیں",
    expand: "پھیلائیں",
    collapse: "سمیٹیں",
    triggerDesc: "نزولی کو ترتیب دینے کیلئے کلک کریں",
    triggerAsc: "چڑھنے کو ترتیب دینے کیلئے کلک کریں",
    cancelSort: "ترتیب کو منسوخ کرنے کیلئے دبائیں"
  },
  Tour: {
    Next: "اگلا",
    Previous: "پچھلا",
    Finish: "ختم کریں"
  },
  Modal: {
    okText: "ٹھیک ہے",
    cancelText: "منسوخ کریں",
    justOkText: "ٹھیک ہے"
  },
  Popconfirm: {
    okText: "ٹھیک ہے",
    cancelText: "منسوخ کریں"
  },
  Transfer: {
    titles: ["", ""],
    searchPlaceholder: "یہاں تلاش کریں",
    itemUnit: "شے",
    itemsUnit: "اشیاء",
    remove: "ہٹائیں",
    selectCurrent: "موجودہ صفحہ منتخب کریں",
    removeCurrent: "موجودہ صفحہ ہٹائیں",
    selectAll: "تمام ڈیٹا کو منتخب کریں",
    removeAll: "تمام ڈیٹا کو ہٹا دیں",
    selectInvert: "موجودہ صفحے کو الٹ دیں"
  },
  Upload: {
    uploading: "اپ لوڈ ہو رہا ہے…",
    removeFile: "فائل کو ہٹا دیں",
    uploadError: "اپ لوڈ کی خرابی",
    previewFile: "پیش نظار فائل",
    downloadFile: "فائل ڈاؤن لوڈ کریں"
  },
  Empty: {
    description: "کوئی ڈیٹا نہیں"
  },
  Icon: {
    icon: "آئیکن"
  },
  Text: {
    edit: "ترمیم",
    copy: "کاپی",
    copied: "کاپی ہوگیا",
    expand: "پھیلائیں"
  },
  Form: {
    optional: "(اختیاری)",
    defaultValidateMessages: {
      default: " ${label} کیلئے فیلڈ کی توثیق میں نقص",
      required: "درج کریں ${label}",
      enum: "${label} ایک ہونا ضروری ہے [${enum}]",
      whitespace: "${label} خالی نہیں ہوسکتا",
      date: {
        format: "${label} تاریخ کی شکل غلط ہے",
        parse: "${label} تاریخ میں تبدیل نہیں کیا جاسکتا",
        invalid: "${label} غلط تاریخ ہے"
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
        len: "${label} ضروری ہے ${len} حروف",
        min: "${label} کم از کم ہونا چاہئے ${min} حروف",
        max: "${label} تک ہونا چاہئے ${max} حروف",
        range: "${label} کے درمیان ہونا چاہئے ${min}-${max} حروف"
      },
      number: {
        len: "${label} کے برابر ہونا چاہئے ${len}",
        min: "${label} کم از کم ہونا چاہئے ${min}",
        max: "${label} زیادہ سے زیادہ ہونا چاہئے ${max}",
        range: "${label} کے درمیان ہونا چاہئے ${min}-${max}"
      },
      array: {
        len: "ضروری ہے ${len} ${label}",
        min: "کم از کم ${min} ${label}",
        max: "زیادہ سے زیادہ ${max} ${label}",
        range: "کی رقم ${label} کے درمیان ہونا چاہئے ${min}-${max}"
      },
      pattern: {
        mismatch: "${label} پیٹرن سے ملتا نہیں ہے ${pattern}"
      }
    }
  },
  Image: {
    preview: "پیش نظارہ"
  }
};
n.default = q;
var v = n;
const A = /* @__PURE__ */ P(v), I = /* @__PURE__ */ x({
  __proto__: null,
  default: A
}, [v]);
export {
  I as u
};
