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

$(document).ready(function(){
    // TODO: 查询用户的实名认证信息


    // TODO: 管理实名信息表单的提交行为
    $('#form-auth').submit(function (e) {
        e.preventDefault();
        var real_name = $('#real-name').val();
        var id_card = $('#id-card').val();
        if (!real_name || !id_card){
            $('.error-msg').show();
            return;
        }
        $('.error-msg').hide();
        var params = {
            'real_name': real_name,
            'id_card': id_card
        };
        $.ajax({
            'url': 'api/v1.0/user/auth',
            'type': 'post',
            'data': JSON.stringify(params),
            "contentType": "application/json",
            'headers': {
                'X-CSRFToken': getCookie('csrf_token')
            },
            'success': function (resp) {
                if (resp.errno == '0'){
                    $('#real-name').attr('disabled', true);
                    $('#id-card').attr('disabled', true);
                    $('.btn-success').hide()
                }
                else if (resp.errno == '4101'){
                    location.href = 'login.html';
                }
                else {
                    alert(resp.errmsg);
                }
            }
        })


    })
})