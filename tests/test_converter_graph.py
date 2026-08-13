from acacore.models.file import BaseFile

from convertool.converters import converters
from convertool.converters import ConvertersGraph


def test_converter_graph():
    graph = ConvertersGraph.from_conversers(converters)

    graph.filter_conversion_graph(requires_file_classes=[BaseFile])

    for paths in graph.graph.values():
        for path in paths:
            for edge in path.branch:
                assert not edge.converter.requires_file_classes or BaseFile in edge.converter.requires_file_classes

    for [name, _], paths in graph["html":].graph.items():
        assert name == "html"
        for path in paths:
            assert path[0].name == "html"

    for [_, output], paths in graph[:"html"].graph.items():
        assert output == "html"
        for path in paths:
            assert "html" in path[-1].converter.outputs

    for [name, _], paths in graph["html"::"document"].graph.items():
        assert name == "html"
        for path in paths:
            assert path.has_step("document")

    for [_, output], paths in graph[:"tiff":"document"].graph.items():
        assert output == "tiff"
        for path in paths:
            assert path.has_step("document")

    for [name, output], paths in graph["msg":"tiff":"document"].graph.items():
        assert name == "msg"
        assert output == "tiff"
        for path in paths:
            assert path.has_step("document")
