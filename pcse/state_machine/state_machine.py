"""State machine example."""


class State:
    """Base but concrete class for state machines / workflows.

    Initialize with a class representing initial state, i.e.:

        workflow = State(InitialState)
        i = 0
        while workflow.next():
            workflow.do(i:=i+1)
    """

    def __init__(self, initial_state):
        self.next_state(initial_state)

    def next_state(self, state):
        self.__class__ = state

    def do(self, ctx):
        raise NotImplementedError()

    def next(self):
        return self.__class__ != State


#
# First state machine / workflow
#

class Initial(State):
    def do(self, ctx):
        print(f'state: INIT, with ctx = {ctx}')
        self.next_state(Fork)


class Fork(State):
    def do(self, ctx):
        print(f'state: FORK, with ctx = {ctx}')
        if ctx > 2:
            self.next_state(Up)
        else:
            self.next_state(Down)


class Up(State):
    def do(self, ctx):
        print(f'state: UP  , with ctx = {ctx}')
        self.next_state(Fork)


class Down(State):
    def do(self, ctx):
        print(f'state: DOWN, with ctx = {ctx}')
        self.next_state(Fork)


#
# Second state machine / workflow
#


class AddA(State):
    def do(self, ctx):
        self.next_state(AddB)
        return ctx+'A'


class AddB(State):
    def do(self, ctx):
        self.next_state(AddC)
        return ctx+'B'


class AddC(State):
    def do(self, ctx):
        self.next_state(State)  # stop that workflow
        return ctx+'C'


# vim: sw=4:et:ai
