function submitCode() {
    var code = $("#code-input").val();

    $.post(`/join-group?code=${code}`)
        .done(function (data) {
            if(data == 'error'){
                $('#error-msg').show();
                return;
            }
            window.location.replace('/joinsuccess')
        })
        .fail(function () {
            $('#error-msg').show();
        });
}

$(document).ready(function () {
    $('#sub').click(submitCode);
});