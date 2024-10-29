# api_get_all.ps1
$url = "http://127.0.0.1:5000/select_all"
$response = Invoke-RestMethod -Uri $url -Method Get
Write-Output "All users data:"
Write-Output $response
