#coding=gbk

#coding=utf-8

#-*- coding: UTF-8 -*-  

from iHome.libs.yuntongxun.CCPRestSDK import REST
import ConfigParser

#主帐号
accountSid= '您的主帐号'

#主帐号Token
accountToken= '您的主帐号Token'

#应用Id
appId='您的应用ID'

#请求地址，格式如下，不需要写http://
serverIP='app.cloopen.com'

#请求端口 
serverPort='8883'

#REST版本号
softVersion='2013-12-26'

  # 发送模板短信
  # @param to 手机号码
  # @param datas 内容数据 格式为数组 例如：{'12','34'}，如不需替换请填 ''
  # @param $tempId 模板Id
class CCP(object):
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, '_instance'):
            obj = super(CCP, cls).__new__(cls, *args, **kwargs)
            obj.rest = REST(serverIP, serverPort, softVersion)
            obj.rest.setAccount(accountSid, accountToken)
            obj.rest.setAppId(appId)
            cls._instance = obj

        return cls._instance

    def send_template_sms(self, to, datas, tempId):

    
        #初始化REST SDK
        result = self.rest.sendTemplateSMS(to,datas,tempId)
        if result.get('statusCode') == '000000':
            return 1
        else:
            return 0

#sendTemplateSMS(手机号码,内容数据,模板Id)