from pcse.state_machine.state_machine import State, Initial, AddA


def test_workflow_1():
    workflow = State(AddA)
    s = ''
    while workflow.next():
        s = workflow.do(s)

    assert s == 'ABC'


def test_workflow_2():
    s = State(initial_state=Initial)
    for i in range(5):
        s.do(i)

    assert True


# vim: sw=4:et:ai
