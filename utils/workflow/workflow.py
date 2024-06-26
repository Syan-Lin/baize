import os
import json
from argparse import Namespace
from utils.workflow.graph import init_graph
from utils.resource import get_resource, ResourceType


def workflow_main(args: Namespace):
    workflow_config = get_resource(ResourceType.workflow, args.workflow[0])
    workflow = init_graph(workflow_config, args.log)
    workflow.run()