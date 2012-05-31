$(function(){
	$("#logout").click(function(){
		location.href='/logout/';
	});

	$("#image_history").click(function(){
		$('form').submit();
	});
});

function getBaseImgDependence(param){
	if (param == " "){
		return false;
	}
	$.get('/hob/get_baseImage_dependency/',
		{'baseImage':param},
		function(data){

		},
		'text');
}