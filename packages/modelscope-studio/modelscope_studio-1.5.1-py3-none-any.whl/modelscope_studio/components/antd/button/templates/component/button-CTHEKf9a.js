import { i as ae, a as L, r as ce, Z as O, g as ue, t as de, s as R } from "./Index-Cl4Ewkvr.js";
const x = window.ms_globals.React, Z = window.ms_globals.React.useMemo, Q = window.ms_globals.React.useState, $ = window.ms_globals.React.useEffect, ie = window.ms_globals.React.forwardRef, le = window.ms_globals.React.useRef, W = window.ms_globals.ReactDOM.createPortal, fe = window.ms_globals.internalContext.useContextPropsContext, pe = window.ms_globals.antd.Button;
var me = /\s/;
function _e(e) {
  for (var t = e.length; t-- && me.test(e.charAt(t)); )
    ;
  return t;
}
var ge = /^\s+/;
function he(e) {
  return e && e.slice(0, _e(e) + 1).replace(ge, "");
}
var F = NaN, ye = /^[-+]0x[0-9a-f]+$/i, be = /^0b[01]+$/i, xe = /^0o[0-7]+$/i, we = parseInt;
function U(e) {
  if (typeof e == "number")
    return e;
  if (ae(e))
    return F;
  if (L(e)) {
    var t = typeof e.valueOf == "function" ? e.valueOf() : e;
    e = L(t) ? t + "" : t;
  }
  if (typeof e != "string")
    return e === 0 ? e : +e;
  e = he(e);
  var o = be.test(e);
  return o || xe.test(e) ? we(e.slice(2), o ? 2 : 8) : ye.test(e) ? F : +e;
}
var N = function() {
  return ce.Date.now();
}, Ee = "Expected a function", ve = Math.max, Ce = Math.min;
function Ie(e, t, o) {
  var s, i, n, r, l, u, _ = 0, g = !1, a = !1, h = !0;
  if (typeof e != "function")
    throw new TypeError(Ee);
  t = U(t) || 0, L(o) && (g = !!o.leading, a = "maxWait" in o, n = a ? ve(U(o.maxWait) || 0, t) : n, h = "trailing" in o ? !!o.trailing : h);
  function p(d) {
    var b = s, T = i;
    return s = i = void 0, _ = d, r = e.apply(T, b), r;
  }
  function w(d) {
    return _ = d, l = setTimeout(m, t), g ? p(d) : r;
  }
  function E(d) {
    var b = d - u, T = d - _, D = t - b;
    return a ? Ce(D, n - T) : D;
  }
  function f(d) {
    var b = d - u, T = d - _;
    return u === void 0 || b >= t || b < 0 || a && T >= n;
  }
  function m() {
    var d = N();
    if (f(d))
      return y(d);
    l = setTimeout(m, E(d));
  }
  function y(d) {
    return l = void 0, h && s ? p(d) : (s = i = void 0, r);
  }
  function S() {
    l !== void 0 && clearTimeout(l), _ = 0, s = u = i = l = void 0;
  }
  function c() {
    return l === void 0 ? r : y(N());
  }
  function v() {
    var d = N(), b = f(d);
    if (s = arguments, i = this, u = d, b) {
      if (l === void 0)
        return w(u);
      if (a)
        return clearTimeout(l), l = setTimeout(m, t), p(u);
    }
    return l === void 0 && (l = setTimeout(m, t)), r;
  }
  return v.cancel = S, v.flush = c, v;
}
var ee = {
  exports: {}
}, A = {};
/**
 * @license React
 * react-jsx-runtime.production.min.js
 *
 * Copyright (c) Facebook, Inc. and its affiliates.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */
var Se = x, Te = Symbol.for("react.element"), Re = Symbol.for("react.fragment"), Oe = Object.prototype.hasOwnProperty, ke = Se.__SECRET_INTERNALS_DO_NOT_USE_OR_YOU_WILL_BE_FIRED.ReactCurrentOwner, Pe = {
  key: !0,
  ref: !0,
  __self: !0,
  __source: !0
};
function te(e, t, o) {
  var s, i = {}, n = null, r = null;
  o !== void 0 && (n = "" + o), t.key !== void 0 && (n = "" + t.key), t.ref !== void 0 && (r = t.ref);
  for (s in t) Oe.call(t, s) && !Pe.hasOwnProperty(s) && (i[s] = t[s]);
  if (e && e.defaultProps) for (s in t = e.defaultProps, t) i[s] === void 0 && (i[s] = t[s]);
  return {
    $$typeof: Te,
    type: e,
    key: n,
    ref: r,
    props: i,
    _owner: ke.current
  };
}
A.Fragment = Re;
A.jsx = te;
A.jsxs = te;
ee.exports = A;
var C = ee.exports;
const {
  SvelteComponent: Le,
  assign: z,
  binding_callbacks: G,
  check_outros: Ae,
  children: ne,
  claim_element: re,
  claim_space: Ne,
  component_subscribe: H,
  compute_slots: je,
  create_slot: We,
  detach: I,
  element: oe,
  empty: K,
  exclude_internal_props: V,
  get_all_dirty_from_scope: Me,
  get_slot_changes: Be,
  group_outros: De,
  init: Fe,
  insert_hydration: k,
  safe_not_equal: Ue,
  set_custom_element_data: se,
  space: ze,
  transition_in: P,
  transition_out: M,
  update_slot_base: Ge
} = window.__gradio__svelte__internal, {
  beforeUpdate: He,
  getContext: Ke,
  onDestroy: Ve,
  setContext: qe
} = window.__gradio__svelte__internal;
function q(e) {
  let t, o;
  const s = (
    /*#slots*/
    e[7].default
  ), i = We(
    s,
    e,
    /*$$scope*/
    e[6],
    null
  );
  return {
    c() {
      t = oe("svelte-slot"), i && i.c(), this.h();
    },
    l(n) {
      t = re(n, "SVELTE-SLOT", {
        class: !0
      });
      var r = ne(t);
      i && i.l(r), r.forEach(I), this.h();
    },
    h() {
      se(t, "class", "svelte-1rt0kpf");
    },
    m(n, r) {
      k(n, t, r), i && i.m(t, null), e[9](t), o = !0;
    },
    p(n, r) {
      i && i.p && (!o || r & /*$$scope*/
      64) && Ge(
        i,
        s,
        n,
        /*$$scope*/
        n[6],
        o ? Be(
          s,
          /*$$scope*/
          n[6],
          r,
          null
        ) : Me(
          /*$$scope*/
          n[6]
        ),
        null
      );
    },
    i(n) {
      o || (P(i, n), o = !0);
    },
    o(n) {
      M(i, n), o = !1;
    },
    d(n) {
      n && I(t), i && i.d(n), e[9](null);
    }
  };
}
function Je(e) {
  let t, o, s, i, n = (
    /*$$slots*/
    e[4].default && q(e)
  );
  return {
    c() {
      t = oe("react-portal-target"), o = ze(), n && n.c(), s = K(), this.h();
    },
    l(r) {
      t = re(r, "REACT-PORTAL-TARGET", {
        class: !0
      }), ne(t).forEach(I), o = Ne(r), n && n.l(r), s = K(), this.h();
    },
    h() {
      se(t, "class", "svelte-1rt0kpf");
    },
    m(r, l) {
      k(r, t, l), e[8](t), k(r, o, l), n && n.m(r, l), k(r, s, l), i = !0;
    },
    p(r, [l]) {
      /*$$slots*/
      r[4].default ? n ? (n.p(r, l), l & /*$$slots*/
      16 && P(n, 1)) : (n = q(r), n.c(), P(n, 1), n.m(s.parentNode, s)) : n && (De(), M(n, 1, 1, () => {
        n = null;
      }), Ae());
    },
    i(r) {
      i || (P(n), i = !0);
    },
    o(r) {
      M(n), i = !1;
    },
    d(r) {
      r && (I(t), I(o), I(s)), e[8](null), n && n.d(r);
    }
  };
}
function J(e) {
  const {
    svelteInit: t,
    ...o
  } = e;
  return o;
}
function Xe(e, t, o) {
  let s, i, {
    $$slots: n = {},
    $$scope: r
  } = t;
  const l = je(n);
  let {
    svelteInit: u
  } = t;
  const _ = O(J(t)), g = O();
  H(e, g, (c) => o(0, s = c));
  const a = O();
  H(e, a, (c) => o(1, i = c));
  const h = [], p = Ke("$$ms-gr-react-wrapper"), {
    slotKey: w,
    slotIndex: E,
    subSlotIndex: f
  } = ue() || {}, m = u({
    parent: p,
    props: _,
    target: g,
    slot: a,
    slotKey: w,
    slotIndex: E,
    subSlotIndex: f,
    onDestroy(c) {
      h.push(c);
    }
  });
  qe("$$ms-gr-react-wrapper", m), He(() => {
    _.set(J(t));
  }), Ve(() => {
    h.forEach((c) => c());
  });
  function y(c) {
    G[c ? "unshift" : "push"](() => {
      s = c, g.set(s);
    });
  }
  function S(c) {
    G[c ? "unshift" : "push"](() => {
      i = c, a.set(i);
    });
  }
  return e.$$set = (c) => {
    o(17, t = z(z({}, t), V(c))), "svelteInit" in c && o(5, u = c.svelteInit), "$$scope" in c && o(6, r = c.$$scope);
  }, t = V(t), [s, i, g, a, l, u, r, n, y, S];
}
class Ye extends Le {
  constructor(t) {
    super(), Fe(this, t, Xe, Je, Ue, {
      svelteInit: 5
    });
  }
}
const {
  SvelteComponent: it
} = window.__gradio__svelte__internal, X = window.ms_globals.rerender, j = window.ms_globals.tree;
function Ze(e, t = {}) {
  function o(s) {
    const i = O(), n = new Ye({
      ...s,
      props: {
        svelteInit(r) {
          window.ms_globals.autokey += 1;
          const l = {
            key: window.ms_globals.autokey,
            svelteInstance: i,
            reactComponent: e,
            props: r.props,
            slot: r.slot,
            target: r.target,
            slotIndex: r.slotIndex,
            subSlotIndex: r.subSlotIndex,
            ignore: t.ignore,
            slotKey: r.slotKey,
            nodes: []
          }, u = r.parent ?? j;
          return u.nodes = [...u.nodes, l], X({
            createPortal: W,
            node: j
          }), r.onDestroy(() => {
            u.nodes = u.nodes.filter((_) => _.svelteInstance !== i), X({
              createPortal: W,
              node: j
            });
          }), l;
        },
        ...s.props
      }
    });
    return i.set(n), n;
  }
  return new Promise((s) => {
    window.ms_globals.initializePromise.then(() => {
      s(o);
    });
  });
}
function Qe(e) {
  const [t, o] = Q(() => R(e));
  return $(() => {
    let s = !0;
    return e.subscribe((n) => {
      s && (s = !1, n === t) || o(n);
    });
  }, [e]), t;
}
function $e(e) {
  const t = Z(() => de(e, (o) => o), [e]);
  return Qe(t);
}
const et = ["animationIterationCount", "borderImageOutset", "borderImageSlice", "borderImageWidth", "boxFlex", "boxFlexGroup", "boxOrdinalGroup", "columnCount", "columns", "flex", "flexGrow", "flexPositive", "flexShrink", "flexNegative", "flexOrder", "gridArea", "gridColumn", "gridColumnEnd", "gridColumnStart", "gridRow", "gridRowEnd", "gridRowStart", "lineClamp", "lineHeight", "opacity", "order", "orphans", "tabSize", "widows", "zIndex", "zoom", "fontWeight", "letterSpacing", "lineHeight"];
function tt(e) {
  return e ? Object.keys(e).reduce((t, o) => {
    const s = e[o];
    return t[o] = nt(o, s), t;
  }, {}) : {};
}
function nt(e, t) {
  return typeof t == "number" && !et.includes(e) ? t + "px" : t;
}
function B(e) {
  const t = [], o = e.cloneNode(!1);
  if (e._reactElement) {
    const i = x.Children.toArray(e._reactElement.props.children).map((n) => {
      if (x.isValidElement(n) && n.props.__slot__) {
        const {
          portals: r,
          clonedElement: l
        } = B(n.props.el);
        return x.cloneElement(n, {
          ...n.props,
          el: l,
          children: [...x.Children.toArray(n.props.children), ...r]
        });
      }
      return null;
    });
    return i.originalChildren = e._reactElement.props.children, t.push(W(x.cloneElement(e._reactElement, {
      ...e._reactElement.props,
      children: i
    }), o)), {
      clonedElement: o,
      portals: t
    };
  }
  Object.keys(e.getEventListeners()).forEach((i) => {
    e.getEventListeners(i).forEach(({
      listener: r,
      type: l,
      useCapture: u
    }) => {
      o.addEventListener(l, r, u);
    });
  });
  const s = Array.from(e.childNodes);
  for (let i = 0; i < s.length; i++) {
    const n = s[i];
    if (n.nodeType === 1) {
      const {
        clonedElement: r,
        portals: l
      } = B(n);
      t.push(...l), o.appendChild(r);
    } else n.nodeType === 3 && o.appendChild(n.cloneNode());
  }
  return {
    clonedElement: o,
    portals: t
  };
}
function rt(e, t) {
  e && (typeof e == "function" ? e(t) : e.current = t);
}
const Y = ie(({
  slot: e,
  clone: t,
  className: o,
  style: s,
  observeAttributes: i
}, n) => {
  const r = le(), [l, u] = Q([]), {
    forceClone: _
  } = fe(), g = _ ? !0 : t;
  return $(() => {
    var E;
    if (!r.current || !e)
      return;
    let a = e;
    function h() {
      let f = a;
      if (a.tagName.toLowerCase() === "svelte-slot" && a.children.length === 1 && a.children[0] && (f = a.children[0], f.tagName.toLowerCase() === "react-portal-target" && f.children[0] && (f = f.children[0])), rt(n, f), o && f.classList.add(...o.split(" ")), s) {
        const m = tt(s);
        Object.keys(m).forEach((y) => {
          f.style[y] = m[y];
        });
      }
    }
    let p = null, w = null;
    if (g && window.MutationObserver) {
      let f = function() {
        var c, v, d;
        (c = r.current) != null && c.contains(a) && ((v = r.current) == null || v.removeChild(a));
        const {
          portals: y,
          clonedElement: S
        } = B(e);
        a = S, u(y), a.style.display = "contents", w && clearTimeout(w), w = setTimeout(() => {
          h();
        }, 50), (d = r.current) == null || d.appendChild(a);
      };
      f();
      const m = Ie(() => {
        f(), p == null || p.disconnect(), p == null || p.observe(e, {
          childList: !0,
          subtree: !0,
          attributes: i
        });
      }, 50);
      p = new window.MutationObserver(m), p.observe(e, {
        attributes: !0,
        childList: !0,
        subtree: !0
      });
    } else
      a.style.display = "contents", h(), (E = r.current) == null || E.appendChild(a);
    return () => {
      var f, m;
      a.style.display = "", (f = r.current) != null && f.contains(a) && ((m = r.current) == null || m.removeChild(a)), p == null || p.disconnect();
    };
  }, [e, g, o, s, n, i, _]), x.createElement("react-child", {
    ref: r,
    style: {
      display: "contents"
    }
  }, ...l);
});
function ot(e, t) {
  const o = Z(() => x.Children.toArray(e.originalChildren || e).filter((n) => n.props.node && !n.props.node.ignore && (!n.props.nodeSlotKey || t)).sort((n, r) => {
    if (n.props.node.slotIndex && r.props.node.slotIndex) {
      const l = R(n.props.node.slotIndex) || 0, u = R(r.props.node.slotIndex) || 0;
      return l - u === 0 && n.props.node.subSlotIndex && r.props.node.subSlotIndex ? (R(n.props.node.subSlotIndex) || 0) - (R(r.props.node.subSlotIndex) || 0) : l - u;
    }
    return 0;
  }).map((n) => n.props.node.target), [e, t]);
  return $e(o);
}
const lt = Ze(({
  slots: e,
  value: t,
  children: o,
  ...s
}) => {
  var n;
  const i = ot(o);
  return /* @__PURE__ */ C.jsxs(C.Fragment, {
    children: [/* @__PURE__ */ C.jsx("div", {
      style: {
        display: "none"
      },
      children: i.length > 0 ? null : o
    }), /* @__PURE__ */ C.jsx(pe, {
      ...s,
      icon: e.icon ? /* @__PURE__ */ C.jsx(Y, {
        slot: e.icon,
        clone: !0
      }) : s.icon,
      loading: e["loading.icon"] ? {
        icon: /* @__PURE__ */ C.jsx(Y, {
          slot: e["loading.icon"]
        }),
        delay: L(s.loading) ? (n = s.loading) == null ? void 0 : n.delay : void 0
      } : s.loading,
      children: i.length > 0 ? o : t
    })]
  });
});
export {
  lt as Button,
  lt as default
};
