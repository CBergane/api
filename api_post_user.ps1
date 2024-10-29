# api_post_user.ps1
$url = "http://127.0.0.1:5000/insert"
$data = @{
    name = "Test! User"
    value = "123"
}
$jsonData = $data | ConvertTo-Json
$response = Invoke-RestMethod -Uri $url -Method Post -Body $jsonData -ContentType "application/json"
Write-Output "User added:"
Write-Output $response
