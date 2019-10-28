$(document).ready(function () {
    $("#SelectAll").click(function () {
        $(':checkbox').each(function () {
            if (this.checked == true) {
                this.checked = false;
            } else {
                this.checked = true;
            }
        });
    });
});

function fixNotification(id, el) {
    $.get( "/notifications/" + id +"/fix", function( data ) {
        console.log(data);
        if (data['status'] === true){
            $(el).parent().empty().append("<span class='text-green'>Fixed</span>");
        }
        else{
            $('.content-wrapper').prepend("<div class='row'><div class='col-md-12'><div class='alert alert-danger alert-bordered'> <button type='button' class='close' data-dismiss='alert'><span>×</span><span class='sr-only'>Close</span> </button>" + data['message'] + "</div></div></div>")
        }
});
}

// function expander(el) {
//     console.log($(el).parent().next('tr').html());
//     // $(el).parent().nextAll('tr.sub-tr').removeClass('hidden');
//     $(el).html('-');
// }

