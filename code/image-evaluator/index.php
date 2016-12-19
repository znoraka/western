<head>
    <link rel="stylesheet" type="text/css" href="css.css">
</head>

<div class="instructions">
    Vous allez visionner 81 images en couleur. Vous allez attribuer une note allant de 1 à 5 à chacune de ces images en fonction de votre ressenti. La notation se fait comme suit :
    <div class="notes">
	<b>1</b> : La dégradation est insupportable, rien n’est visible<br>
	<b>2</b> : La dégradation est très gênante, je suis à peine capable de deviner le contenu<br>
	<b>3</b> : La dégradation est gênante mais je parviens à deviner le contenu<br>
	<b>4</b> : La dégradation est un peu gênante, mais le contenu est lisible<br>
	<b>5</b> : La dégradation n'est pas gênante du tout<br>
    </div>

    Bonne chance !
</div>

<div class="firstform">
    <form action="main.php" method="post">
	<input type="radio" name="sex" value="H" checked>Homme
	<input type="radio" name="sex" value="F">Femme<br>
	<input type="text" hidden="hidden" name="name" value=0 ?>
	Age<input type="number" name="age" value="30">
	<input type="submit" value="Submit">
    </form>
 </div>
