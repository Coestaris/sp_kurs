using CourseWork.DataStructures;
using System.Collections.Generic;
using System.Linq;

namespace CourseWork.LexicalAnalysis
{
    public class Lexeme
    {
        public Assembly ParrentAssembly { get; }
        public List<Token> Tokens { get; private set; }

        private void AssignUserSegmentsAndLabels(out Error error)
        {
            error = null;

            // *something* SEGMENT
            if (Tokens.Count == 2 &&
                Tokens[0].Type == TokenType.Identifier &&
                Tokens[1].Type == TokenType.SegmentKeyword)
            {
                Tokens[0].Type = TokenType.UserSegment;
                if (ParrentAssembly.UserSegments.FindIndex(p => p.Name == Tokens[0].StringValue) != -1)
                {
                    error = new Error(ErrorType.SameUserSegmentAlreadyExists, Tokens[0]);
                    return;
                }

                ParrentAssembly.UserSegments.Add(new UserSegment() { 
                    OpenToken = Tokens[0], 
                });
            }

            // *something* ENDS
            if (Tokens.Count == 2 &&
                Tokens[0].Type == TokenType.Identifier &&
                Tokens[1].Type == TokenType.EndsKeyword)
            {
                Tokens[0].Type = TokenType.UserSegment;
                var structure = ParrentAssembly.UserSegments.Find(p => p.Name == Tokens[0].StringValue);

                // ���� �� ������� ��������� ������� �� ��������� ���������
                if(structure == null)
                {
                    error = new Error(ErrorType.UserSegmentNamesMismatch, Tokens[0]);
                    return;
                }
                
                // ���� ��������� ������� �� ��������� ��������� ��� �������
                if (structure.Closed)
                {
                    error = new Error(ErrorType.SpecifiedUserSegmentAlreadyClosed, Tokens[0]);
                    return;
                }

                structure.CloseToken = Tokens[0];
            }

            // *something*:
            if (Tokens[0].Type == TokenType.Identifier &&
                Tokens[1].Type == TokenType.Symbol && 
                Tokens[1].StringValue == ":")
            {
                Tokens[0].Type = TokenType.Label;
                if (ParrentAssembly.UserLabels.FindIndex(p => p.StringValue == Tokens[0].StringValue) != -1)
                {
                    error = new Error(ErrorType.SameLabelAreadyExists, Tokens[0]);
                    return;
                }
                ParrentAssembly.UserLabels.Add(Tokens[0]);
            }
        }

        public Lexeme(Assembly assembly) 
        {
            ParrentAssembly = assembly;
        }

        public void SetTokens(List<Token> tokens, out Error error)
        {
            error = null;
            Tokens = tokens;
            AssignUserSegmentsAndLabels(out error);
            if (error != null) return;

            //todo?
        }

        public override string ToString()
        {
            return $"[{string.Join(", ", Tokens.Select(p => "\"" + p.ToString()+ "\""))}]";
        }
    }
}