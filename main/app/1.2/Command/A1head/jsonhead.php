<?php
function OutJsonString($json){
    $jsonString = json_encode($json);
    header('Content-Type:application/json');
    return $jsonString;
}
?>