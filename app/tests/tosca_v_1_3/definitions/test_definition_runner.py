import unittest

import TestArtifact
import TestAttribute
import TestCapability
import TestConditionClause
import TestDescription
import TestEventFilter
import TestGroup
import TestInterface
import TestNodeFilter
import TestNotification
import TestNotificationImplementation
import TestOperation
import TestOperationImplementation
import TestProperty
import TestPropertyFilter
import TestRequirement
import TestSchema
import TestTrigger
import TestWorkflowPrecondition
import TestWorkflowStep

definitionTestSuite = unittest.TestSuite()
definitionTestSuite.addTest(unittest.makeSuite(TestArtifact.TestArtifact))
definitionTestSuite.addTest(unittest.makeSuite(TestAttribute.TestAttribute))
definitionTestSuite.addTest(unittest.makeSuite(TestCapability.TestCapability))
definitionTestSuite.addTest(unittest.makeSuite(TestConditionClause.TestConditionClause))
definitionTestSuite.addTest(unittest.makeSuite(TestDescription.TestDescription))
definitionTestSuite.addTest(unittest.makeSuite(TestEventFilter.TestEventFilter))
definitionTestSuite.addTest(unittest.makeSuite(TestGroup.TestGroup))
definitionTestSuite.addTest(unittest.makeSuite(TestInterface.TestInterface))
definitionTestSuite.addTest(unittest.makeSuite(TestNodeFilter.TestNodeFilter))
definitionTestSuite.addTest(unittest.makeSuite(TestNotification.TestNotification))
definitionTestSuite.addTest(unittest.makeSuite(TestNotificationImplementation.TestNotificationImplementation))
definitionTestSuite.addTest(unittest.makeSuite(TestOperation.TestOperation))
definitionTestSuite.addTest(unittest.makeSuite(TestOperationImplementation.TestOperationImplementation))
definitionTestSuite.addTest(unittest.makeSuite(TestConditionClause.TestConditionClause))
definitionTestSuite.addTest(unittest.makeSuite(TestProperty.TestProperty))
definitionTestSuite.addTest(unittest.makeSuite(TestPropertyFilter.TestPropertyFilter))
definitionTestSuite.addTest(unittest.makeSuite(TestRequirement.TestRequirement))
definitionTestSuite.addTest(unittest.makeSuite(TestSchema.TestSchema))
definitionTestSuite.addTest(unittest.makeSuite(TestTrigger.TestTrigger))
definitionTestSuite.addTest(unittest.makeSuite(TestWorkflowPrecondition.TestWorkflowPrecondition))
definitionTestSuite.addTest(unittest.makeSuite(TestWorkflowStep.TestWorkflowStep))

runner = unittest.TextTestRunner(verbosity=2)
runner.run(definitionTestSuite)
