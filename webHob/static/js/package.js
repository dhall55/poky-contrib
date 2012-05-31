/*! build package | get package event */
var timer = null;
var error_count = 0;
$(function(){
	timer=setInterval('getPackageEvent()','1000');
})

function getPackageEvent(){
	jQuery.get('/hob/getPackage_event/',
		{'value': Math.random()},
		function(data){
			json = jQuery.parseJSON(data);
			rcp_pct_width = $('#rcp_pct').width();
			if (json.building){
				$('#rcp_pct span').css('width',json.building+'%');
				$('#rcp_pct p').html('Building  percentage: '+json.building+'%');
				if (json.building == 100) {
					$('#rcp_pct span').css('width',(rcp_pct_width-6)+'px');
					$('#rcp_pct p').html('Preparing for Tree Data, Waiting~~~~');
				}
			}

			if (json.buildConfig){
				$('#build_config').html('<pre>'+json.buildConfig+'</pre>');
				$('#config_logs').html('<pre>'+json.buildConfig+'</pre>');
			}

			if (json.buildStart){
				$('#buildstart').html('<pre>'+json.buildStart+'</pre>');
			}

			if (json.tasklog){
				for(var i = 0; i<json.tasklog.length; i++){
					$('#tasklogs').append(json.tasklog[i].package+'<br/>');
					$('#tasklogs').append('     '+json.tasklog[i].task+'<br/>');
					$('#current_task').html(json.tasklog[i].task);
					$('#current_package').html(json.tasklog[i].package);
				}
			}

			if (json.logs){
				$('#logs').append('<pre>'+json.logs+'</pre>');
			}

			if (json.error){
				error_count = error_count+1;
				var errors="";
				var temp_array = json.error.split(";");
				for(var i=0;i<temp_array.length;i++){
					errors = errors+temp_array[i]+"<br/>";
				}
				$('#error_event').append('<font color="red">'+errors+'</font> <br/>');
				$("#error_count").html('('+error_count+')');
			}

			if (json.packageTree){
				clearInterval(timer);
				disp();
			}
		},
		'text'
	);
}

function disp(){
	var href="/hob/package_list/";
	window.location=href;
}