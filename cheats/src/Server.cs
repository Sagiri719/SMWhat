using System;
using System.Collections.Generic;
using System.Collections.ObjectModel;
using System.IO;
using System.IO.Pipes;
using System.Linq;
using System.Net.Sockets;
using System.Runtime.InteropServices.WindowsRuntime;
using System.Threading.Tasks;
using BizHawk.Client.Common;
using BizHawk.Common.CollectionExtensions;

namespace cheats
{
    struct CommandRequest
    {
        public Operation Command;
        public string[] Arguments;

        public CommandRequest(string command, string[] arguments)
        {
            Command = Operation.CommandMap.ContainsKey(command.ToLower())
                ? Operation.CommandMap[command]
                : null;
            Arguments = arguments;

            if (command != null && !Command.Matches(String.Join(" ", arguments).Trim()))
                throw new ArgumentException($"Command '{command}' does not match the expected pattern: {Command.Pattern}");
        }
    }

    class CommandServer
    {
        private readonly Cheats _cheats;

        private static CommandServer instance = null;

        internal CommandServer(Cheats cheats)
        {
            if (CommandServer.instance != null)
                throw new InvalidOperationException("PipeServer instance already exists. Only one instance can be created.");

            CommandServer.instance = this;
            _cheats = cheats ?? throw new ArgumentNullException(nameof(cheats));

            // Serve the main application from a named pipe
            // Answer requests asynchronously
            Task.Run(() => StartListening());
        }

        private void StartListening()
        {

            try
            {
                TcpListener listener = new TcpListener(System.Net.IPAddress.Loopback, 9999);
                listener.Start();

                while (true)
                {

                    TcpClient client = listener.AcceptTcpClient();
                    NetworkStream stream = client.GetStream();

                    using (StreamReader reader = new StreamReader(stream))
                    using (StreamWriter writer = new StreamWriter(stream) { AutoFlush = true })
                    {
                        string line;
                        while ((line = reader.ReadLine()) != null)
                        {
                            try
                            {
                                line = line.Trim().Replace("\r", "").Replace("\n", "");

                                // Parse the request
                                if (line.Contains(" "))
                                {
                                    var parts = line.Split(' ');
                                    var command = parts[0];
                                    var arguments = parts.Skip(1).ToArray();

                                    CommandRequest request = new CommandRequest(command, arguments);
                                    HandleRequest(request, writer);
                                }
                                else
                                {
                                    // Handle single command without arguments
                                    CommandRequest request = new CommandRequest(line, new string[] { });
                                    HandleRequest(request, writer);
                                }   
                            }
                            catch (Exception ex)
                            {
                                Console.WriteLine($"Error processing request: {ex.Message}");
                                writer.WriteLine($"ERR: {ex.Message}");
                            }
                        }
                    }
                    
                }
            }
            catch (Exception ex)
            {
                Console.WriteLine("Server creation error: " + ex.Message);
                Task.Delay(1000).ContinueWith(_ => StartListening());
            }
        }

        private void HandleRequest(CommandRequest request, StreamWriter writer)
        {
            if (request.Command == null)
            {
                writer.WriteLine("ERR: Null command");
                return;
            }

            switch (request.Command.Name.ToLower())
            {
                case "read":
                    // Handle read memory request
                    // A memory request can either have 2 or 3 arguments:
                    // 1- The memory domain
                    // 2- The address to read from
                    // 3- (optional) The size of the data to read (default is 1 byte)

                    if (request.Arguments.Length < 2 || request.Arguments.Length > 3)
                    {
                        writer.WriteLine("ERR: Invalid number of arguments for 'read' command. Expected 2 or 3 arguments.");
                        return;
                    }

                    string domain = request.Arguments[0].ToUpperInvariant();
                    if (!_cheats.GetAvailableDomains().Contains(domain))
                        writer.WriteLine($"ERR: Invalid memory domain '{request.Arguments[0]}'. Available domains: {string.Join(", ", _cheats.GetAvailableDomains())}");

                    long address = long.Parse(request.Arguments[1]);
                    long size = request.Arguments.Length == 3 ? long.Parse(request.Arguments[2]) : 1;

                    uint[] data = _cheats.ReadMemory(address, size, domain);
                    if (data == null || data.Length == 0)
                    {
                        writer.WriteLine("ERR: No data read from memory.");
                        return;
                    }

                    writer.WriteLine($"{{ size: \"{data.Length}\", data: [{string.Join(", ", data.Select(d => $"\"{d.ToString()}\""))}}}");

                    break;
                case "rmn":
                    // ROM name
                    // Get the name of the current ROM
                    writer.WriteLine(_cheats.GetRomName());
                    break;
                default:
                    writer.WriteLine($"Unknown command: {request.Command}");
                    break;
            }
        }
    }
}