from antlr4 import ParseTreeVisitor
from stgem.monitor.pystl.robustness import *  # noqa: F401,F403 # pylint: disable=unused-wildcard-import

if __name__ is not None and "." in __name__:
    from .stlParser import stlParser
else:
    from stlParser import stlParser


# This class defines a complete generic visitor for a parse tree produced by stlParser.

class stlParserVisitor(ParseTreeVisitor):

    # Visit a parse tree produced by stlParser#stlformula.
    def visitStlformula(self, ctx: stlParser.StlformulaContext):
        return self.visit(ctx.getRuleContext().getChild(0))

    # Visit a parse tree produced by stlParser#predicateExpr.
    def visitPredicateExpr(self, ctx: stlParser.PredicateExprContext):
        phi1 = self.visit(ctx.getRuleContext().getChild(0))
        operator = ctx.getRuleContext().getChild(1).getText()
        phi2 = self.visit(ctx.getRuleContext().getChild(2))
        if operator == "<=":
            return LessThan(phi1, phi2)  # noqa: F405
        if operator == ">=":
            return GreaterThan(phi1, phi2)  # noqa: F405
        if operator == "<":
            return StrictlyLessThan(phi1, phi2)  # noqa: F405
        if operator == ">":
            return StrictlyGreaterThan(phi1, phi2)  # noqa: F405
        if operator == "==":
            return Equals(phi1, phi2)  # noqa: F405
        # !=
        return Not(Equals(phi1, phi2))  # noqa: F405

    # Visit a parse tree produced by stlParser#signalExpr.
    def visitSignalExpr(self, ctx: stlParser.SignalExprContext):
        return self.visit(ctx.getRuleContext().getChild(0))

    # Visit a parse tree produced by stlParser#opFutureExpr.
    def visitOpFutureExpr(self, ctx: stlParser.OpFutureExprContext):
        if ctx.getRuleContext().getChildCount() == 2:
            raise NotImplementedError("Eventually not supported without specifying an interval.")
        if ctx.getRuleContext().getChildCount() == 3:
            phi = self.visit(ctx.getRuleContext().getChild(2))
            interval = self.visit(ctx.getRuleContext().getChild(1))
            return Finally(interval[0], interval[1], phi)  # noqa: F405
        
        raise ValueError(f"Unexpected child count: {ctx.getRuleContext().getChildCount()}")

    # Visit a parse tree produced by stlParser#parenPhiExpr.
    def visitParenPhiExpr(self, ctx: stlParser.ParenPhiExprContext):
        child = self.visit(ctx.getRuleContext().getChild(1))
        # We keep track of parenthesized expressions in order to work with
        # potential And nonassociativity.
        child.parenthesized = True
        return child

    # Visit a parse tree produced by stlParser#opUntilExpr.
    def visitOpUntilExpr(self, ctx: stlParser.OpUntilExprContext):
        phi1 = self.visit(ctx.getRuleContext().getChild(0))
        if ctx.getRuleContext().getChildCount() == 3:
            raise NotImplementedError("Until not supported without specifying an interval.")
        if ctx.getRuleContext().getChildCount() == 4:  # Optional interval
            phi2 = self.visit(ctx.getRuleContext().getChild(3))
            interval = self.visit(ctx.getRuleContext().getChild(2))
            return Until(interval[0], interval[1], phi1, phi2)  # noqa: F405
        
        raise ValueError(f"Unexpected child count: {ctx.getRuleContext().getChildCount()}")

    # Visit a parse tree produced by stlParser#opGloballyExpr.
    def visitOpGloballyExpr(self, ctx: stlParser.OpGloballyExprContext):
        if ctx.getRuleContext().getChildCount() == 2:
            raise NotImplementedError("Global not supported without specifying an interval.")
        if ctx.getRuleContext().getChildCount() == 3:
            phi = self.visit(ctx.getRuleContext().getChild(2))
            interval = self.visit(ctx.getRuleContext().getChild(1))
            return Global(interval[0], interval[1], phi)  # noqa: F405
        
        raise ValueError(f"Unexpected child count: {ctx.getRuleContext().getChildCount()}")

    # Visit a parse tree produced by stlParser#opAndExpr.
    def visitOpAndExpr(self, ctx: stlParser.OpAndExprContext):
        """
        We need to be a bit clever here as antlr does not seem to support what
        we want (maybe it does, but I could not figure it out). Consider two
        formulas X = 'A and B and C' and Y = 'A and (B and C)'. Since And is
        possibly nonassociative (for the alternative robustness functions),
        these are not the same formula to us. We want to return And(A, B, C)
        for X and And(A, And(B, C)) for Y. In order to accomplish this, we keep
        track which parts of the formula are in parentheses (see
        visitParenPhiExpr).

        And yes, you could think that 'A and B and C' would visit this method
        with getChildCount() = 5, but it does not. Hence the workarounds.
        """

        phi1 = self.visit(ctx.getRuleContext().getChild(0))
        phi2 = self.visit(ctx.getRuleContext().getChild(2))
        formulas = []
        if isinstance(phi1, And) and not hasattr(phi1, "parenthesized"):  # noqa: F405
            formulas += phi1.formulas
        else:
            formulas.append(phi1)
        if isinstance(phi2, And) and not hasattr(phi2, "parenthesized"):  # noqa: F405
            formulas += phi2.formulas
        else:
            formulas.append(phi2)

        return And(*formulas)  # noqa: F405

    # Visit a parse tree produced by stlParser#opNextExpr.
    def visitOpNextExpr(self, ctx: stlParser.OpNextExprContext):
        return Next(self.visit(ctx.getRuleContext().getChild(1)))  # noqa: F405

    # Visit a parse tree produced by stlParser#opPropExpr.
    def visitOpPropExpr(self, ctx: stlParser.OpPropExprContext):
        phi1 = self.visit(ctx.getRuleContext().getChild(0))
        operator = ctx.getRuleContext().getChild(1).getText()
        phi2 = self.visit(ctx.getRuleContext().getChild(2))
        if operator in ["implies", "->"]:
            return Implication(phi1, phi2)  # noqa: F405
        if operator in ["iff", "<->"]:
            raise NotImplementedError("Equivalence not implemented.")
        raise ValueError(f"Unsupported operator: {operator}")

    # Visit a parse tree produced by stlParser#opOrExpr.
    def visitOpOrExpr(self, ctx: stlParser.OpOrExprContext):
        # See visitOpAndExpr for explanation.
        phi1 = self.visit(ctx.getRuleContext().getChild(0))
        phi2 = self.visit(ctx.getRuleContext().getChild(2))
        formulas = []
        if isinstance(phi1, Or) and not hasattr(phi1, "parenthesized"):  # noqa: F405
            formulas += phi1.formulas
        else:
            formulas.append(phi1)
        if isinstance(phi2, Or) and not hasattr(phi2, "parenthesized"):  # noqa: F405
            formulas += phi2.formulas
        else:
            formulas.append(phi2)

        return Or(*formulas)  # noqa: F405

    # Visit a parse tree produced by stlParser#opNegExpr.
    def visitOpNegExpr(self, ctx: stlParser.OpNegExprContext):
        phi = self.visit(ctx.getRuleContext().getChild(1))
        return Not(phi)  # noqa: F405

    # Visit a parse tree produced by stlParser#signalParenthesisExpr.
    def visitSignalParenthesisExpr(self, ctx: stlParser.SignalParenthesisExprContext):
        return self.visit(ctx.getRuleContext().getChild(1))

    # Visit a parse tree produced by stlParser#signalName.
    def visitSignalName(self, ctx: stlParser.SignalNameContext):
        name = ctx.getText()
        return Signal(name)  # noqa: F405

    # Visit a parse tree produced by stlParser#signalAbsExpr.
    def visitSignalAbsExpr(self, ctx: stlParser.SignalAbsExprContext):
        return Abs(self.visit(ctx.getRuleContext().getChild(1)))  # noqa: F405

    # Visit a parse tree produced by stlParser#signalSumExpr.
    def visitSignalSumExpr(self, ctx: stlParser.SignalSumExprContext):
        signal1 = self.visit(ctx.getRuleContext().getChild(0))
        operator = ctx.getRuleContext().getChild(1).getText()
        signal2 = self.visit(ctx.getRuleContext().getChild(2))
        if operator == "+":
            return Sum(signal1, signal2)  # noqa: F405
        if operator == "-":
            return Subtract(signal1, signal2)  # noqa: F405
        raise ValueError(f"Unsupported operator: {operator}")

    # Visit a parse tree produced by stlParser#signalNumber.
    def visitSignalNumber(self, ctx: stlParser.SignalNumberContext):
        value = float(ctx.getText())
        return Constant(value)  # noqa: F405

    # Visit a parse tree produced by stlParser#signalMultExpr.
    def visitSignalMultExpr(self, ctx: stlParser.SignalMultExprContext):
        signal1 = self.visit(ctx.getRuleContext().getChild(0))
        operator = ctx.getRuleContext().getChild(1).getText()
        signal2 = self.visit(ctx.getRuleContext().getChild(2))
        if operator == "*":
            return Multiply(signal1, signal2)  # noqa: F405
        if operator == "/":
            return Divide(signal1, signal2)  # noqa: F405
        raise ValueError(f"Unsupported operator: {operator}")

    # Visit a parse tree produced by stlParser#interval.
    def visitInterval(self, ctx: stlParser.IntervalContext):
        A = float(ctx.getRuleContext().getChild(1).getText())
        B = float(ctx.getRuleContext().getChild(3).getText())
        return [A, B]


del stlParser
