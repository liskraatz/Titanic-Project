<?php
// Grab form data from index.php
$name = $_POST['name'];
$age  = (int)$_POST['age'];

// Build the data to send to Flask
$payload = json_encode([
    'name' => $name,
    'age'  => $age
]);

// Send it to Flask using cURL
$ch = curl_init('http://localhost:5000/predict');
curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
curl_setopt($ch, CURLOPT_POST, true);
curl_setopt($ch, CURLOPT_POSTFIELDS, $payload);
curl_setopt($ch, CURLOPT_HTTPHEADER, ['Content-Type: application/json']);

$response = curl_exec($ch);
curl_close($ch);

// Decode Flask's JSON response kk
$result = json_decode($response, true);
?>

<!DOCTYPE html>
<html>
<body>
  <h2>Result for <?= htmlspecialchars($result['name']) ?></h2>
  <p><strong>Age:</strong> <?= $result['age'] ?></p>
  <p><strong>Outcome:</strong> <?= $result['message'] ?></p>
  <br>
  <a href="index.php">← Try again</a>
</body>
</html>