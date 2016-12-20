<?php
require "/home/noe/Documents/dev/test/sql.php";

function histo($db, $sql, $imagename) {
    $histo = array_fill(0, 5, 0);
    foreach ($db->query($sql) as $row) {
        $histo[$row['note'] - 1]++;
    }

    $s = "";

    foreach ($histo as $key=>$value) {
        $s = $s . ($key + 1) . " " . $value . "\n";
    }

    file_put_contents("histo.txt", $s);

    shell_exec("./histo.sh $imagename");
}

function histo2($db, $sql, $imagename) {
    $s = "";
    foreach ($db->query($sql) as $row) {
        $s .= $row['note'] . "\n";
    }

    file_put_contents("histo2.txt", $s);

    shell_exec("python histo.py $imagename");
}

function plot($data, $imagename) {
    foreach ($data as $key=>$value) {
        $s = $s . ($key + 1) . " " . $value . "\n";
    }

    file_put_contents("histo.txt", $s);

    shell_exec("./plot.sh $imagename " . str_replace("_", "-", $imagename));
}
?>
