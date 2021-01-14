$(document).ready(function () {
   $(".updateBtn").click(function () {
      let id = $(this).attr("data-userid") 
      console.log(id)
      req = $.ajax({
          url: '/update',
          type: 'POST',
          data: {id: id}
      });
      req.done(function () {
        $("#user"+id).find(".statusCol").html("<span>Vaccinated</span>")
      });
   }); 
});