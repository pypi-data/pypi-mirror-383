import os
import ast
import inspect
import textwrap

from types import FunctionType


class Helper:
    
    @staticmethod
    def is_ast_function_empty(func_node):
        if not func_node.body:
            return True
        body = func_node.body
        if len(body) == 1:
            stmt = body[0]
            if isinstance(stmt, ast.Pass):
                return True
            if isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Constant):
                if stmt.value.value in (None, Ellipsis) or isinstance(stmt.value.value, str):
                    return True
        return False
    
    
    @staticmethod
    def find_func_node_from_file(func):
        try:
            source_file = inspect.getsourcefile(func) or inspect.getfile(func)
        except (TypeError, OSError):
            return None
        
        if not source_file or not os.path.exists(source_file):
            return None
        
        with open(source_file, "r", encoding="utf-8") as f:
            src = f.read()
            
        try:
            mod = ast.parse(src)
        except SyntaxError:
            return None
        
        target_lineno = getattr(func, "__code__", None) and func.__code__.co_firstlineno
        for node in ast.walk(mod):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == func.__name__:
                if getattr(node, "lineno", None) == target_lineno:
                    return node
                
        for node in ast.walk(mod):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == func.__name__:
                return node
            
        return None


    @staticmethod
    def find_func_node_from_snippet(func):
        try:
            src_snip = inspect.getsource(func)
        except (OSError, TypeError, IOError):
            return None
        
        src_snip = textwrap.dedent(src_snip)
        try:
            mod = ast.parse(src_snip)
        except SyntaxError:
            return None
        
        for node in ast.walk(mod):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == func.__name__:
                return node
            
        return None


    @staticmethod
    def get_function_ast_node(func: FunctionType):
        """Return AST node of a function"""
        try:
            src = inspect.getsource(func)
        except (OSError, TypeError):
            return None
        src = textwrap.dedent(src)
        try:
            mod = ast.parse(src)
        except SyntaxError:
            return None
        for node in ast.walk(mod):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == func.__name__:
                return node
        return None


    @staticmethod
    def is_ast_body_empty(node: ast.AST) -> bool:
        """Check if the AST body is empty (pass, ellipsis, docstring only)"""
        if not node or not hasattr(node, "body"):
            return False
        body = node.body
        if len(body) == 0:
            return True
        for stmt in body:
            if isinstance(stmt, ast.Pass):
                continue
            if isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Constant) and stmt.value.value is Ellipsis:
                continue
            if isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Constant) and isinstance(stmt.value.value, str):
                continue
            return False
        return True


    @staticmethod
    def is_empty_function(func: FunctionType) -> bool:
        if func is None:
            return False
        
        node = Helper.get_function_ast_node(func)
        if node is not None:
            return Helper.is_ast_body_empty(node)
        
        code = getattr(func, "__code__", None)
        if code is None:
            return False
        co_names = getattr(code, "co_names", ())
        co_consts = getattr(code, "co_consts", ())
        if not co_names and (co_consts == (None,) or co_consts == (None,)):
            return True
        
        return False
