/*! get buildconfig event */
$(function(){
	$(".setting_nav ul li").hover(
		function(){
			if ($(this).attr('class')=='template'){
				$(this).addClass('template_hover');
			}else if($(this).attr('class')=='settings'){
				$(this).addClass('settings_hover');
			}else if($(this).attr('class')=='history'){
				$(this).addClass('history_hover');
			}
		},
		function(){
			$(this).removeClass('template_hover');
			$(this).removeClass('settings_hover');
			$(this).removeClass('history_hover');
		}
	);

	$("#layers dl dd.title").click(function(){
		$('#popup_layers').skygqbox({
			title		: "Layer Selection",
			shut		: "Close",
			index		: 2000,
			opacity		: 0.3,
			width		: "auto",
			height		: "auto",
			autoClose	: 0,
			position	: "my"
		});
	});

	$("#show_recipe_list dl dd.title").click(function(){
		location.href='/hob/recipe_task_list/?baseimg='+$("#baseImage").val();
	});

	$("#build_pkg").click(function(){
		if ($("#baseImage").val() == " "){
			alert("please select baseImage first!");
			return false;
		}else{
			location.href='/send_command_buildpackage?baseimage='+$("#baseImage").val();
		}
	});

	$("#build_image").click(function(){
		if ($("#baseImage").val() == " "){
			alert("please select baseImage first!");
			return false;
		}else{
			location.href='/send_command_buildimage?baseimg='+$("#baseImage").val();
		}
	});
	getAsynConfig();
});
var timer = null;
function getAsynConfig(){
	$.post('/hob/buildConfig_request/',
		function(data){
			json = $.parseJSON(data);
			if (json.action=='asyncconfs' && json.status=='OK'){
				timer=setInterval('getConfigEvent()','1000');
			}
		},
		'text');
}

function getConfigEvent(){
	$.get('/hob/get_configEvents/',
			function(data){
				json = $.parseJSON(data);
				for(var value in json){
					$('#'+value).append(json[value]);
				}
				if(json.action == 'OK'){
					clearInterval(timer);
				}
			},
			'text');
}