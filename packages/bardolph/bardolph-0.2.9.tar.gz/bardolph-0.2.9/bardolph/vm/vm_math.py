import operator
from numbers import Number

from bardolph.vm.eval_stack import EvalStack
from bardolph.vm.vm_codes import LoopVar, Operand, Operator, Register


class VmMath:
    _fn_table = {
        Operator.ADD: operator.add,
        Operator.DIV: operator.truediv,
        Operator.EQ: operator.__eq__,
        Operator.GT: operator.gt,
        Operator.GTE: operator.ge,
        Operator.LT: operator.lt,
        Operator.LTE: operator.le,
        Operator.NOTEQ: operator.ne,
        Operator.MOD: operator.mod,
        Operator.MUL: operator.mul,
        Operator.POW: operator.pow,
        Operator.SUB: operator.sub
    }

    def __init__(self, call_stack, reg):
        self._call_stack = call_stack
        self._reg = reg
        self._eval_stack = EvalStack()

    def reset(self) -> None:
        self._eval_stack.clear()

    def push(self, srce) -> None:
        value = None
        if (isinstance(srce, Number) or
                srce in (Register.UNIT_MODE, Operand.NULL)):
            value = srce
        elif isinstance(srce, Register):
            value = self._reg.get_by_enum(srce)
        elif isinstance(srce, (str, LoopVar)):
             value = self._call_stack.get_variable(srce)

        assert value is not None, "pushing None onto eval stack"
        self._eval_stack.push(value)

    def pushq(self, srce) -> None:
        self._eval_stack.push(srce)

    def pop(self, dest) -> None:
        value = self._eval_stack.pop()
        if dest is None:
            return
        if isinstance(dest, Register):
            self._reg.set_by_enum(dest, value)
        elif isinstance(dest, (str, LoopVar)):
            self._call_stack.put_variable(dest, value)

    def op(self, operator) -> None:
        if operator in (Operator.UADD, Operator.USUB, Operator.NOT):
            self.unary_op(operator)
        elif operator in (Operator.AND, Operator.OR):
            self.logical_op(operator)
        else:
            self.bin_op(operator)

    def unary_op(self, operator) -> None:
        if operator is Operator.USUB:
            self._eval_stack.replace_top(-self._eval_stack.top)
        elif operator is Operator.NOT:
            self._eval_stack.replace_top(not self._eval_stack.top)

    def bin_op(self, operator) -> None:
        op2 = self._eval_stack.pop()
        op1 = self._eval_stack.pop()
        self._eval_stack.push(VmMath._fn_table[operator](op1, op2))

    def logical_op(self, operator) -> None:
        op2 = bool(self._eval_stack.pop())
        op1 = bool(self._eval_stack.pop())
        result = op1 and op2 if operator == Operator.AND else op1 or op2
        self._eval_stack.push(result)
