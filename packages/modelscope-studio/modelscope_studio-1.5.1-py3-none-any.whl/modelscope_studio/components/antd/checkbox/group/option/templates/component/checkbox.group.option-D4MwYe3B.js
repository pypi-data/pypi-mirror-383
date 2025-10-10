import { Z as p, g as B } from "./Index-B_iZQz7f.js";
const z = window.ms_globals.React, I = window.ms_globals.ReactDOM.createPortal, H = window.ms_globals.createItemsContext.createItemsContext;
var P = {
  exports: {}
}, b = {};
/**
 * @license React
 * react-jsx-runtime.production.min.js
 *
 * Copyright (c) Facebook, Inc. and its affiliates.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */
var J = z, M = Symbol.for("react.element"), V = Symbol.for("react.fragment"), Y = Object.prototype.hasOwnProperty, Z = J.__SECRET_INTERNALS_DO_NOT_USE_OR_YOU_WILL_BE_FIRED.ReactCurrentOwner, Q = {
  key: !0,
  ref: !0,
  __self: !0,
  __source: !0
};
function T(r, t, l) {
  var n, s = {}, e = null, o = null;
  l !== void 0 && (e = "" + l), t.key !== void 0 && (e = "" + t.key), t.ref !== void 0 && (o = t.ref);
  for (n in t) Y.call(t, n) && !Q.hasOwnProperty(n) && (s[n] = t[n]);
  if (r && r.defaultProps) for (n in t = r.defaultProps, t) s[n] === void 0 && (s[n] = t[n]);
  return {
    $$typeof: M,
    type: r,
    key: e,
    ref: o,
    props: s,
    _owner: Z.current
  };
}
b.Fragment = V;
b.jsx = T;
b.jsxs = T;
P.exports = b;
var X = P.exports;
const {
  SvelteComponent: $,
  assign: y,
  binding_callbacks: x,
  check_outros: ee,
  children: j,
  claim_element: D,
  claim_space: te,
  component_subscribe: k,
  compute_slots: oe,
  create_slot: se,
  detach: _,
  element: L,
  empty: C,
  exclude_internal_props: S,
  get_all_dirty_from_scope: ne,
  get_slot_changes: re,
  group_outros: le,
  init: ie,
  insert_hydration: m,
  safe_not_equal: ae,
  set_custom_element_data: A,
  space: ce,
  transition_in: g,
  transition_out: v,
  update_slot_base: _e
} = window.__gradio__svelte__internal, {
  beforeUpdate: ue,
  getContext: fe,
  onDestroy: de,
  setContext: pe
} = window.__gradio__svelte__internal;
function E(r) {
  let t, l;
  const n = (
    /*#slots*/
    r[7].default
  ), s = se(
    n,
    r,
    /*$$scope*/
    r[6],
    null
  );
  return {
    c() {
      t = L("svelte-slot"), s && s.c(), this.h();
    },
    l(e) {
      t = D(e, "SVELTE-SLOT", {
        class: !0
      });
      var o = j(t);
      s && s.l(o), o.forEach(_), this.h();
    },
    h() {
      A(t, "class", "svelte-1rt0kpf");
    },
    m(e, o) {
      m(e, t, o), s && s.m(t, null), r[9](t), l = !0;
    },
    p(e, o) {
      s && s.p && (!l || o & /*$$scope*/
      64) && _e(
        s,
        n,
        e,
        /*$$scope*/
        e[6],
        l ? re(
          n,
          /*$$scope*/
          e[6],
          o,
          null
        ) : ne(
          /*$$scope*/
          e[6]
        ),
        null
      );
    },
    i(e) {
      l || (g(s, e), l = !0);
    },
    o(e) {
      v(s, e), l = !1;
    },
    d(e) {
      e && _(t), s && s.d(e), r[9](null);
    }
  };
}
function me(r) {
  let t, l, n, s, e = (
    /*$$slots*/
    r[4].default && E(r)
  );
  return {
    c() {
      t = L("react-portal-target"), l = ce(), e && e.c(), n = C(), this.h();
    },
    l(o) {
      t = D(o, "REACT-PORTAL-TARGET", {
        class: !0
      }), j(t).forEach(_), l = te(o), e && e.l(o), n = C(), this.h();
    },
    h() {
      A(t, "class", "svelte-1rt0kpf");
    },
    m(o, a) {
      m(o, t, a), r[8](t), m(o, l, a), e && e.m(o, a), m(o, n, a), s = !0;
    },
    p(o, [a]) {
      /*$$slots*/
      o[4].default ? e ? (e.p(o, a), a & /*$$slots*/
      16 && g(e, 1)) : (e = E(o), e.c(), g(e, 1), e.m(n.parentNode, n)) : e && (le(), v(e, 1, 1, () => {
        e = null;
      }), ee());
    },
    i(o) {
      s || (g(e), s = !0);
    },
    o(o) {
      v(e), s = !1;
    },
    d(o) {
      o && (_(t), _(l), _(n)), r[8](null), e && e.d(o);
    }
  };
}
function R(r) {
  const {
    svelteInit: t,
    ...l
  } = r;
  return l;
}
function ge(r, t, l) {
  let n, s, {
    $$slots: e = {},
    $$scope: o
  } = t;
  const a = oe(e);
  let {
    svelteInit: c
  } = t;
  const u = p(R(t)), f = p();
  k(r, f, (i) => l(0, n = i));
  const d = p();
  k(r, d, (i) => l(1, s = i));
  const w = [], N = fe("$$ms-gr-react-wrapper"), {
    slotKey: q,
    slotIndex: K,
    subSlotIndex: U
  } = B() || {}, F = c({
    parent: N,
    props: u,
    target: f,
    slot: d,
    slotKey: q,
    slotIndex: K,
    subSlotIndex: U,
    onDestroy(i) {
      w.push(i);
    }
  });
  pe("$$ms-gr-react-wrapper", F), ue(() => {
    u.set(R(t));
  }), de(() => {
    w.forEach((i) => i());
  });
  function G(i) {
    x[i ? "unshift" : "push"](() => {
      n = i, f.set(n);
    });
  }
  function W(i) {
    x[i ? "unshift" : "push"](() => {
      s = i, d.set(s);
    });
  }
  return r.$$set = (i) => {
    l(17, t = y(y({}, t), S(i))), "svelteInit" in i && l(5, c = i.svelteInit), "$$scope" in i && l(6, o = i.$$scope);
  }, t = S(t), [n, s, f, d, a, c, o, e, G, W];
}
class be extends $ {
  constructor(t) {
    super(), ie(this, t, ge, me, ae, {
      svelteInit: 5
    });
  }
}
const {
  SvelteComponent: Ie
} = window.__gradio__svelte__internal, O = window.ms_globals.rerender, h = window.ms_globals.tree;
function he(r, t = {}) {
  function l(n) {
    const s = p(), e = new be({
      ...n,
      props: {
        svelteInit(o) {
          window.ms_globals.autokey += 1;
          const a = {
            key: window.ms_globals.autokey,
            svelteInstance: s,
            reactComponent: r,
            props: o.props,
            slot: o.slot,
            target: o.target,
            slotIndex: o.slotIndex,
            subSlotIndex: o.subSlotIndex,
            ignore: t.ignore,
            slotKey: o.slotKey,
            nodes: []
          }, c = o.parent ?? h;
          return c.nodes = [...c.nodes, a], O({
            createPortal: I,
            node: h
          }), o.onDestroy(() => {
            c.nodes = c.nodes.filter((u) => u.svelteInstance !== s), O({
              createPortal: I,
              node: h
            });
          }), a;
        },
        ...n.props
      }
    });
    return s.set(e), e;
  }
  return new Promise((n) => {
    window.ms_globals.initializePromise.then(() => {
      n(l);
    });
  });
}
const {
  withItemsContextProvider: ye,
  useItems: xe,
  ItemHandler: ve
} = H("antd-checkbox-group-options"), ke = he((r) => /* @__PURE__ */ X.jsx(ve, {
  ...r
}));
export {
  ke as CheckboxGroupOption,
  ke as default
};
