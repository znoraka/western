<head>
    <link rel="stylesheet" type="text/css" href="css.css">
</head>

<?php
require "/home/noe/Documents/dev/test/sql.php";
require "plot.php";
    
$id = $_GET["id"];
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
