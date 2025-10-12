"""
AST Transformation Tools for Code Optimization and Generation.

(AI generated docstring)

This module provides higher-level transformation tools that operate on AST structures to perform complex code optimizations and
transformations. The module includes five key functions:

1. makeDictionaryFunctionDef: Creates a lookup dictionary mapping function names to their AST definitions within a module,
	enabling efficient access to specific function definitions.

2. inlineFunctionDef: Performs function inlining by recursively substituting function calls with their implementation bodies,
	creating self-contained functions without external dependencies.

3. removeUnusedParameters: Optimizes function signatures by analyzing and removing unused parameters, updating the function
	signature, return statements, and type annotations accordingly.

4. unparseFindReplace: Recursively replaces AST nodes throughout a tree structure using textual representation matching, providing
	a brute-force but effective approach for complex replacements.

5. write_astModule: Converts an IngredientsModule to optimized Python source code and writes it to a file, handling import
	organization and code formatting in the process.

These transformation tools form the backbone of the code optimization pipeline, enabling sophisticated code transformations while
maintaining semantic integrity and performance characteristics.
"""

from astToolkit import Be, DOT, Grab, IfThis, Make, NodeChanger, NodeTourist, Then, 木
from collections.abc import Mapping
from copy import deepcopy
from hunterMakesPy import raiseIfNone
from hunterMakesPy.filesystemToolkit import settings_autoflakeDEFAULT, writePython
from os import PathLike
from pathlib import PurePath
from typing import Any
import ast
import io

def makeDictionaryAsyncFunctionDef(astAST: ast.AST) -> dict[str, ast.AsyncFunctionDef]:
	"""
	Make a dictionary of `async def` (***async***hronous ***def***inition) function `name` to `ast.AsyncFunctionDef` (***Async***hronous Function ***Def***inition) `object`.

	This function finds all `ast.AsyncFunctionDef` in `astAST` (Abstract Syntax Tree) and makes a
	dictionary of identifiers as strings paired with `ast.AsyncFunctionDef`.

	Parameters
	----------
	astAST : ast.AST
		(Abstract Syntax Tree) The `ast.AST` `object` from which to extract pairs of
		`ast.AsyncFunctionDef.name` as a string and `ast.AsyncFunctionDef` as an `object`.

	Returns
	-------
	dictionaryIdentifier2AsyncFunctionDef : dict[str, ast.AsyncFunctionDef]
		A dictionary of identifier to `ast.AsyncFunctionDef`.
	"""
	dictionaryIdentifier2AsyncFunctionDef: dict[str, ast.AsyncFunctionDef] = {}
	NodeTourist(Be.AsyncFunctionDef, Then.updateKeyValueIn(DOT.name, Then.extractIt, dictionaryIdentifier2AsyncFunctionDef)).visit(astAST)
	return dictionaryIdentifier2AsyncFunctionDef

def makeDictionaryClassDef(astAST: ast.AST) -> dict[str, ast.ClassDef]:
	"""
	Make a dictionary of `class` definition `name` to `ast.ClassDef` (***Class*** ***Def***inition) `object`.

	This function finds all `ast.ClassDef` in `astAST` (Abstract Syntax Tree) and makes a dictionary
	of identifiers as strings paired with `ast.ClassDef`.

	Parameters
	----------
	astAST : ast.AST
		(Abstract Syntax Tree) The `ast.AST` `object` from which to extract pairs of
		`ast.ClassDef.name` as a string and `ast.ClassDef` as an `object`.

	Returns
	-------
	dictionaryIdentifier2ClassDef : dict[str, ast.ClassDef]
		A dictionary of identifier to `ast.ClassDef`.
	"""
	dictionaryIdentifier2ClassDef: dict[str, ast.ClassDef] = {}
	NodeTourist(Be.ClassDef, Then.updateKeyValueIn(DOT.name, Then.extractIt, dictionaryIdentifier2ClassDef)).visit(astAST)
	return dictionaryIdentifier2ClassDef

def makeDictionaryFunctionDef(astAST: ast.AST) -> dict[str, ast.FunctionDef]:
	"""
	Make a dictionary of `def` (***def***inition) function `name` to `ast.FunctionDef` (Function ***Def***inition) `object`.

	This function finds all `ast.FunctionDef` in `astAST` (Abstract Syntax Tree) and makes a
	dictionary of identifiers as strings paired with `ast.FunctionDef`.

	Parameters
	----------
	astAST : ast.AST
		(Abstract Syntax Tree) The `ast.AST` `object` from which to extract pairs of
		`ast.FunctionDef.name` as a string and `ast.FunctionDef` as an `object`.

	Returns
	-------
	dictionaryIdentifier2FunctionDef : dict[str, ast.FunctionDef]
		A dictionary of identifier to `ast.FunctionDef`.
	"""
	dictionaryIdentifier2FunctionDef: dict[str, ast.FunctionDef] = {}
	NodeTourist(Be.FunctionDef, Then.updateKeyValueIn(DOT.name, Then.extractIt, dictionaryIdentifier2FunctionDef)).visit(astAST)
	return dictionaryIdentifier2FunctionDef

def makeDictionaryMosDef(astAST: ast.AST) -> dict[str, ast.AsyncFunctionDef | ast.ClassDef | ast.FunctionDef]:
	"""
	Make a dictionary of identifier to `ast.AsyncFunctionDef` (***Async***hronous Function ***Def***inition), `ast.ClassDef` (***Class*** ***Def***inition), or `ast.FunctionDef` (Function ***Def***inition) `object`.

	This function finds all `ast.AsyncFunctionDef`, `ast.ClassDef`, and `ast.FunctionDef` in
	`astAST` (Abstract Syntax Tree) and makes a dictionary of identifiers as strings paired with
	`ast.AsyncFunctionDef`, `ast.ClassDef`, or `ast.FunctionDef`.

	Parameters
	----------
	astAST : ast.AST
		(Abstract Syntax Tree) The `ast.AST` `object` from which to extract pairs of identifiers and
		`ast.AsyncFunctionDef`, `ast.ClassDef`, or `ast.FunctionDef`.

	Returns
	-------
	dictionaryIdentifier2MosDef : dict[str, ast.AsyncFunctionDef | ast.ClassDef | ast.FunctionDef]
		A dictionary of identifier to `ast.AsyncFunctionDef`, `ast.ClassDef`, or `ast.FunctionDef`.
	"""
	dictionaryIdentifier2MosDef: dict[str, ast.AsyncFunctionDef | ast.ClassDef | ast.FunctionDef] = {}
	dictionaryIdentifier2MosDef.update(makeDictionaryAsyncFunctionDef(astAST))
	dictionaryIdentifier2MosDef.update(makeDictionaryClassDef(astAST))
	dictionaryIdentifier2MosDef.update(makeDictionaryFunctionDef(astAST))
	return dictionaryIdentifier2MosDef

def inlineFunctionDef(identifierToInline: str, astModule: ast.Module) -> ast.FunctionDef:
	"""
	Synthesize a new function from `identifierToInline` with the logic "inlined" from functions called by `identifierToInline`.

	`inlineFunctionDef` starts with the `ast.FunctionDef` in `astModule` whose `ast.FunctionDef.name == identifierToInline`, then
	`inlineFunctionDef` searches through `identifierToInline` for calls to functions defined in `astModule`.

	More specifically, `inlineFunctionDef` searches for an `ast.Call` to an `ast.Name` (*e.g.*, `Path`, but not the
	`ast.Attribute`, `pathlib.Path`). The `ast.Name` identifier is in `ast.Name.id`, for example, `ast.Name.id = "Path"`.
	`inlineFunctionDef` then searches in `astModule` for an `ast.FunctionDef.name` that is the same as the `ast.Name.id`. If
	`inlineFunctionDef` finds a matching `ast.FunctionDef`, it will replace `ast.Call` with the logic from the called function.

	`inlineFunctionDef` repeats the process until it gets bored or until it cannot find any more functions to inline. Therefore,
	`inlineFunctionDef` will inline functions that were not called directly by `identifierToInline` in the original `astModule`.

	`inlineFunctionDef`, however, does not inline an `ast.FunctionDef` if the `ast.FunctionDef` calls itself or if a "child" of
	the `ast.FunctionDef` calls the original `ast.FunctionDef`.

	Parameters
	----------
	identifierToInline : str
		The identifier of the target function; the `str` must match an `ast.FunctionDef.name` in `astModule`.
	astModule : ast.Module
		(abstract syntax tree Module) An `ast.Module` with `ast.FunctionDef.name == identifierToInline` and zero or more other
		`ast.FunctionDef` to inline.

	Returns
	-------
	FunctionDefToInline : ast.FunctionDef
		The synthesized function with inlined logic from other functions defined in `astModule`.

	Raises
	------
		ValueError: If `identifierToInline` does not match any `ast.FunctionDef.name` in `astModule`.
	"""
	dictionaryFunctionDef: dict[str, ast.FunctionDef] = makeDictionaryFunctionDef(astModule)
	try:
		FunctionDefToInline = dictionaryFunctionDef[identifierToInline]
	except KeyError as ERRORmessage:
		message = f"I was unable to find an `ast.FunctionDef` with name {identifierToInline = } in {astModule = }."
		raise ValueError(message) from ERRORmessage

	listIdentifiersCalledFunctions: list[str] = []
# TODO I probably have the skill now to expand this from only `IfThis.isCallToName` to include more options for `ast.Call.func`,
# such as attribute and subscript access. `IfThis.isNestedNameIdentifier` might be perfect. BUT, I think this will affect how I
# key `dictionaryFunctionDef`.
	findIdentifiersToInline = NodeTourist[ast.Call, ast.expr](IfThis.isCallToName
		, Grab.funcAttribute(Grab.idAttribute(Then.appendTo(listIdentifiersCalledFunctions))))
	findIdentifiersToInline.visit(FunctionDefToInline)

	dictionary4Inlining: dict[str, ast.FunctionDef] = {}
	for identifier in sorted(set(listIdentifiersCalledFunctions).intersection(dictionaryFunctionDef.keys())):
# TODO Learn how real programmers avoid infinite loops but still inline recursive functions.
		if NodeTourist(IfThis.matchesMeButNotAnyDescendant(IfThis.isCallIdentifier(identifier)), Then.extractIt).captureLastMatch(astModule) is not None:
			dictionary4Inlining[identifier] = dictionaryFunctionDef[identifier]

	keepGoing = True
	while keepGoing:
		keepGoing = False
		listIdentifiersCalledFunctions.clear()
		findIdentifiersToInline.visit(Make.Module(list(dictionary4Inlining.values())))

		listIdentifiersCalledFunctions = sorted((set(listIdentifiersCalledFunctions).difference(dictionary4Inlining.keys())).intersection(dictionaryFunctionDef.keys()))
		if len(listIdentifiersCalledFunctions) > 0:
			keepGoing = True
			for identifier in listIdentifiersCalledFunctions:
				if NodeTourist(IfThis.matchesMeButNotAnyDescendant(IfThis.isCallIdentifier(identifier)), Then.extractIt).captureLastMatch(astModule) is not None:
					FunctionDefTarget = dictionaryFunctionDef[identifier]
					if len(FunctionDefTarget.body) == 1:
						replacement = NodeTourist(Be.Return, Then.extractIt(DOT.value)).captureLastMatch(FunctionDefTarget)
						inliner = NodeChanger[ast.Call, ast.expr | None](
							findThis = IfThis.isCallIdentifier(identifier), doThat = Then.replaceWith(replacement))
						for astFunctionDef in dictionary4Inlining.values():
							inliner.visit(astFunctionDef)
					else:
						inliner = NodeChanger(Be.Assign.valueIs(IfThis.isCallIdentifier(identifier)), Then.replaceWith(FunctionDefTarget.body[0:-1]))
						for astFunctionDef in dictionary4Inlining.values():
							inliner.visit(astFunctionDef)

	for identifier, FunctionDefTarget in dictionary4Inlining.items():
		if len(FunctionDefTarget.body) == 1:
			replacement = NodeTourist(Be.Return, Then.extractIt(DOT.value)).captureLastMatch(FunctionDefTarget)
			inliner = NodeChanger(IfThis.isCallIdentifier(identifier), Then.replaceWith(replacement))
			inliner.visit(FunctionDefToInline)
		else:
			inliner = NodeChanger(Be.Assign.valueIs(IfThis.isCallIdentifier(identifier)), Then.replaceWith(FunctionDefTarget.body[0:-1]))
			inliner.visit(FunctionDefToInline)
	ast.fix_missing_locations(FunctionDefToInline)
	return FunctionDefToInline

def pythonCode2ast_expr(string: str) -> ast.expr:
	"""PROTOTYPE Convert *one* expression-as-a-string of Python code to an `ast.expr`.

	TODO add list of applicable subclasses. Until then, see `Make.expr` for an approximate list.

	Note well
	---------
	This prototype "shortcut" function has approximately 482 *implied* constraints and pitfalls. If you can't get it to do what
	you want, I recommend saving yourself a bunch of stress and not using this shortcut.
	"""
	return raiseIfNone(NodeTourist(Be.Expr, Then.extractIt(DOT.value)).captureLastMatch(ast.parse(string)))

def removeUnusedParameters(FunctionDef: ast.FunctionDef) -> ast.FunctionDef:
	"""
	Remove unused parameters from `FunctionDef`.

	The `removeUnusedParameters` function removes `ast.arg` (abstract syntax tree ***arg***ument) parameters from the
	`ast.arguments` argument specification of the `ast.FunctionDef` (Function ***Def***inition) function in
	`FunctionDef` that are are not referenced in the `ast.FunctionDef.body` or that are only referenced in
	`ast.Return` return statements.

	This function will replace every `return` statement with a new `return` statement that returns all of the remaining
	parameters. It will update the `returns` annotation.

	Parameters
	----------
	FunctionDef : ast.FunctionDef
		An object containing the AST representation of a function to be processed.

	Returns
	-------
	ast.FunctionDef : ast.FunctionDef
		The modified `ast.FunctionDef` object with unused parameters and corresponding return elements/annotations removed from its AST.
	"""
	list_argCuzMyBrainRefusesToThink = FunctionDef.args.args + FunctionDef.args.posonlyargs + FunctionDef.args.kwonlyargs
	list_arg_arg: list[str] = [ast_arg.arg for ast_arg in list_argCuzMyBrainRefusesToThink]
	listName: list[ast.Name] = []
	fauxFunctionDef = deepcopy(FunctionDef)
	NodeChanger(Be.Return, Then.removeIt).visit(fauxFunctionDef)
	NodeTourist(Be.Name, Then.appendTo(listName)).visit(fauxFunctionDef)
	listIdentifiers: list[str] = [astName.id for astName in listName]
	listIdentifiersNotUsed: list[str] = list(set(list_arg_arg) - set(listIdentifiers))
	for argIdentifier in listIdentifiersNotUsed:
		remove_arg = NodeChanger(IfThis.is_argIdentifier(argIdentifier), Then.removeIt)
		remove_arg.visit(FunctionDef)

	list_argCuzMyBrainRefusesToThink = FunctionDef.args.args + FunctionDef.args.posonlyargs + FunctionDef.args.kwonlyargs

	listName = [Make.Name(ast_arg.arg) for ast_arg in list_argCuzMyBrainRefusesToThink]
	replaceReturn = NodeChanger(Be.Return, Then.replaceWith(Make.Return(Make.Tuple(listName))))
	replaceReturn.visit(FunctionDef)

	list_annotation: list[ast.expr] = [ast_arg.annotation for ast_arg in list_argCuzMyBrainRefusesToThink if ast_arg.annotation is not None]
	FunctionDef.returns = Make.Subscript(Make.Name('tuple'), Make.Tuple(list_annotation))

	ast.fix_missing_locations(FunctionDef)

	return FunctionDef

def unjoinBinOP(astAST: ast.AST, operator: type[ast.operator] = ast.operator) -> list[ast.expr]:
	"""
	Unjoin a binary operation AST node into a list of expressions.

	(AI generated docstring)

	This function takes an AST node representing a binary operation and recursively
	unjoins it into a flat list of expressions. It handles both binary operations
	and unary operations, ensuring that all nested expressions are extracted.

	Parameters
	----------
	astAST : ast.AST
		The AST node to unjoin.
	operator : type[ast.operator] = ast.operator
		The type of binary operator to look for in the AST. Defaults to `ast.operator`.

	Returns
	-------
	list[ast.expr]
		A list of expressions extracted from the binary operation AST node.
	"""
	list_ast_expr: list[ast.expr] = []
	workbench: list[ast.expr] = []

	findThis = Be.BinOp.opIs(lambda this_op: isinstance(this_op, operator))
	doThat = Grab.andDoAllOf([Grab.leftAttribute(Then.appendTo(workbench)), Grab.rightAttribute(Then.appendTo(list_ast_expr))])
	breakingBinOp = NodeTourist(findThis, doThat)

	breakingBinOp.visit(astAST)

	while workbench:
		ast_expr = workbench.pop()
		if isinstance(ast_expr, ast.BinOp):
			breakingBinOp.visit(ast_expr)
		else:
			list_ast_expr.append(ast_expr)

	return list_ast_expr

def unparseFindReplace(astTree: 木, mappingFindReplaceNodes: Mapping[ast.AST, ast.AST]) -> 木:
	"""
	Recursively replace AST (Abstract Syntax Tree) nodes based on a mapping of find-replace pairs.

	(AI generated docstring)

	This function applies brute-force node replacement throughout an AST tree
	by comparing textual representations of nodes. While not the most semantic
	approach, it provides a reliable way to replace complex nested structures
	when more precise targeting methods are difficult to implement.

	The function continues replacing nodes until no more changes are detected
	in the AST's textual representation, ensuring complete replacement throughout
	the tree structure.

	Parameters
	----------
	astTree : ast.AST
		(abstract syntax tree) The AST structure to modify.
	mappingFindReplaceNodes : Mapping[ast.AST, ast.AST]
		A mapping from source nodes to replacement nodes.

	Returns
	-------
	newTree : ast.AST
		The modified AST structure with all matching nodes replaced.
	"""
	keepGoing = True
	newTree = deepcopy(astTree)

	while keepGoing:
		for nodeFind, nodeReplace in mappingFindReplaceNodes.items():
			NodeChanger(IfThis.unparseIs(nodeFind), Then.replaceWith(nodeReplace)).visit(newTree)

		if ast.unparse(newTree) == ast.unparse(astTree):
			keepGoing = False
		else:
			astTree = deepcopy(newTree)
	return newTree

def write_astModule(astModule: ast.Module, pathFilename: PathLike[Any] | PurePath | io.TextIOBase, settings: dict[str, dict[str, Any]] | None = None, identifierPackage: str='') -> None:
	"""
	Convert an AST module to Python source code and write it to a file or stream.

	(AI generated docstring)

	This function takes an AST module structure, converts it to formatted Python source code,
	and writes the result to a file or text stream. The function ensures all AST node locations
	are properly fixed before conversion and applies code formatting and optimization through
	configurable settings.

	By default, the function uses `autoflake` to remove unused imports and variables, and `isort`
	to organize import statements. Custom formatting settings can be provided to control this behavior.

	Parameters
	----------
	astModule : ast.Module
		The AST module to convert and write. This should be a complete module structure with
		all necessary imports, statements, and definitions.
	pathFilename : PathLike[Any] | PurePath | io.TextIOBase
		The destination for the generated Python code. Can be a file path or an open text stream.
	settings : dict[str, dict[str, Any]] | None = None
		Optional configuration for code formatting tools. Should contain nested dictionaries with
		keys like `'autoflake'` and `'isort'`, each mapping to their respective tool settings.
	identifierPackage : str = ''
		Optional package identifier to add to the autoflake additional imports list when no
		settings are provided, ensuring the specified package is preserved during import optimization.

	"""
	ast.fix_missing_locations(astModule)
	pythonSource: str = ast.unparse(astModule)
	if identifierPackage and not settings:
		settings = {'autoflake': settings_autoflakeDEFAULT}
		settings['autoflake']['additional_imports'].append(identifierPackage)
	writePython(pythonSource, pathFilename, settings)
