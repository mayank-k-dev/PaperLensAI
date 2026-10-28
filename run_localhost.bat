@echo off
title PaperLensAI Localhost Server (Port 3000)
echo ============================================================
echo   Starting PaperLensAI on http://localhost:3000
echo ============================================================
echo.
cd /d "%~dp0frontend"
echo Opening http://localhost:3000 in your browser...
start http://localhost:3000
echo Server is running! Keep this window open while using PaperLensAI.
echo Press Ctrl+C anytime to stop.
echo.
powershell -NoProfile -ExecutionPolicy Bypass -Command ^
"$listener = New-Object System.Net.HttpListener; ^
$listener.Prefixes.Add('http://localhost:3000/'); ^
$listener.Start(); ^
Write-Host 'PaperLensAI Web Server listening on http://localhost:3000/'; ^
while ($listener.IsListening) { ^
    try { ^
        $context = $listener.GetContext(); ^
        $request = $context.Request; ^
        $response = $context.Response; ^
        $path = $request.Url.LocalPath.TrimStart('/'); ^
        if ([string]::IsNullOrWhiteSpace($path)) { $path = 'index.html' }; ^
        $fullPath = Join-Path (Get-Location) $path; ^
        if (Test-Path $fullPath -PathType Leaf) { ^
            $bytes = [System.IO.File]::ReadAllBytes($fullPath); ^
            if ($fullPath.EndsWith('.html')) { $response.ContentType = 'text/html; charset=utf-8' } ^
            elseif ($fullPath.EndsWith('.css')) { $response.ContentType = 'text/css' } ^
            elseif ($fullPath.EndsWith('.js')) { $response.ContentType = 'application/javascript' } ^
            elseif ($fullPath.EndsWith('.json')) { $response.ContentType = 'application/json' }; ^
            $response.ContentLength64 = $bytes.Length; ^
            $response.OutputStream.Write($bytes, 0, $bytes.Length); ^
        } else { ^
            $response.StatusCode = 404; ^
        }; ^
        $response.OutputStream.Close(); ^
    } catch { ^
    } ^
}"
