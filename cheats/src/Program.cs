using System;
using System.Collections.Generic;
using System.Collections.ObjectModel;
using System.Drawing;
using System.Linq;
using System.Windows.Forms;
using BizHawk.Client.Common;
using BizHawk.Client.EmuHawk;
using BizHawk.Common;
using BizHawk.Emulation.Common;

namespace cheats
{

    [ExternalTool("smwhat_generic_cheats")]
    public partial class Cheats : ToolFormBase, IExternalToolForm
    {
        private CommandServer _server;

        protected override string WindowTitleStatic
            => "SMWhat - Cheats Tool";

        // The memory access domain to use for reading memory.
        [OptionalApi]
        public IMemoryApi _maybeMemoryApi { get; set; }

        private IMemoryApi MemoryApi
            => _maybeMemoryApi ?? throw new InvalidOperationException("Memory domain not set. This tool requires a valid IMemoryDomains instance.");

        [OptionalApi]
        public IEmulationApi _maybeEmulationApi { get; set; }

        private IEmulationApi EmulatorApi
            => _maybeEmulationApi ?? throw new InvalidOperationException("Emulator not set. This tool requires a valid IEmulator instance.");

        public override void Restart()
        {
            // string gameName = EmulatorApi.GetGameInfo()?.Name;
            // MessageBox.Show($"Restarting tool for game: {gameName}", "Restart", MessageBoxButtons.OK, MessageBoxIcon.Information);
            if (_server == null)
            {
                _server = new CommandServer(this);
                MessageBox.Show("Pipe server started!", "Info", MessageBoxButtons.OK, MessageBoxIcon.Information);
            }
        }

        public Cheats()
        {

            ClientSize = new Size(220, 80);
            SuspendLayout();
            Controls.Add(new System.Windows.Forms.Label { AutoSize = true, Text = "SMWhat serving!", Dock = System.Windows.Forms.DockStyle.Top, Height = 40, TextAlign = ContentAlignment.MiddleCenter, Font = new Font("Arial", 16, FontStyle.Bold) });
            ResumeLayout(performLayout: false);
            PerformLayout();
        }

        internal string GetRomName() {
            var game = EmulatorApi?.GetGameInfo();
            return game?.Name ?? "No ROM Loaded";
        }

    internal uint[] ReadMemory(long startAddress = 0x00000000, long size = 1000, string domain = "WRAM")
    {
        if (MemoryApi == null || !GetAvailableDomains().Contains(domain))
            return Array.Empty<uint>();

        uint[] buffer = new uint[size];
        for (long i = startAddress; i < startAddress + size; i++)
            buffer[i - startAddress] = MemoryApi.ReadByte(i, domain);

        return buffer;
    }

        internal IReadOnlyCollection<string> GetAvailableDomains()
        {
            return MemoryApi.GetMemoryDomainList();
        }
    }
}