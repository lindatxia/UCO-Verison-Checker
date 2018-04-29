$(document).ajaxStart(function(){
	    $('#load').show();
	 }).ajaxStop(function(){
	    $('#load').hide();
 });