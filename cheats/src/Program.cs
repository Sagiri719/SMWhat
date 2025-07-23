using System;
using System.Collections.Generic;
using System.Collections.ObjectModel;
using System.Drawing;
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
        }

        public Cheats()
        {

            ClientSize = new Size(220, 80);
            SuspendLayout();
            Controls.Add(new System.Windows.Forms.Label { AutoSize = true, Text = "SMWhat serving!", Dock = System.Windows.Forms.DockStyle.Top, Height = 40, TextAlign = ContentAlignment.MiddleCenter, Font = new Font("Arial", 16, FontStyle.Bold) });

            Button dothingsbutton = new System.Windows.Forms.Button
            {
                Text = "Read memory NOW!",
                Dock = System.Windows.Forms.DockStyle.Bottom,
                Height = 40,
                DialogResult = System.Windows.Forms.DialogResult.OK,
            };

            dothingsbutton.Click += (sender, e) =>
            {
                try
                {
                    ReadMemory();
                    MessageBox.Show("Memory read successfully!", "Success", MessageBoxButtons.OK, MessageBoxIcon.Information);
                }
                catch (Exception ex)
                {
                    MessageBox.Show($"Error reading memory: {ex.Message}", "Error", MessageBoxButtons.OK, MessageBoxIcon.Error);
                }
            };

            Controls.Add(dothingsbutton);
            ResumeLayout(performLayout: false);
            PerformLayout();

            // Begin pipe server
            new PipeServer();
        }

        public void ReadMemory()
        {
            var s = MemoryApi.GetMemoryDomainList();

            string domains = string.Join(", ", s);
            foreach (string d in s)
            {
                domains += ($"{d} ");
            }

            MessageBox.Show($"Available memory domains: {domains}", "Memory Domains", MessageBoxButtons.OK, MessageBoxIcon.Information);

            string domain = "VRAM";
            long domainSize = 1000;

            long startAddress = 0x00000000;
            string dump = "";
            for (long i = 0; i < domainSize; i += 4)
            {
                uint value = MemoryApi.ReadU32(startAddress + i, domain);
                dump += $"{startAddress + i:X8}: {value:X8}\n";
            }

            MessageBox.Show(dump, $"Memory Dump of {domain}", MessageBoxButtons.OK, MessageBoxIcon.Information);
        }
    }
}