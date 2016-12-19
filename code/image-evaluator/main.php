<?php
if(!isset($_POST['sex'])) {
    header('Location: index.php');
}
$images = [];
foreach(glob("./dataset/train/*") as $v) {
    $images[] = end(explode("/", $v));
}
?>

<head>
    <link rel="stylesheet" type="text/css" href="css.css">
    <script src="jquery-3.1.1.min.js"></script>
</head>

<div id="count">
    0/81
</div>

<img src="empty.png" id="distort" class="center">

<form action="javascript:onFormSubmit();" id="submit">
    Worst - 
    <input type="radio" name="quality" value="1" title="La dégradation est insupportable, rien n’est visible"> 1
    <input type="radio" name="quality" value="2" title="La dégradation est très gênante, je suis à peine capable de deviner le contenu"> 2
    <input type="radio" name="quality" value="3" title="La dégradation est gênante mais je parviens à deviner le contenu" checked> 3
    <input type="radio" name="quality" value="4" title="La dégradation est un peu gênante, mais le contenu est lisible"> 4
    <input type="radio" name="quality" value="5" title="La dégradation n'est pas gênante du tout"> 5
    - Best<br>
    <input type="submit" name="view" value="Valider" id="button"/>
</form> 
<!-- <div class="notes">
     <b>1</b> : La dégradation est insupportable, rien n’est visible<br>
     <b>2</b> : La dégradation est très gênante, je suis à peine capable de deviner le contenu<br>
     <b>3</b> : La dégradation est gênante mais je parviens à deviner le contenu<br>
     <b>4</b> : La dégradation est un peu gênante, mais le contenu est lisible<br>
     <b>5</b> : La dégradation n'est pas gênante du tout<br>
     </div> -->

<script type="text/javascript">
 var ratings = [];
 var currentImage = "";
 var images = shuffleArray(<?php echo json_encode($images); ?>);
 var lock = true;
 var distortions = shuffleArray([
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
 ]);

 function shuffleArray(array) {
     for (var i = array.length - 1; i > 0; i--) {
         var j = Math.floor(Math.random() * (i + 1));
         var temp = array[i];
         array[i] = array[j];
         array[j] = temp;
     }
     return array;
 }
 
 function sleep (time) {
     return new Promise((resolve) => setTimeout(resolve, time));
 }

 function selectImage() {
     var distortion = distortions[ratings.length % distortions.length];
     var image = images[ratings.length];
     return "./dataset/d1/" + distortion + "_76_" + image;
 }
 
 $(document).ready(function() {
     var img = selectImage();
     document.images[0].src = img;
     currentImage = img;
     lock = false;
 });

 function onFormSubmit() {
     var n = $('input[name=quality]:checked', '#submit').val();
     submit(n);
     $('input[name=quality]', '#submit').filter('[value=3]').prop('checked', true);
 }

 function submit(rating) {
     var imgs = currentImage.split("/");
     ratings.push([imgs[imgs.length-1], rating, ratings.length + 1]);

     var newImageSrc = selectImage();
     var image = document.images[0];

     var img = currentImage.split("_");
     var rawImageSrc = "./dataset/train/" + img[img.length - 1];
     image.src = rawImageSrc;
     lock = true;
     $('#button').hide();
     sleep(1000).then(() => {
	 if(ratings.length < 81) {
	     image.src = newImageSrc;
	     lock = false;
	     $('#button').show();
	 } else {
	     post();
	 }
     });
     currentImage = newImageSrc;
     $('#count').text(ratings.length + "/81");
 }

 function post() {
     function createField(form, name, data) {
	 var field = $('<input></input>');
	 field.attr("type", "hidden");
	 field.attr("name", name);
	 field.attr("value", data);
	 form.append(field);	 
     }
     
     var form = $('<form></form>');

     form.attr("method", "post");
     form.attr("action", "end.php");
   
     createField(form, "ratings", ratings);
     createField(form, "sex", "<?php echo $_POST['sex']; ?>");
     createField(form, "age", "<?php echo $_POST['age']; ?>");
  
     $(document.body).append(form);
     form.submit();
 }
 
 $(document).keypress(function(event){
     var n = parseInt(String.fromCharCode(event.which));

     if(!lock && (n > 0 && n < 6)) {
	 submit(n);
     }
 });
</script>
