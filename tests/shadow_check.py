"""Flag function-local imports that shadow a module-level import.

This is the exact defect that broke _on_js_message: a name imported at
module scope, re-imported inside a function, becomes local for the WHOLE
function body - so any use before the inner import raises UnboundLocalError
at runtime while compiling and linting cleanly.
"""
import ast, sys, glob

def module_imports(tree):
    names = set()
    for node in tree.body:
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            for a in node.names:
                names.add(a.asname or a.name.split(".")[0])
    return names

bad = []
for path in sorted(glob.glob("**/*.py", recursive=True)):
    if "__pycache__" in path:
        continue
    try:
        tree = ast.parse(open(path, encoding="utf-8").read())
    except SyntaxError:
        continue
    top = module_imports(tree)
    for fn in ast.walk(tree):
        if not isinstance(fn, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        for node in ast.walk(fn):
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                for a in node.names:
                    n = a.asname or a.name.split(".")[0]
                    if n in top:
                        bad.append((path, fn.lineno, fn.name, n, node.lineno))
for path, fl, fname, n, il in bad:
    print(f"{path}:{il}  '{n}' re-imported inside {fname}() (module-level import exists)")
print(f"\n{len(bad)} shadowing import(s) found")
sys.exit(1 if bad else 0)
