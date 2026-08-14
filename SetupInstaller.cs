using System;
using System.IO;
using System.IO.Compression;
using System.Reflection;
using System.Diagnostics;
using System.Windows.Forms;
using System.Drawing;

namespace JarvisInstaller
{
    public class InstallerForm : Form
    {
        private ProgressBar progressBar;
        private Label lblStatus;
        private Button btnInstall;
        private Button btnClose;

        public InstallerForm()
        {
            this.Text = "Instalador Oficial de Asistente-XDS";
            this.Size = new Size(520, 320);
            this.StartPosition = FormStartPosition.CenterScreen;
            this.FormBorderStyle = FormBorderStyle.FixedSingle;
            this.MaximizeBox = false;
            this.BackColor = Color.FromArgb(15, 23, 42);

            Label lblTitle = new Label();
            lblTitle.Text = "ASISTENTE-XDS";
            lblTitle.Font = new Font("Segoe UI", 18, FontStyle.Bold);
            lblTitle.ForeColor = Color.FromArgb(56, 189, 248);
            lblTitle.Location = new Point(30, 25);
            lblTitle.AutoSize = true;
            this.Controls.Add(lblTitle);

            Label lblSub = new Label();
            lblSub.Text = "Asistente de Inteligencia Artificial Comercial en Tiempo Real";
            lblSub.Font = new Font("Segoe UI", 10, FontStyle.Regular);
            lblSub.ForeColor = Color.FromArgb(148, 163, 184);
            lblSub.Location = new Point(32, 60);
            lblSub.AutoSize = true;
            this.Controls.Add(lblSub);

            lblStatus = new Label();
            lblStatus.Text = "Haga clic en 'Instalar Ahora' para comenzar...";
            lblStatus.Font = new Font("Segoe UI", 9, FontStyle.Italic);
            lblStatus.ForeColor = Color.FromArgb(203, 213, 225);
            lblStatus.Location = new Point(32, 110);
            lblStatus.Size = new Size(440, 25);
            this.Controls.Add(lblStatus);

            progressBar = new ProgressBar();
            progressBar.Location = new Point(35, 140);
            progressBar.Size = new Size(435, 25);
            progressBar.Style = ProgressBarStyle.Continuous;
            this.Controls.Add(progressBar);

            btnInstall = new Button();
            btnInstall.Text = "Instalar Ahora";
            btnInstall.Font = new Font("Segoe UI", 10, FontStyle.Bold);
            btnInstall.BackColor = Color.FromArgb(14, 165, 233);
            btnInstall.ForeColor = Color.White;
            btnInstall.FlatStyle = FlatStyle.Flat;
            btnInstall.FlatAppearance.BorderSize = 0;
            btnInstall.Location = new Point(230, 200);
            btnInstall.Size = new Size(130, 40);
            btnInstall.Click += new EventHandler(OnInstallClick);
            this.Controls.Add(btnInstall);

            btnClose = new Button();
            btnClose.Text = "Cancelar";
            btnClose.Font = new Font("Segoe UI", 10, FontStyle.Regular);
            btnClose.BackColor = Color.FromArgb(51, 65, 85);
            btnClose.ForeColor = Color.White;
            btnClose.FlatStyle = FlatStyle.Flat;
            btnClose.FlatAppearance.BorderSize = 0;
            btnClose.Location = new Point(370, 200);
            btnClose.Size = new Size(100, 40);
            btnClose.Click += (s, e) => this.Close();
            this.Controls.Add(btnClose);

            try
            {
                string iconPath = Path.Combine(AppDomain.CurrentDomain.BaseDirectory, "assets", "jarvis_icono.ico");
                if (File.Exists(iconPath))
                {
                    this.Icon = new Icon(iconPath);
                }
            }
            catch {}
        }

        private void OnInstallClick(object sender, EventArgs e)
        {
            btnInstall.Enabled = false;
            btnClose.Enabled = false;
            lblStatus.Text = "Instalando archivos y configurando Asistente-XDS...";
            progressBar.Value = 20;

            try
            {
                string localApp = Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData);
                string targetDir = Path.Combine(localApp, "JARVIS_IA");

                if (!Directory.Exists(targetDir))
                {
                    Directory.CreateDirectory(targetDir);
                }

                progressBar.Value = 40;

                // 1. Extraer recurso embebido app_data.zip si está dentro del ejecutable
                Assembly asm = Assembly.GetExecutingAssembly();
                Stream resStream = asm.GetManifestResourceStream("app_data.zip");

                if (resStream != null)
                {
                    string zipTemp = Path.Combine(Path.GetTempPath(), "asistente_xds_app.zip");
                    using (FileStream fs = new FileStream(zipTemp, FileMode.Create, FileAccess.Write))
                    {
                        resStream.CopyTo(fs);
                    }
                    progressBar.Value = 60;
                    ZipFile.ExtractToDirectory(zipTemp, targetDir);
                    try { File.Delete(zipTemp); } catch {}
                }
                else
                {
                    // Fallback: copiar directorio local JARVIS_APP si existe al lado
                    string sourceDir = Path.Combine(AppDomain.CurrentDomain.BaseDirectory, "JARVIS_APP");
                    if (Directory.Exists(sourceDir))
                    {
                        CopyDirectory(sourceDir, targetDir);
                    }
                }

                progressBar.Value = 85;
                CreateShortcut(targetDir);

                progressBar.Value = 100;
                lblStatus.ForeColor = Color.FromArgb(52, 211, 153);
                lblStatus.Text = "¡Instalación Completada con Éxito!";

                btnInstall.Text = "Iniciar Asistente";
                btnInstall.Enabled = true;
                btnInstall.Click -= OnInstallClick;
                btnInstall.Click += (s, ev) =>
                {
                    string targetExe = Path.Combine(targetDir, "JARVIS_AI.exe");
                    if (!File.Exists(targetExe))
                    {
                        targetExe = Path.Combine(targetDir, "JARVIS.exe");
                    }

                    if (File.Exists(targetExe))
                    {
                        Process.Start(new ProcessStartInfo(targetExe) { WorkingDirectory = targetDir, UseShellExecute = true });
                    }
                    else
                    {
                        string vbsLauncher = Path.Combine(targetDir, "Ejecutar_JARVIS.vbs");
                        if (File.Exists(vbsLauncher))
                        {
                            Process.Start(new ProcessStartInfo("wscript.exe", "\"" + vbsLauncher + "\"") { UseShellExecute = true });
                        }
                    }
                    this.Close();
                };

                btnClose.Text = "Finalizar";
                btnClose.Enabled = true;
            }
            catch (Exception ex)
            {
                MessageBox.Show("Error durante la instalación: " + ex.Message, "Error de Instalación", MessageBoxButtons.OK, MessageBoxIcon.Error);
                btnInstall.Enabled = true;
                btnClose.Enabled = true;
            }
        }

        private void CopyDirectory(string source, string target)
        {
            foreach (string dirPath in Directory.GetDirectories(source, "*", SearchOption.AllDirectories))
            {
                if (dirPath.Contains("DIST_") || dirPath.Contains(".git")) continue;
                string newDir = dirPath.Replace(source, target);
                Directory.CreateDirectory(newDir);
            }

            foreach (string filePath in Directory.GetFiles(source, "*.*", SearchOption.AllDirectories))
            {
                if (filePath.Contains("DIST_") || filePath.Contains(".git")) continue;
                string newFile = filePath.Replace(source, target);
                File.Copy(filePath, newFile, true);
            }
        }

        private void CreateShortcut(string targetDir)
        {
            try
            {
                string targetExe = Path.Combine(targetDir, "JARVIS_AI.exe");
                if (!File.Exists(targetExe))
                {
                    targetExe = Path.Combine(targetDir, "JARVIS.exe");
                }
                if (!File.Exists(targetExe))
                {
                    targetExe = Path.Combine(targetDir, "Ejecutar_JARVIS.vbs");
                }

                string iconPath = Path.Combine(targetDir, "assets", "jarvis_icono.ico");
                if (!File.Exists(iconPath))
                {
                    iconPath = targetExe;
                }

                string desktop = Environment.GetFolderPath(Environment.SpecialFolder.Desktop);
                string startMenu = Environment.GetFolderPath(Environment.SpecialFolder.Programs);

                string desktopShortcut = Path.Combine(desktop, "JARVIS AI.lnk");
                string startMenuShortcut = Path.Combine(startMenu, "JARVIS AI.lnk");

                string psCommand = string.Format(
                    "$s=(New-Object -ComObject WScript.Shell).CreateShortcut('{0}'); $s.TargetPath='{1}'; $s.WorkingDirectory='{2}'; $s.IconLocation='{3}'; $s.Save(); " +
                    "$s2=(New-Object -ComObject WScript.Shell).CreateShortcut('{4}'); $s2.TargetPath='{1}'; $s2.WorkingDirectory='{2}'; $s2.IconLocation='{3}'; $s2.Save()",
                    desktopShortcut, targetExe, targetDir, iconPath, startMenuShortcut);

                Process.Start(new ProcessStartInfo("powershell", "-NoProfile -Command \"" + psCommand + "\"")
                {
                    CreateNoWindow = true,
                    UseShellExecute = false
                });
            }
            catch {}
        }

        [STAThread]
        public static void Main()
        {
            Application.EnableVisualStyles();
            Application.SetCompatibleTextRenderingDefault(false);
            Application.Run(new InstallerForm());
        }
    }
}

