<!DOCTYPE html>
<html>
<head>
  <title>Titanic Predictor</title>
</head>
<body>
  <h2>Would you survive the Titanic?</h2>

  <form action="result.php" method="POST">
    <label>Your Name: 
      <input type="text" name="name" required>
    </label><br><br>

    <label>Your Age: 
      <input type="number" name="age" min="1" max="100" required>
    </label><br><br>

    <button type="submit">Find Out!</button>
  </form>
</body>
</html>