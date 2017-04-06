import unittest

from trajtracker.events import *


class MyOperation(object):

    def __init__(self):
        self.n_invoked = 0

    def __call__(self, time_in_trial, time_in_session):
        self.n_invoked += 1
        self.time_in_trial = time_in_trial
        self.time_in_session = time_in_session



class EventManagerTests(unittest.TestCase):

    #=================================================================================
    #   Registering and unregistering
    #=================================================================================

    #----------------------------------------------------------
    def test_register_event_sensitive_object(self):
        class ESO(object):
            def __init__(self):
                self.n_reg = 0
            def on_registered(self, event_manager):
                self.n_reg += 1
                self.em = event_manager

        em = EventManager()
        eso = ESO()
        em.register(eso)
        self.assertEqual(1, eso.n_reg)
        self.assertEqual(em, eso.em)

    #----------------------------------------------------------
    def test_unregister_operation(self):

        em = EventManager()
        op = MyOperation()
        event = Event("TEST_EVENT")
        op_id = em.register_operation(event, op, False)

        em.unregister_operation(op_id)
        self.assertEqual(0, len(em._operations_by_id))

        em.dispatch_event(event, 0, 0)
        self.assertEqual(0, op.n_invoked)

    #----------------------------------------------------------
    def test_unregister_operation_while_pending(self):

        em = EventManager()
        op = MyOperation()
        event = Event("TEST_EVENT")
        op_id = em.register_operation(event+1, op, False)

        em.dispatch_event(event, 0, 0)

        em.unregister_operation(op_id)
        self.assertEqual(0, len(em._operations_by_id))
        self.assertEqual(0, len(em._pending_operations))

        em.on_frame(0, 2)
        self.assertEqual(0, op.n_invoked)


    #=================================================================================
    #   Invoking operations with offset=0
    #=================================================================================


    #----------------------------------------------------------
    def test_dont_invoke_on_irrelevant_event(self):

        em = EventManager()
        op = MyOperation()
        event = Event("TEST_EVENT")
        em.register_operation(event, op, False)

        em.dispatch_event(Event("STAM"), 0, 0)
        self.assertEqual(0, op.n_invoked)
        self.assertEqual(1, len(em._operations_by_id))


    #----------------------------------------------------------
    def test_invoke_one_time_operation(self):

        em = EventManager()
        op = MyOperation()
        event = Event("TEST_EVENT")
        em.register_operation(event, op, False)

        em.dispatch_event(event, 0, 0)
        self.assertEqual(1, op.n_invoked)
        self.assertEqual(0, len(em._operations_by_id))
        self.assertEqual(0, get_n_ops_by_event(em))

        em.dispatch_event(event, 0, 0)
        self.assertEqual(1, op.n_invoked)


    #----------------------------------------------------------
    def test_invoke_recurring_operation(self):

        em = EventManager()
        op = MyOperation()
        event = Event("TEST_EVENT")
        em.register_operation(event, op, True)

        em.dispatch_event(event, 0, 0)
        self.assertEqual(1, op.n_invoked)

        em.dispatch_event(event, 0, 0)
        self.assertEqual(2, op.n_invoked)

        self.assertEqual(1, len(em._operations_by_id))
        self.assertEqual(1, get_n_ops_by_event(em))


    #=================================================================================
    #   Invoking operations with offset > 0
    #=================================================================================

    #----------------------------------------------------------
    def test_invoke_one_time_operation_delayed(self):

        em = EventManager()
        op = MyOperation()
        event = Event("TEST_EVENT")
        em.register_operation(event+3, op, False)

        #-- Dispatch an event
        em.dispatch_event(event, 0, 0)
        self.assertEqual(0, op.n_invoked)

        #-- Too little time after the event
        em.on_frame(0, 1)
        self.assertEqual(0, op.n_invoked)

        # enough time after the event
        em.on_frame(0, 3)
        self.assertEqual(1, op.n_invoked)

        #-- Dispatch a 2nd event
        em.dispatch_event(event, 0, 0)
        self.assertEqual(1, op.n_invoked)

        # even after lots of time nothing should be invoked
        em.on_frame(0, 10)
        self.assertEqual(1, op.n_invoked)


    #----------------------------------------------------------
    def test_invoke_recurring_operation_delayed(self):

        em = EventManager()
        op = MyOperation()
        event = Event("TEST_EVENT")
        em.register_operation(event+3, op, True)

        #-- Dispatch an event
        em.dispatch_event(event, 0, 0)
        self.assertEqual(0, op.n_invoked)

        #-- Too little time after the event
        em.on_frame(0, 1)
        self.assertEqual(0, op.n_invoked)

        # enough time after the event
        em.on_frame(0, 3)
        self.assertEqual(1, op.n_invoked)

        #-- Dispatch a 2nd event
        em.dispatch_event(event, 0, 0)
        self.assertEqual(1, op.n_invoked)

        em.on_frame(0, 10)
        self.assertEqual(2, op.n_invoked)


    #----------------------------------------------------------
    def test_invoke_recurring_operation_delayed_simultaneous(self):
        #
        # Dispatch an event twice, in very short intervals; the operation should still be invoked twice
        #

        em = EventManager()
        op = MyOperation()
        event = Event("TEST_EVENT")
        em.register_operation(event+3, op, True)

        #-- Dispatch event#1
        em.dispatch_event(event, 0, 0)
        self.assertEqual(0, op.n_invoked)

        #-- Dispatch event#2
        em.dispatch_event(event, 0, 1)
        self.assertEqual(0, op.n_invoked)

        #-- Check invocations
        em.on_frame(0, 10)
        self.assertEqual(2, op.n_invoked)


    #----------------------------------------------------------
    def test_cancel_pending(self):

        em = EventManager()
        op = MyOperation()
        event = Event("TEST_EVENT")
        em.register_operation(event+3, op, False)

        em.dispatch_event(event, 0, 0)

        em.cancel_pending_operations()

        em.on_frame(0, 3)
        self.assertEqual(0, op.n_invoked)



    #----------------------------------------------------------
    def test_invoke_several_delayed_operations_a(self):

        em = EventManager()
        op1 = MyOperation()
        op2 = MyOperation()
        event1 = Event("Event1")
        event2 = Event("Event2")
        em.register_operation(event1+10, op1, True)
        em.register_operation(event2+20, op2, True)

        # -- Attempt#1: event1 dispatched first, invoked first

        em.dispatch_event(event1, 0, 0)
        em.dispatch_event(event2, 0, 5)

        em.on_frame(0, 15)
        self.assertEqual(1, op1.n_invoked)
        self.assertEqual(0, op2.n_invoked)

        em.on_frame(0, 25)
        self.assertEqual(1, op2.n_invoked)

        # -- Attempt#2: event1 dispatched last, invoked first

        op1.n_invoked = 0
        op2.n_invoked = 0

        em.dispatch_event(event2, 0, 0)
        em.dispatch_event(event1, 0, 5)

        em.on_frame(0, 15)
        self.assertEqual(1, op1.n_invoked)
        self.assertEqual(0, op2.n_invoked)

        em.on_frame(0, 25)
        self.assertEqual(1, op2.n_invoked)


    #=================================================================================
    #   Event heirarchy
    #=================================================================================

    #----------------------------------------------------------
    def test_invoke_extended_event(self):

        em = EventManager()
        op = MyOperation()
        base1 = Event("BASE1")
        base2 = Event("BASE2", extends=base1)
        event = Event("TEST_EVENT", extends=base2)

        em.register_operation(base1, op, True)

        em.dispatch_event(event, 0, 0)
        self.assertEqual(1, op.n_invoked)



#----------------------------------------------------------
def get_n_ops_by_event(event_manager):
    return sum([len(ops) for ops in event_manager._operations_by_event.values()])


if __name__ == '__main__':
    unittest.main()
