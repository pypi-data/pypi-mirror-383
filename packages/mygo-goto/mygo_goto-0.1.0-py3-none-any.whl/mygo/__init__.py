__version__ = "0.1.0"

# goto_ast.py
# -*- coding: utf-8 -*-
"""
在同一函数（同一 code object）内提供简易的 label/goto 能力：
- label("NAME") 记录一个可跳转的“标签行”
- goto("NAME") 通过一次性 sys.settrace，把下一次 line 事件跳到标签行

限制与 pdb j 相同：
* 只能在同一函数内跳转，不能跨函数/跨栈
* 不能跨越 with/try/except/finally/yield/await 等结构性边界
* 目标行必须有真实字节码（本实现把 label 行改成常量表达式，确保可落点）

用法示例：
    from goto_ast import enable_goto, label, goto

    @enable_goto
    def demo():
        print("A")
        label("L")
        print("B-before")
        goto("L")
        print("C-after")

    demo()
"""

import ast
import functools
import inspect
import sys
import textwrap
import types
from typing import Callable, Dict


def label(name: str) -> None:
    """占位：标记一个跳转标签。装饰后会被改写成常量表达式以生成可落点字节码。"""
    return None


def goto(name: str) -> None:
    """占位：跳转到某个标签。装饰后会被改写成 _goto_line(<int>)。"""
    return None


def _goto_line(line: int) -> None:
    """
    在当前帧把"下一次 line 事件"跳到指定行，然后卸载 tracer（一次性）。
    关键点：必须给当前帧设置 f_trace，否则这帧不会触发 line 事件。
    
    注意：goto 后面必须有至少一行代码来触发 line 事件，
    AST 改写时会自动在每个 goto 后插入 Pass 语句来保证这一点。
    """
    target = int(line)
    caller = sys._getframe(1)  # 调用 _goto_line 的帧（即被装饰函数的当前帧）

    def tracer(frame, event, arg):
        # 只处理【同一帧】的下一次 'line' 事件
        if frame is caller and event == "line":
            try:
                frame.f_lineno = target
            finally:
                # 卸载追踪（一次性）
                frame.f_trace = None
                sys.settrace(None)
            return None
        return tracer

    # 关键：让"当前已经在执行的帧"也进入追踪
    caller.f_trace = tracer      # ← 没有这句，当前帧不会触发 line 事件
    sys.settrace(tracer)         # 为新产生的事件安装全局追踪（本线程）


def enable_goto(func: Callable) -> Callable:
    """装饰一个函数，重写其 AST：收集 label，改写 goto。"""
    # 1) 拿函数源码并去掉缩进
    try:
        src = inspect.getsource(func)
    except OSError as e:
        raise RuntimeError("enable_goto 需要能拿到函数的源代码（请保证在 .py 文件中定义）。") from e
    src = textwrap.dedent(src)

    # 2) 解析 AST，仅保留该函数定义，移除装饰器
    mod = ast.parse(src, filename=inspect.getsourcefile(func) or "<string>")
    fdef = None
    for n in mod.body:
        if isinstance(n, ast.FunctionDef) and n.name == func.__name__:
            fdef = n
            break
    if fdef is None:
        raise RuntimeError("function def not found in source")
    fdef.decorator_list = []   # 去掉 @enable_goto
    mod.body = [fdef]          # 只编译这个函数本体

    # 3) 第一遍：收集 label 行号，并把 label(...) 替为“可执行的常量表达式”
    labels: Dict[str, int] = {}

    class LabelCollector(ast.NodeTransformer):
        def visit_Expr(self, node: ast.Expr):
            call = node.value
            if (
                isinstance(call, ast.Call)
                and isinstance(call.func, ast.Name)
                and call.func.id == "label"
                and len(call.args) == 1
                and isinstance(call.args[0], ast.Constant)
                and isinstance(call.args[0].value, str)
            ):
                name = call.args[0].value
                labels[name] = node.lineno  # 源代码行号
                # 用常量表达式生成真实字节码行（不要用 Pass）
                repl = ast.Expr(value=ast.Constant(value=f"__LABEL__:{name}"))
                return ast.copy_location(repl, node)
            return self.generic_visit(node)

    LabelCollector().visit(fdef)

    # 4) 第二遍：把 goto("X") 改写为 _goto_line(<X的行号>)，并在每个 goto 后插入 Pass
    class GotoRewriter(ast.NodeTransformer):
        def _is_goto_expr(self, node):
            """检查节点是否是改写后的 _goto_line 调用"""
            return (
                isinstance(node, ast.Expr)
                and isinstance(node.value, ast.Call)
                and isinstance(node.value.func, ast.Name)
                and node.value.func.id == "_goto_line"
            )
        
        def _insert_pass_after_goto(self, body):
            """处理语句列表，在每个 goto 后插入 Pass"""
            if not body:
                return body
            
            new_body = []
            for stmt in body:
                # 先递归处理语句本身（这会改写内部的 goto）
                visited_stmt = self.visit(stmt)
                new_body.append(visited_stmt)
                
                # 如果这是一个 _goto_line 调用，在后面插入 Pass
                if self._is_goto_expr(visited_stmt):
                    new_body.append(ast.Pass())
            
            return new_body
        
        def visit_FunctionDef(self, node):
            node.body = self._insert_pass_after_goto(node.body)
            return node
        
        def visit_If(self, node):
            node.body = self._insert_pass_after_goto(node.body)
            node.orelse = self._insert_pass_after_goto(node.orelse)
            return node
        
        def visit_For(self, node):
            node.body = self._insert_pass_after_goto(node.body)
            node.orelse = self._insert_pass_after_goto(node.orelse)
            return node
        
        def visit_While(self, node):
            node.body = self._insert_pass_after_goto(node.body)
            node.orelse = self._insert_pass_after_goto(node.orelse)
            return node
        
        def visit_With(self, node):
            node.body = self._insert_pass_after_goto(node.body)
            return node
        
        def visit_Try(self, node):
            node.body = self._insert_pass_after_goto(node.body)
            node.orelse = self._insert_pass_after_goto(node.orelse)
            node.finalbody = self._insert_pass_after_goto(node.finalbody)
            for handler in node.handlers:
                handler.body = self._insert_pass_after_goto(handler.body)
            return node
        
        def visit_Match(self, node):
            for case in node.cases:
                case.body = self._insert_pass_after_goto(case.body)
            return node
        
        def visit_Expr(self, node: ast.Expr):
            """改写 goto 调用为 _goto_line 调用"""
            call = node.value
            if (
                isinstance(call, ast.Call)
                and isinstance(call.func, ast.Name)
                and call.func.id == "goto"
                and len(call.args) == 1
                and isinstance(call.args[0], ast.Constant)
                and isinstance(call.args[0].value, str)
            ):
                name = call.args[0].value
                if name not in labels:
                    raise SyntaxError(f"goto to unknown label '{name}'")
                target = labels[name]
                new = ast.Expr(
                    value=ast.Call(
                        func=ast.Name(id="_goto_line", ctx=ast.Load()),
                        args=[ast.Constant(value=target)],
                        keywords=[],
                    )
                )
                return ast.copy_location(new, node)
            return self.generic_visit(node)

    GotoRewriter().visit(fdef)
    ast.fix_missing_locations(mod)

    # 5) 编译并 exec 到【原函数的】globals；把运行期依赖放进去
    code = compile(mod, filename="<enable_goto>", mode="exec")

    g = func.__globals__  # 使用原始全局命名空间，保证运行期能找到依赖
    g.setdefault("label", label)
    g.setdefault("goto", goto)
    g["_goto_line"] = _goto_line

    exec(code, g, g)
    new_impl = g[func.__name__]

    # 6) 用原来的 globals/closure 构造可调用对象，并保留元信息
    wrapped = types.FunctionType(
        new_impl.__code__,
        func.__globals__,
        func.__name__,
        func.__defaults__,
        func.__closure__,
    )
    functools.update_wrapper(wrapped, func)
    wrapped.__dict__.update(func.__dict__)
    return wrapped
