# Desktop notification when Claude Code finishes responding (Windows).
# Invoked by the Stop hook. Uses a balloon tip via System.Windows.Forms,
# which works on stock Windows without extra modules.
try {
    Add-Type -AssemblyName System.Windows.Forms -ErrorAction Stop
    $n = New-Object System.Windows.Forms.NotifyIcon
    $n.Icon = [System.Drawing.SystemIcons]::Information
    $n.BalloonTipTitle = 'Claude Code'
    $n.BalloonTipText = 'Response complete'
    $n.Visible = $true
    $n.ShowBalloonTip(4000)
    Start-Sleep -Milliseconds 4500
    $n.Dispose()
} catch {
    # Notifications are best-effort; never fail the hook.
    exit 0
}
