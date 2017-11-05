from functools import singledispatch
from reasoner.node_types import node_types

class KNode():
    """Used as the node object in KnowledgeGraph.
    
    Instances of this class can be passed to WorldGraph/greent as query subjects/objects."""
    def __init__(self,identifier,node_type,label=None):
        self.identifier = identifier
        self.label = label
        if node_type not in node_types:
            raise ValueError( 'node_type {} unsupported.'.format( node_type ) )
        self.node_type = node_type
        self.properties = {}
        self.synonyms = []
    def add_synonym(self,synonymous_node):
        """Merge anther KNode (representing a synonym) into this KNode."""
        self.synonyms.append(synonymous_node.identifier)
        for propkey in synonymous_node.properties:
            if propkey in self.properties:
                #TODO: this is messy
                self.properties[ propkey ] = [ self.properties[propkey], syonymous_node.properties[propkey] ]
            else:
                self.properties[ propkey ] = syonymous_node.properties[propkey]
    def __repr__(self):
        #return "KNode(id={0},type={1})".format (self.identifier, self.node_type)
        return "N({0},t={1})".format (self.identifier, self.node_type)
    def __str__(self):
        return self.__repr__()
    #Is using identifier sufficient?  Probably need to be a bit smarter.
    def __hash__(self):
        """Class needs __hash__ in order to be used as a node in networkx"""
        return self.identifier.__hash__()
    def __eq__(x,y):
        return x.identifier == y.identifier
    def to_json(self):
        """Used to serialize a node to JSON."""
        j = { 'identifier': self.identifier, \
              'node_type' : self.node_type }
        if self.layer_number is not None:
            j['layer_number'] = self.layer_number
        for key in self.properties:
            j[key] = self.properties[key]
        return j
    def get_shortname(self):
        """Return a short user-readable string suitable for display in a list"""
        if self.label is not None:
            return '%s (%s)' % (self.label, self.identifier)
        return self.identifier
    def get_exportable(self):
        """Returns information to make a simpler node in networkx.  Helps with finicky graphml writer"""
        export_properties = { 'identifier'   : self.identifier, \
                              'node_type'    : self.node_type,  \
                              'layer_number' : self.layer_number }
        if self.label is not None:
            export_properties['label'] = self.label
        for key in self.properties:
            export_properties[key] = 'See JSON for details'
        return self.get_shortname(), export_properties


class KEdge():
    """Used as the edge object in KnowledgeGraph.

    Instances of this class should be returned from greenT"""
    def __init__(self, edge_source, edge_function, properties = None, is_synonym=False):
        self.edge_source = edge_source
        self.source_node = None
        self.target_node = None
        self.edge_function = edge_function
        if properties is not None:
            self.properties = properties
        else:
            self.properties = {}
        self.is_synonym = is_synonym
    def __key(self):
        return (self.source_node, self.target_node, self.edge_source, self.edge_function)
    def __eq__(x,y):
        return x.__key() == y.__key()
    def __hash__(self):
        return hash(self.__key())
    def long_form (self):
        return "E(src={0},type={1},srcn={2},destn={3})".format (self.edge_source, self.edge_function,
                                                                self.source_node, self.target_node)
    def __repr__(self):
        #return "KEdge(edge_source={0},edge_type={1})".format (self.edge_source, self.edge_type)
        return self.long_form ()
#        return "E(src={0},type={1})".format (self.edge_source, self.edge_type)
    def __str__(self):
        return self.__repr__()
    def to_json(self):
        """Used to serialize a node to JSON."""
        j = { 'edge_source'     : self.edge_source, \
              'edge_function'   : self.edge_function, \
              'is_synonym'      : self.is_synonym }
        for key in self.properties:
            j[key] = self.properties[key]
        return j
    def get_exportable(self):
        """Returns information to make a simpler node in networkx.  Helps with finicky graphml writer"""
        export_properties = { 'edge_source'     : self.edge_source, \
              'edge_function'   : self.edge_function, \
              'is_synonym'      : self.is_synonym }
        for key in self.properties:
            export_properties[key] = 'See JSON for details'
        return export_properties

  


##
# We want to be able to serialize our knowledge graph to json.  That means being able to serialize KNode/KEdge.
# We could sublcass JSONEncoder (and still might), but for now, this set of functions allows the default
# encoder to find the functions that return serializable versions of KNode and KEdge
##

@singledispatch
def elements_to_json(x):
    """Used by default in dumping JSON. For use by json.dump; should not usually be called by users."""
    #The singledispatch decorator allows us to register serializers in our edge and node classes.
    return str(x)
 
@elements_to_json.register(KNode)
def node_to_json(knode):
    """Routes JSON serialization requests to KNode member function.  Not for external use."""
    return knode.to_json()

@elements_to_json.register(KEdge)
def node_to_json(kedge):
    """Routes JSON serialization requests to KEdge member function.  Not for external use."""
    return kedge.to_json()

# END JSON STUFF

