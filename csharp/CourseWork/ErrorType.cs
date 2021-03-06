﻿namespace CourseWork
{
    public enum ErrorType
    {
        SameUserSegmentAlreadyExists,
        UnclosedQuotes,
        UnknownToken,
        SameLabelAlreadyExists,
        UserSegmentNamesMismatch,
        SpecifiedUserSegmentAlreadyClosed,
        UnclosedSegment,
        UnopenedSegment,
        MissingEndKeyword,
        NotSupportedExpressionType,
        WrongTokenAsOperand,
        WrongDirectiveFormat,
        IncorrectInstructionTypes,
        UnexpectedDirective,
        SameEquAlreadyExists,
        SameVarAlreadyExists,
        UnknownInstruction,
        ExpectedNumberOrString,
        UndefinedReference,
        UnexpectedToken,
        VariableExpected,
        Register32Expected,
        WrongRegisterAtIndex
    }
}