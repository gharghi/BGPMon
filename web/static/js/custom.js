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



