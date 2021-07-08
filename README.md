## Description

linkurious is a [tortilla](https://github.com/tortilla/tortilla) based python wrapper around the
[Linkurious HTTP REST API](https://doc.linkurio.us/server-sdk/latest/apidoc/)
that allows users to remotely manage a Linkurious instance, performing the same tasks
that can be done through the web application.

This can be useful to:
- automate some of the most tedious tasks
- integrate the Linkurious instance within a wider multi-services application

[Linkurious Enterprise](https://linkurio.us/product/) is a copyrighted graph visualization and analysis platform,
that allows users to perform queries and build visualizations on multiple graph databases (Neo4j, CosmosDB, JanusGraph).

## Installation

Python versions from 3.6 are supported.

The package is hosted on pypi, and can be installed, for example using pip:

    pip install linkurious

## Usage
The package only has one class (and one exception), creating a `Linkurious` instance passing username and password
will connect to the instance. All following operations will be performed using the same user session. 

    from linkurious import Linkurious
    
    # login
    l = Linkurious(
        host='https://linkurious.example.org', 
        username='user@mail.org', 
        password='****', 
        debug=False
    )
    
    # query execution
    query = """
    MATCH (p:Person)-[i]-(m:Movie) where m.id=12
    return p, i, m
    limit 100
    """
    r = l.run_cypher_query(sourcekey='ae46c2f7', query=query)

    # nodes and edges are transformed before being sent to the visualization 
    r_nodes = [
        {
            'id': n.data.properties.id, 
            'data': {
                'geo': {}
            }, 
            'attributes': {
                'layoutable': True, 
                'x': 0, 'y': 0
            }
        } 
        for n in r['nodes']
    ]
    r_edges = [
        {
            'id': e.data.properties.id, 
            'attributes': {}
        } 
        for e in r.edges
    ]
    
    # visualization creation
    v = l.create_visualization(
        sourcekey='ae46c2f7', 
        title="Test from API", 
        nodes=r_nodes, 
        edges=r_edges
    )
    # server-side auto layouting, in order to spread the nodes
    l.patch_visualization(
        sourcekey='ae46c2f7', id=v.id, 
        do_layout=True,
    )
    
    # visualization styles are reset
    v.design.styles.node = []
    v.design.styles.edge = []
    l.patch_visualization(
        sourcekey='ae46c2f7', id=v.id,     
        visualization={'design': dict(v.design)},
        force_lock=True
    )

    # so that they can now be built anew
    # see https://doc.linkurio.us/server-sdk/latest/apidoc/#api-Visualization-createVisualization
    # and the links on INodeStyle and IEdgeStyle
    v.design.styles.node = [
        { ... }
    ] 
    v.design.styles.edges = [
        { ... }
    ] 
    # design is updated in the visualization
    # it must be transformed into a dict, as v is a Bunch (from tortilla),
    # and it may causes all sorts of bad requests responses from Linkurious API
    l.patch_visualization(
        sourcekey='ae46c2f7', id=v.id,     
        visualization={'design': dict(v.design)},
        force_lock=True
    )
    
    # the same can be done for 
    # - visualization filters (v.filters)
    # - visualization captions (v.nodeFields, v.edgeFields)
    

## Support

There is no guaranteed support available, but authors will try to keep up with issues 
and merge proposed solutions into the code base.

## Project Status
This project is funded by the European Commission and is currently (2021) under active developement.

## Contributing
In order to contribute to this project:
* verify that python 3.6+ is being used (or use [pyenv](https://github.com/pyenv/pyenv))
* verify or install [poetry](https://python-poetry.org/), to handle packages and dependencies in a leaner way, 
  with respect to pip and requirements
* clone the project `git clone git@github.com:openpolis/linkurious.git` 
* install the dependencies in the virtualenv, with `poetry install`,
  this will also install the dev dependencies
* develop 
* create a [pull request](https://docs.github.com/en/github/collaborating-with-pull-requests/proposing-changes-to-your-work-with-pull-requests/about-pull-requests)
* wait for the maintainers to review and eventually merge your pull request into the main repository

### Testing
As this is a tiny utility wrapper around an already tested and quite simple package (tortilla), 
there are no tests.

## Authors
Guglielmo Celata - guglielmo@openpolis.it

## Licensing
This package is released under an MIT License, see details in the LICENSE.txt file.
