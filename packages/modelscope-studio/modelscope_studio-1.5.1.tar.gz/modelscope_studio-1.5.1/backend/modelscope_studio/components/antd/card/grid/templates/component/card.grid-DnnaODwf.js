import { Z as m, g as N } from "./Index-RQoBayQW.js";
const v = window.ms_globals.ReactDOM.createPortal, U = window.ms_globals.antd.Card, {
  SvelteComponent: V,
  assign: I,
  binding_callbacks: y,
  check_outros: W,
  children: R,
  claim_element: D,
  claim_space: Z,
  component_subscribe: C,
  compute_slots: j,
  create_slot: B,
  detach: _,
  element: A,
  empty: k,
  exclude_internal_props: S,
  get_all_dirty_from_scope: F,
  get_slot_changes: H,
  group_outros: J,
  init: Q,
  insert_hydration: p,
  safe_not_equal: X,
  set_custom_element_data: G,
  space: Y,
  transition_in: g,
  transition_out: h,
  update_slot_base: $
} = window.__gradio__svelte__internal, {
  beforeUpdate: ee,
  getContext: te,
  onDestroy: se,
  setContext: oe
} = window.__gradio__svelte__internal;
function E(r) {
  let s, n;
  const l = (
    /*#slots*/
    r[7].default
  ), o = B(
    l,
    r,
    /*$$scope*/
    r[6],
    null
  );
  return {
    c() {
      s = A("svelte-slot"), o && o.c(), this.h();
    },
    l(e) {
      s = D(e, "SVELTE-SLOT", {
        class: !0
      });
      var t = R(s);
      o && o.l(t), t.forEach(_), this.h();
    },
    h() {
      G(s, "class", "svelte-1rt0kpf");
    },
    m(e, t) {
      p(e, s, t), o && o.m(s, null), r[9](s), n = !0;
    },
    p(e, t) {
      o && o.p && (!n || t & /*$$scope*/
      64) && $(
        o,
        l,
        e,
        /*$$scope*/
        e[6],
        n ? H(
          l,
          /*$$scope*/
          e[6],
          t,
          null
        ) : F(
          /*$$scope*/
          e[6]
        ),
        null
      );
    },
    i(e) {
      n || (g(o, e), n = !0);
    },
    o(e) {
      h(o, e), n = !1;
    },
    d(e) {
      e && _(s), o && o.d(e), r[9](null);
    }
  };
}
function ne(r) {
  let s, n, l, o, e = (
    /*$$slots*/
    r[4].default && E(r)
  );
  return {
    c() {
      s = A("react-portal-target"), n = Y(), e && e.c(), l = k(), this.h();
    },
    l(t) {
      s = D(t, "REACT-PORTAL-TARGET", {
        class: !0
      }), R(s).forEach(_), n = Z(t), e && e.l(t), l = k(), this.h();
    },
    h() {
      G(s, "class", "svelte-1rt0kpf");
    },
    m(t, i) {
      p(t, s, i), r[8](s), p(t, n, i), e && e.m(t, i), p(t, l, i), o = !0;
    },
    p(t, [i]) {
      /*$$slots*/
      t[4].default ? e ? (e.p(t, i), i & /*$$slots*/
      16 && g(e, 1)) : (e = E(t), e.c(), g(e, 1), e.m(l.parentNode, l)) : e && (J(), h(e, 1, 1, () => {
        e = null;
      }), W());
    },
    i(t) {
      o || (g(e), o = !0);
    },
    o(t) {
      h(e), o = !1;
    },
    d(t) {
      t && (_(s), _(n), _(l)), r[8](null), e && e.d(t);
    }
  };
}
function P(r) {
  const {
    svelteInit: s,
    ...n
  } = r;
  return n;
}
function le(r, s, n) {
  let l, o, {
    $$slots: e = {},
    $$scope: t
  } = s;
  const i = j(e);
  let {
    svelteInit: c
  } = s;
  const u = m(P(s)), d = m();
  C(r, d, (a) => n(0, l = a));
  const f = m();
  C(r, f, (a) => n(1, o = a));
  const w = [], K = te("$$ms-gr-react-wrapper"), {
    slotKey: L,
    slotIndex: O,
    subSlotIndex: x
  } = N() || {}, q = c({
    parent: K,
    props: u,
    target: d,
    slot: f,
    slotKey: L,
    slotIndex: O,
    subSlotIndex: x,
    onDestroy(a) {
      w.push(a);
    }
  });
  oe("$$ms-gr-react-wrapper", q), ee(() => {
    u.set(P(s));
  }), se(() => {
    w.forEach((a) => a());
  });
  function z(a) {
    y[a ? "unshift" : "push"](() => {
      l = a, d.set(l);
    });
  }
  function M(a) {
    y[a ? "unshift" : "push"](() => {
      o = a, f.set(o);
    });
  }
  return r.$$set = (a) => {
    n(17, s = I(I({}, s), S(a))), "svelteInit" in a && n(5, c = a.svelteInit), "$$scope" in a && n(6, t = a.$$scope);
  }, s = S(s), [l, o, d, f, i, c, t, e, z, M];
}
class re extends V {
  constructor(s) {
    super(), Q(this, s, le, ne, X, {
      svelteInit: 5
    });
  }
}
const {
  SvelteComponent: ce
} = window.__gradio__svelte__internal, T = window.ms_globals.rerender, b = window.ms_globals.tree;
function ae(r, s = {}) {
  function n(l) {
    const o = m(), e = new re({
      ...l,
      props: {
        svelteInit(t) {
          window.ms_globals.autokey += 1;
          const i = {
            key: window.ms_globals.autokey,
            svelteInstance: o,
            reactComponent: r,
            props: t.props,
            slot: t.slot,
            target: t.target,
            slotIndex: t.slotIndex,
            subSlotIndex: t.subSlotIndex,
            ignore: s.ignore,
            slotKey: t.slotKey,
            nodes: []
          }, c = t.parent ?? b;
          return c.nodes = [...c.nodes, i], T({
            createPortal: v,
            node: b
          }), t.onDestroy(() => {
            c.nodes = c.nodes.filter((u) => u.svelteInstance !== o), T({
              createPortal: v,
              node: b
            });
          }), i;
        },
        ...l.props
      }
    });
    return o.set(e), e;
  }
  return new Promise((l) => {
    window.ms_globals.initializePromise.then(() => {
      l(n);
    });
  });
}
const _e = ae(U.Grid);
export {
  _e as CardGrid,
  _e as default
};
