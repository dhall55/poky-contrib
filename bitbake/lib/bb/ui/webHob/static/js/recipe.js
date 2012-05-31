/*! parse recipe | get recipe event */
var timer = null;
function parseRecipe(param){
	if (param == " "){
		return false;
	}
	$("#baseImage_info").hide();
	$("#build_p_i").hide();
	$.post('/hob/parseRecipe_request/',
			{'machine':param},
			function(data){
				json = $.parseJSON(data);
				if (json.action=='parserecipe' && json.status=='OK'){
					$("#rcp_pct").show();
					$('#rcp_pct p').html('Start to parse recipe.......');
					timer=setInterval('getRecipeEvent()','1000');
					}
				},
				'text'
	);
}

function getRecipeEvent(){
	$.get('/hob/parseRecipe_event/',
		{'value': Math.random()},
		function(data){
			json = jQuery.parseJSON(data);
			rcp_pct_width = $('#rcp_pct').width();
			if (json.status == 'parsing') {
				$('#rcp_pct span').css('width',json.value+'%');
				$('#rcp_pct p').html(json.status+'  percentage: '+json.value+'%');
				if (json.value == 100) {
					$('#rcp_pct span').css('width',(rcp_pct_width-6)+'px');
					$('#rcp_pct p').html('Preparing for Tree Data, Waiting~~~~');
				}
			}
			if (json.baseImages){
				clearInterval(timer);
				$('#rcp_pct').hide();
				$('#rcp_pct span').css('width','0%');
				$('#rcp_pct p').html('');
				$('#baseImage_info').fadeIn(1500);
				$("#build_p_i").show();
				var baseimage_table="<option value=' '>------------  base images  ------------</option>";
				for(var i=0;i<json.baseImages.length;i++){
					baseimage_table = baseimage_table + "<option value='"+json.baseImages[i]+"'>"+json.baseImages[i]+"</option>";
				}
				$("#baseImage").html(baseimage_table);
			}
		},
		'text'
	);
}