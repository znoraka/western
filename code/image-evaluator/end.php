<head>
    <link rel="stylesheet" type="text/css" href="css.css">
</head>

<?php
require "/home/noe/Documents/dev/test/sql.php";
require "plot.php";

$id = 0;
if(isset($_POST['age'])) {
    $age = $_POST['age'];
    if(strcmp($_POST['sex'], "H") == 0)
        $sex = 1;
    else $sex = 0;
    $sql = "INSERT INTO personne (age, sexe) VALUES ('$age', '$sex')";
    $db->query($sql);
    $id = $db->lastInsertId();

    $ratings = explode(",", $_POST['ratings']);

    for ($i = 0; $i < sizeof($ratings); $i+=3) {
	$name = $ratings[$i];
	$note = $ratings[$i+1];
	$number = $ratings[$i+2];
	$sql = "INSERT INTO opinion (name, id, number, note) VALUES ('$name', '$id', '$number', '$note')";
	$db->query($sql);
    }
}
    
histo($db, "SELECT note FROM opinion WHERE id=$id", "user.png");
histo($db, "SELECT note FROM opinion", "all.png");
?>

<div class="divhisto">
    <div class="histo">
	<img src=user.png class="histoimg"> <br> <br>
	Vos résultats
    </div>
    <div class="histo">
	<img src=all.png class="histoimg"> <br> <br>
	Résultats de tout le monde
    </div>
</div>
