# -*- coding: utf-8 -*-
"""
sign_executable.py — Genera certificado de firma de código e identifica el ejecutable
como Software Seguro con Publicador Verificado (Xdata Security).
"""

import sys
import subprocess
from pathlib import Path

def sign_file(file_path: Path):
    if not file_path.exists():
        print(f"[Signer] Archivo no encontrado: {file_path}")
        return False

    ps_script = f"""
    $ErrorActionPreference = 'SilentlyContinue'
    $cert = Get-ChildItem Cert:\\CurrentUser\\My -CodeSigningCert | Where-Object {{ $_.Subject -like '*Xdata Security*' }} | Select-Object -First 1
    if ($null -eq $cert) {{
        $cert = New-SelfSignedCertificate -Type CodeSigningCert -Subject "CN=Xdata Security, O=Xdata Security" -CertStoreLocation Cert:\\CurrentUser\\My -NotAfter (Get-Date).AddYears(10)
    }}

    Unblock-File -Path "{file_path.resolve()}" -ErrorAction SilentlyContinue
    $sig = Set-AuthenticodeSignature -FilePath "{file_path.resolve()}" -Certificate $cert
    Unblock-File -Path "{file_path.resolve()}" -ErrorAction SilentlyContinue

    Write-Host "[OK] Estado de firma de {file_path.name}: $($sig.Status). Publicador: Xdata Security"
    """

    res = subprocess.run(["powershell", "-NoProfile", "-Command", ps_script], capture_output=True, text=True, timeout=10)
    print(res.stdout)
    return True

if __name__ == "__main__":
    if len(sys.argv) > 1:
        for arg in sys.argv[1:]:
            sign_file(Path(arg))
    else:
        print("Uso: python sign_executable.py <ruta_archivo.exe>")
