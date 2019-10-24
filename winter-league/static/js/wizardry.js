//$(document).ready(function(){
//	//new_member = '<div class="form-group"><label for="Member">Member</label><select class="form-control member_selection" ><option selected disabled>Please Select</option><option>Craig</option><option>Mike</option><option>Dave</option></select></div>'
//
//	$("#add_member").on({
//		click: function(event){
//		     event.preventDefault();
//			$("div#members").append(new_member);
//			calc_members();
//		},
//		change: function(){
//			calc_members();
//		}
//	});
//	$("#remove_last").on({
//		click: function(event){
//		    event.preventDefault();
//			$("div#members .form-group:last").remove();
//			calc_members();
//		},
//		change: function(){
//			calc_members();
//		}
//	});
//	$('#team').submit(function() {
//        calc_members();
//    });
//	function calc_members() {
//		var n = 0;
//		jQuery.each($("select"), function () {
//			if ($(this).children("option:selected").val() !== "Please Select") {
//				n++;
//			}
//		});
//		$("#team_size").val(n)
//	}
//});