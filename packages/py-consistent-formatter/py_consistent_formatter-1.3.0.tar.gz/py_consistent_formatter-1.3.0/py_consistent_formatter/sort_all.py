import ast
import sys
import warnings
from operator import attrgetter
from typing import List, Sequence, Tuple

from tokenize_rt import Offset, Token, src_to_tokens, tokens_to_src  # type: ignore[import]


class BaseVisitor:
    """Base visitor for all nodes."""
    def visit(self, root: ast.AST) -> None:
        """Visits a node.

        Args:
            root: Node to visit.
        """

        nodes: Sequence[ast.AST]
        if isinstance(root, ast.Module):
            nodes = root.body
        else:
            nodes = [root]
        for node in nodes:
            method = 'visit_' + node.__class__.__name__
            visitor = getattr(self, method, None)
            if visitor is not None:
                visitor(node)


class ValueVisitor(BaseVisitor):
    """Visitor of a value of an assignment."""
    def __init__(self) -> None:
        """Constructor."""
        self._elements: List[List[ast.Constant]] = []

    @property
    def elements(self) -> List[List[ast.Constant]]:
        """Gets list of constants in the assignment.

        Returns:
            List of constants.
        """
        return self._elements

    def _visit_elems(self, elements: List[ast.expr]) -> None:
        new_elements: List[ast.Constant] = []
        for element in elements:
            if not isinstance(element, ast.Constant):
                return
            elif not isinstance(element.value, str):
                # `__all__` has non-constant element in the container
                # Cannot process it
                return
            else:
                new_elements.append(element)
        self._elements.append(new_elements)

    def visit_List(self, node: ast.List) -> None:  # noqa: N802
        """Visits list.

        Args:
            node: Node with the list.
        """
        self._visit_elems(node.elts)

    def visit_Tuple(self, node: ast.Tuple) -> None:  # noqa: N802
        """Visits tuple.

        Args:
            node: Node with the tuple.
        """
        self._visit_elems(node.elts)

    def visit_Set(self, node: ast.Set) -> None:  # noqa: N802
        """Visits set.

        Args:
            node: Node with the set.
        """
        self._visit_elems(node.elts)


class Visitor(BaseVisitor):
    """Main visitor."""
    def __init__(self) -> None:
        """Constructor."""
        self._elements: List[List[ast.Constant]] = []

    @property
    def elements(self) -> List[List[ast.Constant]]:
        """Returns constant elements.

        Returns:
            List of constants.
        """
        return self._elements

    def visit_ass(self, value: ast.AST, targets: List[ast.expr]) -> None:
        """Visits assignments.

        Args:
            value: Assignment value.
            targets: Assignment targets.
        """
        found = False
        for target in targets:
            if isinstance(target, ast.Name) and target.id == '__all__':
                found = True
                break
        if found:
            visitor = ValueVisitor()
            visitor.visit(value)
            self._elements.extend(visitor._elements)

    def visit_Assign(self, node: ast.Assign) -> None:  # noqa: N802
        """Visits assignment.

        Args:
            node: Node to visit.
        """
        self.visit_ass(node.value, node.targets)

    def visit_AnnAssign(self, node: ast.AnnAssign) -> None:  # noqa: N802
        """Visits assignment.

        Args:
            node: Node to visit.
        """
        if node.value is not None:
            self.visit_ass(node.value, [node.target])

    def visit_AugAssign(self, node: ast.AugAssign) -> None:  # noqa: N802
        """Visits assignment.

        Args:
            node: Node to visit.
        """
        self.visit_ass(node.value, [node.target])


def _consume(tokens: List[Token], start: int, pos: Offset) -> Tuple[str, int]:
    toks: List[Token] = []
    last_idx = -1
    for idx, token in enumerate(tokens[start:]):
        last_idx = idx
        if token.offset == pos:
            break
        else:
            toks.append(token)
    return tokens_to_src(toks), start + last_idx


def _scan(tokens: List[Token], start: int, pos: Offset) -> int:
    last_idx = -1
    for idx, token in enumerate(tokens[start:]):
        last_idx = idx
        if token.offset == pos:
            break
    return start + last_idx


def _ast_parse(contents_text: str) -> ast.Module:
    with warnings.catch_warnings():
        warnings.simplefilter('ignore')
        return ast.parse(contents_text.encode())


def sort_public_exports(contents_text: str) -> str:
    """Alphabetically sorts public exports (contents of `__all__`).

    Args:
        contents_text: Python code to process.

    Returns:
        Python code with `__all__` sorted.
    """
    try:
        ast_obj = _ast_parse(contents_text)
    except SyntaxError:
        return contents_text

    visitor = Visitor()
    visitor.visit(ast_obj)
    if not visitor.elements:
        return contents_text

    tokens = src_to_tokens(contents_text)
    chunks = []
    idx = 0

    for elements in visitor.elements:
        start = Offset(elements[0].lineno, elements[0].col_offset)
        chunk, idx = _consume(tokens, idx, start)
        chunks.append(chunk)

        end = Offset(elements[-1].end_lineno, elements[-1].end_col_offset)
        idx2 = _scan(tokens, idx, end)

        if start.line == end.line:
            chunk = ', '.join(f"'{element.value}'" for element in sorted(elements, key=attrgetter('value')))
        else:
            for token in tokens[idx:idx2]:
                if token.name in ('INDENT', 'UNIMPORTANT_WS'):
                    indent = token.src
                    break
            else:
                indent = ''
            chunk = ('\n' + indent).join(f"'{element.value}'," for element in sorted(elements, key=attrgetter('value')))

        if chunk.endswith(',') and tokens[idx2].src.startswith(','):
            # drop double comma
            chunk = chunk[:-1]

        chunks.append(chunk)
        idx = idx2

    chunk, idx = _consume(tokens, idx, Offset(sys.maxsize, 0))
    chunks.append(chunk)
    return ''.join(chunks)
