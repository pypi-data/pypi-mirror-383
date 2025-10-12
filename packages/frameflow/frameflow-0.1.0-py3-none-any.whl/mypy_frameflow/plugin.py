from collections.abc import Callable
from typing import Any, cast

from mypy.nodes import (
    DictExpr,
    Import,
    ImportFrom,
    ListExpr,
    MypyFile,
    StrExpr,
    TupleExpr,
    TypeInfo,
    Var,
)
from mypy.plugin import FunctionContext, MethodContext, Plugin
from mypy.types import (
    AnyType,
    Instance,
    LiteralType,
    Type,
    TypeOfAny,
    TypeType,
    UnboundType,
    UnionType,
    get_proper_type,
)

FRAMEFLOW_DF_DEF = "frameflow.typing.DataFrame"
FRAMEFLOW_DF_ALIAS = "frameflow.DataFrame"

PANDAS_DF_GETITEM = "pandas.core.frame.DataFrame.__getitem__"
PANDAS_DF_CTOR = "pandas.core.frame.DataFrame"
PANDAS_DF_ASSIGN = "pandas.core.frame.DataFrame.assign"
PANDAS_DF_DROP = "pandas.core.frame.DataFrame.drop"

# Pandera typing aliases to hook for type annotations (versions vary)
PANDERA_DF_TYPING = "pandera.typing.DataFrame"
PANDERA_DF_TYPING_PANDAS = "pandera.typing.pandas.DataFrame"


def plugin(version: str) -> type[Plugin]:
    return FrameFlowPlugin


class FrameFlowPlugin(Plugin):
    def get_type_analyze_hook(self, fullname: str) -> Callable[[Any], Type] | None:
        # Rewrite Pandera DataFrame annotations to frameflow.typing.DataFrame with seeded columns
        is_pandera_df = fullname in {PANDERA_DF_TYPING, PANDERA_DF_TYPING_PANDAS} or (
            fullname.endswith(".DataFrame") and ("pandera.typing" in fullname)
        )
        if not is_pandera_df:
            return None

        def hook(ctx: Any) -> Type:
            # During type analysis, ctx.type is usually UnboundType
            unbound = getattr(ctx, "type", None)
            if not isinstance(unbound, UnboundType) or not getattr(
                unbound, "args", None
            ):
                return getattr(ctx, "type", AnyType(TypeOfAny.special_form))
            raw_arg = unbound.args[0]
            api = getattr(ctx, "api", None)
            schema_type: Type | None = None
            if api is not None and hasattr(api, "analyze_type"):
                try:
                    schema_type = api.analyze_type(raw_arg)
                except Exception:
                    schema_type = None
            cols: set[str] | None = None
            if schema_type is not None:
                cols = self._extract_cols_from_pandera_schema(schema_type)
                if cols is None:
                    inner = get_proper_type(schema_type)
                    if isinstance(inner, Instance):
                        cols = self._extract_cols_from_typeinfo(inner.type)
            # Build DataFrame[coltype] using the analyzer API
            if cols is None:
                coltype: Type = AnyType(TypeOfAny.special_form)
            else:
                coltype = self._make_coltype(ctx, cols)
            try:
                return cast(Type, ctx.api.named_type(FRAMEFLOW_DF_ALIAS, [coltype]))
            except Exception:
                return cast(Type, ctx.api.named_type(FRAMEFLOW_DF_DEF, [coltype]))

        return hook

    def get_additional_deps(self, file: MypyFile) -> list[tuple[int, str, int]]:
        """Ensure FrameFlow types are available when pandas or pandera are used.

        This lets the plugin resolve `frameflow.typing.DataFrame` (and public alias
        `frameflow.DataFrame`) even if the user didn't import `frameflow` explicitly.
        We scope this to modules that import either `pandas` or `pandera` to avoid
        unnecessary work on unrelated files.
        """
        seen: set[str] = set()
        # Preferred: MypyFile.imports (set of module names imported by the file)
        try:
            for mod in getattr(file, "imports", []) or []:
                if isinstance(mod, str):
                    seen.add(mod.split(".")[0])
        except Exception:
            pass
        # Fallback: scan the AST for Import / ImportFrom nodes
        if not seen:
            try:
                for node in getattr(file, "defs", []) or []:
                    if isinstance(node, Import):
                        # node.ids or node.names depending on mypy version
                        for pair in (
                            getattr(node, "ids", None)
                            or getattr(node, "names", [])
                            or []
                        ):
                            try:
                                mod = pair[0]
                            except Exception:
                                mod = None
                            if isinstance(mod, str):
                                seen.add(mod.split(".")[0])
                    elif isinstance(node, ImportFrom):
                        mod = getattr(node, "id", None) or getattr(node, "module", None)
                        if isinstance(mod, str):
                            seen.add(mod.split(".")[0])
            except Exception:
                pass

        if "pandas" in seen or "pandera" in seen:
            # Priority 10, synthetic line number -1 per mypy convention
            return [(10, "frameflow.typing", -1), (10, "frameflow", -1)]
        return []

    def get_type_hook(self, fullname: str) -> Callable[[Any], Type] | None:
        # Support multiple Pandera versions/paths; match broadly while staying specific
        is_pandera_df = fullname in {PANDERA_DF_TYPING, PANDERA_DF_TYPING_PANDAS} or (
            fullname.endswith(".DataFrame") and ("pandera.typing" in fullname)
        )
        if is_pandera_df:

            # Use a loose annotation for ctx to support older mypy versions without TypeHookContext
            def hook(ctx: Any) -> Type:
                # Map pandera.typing.DataFrame[Schema] -> frameflow.typing.DataFrame[Literal columns]
                inst = get_proper_type(
                    getattr(ctx, "type", AnyType(TypeOfAny.special_form))
                )
                # If not an Instance, fallback without transformation
                if not isinstance(inst, Instance):
                    return getattr(ctx, "type", AnyType(TypeOfAny.special_form))
                schema_arg: Type | None = inst.args[0] if inst.args else None
                cols: set[str] | None = None
                if schema_arg is not None:
                    # Try when the argument is a Type[Schema]
                    cols = self._extract_cols_from_pandera_schema(schema_arg)
                    # Fallback: if the arg is an Instance of the schema class itself
                    if cols is None:
                        inner = get_proper_type(schema_arg)
                        if isinstance(inner, Instance):
                            cols = self._extract_cols_from_typeinfo(inner.type)
                return self._new_df_type(ctx, cols)

            return hook
        return None

    def get_function_hook(
        self, fullname: str
    ) -> Callable[[FunctionContext], Type] | None:
        targets = {
            PANDAS_DF_CTOR,
        }
        if fullname in targets:

            def hook(ctx: FunctionContext, name: str = fullname) -> Type:
                # Seed columns from pandas constructor: pd.DataFrame({...})
                if name == PANDAS_DF_CTOR:
                    data_expr = None
                    # positional first arg
                    if ctx.args and ctx.args[0]:
                        data_expr = ctx.args[0][0]
                    # or data= keyword
                    if data_expr is None and ctx.arg_names and ctx.args:
                        for names, exprs in zip(ctx.arg_names, ctx.args, strict=False):
                            if names and names[0] == "data" and exprs:
                                data_expr = exprs[0]
                                break
                    cols = (
                        self._literal_keys_from_dict_expr(data_expr)
                        if data_expr is not None
                        else None
                    )
                    return self._new_df_type(ctx, cols)

                # no-op default for other functions

                return ctx.default_return_type

            return hook
        return None

    def get_method_hook(self, fullname: str) -> Callable[[MethodContext], Type] | None:
        # Match by suffix to be robust across subclass resolution and stub/module paths
        if (
            fullname.endswith(".__getitem__")
            or fullname.endswith(".assign")
            or fullname.endswith(".drop")
            or fullname.endswith(".rename")
        ):

            def hook(ctx: MethodContext, name: str = fullname) -> Type:
                # df[["a","b"]] narrowing or df["col"] membership
                if name.endswith(".__getitem__"):
                    recv = ctx.type
                    if not self._is_df_like(recv):
                        return ctx.default_return_type
                    cols_before = self._get_cols_from_ff_df(recv)
                    # Try list/tuple literal narrowing via AST
                    if getattr(ctx, "args", None):
                        arg0s = ctx.args[0] if ctx.args else []
                        arg0 = arg0s[0] if arg0s else None
                        if isinstance(arg0, (ListExpr, TupleExpr)):
                            items = getattr(arg0, "items", [])
                            wanted: set[str] = set()
                            for it in items:
                                if isinstance(it, StrExpr):
                                    wanted.add(it.value)
                                else:
                                    wanted = set()
                                    break
                            if wanted:
                                if cols_before is not None:
                                    missing = wanted - cols_before
                                    if missing:
                                        ctx.api.msg.fail(
                                            f"select: unknown column(s): {sorted(missing)!r}",
                                            ctx.context,
                                        )
                                    return self._new_df_type(
                                        ctx, set(wanted) & set(cols_before)
                                    )
                                return self._new_df_type(ctx, None)
                    key_literal: str | None = None
                    if ctx.arg_types and ctx.arg_types[0]:
                        key_type = get_proper_type(ctx.arg_types[0][0])
                        if isinstance(key_type, LiteralType) and isinstance(
                            key_type.value, str
                        ):
                            key_literal = key_type.value
                    # Fallback to AST if mypy didn't preserve Literal type
                    if key_literal is None and getattr(ctx, "args", None):
                        arg_exprs = ctx.args[0] if ctx.args else []
                        if arg_exprs and isinstance(arg_exprs[0], StrExpr):
                            key_literal = arg_exprs[0].value
                    if (
                        key_literal is not None
                        and cols_before is not None
                        and key_literal not in cols_before
                    ):
                        ctx.api.msg.fail(
                            f"column not found: {key_literal!r}", ctx.context
                        )
                    return ctx.default_return_type

                # df.assign(x=..., y=...)  -- add those kwargs as columns
                if name.endswith(".assign"):
                    recv = ctx.type
                    if not self._is_df_like(recv):
                        return ctx.default_return_type
                    cols_before = self._get_cols_from_ff_df(recv)
                    if cols_before is None:
                        return self._new_df_type(ctx, None)
                    newcols = set(cols_before)
                    for names, _types in zip(
                        ctx.arg_names, ctx.arg_types, strict=False
                    ):
                        if names and names[0]:
                            newcols.add(names[0])
                    return self._new_df_type(ctx, newcols)

                # df.drop(columns=[...])  -- best-effort if Literals flow through
                if name.endswith(".drop"):
                    recv = ctx.type
                    if not self._is_df_like(recv):
                        return ctx.default_return_type
                    cols_before = self._get_cols_from_ff_df(recv)
                    drop_cols: set[str] | None = None
                    for names, types in zip(ctx.arg_names, ctx.arg_types, strict=False):
                        if names and names[0] == "columns":
                            drop_cols = self._literal_strs_from_argtypes(types)
                            break
                    # Fallback to AST when mypy doesn't preserve list literal types
                    if drop_cols is None:
                        for names, exprs in zip(
                            ctx.arg_names, getattr(ctx, "args", []), strict=False
                        ):
                            if names and names[0] == "columns" and exprs:
                                ast_cols = self._literal_strs_from_list_or_tuple_expr(
                                    exprs[0]
                                )
                                if ast_cols is not None:
                                    drop_cols = ast_cols
                                break
                    after_drop: set[str] | None = None
                    if cols_before is not None and drop_cols is not None:
                        missing = drop_cols - cols_before
                        if missing:
                            ctx.api.msg.fail(
                                f"drop(columns=...): unknown column(s): {sorted(missing)!r}",
                                ctx.context,
                            )
                        after_drop = set(cols_before) - drop_cols
                    return self._new_df_type(ctx, after_drop)

                # df.rename(columns={"old": "new"})  -- best-effort on dict literal
                if name.endswith(".rename"):
                    recv = ctx.type
                    if not self._is_df_like(recv):
                        return ctx.default_return_type
                    cols_before = self._get_cols_from_ff_df(recv)
                    if cols_before is None:
                        return self._new_df_type(ctx, None)
                    pairs: set[tuple[str, str]] | None = None
                    # Prefer AST (exprs) to capture dict literals
                    for names, exprs in zip(
                        ctx.arg_names, getattr(ctx, "args", []), strict=False
                    ):
                        if names and names[0] == "columns" and exprs:
                            pairs = self._literal_rename_pairs_from_dict_expr(exprs[0])
                            break
                    if pairs is None:
                        return self._new_df_type(ctx, None)
                    newcols = set(cols_before)
                    for old, new in pairs:
                        if old not in cols_before:
                            ctx.api.msg.fail(
                                f"rename: unknown column: {old!r}", ctx.context
                            )
                            return self._new_df_type(ctx, None)
                        newcols.discard(old)
                        newcols.add(new)
                    return self._new_df_type(ctx, newcols)

                return ctx.default_return_type

            return hook
        return None

        # ===== core helpers =====

    def _is_ff_df(self, typ: Type) -> bool:
        typ = get_proper_type(typ)
        return isinstance(typ, Instance) and (
            typ.type.fullname == FRAMEFLOW_DF_DEF
            or typ.type.fullname == FRAMEFLOW_DF_ALIAS
        )

    def _is_df_like(self, typ: Type) -> bool:
        typ = get_proper_type(typ)
        return isinstance(typ, Instance) and (
            typ.type.fullname == FRAMEFLOW_DF_DEF
            or typ.type.fullname == FRAMEFLOW_DF_ALIAS
            or typ.type.fullname == "pandas.core.frame.DataFrame"
        )

    def _colset_from_typearg(self, typ: Type) -> set[str] | None:
        typ = get_proper_type(typ)
        if isinstance(typ, AnyType):
            return None
        if isinstance(typ, LiteralType) and isinstance(typ.value, str):
            return {typ.value}
        if isinstance(typ, UnionType):
            out: set[str] = set()
            for item in typ.items:
                got = self._colset_from_typearg(item)
                if got is None:
                    return None
                out |= got
            return out
        return None

    def _make_coltype(self, ctx: Any, cols: set[str]) -> Type:
        if not cols:
            return AnyType(TypeOfAny.special_form)
        str_fb = ctx.api.named_type("builtins.str")
        lits = [LiteralType(value=c, fallback=str_fb) for c in sorted(cols)]
        if len(lits) == 1:
            return lits[0]
        return UnionType.make_union(lits)

    def _new_df_type(self, ctx: Any, cols: set[str] | None) -> Type:
        if cols is None:
            coltype: Type = AnyType(TypeOfAny.special_form)
        else:
            coltype = self._make_coltype(ctx, cols)
        # Prefer the public alias if available; otherwise the internal typing path
        try:
            return ctx.api.named_generic_type(FRAMEFLOW_DF_ALIAS, [coltype])  # type: ignore[no-any-return]
        except Exception:
            return ctx.api.named_generic_type(FRAMEFLOW_DF_DEF, [coltype])  # type: ignore[no-any-return]

    def _get_cols_from_ff_df(self, typ: Type) -> set[str] | None:
        typ = get_proper_type(typ)
        if not isinstance(typ, Instance):
            return None
        if (
            typ.type.fullname not in {FRAMEFLOW_DF_DEF, FRAMEFLOW_DF_ALIAS}
            or not typ.args
        ):
            return None
        return self._colset_from_typearg(typ.args[0])

    def _literal_strs_from_argtypes(self, types: list[Type]) -> set[str] | None:
        out: set[str] = set()
        for t in types:
            t = get_proper_type(t)
            if isinstance(t, LiteralType) and isinstance(t.value, str):
                out.add(t.value)
            elif isinstance(t, UnionType):
                got = self._colset_from_typearg(t)
                if got is None:
                    return None
                out |= got
            else:
                return None
        return out

    def _literal_strs_from_argexprs(self, exprs: list[Any]) -> set[str] | None:
        out: set[str] = set()
        for e in exprs:
            if isinstance(e, StrExpr):
                out.add(e.value)
            else:
                return None
        return out

    def _literal_strs_from_list_or_tuple_expr(self, expr: Any) -> set[str] | None:
        if isinstance(expr, (ListExpr, TupleExpr)):
            out: set[str] = set()
            for it in getattr(expr, "items", []):
                if isinstance(it, StrExpr):
                    out.add(it.value)
                else:
                    return None
            return out
        return None

    def _literal_keys_from_dict_expr(self, expr: Any) -> set[str] | None:
        if isinstance(expr, DictExpr):
            out: set[str] = set()
            pairs = getattr(expr, "items", None)
            if not pairs:
                return None
            for pair in pairs:
                try:
                    k = pair[0]
                except Exception:
                    return None
                if isinstance(k, StrExpr):
                    out.add(k.value)
                else:
                    return None
            return out
        return None

    def _literal_rename_pairs_from_dict_expr(
        self, expr: Any
    ) -> set[tuple[str, str]] | None:
        if isinstance(expr, DictExpr):
            out: set[tuple[str, str]] = set()
            pairs = getattr(expr, "items", None)
            if not pairs:
                return None
            for pair in pairs:
                try:
                    k, v = pair[0], pair[1]
                except Exception:
                    return None
                if isinstance(k, StrExpr) and isinstance(v, StrExpr):
                    out.add((k.value, v.value))
                else:
                    return None
            return out
        return None

    # ===== function and method hook implementations are returned via closures above =====

    # ===== Pandera schema introspection =====
    def _extract_cols_from_pandera_schema(self, schema_type: Type) -> set[str] | None:
        schema_type = get_proper_type(schema_type)
        if isinstance(schema_type, TypeType):
            inner = get_proper_type(schema_type.item)
            if isinstance(inner, Instance):
                info: TypeInfo = inner.type
                return self._extract_cols_from_typeinfo(info)
        return None

    def _extract_cols_from_typeinfo(self, info: TypeInfo) -> set[str] | None:
        names: list[str] = []
        for n, sym in info.names.items():
            if n.startswith("_") or n in (
                "Config",
                "Index",
                "Column",
                "Columns",
            ):
                continue
            node = getattr(sym, "node", None)
            # Prefer fields that are variables with annotations on the model
            if isinstance(node, Var):
                names.append(n)
                continue
            # Fallback: include attributes annotated as Series[...] in the Pandera model
            if node is not None and hasattr(node, "type") and node.type is not None:
                t = get_proper_type(node.type)
                if isinstance(t, Instance) and "Series" in t.type.name:
                    names.append(n)
        return set(names) if names else None
