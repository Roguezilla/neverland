$(document).ready(function() {
    $("#upload-file-btn").click(function() {
        if(!($('#file-input').get(0).files.length === 0)) {
            $('#loading').show();
        }
    });
    
    $("body").on("click", "#delete-file-btn", function() {
        location.href = "/delete/" + $(this).attr("filename");
    });
});