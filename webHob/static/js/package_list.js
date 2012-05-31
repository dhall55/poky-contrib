$(function(){
	$("#build_image").click(function(){
		$('form').submit();
	});
});
function get_package_dependency(param){
	var is_checked = '';
	if($("#"+param).attr('checked')==undefined){
		is_checked=0;
	}else{
		is_checked=1;
	}
	var href = "/hob/get_package_dependency/?selected_package="+param+'&is_checked='+is_checked;
	window.location = href;
}
function back_to_recipelist(){
	var href ="/hob/recipe_task_list/";
	window.location = href;
}