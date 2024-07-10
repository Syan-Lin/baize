import sys
import json
from argparse import Namespace
from utils.workflow.graph import init_graph, Graph
from utils.resource import get_resource, ResourceType


def show_workflow(graph: Graph):
    import networkx as nx
    from asciinet import graph_to_ascii
    graph_vis = nx.Graph()
    edges = []
    for node in graph.nodes:
        graph_vis.add_node(node.name)
        for inp in node.input:
            edges.append((node.name, inp.name))
    graph_vis.add_edges_from(edges)
    ascii = graph_to_ascii(graph_vis)
    print(ascii)


def workflow_main(args: Namespace):
    workflow_name = ''
    if args.showworkflow:
        workflow_name = args.showworkflow[0]
    else:
        workflow_name = args.workflow[0]

    workflow_config = get_resource(ResourceType.workflow, workflow_name)
    workflow_config = json.loads(workflow_config)
    workflow = init_graph(workflow_config, args.log)

    if args.showworkflow:
        show_workflow(workflow)
        sys.exit()

    workflow.run()