# Block diagrams and other protocol helpers.

import re
from dataclasses import dataclass
from types import SimpleNamespace
from typing import Any, Callable, Literal, NamedTuple

from hexdoc.minecraft import I18n
from jinja2 import pass_context
from jinja2.runtime import Context
from markupsafe import Markup

from .lang import ArglessI18n, I18nTuple, plural_factory

BOOK = "mediatransport.book"
SYMBOLS = f"{BOOK}.symbols"
TOOLTIPS = f"{BOOK}.tooltips"
PLURAL = f"{BOOK}.pluralizations"
plural = plural_factory(PLURAL)


@pass_context
def plural_var(context: Context, key: str, amount: str) -> str:
    i18n = I18n.of(context)
    rkey = f"{PLURAL}.{key}"
    return I18nTuple.ofa(i18n.localize(rkey), (amount,)).resolve()


@dataclass
class ProtoSymbol:
    name: str
    size: str | int | None = None

    def render_name(self, ctx: Context) -> ArglessI18n:
        i18n = I18n.of(ctx)
        return I18nTuple.of(i18n.localize(f"{SYMBOLS}.{self.name}"))

    def render_tooltip(self, ctx: Context) -> I18nTuple[Any]:
        i18n = I18n.of(ctx)
        stack: list[I18nTuple[Any]] = [I18nTuple.untranslated(self.name)]

        if self.size is not None:
            contents: I18nTuple[Any]
            if isinstance(self.size, str):
                contents = I18nTuple.ofa(
                    i18n.localize(f"{TOOLTIPS}.size_ref"),
                    (I18nTuple.of(i18n.localize(f"{SYMBOLS}.{self.size}")),),
                )
            else:  # int
                contents = plural(ctx, "byte", self.size)

            stack.append(I18nTuple.ofa(i18n.localize(f"{TOOLTIPS}.size"), (contents,)))

        return I18nTuple.join("\n", stack)


symbols = {
    "type": ProtoSymbol(name="type", size=1),
    "data": ProtoSymbol(name="data", size=None),
    "double_value": ProtoSymbol(name="value", size=8),
    "dir": ProtoSymbol(name="dir", size=1),
    "pattern_len": ProtoSymbol(name="length", size=4),
    "angles": ProtoSymbol(name="angles", size="length"),
    "vec_x": ProtoSymbol(name="x", size=8),
    "vec_y": ProtoSymbol(name="y", size=8),
    "vec_z": ProtoSymbol(name="z", size=8),
    "list_len": ProtoSymbol(name="length", size=4),
    "list_iotas": ProtoSymbol(name="iotas", size=None),
    "str_len": ProtoSymbol(name="length", size=4),
    "string": ProtoSymbol(name="string", size="length"),
    "rows": ProtoSymbol(name="rows", size=1),
    "cols": ProtoSymbol(name="cols", size=1),
    "matrix_contents": ProtoSymbol(name="contents", size="rowscols"),
    "rowscols": ProtoSymbol(name="rowscols", size=None),  # combination key, not actual
    "protocol_version": ProtoSymbol(name="version", size=2),
    "max_send": ProtoSymbol(name="max_send", size=4),
    "max_inter_send": ProtoSymbol(name="max_inter_send", size=4),
    "max_recv": ProtoSymbol(name="max_recv", size=4),
    "max_power": ProtoSymbol(name="max_power", size=8),
    "power_regen_rate": ProtoSymbol(name="power_regen_rate", size=8),
    "inter_cost": ProtoSymbol(name="inter_cost", size=8),
    # Figura things that aren't actual protocol stuff but are useful to link
    "Buffer": ProtoSymbol(name="Buffer", size=None),
}


@pass_context
def sym_name(ctx: Context, word: str) -> str:
    symbol = symbols[word]
    return symbol.render_name(ctx).resolve()


@pass_context
def symdef(ctx: Context, word: str) -> str:
    symbol = symbols[word]
    return (
        f'<span class="protocol-sym-def" id="mediatransport-protocol-{word}"'
        f' title="{symbol.render_tooltip(ctx).resolve_html_oneline()}">'
        f"{symbol.render_name(ctx).resolve()}"
        "</span>"
    )


@pass_context
def symr(ctx: Context, word: str) -> str:
    symbol = symbols[word]
    return (
        f'<span class="protocol-sym-raw"'
        f' title="{symbol.render_tooltip(ctx).resolve_html_oneline()}">'
        f"{symbol.render_name(ctx).resolve()}"
        "</span>"
    )


@pass_context
def sym(ctx: Context, word: str) -> str:
    symbol = symbols[word]
    return (
        f'<a class="protocol-sym" href="#mediatransport-protocol-{word}"'
        f' title="{symbol.render_tooltip(ctx).resolve_html_oneline()}">'
        f"{symbol.render_name(ctx).resolve()}"
        "</a>"
    )


tags = {"symdef": symdef, "sym": sym, "symr": symr}

matching_pattern = re.compile(r"{(sym(?:|def|r)):(\w+)}")


def _make_matcher(context: Context):
    def _handle_match(match: re.Match[str]) -> str:
        tag, value = match.groups()
        return tags[tag](context, value)

    return _handle_match


def process_markup(context: Context, raw: str) -> Markup:
    return Markup(matching_pattern.sub(_make_matcher(context), raw))


class Block(NamedTuple):
    size: int | tuple[str, str] | None
    kind: Literal["literal", "sym"]
    sym: str


@pass_context
def dia(context: Context, blocks: list[Block]) -> Markup:
    block_template = context.environment.get_template("block_diagram.html.jinja")
    new_ctx = context.get_all().copy()
    new_ctx["blocks"] = blocks
    return Markup(block_template.render(new_ctx))


class _Box(SimpleNamespace):
    # you can setattr on it.
    tl: Callable[[Context, str], Markup]
    dia: Callable[[Context, list[Block]], Markup]
    sym: Callable[[Context, str], str]
    sym_name: Callable[[Context, str], str]
    codeblock: Callable[[Context, str], Markup]
    plural: Callable[[Context, str, int], I18nTuple[int]]
    plural_var: Callable[[Context, str, str], str]


def context(section: str):
    base = f"{BOOK}.{section}"

    @pass_context
    def tl(context: Context, key: str) -> Markup:
        i18n = I18n.of(context)
        translated = i18n.localize(f"{base}.{key}").value
        return process_markup(context, translated)

    @pass_context
    def codeblock(context: Context, key: str) -> Markup:
        i18n = I18n.of(context)
        raw = i18n.localize(f"{base}.{key}").value
        raw = re.sub(r"^\.", "", raw, flags=re.MULTILINE)
        return Markup(f"<pre>\n{raw}\n</pre>")

    Box = _Box()
    Box.tl = tl
    Box.dia = dia
    Box.sym = sym
    Box.sym_name = sym_name

    Box.codeblock = codeblock

    Box.plural = plural
    Box.plural_var = plural_var

    return Box
