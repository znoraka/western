<head>
    <link rel="stylesheet" type="text/css" href="css.css">
</head>

<div class="instructions">
    Vous allez visionner 81 images. Vous allez attribuer une note allant de 1 à 5 à chacune de ces images en fonction de votre ressenti. La notation se fait comme suit :
    <div class="notes">
	1 : La dégradation est insupportable, rien n’est visible<br>
	2 : La dégradation est très gênante, je suis à peine capable de
	deviner le contenu<br>
	3 : La dégradation est gênante mais je parviens à deviner le contenu<br>
	4 : La dégradation est un peu gênante, mais le contenu est lisible<br>
	5 : La dégradation est imperceptible <br>
    </div>

    Bonne chance !
</div>

<div class="firstform">
    <form action="main.php" method="post">
	<input type="radio" name="sex" value="H" checked>Homme
	<input type="radio" name="sex" value="F">Femme<br>
	<input type="text" hidden="hidden" name="name" value=0 ?>
	Age<input type="number" name="age" value="0">
	<input type="submit" value="Submit">
    </form>
 </div>

 <?php
 $distortions = [
     "ac_dc_shuffle_chrominance",
     "ac_dc_shuffle_chrominance_luminance",
     "ac_dc_shuffle_luminance",
     "ac_dc_shuffle_xor_chrominance",
     "ac_dc_shuffle_xor_luminance",
     "ac_dc_xor_chrominance",
     "ac_dc_xor_chrominance_luminance",
     "ac_dc_xor_luminance",
     "ac_shuffle_chrominance",
     "ac_shuffle_chrominance_luminance",
     "ac_shuffle_luminance",
     "ac_shuffle_xor_chrominance",
     "ac_shuffle_xor_chrominance_luminance",
     "ac_shuffle_xor_luminance",
     "ac_xor_chrominance",
     "ac_xor_chrominance_luminance",
     "ac_xor_luminance",
     "dc_shuffle_chrominance",
     "dc_shuffle_chrominance_luminance",
     "dc_shuffle_luminance",
     "dc_shuffle_xor_chrominance",
     "dc_shuffle_xor_chrominance_luminance",
     "dc_shuffle_xor_luminance",
     "dc_xor_chrominance",
     "dc_xor_chrominance_luminance",
     "dc_xor_luminance"
 ];
 shuffle($distortions);
 setcookie("distortions", serialize($distortions));
 ?>
