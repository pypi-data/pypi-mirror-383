function j() {
}
function W(t, e) {
  return t != t ? e == e : t !== e || t && typeof t == "object" || typeof t == "function";
}
const T = [];
function O(t, e = j) {
  let n;
  const l = /* @__PURE__ */ new Set();
  function i(_) {
    if (W(t, _) && (t = _, n)) {
      const d = !T.length;
      for (const b of l)
        b[1](), T.push(b, t);
      if (d) {
        for (let b = 0; b < T.length; b += 2)
          T[b][0](T[b + 1]);
        T.length = 0;
      }
    }
  }
  function s(_) {
    i(_(t));
  }
  function a(_, d = j) {
    const b = [_, d];
    return l.add(b), l.size === 1 && (n = e(i, s) || j), _(t), () => {
      l.delete(b), l.size === 0 && n && (n(), n = null);
    };
  }
  return { set: i, update: s, subscribe: a };
}
const {
  SvelteComponent: X,
  append_hydration: q,
  attr: m,
  children: C,
  claim_element: N,
  claim_space: y,
  claim_text: J,
  component_subscribe: U,
  create_slot: Y,
  destroy_block: Z,
  detach: g,
  element: S,
  empty: E,
  ensure_array_like: V,
  get_all_dirty_from_scope: $,
  get_slot_changes: x,
  init: ee,
  insert_hydration: I,
  listen: te,
  safe_not_equal: le,
  set_data: K,
  set_store_value: A,
  space: z,
  text: L,
  toggle_class: M,
  transition_in: ie,
  transition_out: ne,
  update_keyed_each: se,
  update_slot_base: ae
} = window.__gradio__svelte__internal, { setContext: _e, createEventDispatcher: oe } = window.__gradio__svelte__internal;
function F(t, e, n) {
  const l = t.slice();
  return l[14] = e[n], l[16] = n, l;
}
function G(t) {
  let e;
  function n(s, a) {
    return (
      /*t*/
      s[14].id === /*$selected_tab*/
      s[4] ? re : ce
    );
  }
  let l = n(t), i = l(t);
  return {
    c() {
      i.c(), e = E();
    },
    l(s) {
      i.l(s), e = E();
    },
    m(s, a) {
      i.m(s, a), I(s, e, a);
    },
    p(s, a) {
      l === (l = n(s)) && i ? i.p(s, a) : (i.d(1), i = l(s), i && (i.c(), i.m(e.parentNode, e)));
    },
    d(s) {
      s && g(e), i.d(s);
    }
  };
}
function ce(t) {
  let e, n = (
    /*t*/
    t[14].name + ""
  ), l, i, s, a, _, d, b, h;
  function u() {
    return (
      /*click_handler*/
      t[12](
        /*t*/
        t[14],
        /*i*/
        t[16]
      )
    );
  }
  return {
    c() {
      e = S("button"), l = L(n), i = z(), this.h();
    },
    l(o) {
      e = N(o, "BUTTON", {
        role: !0,
        "aria-selected": !0,
        "aria-controls": !0,
        "aria-disabled": !0,
        id: !0,
        class: !0
      });
      var c = C(e);
      l = J(c, n), i = y(c), c.forEach(g), this.h();
    },
    h() {
      m(e, "role", "tab"), m(e, "aria-selected", !1), m(e, "aria-controls", s = /*t*/
      t[14].elem_id), e.disabled = a = !/*t*/
      t[14].interactive, m(e, "aria-disabled", _ = !/*t*/
      t[14].interactive), m(e, "id", d = /*t*/
      t[14].elem_id ? (
        /*t*/
        t[14].elem_id + "-button"
      ) : null), m(e, "class", "svelte-lv9hp0");
    },
    m(o, c) {
      I(o, e, c), q(e, l), q(e, i), b || (h = te(e, "click", u), b = !0);
    },
    p(o, c) {
      t = o, c & /*tabs*/
      8 && n !== (n = /*t*/
      t[14].name + "") && K(l, n), c & /*tabs*/
      8 && s !== (s = /*t*/
      t[14].elem_id) && m(e, "aria-controls", s), c & /*tabs*/
      8 && a !== (a = !/*t*/
      t[14].interactive) && (e.disabled = a), c & /*tabs*/
      8 && _ !== (_ = !/*t*/
      t[14].interactive) && m(e, "aria-disabled", _), c & /*tabs*/
      8 && d !== (d = /*t*/
      t[14].elem_id ? (
        /*t*/
        t[14].elem_id + "-button"
      ) : null) && m(e, "id", d);
    },
    d(o) {
      o && g(e), b = !1, h();
    }
  };
}
function re(t) {
  let e, n = (
    /*t*/
    t[14].name + ""
  ), l, i, s, a;
  return {
    c() {
      e = S("button"), l = L(n), i = z(), this.h();
    },
    l(_) {
      e = N(_, "BUTTON", {
        role: !0,
        class: !0,
        "aria-selected": !0,
        "aria-controls": !0,
        id: !0
      });
      var d = C(e);
      l = J(d, n), i = y(d), d.forEach(g), this.h();
    },
    h() {
      m(e, "role", "tab"), m(e, "class", "selected svelte-lv9hp0"), m(e, "aria-selected", !0), m(e, "aria-controls", s = /*t*/
      t[14].elem_id), m(e, "id", a = /*t*/
      t[14].elem_id ? (
        /*t*/
        t[14].elem_id + "-button"
      ) : null);
    },
    m(_, d) {
      I(_, e, d), q(e, l), q(e, i);
    },
    p(_, d) {
      d & /*tabs*/
      8 && n !== (n = /*t*/
      _[14].name + "") && K(l, n), d & /*tabs*/
      8 && s !== (s = /*t*/
      _[14].elem_id) && m(e, "aria-controls", s), d & /*tabs*/
      8 && a !== (a = /*t*/
      _[14].elem_id ? (
        /*t*/
        _[14].elem_id + "-button"
      ) : null) && m(e, "id", a);
    },
    d(_) {
      _ && g(e);
    }
  };
}
function H(t, e) {
  let n, l, i = (
    /*t*/
    e[14].visible && G(e)
  );
  return {
    key: t,
    first: null,
    c() {
      n = E(), i && i.c(), l = E(), this.h();
    },
    l(s) {
      n = E(), i && i.l(s), l = E(), this.h();
    },
    h() {
      this.first = n;
    },
    m(s, a) {
      I(s, n, a), i && i.m(s, a), I(s, l, a);
    },
    p(s, a) {
      e = s, /*t*/
      e[14].visible ? i ? i.p(e, a) : (i = G(e), i.c(), i.m(l.parentNode, l)) : i && (i.d(1), i = null);
    },
    d(s) {
      s && (g(n), g(l)), i && i.d(s);
    }
  };
}
function de(t) {
  let e, n, l = [], i = /* @__PURE__ */ new Map(), s, a, _, d = V(
    /*tabs*/
    t[3]
  );
  const b = (o) => (
    /*t*/
    o[14].id
  );
  for (let o = 0; o < d.length; o += 1) {
    let c = F(t, d, o), f = b(c);
    i.set(f, l[o] = H(f, c));
  }
  const h = (
    /*#slots*/
    t[11].default
  ), u = Y(
    h,
    t,
    /*$$scope*/
    t[10],
    null
  );
  return {
    c() {
      e = S("div"), n = S("div");
      for (let o = 0; o < l.length; o += 1)
        l[o].c();
      s = z(), u && u.c(), this.h();
    },
    l(o) {
      e = N(o, "DIV", { class: !0, id: !0 });
      var c = C(e);
      n = N(c, "DIV", { class: !0, role: !0 });
      var f = C(n);
      for (let w = 0; w < l.length; w += 1)
        l[w].l(f);
      f.forEach(g), s = y(c), u && u.l(c), c.forEach(g), this.h();
    },
    h() {
      m(n, "class", "tab-nav scroll-hide svelte-lv9hp0"), m(n, "role", "tablist"), m(e, "class", a = "tabs " + /*elem_classes*/
      t[2].join(" ") + " svelte-lv9hp0"), m(
        e,
        "id",
        /*elem_id*/
        t[1]
      ), M(e, "hide", !/*visible*/
      t[0]);
    },
    m(o, c) {
      I(o, e, c), q(e, n);
      for (let f = 0; f < l.length; f += 1)
        l[f] && l[f].m(n, null);
      q(e, s), u && u.m(e, null), _ = !0;
    },
    p(o, [c]) {
      c & /*tabs, $selected_tab, change_tab, dispatch*/
      408 && (d = V(
        /*tabs*/
        o[3]
      ), l = se(l, c, b, 1, o, d, i, n, Z, H, null, F)), u && u.p && (!_ || c & /*$$scope*/
      1024) && ae(
        u,
        h,
        o,
        /*$$scope*/
        o[10],
        _ ? x(
          h,
          /*$$scope*/
          o[10],
          c,
          null
        ) : $(
          /*$$scope*/
          o[10]
        ),
        null
      ), (!_ || c & /*elem_classes*/
      4 && a !== (a = "tabs " + /*elem_classes*/
      o[2].join(" ") + " svelte-lv9hp0")) && m(e, "class", a), (!_ || c & /*elem_id*/
      2) && m(
        e,
        "id",
        /*elem_id*/
        o[1]
      ), (!_ || c & /*elem_classes, visible*/
      5) && M(e, "hide", !/*visible*/
      o[0]);
    },
    i(o) {
      _ || (ie(u, o), _ = !0);
    },
    o(o) {
      ne(u, o), _ = !1;
    },
    d(o) {
      o && g(e);
      for (let c = 0; c < l.length; c += 1)
        l[c].d();
      u && u.d(o);
    }
  };
}
function ue(t, e, n) {
  let l, i, { $$slots: s = {}, $$scope: a } = e, { visible: _ = !0 } = e, { elem_id: d = "id" } = e, { elem_classes: b = [] } = e, { selected: h } = e, u = [];
  const o = O(!1);
  U(t, o, (r) => n(4, i = r));
  const c = O(0);
  U(t, c, (r) => n(13, l = r));
  const f = oe();
  _e("good-tabs", {
    register_tab: (r) => {
      let v;
      return u.find((k) => k.id === r.id) ? (v = u.findIndex((k) => k.id === r.id), n(3, u[v] = { ...u[v], ...r }, u)) : (u.push({
        name: r.name,
        id: r.id,
        elem_id: r.elem_id,
        visible: r.visible,
        interactive: r.interactive
      }), v = u.length - 1), o.update((k) => {
        if (k === !1 && r.visible && r.interactive)
          return r.id;
        let D = u.find((B) => B.visible && B.interactive);
        return D ? D.id : k;
      }), n(3, u), v;
    },
    unregister_tab: (r) => {
      const v = u.findIndex((p) => p.id === r.id);
      u.splice(v, 1), o.update((p) => {
        var k, D;
        return p === r.id ? ((k = u[v]) == null ? void 0 : k.id) || ((D = u[u.length - 1]) == null ? void 0 : D.id) : p;
      });
    },
    selected_tab: o,
    selected_tab_index: c
  });
  function w(r) {
    const v = u.find((p) => p.id === r);
    v && v.interactive && v.visible ? (n(9, h = r), A(o, i = r, i), A(c, l = u.findIndex((p) => p.id === r), l), f("change")) : console.warn("Attempted to select a non-interactive or hidden tab.");
  }
  const R = (r, v) => {
    w(r.id), f("select", { value: r.name, index: v });
  };
  return t.$$set = (r) => {
    "visible" in r && n(0, _ = r.visible), "elem_id" in r && n(1, d = r.elem_id), "elem_classes" in r && n(2, b = r.elem_classes), "selected" in r && n(9, h = r.selected), "$$scope" in r && n(10, a = r.$$scope);
  }, t.$$.update = () => {
    t.$$.dirty & /*tabs, selected*/
    520 && h !== null && w(h);
  }, [
    _,
    d,
    b,
    u,
    i,
    o,
    c,
    f,
    w,
    h,
    a,
    s,
    R
  ];
}
class fe extends X {
  constructor(e) {
    super(), ee(this, e, ue, de, le, {
      visible: 0,
      elem_id: 1,
      elem_classes: 2,
      selected: 9
    });
  }
}
const {
  SvelteComponent: be,
  add_flush_callback: me,
  bind: he,
  binding_callbacks: ve,
  claim_component: ge,
  create_component: pe,
  create_slot: ke,
  destroy_component: we,
  get_all_dirty_from_scope: Te,
  get_slot_changes: Ee,
  init: qe,
  mount_component: Ie,
  safe_not_equal: De,
  transition_in: P,
  transition_out: Q,
  update_slot_base: Ce
} = window.__gradio__svelte__internal, { createEventDispatcher: Ne } = window.__gradio__svelte__internal;
function Se(t) {
  let e;
  const n = (
    /*#slots*/
    t[5].default
  ), l = ke(
    n,
    t,
    /*$$scope*/
    t[9],
    null
  );
  return {
    c() {
      l && l.c();
    },
    l(i) {
      l && l.l(i);
    },
    m(i, s) {
      l && l.m(i, s), e = !0;
    },
    p(i, s) {
      l && l.p && (!e || s & /*$$scope*/
      512) && Ce(
        l,
        n,
        i,
        /*$$scope*/
        i[9],
        e ? Ee(
          n,
          /*$$scope*/
          i[9],
          s,
          null
        ) : Te(
          /*$$scope*/
          i[9]
        ),
        null
      );
    },
    i(i) {
      e || (P(l, i), e = !0);
    },
    o(i) {
      Q(l, i), e = !1;
    },
    d(i) {
      l && l.d(i);
    }
  };
}
function je(t) {
  let e, n, l;
  function i(a) {
    t[6](a);
  }
  let s = {
    visible: (
      /*visible*/
      t[1]
    ),
    elem_id: (
      /*elem_id*/
      t[2]
    ),
    elem_classes: (
      /*elem_classes*/
      t[3]
    ),
    $$slots: { default: [Se] },
    $$scope: { ctx: t }
  };
  return (
    /*selected*/
    t[0] !== void 0 && (s.selected = /*selected*/
    t[0]), e = new fe({ props: s }), ve.push(() => he(e, "selected", i)), e.$on(
      "change",
      /*change_handler*/
      t[7]
    ), e.$on(
      "select",
      /*select_handler*/
      t[8]
    ), {
      c() {
        pe(e.$$.fragment);
      },
      l(a) {
        ge(e.$$.fragment, a);
      },
      m(a, _) {
        Ie(e, a, _), l = !0;
      },
      p(a, [_]) {
        const d = {};
        _ & /*visible*/
        2 && (d.visible = /*visible*/
        a[1]), _ & /*elem_id*/
        4 && (d.elem_id = /*elem_id*/
        a[2]), _ & /*elem_classes*/
        8 && (d.elem_classes = /*elem_classes*/
        a[3]), _ & /*$$scope*/
        512 && (d.$$scope = { dirty: _, ctx: a }), !n && _ & /*selected*/
        1 && (n = !0, d.selected = /*selected*/
        a[0], me(() => n = !1)), e.$set(d);
      },
      i(a) {
        l || (P(e.$$.fragment, a), l = !0);
      },
      o(a) {
        Q(e.$$.fragment, a), l = !1;
      },
      d(a) {
        we(e, a);
      }
    }
  );
}
function ye(t, e, n) {
  let { $$slots: l = {}, $$scope: i } = e;
  const s = Ne();
  let { visible: a = !0 } = e, { elem_id: _ = "" } = e, { elem_classes: d = [] } = e, { selected: b } = e, { gradio: h } = e;
  function u(f) {
    b = f, n(0, b);
  }
  const o = () => h.dispatch("change"), c = (f) => h.dispatch("select", f.detail);
  return t.$$set = (f) => {
    "visible" in f && n(1, a = f.visible), "elem_id" in f && n(2, _ = f.elem_id), "elem_classes" in f && n(3, d = f.elem_classes), "selected" in f && n(0, b = f.selected), "gradio" in f && n(4, h = f.gradio), "$$scope" in f && n(9, i = f.$$scope);
  }, t.$$.update = () => {
    t.$$.dirty & /*selected*/
    1 && s("prop_change", { selected: b });
  }, [
    b,
    a,
    _,
    d,
    h,
    l,
    u,
    o,
    c,
    i
  ];
}
class ze extends be {
  constructor(e) {
    super(), qe(this, e, ye, je, De, {
      visible: 1,
      elem_id: 2,
      elem_classes: 3,
      selected: 0,
      gradio: 4
    });
  }
}
export {
  ze as default
};
