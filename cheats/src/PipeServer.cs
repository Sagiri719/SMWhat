using System;
using System.IO;
using System.IO.Pipes;
using System.Linq;
using System.Threading.Tasks;
using BizHawk.Common.CollectionExtensions;

namespace cheats
{
    struct PipeRequest
    {
        public Operation Command;
        public string[] Arguments;

        public PipeRequest(string command, params string[] arguments)
        {
            Command = Operation.CommandMap.ContainsKey(command) ? Operation.CommandMap[command] : throw new ArgumentException($"Unknown command: {command}");
            Arguments = arguments;

            if (command != null && !Command.Matches(String.Join(" ", arguments)))
                throw new ArgumentException($"Command '{command}' does not match the expected pattern: {Command.Pattern}");
        }
    }

    class PipeServer
    {
        private const string PIPE_NAME = "SMWhatCheatsPipe";

        internal PipeServer()
        {
            // Serve the main application from a named pipe
            // Answer requests asynchronously
            Task.Run(() =>
            {
                while (true)
                {
                    using (var pipeServer = new NamedPipeServerStream(PIPE_NAME, PipeDirection.InOut, 1, PipeTransmissionMode.Byte))
                    {    
                        pipeServer.WaitForConnection();

                        using (StreamReader reader = new StreamReader(pipeServer))
                        using (StreamWriter writer = new StreamWriter(pipeServer) { AutoFlush = true })
                        {
                            string request = reader.ReadLine();
                            if (!string.IsNullOrEmpty(request))
                            {
                                try
                                {
                                    PipeRequest pipeRequest = new PipeRequest(
                                        request.Split(' ')[0].ToLower(),
                                        request.Split(' ').Skip(1).ToArray()
                                    );
                                    HandleRequest(pipeRequest, writer);
                                }
                                catch (Exception)
                                {
                                    writer.WriteLine("ERR: Invalid format");
                                }
                            }
                        }
                    }
                }
            });
        }

        private void HandleRequest(PipeRequest request, StreamWriter writer)
        {
            if (request.Command == null)
            {
                writer.WriteLine("ERR: Unknown command");
                return;
            }

            switch (request.Command.Name)
            {
                case "read":
                    // Handle read memory request
                    // Example: ReadMemory(request.Arguments);
                    writer.WriteLine("Memory read successfully.");
                    break;
                default:
                    writer.WriteLine($"Unknown command: {request.Command}");
                    break;
            }
        }
    }
}