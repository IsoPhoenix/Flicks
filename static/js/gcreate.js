var users = []
var result;
function checkPeople() {
    var code = $('#code-meta').attr('code');
    $.get(`/check-people?code=${code}`)
        .done(function (data) {
            if (data == 'error') {
                console.error('AJAX ERROR!');
                return;
            }
            data = JSON.parse(data);
            result = data;
            data.forEach(function (v) {
                if (!users.includes(v[0])) {
                    $('#people').append(`<li class="list-group-item">${v[0]}</li>`);
                    users.push(v[0]);
                }
            }, this);
            // TODO: Start here. pass code in url. write the backend, loop through current members. continue in loop on current user. return all other members of group. loop through and append in js
            setTimeout(checkPeople, 1000);
        })
        .fail(function () {
            console.error('AJAX ERROR!');
        });
}

$(document).ready(function () {
    users.push($('#code-meta').attr('person'))
    setTimeout(checkPeople, 1000);
});