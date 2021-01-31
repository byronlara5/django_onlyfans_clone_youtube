(function($){
  $(function(){

    $('.sidenav').sidenav();
    $('.tabs').tabs();
    $('.materialboxed').materialbox();
    $('select').formSelect();
    $('.slider').slider();
    $('.tooltipped').tooltip();
    $('.modal').modal();

    $("addtolistform").submit(function(){
      $.ajax({
        url: '/profile/addtolist',
        data: $("#addtolistform").serialize(),
        cache: false,
        type: "post",
        success: function(data){
          console.log("Person added succesfully")
        }
      });
      return false;
    });

  }); // end of document ready
})(jQuery); // end of jQuery name space
