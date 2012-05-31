function get_recipe_dependency(param){
	var is_checked = '';
	if($("#"+param).attr('checked')==undefined){
		is_checked=0;
	}else{
		is_checked=1;
	}
	var href ='/hob/get_recipe_dependency/?selected_recipe='+param+'&is_checked='+is_checked;
	window.location = href;
}

$(function(){
	$("#build_pkg").click(function(){
		$('form').submit();
	});

	$("#build_image").click(function(){
		$("#is_buildImg").attr("value",'1');
		$('form').submit();
	});
});