/*! build package | get package event */
var timer = null;
var error_count = 0;
$(function(){
	timer=setInterval('getPackageEvent()','1000');
})

function getPackageEvent(){
	jQuery.get('/hob/getPackage_event/',
		function(data){
			json = jQuery.parseJSON(data);
			if (json.cacheProgress) {
				if(json.value.current <= json.value.total){
					currentNum = parseInt((parseInt(json.value.current)/parseInt(json.value.total)*100));
					$("#current_task").html(json.value.current);
					$("#total_task").html(json.value.total);
					SetProgress(currentNum);
				}
			}else if(json.build_start){
				$("#buildstart_flag").html(json.value);
			}else if(json.queueProgress){
				if(json.value.num_of_completed <= json.value.total){
					currentNum = parseInt((parseInt(json.value.num_of_completed)/parseInt(json.value.total)*100));
					$("#current_task").html(json.value.num_of_completed);
					$("#total_task").html(json.value.total);
					SetProgress(currentNum);
				}
			}else if(json.buildLogs){
				$("#current_pkg").html(json.buildLogs[0].package);
				$("#build_logs").append('package:'+json.buildLogs[0].package+' <br/>     task:'+json.buildLogs[0].task+'<br/>');
			}else if(json.error){
				error_count = error_count+1;
				var errors="";
				var temp_array = json.error.split(";");
				for(var i=0;i<temp_array.length;i++){
					errors = errors+temp_array[i]+"<br/>";
				}
				jQuery('#error_event').append('<font color="red">'+errors+'</font> <br/>');
				$("#error_count").html('('+error_count+')');
			}else if(json.packageTree){
				clearInterval(timer);
				disp(json.selected_packageSize);
			}
		},
		'text'
	);
}

function disp(param){
	var href="/hob/package_list/?pkgSize="+param;
	window.location=href;
}
