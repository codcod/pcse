# State machine

Base class for a state machine / workflow.

```python
class State:
    def __init__(self, initial_state):
        self.next_state(initial_state)

    def next_state(self, state):
        self.__class__ = state

    def do(self, ctx):
        raise NotImplementedError()
```

Each state inherits after base:

```python
class StateOne(State):
    def do(self, ctx):
        print('one')
        self.next_state(StateTwo)

class StateTwo(State):
    def do(self, ctx):
        print('two')
        self.next_state(StateOne)
```

Sample usage:

```python
s = State(initial_state=StateOne)
for i in range(5):
    s.do(i)
```

A workflow-like calling structure can be achived by adding this "stop" method
to the base type:

```python
    def next(self):
        return self.__class__ != Stat
```

When a state redirects to base it means workflow ends:

```python
class StateTwo(State):
    def do(self, ctx):
        print('two')
        self.next_state(State)
```

Usage in this case could be:

```python
workflow = State(StateOne)
while workflow.next():
    workflow.do(None)
```
