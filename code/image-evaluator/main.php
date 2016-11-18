<head>
    <link rel="stylesheet" type="text/css" href="css.css">
    <script src="jquery-3.1.1.min.js"></script>
</head>

<script type="text/javascript">
 function sleep (time) {
     return new Promise((resolve) => setTimeout(resolve, time));
 }
 $(document).ready(function() {
     if($('#raw').length) {
	 $('#distort').hide();
	 $('#submit').hide();
	 sleep(1000).then(() => {
	     $('#distort').show();
	     $('#submit').show();
	     $('#raw').hide();
	 });
     }
 });
</script>

<?php

require "/home/noe/Documents/dev/test/sql.php";

function selectImage($distortions, $count) {
    $distortion = $distortions[$count % sizeof($distortions)];
    //changer _76_en _15_ si on change de dataset
    $res = glob("./dataset/d1/" . $distortion . "_76_*");
    /* echo "number of results = ". sizeof($res)  ."<br>";*/
    shuffle($res);
    return $res[0];
}

error_reporting(E_ALL);

if(isset($_POST['sex'])) {
    /* print_r($_POST);*/
    $age = $_POST['age'];
    if(strcmp($_POST['sex'], "H") == 0)
        $sex = 1;
    else $sex = 0;
    /* echo "sex = $sex<br>";*/
    $sql = "INSERT INTO personne (age, sexe) VALUES ('$age', '$sex')";
    /* echo "inserting $sql<br>";*/
    $db->query($sql);
    $id = $db->lastInsertId();
}
// print_r(unserialize($_COOKIE['distortions']));
// echo "<br>";

$count = 0;
$viewed = 0;
if(isset($_POST['count'])) {
    $count = $_POST['count'];
    $name = $_POST['name'];
    $id = $_POST['id'];
    $viewed = $_POST['viewed'];
    $note = $_POST['quality'];
    $sql = "INSERT INTO opinion (name, id, number, note) VALUES ('$name', '$id', '$count', '$note')";
    /* echo "inserting $sql<br>";*/
    $db->query($sql);

}
if(!isset($_POST['name'])) {
    header('Location: index.php');
}

if($count > 81) {
    header('Location: end.php?id='.$id."&v=$viewed");
}

echo "$count/81<br>";


if(isset($_POST['view'])) {
    $img = "./dataset/train/" . end(explode("_", $_POST['name']));
    echo "<img src=$img id='raw' class='center'>";
    $viewed++;
}

$imagepath = selectImage(unserialize($_COOKIE["distortions"]), $count);
$imagename = end(explode("/", $imagepath));

echo "<img src=$imagepath id='distort' class=\"center\">";
?>


<form action="main.php" method="post" id="submit">
    Worst - 
    <input type="radio" name="quality" value="1" title="La dégradation est insupportable, rien n’est visible"> 1
    <input type="radio" name="quality" value="2" title="La dégradation est très gênante, je suis à peine capable de deviner le contenu"> 2
    <input type="radio" name="quality" value="3" title="La dégradation est gênante mais je parviens à deviner le contenu" checked> 3
    <input type="radio" name="quality" value="4" title="La dégradation est un peu gênante, mais le contenu est lisible"> 4
    <input type="radio" name="quality" value="5" title="La dégradation est imperceptible"> 5
    - Best
    <input type="text" hidden="hidden" name="count" value=<?php echo $count + 1; ?>>
    <input type="text" hidden="hidden" name="name" value=<?php echo $imagename; ?>>
    <input type="text" hidden="hidden" name="id" value=<?php echo $id; ?>> <br>
    <input type="text" hidden="hidden" name="viewed" value=<?php echo $viewed; ?>> <br>
    <input type="submit" name="view" value="Valider et voir l'image" />
    <input type="submit" name="submit"  value="Valider" />
</form> 

