/*! parse recipe | get recipe event */
var timer = null;
function parse_recipe(param){
	$.post('/hob/parseRecipe_request/',
			{'machine':param},
			function(data){
				json = $.parseJSON(data);
				if (json.action=='parserecipe' && json.status=='OK'){
					document.getElementById("center").style.display ="block";
					timer=setInterval('getRecipeEvent()','1000');
					}
				},
				'text'
	);
}

function getRecipeEvent(){
	jQuery.get('/hob/parseRecipe_event/',
		function(data){
			json = jQuery.parseJSON(data);
			if (json.cacheProgress || json.treedataProgress) {
				if(json.value.current <= json.value.total){
					currentNum = parseInt((parseInt(json.value.current)/parseInt(json.value.total)*100))
					SetProgress(currentNum);
				}
			}else if(json.baseImgs){
				clearInterval(timer);
				document.getElementById("center").style.display ="none";
				document.getElementById("disp_baseimgs").style.display ="block";
				var baseimage_table="";
				for(var i=0;i<json.baseImgs.length;i++){
					baseimage_table=baseimage_table+"<tr>"
					baseimage_table=baseimage_table+"<td align='left'><input type='radio' name='radio' value='"+json.baseImgs[i].name+"' /></td>"
					baseimage_table=baseimage_table+"<td align='left'>"+json.baseImgs[i].name+"</td>"
					baseimage_table=baseimage_table+"<td align='left'>"+json.baseImgs[i].desc+"</td>"
					baseimage_table=baseimage_table+"</tr>"
				}
				$("#baseImg").append(baseimage_table);
			}
		},
		'text'
	);
}
