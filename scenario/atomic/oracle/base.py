import py_trees

class Criterion(py_trees.behaviour.Behaviour):

    """
    Base class for all criteria used to evaluate a scenario for success/failure

    Important parameters (PUBLIC):
    - name: Name of the criterion
    - expected_value_success:    Result in case of success
                                 (e.g. max_speed, zero collisions, ...)
    - expected_value_acceptable: Result that does not mean a failure,
                                 but is not good enough for a success
    - actual_value: Actual result after running the scenario
    - test_status: Used to access the result of the criterion
    - optional: Indicates if a criterion is optional (not used for overall analysis)
    """

    def __init__(self,
                 name,
                 actor,
                 expected_value_success,
                 expected_value_acceptable=None,
                 optional=False,
                 terminate_on_failure=False):
        super(Criterion, self).__init__(name)
        self.logger.debug("%s.__init__()" % (self.__class__.__name__))
        self._terminate_on_failure = terminate_on_failure

        self.name = name
        self.actor = actor
        self.test_status = "INIT"
        self.expected_value_success = expected_value_success
        self.expected_value_acceptable = expected_value_acceptable
        self.actual_value = 0
        self.optional = optional
        self.list_traffic_events = []

    def initialise(self):
        """
        Initialise the criterion. Can be extended by the user-derived class
        """
        self.logger.debug("%s.initialise()" % (self.__class__.__name__))

    def terminate(self, new_status):
        """
        Terminate the criterion. Can be extended by the user-derived class
        """
        if (self.test_status == "RUNNING") or (self.test_status == "INIT"):
            self.test_status = "SUCCESS"

        self.logger.debug("%s.terminate()[%s->%s]" % (self.__class__.__name__, self.status, new_status))
