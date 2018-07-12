from pacman.model.graphs.application import ApplicationEdge


class ConnectionLearningRuleApplicationEdge(
        ApplicationEdge):

    __slots__ = [
        # the learning rule associated with this application edge
        "_learning_rule",
        #
        "_input_port",
        #
        "_reception_parameters"
    ]

    def __init__(self, pre_vertex, post_vertex, learning_rule, input_port,
                 reception_parameters):
        ApplicationEdge.__init__(
            self, pre_vertex=pre_vertex, post_vertex=post_vertex)
        self._learning_rule = learning_rule
        self._input_port = input_port
        self._reception_parameters = reception_parameters

    @property
    def input_port(self):
        return self._input_port

    @property
    def reception_parameters(self):
        return self._reception_parameters

    @property
    def learning_rule(self):
        return self._learning_rule