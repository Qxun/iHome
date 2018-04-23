function showSuccessMsg() {
    $('.popup_con').fadeIn('fast', function() {
        setTimeout(function(){
            $('.popup_con').fadeOut('fast',function(){}); 
        },1000) 
    });
}

function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}

$(document).ready(function () {
    // TODO: 在页面加载完毕向后端查询用户的信息
    $.get('/api/v1.0/user',function (resp) {
        if (resp.errno == '0') {
            $('#user-avatar').attr('src', resp.data.avatar_url);
            $('#user-name').val(resp.data.username);
        }
        else if (resp.errno == '4101') {
            location.href = 'login.html';
        }
        else {
            alert(resp.errmsg);
        }
    });
    // TODO: 管理上传用户头像表单的行为
    $('#form-avatar').submit(function (e) {
        e.preventDefault();

        $(this).ajaxSubmit({
            'url': '/api/v1.0/user/avatar',
            'type': 'post',
            'headers': {
                'X-CSRFToken': getCookie('csrf_token')
            },
            'success': function (resp) {
                if (resp.errno == '0') {
                    $('#user-avatar').attr('src', resp.data['avatar_url']);
                }
                else if (resp.errno == '4101') {
                    location.href = 'login.html'
                }
                else {
                    alert(resp.errmsg);
                }
            }
        })
    });
    // TODO: 管理用户名修改的逻辑
    $('#form-name').submit(function (e) {
        e.preventDefault();
        var username = $('#user-name').val();
        if (!username){
            return;
        }
        var params = {
            'username': username
        };
        $.ajax({
            'url': '/api/v1.0/user/name',
            'type': 'put',
            'data': JSON.stringify(params),
            'contentType': 'application/json',
            'headers': {
                'X-CSRFToken': getCookie('csrf_token')
            },
            'success': function (resp) {
                if (resp.errno == '0') {
                    showSuccessMsg()
                }
                else if (resp.errno == '4101'){
                    location.href = 'login.html';
                }
                else if (resp.errno == '4003'){
                    $('.error-msg').show()
                }
                else {
                    alert(resp.errmsg);
                }
            }
        })

    })
});

