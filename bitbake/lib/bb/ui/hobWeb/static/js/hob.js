function changePic(param,src){
  if (param == 'template'){
	document.getElementById("defaultTmp").src=src;
  }else if(param == 'image'){
	document.getElementById("defaultImg").src=src;
  }else if(param == 'setting'){
	document.getElementById("defaultConfig").src=src;
  }else if(param == 'layer'){
	  document.getElementById("defaultLayer").src=src;
  }else if(param == 'recipe'){
	  document.getElementById("defaultrecipe").src=src;
  }else if(param == 'package'){
	  document.getElementById("defaultpackage").src=src;
  }
}

$(function(){
	getAsynConfig();
});
var timer = null;
function getAsynConfig(){
	$.post('/hob/config_request/',
		function(data){
			json = $.parseJSON(data);
			if (json.action=='findconfs' && json.status=='OK'){
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
			if(json.action == 'DONE'){
				clearInterval(timer);
			}
		},
		'text');
}
