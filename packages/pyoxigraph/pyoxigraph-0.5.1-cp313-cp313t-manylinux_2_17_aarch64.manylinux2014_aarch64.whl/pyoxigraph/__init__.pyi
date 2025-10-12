import collections.abc
import os
import typing

__all__ = [
    "BaseDirection",
    "BlankNode",
    "CanonicalizationAlgorithm",
    "Dataset",
    "DefaultGraph",
    "Literal",
    "NamedNode",
    "Quad",
    "QuadParser",
    "QueryBoolean",
    "QueryResultsFormat",
    "QuerySolution",
    "QuerySolutions",
    "QueryTriples",
    "RdfFormat",
    "Store",
    "Triple",
    "Variable",
    "parse",
    "parse_query_results",
    "serialize",
    "__version__",
]
__version__: str = ...

@typing.final
class BaseDirection:
    """A `directional language-tagged string <https://www.w3.org/TR/rdf12-concepts/#dfn-dir-lang-string>`_ `base-direction <https://www.w3.org/TR/rdf12-concepts/#dfn-base-direction>`_

    :param value: the direction as a string (`ltr` or `rtl`).

    >>> str(BaseDirection.LTR)
    'ltr'
    >>> str(BaseDirection("ltr"))
    'ltr'"""

    value: str
    "the base direction as a string"

    def __init__(self, /, value: str) -> None:
        """A `directional language-tagged string <https://www.w3.org/TR/rdf12-concepts/#dfn-dir-lang-string>`_ `base-direction <https://www.w3.org/TR/rdf12-concepts/#dfn-base-direction>`_

        :param value: the direction as a string (`ltr` or `rtl`).

        >>> str(BaseDirection.LTR)
        'ltr'
        >>> str(BaseDirection("ltr"))
        'ltr'"""

    def __copy__(self, /) -> BaseDirection: ...
    def __deepcopy__(self, /, memo: typing.Any) -> BaseDirection: ...
    def __eq__(self, value: typing.Any, /) -> bool:
        """Return self==value."""

    def __ge__(self, value: typing.Any, /) -> bool:
        """Return self>=value."""

    def __getnewargs__(self, /) -> typing.Any: ...
    def __gt__(self, value: typing.Any, /) -> bool:
        """Return self>value."""

    def __hash__(self, /) -> int:
        """Return hash(self)."""

    def __le__(self, value: typing.Any, /) -> bool:
        """Return self<=value."""

    def __lt__(self, value: typing.Any, /) -> bool:
        """Return self<value."""

    def __ne__(self, value: typing.Any, /) -> bool:
        """Return self!=value."""

    def __repr__(self, /) -> str:
        """Return repr(self)."""

    def __str__(self, /) -> str:
        """Return str(self)."""
    LTR: BaseDirection = ...
    RTL: BaseDirection = ...
    __match_args__: tuple[str, ...] = ("value",)

@typing.final
class BlankNode:
    """An RDF `blank node <https://www.w3.org/TR/rdf11-concepts/#dfn-blank-node>`_.

    :param value: the `blank node identifier <https://www.w3.org/TR/rdf11-concepts/#dfn-blank-node-identifier>`_ (if not present, a random blank node identifier is automatically generated).
    :raises ValueError: if the blank node identifier is invalid according to NTriples, Turtle, and SPARQL grammars.

    The :py:class:`str` function provides a serialization compatible with NTriples, Turtle, and SPARQL:

    >>> str(BlankNode('ex'))
    '_:ex'"""

    value: str
    "the `blank node identifier <https://www.w3.org/TR/rdf11-concepts/#dfn-blank-node-identifier>`_."

    def __init__(self, /, value: str | None = None) -> None:
        """An RDF `blank node <https://www.w3.org/TR/rdf11-concepts/#dfn-blank-node>`_.

        :param value: the `blank node identifier <https://www.w3.org/TR/rdf11-concepts/#dfn-blank-node-identifier>`_ (if not present, a random blank node identifier is automatically generated).
        :raises ValueError: if the blank node identifier is invalid according to NTriples, Turtle, and SPARQL grammars.

        The :py:class:`str` function provides a serialization compatible with NTriples, Turtle, and SPARQL:

        >>> str(BlankNode('ex'))
        '_:ex'"""

    def __copy__(self, /) -> BlankNode: ...
    def __deepcopy__(self, /, memo: typing.Any) -> BlankNode: ...
    def __eq__(self, value: typing.Any, /) -> bool:
        """Return self==value."""

    def __ge__(self, value: typing.Any, /) -> bool:
        """Return self>=value."""

    def __getnewargs__(self, /) -> typing.Any: ...
    def __gt__(self, value: typing.Any, /) -> bool:
        """Return self>value."""

    def __hash__(self, /) -> int:
        """Return hash(self)."""

    def __le__(self, value: typing.Any, /) -> bool:
        """Return self<=value."""

    def __lt__(self, value: typing.Any, /) -> bool:
        """Return self<value."""

    def __ne__(self, value: typing.Any, /) -> bool:
        """Return self!=value."""

    def __repr__(self, /) -> str:
        """Return repr(self)."""

    def __str__(self, /) -> str:
        """Return str(self)."""
    __match_args__: tuple[str, ...] = ("value",)

@typing.final
class CanonicalizationAlgorithm:
    """RDF canonicalization algorithms.

    The following algorithms are supported:

    * :py:attr:`CanonicalizationAlgorithm.UNSTABLE`: an unstable algorithm preferred by PyOxigraph."""

    def __init__(self, /) -> None:
        """RDF canonicalization algorithms.

        The following algorithms are supported:

        * :py:attr:`CanonicalizationAlgorithm.UNSTABLE`: an unstable algorithm preferred by PyOxigraph."""

    def __copy__(self, /) -> CanonicalizationAlgorithm: ...
    def __deepcopy__(self, /, memo: typing.Any) -> CanonicalizationAlgorithm: ...
    def __repr__(self, /) -> str:
        """Return repr(self)."""
    UNSTABLE: CanonicalizationAlgorithm = ...

@typing.final
class Dataset:
    """An in-memory `RDF dataset <https://www.w3.org/TR/rdf11-concepts/#dfn-rdf-dataset>`_.

    It can accommodate a fairly large number of quads (in the few millions).

    Use :py:class:`Store` if you need on-disk persistence or SPARQL.

    Warning: It interns the strings and does not do any garbage collection yet:
    if you insert and remove a lot of different terms, memory will grow without any reduction.

    :param quads: some quads to initialize the dataset with.

    The :py:class:`str` function provides an N-Quads serialization:

    >>> str(Dataset([Quad(NamedNode('http://example.com/s'), NamedNode('http://example.com/p'), NamedNode('http://example.com/o'), NamedNode('http://example.com/g'))]))
    '<http://example.com/s> <http://example.com/p> <http://example.com/o> <http://example.com/g> .\\n'"""

    def __init__(self, /, quads: collections.abc.Iterable[Quad] | None = None) -> None:
        """An in-memory `RDF dataset <https://www.w3.org/TR/rdf11-concepts/#dfn-rdf-dataset>`_.

        It can accommodate a fairly large number of quads (in the few millions).

        Use :py:class:`Store` if you need on-disk persistence or SPARQL.

        Warning: It interns the strings and does not do any garbage collection yet:
        if you insert and remove a lot of different terms, memory will grow without any reduction.

        :param quads: some quads to initialize the dataset with.

        The :py:class:`str` function provides an N-Quads serialization:

        >>> str(Dataset([Quad(NamedNode('http://example.com/s'), NamedNode('http://example.com/p'), NamedNode('http://example.com/o'), NamedNode('http://example.com/g'))]))
        '<http://example.com/s> <http://example.com/p> <http://example.com/o> <http://example.com/g> .\\n'"""

    def add(self, /, quad: Quad) -> None:
        """Adds a quad to the dataset.

        :param quad: the quad to add.

        >>> quad = Quad(NamedNode('http://example.com/s'), NamedNode('http://example.com/p'), NamedNode('http://example.com/o'), NamedNode('http://example.com/g'))
        >>> dataset = Dataset()
        >>> dataset.add(quad)
        >>> quad in dataset
        True"""

    def canonicalize(self, /, algorithm: CanonicalizationAlgorithm) -> None:
        """Canonicalizes the dataset by renaming blank nodes.

        Warning: Blank node ids depends on the current shape of the graph. Adding a new quad might change the ids of a lot of blank nodes.
        Hence, this canonization might not be suitable for diffs.

        Warning: This implementation worst-case complexity is in *O(b!)* with *b* the number of blank nodes in the input dataset.

        :param algorithm: the canonicalization algorithm to use.

        >>> d1 = Dataset([Quad(BlankNode(), NamedNode('http://example.com/p'), BlankNode())])
        >>> d2 = Dataset([Quad(BlankNode(), NamedNode('http://example.com/p'), BlankNode())])
        >>> d1 == d2
        False
        >>> d1.canonicalize(CanonicalizationAlgorithm.UNSTABLE)
        >>> d2.canonicalize(CanonicalizationAlgorithm.UNSTABLE)
        >>> d1 == d2
        True"""

    def clear(self, /) -> None:
        """Removes all quads from the dataset.


        >>> quad = Quad(NamedNode('http://example.com/s'), NamedNode('http://example.com/p'), NamedNode('http://example.com/o'), NamedNode('http://example.com/g'))
        >>> dataset = Dataset([quad])
        >>> dataset.clear()
        >>> len(dataset)
        0"""

    def discard(self, /, quad: Quad) -> None:
        """Removes a quad from the dataset if it is present.

        :param quad: the quad to remove.

        >>> quad = Quad(NamedNode('http://example.com/s'), NamedNode('http://example.com/p'), NamedNode('http://example.com/o'), NamedNode('http://example.com/g'))
        >>> dataset = Dataset([quad])
        >>> dataset.discard(quad)
        >>> quad in dataset
        False"""

    def quads_for_graph_name(
        self, /, graph_name: NamedNode | BlankNode | DefaultGraph
    ) -> collections.abc.Iterator[Quad]:
        """Looks for the quads with the given graph name.

        :param graph_name: the quad graph name.
        :return: an iterator of the quads.

        >>> store = Dataset([Quad(NamedNode('http://example.com'), NamedNode('http://example.com/p'), Literal('1'), NamedNode('http://example.com/g'))])
        >>> list(store.quads_for_graph_name(NamedNode('http://example.com/g')))
        [<Quad subject=<NamedNode value=http://example.com> predicate=<NamedNode value=http://example.com/p> object=<Literal value=1 datatype=<NamedNode value=http://www.w3.org/2001/XMLSchema#string>> graph_name=<NamedNode value=http://example.com/g>>]"""

    def quads_for_object(self, /, object: NamedNode | BlankNode | Literal | Triple) -> collections.abc.Iterator[Quad]:
        """Looks for the quads with the given object.

        :param object: the quad object.
        :return: an iterator of the quads.

        >>> store = Dataset([Quad(NamedNode('http://example.com'), NamedNode('http://example.com/p'), Literal('1'), NamedNode('http://example.com/g'))])
        >>> list(store.quads_for_object(Literal('1')))
        [<Quad subject=<NamedNode value=http://example.com> predicate=<NamedNode value=http://example.com/p> object=<Literal value=1 datatype=<NamedNode value=http://www.w3.org/2001/XMLSchema#string>> graph_name=<NamedNode value=http://example.com/g>>]"""

    def quads_for_predicate(self, /, predicate: NamedNode) -> collections.abc.Iterator[Quad]:
        """Looks for the quads with the given predicate.

        :param predicate: the quad predicate.
        :return: an iterator of the quads.

        >>> store = Dataset([Quad(NamedNode('http://example.com'), NamedNode('http://example.com/p'), Literal('1'), NamedNode('http://example.com/g'))])
        >>> list(store.quads_for_predicate(NamedNode('http://example.com/p')))
        [<Quad subject=<NamedNode value=http://example.com> predicate=<NamedNode value=http://example.com/p> object=<Literal value=1 datatype=<NamedNode value=http://www.w3.org/2001/XMLSchema#string>> graph_name=<NamedNode value=http://example.com/g>>]"""

    def quads_for_subject(self, /, subject: NamedNode | BlankNode | Triple) -> collections.abc.Iterator[Quad]:
        """Looks for the quads with the given subject.

        :param subject: the quad subject.
        :return: an iterator of the quads.

        >>> store = Dataset([Quad(NamedNode('http://example.com'), NamedNode('http://example.com/p'), Literal('1'), NamedNode('http://example.com/g'))])
        >>> list(store.quads_for_subject(NamedNode('http://example.com')))
        [<Quad subject=<NamedNode value=http://example.com> predicate=<NamedNode value=http://example.com/p> object=<Literal value=1 datatype=<NamedNode value=http://www.w3.org/2001/XMLSchema#string>> graph_name=<NamedNode value=http://example.com/g>>]"""

    def remove(self, /, quad: Quad) -> None:
        """Removes a quad from the dataset and raises an exception if it is not in the set.

        :param quad: the quad to remove.
        :raises KeyError: if the element was not in the set.

        >>> quad = Quad(NamedNode('http://example.com/s'), NamedNode('http://example.com/p'), NamedNode('http://example.com/o'), NamedNode('http://example.com/g'))
        >>> dataset = Dataset([quad])
        >>> dataset.remove(quad)
        >>> quad in dataset
        False"""

    def __bool__(self, /) -> bool:
        """True if self else False"""

    def __contains__(self, key: typing.Any, /) -> bool:
        """Return bool(key in self)."""

    def __eq__(self, value: typing.Any, /) -> bool:
        """Return self==value."""

    def __ge__(self, value: typing.Any, /) -> bool:
        """Return self>=value."""

    def __gt__(self, value: typing.Any, /) -> bool:
        """Return self>value."""

    def __iter__(self, /) -> typing.Any:
        """Implement iter(self)."""

    def __le__(self, value: typing.Any, /) -> bool:
        """Return self<=value."""

    def __len__(self, /) -> int:
        """Return len(self)."""

    def __lt__(self, value: typing.Any, /) -> bool:
        """Return self<value."""

    def __ne__(self, value: typing.Any, /) -> bool:
        """Return self!=value."""

    def __str__(self, /) -> str:
        """Return str(self)."""

@typing.final
class DefaultGraph:
    """The RDF `default graph name <https://www.w3.org/TR/rdf11-concepts/#dfn-default-graph>`_."""

    def __init__(self, /) -> None:
        """The RDF `default graph name <https://www.w3.org/TR/rdf11-concepts/#dfn-default-graph>`_."""

    def __copy__(self, /) -> DefaultGraph: ...
    def __deepcopy__(self, /, memo: typing.Any) -> DefaultGraph: ...
    def __eq__(self, value: typing.Any, /) -> bool:
        """Return self==value."""

    def __ge__(self, value: typing.Any, /) -> bool:
        """Return self>=value."""

    def __getnewargs__(self, /) -> typing.Any: ...
    def __gt__(self, value: typing.Any, /) -> bool:
        """Return self>value."""

    def __hash__(self, /) -> int:
        """Return hash(self)."""

    def __le__(self, value: typing.Any, /) -> bool:
        """Return self<=value."""

    def __lt__(self, value: typing.Any, /) -> bool:
        """Return self<value."""

    def __ne__(self, value: typing.Any, /) -> bool:
        """Return self!=value."""

    def __repr__(self, /) -> str:
        """Return repr(self)."""

    def __str__(self, /) -> str:
        """Return str(self)."""

@typing.final
class Literal:
    """An RDF `literal <https://www.w3.org/TR/rdf11-concepts/#dfn-literal>`_.

    :param value: the literal value or `lexical form <https://www.w3.org/TR/rdf11-concepts/#dfn-lexical-form>`_.
    :param datatype: the literal `datatype IRI <https://www.w3.org/TR/rdf11-concepts/#dfn-datatype-iri>`_.
    :param language: the literal `language tag <https://www.w3.org/TR/rdf11-concepts/#dfn-language-tag>`_.
    :param direction: the literal `base direction <https://www.w3.org/TR/rdf12-concepts/#dfn-base-direction>`_.
    :raises ValueError: if the language tag is not valid according to `RFC 5646 <https://tools.ietf.org/rfc/rfc5646>`_ (`BCP 47 <https://tools.ietf.org/rfc/bcp/bcp47>`_).

    The :py:class:`str` function provides a serialization compatible with NTriples, Turtle, and SPARQL:

    >>> str(Literal('example'))
    '"example"'
    >>> str(Literal('example', language='en'))
    '"example"@en'
    >>> str(Literal('11', datatype=NamedNode('http://www.w3.org/2001/XMLSchema#integer')))
    '"11"^^<http://www.w3.org/2001/XMLSchema#integer>'
    >>> str(Literal(11))
    '"11"^^<http://www.w3.org/2001/XMLSchema#integer>'"""

    datatype: NamedNode
    "the literal `datatype IRI <https://www.w3.org/TR/rdf11-concepts/#dfn-datatype-iri>`_."
    direction: BaseDirection | None
    "the literal `base direction <https://www.w3.org/TR/rdf12-concepts/#dfn-base-direction>`_."
    language: str | None
    "the literal `language tag <https://www.w3.org/TR/rdf11-concepts/#dfn-language-tag>`_."
    value: str
    "the literal value or `lexical form <https://www.w3.org/TR/rdf11-concepts/#dfn-lexical-form>`_."

    def __init__(
        self,
        /,
        value: str | int | float | bool,
        *,
        datatype: NamedNode | None = None,
        language: str | None = None,
        direction: BaseDirection | None = None,
    ) -> None:
        """An RDF `literal <https://www.w3.org/TR/rdf11-concepts/#dfn-literal>`_.

        :param value: the literal value or `lexical form <https://www.w3.org/TR/rdf11-concepts/#dfn-lexical-form>`_.
        :param datatype: the literal `datatype IRI <https://www.w3.org/TR/rdf11-concepts/#dfn-datatype-iri>`_.
        :param language: the literal `language tag <https://www.w3.org/TR/rdf11-concepts/#dfn-language-tag>`_.
        :param direction: the literal `base direction <https://www.w3.org/TR/rdf12-concepts/#dfn-base-direction>`_.
        :raises ValueError: if the language tag is not valid according to `RFC 5646 <https://tools.ietf.org/rfc/rfc5646>`_ (`BCP 47 <https://tools.ietf.org/rfc/bcp/bcp47>`_).

        The :py:class:`str` function provides a serialization compatible with NTriples, Turtle, and SPARQL:

        >>> str(Literal('example'))
        '"example"'
        >>> str(Literal('example', language='en'))
        '"example"@en'
        >>> str(Literal('11', datatype=NamedNode('http://www.w3.org/2001/XMLSchema#integer')))
        '"11"^^<http://www.w3.org/2001/XMLSchema#integer>'
        >>> str(Literal(11))
        '"11"^^<http://www.w3.org/2001/XMLSchema#integer>'"""

    def __copy__(self, /) -> Literal: ...
    def __deepcopy__(self, /, memo: typing.Any) -> Literal: ...
    def __eq__(self, value: typing.Any, /) -> bool:
        """Return self==value."""

    def __ge__(self, value: typing.Any, /) -> bool:
        """Return self>=value."""

    def __getnewargs_ex__(self, /) -> typing.Any: ...
    def __gt__(self, value: typing.Any, /) -> bool:
        """Return self>value."""

    def __hash__(self, /) -> int:
        """Return hash(self)."""

    def __le__(self, value: typing.Any, /) -> bool:
        """Return self<=value."""

    def __lt__(self, value: typing.Any, /) -> bool:
        """Return self<value."""

    def __ne__(self, value: typing.Any, /) -> bool:
        """Return self!=value."""

    def __repr__(self, /) -> str:
        """Return repr(self)."""

    def __str__(self, /) -> str:
        """Return str(self)."""
    __match_args__: tuple[str, ...] = ("value",)

@typing.final
class NamedNode:
    """An RDF `node identified by an IRI <https://www.w3.org/TR/rdf11-concepts/#dfn-iri>`_.

    :param value: the IRI as a string.
    :raises ValueError: if the IRI is not valid according to `RFC 3987 <https://tools.ietf.org/rfc/rfc3987>`_.

    The :py:class:`str` function provides a serialization compatible with NTriples, Turtle, and SPARQL:

    >>> str(NamedNode('http://example.com'))
    '<http://example.com>'"""

    value: str
    "the named node IRI."

    def __init__(self, /, value: str) -> None:
        """An RDF `node identified by an IRI <https://www.w3.org/TR/rdf11-concepts/#dfn-iri>`_.

        :param value: the IRI as a string.
        :raises ValueError: if the IRI is not valid according to `RFC 3987 <https://tools.ietf.org/rfc/rfc3987>`_.

        The :py:class:`str` function provides a serialization compatible with NTriples, Turtle, and SPARQL:

        >>> str(NamedNode('http://example.com'))
        '<http://example.com>'"""

    def __copy__(self, /) -> NamedNode: ...
    def __deepcopy__(self, /, memo: typing.Any) -> NamedNode: ...
    def __eq__(self, value: typing.Any, /) -> bool:
        """Return self==value."""

    def __ge__(self, value: typing.Any, /) -> bool:
        """Return self>=value."""

    def __getnewargs__(self, /) -> typing.Any: ...
    def __gt__(self, value: typing.Any, /) -> bool:
        """Return self>value."""

    def __hash__(self, /) -> int:
        """Return hash(self)."""

    def __le__(self, value: typing.Any, /) -> bool:
        """Return self<=value."""

    def __lt__(self, value: typing.Any, /) -> bool:
        """Return self<value."""

    def __ne__(self, value: typing.Any, /) -> bool:
        """Return self!=value."""

    def __repr__(self, /) -> str:
        """Return repr(self)."""

    def __str__(self, /) -> str:
        """Return str(self)."""
    __match_args__: tuple[str, ...] = ("value",)

@typing.final
class Quad:
    """An RDF `triple <https://www.w3.org/TR/rdf11-concepts/#dfn-rdf-triple>`_.
    in a `RDF dataset <https://www.w3.org/TR/rdf11-concepts/#dfn-rdf-dataset>`_.

    :param subject: the quad subject.
    :param predicate: the quad predicate.
    :param object: the quad object.
    :param graph_name: the quad graph name. If not present, the default graph is assumed.

    The :py:class:`str` function provides a serialization compatible with NTriples, Turtle, and SPARQL:

    >>> str(Quad(NamedNode('http://example.com'), NamedNode('http://example.com/p'), Literal('1'), NamedNode('http://example.com/g')))
    '<http://example.com> <http://example.com/p> "1" <http://example.com/g>'

    >>> str(Quad(NamedNode('http://example.com'), NamedNode('http://example.com/p'), Literal('1'), DefaultGraph()))
    '<http://example.com> <http://example.com/p> "1"'

    A quad could also be easily destructed into its components:

    >>> (s, p, o, g) = Quad(NamedNode('http://example.com'), NamedNode('http://example.com/p'), Literal('1'), NamedNode('http://example.com/g'))"""

    graph_name: NamedNode | BlankNode | DefaultGraph
    "the quad graph name."
    object: NamedNode | BlankNode | Literal | Triple
    "the quad object."
    predicate: NamedNode
    "the quad predicate."
    subject: NamedNode | BlankNode | Triple
    "the quad subject."
    triple: Triple
    "the quad underlying triple."

    def __init__(
        self,
        /,
        subject: NamedNode | BlankNode | Triple,
        predicate: NamedNode,
        object: NamedNode | BlankNode | Literal | Triple,
        graph_name: NamedNode | BlankNode | DefaultGraph | None = None,
    ) -> None:
        """An RDF `triple <https://www.w3.org/TR/rdf11-concepts/#dfn-rdf-triple>`_.
        in a `RDF dataset <https://www.w3.org/TR/rdf11-concepts/#dfn-rdf-dataset>`_.

        :param subject: the quad subject.
        :param predicate: the quad predicate.
        :param object: the quad object.
        :param graph_name: the quad graph name. If not present, the default graph is assumed.

        The :py:class:`str` function provides a serialization compatible with NTriples, Turtle, and SPARQL:

        >>> str(Quad(NamedNode('http://example.com'), NamedNode('http://example.com/p'), Literal('1'), NamedNode('http://example.com/g')))
        '<http://example.com> <http://example.com/p> "1" <http://example.com/g>'

        >>> str(Quad(NamedNode('http://example.com'), NamedNode('http://example.com/p'), Literal('1'), DefaultGraph()))
        '<http://example.com> <http://example.com/p> "1"'

        A quad could also be easily destructed into its components:

        >>> (s, p, o, g) = Quad(NamedNode('http://example.com'), NamedNode('http://example.com/p'), Literal('1'), NamedNode('http://example.com/g'))"""

    def __copy__(self, /) -> Quad: ...
    def __deepcopy__(self, /, memo: typing.Any) -> Quad: ...
    def __eq__(self, value: typing.Any, /) -> bool:
        """Return self==value."""

    def __ge__(self, value: typing.Any, /) -> bool:
        """Return self>=value."""

    def __getitem__(self, key: typing.Any, /) -> typing.Any:
        """Return self[key]."""

    def __getnewargs__(self, /) -> typing.Any: ...
    def __gt__(self, value: typing.Any, /) -> bool:
        """Return self>value."""

    def __hash__(self, /) -> int:
        """Return hash(self)."""

    def __iter__(self, /) -> typing.Any:
        """Implement iter(self)."""

    def __le__(self, value: typing.Any, /) -> bool:
        """Return self<=value."""

    def __len__(self, /) -> int:
        """Return len(self)."""

    def __lt__(self, value: typing.Any, /) -> bool:
        """Return self<value."""

    def __ne__(self, value: typing.Any, /) -> bool:
        """Return self!=value."""

    def __repr__(self, /) -> str:
        """Return repr(self)."""

    def __str__(self, /) -> str:
        """Return str(self)."""
    __match_args__: tuple[str, ...] = ("subject", "predicate", "object", "graph_name")

@typing.final
class QuadParser:
    """An iterator of :py:class:`Quad` returned by :py:func:`parse`.

    >>> store = Store()
    >>> store.add(Quad(NamedNode('http://example.com'), NamedNode('http://example.com/p'), Literal('1')))
    >>> quads = parse(input=b'<foo> <p> "1" .', format=RdfFormat.TURTLE, base_iri="http://example.com/")
    >>> next(quads)
    <Quad subject=<NamedNode value=http://example.com/foo> predicate=<NamedNode value=http://example.com/p> object=<Literal value=1 datatype=<NamedNode value=http://www.w3.org/2001/XMLSchema#string>> graph_name=<DefaultGraph>>"""

    base_iri: str | None
    prefixes: dict[str, str]

    def __init__(self, /) -> None:
        """An iterator of :py:class:`Quad` returned by :py:func:`parse`.

        >>> store = Store()
        >>> store.add(Quad(NamedNode('http://example.com'), NamedNode('http://example.com/p'), Literal('1')))
        >>> quads = parse(input=b'<foo> <p> "1" .', format=RdfFormat.TURTLE, base_iri="http://example.com/")
        >>> next(quads)
        <Quad subject=<NamedNode value=http://example.com/foo> predicate=<NamedNode value=http://example.com/p> object=<Literal value=1 datatype=<NamedNode value=http://www.w3.org/2001/XMLSchema#string>> graph_name=<DefaultGraph>>"""

    def __iter__(self, /) -> typing.Any:
        """Implement iter(self)."""

    def __next__(self, /) -> typing.Any:
        """Implement next(self)."""

@typing.final
class QueryBoolean:
    """A boolean returned by a SPARQL ``ASK`` query.

    It can be easily casted to a regular boolean using the :py:func:`bool` function.

    >>> store = Store()
    >>> store.add(Quad(NamedNode('http://example.com'), NamedNode('http://example.com/p'), Literal('1')))
    >>> bool(store.query('ASK { ?s ?p ?o }'))
    True"""

    def __init__(self, /) -> None:
        """A boolean returned by a SPARQL ``ASK`` query.

        It can be easily casted to a regular boolean using the :py:func:`bool` function.

        >>> store = Store()
        >>> store.add(Quad(NamedNode('http://example.com'), NamedNode('http://example.com/p'), Literal('1')))
        >>> bool(store.query('ASK { ?s ?p ?o }'))
        True"""

    def serialize(
        self,
        /,
        output: typing.IO[bytes] | str | os.PathLike[str] | None = None,
        format: QueryResultsFormat | None = None,
    ) -> bytes | None:
        """Writes the query results into a file.

        It currently supports the following formats:

        * `XML <https://www.w3.org/TR/rdf-sparql-XMLres/>`_ (:py:attr:`QueryResultsFormat.XML`)
        * `JSON <https://www.w3.org/TR/sparql11-results-json/>`_ (:py:attr:`QueryResultsFormat.JSON`)
        * `CSV <https://www.w3.org/TR/sparql11-results-csv-tsv/>`_ (:py:attr:`QueryResultsFormat.CSV`)
        * `TSV <https://www.w3.org/TR/sparql11-results-csv-tsv/>`_ (:py:attr:`QueryResultsFormat.TSV`)

        :param output: The binary I/O object or file path to write to. For example, it could be a file path as a string or a file writer opened in binary mode with ``open('my_file.ttl', 'wb')``. If :py:const:`None`, a :py:class:`bytes` buffer is returned with the serialized content.
        :param format: the format of the query results serialization. If :py:const:`None`, the format is guessed from the file name extension.
        :raises ValueError: if the format is not supported.
        :raises OSError: if a system error happens while writing the file.

        >>> store = Store()
        >>> store.add(Quad(NamedNode('http://example.com'), NamedNode('http://example.com/p'), Literal('1')))
        >>> results = store.query("ASK { ?s ?p ?o }")
        >>> results.serialize(format=QueryResultsFormat.JSON)
        b'{"head":{},"boolean":true}'"""

    def __bool__(self, /) -> bool:
        """True if self else False"""

    def __eq__(self, value: typing.Any, /) -> bool:
        """Return self==value."""

    def __ge__(self, value: typing.Any, /) -> bool:
        """Return self>=value."""

    def __gt__(self, value: typing.Any, /) -> bool:
        """Return self>value."""

    def __hash__(self, /) -> int:
        """Return hash(self)."""

    def __le__(self, value: typing.Any, /) -> bool:
        """Return self<=value."""

    def __lt__(self, value: typing.Any, /) -> bool:
        """Return self<value."""

    def __ne__(self, value: typing.Any, /) -> bool:
        """Return self!=value."""

    def __repr__(self, /) -> str:
        """Return repr(self)."""

@typing.final
class QueryResultsFormat:
    """`SPARQL query <https://www.w3.org/TR/sparql11-query/>`_ results serialization formats.

    The following formats are supported:

    * `XML <https://www.w3.org/TR/rdf-sparql-XMLres/>`_ (:py:attr:`QueryResultsFormat.XML`)
    * `JSON <https://www.w3.org/TR/sparql11-results-json/>`_ (:py:attr:`QueryResultsFormat.JSON`)
    * `CSV <https://www.w3.org/TR/sparql11-results-csv-tsv/>`_ (:py:attr:`QueryResultsFormat.CSV`)
    * `TSV <https://www.w3.org/TR/sparql11-results-csv-tsv/>`_ (:py:attr:`QueryResultsFormat.TSV`)"""

    file_extension: str
    "the format `IANA-registered <https://tools.ietf.org/html/rfc2046>`_ file extension."
    iri: str
    "the format canonical IRI according to the `Unique URIs for file formats registry <https://www.w3.org/ns/formats/>`_."
    media_type: str
    "the format `IANA media type <https://tools.ietf.org/html/rfc2046>`_."
    name: str
    "the format name."

    def __init__(self, /) -> None:
        """`SPARQL query <https://www.w3.org/TR/sparql11-query/>`_ results serialization formats.

        The following formats are supported:

        * `XML <https://www.w3.org/TR/rdf-sparql-XMLres/>`_ (:py:attr:`QueryResultsFormat.XML`)
        * `JSON <https://www.w3.org/TR/sparql11-results-json/>`_ (:py:attr:`QueryResultsFormat.JSON`)
        * `CSV <https://www.w3.org/TR/sparql11-results-csv-tsv/>`_ (:py:attr:`QueryResultsFormat.CSV`)
        * `TSV <https://www.w3.org/TR/sparql11-results-csv-tsv/>`_ (:py:attr:`QueryResultsFormat.TSV`)"""

    @staticmethod
    def from_extension(extension: str) -> QueryResultsFormat | None:
        """Looks for a known format from an extension.

        It supports some aliases.

        :param extension: the extension.
        :return: :py:class:`QueryResultsFormat` if the extension is known or :py:const:`None` if not.

        >>> QueryResultsFormat.from_extension("json")
        <QueryResultsFormat SPARQL Results in JSON>"""

    @staticmethod
    def from_media_type(media_type: str) -> QueryResultsFormat | None:
        """Looks for a known format from a media type.

        It supports some media type aliases.
        For example, "application/xml" is going to return :py:const:`QueryResultsFormat.XML` even if it is not its canonical media type.

        :param media_type: the media type.
        :return: :py:class:`QueryResultsFormat` if the media type is known or :py:const:`None` if not.

        >>> QueryResultsFormat.from_media_type("application/sparql-results+json; charset=utf-8")
        <QueryResultsFormat SPARQL Results in JSON>"""

    def __copy__(self, /) -> QueryResultsFormat: ...
    def __deepcopy__(self, /, memo: typing.Any) -> QueryResultsFormat: ...
    def __eq__(self, value: typing.Any, /) -> bool:
        """Return self==value."""

    def __ge__(self, value: typing.Any, /) -> bool:
        """Return self>=value."""

    def __gt__(self, value: typing.Any, /) -> bool:
        """Return self>value."""

    def __hash__(self, /) -> int:
        """Return hash(self)."""

    def __le__(self, value: typing.Any, /) -> bool:
        """Return self<=value."""

    def __lt__(self, value: typing.Any, /) -> bool:
        """Return self<value."""

    def __ne__(self, value: typing.Any, /) -> bool:
        """Return self!=value."""

    def __repr__(self, /) -> str:
        """Return repr(self)."""

    def __str__(self, /) -> str:
        """Return str(self)."""
    CSV: QueryResultsFormat = ...
    JSON: QueryResultsFormat = ...
    TSV: QueryResultsFormat = ...
    XML: QueryResultsFormat = ...

@typing.final
class QuerySolution:
    """Tuple associating variables and terms that are the result of a SPARQL ``SELECT`` query.

    It is the equivalent of a row in SQL.

    It could be indexes by variable name (:py:class:`Variable` or :py:class:`str`) or position in the tuple (:py:class:`int`).
    Unpacking also works.

    >>> store = Store()
    >>> store.add(Quad(NamedNode('http://example.com'), NamedNode('http://example.com/p'), Literal('1')))
    >>> solution = next(store.query('SELECT ?s ?p ?o WHERE { ?s ?p ?o }'))
    >>> solution[Variable('s')]
    <NamedNode value=http://example.com>
    >>> solution['s']
    <NamedNode value=http://example.com>
    >>> solution[0]
    <NamedNode value=http://example.com>
    >>> s, p, o = solution
    >>> s
    <NamedNode value=http://example.com>"""

    def __init__(self, /) -> None:
        """Tuple associating variables and terms that are the result of a SPARQL ``SELECT`` query.

        It is the equivalent of a row in SQL.

        It could be indexes by variable name (:py:class:`Variable` or :py:class:`str`) or position in the tuple (:py:class:`int`).
        Unpacking also works.

        >>> store = Store()
        >>> store.add(Quad(NamedNode('http://example.com'), NamedNode('http://example.com/p'), Literal('1')))
        >>> solution = next(store.query('SELECT ?s ?p ?o WHERE { ?s ?p ?o }'))
        >>> solution[Variable('s')]
        <NamedNode value=http://example.com>
        >>> solution['s']
        <NamedNode value=http://example.com>
        >>> solution[0]
        <NamedNode value=http://example.com>
        >>> s, p, o = solution
        >>> s
        <NamedNode value=http://example.com>"""

    def __copy__(self, /) -> QuerySolution: ...
    def __deepcopy__(self, /, memo: typing.Any) -> QuerySolution: ...
    def __eq__(self, value: typing.Any, /) -> bool:
        """Return self==value."""

    def __ge__(self, value: typing.Any, /) -> bool:
        """Return self>=value."""

    def __getitem__(self, key: typing.Any, /) -> typing.Any:
        """Return self[key]."""

    def __gt__(self, value: typing.Any, /) -> bool:
        """Return self>value."""

    def __iter__(self, /) -> typing.Any:
        """Implement iter(self)."""

    def __le__(self, value: typing.Any, /) -> bool:
        """Return self<=value."""

    def __len__(self, /) -> int:
        """Return len(self)."""

    def __lt__(self, value: typing.Any, /) -> bool:
        """Return self<value."""

    def __ne__(self, value: typing.Any, /) -> bool:
        """Return self!=value."""

    def __repr__(self, /) -> str:
        """Return repr(self)."""

@typing.final
class QuerySolutions:
    """An iterator of :py:class:`QuerySolution` returned by a SPARQL ``SELECT`` query

    >>> store = Store()
    >>> store.add(Quad(NamedNode('http://example.com'), NamedNode('http://example.com/p'), Literal('1')))
    >>> list(store.query('SELECT ?s WHERE { ?s ?p ?o }'))
    [<QuerySolution s=<NamedNode value=http://example.com>>]"""

    variables: list[Variable]
    "the ordered list of all variables that could appear in the query results"

    def __init__(self, /) -> None:
        """An iterator of :py:class:`QuerySolution` returned by a SPARQL ``SELECT`` query

        >>> store = Store()
        >>> store.add(Quad(NamedNode('http://example.com'), NamedNode('http://example.com/p'), Literal('1')))
        >>> list(store.query('SELECT ?s WHERE { ?s ?p ?o }'))
        [<QuerySolution s=<NamedNode value=http://example.com>>]"""

    def serialize(
        self,
        /,
        output: typing.IO[bytes] | str | os.PathLike[str] | None = None,
        format: QueryResultsFormat | None = None,
    ) -> bytes | None:
        """Writes the query results into a file.

        It currently supports the following formats:

        * `XML <https://www.w3.org/TR/rdf-sparql-XMLres/>`_ (:py:attr:`QueryResultsFormat.XML`)
        * `JSON <https://www.w3.org/TR/sparql11-results-json/>`_ (:py:attr:`QueryResultsFormat.JSON`)
        * `CSV <https://www.w3.org/TR/sparql11-results-csv-tsv/>`_ (:py:attr:`QueryResultsFormat.CSV`)
        * `TSV <https://www.w3.org/TR/sparql11-results-csv-tsv/>`_ (:py:attr:`QueryResultsFormat.TSV`)

        :param output: The binary I/O object or file path to write to. For example, it could be a file path as a string or a file writer opened in binary mode with ``open('my_file.ttl', 'wb')``. If :py:const:`None`, a :py:class:`bytes` buffer is returned with the serialized content.
        :param format: the format of the query results serialization. If :py:const:`None`, the format is guessed from the file name extension.
        :raises ValueError: if the format is not supported.
        :raises OSError: if a system error happens while writing the file.

        >>> store = Store()
        >>> store.add(Quad(NamedNode('http://example.com'), NamedNode('http://example.com/p'), Literal('1')))
        >>> results = store.query("SELECT ?s ?p ?o WHERE { ?s ?p ?o }")
        >>> results.serialize(format=QueryResultsFormat.JSON)
        b'{"head":{"vars":["s","p","o"]},"results":{"bindings":[{"s":{"type":"uri","value":"http://example.com"},"p":{"type":"uri","value":"http://example.com/p"},"o":{"type":"literal","value":"1"}}]}}'"""

    def __iter__(self, /) -> typing.Any:
        """Implement iter(self)."""

    def __next__(self, /) -> typing.Any:
        """Implement next(self)."""

@typing.final
class QueryTriples:
    """An iterator of :py:class:`Triple` returned by a SPARQL ``CONSTRUCT`` or ``DESCRIBE`` query

    >>> store = Store()
    >>> store.add(Quad(NamedNode('http://example.com'), NamedNode('http://example.com/p'), Literal('1')))
    >>> list(store.query('CONSTRUCT WHERE { ?s ?p ?o }'))
    [<Triple subject=<NamedNode value=http://example.com> predicate=<NamedNode value=http://example.com/p> object=<Literal value=1 datatype=<NamedNode value=http://www.w3.org/2001/XMLSchema#string>>>]"""

    def __init__(self, /) -> None:
        """An iterator of :py:class:`Triple` returned by a SPARQL ``CONSTRUCT`` or ``DESCRIBE`` query

        >>> store = Store()
        >>> store.add(Quad(NamedNode('http://example.com'), NamedNode('http://example.com/p'), Literal('1')))
        >>> list(store.query('CONSTRUCT WHERE { ?s ?p ?o }'))
        [<Triple subject=<NamedNode value=http://example.com> predicate=<NamedNode value=http://example.com/p> object=<Literal value=1 datatype=<NamedNode value=http://www.w3.org/2001/XMLSchema#string>>>]"""

    def serialize(
        self, /, output: typing.IO[bytes] | str | os.PathLike[str] | None = None, format: RdfFormat | None = None
    ) -> bytes | None:
        """Writes the query results into a file.

        It currently supports the following formats:

        * `JSON-LD 1.0 <https://www.w3.org/TR/json-ld/>`_ (:py:attr:`RdfFormat.JSON_LD`)
        * `canonical <https://www.w3.org/TR/n-triples/#canonical-ntriples>`_ `N-Triples <https://www.w3.org/TR/n-triples/>`_ (:py:attr:`RdfFormat.N_TRIPLES`)
        * `N-Quads <https://www.w3.org/TR/n-quads/>`_ (:py:attr:`RdfFormat.N_QUADS`)
        * `Turtle <https://www.w3.org/TR/turtle/>`_ (:py:attr:`RdfFormat.TURTLE`)
        * `TriG <https://www.w3.org/TR/trig/>`_ (:py:attr:`RdfFormat.TRIG`)
        * `N3 <https://w3c.github.io/N3/spec/>`_ (:py:attr:`RdfFormat.N3`)
        * `RDF/XML <https://www.w3.org/TR/rdf-syntax-grammar/>`_ (:py:attr:`RdfFormat.RDF_XML`)

        :param output: The binary I/O object or file path to write to. For example, it could be a file path as a string or a file writer opened in binary mode with ``open('my_file.ttl', 'wb')``. If :py:const:`None`, a :py:class:`bytes` buffer is returned with the serialized content.
        :param format: the format of the RDF serialization. If :py:const:`None`, the format is guessed from the file name extension.
        :raises ValueError: if the format is not supported.
        :raises OSError: if a system error happens while writing the file.

        >>> store = Store()
        >>> store.add(Quad(NamedNode('http://example.com'), NamedNode('http://example.com/p'), Literal('1')))
        >>> results = store.query("CONSTRUCT { ?s ?p ?o } WHERE { ?s ?p ?o }")
        >>> results.serialize(format=RdfFormat.N_TRIPLES)
        b'<http://example.com> <http://example.com/p> "1" .\\n'"""

    def __iter__(self, /) -> typing.Any:
        """Implement iter(self)."""

    def __next__(self, /) -> typing.Any:
        """Implement next(self)."""

@typing.final
class RdfFormat:
    """RDF serialization formats.

    The following formats are supported:

    * `JSON-LD 1.0 <https://www.w3.org/TR/json-ld/>`_ (:py:attr:`RdfFormat.JSON_LD`)
    * `N-Triples <https://www.w3.org/TR/n-triples/>`_ (:py:attr:`RdfFormat.N_TRIPLES`)
    * `N-Quads <https://www.w3.org/TR/n-quads/>`_ (:py:attr:`RdfFormat.N_QUADS`)
    * `Turtle <https://www.w3.org/TR/turtle/>`_ (:py:attr:`RdfFormat.TURTLE`)
    * `TriG <https://www.w3.org/TR/trig/>`_ (:py:attr:`RdfFormat.TRIG`)
    * `N3 <https://w3c.github.io/N3/spec/>`_ (:py:attr:`RdfFormat.N3`)
    * `RDF/XML <https://www.w3.org/TR/rdf-syntax-grammar/>`_ (:py:attr:`RdfFormat.RDF_XML`)

    >>> RdfFormat.N3.media_type
    'text/n3'"""

    file_extension: str
    "the format `IANA-registered <https://tools.ietf.org/html/rfc2046>`_ file extension."
    iri: str
    "the format canonical IRI according to the `Unique URIs for file formats registry <https://www.w3.org/ns/formats/>`_."
    media_type: str
    "the format `IANA media type <https://tools.ietf.org/html/rfc2046>`_."
    name: str
    "the format name."
    supports_datasets: bool
    "if the formats supports `RDF datasets <https://www.w3.org/TR/rdf11-concepts/#dfn-rdf-dataset>`_ and not only `RDF graphs <https://www.w3.org/TR/rdf11-concepts/#dfn-rdf-graph>`_."
    supports_rdf_star: bool
    "if the format supports `RDF-star quoted triples <https://w3c.github.io/rdf-star/cg-spec/2021-12-17.html#dfn-quoted>`_."

    def __init__(self, /) -> None:
        """RDF serialization formats.

        The following formats are supported:

        * `JSON-LD 1.0 <https://www.w3.org/TR/json-ld/>`_ (:py:attr:`RdfFormat.JSON_LD`)
        * `N-Triples <https://www.w3.org/TR/n-triples/>`_ (:py:attr:`RdfFormat.N_TRIPLES`)
        * `N-Quads <https://www.w3.org/TR/n-quads/>`_ (:py:attr:`RdfFormat.N_QUADS`)
        * `Turtle <https://www.w3.org/TR/turtle/>`_ (:py:attr:`RdfFormat.TURTLE`)
        * `TriG <https://www.w3.org/TR/trig/>`_ (:py:attr:`RdfFormat.TRIG`)
        * `N3 <https://w3c.github.io/N3/spec/>`_ (:py:attr:`RdfFormat.N3`)
        * `RDF/XML <https://www.w3.org/TR/rdf-syntax-grammar/>`_ (:py:attr:`RdfFormat.RDF_XML`)

        >>> RdfFormat.N3.media_type
        'text/n3'"""

    @staticmethod
    def from_extension(extension: str) -> RdfFormat | None:
        """Looks for a known format from an extension.

        It supports some aliases.

        :param extension: the extension.
        :return: :py:class:`RdfFormat` if the extension is known or :py:const:`None` if not.

        >>> RdfFormat.from_extension("nt")
        <RdfFormat N-Triples>"""

    @staticmethod
    def from_media_type(media_type: str) -> RdfFormat | None:
        """Looks for a known format from a media type.

        It supports some media type aliases.
        For example, "application/xml" is going to return RDF/XML even if it is not its canonical media type.

        :param media_type: the media type.
        :return: :py:class:`RdfFormat` if the media type is known or :py:const:`None` if not.

        >>> RdfFormat.from_media_type("text/turtle; charset=utf-8")
        <RdfFormat Turtle>"""

    def __copy__(self, /) -> RdfFormat: ...
    def __deepcopy__(self, /, memo: typing.Any) -> RdfFormat: ...
    def __eq__(self, value: typing.Any, /) -> bool:
        """Return self==value."""

    def __ge__(self, value: typing.Any, /) -> bool:
        """Return self>=value."""

    def __gt__(self, value: typing.Any, /) -> bool:
        """Return self>value."""

    def __hash__(self, /) -> int:
        """Return hash(self)."""

    def __le__(self, value: typing.Any, /) -> bool:
        """Return self<=value."""

    def __lt__(self, value: typing.Any, /) -> bool:
        """Return self<value."""

    def __ne__(self, value: typing.Any, /) -> bool:
        """Return self!=value."""

    def __repr__(self, /) -> str:
        """Return repr(self)."""

    def __str__(self, /) -> str:
        """Return str(self)."""
    JSON_LD: RdfFormat = ...
    N3: RdfFormat = ...
    N_QUADS: RdfFormat = ...
    N_TRIPLES: RdfFormat = ...
    RDF_XML: RdfFormat = ...
    STREAMING_JSON_LD: RdfFormat = ...
    TRIG: RdfFormat = ...
    TURTLE: RdfFormat = ...

@typing.final
class Store:
    """RDF store.

    It encodes a `RDF dataset <https://www.w3.org/TR/rdf11-concepts/#dfn-rdf-dataset>`_ and allows to query it using SPARQL.
    It is based on the `RocksDB <https://rocksdb.org/>`_ key-value database.

    This store ensures the "repeatable read" isolation level: the store only exposes changes that have
    been "committed" (i.e. no partial writes) and the exposed state does not change for the complete duration
    of a read operation (e.g. a SPARQL query) or a read/write operation (e.g. a SPARQL update).

    The :py:class:`Store` constructor opens a read-write instance.
    To open a static read-only instance use :py:func:`Store.read_only`.

    :param path: the path of the directory in which the store should read and write its data. If the directory does not exist, it is created.
    If no directory is provided a temporary one is created and removed when the Python garbage collector removes the store.
    In this case, the store data are kept in memory and never written on disk.
    :raises OSError: if the target directory contains invalid data or could not be accessed.

    The :py:class:`str` function provides a serialization of the store in NQuads:

    >>> store = Store()
    >>> store.add(Quad(NamedNode('http://example.com'), NamedNode('http://example.com/p'), Literal('1'), NamedNode('http://example.com/g')))
    >>> str(store)
    '<http://example.com> <http://example.com/p> "1" <http://example.com/g> .\\n'"""

    def __init__(self, /, path: str | os.PathLike[str] | None = None) -> None:
        """RDF store.

        It encodes a `RDF dataset <https://www.w3.org/TR/rdf11-concepts/#dfn-rdf-dataset>`_ and allows to query it using SPARQL.
        It is based on the `RocksDB <https://rocksdb.org/>`_ key-value database.

        This store ensures the "repeatable read" isolation level: the store only exposes changes that have
        been "committed" (i.e. no partial writes) and the exposed state does not change for the complete duration
        of a read operation (e.g. a SPARQL query) or a read/write operation (e.g. a SPARQL update).

        The :py:class:`Store` constructor opens a read-write instance.
        To open a static read-only instance use :py:func:`Store.read_only`.

        :param path: the path of the directory in which the store should read and write its data. If the directory does not exist, it is created.
        If no directory is provided a temporary one is created and removed when the Python garbage collector removes the store.
        In this case, the store data are kept in memory and never written on disk.
        :raises OSError: if the target directory contains invalid data or could not be accessed.

        The :py:class:`str` function provides a serialization of the store in NQuads:

        >>> store = Store()
        >>> store.add(Quad(NamedNode('http://example.com'), NamedNode('http://example.com/p'), Literal('1'), NamedNode('http://example.com/g')))
        >>> str(store)
        '<http://example.com> <http://example.com/p> "1" <http://example.com/g> .\\n'"""

    def add(self, /, quad: Quad) -> None:
        """Adds a quad to the store.

        :param quad: the quad to add.
        :raises OSError: if an error happens during the quad insertion.

        >>> store = Store()
        >>> store.add(Quad(NamedNode('http://example.com'), NamedNode('http://example.com/p'), Literal('1'), NamedNode('http://example.com/g')))
        >>> list(store)
        [<Quad subject=<NamedNode value=http://example.com> predicate=<NamedNode value=http://example.com/p> object=<Literal value=1 datatype=<NamedNode value=http://www.w3.org/2001/XMLSchema#string>> graph_name=<NamedNode value=http://example.com/g>>]"""

    def add_graph(self, /, graph_name: NamedNode | BlankNode | DefaultGraph) -> None:
        """Adds a named graph to the store.

        :param graph_name: the name of the name graph to add.
        :raises OSError: if an error happens during the named graph insertion.

        >>> store = Store()
        >>> store.add_graph(NamedNode('http://example.com/g'))
        >>> list(store.named_graphs())
        [<NamedNode value=http://example.com/g>]"""

    def backup(self, /, target_directory: str | os.PathLike[str]) -> None:
        """Creates database backup into the `target_directory`.

        After its creation, the backup is usable using :py:class:`Store` constructor.
        like a regular pyxigraph database and operates independently from the original database.

        Warning: Backups are only possible for on-disk databases created by providing a path to :py:class:`Store` constructor.
        Temporary in-memory databases created without path are not compatible with the backup system.

        Warning: An error is raised if the ``target_directory`` already exists.

        If the target directory is in the same file system as the current database,
        the database content will not be fully copied
        but hard links will be used to point to the original database immutable snapshots.
        This allows cheap regular backups.

        If you want to move your data to another RDF storage system, you should have a look at the :py:func:`dump_dataset` function instead.

        :param target_directory: the directory name to save the database to.
        :raises OSError: if an error happens during the backup."""

    def bulk_extend(self, /, quads: collections.abc.Iterable[Quad]) -> None:
        """Adds a set of quads to this store without keeping them all into memory.

        It always writes new files to disk, the :py:func:`extend` method is also available for fast insertion of a small number of quads.

        :param quads: the quads to add.
        :raises OSError: if an error happens during the quad insertion.

        >>> store = Store()
        >>> store.bulk_extend([Quad(NamedNode('http://example.com'), NamedNode('http://example.com/p'), Literal('1'), NamedNode('http://example.com/g'))])
        >>> list(store)
        [<Quad subject=<NamedNode value=http://example.com> predicate=<NamedNode value=http://example.com/p> object=<Literal value=1 datatype=<NamedNode value=http://www.w3.org/2001/XMLSchema#string>> graph_name=<NamedNode value=http://example.com/g>>]"""

    def bulk_load(
        self,
        /,
        input: bytes | str | typing.IO[bytes] | typing.IO[str] | None = None,
        format: RdfFormat | None = None,
        *,
        path: str | os.PathLike[str] | None = None,
        base_iri: str | None = None,
        to_graph: NamedNode | BlankNode | DefaultGraph | None = None,
        lenient: bool = False,
    ) -> None:
        """Loads some RDF serialization into the store without keeping it all into memory.

        This function is designed to be as fast as possible on big files.

        It always writes new files to disk, the :py:func:`load` method is also available for fast insertion of small files.

        It currently supports the following formats:

        * `JSON-LD 1.0 <https://www.w3.org/TR/json-ld/>`_ (:py:attr:`RdfFormat.JSON_LD`)
        * `N-Triples <https://www.w3.org/TR/n-triples/>`_ (:py:attr:`RdfFormat.N_TRIPLES`)
        * `N-Quads <https://www.w3.org/TR/n-quads/>`_ (:py:attr:`RdfFormat.N_QUADS`)
        * `Turtle <https://www.w3.org/TR/turtle/>`_ (:py:attr:`RdfFormat.TURTLE`)
        * `TriG <https://www.w3.org/TR/trig/>`_ (:py:attr:`RdfFormat.TRIG`)
        * `N3 <https://w3c.github.io/N3/spec/>`_ (:py:attr:`RdfFormat.N3`)
        * `RDF/XML <https://www.w3.org/TR/rdf-syntax-grammar/>`_ (:py:attr:`RdfFormat.RDF_XML`)

        :param input: The :py:class:`str`, :py:class:`bytes` or I/O object to read from. For example, it could be the file content as a string or a file reader opened in binary mode with ``open('my_file.ttl', 'rb')``.
        :param format: the format of the RDF serialization. If :py:const:`None`, the format is guessed from the file name extension.
        :param path: The file path to read from. Replace the ``input`` parameter.
        :param base_iri: the base IRI used to resolve the relative IRIs in the file or :py:const:`None` if relative IRI resolution should not be done.
        :param to_graph: if it is a file composed of triples, the graph in which the triples should be stored. By default, the default graph is used.
        :param lenient: Skip some data validation during loading, like validating IRIs. This makes parsing faster at the cost of maybe ingesting invalid data.
        :raises ValueError: if the format is not supported.
        :raises SyntaxError: if the provided data is invalid.
        :raises OSError: if an error happens during a quad insertion or if a system error happens while reading the file.

        >>> store = Store()
        >>> store.bulk_load(input=b'<foo> <p> "1" .', format=RdfFormat.TURTLE, base_iri="http://example.com/", to_graph=NamedNode("http://example.com/g"))
        >>> list(store)
        [<Quad subject=<NamedNode value=http://example.com/foo> predicate=<NamedNode value=http://example.com/p> object=<Literal value=1 datatype=<NamedNode value=http://www.w3.org/2001/XMLSchema#string>> graph_name=<NamedNode value=http://example.com/g>>]"""

    def clear(self, /) -> None:
        """Clears the store by removing all its contents.

        :raises OSError: if an error happens during the operation.

        >>> store = Store()
        >>> store.add(Quad(NamedNode('http://example.com'), NamedNode('http://example.com/p'), Literal('1'), NamedNode('http://example.com/g')))
        >>> store.clear()
        >>> list(store)
        []
        >>> list(store.named_graphs())
        []"""

    def clear_graph(self, /, graph_name: NamedNode | BlankNode | DefaultGraph) -> None:
        """Clears a graph from the store without removing it.

        :param graph_name: the name of the name graph to clear.
        :raises OSError: if an error happens during the operation.

        >>> store = Store()
        >>> store.add(Quad(NamedNode('http://example.com'), NamedNode('http://example.com/p'), Literal('1'), NamedNode('http://example.com/g')))
        >>> store.clear_graph(NamedNode('http://example.com/g'))
        >>> list(store)
        []
        >>> list(store.named_graphs())
        [<NamedNode value=http://example.com/g>]"""

    def contains_named_graph(self, /, graph_name: NamedNode | BlankNode | DefaultGraph) -> bool:
        """Returns if the store contains the given named graph.

        :param graph_name: the name of the named graph.
        :raises OSError: if an error happens during the named graph lookup.

        >>> store = Store()
        >>> store.add_graph(NamedNode('http://example.com/g'))
        >>> store.contains_named_graph(NamedNode('http://example.com/g'))
        True"""

    def dump(
        self,
        /,
        output: typing.IO[bytes] | str | os.PathLike[str] | None = None,
        format: RdfFormat | None = None,
        *,
        from_graph: NamedNode | BlankNode | DefaultGraph | None = None,
        prefixes: dict[str, str] | None = None,
        base_iri: str | None = None,
    ) -> bytes | None:
        """Dumps the store quads or triples into a file.

        It currently supports the following formats:

        * `JSON-LD 1.0 <https://www.w3.org/TR/json-ld/>`_ (:py:attr:`RdfFormat.JSON_LD`)
        * `N-Triples <https://www.w3.org/TR/n-triples/>`_ (:py:attr:`RdfFormat.N_TRIPLES`)
        * `N-Quads <https://www.w3.org/TR/n-quads/>`_ (:py:attr:`RdfFormat.N_QUADS`)
        * `Turtle <https://www.w3.org/TR/turtle/>`_ (:py:attr:`RdfFormat.TURTLE`)
        * `TriG <https://www.w3.org/TR/trig/>`_ (:py:attr:`RdfFormat.TRIG`)
        * `N3 <https://w3c.github.io/N3/spec/>`_ (:py:attr:`RdfFormat.N3`)
        * `RDF/XML <https://www.w3.org/TR/rdf-syntax-grammar/>`_ (:py:attr:`RdfFormat.RDF_XML`)

        :param output: The binary I/O object or file path to write to. For example, it could be a file path as a string or a file writer opened in binary mode with ``open('my_file.ttl', 'wb')``. If :py:const:`None`, a :py:class:`bytes` buffer is returned with the serialized content.
        :param format: the format of the RDF serialization.  If :py:const:`None`, the format is guessed from the file name extension.
        :param from_graph: the store graph from which dump the triples. Required if the serialization format does not support named graphs. If it does supports named graphs the full dataset is written.
        :param prefixes: the prefixes used in the serialization if the format supports it.
        :param base_iri: the base IRI used in the serialization if the format supports it.
        :return: :py:class:`bytes` with the serialization if the ``output`` parameter is :py:const:`None`, :py:const:`None` if ``output`` is set.
        :raises ValueError: if the format is not supported or the `from_graph` parameter is not given with a syntax not supporting named graphs.
        :raises OSError: if an error happens during a quad lookup or file writing.

        >>> store = Store()
        >>> store.add(Quad(NamedNode('http://example.com'), NamedNode('http://example.com/p'), Literal('1')))
        >>> store.dump(format=RdfFormat.TRIG)
        b'<http://example.com> <http://example.com/p> "1" .\\n'

        >>> import io
        >>> store = Store()
        >>> store.add(Quad(NamedNode('http://example.com'), NamedNode('http://example.com/p'), Literal('1'), NamedNode('http://example.com/g')))
        >>> output = io.BytesIO()
        >>> store.dump(output, RdfFormat.TURTLE, from_graph=NamedNode("http://example.com/g"), prefixes={"ex": "http://example.com/"}, base_iri="http://example.com")
        >>> output.getvalue()
        b'@base <http://example.com> .\\n@prefix ex: </> .\\n<> ex:p "1" .\\n'"""

    def extend(self, /, quads: collections.abc.Iterable[Quad]) -> None:
        """Adds a set of quads to this store.

        Insertion is done in a transactional manner: either the full operation succeeds, or nothing is written to the database.
        The :py:func:`bulk_extend` method is also available for loading of a very large number of quads without having them all into memory.

        :param quads: the quads to add.
        :raises OSError: if an error happens during the quad insertion.

        >>> store = Store()
        >>> store.extend([Quad(NamedNode('http://example.com'), NamedNode('http://example.com/p'), Literal('1'), NamedNode('http://example.com/g'))])
        >>> list(store)
        [<Quad subject=<NamedNode value=http://example.com> predicate=<NamedNode value=http://example.com/p> object=<Literal value=1 datatype=<NamedNode value=http://www.w3.org/2001/XMLSchema#string>> graph_name=<NamedNode value=http://example.com/g>>]"""

    def flush(self, /) -> None:
        """Flushes all buffers and ensures that all writes are saved on disk.

        Flushes are automatically done using background threads but might lag a little bit.

        :raises OSError: if an error happens during the flush."""

    def load(
        self,
        /,
        input: bytes | str | typing.IO[bytes] | typing.IO[str] | None = None,
        format: RdfFormat | None = None,
        *,
        path: str | os.PathLike[str] | None = None,
        base_iri: str | None = None,
        to_graph: NamedNode | BlankNode | DefaultGraph | None = None,
        lenient: bool = False,
    ) -> None:
        """Loads RDF serialization into the store.

        Loads are applied in a transactional manner: either the full operation succeeds, or nothing is written to the database.
        The :py:func:`bulk_load` method is also available for loading big files without loading all its content into memory.

        Beware, the full file is loaded into memory.

        It currently supports the following formats:

        * `JSON-LD 1.0 <https://www.w3.org/TR/json-ld/>`_ (:py:attr:`RdfFormat.JSON_LD`)
        * `N-Triples <https://www.w3.org/TR/n-triples/>`_ (:py:attr:`RdfFormat.N_TRIPLES`)
        * `N-Quads <https://www.w3.org/TR/n-quads/>`_ (:py:attr:`RdfFormat.N_QUADS`)
        * `Turtle <https://www.w3.org/TR/turtle/>`_ (:py:attr:`RdfFormat.TURTLE`)
        * `TriG <https://www.w3.org/TR/trig/>`_ (:py:attr:`RdfFormat.TRIG`)
        * `N3 <https://w3c.github.io/N3/spec/>`_ (:py:attr:`RdfFormat.N3`)
        * `RDF/XML <https://www.w3.org/TR/rdf-syntax-grammar/>`_ (:py:attr:`RdfFormat.RDF_XML`)

        :param input: The :py:class:`str`, :py:class:`bytes` or I/O object to read from. For example, it could be the file content as a string or a file reader opened in binary mode with ``open('my_file.ttl', 'rb')``.
        :param format: the format of the RDF serialization. If :py:const:`None`, the format is guessed from the file name extension.
        :param path: The file path to read from. Replace the ``input`` parameter.
        :param base_iri: the base IRI used to resolve the relative IRIs in the file or :py:const:`None` if relative IRI resolution should not be done.
        :param to_graph: if it is a file composed of triples, the graph in which the triples should be stored. By default, the default graph is used.
        :param lenient: Skip some data validation during loading, like validating IRIs. This makes parsing faster at the cost of maybe ingesting invalid data.
        :raises ValueError: if the format is not supported.
        :raises SyntaxError: if the provided data is invalid.
        :raises OSError: if an error happens during a quad insertion or if a system error happens while reading the file.

        >>> store = Store()
        >>> store.load(input='<foo> <p> "1" .', format=RdfFormat.TURTLE, base_iri="http://example.com/", to_graph=NamedNode("http://example.com/g"))
        >>> list(store)
        [<Quad subject=<NamedNode value=http://example.com/foo> predicate=<NamedNode value=http://example.com/p> object=<Literal value=1 datatype=<NamedNode value=http://www.w3.org/2001/XMLSchema#string>> graph_name=<NamedNode value=http://example.com/g>>]"""

    def named_graphs(self, /) -> collections.abc.Iterator[NamedNode | BlankNode]:
        """Returns an iterator over all the store named graphs.

        :return: an iterator of the store graph names.
        :raises OSError: if an error happens during the named graphs lookup.

        >>> store = Store()
        >>> store.add(Quad(NamedNode('http://example.com'), NamedNode('http://example.com/p'), Literal('1'), NamedNode('http://example.com/g')))
        >>> list(store.named_graphs())
        [<NamedNode value=http://example.com/g>]"""

    def optimize(self, /) -> None:
        """Optimizes the database for future workload.

        Useful to call after a batch upload or another similar operation.

        :raises OSError: if an error happens during the optimization."""

    def quads_for_pattern(
        self,
        /,
        subject: NamedNode | BlankNode | Triple | None,
        predicate: NamedNode | None,
        object: NamedNode | BlankNode | Literal | Triple | None,
        graph_name: NamedNode | BlankNode | DefaultGraph | None = None,
    ) -> collections.abc.Iterator[Quad]:
        """Looks for the quads matching a given pattern.

        :param subject: the quad subject or :py:const:`None` to match everything.
        :param predicate: the quad predicate or :py:const:`None` to match everything.
        :param object: the quad object or :py:const:`None` to match everything.
        :param graph_name: the quad graph name. To match only the default graph, use :py:class:`DefaultGraph`. To match everything use :py:const:`None`.
        :return: an iterator of the quads matching the pattern.
        :raises OSError: if an error happens during the quads lookup.

        >>> store = Store()
        >>> store.add(Quad(NamedNode('http://example.com'), NamedNode('http://example.com/p'), Literal('1'), NamedNode('http://example.com/g')))
        >>> list(store.quads_for_pattern(NamedNode('http://example.com'), None, None, None))
        [<Quad subject=<NamedNode value=http://example.com> predicate=<NamedNode value=http://example.com/p> object=<Literal value=1 datatype=<NamedNode value=http://www.w3.org/2001/XMLSchema#string>> graph_name=<NamedNode value=http://example.com/g>>]"""

    def query(
        self,
        /,
        query: str,
        *,
        base_iri: str | None = None,
        prefixes: dict[str, str] | None = None,
        use_default_graph_as_union: bool = False,
        default_graph: NamedNode | BlankNode | DefaultGraph | list[NamedNode | BlankNode | DefaultGraph] | None = None,
        named_graphs: list[NamedNode | BlankNode] | None = None,
        substitutions: dict[Variable, NamedNode | BlankNode | Literal | Triple] | None = None,
        custom_functions: dict[NamedNode, typing.Callable[..., NamedNode | BlankNode | Literal | Triple | None]]
        | None = None,
        custom_aggregate_functions: dict[NamedNode, typing.Callable[[], AggregateFunctionAccumulator]] | None = None,
    ) -> QuerySolutions | QueryBoolean | QueryTriples:
        """Executes a `SPARQL 1.1 query <https://www.w3.org/TR/sparql11-query/>`_.

        :param query: the query to execute.
        :param base_iri: the base IRI used to resolve the relative IRIs in the SPARQL query or :py:const:`None` if relative IRI resolution should not be done.
        :param prefixes: a set of default prefixes to use during the SPARQL query parsing as a prefix name -> prefix IRI dictionary.
        :param use_default_graph_as_union: if the SPARQL query should look for triples in all the dataset graphs by default (i.e. without `GRAPH` operations). Disabled by default.
        :param default_graph: list of the graphs that should be used as the query default graph. By default, the store default graph is used.
        :param named_graphs: list of the named graphs that could be used in SPARQL `GRAPH` clause. By default, all the store named graphs are available.
        :param substitutions: dictionary of values variables should be substituted with. Substitution follows `RDF-dev SEP-0007 <https://github.com/w3c/sparql-dev/blob/main/SEP/SEP-0007/sep-0007.md>`_.
        :param custom_functions: dictionary of custom functions mapping function names to their definition. Custom functions takes for input some RDF term and returns a RDF term or :py:const:`None`.
        :param custom_aggregate_functions: dictionary of custom aggregate functions mapping function names to their definition. Custom aggregate functions take no input and return an object with two methods, `accumulate(self, term: Term)` to add a new term to the accumulator and `finish(self) -> Term` to return the accumulated result.
        :return: a :py:class:`bool` for ``ASK`` queries, an iterator of :py:class:`Triple` for ``CONSTRUCT`` and ``DESCRIBE`` queries and an iterator of :py:class:`QuerySolution` for ``SELECT`` queries.
        :raises SyntaxError: if the provided query is invalid.
        :raises OSError: if an error happens while reading the store.

        ``SELECT`` query:

        >>> store = Store()
        >>> store.add(Quad(NamedNode('http://example.com'), NamedNode('http://example.com/p'), Literal('1')))
        >>> [solution['s'] for solution in store.query('SELECT ?s WHERE { ?s ?p ?o }')]
        [<NamedNode value=http://example.com>]

        ``CONSTRUCT`` query:

        >>> store = Store()
        >>> store.add(Quad(NamedNode('http://example.com'), NamedNode('http://example.com/p'), Literal('1')))
        >>> list(store.query('CONSTRUCT WHERE { ?s ?p ?o }'))
        [<Triple subject=<NamedNode value=http://example.com> predicate=<NamedNode value=http://example.com/p> object=<Literal value=1 datatype=<NamedNode value=http://www.w3.org/2001/XMLSchema#string>>>]

        ``ASK`` query:

        >>> store = Store()
        >>> store.add(Quad(NamedNode('http://example.com'), NamedNode('http://example.com/p'), Literal('1')))
        >>> bool(store.query('ASK { ?s ?p ?o }'))
        True"""

    @staticmethod
    def read_only(path: str) -> Store:
        """Opens a read-only store from disk.

        Opening as read-only while having an other process writing the database is undefined behavior.

        :param path: path to the primary read-write instance data.
        :return: the opened store.
        :raises OSError: if the target directory contains invalid data or could not be accessed."""

    def remove(self, /, quad: Quad) -> None:
        """Removes a quad from the store.

        :param quad: the quad to remove.
        :raises OSError: if an error happens during the quad removal.

        >>> store = Store()
        >>> quad = Quad(NamedNode('http://example.com'), NamedNode('http://example.com/p'), Literal('1'), NamedNode('http://example.com/g'))
        >>> store.add(quad)
        >>> store.remove(quad)
        >>> list(store)
        []"""

    def remove_graph(self, /, graph_name: NamedNode | BlankNode | DefaultGraph) -> None:
        """Removes a graph from the store.

        The default graph will not be removed but just cleared.

        :param graph_name: the name of the name graph to remove.
        :raises OSError: if an error happens during the named graph removal.

        >>> store = Store()
        >>> store.add(Quad(NamedNode('http://example.com'), NamedNode('http://example.com/p'), Literal('1'), NamedNode('http://example.com/g')))
        >>> store.remove_graph(NamedNode('http://example.com/g'))
        >>> list(store.named_graphs())
        []"""

    def update(
        self,
        /,
        update: str,
        *,
        base_iri: str | None = None,
        prefixes: dict[str, str] | None = None,
        custom_functions: dict[NamedNode, typing.Callable[..., NamedNode | BlankNode | Literal | Triple | None]]
        | None = None,
        custom_aggregate_functions: dict[NamedNode, typing.Callable[[], AggregateFunctionAccumulator]] | None = None,
    ) -> None:
        """Executes a `SPARQL 1.1 update <https://www.w3.org/TR/sparql11-update/>`_.

        Updates are applied in a transactional manner: either the full operation succeeds, or nothing is written to the database.

        :param update: the update to execute.
        :param base_iri: the base IRI used to resolve the relative IRIs in the SPARQL update or :py:const:`None` if relative IRI resolution should not be done.
        :param prefixes: a set of default prefixes to use during the SPARQL query parsing as a prefix name -> prefix IRI dictionary.
        :param custom_functions: dictionary of custom functions mapping function names to their definition. Custom functions take for input some RDF terms and returns a RDF term or :py:const:`None`.
        :param custom_aggregate_functions: dictionary of custom aggregate functions mapping function names to their definition. Custom aggregate functions take no input and return an object with two methods, `accumulate(self, term: Term)` to add a new term to the accumulator and `finish(self) -> Term` to return the accumulated result.
        :raises SyntaxError: if the provided update is invalid.
        :raises OSError: if an error happens while reading the store.

        ``INSERT DATA`` update:

        >>> store = Store()
        >>> store.update('INSERT DATA { <http://example.com> <http://example.com/p> "1" }')
        >>> list(store)
        [<Quad subject=<NamedNode value=http://example.com> predicate=<NamedNode value=http://example.com/p> object=<Literal value=1 datatype=<NamedNode value=http://www.w3.org/2001/XMLSchema#string>> graph_name=<DefaultGraph>>]

        ``DELETE DATA`` update:

        >>> store = Store()
        >>> store.add(Quad(NamedNode('http://example.com'), NamedNode('http://example.com/p'), Literal('1')))
        >>> store.update('DELETE DATA { <http://example.com> <http://example.com/p> "1" }')
        >>> list(store)
        []

        ``DELETE`` update:

        >>> store = Store()
        >>> store.add(Quad(NamedNode('http://example.com'), NamedNode('http://example.com/p'), Literal('1')))
        >>> store.update('DELETE WHERE { <http://example.com> ?p ?o }')
        >>> list(store)
        []"""

    def __bool__(self, /) -> bool:
        """True if self else False"""

    def __contains__(self, key: typing.Any, /) -> bool:
        """Return bool(key in self)."""

    def __iter__(self, /) -> typing.Any:
        """Implement iter(self)."""

    def __len__(self, /) -> int:
        """Return len(self)."""

    def __str__(self, /) -> str:
        """Return str(self)."""

@typing.final
class Triple:
    """An RDF `triple <https://www.w3.org/TR/rdf11-concepts/#dfn-rdf-triple>`_.

    :param subject: the triple subject.
    :param predicate: the triple predicate.
    :param object: the triple object.

    The :py:class:`str` function provides a serialization compatible with NTriples, Turtle, and SPARQL:

    >>> str(Triple(NamedNode('http://example.com'), NamedNode('http://example.com/p'), Literal('1')))
    '<http://example.com> <http://example.com/p> "1"'

    A triple could also be easily destructed into its components:

    >>> (s, p, o) = Triple(NamedNode('http://example.com'), NamedNode('http://example.com/p'), Literal('1'))"""

    object: NamedNode | BlankNode | Literal | Triple
    "the triple object."
    predicate: NamedNode
    "the triple predicate."
    subject: NamedNode | BlankNode | Triple
    "the triple subject."

    def __init__(
        self,
        /,
        subject: NamedNode | BlankNode | Triple,
        predicate: NamedNode,
        object: NamedNode | BlankNode | Literal | Triple,
    ) -> None:
        """An RDF `triple <https://www.w3.org/TR/rdf11-concepts/#dfn-rdf-triple>`_.

        :param subject: the triple subject.
        :param predicate: the triple predicate.
        :param object: the triple object.

        The :py:class:`str` function provides a serialization compatible with NTriples, Turtle, and SPARQL:

        >>> str(Triple(NamedNode('http://example.com'), NamedNode('http://example.com/p'), Literal('1')))
        '<http://example.com> <http://example.com/p> "1"'

        A triple could also be easily destructed into its components:

        >>> (s, p, o) = Triple(NamedNode('http://example.com'), NamedNode('http://example.com/p'), Literal('1'))"""

    def __copy__(self, /) -> Triple: ...
    def __deepcopy__(self, /, memo: typing.Any) -> Triple: ...
    def __eq__(self, value: typing.Any, /) -> bool:
        """Return self==value."""

    def __ge__(self, value: typing.Any, /) -> bool:
        """Return self>=value."""

    def __getitem__(self, key: typing.Any, /) -> typing.Any:
        """Return self[key]."""

    def __getnewargs__(self, /) -> typing.Any: ...
    def __gt__(self, value: typing.Any, /) -> bool:
        """Return self>value."""

    def __hash__(self, /) -> int:
        """Return hash(self)."""

    def __iter__(self, /) -> typing.Any:
        """Implement iter(self)."""

    def __le__(self, value: typing.Any, /) -> bool:
        """Return self<=value."""

    def __len__(self, /) -> int:
        """Return len(self)."""

    def __lt__(self, value: typing.Any, /) -> bool:
        """Return self<value."""

    def __ne__(self, value: typing.Any, /) -> bool:
        """Return self!=value."""

    def __repr__(self, /) -> str:
        """Return repr(self)."""

    def __str__(self, /) -> str:
        """Return str(self)."""
    __match_args__: tuple[str, ...] = ("subject", "predicate", "object")

@typing.final
class Variable:
    """A SPARQL query variable.

    :param value: the variable name as a string.
    :raises ValueError: if the variable name is invalid according to the SPARQL grammar.

    The :py:class:`str` function provides a serialization compatible with SPARQL:

    >>> str(Variable('foo'))
    '?foo'"""

    value: str
    "the variable name."

    def __init__(self, /, value: str) -> None:
        """A SPARQL query variable.

        :param value: the variable name as a string.
        :raises ValueError: if the variable name is invalid according to the SPARQL grammar.

        The :py:class:`str` function provides a serialization compatible with SPARQL:

        >>> str(Variable('foo'))
        '?foo'"""

    def __copy__(self, /) -> Variable: ...
    def __deepcopy__(self, /, memo: typing.Any) -> Variable: ...
    def __eq__(self, value: typing.Any, /) -> bool:
        """Return self==value."""

    def __ge__(self, value: typing.Any, /) -> bool:
        """Return self>=value."""

    def __getnewargs__(self, /) -> typing.Any: ...
    def __gt__(self, value: typing.Any, /) -> bool:
        """Return self>value."""

    def __hash__(self, /) -> int:
        """Return hash(self)."""

    def __le__(self, value: typing.Any, /) -> bool:
        """Return self<=value."""

    def __lt__(self, value: typing.Any, /) -> bool:
        """Return self<value."""

    def __ne__(self, value: typing.Any, /) -> bool:
        """Return self!=value."""

    def __repr__(self, /) -> str:
        """Return repr(self)."""

    def __str__(self, /) -> str:
        """Return str(self)."""
    __match_args__: tuple[str, ...] = ("value",)

def parse(
    input: bytes | str | typing.IO[bytes] | typing.IO[str] | None = None,
    format: RdfFormat | None = None,
    *,
    path: str | os.PathLike[str] | None = None,
    base_iri: str | None = None,
    without_named_graphs: bool = False,
    rename_blank_nodes: bool = False,
    lenient: bool = False,
) -> QuadParser:
    """Parses RDF graph and dataset serialization formats.

    It currently supports the following formats:

    * `JSON-LD 1.0 <https://www.w3.org/TR/json-ld/>`_ (:py:attr:`RdfFormat.JSON_LD`)
    * `N-Triples <https://www.w3.org/TR/n-triples/>`_ (:py:attr:`RdfFormat.N_TRIPLES`)
    * `N-Quads <https://www.w3.org/TR/n-quads/>`_ (:py:attr:`RdfFormat.N_QUADS`)
    * `Turtle <https://www.w3.org/TR/turtle/>`_ (:py:attr:`RdfFormat.TURTLE`)
    * `TriG <https://www.w3.org/TR/trig/>`_ (:py:attr:`RdfFormat.TRIG`)
    * `N3 <https://w3c.github.io/N3/spec/>`_ (:py:attr:`RdfFormat.N3`)
    * `RDF/XML <https://www.w3.org/TR/rdf-syntax-grammar/>`_ (:py:attr:`RdfFormat.RDF_XML`)

    :param input: The :py:class:`str`, :py:class:`bytes` or I/O object to read from. For example, it could be the file content as a string or a file reader opened in binary mode with ``open('my_file.ttl', 'rb')``.
    :param format: the format of the RDF serialization. If :py:const:`None`, the format is guessed from the file name extension.
    :param path: The file path to read from. Replace the ``input`` parameter.
    :param base_iri: the base IRI used to resolve the relative IRIs in the file or :py:const:`None` if relative IRI resolution should not be done.
    :param without_named_graphs: Sets that the parser must fail when parsing a named graph.
    :param rename_blank_nodes: Renames the blank nodes identifiers from the ones set in the serialization to random ids. This allows avoiding identifier conflicts when merging graphs together.
    :param lenient: Skip some data validation during loading, like validating IRIs. This makes parsing faster at the cost of maybe ingesting invalid data.
    :return: an iterator of RDF triples or quads depending on the format.
    :raises ValueError: if the format is not supported.
    :raises SyntaxError: if the provided data is invalid.
    :raises OSError: if a system error happens while reading the file.

    >>> list(parse(input=b'<foo> <p> "1" .', format=RdfFormat.TURTLE, base_iri="http://example.com/"))
    [<Quad subject=<NamedNode value=http://example.com/foo> predicate=<NamedNode value=http://example.com/p> object=<Literal value=1 datatype=<NamedNode value=http://www.w3.org/2001/XMLSchema#string>> graph_name=<DefaultGraph>>]"""

def parse_query_results(
    input: bytes | str | typing.IO[bytes] | typing.IO[str] | None = None,
    format: QueryResultsFormat | None = None,
    *,
    path: str | os.PathLike[str] | None = None,
) -> QuerySolutions | QueryBoolean:
    """Parses SPARQL query results.

    It currently supports the following formats:

    * `XML <https://www.w3.org/TR/rdf-sparql-XMLres/>`_ (:py:attr:`QueryResultsFormat.XML`)
    * `JSON <https://www.w3.org/TR/sparql11-results-json/>`_ (:py:attr:`QueryResultsFormat.JSON`)
    * `TSV <https://www.w3.org/TR/sparql11-results-csv-tsv/>`_ (:py:attr:`QueryResultsFormat.TSV`)

    :param input: The :py:class:`str`, :py:class:`bytes` or I/O object to read from. For example, it could be the file content as a string or a file reader opened in binary mode with ``open('my_file.ttl', 'rb')``.
    :param format: the format of the query results serialization. If :py:const:`None`, the format is guessed from the file name extension.
    :param path: The file path to read from. Replaces the ``input`` parameter.
    :return: an iterator of :py:class:`QuerySolution` or a :py:class:`bool`.
    :raises ValueError: if the format is not supported.
    :raises SyntaxError: if the provided data is invalid.
    :raises OSError: if a system error happens while reading the file.

    >>> list(parse_query_results('?s\\t?p\\t?o\\n<http://example.com/s>\\t<http://example.com/s>\\t1\\n', QueryResultsFormat.TSV))
    [<QuerySolution s=<NamedNode value=http://example.com/s> p=<NamedNode value=http://example.com/s> o=<Literal value=1 datatype=<NamedNode value=http://www.w3.org/2001/XMLSchema#integer>>>]

    >>> parse_query_results('{"head":{},"boolean":true}', QueryResultsFormat.JSON)
    <QueryBoolean true>"""

def serialize(
    input: collections.abc.Iterable[Triple] | collections.abc.Iterable[Quad],
    output: typing.IO[bytes] | str | os.PathLike[str] | None = None,
    format: RdfFormat | None = None,
    *,
    prefixes: dict[str, str] | None = None,
    base_iri: str | None = None,
) -> bytes | None:
    """Serializes an RDF graph or dataset.

    It currently supports the following formats:

    * `JSON-LD 1.0 <https://www.w3.org/TR/json-ld/>`_ (:py:attr:`RdfFormat.JSON_LD`)
    * `canonical <https://www.w3.org/TR/n-triples/#canonical-ntriples>`_ `N-Triples <https://www.w3.org/TR/n-triples/>`_ (:py:attr:`RdfFormat.N_TRIPLES`)
    * `N-Quads <https://www.w3.org/TR/n-quads/>`_ (:py:attr:`RdfFormat.N_QUADS`)
    * `Turtle <https://www.w3.org/TR/turtle/>`_ (:py:attr:`RdfFormat.TURTLE`)
    * `TriG <https://www.w3.org/TR/trig/>`_ (:py:attr:`RdfFormat.TRIG`)
    * `N3 <https://w3c.github.io/N3/spec/>`_ (:py:attr:`RdfFormat.N3`)
    * `RDF/XML <https://www.w3.org/TR/rdf-syntax-grammar/>`_ (:py:attr:`RdfFormat.RDF_XML`)

    :param input: the RDF triples and quads to serialize.
    :param output: The binary I/O object or file path to write to. For example, it could be a file path as a string or a file writer opened in binary mode with ``open('my_file.ttl', 'wb')``. If :py:const:`None`, a :py:class:`bytes` buffer is returned with the serialized content.
    :param format: the format of the RDF serialization. If :py:const:`None`, the format is guessed from the file name extension.
    :param prefixes: the prefixes used in the serialization if the format supports it.
    :param base_iri: the base IRI used in the serialization if the format supports it.
    :return: :py:class:`bytes` with the serialization if the ``output`` parameter is :py:const:`None`, :py:const:`None` if ``output`` is set.
    :raises ValueError: if the format is not supported.
    :raises TypeError: if a triple is given during a quad format serialization or reverse.
    :raises OSError: if a system error happens while writing the file.

    >>> serialize([Triple(NamedNode('http://example.com'), NamedNode('http://example.com/p'), Literal('1'))], format=RdfFormat.TURTLE)
    b'<http://example.com> <http://example.com/p> "1" .\\n'

    >>> import io
    >>> output = io.BytesIO()
    >>> serialize([Triple(NamedNode('http://example.com'), NamedNode('http://example.com/p'), Literal('1'))], output, RdfFormat.TURTLE, prefixes={"ex": "http://example.com/"}, base_iri="http://example.com")
    >>> output.getvalue()
    b'@base <http://example.com> .\\n@prefix ex: </> .\\n<> ex:p "1" .\\n'"""
@typing.type_check_only
class AggregateFunctionAccumulator(typing.Protocol):
    def accumulate(self, element: NamedNode | BlankNode | Literal | Triple) -> None: ...
    def finish(self) -> NamedNode | BlankNode | Literal | Triple | None: ...
