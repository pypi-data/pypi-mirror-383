import { c as b } from "./Index-Bv07WiuH.js";
import { i as o, o as g, c as x } from "./config-provider-ROh4C3n3.js";
function M(u, f) {
  for (var s = 0; s < f.length; s++) {
    const t = f[s];
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
var n = {}, i = {};
Object.defineProperty(i, "__esModule", {
  value: !0
});
i.default = void 0;
var y = {
  // Options
  items_per_page: "/ хуудас",
  jump_to: "Шилжих",
  jump_to_confirm: "сонгох",
  page: "",
  // Pagination
  prev_page: "Өмнөх хуудас",
  next_page: "Дараагийн хуудас",
  prev_5: "Дараагийн 5 хуудас",
  next_5: "Дараагийн 5 хуудас",
  prev_3: "Дараагийн 3 хуудас",
  next_3: "Дараагийн 3 хуудас",
  page_size: "Page Size"
};
i.default = y;
var c = {}, l = {}, m = {}, P = o.default;
Object.defineProperty(m, "__esModule", {
  value: !0
});
m.default = void 0;
var _ = P(g), h = x, N = (0, _.default)((0, _.default)({}, h.commonLocale), {}, {
  locale: "mn_MN",
  today: "Өнөөдөр",
  now: "Одоо",
  backToToday: "Өнөөдөрлүү буцах",
  ok: "OK",
  clear: "Цэвэрлэх",
  week: "Долоо хоног",
  month: "Сар",
  year: "Жил",
  timeSelect: "Цаг сонгох",
  dateSelect: "Огноо сонгох",
  weekSelect: "7 хоног сонгох",
  monthSelect: "Сар сонгох",
  yearSelect: "Жил сонгох",
  decadeSelect: "Арван сонгох",
  dateFormat: "YYYY/MM/DD",
  dayFormat: "DD",
  dateTimeFormat: "YYYY/MM/DD HH:mm:ss",
  previousMonth: "Өмнөх сар (PageUp)",
  nextMonth: "Дараа сар (PageDown)",
  previousYear: "Өмнөх жил (Control + left)",
  nextYear: "Дараа жил (Control + right)",
  previousDecade: "Өмнөх арван",
  nextDecade: "Дараа арван",
  previousCentury: "Өмнөх зуун",
  nextCentury: "Дараа зуун"
});
m.default = N;
var r = {};
Object.defineProperty(r, "__esModule", {
  value: !0
});
r.default = void 0;
const j = {
  placeholder: "Цаг сонгох"
};
r.default = j;
var $ = o.default;
Object.defineProperty(l, "__esModule", {
  value: !0
});
l.default = void 0;
var T = $(m), D = $(r);
const O = {
  lang: Object.assign({
    placeholder: "Огноо сонгох",
    rangePlaceholder: ["Эхлэх огноо", "Дуусах огноо"]
  }, T.default),
  timePickerLocale: Object.assign({}, D.default)
};
l.default = O;
var S = o.default;
Object.defineProperty(c, "__esModule", {
  value: !0
});
c.default = void 0;
var k = S(l);
c.default = k.default;
var d = o.default;
Object.defineProperty(n, "__esModule", {
  value: !0
});
n.default = void 0;
var C = d(i), Y = d(c), w = d(l), F = d(r);
const e = "${label} нь хүчинтэй ${type} биш", A = {
  locale: "mn-mn",
  Pagination: C.default,
  DatePicker: w.default,
  TimePicker: F.default,
  Calendar: Y.default,
  global: {
    placeholder: "Сонгоно уу",
    close: "Хаах"
  },
  Table: {
    filterTitle: "Хайх цэс",
    filterConfirm: "Тийм",
    filterReset: "Цэвэрлэх",
    filterEmptyText: "Шүүлтүүр байхгүй",
    filterCheckAll: "Бүх зүйлийг сонгоно уу",
    filterSearchPlaceholder: "Шүүлтүүрээс хайх",
    emptyText: "Өгөгдөл алга",
    selectAll: "Бүгдийг сонгох",
    selectInvert: "Бусдыг сонгох",
    selectNone: "Бүх өгөгдлийг арилгах",
    selectionAll: "Бүх өгөгдлийг сонгоно уу",
    sortTitle: "Эрэмбэлэх",
    expand: "Мөрийг өргөжүүлэх",
    collapse: "Мөрийг буулгах",
    triggerDesc: "Буурах байдлаар эрэмбэлэхийн тулд товшино уу",
    triggerAsc: "Өсөхөөр эрэмбэлэхийн тулд товшино уу",
    cancelSort: "Эрэмбэлэхийг цуцлахын тулд товшино уу"
  },
  Tour: {
    Next: "Дараах",
    Previous: "Урд",
    Finish: "Төгсгөх"
  },
  Modal: {
    okText: "Тийм",
    cancelText: "Цуцлах",
    justOkText: "Тийм"
  },
  Popconfirm: {
    okText: "Тийм",
    cancelText: "Цуцлах"
  },
  Transfer: {
    titles: ["", ""],
    searchPlaceholder: "Хайх",
    itemUnit: "Зүйл",
    itemsUnit: "Зүйлүүд",
    remove: "Устгах",
    selectCurrent: "Одоогийн хуудсыг сонгоно уу",
    removeCurrent: "Одоогийн хуудсыг устгана уу",
    selectAll: "Бүх өгөгдлийг сонгоно уу",
    removeAll: "Бүх өгөгдлийг устгана уу",
    selectInvert: "Одоогийн хуудсыг эргүүлэх"
  },
  Upload: {
    uploading: "Хуулж байна...",
    removeFile: "Файл устгах",
    uploadError: "Хуулахад алдаа гарлаа",
    previewFile: "Файлыг түргэн үзэх",
    downloadFile: "Файлыг татах"
  },
  Empty: {
    description: "Мэдээлэл байхгүй байна"
  },
  Icon: {
    icon: "дүрс"
  },
  Text: {
    edit: "Засварлах",
    copy: "Хуулбарлах",
    copied: "Хуулсан",
    expand: "Өргөтгөх"
  },
  Form: {
    optional: "(сонголттой)",
    defaultValidateMessages: {
      default: "${label}-ийн талбарын баталгаажуулалтын алдаа",
      required: "${label} оруулна уу",
      enum: "${label} нь [${enum}]-ийн нэг байх ёстой",
      whitespace: "${label} нь хоосон тэмдэгт байж болохгүй",
      date: {
        format: "${label} огнооны формат буруу байна",
        parse: "${label}-г огноо руу хөрвүүлэх боломжгүй",
        invalid: "${label} нь хүчингүй огноо юм"
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
        len: "${label} ${len} тэмдэгттэй байх ёстой",
        min: "${label} хамгийн багадаа ${min} тэмдэгттэй байх ёстой",
        max: "${label} нь ${max} хүртэлх тэмдэгттэй байх ёстой",
        range: "${label} ${min}-${max} тэмдэгтийн хооронд байх ёстой"
      },
      number: {
        len: "${label} нь ${len}-тэй тэнцүү байх ёстой",
        min: "${label} хамгийн багадаа ${min} байх ёстой",
        max: "${label} дээд тал нь ${max} байх ёстой",
        range: "${label} ${min}-${max} хооронд байх ёстой"
      },
      array: {
        len: "${len} ${label} байх ёстой",
        min: "Дор хаяж ${мин} ${label}",
        max: "Хамгийн ихдээ ${max} ${label}",
        range: "${label}-н хэмжээ ${min}-${max} хооронд байх ёстой"
      },
      pattern: {
        mismatch: "${label} нь ${pattern} загвартай тохирохгүй байна"
      }
    }
  },
  Image: {
    preview: "Урьдчилан үзэх"
  }
};
n.default = A;
var v = n;
const q = /* @__PURE__ */ b(v), I = /* @__PURE__ */ M({
  __proto__: null,
  default: q
}, [v]);
export {
  I as m
};
