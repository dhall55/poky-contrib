function backto_managelist(){
	var href = "/management/manage_list/";
	window.location = href;
}

$(function(){
	$("#checkboxAll").click(function(){
		if($("#checkboxAll").attr('checked') == 'checked'){
			$("[name='checkbox']").attr("checked",'true');
		}else{
			$("[name='checkbox']").removeAttr("checked");
		}
	});
});

function del_items(){
	if ($("#checkboxAll").attr('checked') == 'checked' || $("[name='checkbox']").attr('checked') == 'checked'){
		$('form').submit();
	}else{
		return false
	}
}

function add_bitbake(){
	var href = "/management/saveOrupdate_bitbake/";
	window.location = href;
}