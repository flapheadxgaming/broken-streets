# apps/calculator.py
# Calculator mini-app for the Mobile OS.
# A fully functional four-function calculator with a clean Kivy UI.
# Layout: a top display label + a 4×5 button grid.

import ast
import operator as _op

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.graphics import Color, Rectangle

# Allowed AST node types and operators for the safe evaluator
_ALLOWED_OPS = {
    ast.Add: _op.add,
    ast.Sub: _op.sub,
    ast.Mult: _op.mul,
    ast.Div: _op.truediv,
    ast.USub: _op.neg,
    ast.UAdd: _op.pos,
}


def _safe_eval(expression: str) -> float:
    """
    Evaluate a simple arithmetic expression without using ``eval()``.

    Only supports: integer/float literals, +, -, *, /
    Raises ``ValueError`` for unsupported constructs.
    """
    def _eval(node):
        if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
            return node.value
        if isinstance(node, ast.BinOp) and type(node.op) in _ALLOWED_OPS:
            return _ALLOWED_OPS[type(node.op)](_eval(node.left), _eval(node.right))
        if isinstance(node, ast.UnaryOp) and type(node.op) in _ALLOWED_OPS:
            return _ALLOWED_OPS[type(node.op)](_eval(node.operand))
        raise ValueError(f"Unsupported expression node: {type(node).__name__}")

    tree = ast.parse(expression, mode="eval")
    return _eval(tree.body)

# Button layout rows (display string, action string)
_BUTTON_ROWS = [
    ["C", "±", "%", "÷"],
    ["7", "8", "9", "×"],
    ["4", "5", "6", "−"],
    ["1", "2", "3", "+"],
    ["0", ".", "⌫", "="],
]

# Map display symbols to Python operators
_OP_MAP = {"÷": "/", "×": "*", "−": "-", "+": "+"}


class CalculatorApp(BoxLayout):
    """
    Four-function calculator mini-app.

    Supports: digit entry, +, −, ×, ÷, % (of current value),
    sign toggle (±), backspace (⌫), clear (C) and equals (=).
    """

    def __init__(self, theme=None, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "vertical"
        self._theme   = theme
        # Calculator state
        self._expression = ""   # the expression being built
        self._result     = ""   # last computed result
        self._just_evaluated = False

        self._build()

    # ------------------------------------------------------------------
    # Construction
    # ------------------------------------------------------------------

    def _build(self):
        # Display area
        self._display = Label(
            text="0",
            font_size="36sp",
            halign="right",
            valign="middle",
            size_hint=(1, 0.25),
            padding=[16, 0],
        )
        self._display.bind(size=self._display.setter("text_size"))
        self.add_widget(self._display)

        # Button grid
        grid = GridLayout(cols=4, spacing=2, padding=2, size_hint=(1, 0.75))
        for row in _BUTTON_ROWS:
            for symbol in row:
                btn = Button(
                    text=symbol,
                    font_size="22sp",
                    on_release=lambda inst, s=symbol: self._on_button(s),
                )
                # Style operator and equals buttons differently
                if symbol in _OP_MAP or symbol == "=":
                    btn.background_color = (1, 0.6, 0, 1)
                elif symbol in ("C", "±", "%"):
                    btn.background_color = (0.6, 0.6, 0.6, 1)
                grid.add_widget(btn)
        self.add_widget(grid)

    # ------------------------------------------------------------------
    # Input handling
    # ------------------------------------------------------------------

    def _on_button(self, symbol: str) -> None:
        if symbol == "C":
            self._clear()
        elif symbol == "±":
            self._toggle_sign()
        elif symbol == "%":
            self._percent()
        elif symbol == "⌫":
            self._backspace()
        elif symbol == "=":
            self._evaluate()
        elif symbol in _OP_MAP:
            self._append_operator(_OP_MAP[symbol])
        else:
            self._append_digit(symbol)
        self._refresh_display()

    def _clear(self):
        self._expression = ""
        self._just_evaluated = False

    def _toggle_sign(self):
        # Negate the last number token in the expression
        try:
            val = float(self._expression or "0")
            self._expression = str(-val)
        except ValueError:
            pass

    def _percent(self):
        try:
            val = float(self._expression or "0")
            self._expression = str(val / 100)
        except ValueError:
            pass

    def _backspace(self):
        self._expression = self._expression[:-1]
        self._just_evaluated = False

    def _append_digit(self, digit: str):
        if self._just_evaluated:
            self._expression = ""
            self._just_evaluated = False
        self._expression += digit

    def _append_operator(self, op: str):
        self._just_evaluated = False
        # Replace a trailing operator instead of stacking
        if self._expression and self._expression[-1] in "+-*/":
            self._expression = self._expression[:-1]
        self._expression += op

    def _evaluate(self):
        try:
            # Use a restricted safe evaluator instead of eval()
            result = _safe_eval(self._expression)
            self._expression = str(result)
            self._just_evaluated = True
        except Exception:
            self._expression = "Error"
            self._just_evaluated = True

    def _refresh_display(self):
        self._display.text = self._expression or "0"
