using System.Collections.Generic;

namespace cheats
{
    public class Operation
    {
        public readonly string Name; // The operation code
        public string Pattern; // The regex pattern to match the command arguments

        public override string ToString() => $"{Name} ({Pattern})";

        public Operation(string name, string pattern = @".*")
        {
            Name = name;
            Pattern = pattern;
        }

        public bool Matches(string command)
        {
            // Check if the command matches the pattern
            return System.Text.RegularExpressions.Regex.IsMatch(command, Pattern);
        }

        public static readonly Dictionary<string, Operation> CommandMap = new Dictionary<string, Operation>
        {
            { "read", new Operation("READ", @"[A-Z]+ 0x[0-9A-F]+") },
        };
    };

}