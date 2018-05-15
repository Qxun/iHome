function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}

$(document).ready(function() {
    $("#mobile").focus(function(){
        $("#mobile-err").hide();
    });
    $("#password").focus(function(){
        $("#password-err").hide();
    });
    // TODO: 添加登录表单提交操作
    $(".form-login").submit(function(e){
        e.preventDefault();
        var mobile = $("#mobile").val();
        var passwd = $("#password").val();
        if (!mobile) {
            $("#mobile-err span").html("请填写正确的手机号！");
            $("#mobile-err").show();
            return;
        } 
        if (!passwd) {
            $("#password-err span").html("请填写密码!");
            $("#password-err").show();
            return;
        }
        var params = {
            'mobile': mobile,
            'password': passwd
        };
        $.ajax({
            'url': '/api/v1.0/session',
            'type': 'post',
            'data': JSON.stringify(params),
            'contentType': 'application/json',
            'headers': {
                'X-CSRFToken': getCookie('csrf_token')
            },
            'success': function (resp) {
                if (resp.errno == '0'){
                    location.href = 'index.html'
                }
                else {
                    $('#password-err span').html(resp.errmsg);
                    $('#password-err').show();
                }
            }
        })

    });
})
