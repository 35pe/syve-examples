<?php

// constants
$API_URL = 'https://api.hexis.ai/off/de/v1';
$FORM_URL = 'https://your.domain/form.html';
$API_KEY = 'Your API key';

// submit to api
function classify ($text) {
  global $API_URL, $API_KEY;
  $postData = json_encode(array('text' => $text));
  $ch = curl_init($API_URL);
  curl_setopt($ch, CURLOPT_POSTFIELDS, $postData);
  curl_setopt($ch, CURLOPT_HTTPHEADER, array('Authorization: Bearer '.$API_KEY, 'Content-Length: '.strlen($postData)));
  curl_setopt($ch, CURLOPT_SSL_VERIFYHOST, 2);
  curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
  //curl_setopt($ch, CURLOPT_REFERER, 'http://pernes.net/form.html');  // optional - sending from server side script can be restricted via ip
  $response = curl_exec($ch);
  curl_close($ch);
  return $response;
}

if ($_POST['text'] != '' and $_SERVER['HTTP_REFERER'] == $FORM_URL and $_SERVER['HTTP_ACCEPT_LANGUAGE'] != '' and strpos($_SERVER['CONTENT_TYPE'], 'multipart/form-data') !== false) {
  $result = json_decode(classify($_POST['text']));
  echo json_encode(array('status' => $result ? 1 : 0, 'score' => $result ? $result->scores[0] : 'An error has occured'));
}

?>