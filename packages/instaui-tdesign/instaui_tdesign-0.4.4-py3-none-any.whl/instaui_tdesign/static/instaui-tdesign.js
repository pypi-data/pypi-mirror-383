import { defineComponent as V, useAttrs as lt, useSlots as ct, createBlock as Y, openBlock as J, mergeProps as pt, unref as h, createSlots as gt, renderList as Z, withCtx as j, renderSlot as dt, normalizeProps as ht, guardReactiveProps as _t, computed as w, ref as Jt, createElementVNode as St, createVNode as be, toDisplayString as rt, createTextVNode as Ct, resolveDynamicComponent as ve } from "vue";
import * as B from "tdesign-vue-next";
import { useConfig as me } from "tdesign-vue-next";
function Ae(t) {
  const { container: e = ".insta-main" } = t;
  return e;
}
const Te = /* @__PURE__ */ V({
  inheritAttrs: !1,
  __name: "Affix",
  setup(t) {
    const e = lt(), r = ct(), n = Ae(e);
    return (a, i) => (J(), Y(B.Affix, pt(h(e), { container: h(n) }), gt({ _: 2 }, [
      Z(h(r), (o, u) => ({
        name: u,
        fn: j((s) => [
          dt(a.$slots, u, ht(_t(s)))
        ])
      }))
    ]), 1040, ["container"]));
  }
});
var Qt = typeof global == "object" && global && global.Object === Object && global, we = typeof self == "object" && self && self.Object === Object && self, O = Qt || we || Function("return this")(), C = O.Symbol, kt = Object.prototype, Oe = kt.hasOwnProperty, $e = kt.toString, z = C ? C.toStringTag : void 0;
function Pe(t) {
  var e = Oe.call(t, z), r = t[z];
  try {
    t[z] = void 0;
    var n = !0;
  } catch {
  }
  var a = $e.call(t);
  return n && (e ? t[z] = r : delete t[z]), a;
}
var Se = Object.prototype, Ce = Se.toString;
function xe(t) {
  return Ce.call(t);
}
var Ee = "[object Null]", Re = "[object Undefined]", xt = C ? C.toStringTag : void 0;
function F(t) {
  return t == null ? t === void 0 ? Re : Ee : xt && xt in Object(t) ? Pe(t) : xe(t);
}
function D(t) {
  return t != null && typeof t == "object";
}
var je = "[object Symbol]";
function G(t) {
  return typeof t == "symbol" || D(t) && F(t) == je;
}
function X(t, e) {
  for (var r = -1, n = t == null ? 0 : t.length, a = Array(n); ++r < n; )
    a[r] = e(t[r], r, t);
  return a;
}
var b = Array.isArray, Et = C ? C.prototype : void 0, Rt = Et ? Et.toString : void 0;
function te(t) {
  if (typeof t == "string")
    return t;
  if (b(t))
    return X(t, te) + "";
  if (G(t))
    return Rt ? Rt.call(t) : "";
  var e = t + "";
  return e == "0" && 1 / t == -1 / 0 ? "-0" : e;
}
function yt(t) {
  var e = typeof t;
  return t != null && (e == "object" || e == "function");
}
function ee(t) {
  return t;
}
var Ie = "[object AsyncFunction]", De = "[object Function]", Fe = "[object GeneratorFunction]", Me = "[object Proxy]";
function re(t) {
  if (!yt(t))
    return !1;
  var e = F(t);
  return e == De || e == Fe || e == Ie || e == Me;
}
var nt = O["__core-js_shared__"], jt = function() {
  var t = /[^.]+$/.exec(nt && nt.keys && nt.keys.IE_PROTO || "");
  return t ? "Symbol(src)_1." + t : "";
}();
function Le(t) {
  return !!jt && jt in t;
}
var ze = Function.prototype, Ne = ze.toString;
function E(t) {
  if (t != null) {
    try {
      return Ne.call(t);
    } catch {
    }
    try {
      return t + "";
    } catch {
    }
  }
  return "";
}
var Be = /[\\^$.*+?()[\]{}|]/g, Ge = /^\[object .+?Constructor\]$/, He = Function.prototype, Ue = Object.prototype, Ke = He.toString, qe = Ue.hasOwnProperty, We = RegExp(
  "^" + Ke.call(qe).replace(Be, "\\$&").replace(/hasOwnProperty|(function).*?(?=\\\()| for .+?(?=\\\])/g, "$1.*?") + "$"
);
function Xe(t) {
  if (!yt(t) || Le(t))
    return !1;
  var e = re(t) ? We : Ge;
  return e.test(E(t));
}
function Ze(t, e) {
  return t?.[e];
}
function M(t, e) {
  var r = Ze(t, e);
  return Xe(r) ? r : void 0;
}
var ot = M(O, "WeakMap");
function Ve() {
}
function Ye(t, e, r, n) {
  for (var a = t.length, i = r + -1; ++i < a; )
    if (e(t[i], i, t))
      return i;
  return -1;
}
function Je(t) {
  return t !== t;
}
function Qe(t, e, r) {
  for (var n = r - 1, a = t.length; ++n < a; )
    if (t[n] === e)
      return n;
  return -1;
}
function ke(t, e, r) {
  return e === e ? Qe(t, e, r) : Ye(t, Je, r);
}
function tr(t, e) {
  var r = t == null ? 0 : t.length;
  return !!r && ke(t, e, 0) > -1;
}
var er = 9007199254740991, rr = /^(?:0|[1-9]\d*)$/;
function ne(t, e) {
  var r = typeof t;
  return e = e ?? er, !!e && (r == "number" || r != "symbol" && rr.test(t)) && t > -1 && t % 1 == 0 && t < e;
}
function ie(t, e) {
  return t === e || t !== t && e !== e;
}
var nr = 9007199254740991;
function bt(t) {
  return typeof t == "number" && t > -1 && t % 1 == 0 && t <= nr;
}
function vt(t) {
  return t != null && bt(t.length) && !re(t);
}
var ir = Object.prototype;
function ar(t) {
  var e = t && t.constructor, r = typeof e == "function" && e.prototype || ir;
  return t === r;
}
function or(t, e) {
  for (var r = -1, n = Array(t); ++r < t; )
    n[r] = e(r);
  return n;
}
var sr = "[object Arguments]";
function It(t) {
  return D(t) && F(t) == sr;
}
var ae = Object.prototype, ur = ae.hasOwnProperty, fr = ae.propertyIsEnumerable, oe = It(/* @__PURE__ */ function() {
  return arguments;
}()) ? It : function(t) {
  return D(t) && ur.call(t, "callee") && !fr.call(t, "callee");
};
function lr() {
  return !1;
}
var se = typeof exports == "object" && exports && !exports.nodeType && exports, Dt = se && typeof module == "object" && module && !module.nodeType && module, cr = Dt && Dt.exports === se, Ft = cr ? O.Buffer : void 0, pr = Ft ? Ft.isBuffer : void 0, st = pr || lr, gr = "[object Arguments]", dr = "[object Array]", hr = "[object Boolean]", _r = "[object Date]", yr = "[object Error]", br = "[object Function]", vr = "[object Map]", mr = "[object Number]", Ar = "[object Object]", Tr = "[object RegExp]", wr = "[object Set]", Or = "[object String]", $r = "[object WeakMap]", Pr = "[object ArrayBuffer]", Sr = "[object DataView]", Cr = "[object Float32Array]", xr = "[object Float64Array]", Er = "[object Int8Array]", Rr = "[object Int16Array]", jr = "[object Int32Array]", Ir = "[object Uint8Array]", Dr = "[object Uint8ClampedArray]", Fr = "[object Uint16Array]", Mr = "[object Uint32Array]", d = {};
d[Cr] = d[xr] = d[Er] = d[Rr] = d[jr] = d[Ir] = d[Dr] = d[Fr] = d[Mr] = !0;
d[gr] = d[dr] = d[Pr] = d[hr] = d[Sr] = d[_r] = d[yr] = d[br] = d[vr] = d[mr] = d[Ar] = d[Tr] = d[wr] = d[Or] = d[$r] = !1;
function Lr(t) {
  return D(t) && bt(t.length) && !!d[F(t)];
}
function ue(t) {
  return function(e) {
    return t(e);
  };
}
var fe = typeof exports == "object" && exports && !exports.nodeType && exports, N = fe && typeof module == "object" && module && !module.nodeType && module, zr = N && N.exports === fe, it = zr && Qt.process, Mt = function() {
  try {
    var t = N && N.require && N.require("util").types;
    return t || it && it.binding && it.binding("util");
  } catch {
  }
}(), Lt = Mt && Mt.isTypedArray, le = Lt ? ue(Lt) : Lr, Nr = Object.prototype, Br = Nr.hasOwnProperty;
function Gr(t, e) {
  var r = b(t), n = !r && oe(t), a = !r && !n && st(t), i = !r && !n && !a && le(t), o = r || n || a || i, u = o ? or(t.length, String) : [], s = u.length;
  for (var f in t)
    Br.call(t, f) && !(o && // Safari 9 has enumerable `arguments.length` in strict mode.
    (f == "length" || // Node.js 0.10 has enumerable non-index properties on buffers.
    a && (f == "offset" || f == "parent") || // PhantomJS 2 has enumerable non-index properties on typed arrays.
    i && (f == "buffer" || f == "byteLength" || f == "byteOffset") || // Skip index properties.
    ne(f, s))) && u.push(f);
  return u;
}
function Hr(t, e) {
  return function(r) {
    return t(e(r));
  };
}
var Ur = Hr(Object.keys, Object), Kr = Object.prototype, qr = Kr.hasOwnProperty;
function Wr(t) {
  if (!ar(t))
    return Ur(t);
  var e = [];
  for (var r in Object(t))
    qr.call(t, r) && r != "constructor" && e.push(r);
  return e;
}
function mt(t) {
  return vt(t) ? Gr(t) : Wr(t);
}
var Xr = /\.|\[(?:[^[\]]*|(["'])(?:(?!\1)[^\\]|\\.)*?\1)\]/, Zr = /^\w*$/;
function At(t, e) {
  if (b(t))
    return !1;
  var r = typeof t;
  return r == "number" || r == "symbol" || r == "boolean" || t == null || G(t) ? !0 : Zr.test(t) || !Xr.test(t) || e != null && t in Object(e);
}
var H = M(Object, "create");
function Vr() {
  this.__data__ = H ? H(null) : {}, this.size = 0;
}
function Yr(t) {
  var e = this.has(t) && delete this.__data__[t];
  return this.size -= e ? 1 : 0, e;
}
var Jr = "__lodash_hash_undefined__", Qr = Object.prototype, kr = Qr.hasOwnProperty;
function tn(t) {
  var e = this.__data__;
  if (H) {
    var r = e[t];
    return r === Jr ? void 0 : r;
  }
  return kr.call(e, t) ? e[t] : void 0;
}
var en = Object.prototype, rn = en.hasOwnProperty;
function nn(t) {
  var e = this.__data__;
  return H ? e[t] !== void 0 : rn.call(e, t);
}
var an = "__lodash_hash_undefined__";
function on(t, e) {
  var r = this.__data__;
  return this.size += this.has(t) ? 0 : 1, r[t] = H && e === void 0 ? an : e, this;
}
function x(t) {
  var e = -1, r = t == null ? 0 : t.length;
  for (this.clear(); ++e < r; ) {
    var n = t[e];
    this.set(n[0], n[1]);
  }
}
x.prototype.clear = Vr;
x.prototype.delete = Yr;
x.prototype.get = tn;
x.prototype.has = nn;
x.prototype.set = on;
function sn() {
  this.__data__ = [], this.size = 0;
}
function Q(t, e) {
  for (var r = t.length; r--; )
    if (ie(t[r][0], e))
      return r;
  return -1;
}
var un = Array.prototype, fn = un.splice;
function ln(t) {
  var e = this.__data__, r = Q(e, t);
  if (r < 0)
    return !1;
  var n = e.length - 1;
  return r == n ? e.pop() : fn.call(e, r, 1), --this.size, !0;
}
function cn(t) {
  var e = this.__data__, r = Q(e, t);
  return r < 0 ? void 0 : e[r][1];
}
function pn(t) {
  return Q(this.__data__, t) > -1;
}
function gn(t, e) {
  var r = this.__data__, n = Q(r, t);
  return n < 0 ? (++this.size, r.push([t, e])) : r[n][1] = e, this;
}
function $(t) {
  var e = -1, r = t == null ? 0 : t.length;
  for (this.clear(); ++e < r; ) {
    var n = t[e];
    this.set(n[0], n[1]);
  }
}
$.prototype.clear = sn;
$.prototype.delete = ln;
$.prototype.get = cn;
$.prototype.has = pn;
$.prototype.set = gn;
var U = M(O, "Map");
function dn() {
  this.size = 0, this.__data__ = {
    hash: new x(),
    map: new (U || $)(),
    string: new x()
  };
}
function hn(t) {
  var e = typeof t;
  return e == "string" || e == "number" || e == "symbol" || e == "boolean" ? t !== "__proto__" : t === null;
}
function k(t, e) {
  var r = t.__data__;
  return hn(e) ? r[typeof e == "string" ? "string" : "hash"] : r.map;
}
function _n(t) {
  var e = k(this, t).delete(t);
  return this.size -= e ? 1 : 0, e;
}
function yn(t) {
  return k(this, t).get(t);
}
function bn(t) {
  return k(this, t).has(t);
}
function vn(t, e) {
  var r = k(this, t), n = r.size;
  return r.set(t, e), this.size += r.size == n ? 0 : 1, this;
}
function P(t) {
  var e = -1, r = t == null ? 0 : t.length;
  for (this.clear(); ++e < r; ) {
    var n = t[e];
    this.set(n[0], n[1]);
  }
}
P.prototype.clear = dn;
P.prototype.delete = _n;
P.prototype.get = yn;
P.prototype.has = bn;
P.prototype.set = vn;
var mn = "Expected a function";
function Tt(t, e) {
  if (typeof t != "function" || e != null && typeof e != "function")
    throw new TypeError(mn);
  var r = function() {
    var n = arguments, a = e ? e.apply(this, n) : n[0], i = r.cache;
    if (i.has(a))
      return i.get(a);
    var o = t.apply(this, n);
    return r.cache = i.set(a, o) || i, o;
  };
  return r.cache = new (Tt.Cache || P)(), r;
}
Tt.Cache = P;
var An = 500;
function Tn(t) {
  var e = Tt(t, function(n) {
    return r.size === An && r.clear(), n;
  }), r = e.cache;
  return e;
}
var wn = /[^.[\]]+|\[(?:(-?\d+(?:\.\d+)?)|(["'])((?:(?!\2)[^\\]|\\.)*?)\2)\]|(?=(?:\.|\[\])(?:\.|\[\]|$))/g, On = /\\(\\)?/g, $n = Tn(function(t) {
  var e = [];
  return t.charCodeAt(0) === 46 && e.push(""), t.replace(wn, function(r, n, a, i) {
    e.push(a ? i.replace(On, "$1") : n || r);
  }), e;
});
function Pn(t) {
  return t == null ? "" : te(t);
}
function ce(t, e) {
  return b(t) ? t : At(t, e) ? [t] : $n(Pn(t));
}
function tt(t) {
  if (typeof t == "string" || G(t))
    return t;
  var e = t + "";
  return e == "0" && 1 / t == -1 / 0 ? "-0" : e;
}
function wt(t, e) {
  e = ce(e, t);
  for (var r = 0, n = e.length; t != null && r < n; )
    t = t[tt(e[r++])];
  return r && r == n ? t : void 0;
}
function Sn(t, e, r) {
  var n = t == null ? void 0 : wt(t, e);
  return n === void 0 ? r : n;
}
function Cn(t, e) {
  for (var r = -1, n = e.length, a = t.length; ++r < n; )
    t[a + r] = e[r];
  return t;
}
function xn() {
  this.__data__ = new $(), this.size = 0;
}
function En(t) {
  var e = this.__data__, r = e.delete(t);
  return this.size = e.size, r;
}
function Rn(t) {
  return this.__data__.get(t);
}
function jn(t) {
  return this.__data__.has(t);
}
var In = 200;
function Dn(t, e) {
  var r = this.__data__;
  if (r instanceof $) {
    var n = r.__data__;
    if (!U || n.length < In - 1)
      return n.push([t, e]), this.size = ++r.size, this;
    r = this.__data__ = new P(n);
  }
  return r.set(t, e), this.size = r.size, this;
}
function T(t) {
  var e = this.__data__ = new $(t);
  this.size = e.size;
}
T.prototype.clear = xn;
T.prototype.delete = En;
T.prototype.get = Rn;
T.prototype.has = jn;
T.prototype.set = Dn;
function Fn(t, e) {
  for (var r = -1, n = t == null ? 0 : t.length, a = 0, i = []; ++r < n; ) {
    var o = t[r];
    e(o, r, t) && (i[a++] = o);
  }
  return i;
}
function Mn() {
  return [];
}
var Ln = Object.prototype, zn = Ln.propertyIsEnumerable, zt = Object.getOwnPropertySymbols, Nn = zt ? function(t) {
  return t == null ? [] : (t = Object(t), Fn(zt(t), function(e) {
    return zn.call(t, e);
  }));
} : Mn;
function Bn(t, e, r) {
  var n = e(t);
  return b(t) ? n : Cn(n, r(t));
}
function Nt(t) {
  return Bn(t, mt, Nn);
}
var ut = M(O, "DataView"), ft = M(O, "Promise"), I = M(O, "Set"), Bt = "[object Map]", Gn = "[object Object]", Gt = "[object Promise]", Ht = "[object Set]", Ut = "[object WeakMap]", Kt = "[object DataView]", Hn = E(ut), Un = E(U), Kn = E(ft), qn = E(I), Wn = E(ot), S = F;
(ut && S(new ut(new ArrayBuffer(1))) != Kt || U && S(new U()) != Bt || ft && S(ft.resolve()) != Gt || I && S(new I()) != Ht || ot && S(new ot()) != Ut) && (S = function(t) {
  var e = F(t), r = e == Gn ? t.constructor : void 0, n = r ? E(r) : "";
  if (n)
    switch (n) {
      case Hn:
        return Kt;
      case Un:
        return Bt;
      case Kn:
        return Gt;
      case qn:
        return Ht;
      case Wn:
        return Ut;
    }
  return e;
});
var qt = O.Uint8Array, Xn = "__lodash_hash_undefined__";
function Zn(t) {
  return this.__data__.set(t, Xn), this;
}
function Vn(t) {
  return this.__data__.has(t);
}
function K(t) {
  var e = -1, r = t == null ? 0 : t.length;
  for (this.__data__ = new P(); ++e < r; )
    this.add(t[e]);
}
K.prototype.add = K.prototype.push = Zn;
K.prototype.has = Vn;
function Yn(t, e) {
  for (var r = -1, n = t == null ? 0 : t.length; ++r < n; )
    if (e(t[r], r, t))
      return !0;
  return !1;
}
function pe(t, e) {
  return t.has(e);
}
var Jn = 1, Qn = 2;
function ge(t, e, r, n, a, i) {
  var o = r & Jn, u = t.length, s = e.length;
  if (u != s && !(o && s > u))
    return !1;
  var f = i.get(t), l = i.get(e);
  if (f && l)
    return f == e && l == t;
  var p = -1, c = !0, _ = r & Qn ? new K() : void 0;
  for (i.set(t, e), i.set(e, t); ++p < u; ) {
    var g = t[p], y = e[p];
    if (n)
      var v = o ? n(y, g, p, e, t, i) : n(g, y, p, t, e, i);
    if (v !== void 0) {
      if (v)
        continue;
      c = !1;
      break;
    }
    if (_) {
      if (!Yn(e, function(A, m) {
        if (!pe(_, m) && (g === A || a(g, A, r, n, i)))
          return _.push(m);
      })) {
        c = !1;
        break;
      }
    } else if (!(g === y || a(g, y, r, n, i))) {
      c = !1;
      break;
    }
  }
  return i.delete(t), i.delete(e), c;
}
function kn(t) {
  var e = -1, r = Array(t.size);
  return t.forEach(function(n, a) {
    r[++e] = [a, n];
  }), r;
}
function Ot(t) {
  var e = -1, r = Array(t.size);
  return t.forEach(function(n) {
    r[++e] = n;
  }), r;
}
var ti = 1, ei = 2, ri = "[object Boolean]", ni = "[object Date]", ii = "[object Error]", ai = "[object Map]", oi = "[object Number]", si = "[object RegExp]", ui = "[object Set]", fi = "[object String]", li = "[object Symbol]", ci = "[object ArrayBuffer]", pi = "[object DataView]", Wt = C ? C.prototype : void 0, at = Wt ? Wt.valueOf : void 0;
function gi(t, e, r, n, a, i, o) {
  switch (r) {
    case pi:
      if (t.byteLength != e.byteLength || t.byteOffset != e.byteOffset)
        return !1;
      t = t.buffer, e = e.buffer;
    case ci:
      return !(t.byteLength != e.byteLength || !i(new qt(t), new qt(e)));
    case ri:
    case ni:
    case oi:
      return ie(+t, +e);
    case ii:
      return t.name == e.name && t.message == e.message;
    case si:
    case fi:
      return t == e + "";
    case ai:
      var u = kn;
    case ui:
      var s = n & ti;
      if (u || (u = Ot), t.size != e.size && !s)
        return !1;
      var f = o.get(t);
      if (f)
        return f == e;
      n |= ei, o.set(t, e);
      var l = ge(u(t), u(e), n, a, i, o);
      return o.delete(t), l;
    case li:
      if (at)
        return at.call(t) == at.call(e);
  }
  return !1;
}
var di = 1, hi = Object.prototype, _i = hi.hasOwnProperty;
function yi(t, e, r, n, a, i) {
  var o = r & di, u = Nt(t), s = u.length, f = Nt(e), l = f.length;
  if (s != l && !o)
    return !1;
  for (var p = s; p--; ) {
    var c = u[p];
    if (!(o ? c in e : _i.call(e, c)))
      return !1;
  }
  var _ = i.get(t), g = i.get(e);
  if (_ && g)
    return _ == e && g == t;
  var y = !0;
  i.set(t, e), i.set(e, t);
  for (var v = o; ++p < s; ) {
    c = u[p];
    var A = t[c], m = e[c];
    if (n)
      var q = o ? n(m, A, c, e, t, i) : n(A, m, c, t, e, i);
    if (!(q === void 0 ? A === m || a(A, m, r, n, i) : q)) {
      y = !1;
      break;
    }
    v || (v = c == "constructor");
  }
  if (y && !v) {
    var R = t.constructor, L = e.constructor;
    R != L && "constructor" in t && "constructor" in e && !(typeof R == "function" && R instanceof R && typeof L == "function" && L instanceof L) && (y = !1);
  }
  return i.delete(t), i.delete(e), y;
}
var bi = 1, Xt = "[object Arguments]", Zt = "[object Array]", W = "[object Object]", vi = Object.prototype, Vt = vi.hasOwnProperty;
function mi(t, e, r, n, a, i) {
  var o = b(t), u = b(e), s = o ? Zt : S(t), f = u ? Zt : S(e);
  s = s == Xt ? W : s, f = f == Xt ? W : f;
  var l = s == W, p = f == W, c = s == f;
  if (c && st(t)) {
    if (!st(e))
      return !1;
    o = !0, l = !1;
  }
  if (c && !l)
    return i || (i = new T()), o || le(t) ? ge(t, e, r, n, a, i) : gi(t, e, s, r, n, a, i);
  if (!(r & bi)) {
    var _ = l && Vt.call(t, "__wrapped__"), g = p && Vt.call(e, "__wrapped__");
    if (_ || g) {
      var y = _ ? t.value() : t, v = g ? e.value() : e;
      return i || (i = new T()), a(y, v, r, n, i);
    }
  }
  return c ? (i || (i = new T()), yi(t, e, r, n, a, i)) : !1;
}
function $t(t, e, r, n, a) {
  return t === e ? !0 : t == null || e == null || !D(t) && !D(e) ? t !== t && e !== e : mi(t, e, r, n, $t, a);
}
var Ai = 1, Ti = 2;
function wi(t, e, r, n) {
  var a = r.length, i = a;
  if (t == null)
    return !i;
  for (t = Object(t); a--; ) {
    var o = r[a];
    if (o[2] ? o[1] !== t[o[0]] : !(o[0] in t))
      return !1;
  }
  for (; ++a < i; ) {
    o = r[a];
    var u = o[0], s = t[u], f = o[1];
    if (o[2]) {
      if (s === void 0 && !(u in t))
        return !1;
    } else {
      var l = new T(), p;
      if (!(p === void 0 ? $t(f, s, Ai | Ti, n, l) : p))
        return !1;
    }
  }
  return !0;
}
function de(t) {
  return t === t && !yt(t);
}
function Oi(t) {
  for (var e = mt(t), r = e.length; r--; ) {
    var n = e[r], a = t[n];
    e[r] = [n, a, de(a)];
  }
  return e;
}
function he(t, e) {
  return function(r) {
    return r == null ? !1 : r[t] === e && (e !== void 0 || t in Object(r));
  };
}
function $i(t) {
  var e = Oi(t);
  return e.length == 1 && e[0][2] ? he(e[0][0], e[0][1]) : function(r) {
    return r === t || wi(r, t, e);
  };
}
function Pi(t, e) {
  return t != null && e in Object(t);
}
function Si(t, e, r) {
  e = ce(e, t);
  for (var n = -1, a = e.length, i = !1; ++n < a; ) {
    var o = tt(e[n]);
    if (!(i = t != null && r(t, o)))
      break;
    t = t[o];
  }
  return i || ++n != a ? i : (a = t == null ? 0 : t.length, !!a && bt(a) && ne(o, a) && (b(t) || oe(t)));
}
function Ci(t, e) {
  return t != null && Si(t, e, Pi);
}
var xi = 1, Ei = 2;
function Ri(t, e) {
  return At(t) && de(e) ? he(tt(t), e) : function(r) {
    var n = Sn(r, t);
    return n === void 0 && n === e ? Ci(r, t) : $t(e, n, xi | Ei);
  };
}
function ji(t) {
  return function(e) {
    return e?.[t];
  };
}
function Ii(t) {
  return function(e) {
    return wt(e, t);
  };
}
function Di(t) {
  return At(t) ? ji(tt(t)) : Ii(t);
}
function _e(t) {
  return typeof t == "function" ? t : t == null ? ee : typeof t == "object" ? b(t) ? Ri(t[0], t[1]) : $i(t) : Di(t);
}
function Fi(t) {
  return function(e, r, n) {
    for (var a = -1, i = Object(e), o = n(e), u = o.length; u--; ) {
      var s = o[++a];
      if (r(i[s], s, i) === !1)
        break;
    }
    return e;
  };
}
var Mi = Fi();
function Li(t, e) {
  return t && Mi(t, e, mt);
}
function zi(t, e) {
  return function(r, n) {
    if (r == null)
      return r;
    if (!vt(r))
      return t(r, n);
    for (var a = r.length, i = -1, o = Object(r); ++i < a && n(o[i], i, o) !== !1; )
      ;
    return r;
  };
}
var Ni = zi(Li);
function Bi(t, e) {
  var r = -1, n = vt(t) ? Array(t.length) : [];
  return Ni(t, function(a, i, o) {
    n[++r] = e(a, i, o);
  }), n;
}
function Gi(t, e) {
  var r = t.length;
  for (t.sort(e); r--; )
    t[r] = t[r].value;
  return t;
}
function Hi(t, e) {
  if (t !== e) {
    var r = t !== void 0, n = t === null, a = t === t, i = G(t), o = e !== void 0, u = e === null, s = e === e, f = G(e);
    if (!u && !f && !i && t > e || i && o && s && !u && !f || n && o && s || !r && s || !a)
      return 1;
    if (!n && !i && !f && t < e || f && r && a && !n && !i || u && r && a || !o && a || !s)
      return -1;
  }
  return 0;
}
function Ui(t, e, r) {
  for (var n = -1, a = t.criteria, i = e.criteria, o = a.length, u = r.length; ++n < o; ) {
    var s = Hi(a[n], i[n]);
    if (s) {
      if (n >= u)
        return s;
      var f = r[n];
      return s * (f == "desc" ? -1 : 1);
    }
  }
  return t.index - e.index;
}
function Ki(t, e, r) {
  e.length ? e = X(e, function(i) {
    return b(i) ? function(o) {
      return wt(o, i.length === 1 ? i[0] : i);
    } : i;
  }) : e = [ee];
  var n = -1;
  e = X(e, ue(_e));
  var a = Bi(t, function(i, o, u) {
    var s = X(e, function(f) {
      return f(i);
    });
    return { criteria: s, index: ++n, value: i };
  });
  return Gi(a, function(i, o) {
    return Ui(i, o, r);
  });
}
function qi(t, e, r, n) {
  return t == null ? [] : (b(e) || (e = e == null ? [] : [e]), r = r, b(r) || (r = r == null ? [] : [r]), Ki(t, e, r));
}
var Wi = 1 / 0, Xi = I && 1 / Ot(new I([, -0]))[1] == Wi ? function(t) {
  return new I(t);
} : Ve, Zi = 200;
function Vi(t, e, r) {
  var n = -1, a = tr, i = t.length, o = !0, u = [], s = u;
  if (i >= Zi) {
    var f = e ? null : Xi(t);
    if (f)
      return Ot(f);
    o = !1, a = pe, s = new K();
  } else
    s = e ? [] : u;
  t:
    for (; ++n < i; ) {
      var l = t[n], p = e ? e(l) : l;
      if (l = l !== 0 ? l : 0, o && p === p) {
        for (var c = s.length; c--; )
          if (s[c] === p)
            continue t;
        e && s.push(p), u.push(l);
      } else a(s, p, r) || (s !== u && s.push(p), u.push(l));
    }
  return u;
}
function Yt(t, e) {
  return t && t.length ? Vi(t, _e(e)) : [];
}
const Yi = {
  hover: !0,
  bordered: !0,
  tableLayout: "auto",
  showSortColumnBgColor: !0
};
function Ji(t) {
  const e = [], r = w(() => t.data ?? []);
  return {
    tableData: w(() => {
      const i = r.value;
      return e.reduce((o, u) => u(o), i);
    }),
    orgData: r,
    registerRowsHandler: (i) => {
      e.push(i);
    }
  };
}
function Qi(t) {
  const { tableData: e, attrs: r } = t, n = [], a = w(() => {
    let u = !r.columns && e.value.length > 0 ? na(e.value) : r.columns ?? [];
    u = u.map(ia);
    for (const s of n)
      u = s(u);
    return u;
  });
  function i(o) {
    n.push(o);
  }
  return [a, i];
}
function ki(t) {
  const { tableData: e, attrs: r } = t;
  return w(() => {
    const { pagination: n } = r;
    let a;
    if (typeof n == "boolean") {
      if (!n)
        return;
      a = {
        defaultPageSize: 10
      };
    }
    return typeof n == "number" && n > 0 && (a = {
      defaultPageSize: n
    }), typeof n == "object" && n !== null && (a = n), {
      defaultCurrent: 1,
      total: e.value.length,
      ...a
    };
  });
}
function ta(t) {
  const { attrs: e, columns: r, registerRowsHandler: n } = t;
  let a = Jt(e.sort);
  const i = w(() => r.value?.some((s) => s.sorter)), o = w(
    () => r.value.filter((s) => s.sorter).length > 1
  );
  return n((s) => {
    if (!a.value)
      return s;
    const f = Array.isArray(a.value) ? a.value : [a.value], l = f.map((c) => c.sortBy), p = f.map(
      (c) => c.descending ? "desc" : "asc"
    );
    return qi(s, l, p);
  }), {
    onSortChange: (s) => {
      i.value && (a.value = s);
    },
    multipleSort: o,
    sort: a
  };
}
function ea(t) {
  const { tableData: e, registerColumnsHandler: r, registerRowsHandler: n, columns: a } = t;
  r(
    (l) => l.map(
      (p) => aa(
        p,
        e,
        t.tdesignGlobalConfig
      )
    )
  );
  const i = Jt(), o = new Map(a.value.map((l) => [l.colKey, l]));
  n((l) => {
    if (!i.value)
      return l;
    const p = Object.keys(i.value).map((c) => {
      const _ = i.value[c], g = o.get(c).filter.type;
      return {
        key: c,
        value: _,
        type: g
      };
    });
    return l.filter((c) => p.every((_) => {
      if (_.type === "multiple") {
        const g = _.value;
        return g.length === 0 ? !0 : g.includes(c[_.key]);
      }
      if (_.type === "single") {
        const g = _.value;
        return g ? c[_.key] === g : !0;
      }
      if (_.type === "input") {
        const g = _.value;
        return g ? c[_.key].toString().includes(g) : !0;
      }
      throw new Error("not support filter type");
    }));
  });
  const u = (l, p) => {
    if (!p.col) {
      i.value = void 0;
      return;
    }
    i.value = {
      ...l
    };
  };
  function s() {
    i.value = void 0;
  }
  function f() {
    return i.value ? Object.keys(i.value).map((l) => {
      const p = o.get(l).label, c = i.value[l];
      return c.length === 0 ? "" : `${p}: ${JSON.stringify(c)}`;
    }).join("; ") : null;
  }
  return {
    onFilterChange: u,
    filterValue: i,
    resetFilters: s,
    filterResultText: f
  };
}
function ra(t) {
  const { attrs: e } = t;
  return w(() => ({
    ...Yi,
    ...e
  }));
}
function na(t) {
  const e = t[0];
  return Object.keys(e).map((n) => ({
    colKey: n,
    title: n,
    sorter: !0
  }));
}
function ia(t) {
  const e = t.name ?? t.colKey, r = `header-cell-${e}`, n = `body-cell-${e}`, a = t.label ?? t.colKey;
  return {
    ...t,
    name: e,
    label: a,
    title: r,
    cell: n
  };
}
function aa(t, e, r) {
  if (!("filter" in t))
    return t;
  if (!("type" in t.filter)) throw new Error("filter type is required");
  const { colKey: a } = t, { type: i } = t.filter;
  if (i === "multiple") {
    const o = Yt(e.value, a).map((s) => ({
      label: s[a],
      value: s[a]
    })), u = {
      resetValue: [],
      list: [
        { label: r.selectAllText, checkAll: !0 },
        ...o
      ],
      ...t.filter
    };
    return {
      ...t,
      filter: u
    };
  }
  if (i === "single") {
    const u = {
      resetValue: null,
      list: Yt(e.value, a).map((s) => ({
        label: s[a],
        value: s[a]
      })),
      showConfirmAndReset: !0,
      ...t.filter
    };
    return {
      ...t,
      filter: u
    };
  }
  if (i === "input") {
    const o = {
      resetValue: "",
      confirmEvents: ["onEnter"],
      showConfirmAndReset: !0,
      ...t.filter,
      props: {
        ...t.filter?.props
      }
    };
    return {
      ...t,
      filter: o
    };
  }
  throw new Error("not support filter type");
}
function oa(t, e) {
  return w(() => {
    const r = Object.keys(t).filter(
      (n) => n.startsWith("header-cell-")
    );
    return e.value.filter((n) => !r.includes(n.title)).map((n) => ({
      slotName: `header-cell-${n.name}`,
      content: n.label ?? n.colKey
    }));
  });
}
const sa = /* @__PURE__ */ V({
  inheritAttrs: !1,
  __name: "Table",
  setup(t) {
    const e = lt(), { t: r, globalConfig: n } = me("table"), { tableData: a, orgData: i, registerRowsHandler: o } = Ji(e), [u, s] = Qi({
      tableData: a,
      attrs: e
    }), f = ki({ tableData: a, attrs: e }), { sort: l, onSortChange: p, multipleSort: c } = ta({
      registerRowsHandler: o,
      attrs: e,
      columns: u
    }), { onFilterChange: _, filterValue: g, resetFilters: y, filterResultText: v } = ea({
      tableData: i,
      registerRowsHandler: o,
      registerColumnsHandler: s,
      columns: u,
      tdesignGlobalConfig: n.value
    }), A = ra({ attrs: e }), m = ct(), q = oa(m, u);
    return (R, L) => (J(), Y(B.Table, pt(h(A), {
      pagination: h(f),
      sort: h(l),
      data: h(a),
      columns: h(u),
      "filter-value": h(g),
      onSortChange: h(p),
      onFilterChange: h(_),
      "multiple-sort": h(c)
    }), gt({
      "filter-row": j(() => [
        St("div", null, [
          St("span", null, rt(h(r)(h(n).searchResultText, {
            result: h(v)(),
            count: h(a).length
          })), 1),
          be(B.Button, {
            theme: "primary",
            variant: "text",
            onClick: h(y)
          }, {
            default: j(() => [
              Ct(rt(h(n).clearFilterResultButtonText), 1)
            ]),
            _: 1
          }, 8, ["onClick"])
        ])
      ]),
      _: 2
    }, [
      Z(h(q), (et) => ({
        name: et.slotName,
        fn: j(() => [
          Ct(rt(et.content), 1)
        ])
      })),
      Z(h(m), (et, Pt) => ({
        name: Pt,
        fn: j((ye) => [
          dt(R.$slots, Pt, ht(_t(ye)))
        ])
      }))
    ]), 1040, ["pagination", "sort", "data", "columns", "filter-value", "onSortChange", "onFilterChange", "multiple-sort"]));
  }
});
function ua(t) {
  const { affixProps: e = {} } = t;
  return {
    container: ".insta-main",
    ...e
  };
}
function fa(t) {
  const { container: e = ".insta-main" } = t;
  return e;
}
const la = /* @__PURE__ */ V({
  inheritAttrs: !1,
  __name: "Anchor",
  setup(t) {
    const e = lt(), r = ct(), n = ua(e), a = fa(e);
    return (i, o) => (J(), Y(B.Anchor, pt(h(e), {
      container: h(a),
      "affix-props": h(n)
    }), gt({ _: 2 }, [
      Z(h(r), (u, s) => ({
        name: s,
        fn: j((f) => [
          dt(i.$slots, s, ht(_t(f)))
        ])
      }))
    ]), 1040, ["container", "affix-props"]));
  }
}), ca = /* @__PURE__ */ V({
  __name: "Icon",
  props: {
    name: {},
    size: {},
    color: {},
    prefix: {}
  },
  setup(t) {
    const e = t, r = w(() => {
      const [n, a] = e.name.split(":");
      return a ? e.name : `${e.prefix || "tdesign"}:${e.name}`;
    });
    return (n, a) => (J(), Y(ve("icon"), {
      class: "t-icon",
      icon: r.value,
      size: n.size,
      color: n.color
    }, null, 8, ["icon", "size", "color"]));
  }
});
function da(t) {
  t.use(B), t.component("t-table", sa), t.component("t-affix", Te), t.component("t-anchor", la), t.component("t-icon", ca);
}
export {
  da as install
};
