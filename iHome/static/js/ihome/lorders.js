//模态框居中的控制
function centerModals() {
    $('.modal').each(function (i) {   //遍历每一个模态框
        var $clone = $(this).clone().css('display', 'block').appendTo('body');
        var top = Math.round(($clone.height() - $clone.find('.modal-content').height()) / 2);
        top = top > 0 ? top : 0;
        $clone.remove();
        $(this).find('.modal-content').css("margin-top", top - 30);  //修正原先已经有的30个像素
    });
}

function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}

$(document).ready(function () {
    $('.modal').on('show.bs.modal', centerModals);      //当模态框出现的时候
    $(window).on('resize', centerModals);
    // TODO: 查询房东的订单
    $.get('/api/v1.0/orders?role=landlord', function (resp) {
        if (resp.errno == '0') {
            var html = template('orders-list-tmpl', {'orders': resp.data});
            $('.orders-list').html(html);
            // TODO: 查询成功之后需要设置接单和拒单的处理
            $(".order-accept").on('click', function () {
                var orderId = $(this).parents("li").attr("order-id");
                console.log(orderId);
                $(".modal-accept").attr("order-id", orderId);
            });

            $('.modal-accept').click(function (e) {
                var orderId = $(this).attr("order-id");

                $.ajax({
                    'url': '/api/v1.0/orders/' + orderId + '/status?action=accept',
                    'type': 'put',
                    'headers': {
                        'X-CSRFToken': getCookie('csrf_token')
                    },
                    'success': function (resp) {
                        if (resp.errno == '0') {
                            // 更改页面上订单的显示状态
                            $(".orders-list>li[order-id=" + orderId + "]>div.order-content>div.order-text>ul li:eq(4)>span").html("已接单");
                            // 隐藏接单和拒单按钮
                            $("ul.orders-list>li[order-id=" + orderId + "]>div.order-title>div.order-operate").hide();
                            // 隐藏确定接单的提示框
                            $("#accept-modal").modal("hide");
                        }
                        else if (resp.errno == "4101") {
                            // 用户未登录，跳转到登录页面
                            location.href = "login.html";
                        }
                        else {
                            // 出错
                            alert(resp.errmsg);
                        }
                    }
                })

            });

            $(".order-reject").on("click", function () {
                var orderId = $(this).parents("li").attr("order-id");
                $(".modal-reject").attr("order-id", orderId);
            });

            $(".modal-reject").click(function () {
                var orderId = $(this).attr("order-id");
                // 请求后端拒单
                // 获取拒单原因
                var reason = $("#reject-reason").val();
                var params = {
                    "reason": reason
                };
                $.ajax({
                    "url": "/api/v1.0/orders/" + orderId + '/status?action=reject',
                    "type": "put",
                    "data": JSON.stringify(params),
                    "contentType": "application/json",
                    "headers": {
                        "X-CSRFToken": getCookie("csrf_token")
                    },
                    "success": function (resp) {
                        if (resp.errno == "0") {
                            // 成功
                            // 更改页面上订单的显示状态
                            $(".orders-list>li[order-id="+ orderId +"]>div.order-content>div.order-text>ul li:eq(4)>span").html("已拒单");
                            // 隐藏接单和拒单按钮
                            $("ul.orders-list>li[order-id="+ orderId +"]>div.order-title>div.order-operate").hide();
                            // 隐藏确定拒单的提示框
                            $("#reject-modal").modal("hide");
                        }
                        else if (resp.errno == "4101") {
                            // 用户未登录，跳转到登录页面
                            location.href = "login.html";
                        }
                        else {
                            // 出错
                            alert(resp.errmsg);
                        }
                    }
                })
            })


        }
        else if (resp.errno == '4101') {
            location.href = 'login.html'
        }
        else {
            // alert(resp.errmsg)
            console.log(resp.errmsg)
        }
    });


});
