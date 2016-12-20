<?php
require "/home/noe/Documents/dev/test/sql.php";
require "plot.php";

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

$distort = $_POST['distort'];
?>

<form action="" method="post">
    <select name="distort">
	<?php
	foreach($distortions as $value) {
            echo "<option" . ((strcmp($distort, $value) == 0)?" selected=\"selected\"":"") . " value=$value>$value</option>\n";
	}
	?>
    </select>
    <input type="submit" value="Ok">
</form>

<?php

if(isset($_POST['distort'])) {
    $sql = "SELECT * FROM opinion WHERE name LIKE \"" . $distort . "_76%\"";
    $sql2 = "SELECT psnr, npcr, uaci, corr_horiz, corr_vert, entropy FROM stats WHERE image LIKE \"" . $distort . "_76%\"";
    
    histo($db, $sql, "mos.png");

    $img = glob("./dataset/d1/" . $distort . "_76_*");
    shuffle($img);
    echo "<img src=" . $img[0] . " class=\"histoimg\"><br>";
    echo "<img src=mos.png class=\"histoimg\">";

    $avg = 0;
    $count = 0;
    foreach ($db->query($sql) as $row) {
        $avg += $row['note'];
	$count++;
    }
    echo "<br>MOS = " . round($avg / $count, 2) . "<br>";

    $avgs = array();
    $values = array();
    $count = 0;
    foreach ($db->query($sql2) as $row) {
	foreach($row as $key => $stats) {
	    if(!is_int($key)) {
		$avgs[$key] += str_replace("\%", "", $row[$key]);
		$values[$key][] = $row[$key];
	    }
	}
	$count++;
    }
    
    foreach($avgs as $key => $value) {
	plot($values[$key], "$key.png");
	echo "<img src=$key.png class=\"histoimg\"><br>";
	echo "avg $key = " . round($value / $count, 2) . "<br>";
    }

}

?>

