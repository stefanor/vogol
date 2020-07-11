<?php 

require_once(dirname(__FILE__)."/config.php");



if (empty($_GET['room']) ) {
	if (!empty($_SERVER['PHP_AUTH_USER']) && ($_SERVER['PHP_AUTH_USER'][0]=='1'|| $_SERVER['PHP_AUTH_USER'][0]=='2' ) ) {
		$spl = explode('-', $_SERVER['PHP_AUTH_USER']);
		$room = strtolower($spl[1]);
	} else {
		echo "<h1>Get a room.</h1><br>";
		foreach ($config as $r => $h ) {
			echo '<a href="/vocto.php?room='.$r.'">'.$r.'</a><br>';
		}
		exit();
	}
} else {
	$room = strtolower($_GET['room']);
}
if (empty($config[$room])) {
	echo "<h1>room not found.</h1><br>";
	foreach ($config as $r => $h ) {
		echo '<a href="/vocto.php?room='.$r.'">'.$r.'</a><br>';
	}
	exit();
}

$host = $config[$room];


if (empty($_GET['w']) && empty($argv[1])) {
?>
<head><title>room <?php echo $room; ?></title>
</head>
<body>
<div>
</div>
<table>
<tr>
<td>	<form method=GET target="tgt" action="/vocto.php" style="float: left;"><input hidden name="room" value="<?php echo $room;?>"><input hidden name="w" value="R-fs"><input type="submit" style="height:50px" value="Recording fullscreen"></form></td>
<td>	<form method=GET target="tgt" action="/vocto.php" style="float: left;"><input hidden name="room" value="<?php echo $room;?>"><input hidden name="w" value="J-f"><input type="submit" style="height:50px;" value="Jitsi fullscreen"></form></td>
</tr>
<tr>
<td>	<form method=GET target="tgt" action="/vocto.php" style="float: left;"><input hidden name="room" value="<?php echo $room;?>"><input hidden name="w" value="JG-sbs"><input type="submit" style="height:50px" value="Jitsi/Grabber side-by-side"></form></td>
<td>	<form method=GET target="tgt" action="/vocto.php" style="float: left;"><input hidden name="room" value="<?php echo $room;?>"><input hidden name="w" value="GJ-pip"><input type="submit" style="height:50px" value="Grabber/Jitsi picture-in-picture"></form></td>
</tr>
<tr>
<td>	<form method=GET target="tgt" action="/vocto.php" style="float: left;"><input hidden name="room" value="<?php echo $room;?>"><input hidden name="w" value="L-fs"><input type="submit" style="height:50px" value="Loop fullscreen"></form></td>
<td>	<form method=GET target="tgt" action="/vocto.php" style="float: left;"><input hidden name="room" value="<?php echo $room;?>"><input hidden name="w" value="LG-sbs"><input type="submit" style="height:50px" value="Loop/Grabber side-by-side"></form></td>
</tr>
<tr>
<td>	<form method=GET target="tgt" action="/vocto.php" style="float: left;"><input hidden name="room" value="<?php echo $room;?>"><input hidden name="w" value="nostream"><input type="submit" style="height:50px" value="No stream (stop recording)"></form></td>
<td>	<form method=GET target="tgt" action="/vocto.php" style="float: left;"><input hidden name="room" value="<?php echo $room;?>"><input hidden name="w" value="live"><input type="submit" style="height:50px" value="Live (record)"></form></td>
</tr>
<tr><td colspan=2><img id="output" src="/<?php echo $room;?>/room.jpg" width=480 height=270></td></tr>
<tr>
<td>
	<img id="loop" src="/<?php echo $room;?>/loop.jpg" width==240 height=135>
</td>
<td>
	<img id="grabber" src="/<?php echo $room;?>/grabber.jpg" width==240 height=135>
</td>
<td>
	<img id="recording" src="/<?php echo $room;?>/recording.jpg" width==240 height=135>
</td>
<td>
	<img id="jitsi" src="/<?php echo $room;?>/jitsi.jpg" width==240 height=135>
</td>
</tr>
<table>
<script>var img1 = document.getElementsByTagName('img')[0];var src1=img1.src;img1.addEventListener('load', function() {setTimeout(function() {img1.src=src1+'?'+Date.now()}, 1000)})</script>
<script>var img2 = document.getElementsByTagName('img')[1];var src2=img2.src;img2.addEventListener('load', function() {setTimeout(function() {img2.src=src2+'?'+Date.now()}, 1000)})</script>
<script>var img3 = document.getElementsByTagName('img')[2];var src3=img3.src;img3.addEventListener('load', function() {setTimeout(function() {img3.src=src3+'?'+Date.now()}, 1000)})</script>
</script>
<iframe name="tgt" id="target" width="0" height="0"></iframe>
</body>
<?php
	exit();
}


if (empty($_GET['w'])) {
	$param = $argv[1];
} else {
	$param = $_GET['w'];
}

if ($param === 'R-fs') $cmd = array('set_video_a recording', 'set_composite_mode fullscreen');
if ($param === 'J-fs') $cmd = array('set_video_a jitsi', 'set_composite_mode fullscreen');
if ($param === 'JG-sbs') $cmd = array('set_video_a jitsi', 'set_video_b grabber', 'set_composite_mode side_by_side_equal');
if ($param === 'GJ-pip') $cmd = array('set_video_a grabber', 'set_video_b jitsi', 'set_composite_mode side_by_side_preview');
if ($param === 'L-fs') $cmd = array('set_video_a loop', 'set_composite_mode fullscreen');
if ($param === 'LG-sbs') $cmd = array('set_video_a loop', 'set_video_b grabber', 'set_composite_mode side_by_side_equal');

if ($param === 'nostream') $cmd = array('set_stream_blank pause');
if ($param === 'live') $cmd = array('set_stream_live');

$fp=fsockopen($host, 9999, $errno, $errstr, 30);

if (!$fp) {
	echo "$errstr ($errno)<br />\n";
	exit(1);
}

foreach ($cmd as $k => $command)  {
	fwrite($fp, $command."\n");
}
fclose($fp);
